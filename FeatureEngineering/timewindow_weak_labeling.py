"""
weak_labeling.py
=================
Quy tac gan nhan (moi rule co the giai thich duoc duoi goc do mang may tinh):
  R1. suspicious_uri_ratio > 1%
        -> Ty le dang ke request co dau hieu SQL Injection / XSS / Path
           traversal
  R2. requests_per_window (hoac requests_per_minute) > percentile 95
        -> Tan so request bat thuong cao, dau hieu (flash-)flood/DDoS.
  R3. max_requests_single_ip > percentile 95  (chi ap dung file time-window)
        -> Mot IP don le gui qua nhieu request trong 1 khoang thoi gian
           ngan, dau hieu tan cong tu 1 nguon.
  R4. status_5xx_ratio > 0.05 (5%)
        -> Ty le loi server bat thuong cao, co the do tan cong lam qua tai
           he thong hoac khai thac loi (vd request malformed).
  R5. error_ratio_4xx_5xx (hoac status_4xx_ratio) > percentile 95
        -> Nhieu request loi 4xx (vd 404) dong loat, dau hieu scanning/
           brute-force tim duong dan/endpoint.

  -> weak_label = "Anomaly" neu THOA MAN >=1 rule, nguoc lai = "Normal".
  -> label_reason liet ke cac rule da kich hoat (phuc vu giai thich ket
     qua trong Chuong 5 cua bao cao).

Dau ra:
  - timewindow_labeled.csv        (toan bo, co weak_label + label_reason)
  - timewindow_labeled_train.csv  (80%, stratified theo weak_label)
  - timewindow_labeled_test.csv   (20%, stratified theo weak_label)
  - ip_labeled.csv / ip_labeled_train.csv / ip_labeled_test.csv (tuong tu,
    theo don vi IP)

Cach chay:
    python3 weak_labeling.py \
        --window-features features_by_timewindow.csv \
        --ip-features features_by_ip.csv
"""

import argparse

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

RANDOM_STATE = 42


def label_timewindow(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    p95_requests = df["requests_per_window"].quantile(0.95)
    p95_max_ip = df["max_requests_single_ip"].quantile(0.95)
    p95_error4xx = df["status_4xx_ratio"].quantile(0.95)

    r1 = df["suspicious_uri_ratio"] > 0.01
    r2 = df["requests_per_window"] > p95_requests
    r3 = df["max_requests_single_ip"] > p95_max_ip
    r4 = df["status_5xx_ratio"] > 0.05
    r5 = df["status_4xx_ratio"] > p95_error4xx

    reasons = []
    for i in range(len(df)):
        hit = []
        if r1.iloc[i]: hit.append("R1_suspicious_uri")
        if r2.iloc[i]: hit.append("R2_high_request_rate")
        if r3.iloc[i]: hit.append("R3_single_ip_flood")
        if r4.iloc[i]: hit.append("R4_high_5xx_error")
        if r5.iloc[i]: hit.append("R5_high_4xx_scan")
        reasons.append(";".join(hit) if hit else "none")

    df["label_reason"] = reasons
    df["weak_label"] = np.where(df["label_reason"] != "none", "Anomaly", "Normal")

    print(f"[time-window] Nguong: requests>{p95_requests:.1f}, "
          f"max_ip_req>{p95_max_ip:.1f}, err4xx>{p95_error4xx:.3f}")
    print(f"[time-window] Phan bo nhan: {df['weak_label'].value_counts().to_dict()}")
    return df


def label_ip(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    p95_rpm = df["requests_per_minute"].quantile(0.95)
    p95_error4xx = df["status_4xx_ratio"].quantile(0.95)

    r1 = df["suspicious_uri_ratio"] > 0.01
    r2 = df["requests_per_minute"] > p95_rpm
    r4 = df["status_5xx_ratio"] > 0.05
    r5 = df["status_4xx_ratio"] > p95_error4xx
    # R6 (min_request_interval_sec < 0.05) da bi LOAI KHOI bo rule per-IP:
    # median min_request_interval_sec toan dataset = 0s, vi trinh duyet tai
    # nhieu asset (anh/css/js) gan nhu dong thoi khi mo 1 trang - day la hanh
    # vi BINH THUONG cua nguoi dung that, khong phai dau hieu bot dang tin
    # cay cho dataset nay. Giu lai o day chi de tham khao/debug.

    reasons = []
    for i in range(len(df)):
        hit = []
        if r1.iloc[i]: hit.append("R1_suspicious_uri")
        if r2.iloc[i]: hit.append("R2_high_request_rate")
        if r4.iloc[i]: hit.append("R4_high_5xx_error")
        if r5.iloc[i]: hit.append("R5_high_4xx_scan")
        reasons.append(";".join(hit) if hit else "none")

    df["label_reason"] = reasons
    df["weak_label"] = np.where(df["label_reason"] != "none", "Anomaly", "Normal")

    print(f"[per-IP] Nguong: rpm>{p95_rpm:.2f}, err4xx>{p95_error4xx:.3f}")
    print(f"[per-IP] Phan bo nhan: {df['weak_label'].value_counts().to_dict()}")
    return df


def split_and_save(df: pd.DataFrame, prefix: str, test_size: float = 0.2):
    """
    Tach train/test hop ly (stratified theo weak_label) - dung cho Chuong 3:
    'Voi supervised learning phai tach train/test hop ly; khong huan luyen
    lai mo hinh tren test set.'
    """
    df.to_csv(f"{prefix}_labeled.csv", index=False)

    # neu 1 lop qua it mau thi khong stratify duoc -> fallback
    counts = df["weak_label"].value_counts()
    stratify = df["weak_label"] if counts.min() >= 2 else None

    train_df, test_df = train_test_split(
        df, test_size=test_size, random_state=RANDOM_STATE, stratify=stratify
    )
    train_df.to_csv(f"{prefix}_labeled_train.csv", index=False)
    test_df.to_csv(f"{prefix}_labeled_test.csv", index=False)

    print(f"[{prefix}] Train: {len(train_df)} dong, Test: {len(test_df)} dong")
    print(f"[{prefix}] Ty le Anomaly - train: {(train_df['weak_label'] == 'Anomaly').mean():.3f}, "
          f"test: {(test_df['weak_label'] == 'Anomaly').mean():.3f}")


def main():
    parser = argparse.ArgumentParser(description="Gan weak label (heuristic) cho feature CSV")
    parser.add_argument("--window-features", default="features_by_timewindow.csv")
    parser.add_argument("--ip-features", default="features_by_ip.csv")
    parser.add_argument("--test-size", type=float, default=0.2)
    args = parser.parse_args()

    print("=== Gan nhan cho time-window features ===")
    win = pd.read_csv(args.window_features)
    win_labeled = label_timewindow(win)
    split_and_save(win_labeled, "timewindow", test_size=args.test_size)

    print("\n=== Gan nhan cho per-IP features ===")
    ip = pd.read_csv(args.ip_features)
    ip_labeled = label_ip(ip)
    split_and_save(ip_labeled, "ip", test_size=args.test_size)

    print("\nHoan tat.")


if __name__ == "__main__":
    main()
