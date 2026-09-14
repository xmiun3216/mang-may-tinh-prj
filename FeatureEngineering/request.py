import os
import re
import numpy as np
import pandas as pd
import urllib.parse

RAW_DATA_PATH = "raw_data.csv"          # file du lieu dau vao
TIME_WINDOW = "1min"                    # do rong khung thoi gian tong hop
OUTPUT_REQUEST_LEVEL = "request_level_features.csv"

# Format timestamp mac dinh cua nguon du lieu hien tai (chi co do phan giai PHUT).
# Neu log nguon co them GIAY, doi thanh "%m/%d/%Y %H:%M:%S" de request_interval
# chinh xac hon (xem parse_timestamp()).
TIMESTAMP_FORMAT = "%m/%d/%Y %H:%M"

# Vi timestamp trong du lieu nguon chi co do phan giai PHUT (khong co giay),
# nhieu request THUC SU khac nhau co the trung y het nhau tren cac cot
# ip/timestamp/method/uri/status_code/bytes va bi drop_duplicates() xoa oan.
# Mac dinh BAT de dung yeu cau "xu ly duplicate" cua de bai; neu ban thay
# so dong bi mat qua nhieu va muon giu nguyen du lieu tho, doi thanh False.
DROP_DUPLICATES = True


# ==============================================================================
# DOC VA CHUAN HOA DU LIEU
# ==============================================================================

def parse_timestamp(series: pd.Series) -> pd.Series:
    """Parse timestamp theo TIMESTAMP_FORMAT truoc; cac dong khong khop se
    duoc thu lai bang parser linh hoat (pandas tu doan format) thay vi bi
    coerce thang thanh NaT."""
    parsed = pd.to_datetime(series, format=TIMESTAMP_FORMAT, errors="coerce")
    failed_mask = parsed.isna() & series.notna()

    if failed_mask.any():
        fallback = pd.to_datetime(series[failed_mask], errors="coerce")
        parsed.loc[failed_mask] = fallback
        still_failed = parsed.isna() & series.notna()
        if still_failed.any():
            print(f"[WARNING] {still_failed.sum()} dong khong the parse timestamp "
                  f"(ca format chuan lan fallback), se bi loai bo o buoc sau.")

    return parsed


