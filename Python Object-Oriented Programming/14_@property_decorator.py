import pandas as pd
df = pd.read_csv(r"C:\Users\PC\01_Python\request_level_features.csv")
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