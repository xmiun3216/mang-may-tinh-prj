# BÁO CÁO DỰ ÁN - NHÓM 04
**TOPIC 16:** Phát hiện bất thường trong Web Server Access log bằng Machine Learning cơ bản

## 1. Thành viên nhóm
*   Đinh Đức Thiện – 2519960051
*   Phạm Khánh Chi – 2519960010
*   Lê Ngọc Minh – 2519960032
*   Lê Phương Anh – 2519960006
*   Nguyễn Việt Hoàng – 2519960018

## 2. Kiến trúc Hệ thống
Dự án áp dụng phương pháp **Học không giám sát (Unsupervised Learning)** để giải quyết bài toán phát hiện xâm nhập và bất thường trên Web Server:
*   **Thuật toán cốt lõi:** `Isolation Forest`.
*   **Cơ chế hoạt động:** Hệ thống không phụ thuộc vào dữ liệu gán nhãn sẵn. Dữ liệu sau khi trích xuất đặc trưng mức request sẽ được đưa vào mô hình để tính toán điểm số dị biệt (Anomaly Score), tự động phân lập các hành vi tấn công tàng hình, dò quét lỗ hổng hoặc đột biến lưu lượng bất thường.

## 3. Cấu trúc thư mục dự án
```text
Group04_Topic16/
├── Report_Group04.pdf                 # File báo cáo PDF
├── Report_Group04.docx                # File báo cáo Word
├── README.md                          # Hướng dẫn chạy dự án
├── requirements.txt                   # Danh sách thư viện Python phụ thuộc
├── data/
│   ├── access.log                     # Dữ liệu log thô
│   └── datanew.csv                    # Dữ liệu log đã chuẩn hóa
├── FeatureEngineering/                # Module trích xuất đặc trưng
│   ├── request.py                     # Script xử lý trích xuất mức request
│   └── request_level_features.csv     # Bảng đặc trưng mức request đầu ra
├── source/                            # Mã nguồn phân tích & mô hình
│   ├── parse_lognew.py                # Script tiền xử lý log
│   └── tv3.py                         # Mô hình Isolation Forest
└── results/
    ├── figures/                       # Ảnh biểu đồ kết quả
    └── tables/                        # Bảng dữ liệu đầu ra
        ├── aggregated_ip_features.csv # Đặc trưng tổng hợp theo IP (Từ TV3)
        └── Anomalies_Timeline.csv     # Dòng thời gian điểm bất thường (Từ TV3)

## 4. Cài đặt môi trường
Mở Terminal/Command Prompt tại thư mục gốc của dự án và cài đặt các thư viện cần thiết:

        pip install -r requirements.txt

## 5. Hướng dẫn chạy chương trình
Chạy lần lượt các thư mục python trong thư mục 'source/':

**Bước 1: Tiền xử lí dữ liệu log thô**
Làm sạch, bóc tách các trường từ file access.log và chuẩn hóa về datanew.csv.

        python source/parse_lognew.py   

**Bước 2: Trích xuất đặc trưng mức yêu cầu (Request-level)**
Xử lý dữ liệu chuẩn hóa thành ma trận đặc trưng mô tả hành vi mạng ở mức từng request, sinh ra file FeatureEngineering/request_level_features.csv làm dữ liệu đầu vào cho mô hình:

        python FeatureEngineering/request.py

**Bước 3: Huấn luyện và phát hiện dị biệt (Isolation Forest)**
Chạy mô hình học không giám sát để tính toán điểm bất thường (Anomaly Score), phân lập các truy cập độc hại và xuất báo cáo kết quả:

        python source/Unsupervised.py

**Đầu ra (Outcomes) của mô hình Isolation Forest**:
Sau khi chạy xong Bước 3, mô hình sẽ tự động sinh ra 2 file báo cáo lưu tại thư mục results/tables/ (hoặc thư mục gốc tùy cấu hình code):

aggregated_ip_features.csv: Bảng tổng hợp các đặc trưng hành vi nhóm theo từng địa chỉ IP.

Anomalies_Timeline.csv: Bảng thống kê chi tiết dòng thời gian của các luồng truy cập bị cắm cờ bất thường.