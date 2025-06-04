# TỔNG QUAN

## 1.1. GIỚI THIỆU
Trong những năm gần đây, an toàn thực phẩm đã trở thành vấn đề nhức nhối của xã hội. Theo báo cáo của các tổ chức y tế, hàng triệu người mỗi năm phải đối mặt với rủi ro sức khỏe do sử dụng thực phẩm không đạt chuẩn. Trong đó, nông sản, một trong những nguồn cung cấp thực phẩm chính, cũng không nằm ngoài thực trạng này. Điều này làm gia tăng nhu cầu cấp thiết về các sản phẩm nông sản sạch, đảm bảo chất lượng và có nguồn gốc rõ ràng.

Bên cạnh đó, người nông dân, dù sở hữu các sản phẩm đạt tiêu chuẩn, lại gặp nhiều khó khăn trong việc tiếp cận thị trường và quảng bá thương hiệu. Nhiều kênh phân phối hiện nay còn tồn tại những bất cập, như thiếu minh bạch về thông tin sản phẩm, quy trình giao dịch phức tạp và chi phí trung gian cao.

Nhận thức được những vấn đề trên, nhóm đã quyết định lựa chọn đề tài **“Ứng dụng Django xây dựng trang web bán nông sản sạch”**. Mục tiêu của dự án là:
- Tạo ra một nền tảng trực tuyến giúp người tiêu dùng dễ dàng tiếp cận sản phẩm nông sản sạch.
- Hỗ trợ người sản xuất quản lý và phân phối sản phẩm hiệu quả.
- Ứng dụng công nghệ để minh bạch hóa thông tin sản phẩm, tối ưu quy trình mua bán và giảm chi phí giao dịch.

Với công nghệ Django, nhóm kỳ vọng xây dựng một hệ thống thân thiện với người dùng, linh hoạt và có khả năng mở rộng trong tương lai. Đề tài này không chỉ giải quyết các vấn đề thực tiễn mà còn đóng góp vào việc xây dựng một xã hội tiêu dùng an toàn, minh bạch và bền vững.

---

## 1.2. BỐI CẢNH NÔNG SẢN SẠCH HIỆN NAY

Trong bối cảnh ngành nông nghiệp đang phải đối mặt với hàng loạt thách thức, từ việc lạm dụng hóa chất, suy thoái đất đai, biến đổi khí hậu đến vấn nạn nông sản "bẩn," khái niệm nông sản sạch đã trở thành một hướng đi không thể thiếu. Thực phẩm sạch không chỉ đảm bảo sức khỏe cho người tiêu dùng mà còn mở ra cánh cửa cho sự phát triển bền vững của nông nghiệp, đặc biệt tại Việt Nam – quốc gia có nền kinh tế nông nghiệp truyền thống lâu đời.

### 1.2.1. NHỮNG VẤN ĐỀ CỦA NÔNG SẢN HIỆN NAY

**a. Lạm Dụng Hóa Chất Trong Nông Nghiệp**

Một trong những vấn đề nhức nhối nhất hiện nay là việc lạm dụng thuốc trừ sâu, thuốc kích thích tăng trưởng, và phân bón hóa học trong quá trình sản xuất nông sản. Điều này không chỉ làm giảm chất lượng sản phẩm mà còn gây hại nghiêm trọng đến sức khỏe người tiêu dùng. Theo các báo cáo y tế, việc tiêu thụ thực phẩm có dư lượng thuốc trừ sâu cao có thể dẫn đến các bệnh mãn tính như ung thư, suy giảm miễn dịch, và rối loạn nội tiết.

Không chỉ dừng lại ở sức khỏe con người, việc sử dụng hóa chất không kiểm soát còn gây ô nhiễm đất và nguồn nước, làm mất cân bằng hệ sinh thái tự nhiên. Đất đai bị thoái hóa, nguồn nước bị nhiễm độc, khiến việc canh tác ngày càng khó khăn, đẩy người nông dân vào vòng luẩn quẩn.

