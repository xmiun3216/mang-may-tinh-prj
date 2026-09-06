#You can log to 5 different levels: debug, infor, warning, error, critical   
import logging 
#In default mode, messages is only displayed with a severity level of warning or higher. To change it, we use: basicConfig
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',         
                    datefmt = '%m/%d/%Y %H:%M:%S')
# w: write: ghi đè, tức mỗi lần khởi tạo thì sẽ ghi lại vào file khác, ko ghi tiếp và file cũ 
logging.debug("Sử dụng trong quá trình phát triển & gỡ lỗi | Ghi lại các thông tin chi tiết để chẩn đoán vấn đề")
logging.info("Xác nhận rằng mọi thứ đang hoạt động đúng như mong đợi | Ghi lại các sự kiện mang tính cột mốc")
logging.warning("Dùng khi có điều bất thường đã xảy ra or có thể xảy ra trong tương lai gần | Cảnh báo về các tình huống ko lý tưởng chưa gây lỗi")                                                                                                       
logging.error("Khi có vấn đề nghiêMm trọng, phần mềm ko thể thực hiện 1 chức năng nào đó | Ghi lại các lỗi khiến một luồng xử lý bị gián ")
logging.critical("Khi có lỗi rất nghiêm trọng, chương trình ko thể chạy được | Báo động đỏ")

import helper

