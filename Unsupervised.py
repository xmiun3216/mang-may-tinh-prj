import pandas as pd
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
# Bước 1: Xây dựng file aggregated_ip_features.csv với 7 đặc trưng
df = pd.read_csv('request_level_features.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['time_window'] = df['timestamp'].dt.floor('1min')
aggregated_df = (
    df.groupby(['ip', 'time_window'])
    .agg(
        request_count=('uri', 'count'),  
        error_4xx_rate=('is_4xx', 'mean'), 
        error_5xx_rate=('is_5xx', 'mean'), 
        avg_payload_bytes=('bytes','mean',
        ),
        max_payload_bytes=('bytes', 'max'),  
        unique_uri_count=('uri','nunique',
        ), 
        suspicious_flag_count=('is_suspicious_uri','sum',
        ),  
    )
    .reset_index()
)
aggregated_df.to_csv('aggregated_ip_features.csv', index=False)

raw_df = pd.read_csv('request_level_features.csv')
agg_df = pd.read_csv('aggregated_ip_features.csv')

raw_df['timestamp'] = pd.to_datetime(raw_df['timestamp'])
raw_df['time_window'] = raw_df['timestamp'].dt.floor('1min') 

agg_df['time_window'] = pd.to_datetime(agg_df['time_window'])

if 'Index' not in raw_df.columns:
    raw_df.insert(0, 'Index', range(1, len(raw_df) + 1))
# Bước 2: Cập nhật features cho thuật toán Isolation Forest
features = [
    'request_count', 'error_4xx_rate', 'error_5xx_rate', 
    'avg_payload_bytes', 'max_payload_bytes', 
    'unique_uri_count', 'suspicious_flag_count'
]
X = agg_df[features]

model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)

# Bước 3: Fit và dự đoán trực tiếp trên tập agg_df dựa vào điểm Anomaly_Score
agg_df['Label'] = model.fit_predict(X)                
agg_df['Anomaly_Score'] = model.decision_function(X) 

# Bước 4: Kiểm chứng chỉ số contamination
# 1. Kiểm tra phân bố điểm Anomaly Score
plt.figure(figsize=(10, 5))
sns.histplot(agg_df['Anomaly_Score'], bins=50, kde=True)
plt.axvline(x=agg_df[agg_df['Label'] == -1]['Anomaly_Score'].max(), color='red', linestyle='--', label='Ngưỡng cắt (Threshold)')
plt.title('Phân bố Anomaly Score')
plt.legend()
plt.show()

# 2. Kiểm tra bằng Thống kê trung bình (Rất quan trọng)
print("\n--- BẢNG SO SÁNH ĐẶC TRƯNG GIỮA NORMAL VÀ ATTACK ---")
profile = agg_df.groupby('Label')[['request_count', 'error_4xx_rate', 'error_5xx_rate', 'unique_uri_count', 'suspicious_flag_count']].mean()
print(profile)

# 3. Kiểm tra bằng phân bố PCA
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)
plt.figure(figsize=(10, 8))
plt.scatter(X_pca[agg_df['Label'] == 1, 0], X_pca[agg_df['Label'] == 1, 1], 
            c='blue', label='Normal (Hợp lệ)', alpha=0.3, s=15, edgecolors='none')
plt.scatter(X_pca[agg_df['Label'] == -1, 0], X_pca[agg_df['Label'] == -1, 1], 
            c='red', label='Anomaly (Bất thường)', marker='x', s=60, linewidths=1.5)
plt.title('Phân bố không gian dữ liệu PCA (chuẩn hóa StandardScaler)', fontsize=14, pad=15)
plt.xlabel(f'Principal Component 1 (Giải thích {pca.explained_variance_ratio_[0]*100:.1f}% phương sai)', fontsize=12)
plt.ylabel(f'Principal Component 2 (Giải thích {pca.explained_variance_ratio_[1]*100:.1f}% phương sai)', fontsize=12)
plt.legend(loc='best')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()

# Bước 5:  Lọc Label == -1 (Bất thường), sắp xếp theo Anomaly_Score tăng dần
sample_uris = raw_df.groupby(['ip', 'time_window'])['uri'].first().reset_index()
sample_uris.rename(columns={'uri': 'Sample_URI'}, inplace=True)
agg_df_with_uri = agg_df.merge(sample_uris, on=['ip', 'time_window'], how='left')

output_df = agg_df_with_uri[agg_df_with_uri['Label'] == -1].sort_values(by='Anomaly_Score', ascending=True)

output_df.to_csv('Anomalies_Timeline.csv', index=False)
print(f"Đã xuất Output với {len(output_df)} cụm hành vi bất thường (Time-window level).")