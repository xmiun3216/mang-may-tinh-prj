"""
feature_engineering.py
=======================
Muc tieu : Doc file log da duoc parse (datanew.csv),
           dung pandas de trich xuat dac trung mang (network features) phuc vu
           bai toan phat hien bat thuong.

Dau vao  : datanew.csv voi cac cot:
           IP, timestamp, method, uri_raw, uri, status_code, bytes
Dau ra   : 2 file CSV
   1) features_by_timewindow.csv
        -> Moi dong la 1 time window (mac dinh 1 phut).
        -> Day la bang feature CHINH dung de train Isolation Forest theo T16
           (requests/minute, URL_length, response_bytes, status_ratio,
            method_distribution, request_interval, unique_URL_count, ...)
   2) features_by_ip.csv
        -> Moi dong la 1 IP (tong hop toan bo thoi gian quan sat).
        -> Dac trung theo dia chi IP: so request/phut, ty le loi 4xx/5xx,
           do dai payload trung binh, so luong URI nghi ngo (SQLi/XSS).

Cach chay:
    python3 feature_engineering.py --input datanew.csv --window 1min \
        --out-window features_by_timewindow.csv --out-ip features_by_ip.csv
"""

import argparse
import re
import sys

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# 1. Regex phat hien dau hieu tan cong pho bien trong URI (SQL Injection/XSS)
#    -> chi la HEURISTIC ho tro feature engineering, KHONG dung de tu ket
#       luan la tan cong (xem gioi han cua de tai).
# --------------------------------------------------------------------------
SUSPICIOUS_PATTERNS = [
    r"(\%27)|(\')|(\-\-)|(\%23)|(#)",                 # SQLi: quote, comment
    r"((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))",  # SQLi trong query
    r"\b(union|select|insert|update|delete|drop|sleep|benchmark)\b",  # SQL keywords
    r"(<script|%3cscript|javascript:|onerror\s*=|onload\s*=)",        # XSS
    r"(\.\./)|(\.\.%2f)|(\.\.\\)",                    # Path/Directory traversal
    r"(/etc/passwd|/bin/bash|cmd\.exe|powershell)",   # command/file injection
]
SUSPICIOUS_RE = re.compile("|".join(SUSPICIOUS_PATTERNS), flags=re.IGNORECASE)


def load_data(path: str) -> pd.DataFrame:
    """Doc CSV va ep kieu du lieu dung."""
    df = pd.read_csv(path)

    required_cols = {"IP", "timestamp", "method", "uri", "status_code", "bytes"}
    missing = required_cols - set(df.columns)
    if missing:
        sys.exit(f"[LOI] Thieu cot bat buoc trong {path}: {missing}")

    # timestamp -> datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    before = len(df)
    df = df.dropna(subset=["timestamp"]).copy()
    if len(df) < before:
        print(f"[CANH BAO] Bo {before - len(df)} dong loi timestamp khong parse duoc.")

    # bytes / status_code -> numeric, xu ly missing/loi dinh dang
    df["bytes"] = pd.to_numeric(df["bytes"], errors="coerce").fillna(0)
    df["status_code"] = pd.to_numeric(df["status_code"], errors="coerce").fillna(0).astype(int)

    # loai bo trung lap hoan toan (duplicate rows)
    dup = df.duplicated().sum()
    if dup:
        print(f"[INFO] Loai {dup} dong trung lap.")
        df = df.drop_duplicates()

    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


def add_row_level_features(df: pd.DataFrame) -> pd.DataFrame:
    """Cac dac trung tinh tren tung request (dung lam nguyen lieu de aggregate)."""
    df = df.copy()

    df["url_length"] = df["uri"].astype(str).str.len()
    df["is_2xx"] = df["status_code"].between(200, 299)
    df["is_3xx"] = df["status_code"].between(300, 399)
    df["is_4xx"] = df["status_code"].between(400, 499)
    df["is_5xx"] = df["status_code"].between(500, 599)

    df["is_suspicious_uri"] = df["uri"].astype(str).apply(
        lambda u: bool(SUSPICIOUS_RE.search(u))
    )

    # khoang cach thoi gian (giay) giua request hien tai va request truoc do
    # cua CUNG MOT IP -> proxy cho "request_interval"
    df = df.sort_values(["IP", "timestamp"])
    df["prev_ts_same_ip"] = df.groupby("IP")["timestamp"].shift(1)
    df["request_interval_ip_sec"] = (
        (df["timestamp"] - df["prev_ts_same_ip"]).dt.total_seconds()
    )

    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


