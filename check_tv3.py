import pandas as pd

# Đọc file của TV3
tv3_df = pd.read_csv('Output1_TimeWindow_Labeled_TV4.csv')

print("=== THỐNG KÊ KẾT QUẢ ISOLATION FOREST (TV3) ===")
print(f"Tổng số luồng IP đã kiểm tra: {len(tv3_df)}")

# Đếm số lượng bị gắn nhãn bất thường (Label_Text là Anomaly hoặc Label là -1)
# Mình sẽ dùng value_counts() để hiển thị tất cả các nhãn TV3 đã dự đoán
print("\nPhân bổ dự đoán của TV3:")
if 'Label_Text' in tv3_df.columns:
    print(tv3_df['Label_Text'].value_counts())
elif 'Label' in tv3_df.columns:
    print(tv3_df['Label'].value_counts())