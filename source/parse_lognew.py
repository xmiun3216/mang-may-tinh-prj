import re
import csv
from datetime import datetime
import pandas as pd

# Regex chuẩn để bóc tách 6 thành phần từ file access log
LOG_PATTERN = re.compile(
    r'^(\S+) \S+ \S+ \[([^\]]+)\] "([A-Z]+)\s+(\S+)\s+.*?" (\d{3}) (\d+|-)'
)

def parse_and_clean_log(log_path, csv_path, max_lines=100000):
    print("Đang tiến hành đọc và xử lý file log...")
    with open(log_path, 'r', encoding='utf-8') as f_in, \
         open(csv_path, 'w', newline='', encoding='utf-8') as f_out:
        
        writer = csv.writer(f_out)
        # BỔ SUNG: Thêm cột 'uri_raw' để quét mã độc, giữ nguyên 'uri' để đếm Endpoint
        writer.writerow(['IP', 'timestamp', 'method', 'uri_raw', 'uri', 'status_code', 'bytes'])
        
        parsed_count = 0
        error_count = 0

        for line in f_in:
            if parsed_count >= max_lines:
                break
                
            match = LOG_PATTERN.match(line)
            if match:
                ip = match.group(1)
                raw_time = match.group(2)
                method = match.group(3)
                
                # TỐI ƯU: Lấy chuỗi gốc (uri_raw) và chuỗi đã cắt (uri)
                uri_raw = match.group(4)
                uri = uri_raw.split('?')[0]
                
                # Ép kiểu dữ liệu số nguyên
                status_code = int(match.group(5))
                raw_bytes = match.group(6)
                bytes_sent = int(raw_bytes) if raw_bytes != '-' else 0
                
                # Ép chuẩn định dạng thời gian
                try:
                    clean_time_str = raw_time.split(' ')[0] 
                    dt_obj = datetime.strptime(clean_time_str, "%d/%b/%Y:%H:%M:%S")
                    formatted_time = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    formatted_time = raw_time 

                # BỔ SUNG: Ghi thêm uri_raw vào file CSV
                writer.writerow([ip, formatted_time, method, uri_raw, uri, status_code, bytes_sent])
                parsed_count += 1
            else:
                error_count += 1
                
    print(f"Hoàn tất! Đã xuất thành công {parsed_count} dòng vào file {csv_path}")
    if error_count > 0:
        print(f"Có {error_count} dòng không đúng định dạng chuẩn đã được bỏ qua.")

if __name__ == "__main__":
    # Đường dẫn file log gốc của bạn
    log_file_path = "../data/raw/access.log"
    
    # XUẤT RA FILE MỚI: datanew.csv
    csv_file_path = "../data/processed/datanew.csv"
    
    # Chạy với 100k dòng 
    parse_and_clean_log(log_file_path, csv_file_path, max_lines=100000)

    # Đọc lại từ file datanew.csv để kiểm tra thời gian
    df = pd.read_csv(csv_file_path)
    time_start = df['timestamp'].iloc[0]
    time_end = df['timestamp'].iloc[-1]

    print(f"Mẫu dữ liệu bắt đầu từ: {time_start}")
    print(f"Mẫu dữ liệu kết thúc lúc: {time_end}")