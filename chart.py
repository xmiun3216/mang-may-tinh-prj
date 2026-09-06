import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Đọc file request_level_features.csv
# df_req = pd.read_csv('request_level_features.csv')

plt.figure(figsize=(9, 5.5))
sns.scatterplot(
    data=df_req,
    x='bytes',
    y='url_length',
    hue='is_suspicious',  # Phân màu đỏ/xanh theo nhãn nghi ngờ
    palette={0: '#3498db', 1: '#e74c3c'},
    alpha=0.4,  # Giảm độ mờ tránh đè điểm
    s=25,  # Thu nhỏ kích thước chấm
)

plt.title(
    'Phân phối đặc trưng Request: URL Length vs Response Bytes',
    fontsize=13,
    fontweight='bold',
)
plt.xlabel('Response Size (Bytes)', fontsize=11)
plt.ylabel('URL Length (Characters)', fontsize=11)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(title='Is Suspicious', labels=['Bình thường (0)', 'Khả nghi (1)'])
plt.tight_layout()
plt.show()