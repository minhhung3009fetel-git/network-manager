================================
🚀 NETWORK DEVICE MANAGER 🚀
================================

Hướng dẫn cài đặt và sử dụng công cụ quản lý thiết bị mạng.

## 1. Yêu Cầu Cần Có (Prerequisites)

Trước khi bắt đầu, hãy đảm bảo máy tính của bạn đã được cài đặt:

* **Python**: Phiên bản 3.9 trở lên.
* **Git**: Để tải mã nguồn từ repository.

---
## 2. Hướng Dẫn Cài Đặt Chi Tiết

Thực hiện theo các bước dưới đây để cài đặt môi trường và chạy ứng dụng.

### Bước 1: Tải mã nguồn về máy

Mở Terminal (trên macOS/Linux) hoặc PowerShell/CMD (trên Windows) và chạy các lệnh sau:

# Tải mã nguồn từ GitHub (thay URL bằng URL repo của bạn)
git clone https://github.com/minhhung3009fetel-git/network-manager

# Di chuyển vào thư mục dự án vừa tải về
cd your-project-name


### Bước 2: Tạo và Kích hoạt Môi trường ảo

Sử dụng môi trường ảo là một bước rất quan trọng để không làm ảnh hưởng đến các thư viện Python hệ thống.

# Tạo một môi trường ảo tên là "venv"
python -m venv venv

# Kích hoạt môi trường ảo vừa tạo
# Trên Windows:
.\venv\Scripts\activate

# Trên macOS hoặc Linux:
source venv/bin/activate

Sau khi kích hoạt, bạn sẽ thấy (venv) xuất hiện ở đầu dòng lệnh của mình.

### Bước 3: Cài đặt các thư viện cần thiết

Dùng lệnh `pip` để cài đặt tất cả các thư viện đã được định nghĩa trong tệp `requirements.txt`.

pip install -r requirements.txt


### Bước 4: Chuẩn bị dữ liệu thiết bị

Chỉnh sửa tệp `data/devices.txt` để thêm vào danh sách các thiết bị mạng bạn muốn quản lý.
Định dạng mỗi dòng như sau: `TênThiếtBị,ĐịaChỉIP,LoạiThiếtBị`

Ví dụ:
HN-Router,10.10.0.1,cisco_ios
HN-Firewall,10.10.0.9,fortinet


---
## 3. Cách Chạy Chương Trình

Sau khi hoàn tất các bước cài đặt, bạn có thể khởi động ứng dụng bằng lệnh sau:

python main.py

Giao diện chính của chương trình sẽ xuất hiện và bạn có thể bắt đầu sử dụng.
