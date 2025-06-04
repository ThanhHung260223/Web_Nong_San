# myapp/management/commands/update_defective_products.py
from django.core.management.base import BaseCommand
from NongSan.models import Product, Defective_Product
from django.utils.timezone import now

class Command(BaseCommand):
    help = 'Cập nhật sản phẩm hết hạn và chuyển vào bảng Defective_Product'

    def handle(self, *args, **kwargs):
        # Lấy tất cả các sản phẩm đã hết hạn
        expired_products = Product.objects.filter(ex_date__lt=now(), status='Còn hàng')
        
        # Duyệt qua từng sản phẩm hết hạn
        for product in expired_products:
            Defective_Product.objects.create(
                product=product,
                quantity=product.quantity,
                reason='Hết hạn sử dụng',
                status='Hỏng'
            )
            # Cập nhật trạng thái sản phẩm gốc
            product.status = 'Hết hàng'
            product.quantity = 0
            product.save()
        
        self.stdout.write(self.style.SUCCESS('Đã cập nhật sản phẩm hết hạn thành công.'))
