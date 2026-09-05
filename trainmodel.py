import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyClassifier
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.metrics import classification_report, confusion_matrix

print("1. Đang tải và xử lý dữ liệu...")
df = pd.read_csv('data3.csv') 

df = df.dropna()

# 2. TIỀN XỬ LÝ (Preprocessing)
# Tạo cột nhãn số: Nếu Label_Text là 'Normal' thì gán 0, khác thì gán 1
df['label'] = (df['Label_Text'] != 'Normal').astype(int)

# Bỏ các cột dạng chữ và cột kết quả của TV3
cols_to_drop = ['ip', 'timestamp', 'method', 'uri', 'Label_Text', 'Anomaly_Score', 'label', 'Index']
# Ma trận X chỉ chứa các đặc trưng số để học (bytes, request_count, error_4xx...)
X = df.drop(columns=[col for col in cols_to_drop if col in df.columns])
y = df['label']

# 3. CHIA TẬP TRAIN/TEST (80/20)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"-> Số mẫu Train: {len(X_train)} | Số mẫu Test: {len(X_test)}")

# 4. CHẠY BASELINE (Mô hình ngốc nghếch)
print("\n" + "="*40)
print("KẾT QUẢ BASELINE (DUMMY CLASSIFIER)")
print("="*40)
dummy = DummyClassifier(strategy='most_frequent')
dummy.fit(X_train, y_train)
y_pred_dummy = dummy.predict(X_test)

print("Ma trận nhầm lẫn:")
print(confusion_matrix(y_test, y_pred_dummy))
print("\nBáo cáo phân loại:")
print(classification_report(y_test, y_pred_dummy, zero_division=0))

# 5. CHẠY DECISION TREE
print("\n" + "="*40)
print("KẾT QUẢ DECISION TREE")
print("="*40)
tree = DecisionTreeClassifier(max_depth=4, random_state=42)
tree.fit(X_train, y_train)
y_pred_tree = tree.predict(X_test)

print("Ma trận nhầm lẫn:")
print(confusion_matrix(y_test, y_pred_tree))
print("\nBáo cáo phân loại:")
print(classification_report(y_test, y_pred_tree, zero_division=0))

print("\n" + "="*40)
print("CÁC LUẬT MÔ HÌNH HỌC ĐƯỢC (RULES)")
print("="*40)
print(export_text(tree, feature_names=list(X.columns)))