import os
import re
import numpy as np
import pandas as pd
import urllib.parse
RAW_DATA_PATH = "raw_data.csv"          # file du lieu dau vao
TIME_WINDOW = "1min"                    # do rong khung thoi gian tong hop
OUTPUT_REQUEST_LEVEL = "request_level_features.csv"
OUTPUT_WINDOW_LEVEL = "window_level_features.csv"

def load_data(path: str) -> pd.DataFrame:
    if os.path.exists(path):
        df = pd.read_csv(path)
        print(f"[INFO] Da doc {len(df)} dong tu '{path}'")
    # Chuan hoa ten cot ve chu thuong, khong dau cach
    df.columns = [c.strip().lower() for c in df.columns]

    required_cols = {"timestamp", "ip", "method", "uri", "status_code", "bytes"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Thieu cac cot bat buoc trong du lieu: {missing}")

    # Parse theo format 
    df["timestamp"] = pd.to_datetime(
        df["timestamp"], format="%m/%d/%Y %H:%M", errors="coerce"
    )

    df = df.sort_values("timestamp").reset_index(drop=True)
    df["status_code"] = df["status_code"].astype(int)
    df["response_bytes"] = pd.to_numeric(df["bytes"], errors="coerce").fillna(0)

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

SUSPICIOUS_PATTERNS = re.compile(
    r"(\%27)|(\')|(--)|(\%23)|(#)|"                      # SQLi: quote, comment
    r"(<script)|(javascript:)|(onerror\s*=)|(onload\s*=)|"  # XSS
    r"(union\s+select)|(or\s+1\s*=\s*1)|(drop\s+table)|"    # SQLi
    r"(\.\./)|(\.\.\\)|(etc/passwd)|"                        # Path traversal
    r"(%00)|(\bexec\b)|(\bcmd\b)",                            # Null byte / RCE
    re.IGNORECASE,
)


def is_suspicious(decoded_uri: str) -> int:
    """Tra ve 1 neu URI chua dau hieu tan cong pho bien, nguoc lai 0."""
    return int(bool(SUSPICIOUS_PATTERNS.search(str(decoded_uri))))


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
    df["request_interval"] = (
        df.groupby("ip")["timestamp"].diff().dt.total_seconds()
    )
    df["request_interval"] = df["request_interval"].fillna(0)

    # --- One-hot method distribution o muc request (de tong hop sau nay) ---
    method_dummies = pd.get_dummies(df["method"], prefix="method")
    df = pd.concat([df, method_dummies], axis=1)

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
        "unique_url_count": ("uri", "nunique"),
        "avg_url_length": ("url_length", "mean"),
        "max_url_length": ("url_length", "max"),
        "avg_response_bytes": ("response_bytes", "mean"),
        "std_response_bytes": ("response_bytes", "std"),
        "error_4xx_ratio": ("is_4xx", "mean"),
        "error_5xx_ratio": ("is_5xx", "mean"),
        "suspicious_uri_count": ("is_suspicious_uri", "sum"),
        "suspicious_uri_ratio": ("is_suspicious_uri", "mean"),
        "avg_request_interval": ("request_interval", "mean"),
    }

    window_features = df.groupby("window").agg(**agg_dict).reset_index()
    window_features = window_features.merge(ip_rate_agg, on="window", how="left")

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

    return df_request, df_window


if __name__ == "__main__":
    main()
