import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import formats
from django.utils.timezone import now
from django.db.models.signals import pre_save
from django.dispatch import receiver
from ckeditor.fields import RichTextField


class Account(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    default_address = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.username


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)

    def __str__(self):
        return self.name

class Province(models.Model):
    province_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class District(models.Model):
    district_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Ward(models.Model):
    ward_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    district = models.ForeignKey(District, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Address(models.Model):
    address_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Orders(models.Model):
    STATUS_CHOICES = [
        ('Chờ xác nhận', 'Chờ xác nhận'),
        ('Chờ lấy hàng', 'Chờ lấy hàng'),
        ('Đang vận chuyển', 'Đang vận chuyển'),
        ('Đã giao', 'Đã giao'),
        ('Đã hủy', 'Đã hủy'),
    ]
    PAYMENT_CHOICES = [
        ('Chuyển khoản qua ngân hàng', 'Chuyển khoản qua ngân hàng'),
        ('Thanh toán khi nhận hàng', 'Thanh toán khi nhận hàng'),
    ]
    order_id = models.AutoField(primary_key=True)
    order_time = models.DateTimeField(auto_now_add=True)
    delivery_time = models.DateTimeField(null=True)
    status_order = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='Chờ xác nhận'
    )
    address_detail = models.CharField(max_length=255)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    payment_method = models.CharField(
        max_length=50,
        choices=PAYMENT_CHOICES,
        default='Thanh toán khi nhận hàng',
        null=True
    )
    def __str__(self):
        return f'Order {self.order_id} by {self.account}'

class Coupon(models.Model):
    coupon_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    discount = models.DecimalField(max_digits=5, decimal_places=0)
    posting_date = models.DateTimeField(null= True, blank=True)
    expiry_date = models.DateTimeField(null= True, blank=True)
    decription = models.CharField(max_length=200, null= True, blank=True)

    @property
    def is_valid(self):
        """Kiểm tra xem coupon còn hợp lệ không"""
        current_time = now()
        return self.expiry_date is None or self.expiry_date > current_time
    
    def __str__(self):
        return self.name

class Product(models.Model):
    STATUS_CHOICES = [
        ('Còn hàng', 'Còn hàng'),
        ('Hết hàng', 'Hết hàng'),
    ]
    unit_CHOICES = [
        ('g', 'g'),
        ('kg', 'kg'),
    ]
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.FloatField(default=0)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True, default='product_images/default.jpg')
    quantity = models.IntegerField(default=0)
    detail = RichTextField()
    posting_date = models.DateTimeField(auto_now_add=True)
    unit = models.CharField(
        max_length=5,
        choices=unit_CHOICES,
    )
    short_descrip = models.CharField(max_length=500, null=True, blank=True, default=' ')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Còn hàng')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True, blank=True)
    ex_date = models.DateTimeField(null= True, blank=True)
    display_product = models.BooleanField( default= False, blank=True, null=True)
    @property
    def is_coupon_valid(self):  
        return self.coupon and self.coupon.is_valid
    
    def check_expired_coupon(self):
        if self.coupon and not self.coupon.is_valid:
            self.coupon = None  # Xóa coupon khỏi sản phẩm nếu đã hết hạn

    def save(self, *args, **kwargs):
        self.check_expired_coupon()  # Kiểm tra và xóa coupon hết hạn
        if self.quantity == 0:
            self.status = 'Hết hàng'
        else:
            self.status = 'Còn hàng'
        super().save(*args, **kwargs)

    def check_and_mark_expired(self):
        """Kiểm tra và đánh dấu sản phẩm hết hạn vào danh sách hư hỏng."""
        if self.ex_date and datetime.now() > self.ex_date:
            # Tạo một bản ghi trong Defective_Product
            defective_product, created = Defective_Product.objects.get_or_create(
                product=self,
                reason="Hết hạn sử dụng",
                status="Đã xử lý",
                defaults={
                    'quantity': self.quantity,
                }
            )
            if created:  # Nếu vừa tạo bản ghi mới
                # Cập nhật số lượng sản phẩm về 0
                self.quantity = 0
                self.status = 'Hết hàng'
                self.save()
    def __str__(self):
        return self.name
# Tín hiệu để kiểm tra coupon hết hạn và tự động xóa nó khỏi sản phẩm

class OrderDetail(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'OrderDetail: {self.order} - {self.product}'




class Wishlist(models.Model):
    wishlist_id = models.AutoField(primary_key=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f'Wishlist: {self.account} - {self.product}'

class Cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f'Cart: {self.account} - {self.product}'

class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    rating_star = models.IntegerField()
    status = models.CharField(max_length=255)
    img_feedback = models.ImageField(upload_to='img_feedback/', null=True, blank=True)
    feedback_content = models.TextField()
    posting_date = models.DateTimeField(auto_now_add=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f'Feedback {self.feedback_id} for {self.product}'

class Defective_Product(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    date_reported = models.DateTimeField(auto_now_add=True)
    reason = models.TextField()
    status = models.CharField(max_length=100)

    
    def save(self, *args, **kwargs):
        """Giảm số lượng sản phẩm khi tạo Defective_Product"""
        if self.product and self.quantity > 0:
            # Giảm số lượng của sản phẩm
            self.product.quantity -= self.quantity
            self.product.save()  # Lưu lại thay đổi số lượng
        super(Defective_Product, self).save(*args, **kwargs)

    def __str__(self):
        return f"Defective product: {self.product.name}, Quantity: {self.quantity}"

# # Đảm bảo giảm số lượng mỗi khi tạo bản ghi Defective_Product
# @receiver(pre_save, sender=Defective_Product)
# def decrease_product_quantity(sender, instance, **kwargs):
#     """Giảm số lượng sản phẩm khi một Defective_Product được tạo mới"""
#     if instance.product:
#         # Giảm số lượng sản phẩm
#         instance.product.quantity -= instance.quantity
#         instance.product.save()

class Supplier (models.Model):
    supplier_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, null=True, default='')
    phone_number = models.CharField(max_length=10, blank=True, null=True, default='')
    def __str__(self):
            return self.name

class Receipt (models.Model):
    receipt_id = models.AutoField(primary_key=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    date_receipt = models.DateTimeField(null=True, blank=True)

class Receipt_Detail (models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    expiry_date = models.DateTimeField(null=True, blank=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=0)
    unit = models.CharField(max_length=50)

class TitleBlog(models.Model):
    name = models.CharField(max_length=255)  # Tên danh mục blog
    description = models.TextField(null=True, blank=True)  # Mô tả ngắn gọn về danh mục
    created_at = models.DateTimeField(auto_now_add=True)  # Ngày tạo danh mục

    def __str__(self):
        return self.name
    

# Model Blog kế thừa từ TitleBlog, mỗi blog sẽ thuộc một danh mục cụ thể
class Blog(models.Model):
    title_blog = models.ForeignKey(TitleBlog, on_delete=models.CASCADE)  # Liên kết với danh mục
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True)  # Người đăng bài (Admin)
    title = models.CharField(max_length=255)  # Tiêu đề bài viết
    create_date = models.DateTimeField(auto_now_add=True)  # Ngày đăng bài viết
    image_1 = models.ImageField(upload_to='blog_images/', null=True, blank=True, default='default.jpg')  # Ảnh đại diện bài viết
    short_descrip = models.CharField(max_length=500, null=True, blank=True)  # Mô tả ngắn về bài viết
    detail = RichTextField()  # Nội dung chi tiết bài viết
    link = models.URLField(max_length=200, null=True, blank=True)  # Liên kết đến bài viết chi tiết

    def __str__(self):
        return self.title