def load_data(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Khong tim thay file du lieu dau vao: '{path}'")

    df = pd.read_csv(path)
    print(f"[INFO] Da doc {len(df)} dong tu '{path}'")

    # Chuan hoa ten cot ve chu thuong, khong dau cach
    df.columns = [c.strip().lower() for c in df.columns]

    required_cols = {"timestamp", "ip", "method", "uri", "status_code", "bytes"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Thieu cac cot bat buoc trong du lieu: {missing}")

    # --- Loai bo ban ghi trung lap hoan toan (co the tat bang DROP_DUPLICATES) ---
    if DROP_DUPLICATES:
        n_before = len(df)
        df = df.drop_duplicates().reset_index(drop=True)
        n_dupes = n_before - len(df)
        if n_dupes > 0:
            print(f"[INFO] Da loai bo {n_dupes} dong trung lap ({n_dupes/n_before:.2%}). "
                  f"Luu y: timestamp chi co do phan giai phut nen con so nay CO THE bao gom "
                  f"ca cac request khac nhau bi trung ngau nhien tren cac cot con lai.")

    # --- Parse timestamp ---
    df["timestamp"] = parse_timestamp(df["timestamp"])
    n_bad_ts = df["timestamp"].isna().sum()
    if n_bad_ts > 0:
        print(f"[WARNING] Loai bo {n_bad_ts} dong khong co timestamp hop le")
        df = df.dropna(subset=["timestamp"])

    df = df.sort_values("timestamp").reset_index(drop=True)

    # --- status_code: ep kieu an toan, khong crash khi co gia tri thieu/loi ---
    df["status_code"] = pd.to_numeric(df["status_code"], errors="coerce")
    n_bad_status = df["status_code"].isna().sum()
    if n_bad_status > 0:
        print(f"[WARNING] Loai bo {n_bad_status} dong thieu/loi status_code")
        df = df.dropna(subset=["status_code"])
    df["status_code"] = df["status_code"].astype(int)

    # --- bytes: thieu -> 0, giu nguyen hanh vi cu (theo dung mo ta trong bao cao) ---
    df["response_bytes"] = pd.to_numeric(df["bytes"], errors="coerce").fillna(0)

    df = df.reset_index(drop=True)
    return df


# ==============================================================================
# GIAI MA URI (URL DECODE)
# ==============================================================================

def decode_uri(uri: str) -> str:
    """Giai ma URL-encoded string, ha ve chu thuong de chuan hoa khi quet pattern."""
    try:
        return urllib.parse.unquote(str(uri)).lower()
    except Exception:
        return str(uri).lower()


# ==============================================================================
# PHAT HIEN KY TU / PATTERN LA TRONG URI (SQLi / XSS / Path Traversal ...)
# ==============================================================================
# Luu y: cac pattern don le nhu dau nhay don ('), dau gach doi (--), dau # rieng
# le da BI LOAI BO khoi bo luat nay vi gay false positive rat nang tren du lieu
# thuc te (vd: URL san pham tieng Farsi dung "--" lam dau phan cach, hoac dung
# dau nhay don trong ten model san pham). Bo luat hien tai chi giu cac pattern
# co NGU CANH ro rang, gan voi ky thuat tan cong that su.
SUSPICIOUS_PATTERNS = re.compile(
    r"(\%27.{0,20}(--|\%23|#))|"                              # quote roi comment SQL ngay sau (that su giong SQLi)
    r"(\bunion\s+select\b)|(\bor\s+1\s*=\s*1\b)|(\bdrop\s+table\b)|(\bselect\s+.+\sfrom\b)|"  # SQLi co ngu canh
    r"(<script[\s>])|(javascript:)|(onerror\s*=)|(onload\s*=)|"  # XSS
    r"(\.\./\.\./)|(\.\.\\\.\.\\)|(/etc/passwd)|(boot\.ini)|"    # Path traversal
    r"(%00)|(\bcmd\.exe\b)|(;\s*rm\s+-rf\s)|(\|\s*nc\s+-)",       # Null byte / RCE
    re.IGNORECASE,
)


def is_suspicious(decoded_uri: str) -> int:
    """Tra ve 1 neu URI chua dau hieu tan cong pho bien, nguoc lai 0."""
    return int(bool(SUSPICIOUS_PATTERNS.search(str(decoded_uri))))


# ==============================================================================
# OUTLIER FLAG (IQR) - khong loai bo du lieu, chi danh dau de phuc vu EDA/bao cao
# ==============================================================================

def flag_outliers_iqr(series: pd.Series, k: float = 1.5) -> pd.Series:
    """Danh dau outlier bang quy tac IQR. Khong drop du lieu: voi bai toan
    anomaly detection, outlier chinh la doi tuong can quan sat, khong phai
    nhieu can loai bo."""
    q1, q3 = series.quantile([0.25, 0.75])
    iqr = q3 - q1
    lower, upper = q1 - k * iqr, q3 + k * iqr
    return ((series < lower) | (series > upper)).astype(int)


# ==============================================================================
# FEATURE O MUC DO TUNG REQUEST (REQUEST-LEVEL)
# ==============================================================================

def build_request_level_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # --- Giai ma va do dai URL ---
    df["decoded_uri"] = df["uri"].apply(decode_uri)
    df["url_length"] = df["uri"].astype(str).str.len()

    # --- Co lo hong / bat thuong trong URI khong ---
    df["is_suspicious_uri"] = df["decoded_uri"].apply(is_suspicious)

    # --- Co error khong ---
    df["is_4xx"] = df["status_code"].between(400, 499).astype(int)
    df["is_5xx"] = df["status_code"].between(500, 599).astype(int)

    # --- Khoang cach thoi gian giua request lien tiep cua cung 1 IP (giay) ---
    df = df.sort_values(["ip", "timestamp"])

    df["is_first_request_of_ip"] = (df.groupby("ip").cumcount() == 0)
    df["request_interval"] = (
        df.groupby("ip")["timestamp"].diff().dt.total_seconds()
    )
    # Request dau tien cua 1 IP khong co request truoc do de so sanh: dung sentinel
    # -1 thay vi 0, de khong bi hieu nham la "request lien tiep sat nhau" (0 giay).
    df.loc[df["is_first_request_of_ip"], "request_interval"] = -1

    # --- One-hot method distribution o muc request (de tong hop sau nay) ---
    method_dummies = pd.get_dummies(df["method"], prefix="method")
    df = pd.concat([df, method_dummies], axis=1)

    # --- Outlier flag (IQR) cho url_length va response_bytes, phuc vu EDA ---
    df["is_outlier_url_length"] = flag_outliers_iqr(df["url_length"])
    df["is_outlier_response_bytes"] = flag_outliers_iqr(df["response_bytes"])

    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


# ==============================================================================
# FEATURE THEO KHUNG THOI GIAN (TIME-WINDOW LEVEL) - dung cho Isolation Forest
# ==============================================================================

def build_window_level_features(df: pd.DataFrame, freq: str = TIME_WINDOW) -> pd.DataFrame:
    df = df.copy()
    df["window"] = df["timestamp"].dt.floor(freq)

    # --- Requests/phut tu tung IP, roi lay gia tri trung binh/max trong window ---
    ip_minute_counts = (
        df.groupby(["ip", "window"]).size().reset_index(name="requests_per_minute_per_ip")
    )
    ip_rate_agg = ip_minute_counts.groupby("window")["requests_per_minute_per_ip"].agg(
        avg_requests_per_ip="mean",
        max_requests_per_ip="max",
    ).reset_index()

    method_cols = [c for c in df.columns if c.startswith("method_")]

    agg_dict = {
        "total_requests": ("ip", "count"),
        "unique_ip_count": ("ip", "nunique"),
        "unique_url_count": ("decoded_uri", "nunique"),  # dung URI da giai ma de tranh dem trung do encode khac nhau
        "avg_url_length": ("url_length", "mean"),
        "max_url_length": ("url_length", "max"),
        "avg_response_bytes": ("response_bytes", "mean"),
        "std_response_bytes": ("response_bytes", "std"),
        "error_4xx_ratio": ("is_4xx", "mean"),
        "error_5xx_ratio": ("is_5xx", "mean"),
        "suspicious_uri_count": ("is_suspicious_uri", "sum"),
        "suspicious_uri_ratio": ("is_suspicious_uri", "mean"),
        "outlier_url_length_ratio": ("is_outlier_url_length", "mean"),
        "outlier_response_bytes_ratio": ("is_outlier_response_bytes", "mean"),
    }

    window_features = df.groupby("window").agg(**agg_dict).reset_index()
    window_features = window_features.merge(ip_rate_agg, on="window", how="left")

    # --- avg_request_interval: chi tinh tren cac request THUC SU co request truoc
    # do cua cung IP trong cua so (bo qua sentinel -1 cua request dau tien) ---
    valid_interval = df[df["request_interval"] >= 0]
    interval_agg = (
        valid_interval.groupby("window")["request_interval"]
        .mean()
        .reset_index(name="avg_request_interval")
    )
    window_features = window_features.merge(interval_agg, on="window", how="left")

    # --- Ty le phan phoi method (GET/POST/...) trong tung window ---
    if method_cols:
        method_ratio = df.groupby("window")[method_cols].mean().reset_index()
        method_ratio = method_ratio.rename(
            columns={c: c.replace("method_", "method_ratio_") for c in method_cols}
        )
        window_features = window_features.merge(method_ratio, on="window", how="left")

    window_features = window_features.fillna(0)
    window_features = window_features.sort_values("window").reset_index(drop=True)

    return window_features


# ==============================================================================
# MAIN PIPELINE
# ==============================================================================

def main():
    print("=" * 70)
    print("BUOC 1: Doc va chuan hoa du lieu")
    print("=" * 70)
    df_raw = load_data(RAW_DATA_PATH)

    print("\n" + "=" * 70)
    print("BUOC 2: Trich xuat feature o muc do request (Request-Level)")
    print("=" * 70)
    df_request = build_request_level_features(df_raw)
    print(df_request[[
        "timestamp", "ip", "method", "url_length",
        "is_suspicious_uri", "is_4xx", "is_5xx", "request_interval"
    ]].head(10))

    print("\n" + "=" * 70)
    print("BUOC 3: Tong hop feature theo khung thoi gian (Window-Level)")
    print("=" * 70)
    df_window = build_window_level_features(df_request, freq=TIME_WINDOW)
    print(df_window.head(10))

    print("\n" + "=" * 70)
    print("BUOC 4: Luu ket qua ra file CSV")
    print("=" * 70)
    df_request.to_csv(OUTPUT_REQUEST_LEVEL, index=False)
    df_window.to_csv(OUTPUT_WINDOW_LEVEL, index=False)
    print(f"[DONE] Da luu: {OUTPUT_REQUEST_LEVEL}  ({len(df_request)} dong)")
    print(f"[DONE] Da luu: {OUTPUT_WINDOW_LEVEL}  ({len(df_window)} dong)")

    print("\n" + "=" * 70)
    print("THONG KE NHANH - Cac window co dau hieu bat thuong ro rang nhat")
    print("(dua tren suspicious_uri_count va max_requests_per_ip)")
    print("=" * 70)
    top_suspicious = df_window.sort_values(
        by=["suspicious_uri_count", "max_requests_per_ip"], ascending=False
    ).head(5)
    print(top_suspicious[[
        "window", "total_requests", "unique_ip_count",
        "suspicious_uri_count", "max_requests_per_ip", "error_4xx_ratio", "error_5xx_ratio"
    ]])

    print("\n" + "=" * 70)
    print("THONG KE NHANH - Phan tich false positive cua is_suspicious_uri")
    print("(danh sach mau de kiem tra bang mat, phuc vu bao cao)")
    print("=" * 70)
    sample_flagged = df_request.loc[df_request["is_suspicious_uri"] == 1, "decoded_uri"]
    print(f"So request bi gan co is_suspicious_uri=1: {len(sample_flagged)}")
    print(sample_flagged.drop_duplicates().head(10).to_string(index=False))

    return df_request, df_window


if __name__ == "__main__":
    main()
