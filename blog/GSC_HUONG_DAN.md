# Hướng dẫn submit sitemap vào Google Search Console (GSC)

Mục tiêu: cho Google biết blog của anh tồn tại → crawl + index nhanh → lên top.

## Bước 1: Tạo property trên GSC
1. Vào https://search.google.com/search-console/
2. Đăng nhập bằng tài khoản Google (dùng vanthuonghi@gmail.com cho nhất quán)
3. Ô "URL tiền tố thuộc tính" → dán:
   `https://vanthuonghi.github.io/speedreading-insights/`
4. Nhấn "Tiếp tục"

## Bước 2: Xác minh quyền sở hữu (verification)
GitHub Pages không cho sửa HTML dễ → dùng cách **Tải file xác minh lên repo**:
- GSC sẽ hiện một file `googleXXXX.html`
- Anh báo em tên file → em tạo file đó tại repo ROOT và push lên
- Hoặc đơn giản hơn: chọn phương thức **"Tài khoản Google Analytics"** nếu anh đã liên kết GA (bỏ qua bước này)
- Nhấn "Xác minh"

## Bước 3: Submit sitemap
1. Menu trái → **Sơ đồ trang web (Sitemaps)**
2. Ô "Thêm sơ đồ trang web" → dán: `sitemap.xml`
   (GSC tự ghép thành: https://vanthuonghi.github.io/speedreading-insights/sitemap.xml)
3. Nhấn "Gửi" → trạng thái "Đã gửi thành công"

## Bước 4: Yêu cầu index thủ công (nhanh hơn)
1. Menu trái → **URL Inspection** (thanh kiểm tra URL)
2. Dán từng URL bài viết, ví dụ:
   - `https://vanthuonghi.github.io/speedreading-insights/blog/doc-nhanh-co-that-su-hieu-qua/`
   - `.../blog/ky-thuat-sq3r-doc-hieu-sau/`
   - `.../blog/on-tap-phan-bo-ghi-nho-lau/`
3. Nếu hiện "URL chưa được lập chỉ mục" → nhấn **"Yêu cầu lập chỉ mục"**
4. Google thường xử lý trong vài giờ đến 1-2 ngày.

## Bước 5: Theo dõi
- Sau 1 tuần: vào mục **Hiệu suất (Performance)** xem impressions/clicks
- Viết thêm bài mỗi ngày → cluster tăng authority

## Lưu ý lên top nhanh hơn
- Viết đều đặn (1 bài/ngày) → Google thích site cập nhật
- Internal link chéo (đã làm sẵn giữa 3 bài)
- (Tùy chọn) Trỏ custom domain `blog.speedreading.vn` hoặc `speedreading.vn/blog` vào GitHub Pages → authority cao hơn github.io
- Share bài lên Facebook (có traffic → rank tốt)

---
Em (Hermes) có thể làm thay anh bước 2 (tạo file verify) nếu anh cho tên file.
Các bước 1, 3, 4 anh tự làm trên giao diện GSC (cần đăng nhập Google của anh).