def build_timewindow_features(df: pd.DataFrame, window: str = "1min") -> pd.DataFrame:
    """
    Feature theo time-window (T16: requests/minute, URL_length, response_bytes,
    status_ratio, method_distribution, request_interval, unique_URL_count).
    """
    df = df.set_index("timestamp")
    g = df.groupby(pd.Grouper(freq=window))

    feats = pd.DataFrame({
        "requests_per_window":     g.size(),
        "unique_ip_count":         g["IP"].nunique(),
        "unique_url_count":        g["uri"].nunique(),
        "avg_url_length":          g["url_length"].mean(),
        "max_url_length":          g["url_length"].max(),
        "avg_response_bytes":      g["bytes"].mean(),
        "total_response_bytes":    g["bytes"].sum(),
        "status_2xx_ratio":        g["is_2xx"].mean(),
        "status_3xx_ratio":        g["is_3xx"].mean(),
        "status_4xx_ratio":        g["is_4xx"].mean(),
        "status_5xx_ratio":        g["is_5xx"].mean(),
        "suspicious_uri_ratio":    g["is_suspicious_uri"].mean(),
        "avg_request_interval_sec": g["request_interval_ip_sec"].mean(),
    })

    # method distribution (ty le GET / POST / HEAD / khac trong window)
    method_dummies = pd.get_dummies(df["method"].where(
        df["method"].isin(["GET", "POST", "HEAD"]), other="OTHER"
    ), prefix="method_ratio")
    method_ratio = method_dummies.groupby(pd.Grouper(freq=window)).mean()
    feats = feats.join(method_ratio)

    # request cao nhat tu 1 IP trong window -> tin hieu flood/DDoS tu 1 nguon
    max_req_per_ip = (
        df.groupby([pd.Grouper(freq=window), "IP"]).size()
        .groupby(level=0).max()
        .rename("max_requests_single_ip")
    )
    feats = feats.join(max_req_per_ip)

    feats = feats.fillna(0)
    feats = feats.reset_index().rename(columns={"timestamp": "window_start"})

    # bo cac window rong (khong co request nao) neu co do gap du lieu
    feats = feats[feats["requests_per_window"] > 0].reset_index(drop=True)
    return feats


def build_ip_features(df: pd.DataFrame, window: str = "1min") -> pd.DataFrame:
    """
    Feature theo tung IP (yeu cau cu the cua Thanh vien 2):
      - so request/phut tu 1 IP
      - ty le loi 4xx/5xx
      - do dai payload (bytes / url_length) trung binh
      - so luong / ty le URI nghi ngo (SQLi/XSS)
    """
    total_span_min = max(
        (df["timestamp"].max() - df["timestamp"].min()).total_seconds() / 60.0, 1e-9
    )

    grp = df.groupby("IP")

    feats = pd.DataFrame({
        "total_requests":       grp.size(),
        "requests_per_minute":  grp.size() / total_span_min,
        "unique_url_count":     grp["uri"].nunique(),
        "avg_url_length":       grp["url_length"].mean(),
        "avg_response_bytes":   grp["bytes"].mean(),
        "total_response_bytes": grp["bytes"].sum(),
        "status_4xx_ratio":     grp["is_4xx"].mean(),
        "status_5xx_ratio":     grp["is_5xx"].mean(),
        "error_ratio_4xx_5xx":  (grp["is_4xx"].sum() + grp["is_5xx"].sum()) / grp.size(),
        "suspicious_uri_count": grp["is_suspicious_uri"].sum(),
        "suspicious_uri_ratio": grp["is_suspicious_uri"].mean(),
        "avg_request_interval_sec": grp["request_interval_ip_sec"].mean(),
        "min_request_interval_sec": grp["request_interval_ip_sec"].min(),
    })

    # method distribution theo tung IP
    method_dummies = pd.get_dummies(df["method"].where(
        df["method"].isin(["GET", "POST", "HEAD"]), other="OTHER"
    ), prefix="method_ratio")
    method_dummies["IP"] = df["IP"].values
    method_ratio = method_dummies.groupby("IP").mean()
    feats = feats.join(method_ratio)

    feats = feats.fillna(0).reset_index()
    feats = feats.sort_values("total_requests", ascending=False).reset_index(drop=True)
    return feats


def main():
    parser = argparse.ArgumentParser(description="Feature engineering cho Web server log (T16)")
    parser.add_argument("--input", default="datanew.csv", help="File CSV dau vao (dau ra Thanh vien 1)")
    parser.add_argument("--window", default="1min", help="Do rong time-window, vd: 1min, 30s, 5min")
    parser.add_argument("--out-window", default="features_by_timewindow.csv")
    parser.add_argument("--out-ip", default="features_by_ip.csv")
    args = parser.parse_args()

    print(f"[1/4] Dang doc du lieu tu: {args.input}")
    df = load_data(args.input)
    print(f"      -> {len(df):,} dong, khoang thoi gian: {df['timestamp'].min()} -> {df['timestamp'].max()}")

    print("[2/4] Dang tinh dac trung theo tung request...")
    df = add_row_level_features(df)

    print(f"[3/4] Dang tong hop dac trung theo time-window ({args.window})...")
    win_feats = build_timewindow_features(df, window=args.window)
    win_feats.to_csv(args.out_window, index=False)
    print(f"      -> Da luu {len(win_feats):,} dong vao {args.out_window}")

    print("[4/4] Dang tong hop dac trung theo tung IP...")
    ip_feats = build_ip_features(df, window=args.window)
    ip_feats.to_csv(args.out_ip, index=False)
    print(f"      -> Da luu {len(ip_feats):,} dong vao {args.out_ip}")

    print("\nHoan tat. Cac cot feature theo time-window:")
    print(list(win_feats.columns))
    print("\nCac cot feature theo IP:")
    print(list(ip_feats.columns))


if __name__ == "__main__":
    main()
