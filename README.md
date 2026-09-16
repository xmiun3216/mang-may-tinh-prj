# BÁO CÁO DỰ ÁN - NHÓM 04
**Tên đề tài (Topic 16):** Phát hiện bất thường trong Web Server Access log bằng Machine Learning cơ bản

## 1. Thành viên nhóm và mã sinh viên
*   Đinh Đức Thiện – 2519960051
*   Phạm Khánh Chi – 2519960010
*   Lê Ngọc Minh – 2519960032
*   Lê Phương Anh – 2519960006
*   Nguyễn Việt Hoàng – 2519960018

## 2. Mô tả ngắn bài toán
Dự án giải quyết bài toán phát hiện các truy cập mạng độc hại (DDoS, rà quét lỗ hổng, Zero-day) thông qua phân tích Web Server Access log. Thay vì sử dụng các tập luật tĩnh, nhóm ứng dụng thuật toán **Học máy Không giám sát (Isolation Forest)** để tự động cô lập điểm dị thường (Anomaly) dựa trên hành vi mạng thực tế mà không cần phụ thuộc vào dữ liệu gán nhãn sẵn.

## 3. Môi trường chạy và Python version
*   **Hệ điều hành:** Windows / Linux / macOS
*   **Python version:** Khuyến nghị Python 3.9 trở lên (3.9+).

## 4. Thư viện cần cài và cách cài
Các thư viện phụ thuộc được quản lý trong file `requirements.txt`. Khởi chạy Terminal/Command Prompt tại thư mục gốc của dự án và chạy lệnh sau để cài đặt:
```bash
pip install -r requirements.txt

## 5. Dataset: Nguồn, vị trí file và cách tạo
Nguồn gốc: Dữ liệu Access log thô của Web Server.

Vị trí file thô: data/access.log.

Cách tạo dữ liệu chuẩn bị: Dữ liệu thô được parse và làm sạch, lưu thành data/datanew.csv. Sau đó, được trích xuất thành các ma trận đặc trưng lưu tại results/tables/ thông qua các script tiền xử lý của nhóm.

## 6. Cấu trúc thư mục
Group04_Topic16/
├── Report_Group04.pdf                 # File báo cáo PDF
├── Report_Group04.docx                # File báo cáo Word
├── README.md                          # Tài liệu hướng dẫn
├── requirements.txt                   # Danh sách thư viện Python
├── data/
│   ├── access.log                     # Dữ liệu log thô
│   └── datanew.csv                    # Dữ liệu log đã chuẩn hóa
├── source/                            # Mã nguồn phân tích & mô hình
│   ├── FeatureEngineering/            
│   │   └── request.py                 # Trích xuất đặc trưng mức request
│   ├── parse_lognew.py                # Script tiền xử lý log
│   └── Unsupervised.py                         # Mô hình Isolation Forest
└── results/
    ├── figures/                       # Ảnh biểu đồ trực quan hóa
    │   ├── anomaly_timewindow_15min.png
    │   ├── http_status_distribution.png
    │   ├── pca_data_space.png
    │   ├── phan_bo_anomaly_score.png
    │   ├── phan_bo_muc_do_rui_ro.png
    │   ├── timewindow_by_root_cause.png
    │   └── tuong_quan_url_payload.png
    └── tables/                        # Bảng dữ liệu đầu ra
        ├── aggregated_ip_features.csv 
        ├── Anomalies_Timeline.csv     
        ├── features_comparision.csv   
        └── request_level_features.csv

## 7. Thứ tự chạy các script
Vui lòng thực hiện theo trình tự các bước sau

**Link data gốc (do file data gốc quá lớn): https://drive.google.com/file/d/1BALRNxzBnLYjlBi7LYju92t7N4s0YUXx/view?usp=sharing **

Vui lòng tải file data gốc vào cùng thư mục này trước khi thực hiện bước 1

Bước 1: Tiền xử lý dữ liệu log thô

        python source/parse_lognew.py

Bước 2: Trích xuất đặc trưng mức yêu cầu (Request-level)

        python source/FeatureEngineering/request.py

Bước 3: Huấn luyện mô hình và phát hiện dị biệt (Isolation Forest)

        python source/Unsupervised.py

## 8. Output mong đợi
Sau khi hoàn thành Bước 3, hệ thống sẽ tự động xuất ra các tệp tin tại thư mục results/:

Tables (results/tables/): Các bảng CSV chứa ma trận đặc trưng, phân tích so sánh (features_comparision.csv) và danh sách luồng IP bị cảnh báo bất thường cùng dòng thời gian (Anomalies_Timeline.csv).

Figures (results/figures/): 7 biểu đồ .png trực quan hóa phân bố trạng thái HTTP, tương quan URL, phân bố Anomaly Score, và không gian dữ liệu PCA.

## 9. Ghi chú về random_state và cấu hình tái lập

Nhằm đảm bảo tính tái lập kết quả (Reproducibility), thuật toán Isolation Forest được cấu hình cứng tham số khởi tạo hạt giống ngẫu nhiên: random_state = 42. Điều này đảm bảo trong mọi lần chạy lại script hoặc trên các môi trường máy tính khác nhau, điểm dị biệt (Anomaly Score) và danh sách các IP bị chặn sẽ hội tụ ra kết quả giống hệt nhau 100%.

## 10. Các giới hạn hoặc lưu ý an toàn

Đường dẫn tương đối: Script sử dụng đường dẫn tương đối để đọc/ghi file. Vui lòng luôn gọi lệnh thực thi python từ thư mục gốc của dự án (Group04_Topic16) để tránh lỗi FileNotFoundError.

Bản chất thuật toán: Do sử dụng phương pháp Không giám sát, điểm số cô lập (Anomaly Score) đóng vai trò là "cảnh báo sớm" thay vì bộ luật chặn tĩnh. Cần kết hợp với chuyên gia phân tích để điều chỉnh tham số ngưỡng cắt (contamination) nhằm tránh hiện tượng cảnh báo giả (False Positive) làm gián đoạn người dùng hợp lệ.