**b. Nông Sản "Bẩn" Tràn Lan**

Việc thiếu kiểm soát chất lượng trong khâu sản xuất và phân phối đã khiến thị trường xuất hiện tràn lan các loại nông sản không rõ nguồn gốc, không đạt tiêu chuẩn an toàn. Người tiêu dùng ngày càng mất niềm tin vào chất lượng thực phẩm, đặc biệt là rau củ quả, thịt cá.

Tại nhiều vùng quê, người nông dân thường phun thuốc hóa học ngay trước ngày thu hoạch để đạt năng suất cao. Điều này không chỉ làm giảm giá trị dinh dưỡng mà còn tiềm ẩn nguy cơ ngộ độc thực phẩm.

**c. Tình Trạng "Được Mùa Mất Giá"**

Thực trạng được mùa mất giá là vấn đề tồn tại lâu dài trong nông nghiệp Việt Nam. Mỗi mùa vụ, người nông dân thường đối mặt với nguy cơ sản phẩm bị tồn đọng hoặc bán dưới giá thành sản xuất do thiếu đầu ra ổn định. Trong khi đó, người tiêu dùng lại phải mua nông sản với giá cao do chi phí vận chuyển, lưu kho, và trung gian.

---

### 1.2.2. NÔNG SẢN SẠCH LỜI GIẢI CHO TÌNH TRẠNG HIỆN NAY

**a. Định Nghĩa Nông Sản Sạch**

Nông sản sạch là các sản phẩm được sản xuất theo quy trình tự nhiên, hạn chế hoặc không sử dụng các hóa chất độc hại. Đây là sản phẩm không chỉ an toàn cho người sử dụng mà còn thân thiện với môi trường, góp phần bảo vệ hệ sinh thái và đảm bảo sự bền vững trong nông nghiệp.

**b. Lợi Ích Của Nông Sản Sạch**

- **Bảo vệ sức khỏe cộng đồng:**  
Thực phẩm sạch giúp người tiêu dùng tránh được các nguy cơ từ hóa chất độc hại, đồng thời cung cấp nguồn dinh dưỡng tốt hơn. Các loại rau củ quả sạch thường giàu vitamin và khoáng chất, hỗ trợ tăng cường hệ miễn dịch và nâng cao chất lượng cuộc sống.

- **Bảo vệ môi trường:**  
Quy trình sản xuất nông sản sạch ưu tiên sử dụng phân bón hữu cơ, thuốc bảo vệ thực vật sinh học, và các biện pháp tự nhiên nhằm hạn chế tác động xấu đến môi trường. Điều này giúp đất đai được phục hồi, nguồn nước không bị ô nhiễm, và giảm thiểu khí thải gây hiệu ứng nhà kính.

- **Tăng giá trị nông sản:**  
Sản phẩm sạch không chỉ đáp ứng nhu cầu trong nước mà còn dễ dàng đạt các tiêu chuẩn khắt khe của thị trường quốc tế. Điều này mở ra cơ hội xuất khẩu, nâng cao thu nhập cho người nông dân và doanh nghiệp.

---

### 1.2.3. GIẢI PHÁP THÚC ĐẨY NÔNG SẢN SẠCH TẠI VIỆT NAM

- **Xây Dựng Chuỗi Sản Xuất Bền Vững**  
  Thiết lập chuỗi giá trị từ khâu trồng trọt, chăm sóc đến thu hoạch và phân phối. Khuyến khích và nhân rộng các mô hình nông nghiệp hữu cơ, tuần hoàn.

- **Tăng Cường Kiểm Soát Chất Lượng**  
  Nhà nước cần ban hành và thực thi tiêu chuẩn nghiêm ngặt, phổ biến hệ thống chứng nhận như VietGAP, GlobalGAP.

