import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.dummy import DummyClassifier
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay

# ==========================================
# 1. ĐỌC DỮ LIỆU TỪ 2 FILE ĐÃ CHIA SẴN
# ==========================================
print("Đang tải dữ liệu...")
train_df = pd.read_csv('timewindow_labeled_train.csv')
test_df = pd.read_csv('timewindow_labeled_test.csv')

# --- LƯU Ý QUAN TRỌNG ---
# Tên cột chứa nhãn trong file CSV là 'weak_label'
TARGET_COL = 'weak_label' 

# Lọc bỏ các cột không dùng để học (chống rò rỉ dữ liệu)
# BẮT BUỘC PHẢI BỎ 'label_reason' ĐỂ MÔ HÌNH KHÔNG BỊ "HỌC VẸT"
cols_to_drop = ['ip', 'timestamp', 'time_window', 'Anomaly_Score', 'label_reason', TARGET_COL]

# Chuẩn bị tập Train
X_train = train_df.drop(columns=[c for c in cols_to_drop if c in train_df.columns])
y_train = train_df[TARGET_COL]

# Chuẩn bị tập Test
X_test = test_df.drop(columns=[c for c in cols_to_drop if c in test_df.columns])
y_test = test_df[TARGET_COL]

# Đảm bảo toàn bộ dữ liệu X là dạng số và không có giá trị NaN gây lỗi
X_train = X_train.apply(pd.to_numeric, errors='coerce').fillna(0)
X_test = X_test.apply(pd.to_numeric, errors='coerce').fillna(0)

print(f"Số lượng mẫu Train: {len(X_train)} | Số lượng mẫu Test: {len(X_test)}")

# ==========================================
# 2. CHẠY MÔ HÌNH BASELINE (DUMMY CLASSIFIER)
# ==========================================
print("\n" + "="*40)
print("KẾT QUẢ BASELINE (DUMMY CLASSIFIER)")
print("="*40)
dummy = DummyClassifier(strategy='most_frequent')
dummy.fit(X_train, y_train)
y_pred_dummy = dummy.predict(X_test)

print("Ma trận nhầm lẫn (Baseline):")
print(confusion_matrix(y_test, y_pred_dummy))
print("\nBáo cáo phân loại (Baseline):")
print(classification_report(y_test, y_pred_dummy, zero_division=0))

# ==========================================
# 3. CHẠY MÔ HÌNH DECISION TREE (SUPERVISED)
# ==========================================
print("\n" + "="*40)
print("KẾT QUẢ DECISION TREE")
print("="*40)
# Giới hạn max_depth=4 để tránh quá khớp và giữ số lượng luật tối ưu
tree_model = DecisionTreeClassifier(max_depth=4, random_state=42)
tree_model.fit(X_train, y_train)
y_pred_tree = tree_model.predict(X_test)

print("Ma trận nhầm lẫn (Decision Tree):")
print(confusion_matrix(y_test, y_pred_tree))
print("\nBáo cáo phân loại (Decision Tree):")
print(classification_report(y_test, y_pred_tree, zero_division=0))


# ==========================================
# 4. XUẤT 3 BIỂU ĐỒ (VISUALIZATION)
# ==========================================
print("\n" + "="*40)
print("ĐANG XUẤT BIỂU ĐỒ (VISUALIZATION)...")
print("="*40)

# Lấy danh sách nhãn tự động ('Anomaly', 'Normal') để vẽ biểu đồ
classes = sorted(y_test.unique().astype(str).tolist())

# --- Biểu đồ 1: Ma trận nhầm lẫn (Confusion Matrix) ---
plt.figure(figsize=(8, 6))
disp = ConfusionMatrixDisplay.from_estimator(
    tree_model, X_test, y_test, 
    display_labels=classes, 
    cmap=plt.cm.Blues
)
plt.title("Biểu đồ 1: Ma trận nhầm lẫn (Decision Tree)")
plt.savefig("confusion_matrix.png", dpi=300, bbox_inches='tight')
plt.close('all') 
print("- Đã lưu biểu đồ Ma trận nhầm lẫn thành 'confusion_matrix.png'")

# --- Biểu đồ 2: Cấu trúc Cây quyết định (Decision Tree Structure) ---
# Đặt figsize cực lớn (40, 15) để chữ không bị đè lên nhau
plt.figure(figsize=(40, 15)) 
plot_tree(tree_model, 
          feature_names=list(X_train.columns), 
          class_names=classes, 
          filled=True, rounded=True, fontsize=12)
plt.title("Biểu đồ 2: Cấu trúc mô hình Cây quyết định (max_depth=4)", fontsize=20)
plt.savefig("decision_tree_structure.png", dpi=300, bbox_inches='tight')
plt.close('all')
print("- Đã lưu biểu đồ Cấu trúc cây thành 'decision_tree_structure.png'")

# --- Biểu đồ 3: Mức độ quan trọng của Đặc trưng (Feature Importance) ---
importances = tree_model.feature_importances_
indices = np.argsort(importances)[::-1] 
features = X_train.columns

plt.figure(figsize=(10, 6))
plt.title("Biểu đồ 3: Mức độ quan trọng của các Đặc trưng (Feature Importance)")
plt.bar(range(X_train.shape[1]), importances[indices], align="center", color='teal')
plt.xticks(range(X_train.shape[1]), [features[i] for i in indices], rotation=45, ha='right')
plt.xlim([-1, X_train.shape[1]])
plt.tight_layout()
plt.savefig("feature_importance.png", dpi=300)
plt.close('all')
print("- Đã lưu biểu đồ Feature Importance thành 'feature_importance.png'")

print("\nHOÀN TẤT! Hãy kiểm tra 3 file ảnh vừa được tạo ra trong thư mục.")