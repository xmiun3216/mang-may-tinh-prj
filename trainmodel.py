import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyClassifier
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import numpy as np

print("1. Đang tải và xử lý dữ liệu...")
df = pd.read_csv('data3.csv') 

df = df.dropna()

# 2. TIỀN XỬ LÝ (Preprocessing)
df['label'] = (df['Label_Text'] != 'Normal').astype(int)

cols_to_drop = ['ip', 'timestamp', 'method', 'uri', 'Label_Text', 'Anomaly_Score', 'label', 'Index']
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

# 6. XUẤT BIỂU ĐỒ (VISUALIZATION)
print("\n" + "="*40)
print("ĐANG XUẤT BIỂU ĐỒ (VISUALIZATION)...")
print("="*40)

# --- Biểu đồ 1: Ma trận nhầm lẫn ---
fig, ax = plt.subplots(figsize=(6, 5))
ConfusionMatrixDisplay.from_estimator(tree, X_test, y_test, cmap='Blues', ax=ax)
plt.title("Biểu đồ 1: Ma trận nhầm lẫn của Decision Tree")
plt.savefig("confusion_matrix.png", dpi=300, bbox_inches='tight')
plt.close()
print("- Đã lưu biểu đồ Ma trận nhầm lẫn thành 'confusion_matrix.png'")

# --- Biểu đồ 2: Trực quan hóa Cây quyết định ---
plt.figure(figsize=(40, 20))
plot_tree(tree, feature_names=list(X.columns), class_names=['Normal', 'Attack'], 
          filled=True, rounded=True, fontsize=10)
plt.title("Biểu đồ 2: Cấu trúc mô hình Cây quyết định")
plt.savefig("decision_tree_structure.png", dpi=300, bbox_inches='tight')
plt.close()
print("- Đã lưu biểu đồ Cấu trúc cây thành 'decision_tree_structure.png'")

# --- Biểu đồ 3: Feature Importance ---
importances = tree.feature_importances_
indices = np.argsort(importances)[::-1]

plt.figure(figsize=(10, 6))
plt.title("Biểu đồ 3: Mức độ quan trọng của các đặc trưng (Feature Importance)")
plt.bar(range(X.shape[1]), importances[indices], align="center", color='skyblue')
plt.xticks(range(X.shape[1]), [list(X.columns)[i] for i in indices], rotation=45, ha='right')
plt.xlim([-1, X.shape[1]])
plt.tight_layout()
plt.savefig("feature_importance.png", dpi=300)
plt.close()
print("- Đã lưu biểu đồ Feature Importance thành 'feature_importance.png'")