- **Nâng Cao Nhận Thức Người Tiêu Dùng**  
  Đẩy mạnh truyền thông, hội chợ nông sản, giáo dục cộng đồng để tăng cường hiểu biết về lợi ích của thực phẩm sạch.

- **Hỗ Trợ Người Nông Dân Chuyển Đổi Mô Hình Canh Tác**  
  Cung cấp hỗ trợ tài chính, kỹ thuật và thị trường tiêu thụ cho người nông dân.

- **Xây Dựng Thị Trường Tiêu Thụ Ổn Định**  
  Doanh nghiệp và hợp tác xã làm trung gian kết nối nông dân với người tiêu dùng, sử dụng sàn thương mại điện tử, siêu thị chuyên cung cấp nông sản sạch.

---

## 1.3. CƠ SỞ LÝ THUYẾT

### 1.3.1. DJANGO

**a. Định nghĩa Django là gì?**  
Django là một web framework mã nguồn mở, được viết bằng Python, giúp xây dựng ứng dụng web nhanh và an toàn, hỗ trợ quản lý cơ sở dữ liệu, xác thực người dùng, và giao diện.

**b. Đặc điểm nổi bật của Django**

| Đặc điểm              | Ý nghĩa                                                                                   |
|-----------------------|------------------------------------------------------------------------------------------|
| DRY (Don’t Repeat Yourself) | Hạn chế viết lại mã bằng cách tái sử dụng các thành phần trong framework.             |
| Bảo mật cao           | Bảo vệ chống lại các lỗ hổng như SQL Injection, CSRF, XSS, v.v.                          |
| Tích hợp admin site   | Giao diện quản trị tự động dựa trên mô hình dữ liệu đã định nghĩa.                       |
| Hỗ trợ ORM            | Quản lý dữ liệu dễ dàng thông qua model Python, không cần SQL phức tạp.                   |
| Mở rộng dễ dàng       | Hỗ trợ tích hợp nhiều ứng dụng, thư viện Python qua pip install.                         |

**c. Tại sao chọn Django cho dự án này?**  
- Phù hợp dự án nhỏ và vừa, triển khai nhanh.  
- Hỗ trợ sẵn tính năng bảo mật, xác thực người dùng.  
- Dễ quản lý dữ liệu sản phẩm nông sản đa dạng.  
- Tính năng quản trị giúp người bán và quản trị viên dễ dàng cập nhật thông tin.

---

## 1.4. MỤC TIÊU NGHIÊN CỨU

- Xây dựng hệ thống website bán nông sản sạch thân thiện, dễ sử dụng.  
- Đảm bảo các thông tin về sản phẩm được cập nhật chính xác, minh bạch.  
- Tạo điều kiện cho người sản xuất dễ dàng quản lý sản phẩm, đơn hàng.  
- Nâng cao trải nghiệm mua sắm cho người tiêu dùng với giao diện hiện đại, tiện lợi.  

---

## 1.5. PHẠM VI NGHIÊN CỨU

- **Phạm vi lĩnh vực:** Nông sản sạch, thương mại điện tử.  
- **Phạm vi địa lý:** Tập trung vào thị trường Việt Nam.  
- **Phạm vi chức năng:** Quản lý sản phẩm, giỏ hàng, đơn hàng, tài khoản người dùng.

---

## 1.6. Ý NGHĨA CỦA ĐỀ TÀI

- Giúp người tiêu dùng dễ dàng tiếp cận nông sản sạch, đảm bảo sức khỏe.  
- Hỗ trợ người nông dân và doanh nghiệp giảm chi phí trung gian, tăng lợi nhuận.  
- Góp phần thúc đẩy nông nghiệp bền vững và phát triển thương mại điện tử trong lĩnh vực nông nghiệp.

---

**Kết luận:**  
Dự án xây dựng trang web bán nông sản sạch bằng Django mang lại nhiều lợi ích thực tiễn và có ý nghĩa xã hội lớn, góp phần phát triển nền nông nghiệp xanh, sạch và bền vững.

