from multiprocessing import Value
from django.contrib import admin
from django.forms import CharField
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.shortcuts import redirect, render, reverse
from django.urls import path
from .models import Account, Category, Product, Orders, Cart, OrderDetail, Coupon, Wishlist, Feedback, Address, Province, District, Ward, Defective_Product, Receipt, Receipt_Detail, Supplier, Blog, TitleBlog
from .forms import ProductForm, CartForm, CategoryForm, OrdersForm, WishlistForm 
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from datetime import datetime
from django.utils import timezone
from datetime import timedelta




class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        fields = ('name', 'image', 'category', 'price', 'quantity', 'detail', 'short_descrip', 'unit', 'coupon')  # You can add more fields as needed
        import_id_fields = ('name',)


class ProductAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    form = ProductForm
    list_display = ('formatted_id', 'formatted_name', 'thumbnail', 'formatted_price', 'formatted_quantity', 'formatted_category', 'formatted_ex_date', 'formatted_status', 'row_actions')
    search_fields = ('name', 'price')
    ordering = ('product_id',)
    resource_class = ProductResource
    list_filter = ('category','status')
    def has_module_permission(self, request):
        """Ẩn model khỏi trang admin chính"""
        return False
    
    def format_centered(self, value):
        return format_html(
            '<div style="display: flex; align-items: center; justify-content: center; height: 70px;">{}</div>',
            value
        )

    
    def formatted_id(self, obj):
        return self.format_centered(obj.product_id)
    formatted_id.short_description = 'ID'

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="70" height="70" />', obj.image.url)
        return "No Image"
    thumbnail.short_description = 'Ảnh'

    def formatted_name(self, obj):
        return self.format_centered(obj.name)
    formatted_name.short_description = 'Tên Sản Phẩm'

    def formatted_price(self, obj):
        if obj.price == 0:
            return format_html(
            '<span style="color: red; font-weight: bold; display: flex; align-items: center; justify-content: center;">⚠ Cảnh báo: Giá hiện tại không hợp lệ</span>'
        )
        formatted = f"{obj.price * 1000:,.0f}₫"
        return self.format_centered(formatted)
    formatted_price.short_description = 'Giá'

    def formatted_quantity(self, obj):
        if obj.quantity == 0:
            return format_html(
            '<span style="color: red; font-weight: bold; display: flex; align-items: center; justify-content: center;">0</span>'
        )
        return self.format_centered(obj.quantity)
    formatted_quantity.short_description = 'Số Lượng'

    def formatted_category(self, obj):
        return self.format_centered(obj.category)
    formatted_category.short_description = 'Danh Mục'

    def formatted_status(self, obj):
        if obj.quantity == 0 or obj.status.lower() == 'hết hàng':
            return format_html(
            '<span style="color: red; font-weight: bold; display: flex; align-items: center; justify-content: center;">⚠ Cảnh báo: Hết hàng</span>'
        )
        if  10 > obj.quantity > 0 :
            return format_html(
            '<span style="color: orange; font-weight: bold; display: flex; align-items: center; justify-content: center;">⚠ Cảnh báo: Sắp hết hàng</span>'
        )
        return self.format_centered(obj.status)
    formatted_status.short_description = 'Trạng Thái'

    def formatted_ex_date(self, obj):
        # Kiểm tra nếu sản phẩm có hạn sử dụng
        if obj.ex_date:
            # Chuyển đổi ex_date thành aware datetime nếu nó chưa có múi giờ
            if obj.ex_date.tzinfo is None:
                obj.ex_date = timezone.make_aware(obj.ex_date)

            # Lấy thời gian hiện tại
            now = timezone.now()
             # Nếu sản phẩm hết hạn, chuyển vào bảng hư hỏng
            # Tính toán sự khác biệt giữa ngày hết hạn và ngày hiện tại
            time_diff = obj.ex_date - now

            # Kiểm tra nếu sản phẩm đã hết hạn
            if obj.ex_date < now:
                return format_html(
                    '<span style="color: red; font-weight: bold; display: flex; align-items: center; justify-content: center;">Hết hạn ({})</span>',
                    obj.ex_date.strftime('%d-%m-%Y')
                )
            # Kiểm tra nếu sản phẩm sắp hết hạn (ví dụ trong vòng 3 ngày)
            elif time_diff <= timedelta(days=3):
                return format_html(
                    '<span style="color: orange; font-weight: bold; display: flex; align-items: center; justify-content: center;">Sắp hết hạn ({})</span>',
                    obj.ex_date.strftime('%d-%m-%Y')
                )

            # Nếu không hết hạn và không sắp hết hạn
            return self.format_centered(obj.ex_date.strftime('%d-%m-%Y'))

        return self.format_centered('Không có hạn sử dụng')

    formatted_ex_date.short_description = 'HSD'
    
    def row_actions(self, obj):
        edit_url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name), args=[obj.pk])
        delete_url = reverse('admin:%s_%s_delete' % (obj._meta.app_label, obj._meta.model_name), args=[obj.pk])

        return format_html(
            '<div style="display: flex; align-items: center; justify-content: center; height: 70px;">'
            '<a class="button" href="{}" style="color: blue; margin-right: 10px;">Sửa</a>'
            '<a class="button" href="{}" style="color: red;">Xóa</a>'
            '</div>',
            edit_url, delete_url
        )
    row_actions.short_description = ' '

    class Media:
        css = {
            'all': ('/static/css/admin_custom.css',)  # Đường dẫn đến file CSS tùy chỉnh
        }

class DefectiveProductResource(resources.ModelResource):
    class Meta:
        model = Defective_Product
        fields = ('product', 'quantity', 'reason', 'status')  # You can add more fields as needed
        import_id_fields = ('product',)

class DefectiveProductAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('formatted_product', 'formatted_image', 'formatted_quantity', 'formatted_date_reported', 'formatted_reason', 'formatted_status', 'row_actions')
    search_fields = ('product__name', 'status')
    ordering = ('date_reported',)
    resource_class = DefectiveProductResource
    def has_module_permission(self, request):
        """Ẩn model khỏi trang admin chính"""
        return False

    def format_centered(self, value):
        return format_html(
            '<div style="display: flex; align-items: center; justify-content: center; height: 70px;">{}</div>',
            value
        )

    def formatted_product(self, obj):
        return self.format_centered(obj.product.name)
    formatted_product.short_description = 'Sản phẩm'

    def formatted_image(self, obj):
        """Hiển thị ảnh sản phẩm"""
        if obj.product.image:
            return format_html('<img src="{}" width="70" height="70" />', obj.product.image.url)
        return "No Image"
    formatted_image.short_description = 'Ảnh'

    def formatted_quantity(self, obj):
        return self.format_centered(obj.quantity)
    formatted_quantity.short_description = 'Số lượng'

    def formatted_date_reported(self, obj):
        return self.format_centered(obj.date_reported.strftime('%Y-%m-%d %H:%M:%S'))
    formatted_date_reported.short_description = 'Ngày nhập'

    def formatted_reason(self, obj):
        return self.format_centered(obj.reason)
    formatted_reason.short_description = 'Lý do'

    def formatted_status(self, obj):
        return self.format_centered(obj.status)
    formatted_status.short_description = 'Trạng thái'

    def row_actions(self, obj):
        edit_url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name), args=[obj.pk])
        delete_url = reverse('admin:%s_%s_delete' % (obj._meta.app_label, obj._meta.model_name), args=[obj.pk])

        return format_html(
            '<div style="display: flex; align-items: center; justify-content: center; height: 70px;">'
            '<a class="button" href="{}" style="color: blue; margin-right: 10px;">Sửa</a>'
            '<a class="button" href="{}" style="color: red;">Xóa</a>'
            '</div>',
            edit_url, delete_url
        )
    row_actions.short_description = ' '

    class Media:
        css = {
            'all': ('/static/css/admin_custom.css',)  # Đường dẫn đến file CSS tùy chỉnh
        }


class BaseAdmin(admin.ModelAdmin):
    def format_centered(self, value):
        return format_html(
            '<div style="display: flex; align-items: center; justify-content: center; height: 70px;">{}</div>',
            value
        )

    def row_actions(self, obj):
        edit_url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name), args=[obj.pk])
        delete_url = reverse('admin:%s_%s_delete' % (obj._meta.app_label, obj._meta.model_name), args=[obj.pk])

        return format_html(
            '<div style="display: flex; align-items: center; justify-content: center; height: 70px;">'
            '<a class="button" href="{}" style="color: blue; margin-right: 10px;">Sửa</a>'
            '<a class="button" href="{}" style="color: red;">Xóa</a>'
            '</div>',
            edit_url, delete_url
        )
    row_actions.short_description = ' '
    
    def get_row_actions(self, obj):
        return self.row_actions(obj)
    

class AccountResource(resources.ModelResource):
    class Meta:
        model = Account
        fields = ('avatar', 'phone_number', 'default_address', 'password', 'username', 'firstname','lastname', 'emailaddress:')  # You can add more fields as needed
        import_id_fields = ('username',)

class AccountAdmin(ImportExportModelAdmin, BaseAdmin):
    def has_module_permission(self, request):
        """Ẩn model khỏi trang admin chính"""
        return False
    list_display = ('formatted_username', 'thumbnail', 'formatted_email', 'formatted_phone_number', 'formatted_default_address', 'row_actions')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('username',)

    resource_class = AccountResource

    def thumbnail(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="70" height="70" />', obj.avatar.url)
        return "No Image"
    thumbnail.short_description = 'Ảnh'

    def formatted_username(self, obj):
        return obj.username
    formatted_username.short_description = 'Tên đăng nhập'

    def formatted_email(self, obj):
        return (obj.email if obj.email else "Chưa có email")
    formatted_email.short_description = 'Email'

    def formatted_phone_number(self, obj):
        return (obj.phone_number if obj.phone_number else "Chưa có SDT")
    formatted_phone_number.short_description = 'SDT'

    def formatted_default_address(self, obj):
        return (obj.default_address if obj.default_address else "Chưa có địa chỉ")
    formatted_default_address.short_description = 'Địa chỉ'
    

class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        fields = ('name', 'image')  
        import_id_fields = ('name',)

class CategoryAdmin(ImportExportModelAdmin, BaseAdmin):
    list_display = ('formatted_category_id', 'formatted_name', 'thumbnail', 'row_actions')
    search_fields = ('name',)
    ordering = ('category_id',)
    resource_class = CategoryResource

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="70" height="70" />', obj.image.url)
        return "No Image"
    thumbnail.short_description = 'Ảnh'
    def formatted_category_id(self, obj):
        return obj.category_id
    formatted_category_id.short_description = 'ID'

    def formatted_name(self, obj):
            return obj.name
    formatted_name.short_description = 'Tên danh mục'

    def has_module_permission(self, request):
        """Ẩn model khỏi trang admin chính"""
        return False

# class ProvinceAdmin(BaseAdmin):
#     def has_module_permission(self, request):
#         """Ẩn model khỏi trang admin chính"""
#         return False
#     list_display = ('province_id', 'name', 'row_actions')
#     search_fields = ('name',)
#     ordering = ('province_id',)

# class DistrictAdmin(BaseAdmin):
#     def has_module_permission(self, request):
#         """Ẩn model khỏi trang admin chính"""
#         return False
#     list_display = ('district_id', 'name', 'formatted_province', 'row_actions')
#     search_fields = ('name',)
#     ordering = ('district_id',)

#     def formatted_province(self, obj):
#         return self.format_centered(obj.province.name if obj.province else "No Province")
#     formatted_province.short_description = 'Tỉnh/Thành phố'

# class WardAdmin(BaseAdmin):
#     def has_module_permission(self, request):
#         """Ẩn model khỏi trang admin chính"""
#         return False
#     list_display = ('ward_id', 'name', 'formatted_district', 'row_actions')
#     search_fields = ('name',)
#     ordering = ('ward_id',)

#     def formatted_district(self, obj):
#         return self.format_centered(obj.district.name if obj.district else "No District")
#     formatted_district.short_description = 'Quận/Huyện'

class AddressAdmin(BaseAdmin):
    def has_module_permission(self, request):
        """Ẩn model khỏi trang admin chính"""
        return False
    list_display = ('address_id', 'name', 'formatted_ward', 'formatted_account', 'row_actions')
    search_fields = ('name',)
    ordering = ('address_id',)

    def formatted_ward(self, obj):
        return self.format_centered(obj.ward.name if obj.ward else "No Ward")
    formatted_ward.short_description = 'Đường'

    def formatted_account(self, obj):
        return self.format_centered(obj.account.username if obj.account else "No Account")
    formatted_account.short_description = 'Tài khoản'

class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        fields = ('name', 'image')  
        import_id_fields = ('name',)

# class OrdersAdmin(BaseAdmin):
#     def has_module_permission(self, request):
#         """Ẩn model khỏi trang admin chính"""
#         return False
#     list_display = ('order_id', 'order_time', 'delivery_time', 'status_order', 'formatted_account', 'price', 'row_actions')
#     search_fields = ('status_order',)
#     ordering = ('order_id',)

#     def formatted_account(self, obj):
#         return self.format_centered(obj.account.username if obj.account else "No Account")
#     formatted_account.short_description = 'Account'

class OrdersAdmin(BaseAdmin):
    def has_module_permission(self, request):
        """Ẩn model khỏi trang admin chính"""
        return False

    list_display = ('formatted_order_id', 'formatted_order_time', 'formatted_delivery_time', 'status_with_warning', 'formatted_account', 'formatted_price', 'formatted_payment_method', 'row_actions')
    search_fields = ('status_order',)
    ordering = ('order_id',)
    list_filter = ('status_order',)  # Bộ lọc trạng thái đơn hàng

    def formatted_account(self, obj):
        return (obj.account.username if obj.account else "No Account")
    formatted_account.short_description = 'Tài khoản'

    def formatted_order_id(self, obj):
        return obj.order_id
    formatted_order_id.short_description = 'ID'

    def formatted_delivery_time(self, obj):
        return obj.delivery_time
    formatted_delivery_time.short_description = 'Ngày vận chuyển'

    def formatted_order_time(self, obj):
        return obj.order_time
    formatted_order_time.short_description = 'Ngày đặt hàng'

    def formatted_price(self, obj):
        formatted = f"{obj.price * 1000:,.0f}₫"
        return formatted
    formatted_price.short_description = 'Giá'

    # def status_with_warning(self, obj):
    #     if obj.status_order == 'Chờ xác nhận':
    #         return format_html(
    #             '<span style="color: red; font-weight: bold;">{}</span>',
    #             obj.status_order
    #         )
    #     return obj.status_order
    # status_with_warning.short_description = 'Trạng thái'
    def status_with_warning(self, obj):
        if obj.status_order == 'Chờ xác nhận':
            return format_html(
            '<span style="color: orange; font-weight: bold;">{}</span>',
            obj.status_order
        )
        elif obj.status_order == 'Chờ lấy hàng':
            return format_html(
                '<span style="color: blue; font-weight: bold;">{}</span>',
                obj.status_order
            )
        elif obj.status_order == 'Đang vận chuyển':
            return format_html(
                '<span style="color: purple; font-weight: bold;">{}</span>',
                obj.status_order
            )
        elif obj.status_order == 'Đã giao':
            return format_html(
                '<span style="color: green; font-weight: bold;">{}</span>',
                obj.status_order
            )
        elif obj.status_order == 'Đã hủy':
            return format_html(
                '<span style="color: red; font-weight: bold;">{}</span>',
                obj.status_order
            )
        else:
            return obj.status_order
    status_with_warning.short_description = 'Trạng thái'
    def formatted_payment_method(self, obj):
        return obj.payment_method
    formatted_payment_method.short_description = 'Thanh Toán'
    def row_actions(self, obj):
        edit_url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name), args=[obj.pk])
        delete_url = reverse('admin:%s_%s_delete' % (obj._meta.app_label, obj._meta.model_name), args=[obj.pk])

        return format_html(
            '<div style="display: flex; align-items: center; justify-content: center; height: 70px;">'
            '<a class="button" href="{}" style="color: blue; margin-right: 10px;">Sửa</a>'
            '<a class="button" href="{}" style="color: red;">Xóa</a>'
            '</div>',
            edit_url, delete_url
        )
    row_actions.short_description = ' '

class CouponAdmin(BaseAdmin):
    def has_module_permission(self, request):
        """Ẩn model khỏi trang admin chính"""
        return False
    
    list_display = ('formatted_coupon_id', 'formatted_name', 'formatted_discount', 'formatted_posting_date', 'formatted_expiry_date', 'row_actions')
    search_fields = ('name',)
    ordering = ('coupon_id',)

    def formatted_coupon_id(self, obj):
        return obj.coupon_id
    formatted_coupon_id.short_description = 'ID'

    def formatted_name(self, obj):
        return obj.name 
    formatted_name.short_description = 'Mã'

    def formatted_discount(self, obj):
        return obj.discount
    formatted_discount.short_description = 'Khuyến mãi'

    def formatted_posting_date(self, obj):
        return obj.posting_date
    formatted_posting_date.short_description = 'Ngày bắt đầu'

    def formatted_expiry_date(self, obj):
        return obj.expiry_date
    formatted_expiry_date.short_description = 'Ngày kết thúc'

class OrderDetailAdmin(BaseAdmin):
    def has_module_permission(self, request):
        """Ẩn model khỏi trang admin chính"""
        return False
    list_display = ('formatted_order', 'thumbnail', 'formatted_product', 'formatted_quantity', 'formatted_coupon', 'row_actions')
    search_fields = ('order__order_id', 'product__name')
    ordering = ('order',)
    list_filter = ('order',)  # Thêm bộ lọc theo đơn hàng
    def thumbnail(self, obj):
        if obj.product.image:
            return format_html('<img src="{}" width="70" height="70" />', obj.product.image.url)
        return "No Image"
    thumbnail.short_description = 'Ảnh'
    
    def formatted_order(self, obj):
        return obj.order
    formatted_order.short_description = 'Đơn hàng'

    def formatted_product(self, obj):
        return obj.product
    formatted_product.short_description = 'Sản phẩm'

    def formatted_quantity(self, obj):
        return obj.quantity
    formatted_quantity.short_description = 'Số lượng'

    def formatted_coupon(self, obj):
        return (obj.coupon.name if obj.coupon else "No Coupon")
    formatted_coupon.short_description = 'Khuyến mãi'

class WishlistAdmin(BaseAdmin):
    def has_module_permission(self, request):
        """Ẩn model khỏi trang admin chính"""
        return False
    
    list_display = ('formatted_wishlist_id', 'formatted_account', 'formatted_img' ,'formatted_product', 'row_actions')
    search_fields = ('account__username', 'product__name')
    ordering = ('wishlist_id',)

    def formatted_img(self, obj):
        if obj.product.image:
            return format_html('<img src="{}" width="70" height="70" />', obj.product.image.url)
        return "No Image"
    formatted_img.short_description = 'Ảnh'
    def formatted_account(self, obj):
        return (obj.account.username if obj.account else "No Account")
    formatted_account.short_description = 'Tài khoản'

    def formatted_wishlist_id(self, obj):
        return obj.wishlist_id
    formatted_wishlist_id.short_description = 'ID'

    def formatted_product(self, obj):
        return obj.product.name
    formatted_product.short_description = 'Sản phẩm'

    def formatted_wishlist_id(self, obj):
        return obj.wishlist_id
    formatted_wishlist_id.short_description = 'ID'

    def formatted_wishlist_id(self, obj):
        return obj.wishlist_id
    formatted_wishlist_id.short_description = 'ID'

class CartAdmin(BaseAdmin):
    def has_module_permission(self, request):
        """Ẩn model khỏi trang admin chính"""
        return False
    
    list_display = ('formatted_account', 'thumbnail', 'formatted_product', 'formatted_quantity', 'row_actions')
    search_fields = ('account__username', 'product__name')
    ordering = ('account',)

    def formatted_account(self, obj):
        return (obj.account.username if obj.account else "No Account")
    formatted_account.short_description = 'Tài khoản'

    def formatted_product(self, obj):
        return obj.product.name 
    formatted_product.short_description = 'Sản phẩm'

    def thumbnail(self, obj):
        if obj.product.image:
            return format_html('<img src="{}" width="70" height="70" />', obj.product.image.url)
        return "No Image"
    thumbnail.short_description = 'Ảnh'
    def formatted_quantity(self, obj):
        return obj.quantity
    formatted_quantity.short_description = 'Số lượng'
class SupplierAdmin(BaseAdmin):
    def has_module_permission(self, request):
        """Ẩn model khỏi trang admin chính"""
        return False
    
    list_display = ('formatted_supp_id', 'formatted_address', 'formatted_phone', 'row_actions')
    search_fields = ('address', 'supplier_id')
    ordering = ('supplier_id',)

    def formatted_supp_id(self, obj):
        return (obj.supplier_id if obj.supplier_id else "None")
    formatted_supp_id.short_description = 'ID'
    def formatted_address(self, obj):
        return (obj.address if obj.address else "None")
    formatted_address.short_description = 'Địa chỉ'
    def formatted_phone(self, obj):
        return (obj.phone_number if obj.phone_number else "None")
    formatted_phone.short_description = 'SDT'

    
class FeedbackAdmin(BaseAdmin):
    def has_module_permission(self, request):
        """Ẩn model khỏi trang admin chính"""
        return False
    list_display = ('formatted_feedback_id', 'thumbnail', 'formatted_rating_star', 'formatted_status', 'formatted_feedback_content', 'formatted_account', 'formatted_product', 'row_actions')
    search_fields = ('status', 'feedback_content')
    ordering = ('feedback_id',)

    def thumbnail(self, obj):
        if obj.img_feedback:
            return format_html('<img src="{}" width="70" height="70" />', obj.img_feedback.url)
        return "No Image"
    thumbnail.short_description = 'Ảnh'

    def thumbnail_pro(self, obj):
        if obj.product.image:
            return format_html('<img src="{}" width="70" height="70" />', obj.product.image.url)
        return "No Image"
    thumbnail_pro.short_description = ' '

    def formatted_account(self, obj):
        return (obj.account.username if obj.account else "No Account")
    formatted_account.short_description = 'Tài khoản'

    def formatted_feedback_id(self, obj):
        return (obj.feedback_id if obj.feedback_id else "None")
    formatted_feedback_id.short_description = 'ID'

    def formatted_rating_star(self, obj):
        return (obj.rating_star if obj.rating_star else "0")
    formatted_rating_star.short_description = 'Số sao'

    def formatted_status(self, obj):
        return (obj.status if obj.status else "None")
    formatted_status.short_description = 'Trạng thái'

    def formatted_feedback_content(self, obj):
        return (obj.feedback_content if obj.feedback_content else "None")
    formatted_feedback_content.short_description = 'Nội dung'

    def formatted_product(self, obj):
        return (obj.product.name if obj.product else "No Product")
    formatted_product.short_description = 'Sản phẩm'

class BlogDetailResource(resources.ModelResource):
    class Meta:
        model = Blog
        fields = ('id','title_blog', 'account', 'title', 'create_date', 'image_1', 'short_descrip', 'detail', 'link')  # You can add more fields as needed
        import_id_fields = ('title_blog',)

class TitleBlogResource(resources.ModelResource):
    class Meta:
        model = Blog
        fields = ('id','name', 'account', 'created_at', 'description')  # You can add more fields as needed
        import_id_fields = ('name',)
               
class ProvinceResource(resources.ModelResource):
    class Meta:
        model = Province
        fields = ('province_id','name')  # You can add more fields as needed
        import_id_fields = ('name',)

class DistrictResource(resources.ModelResource):
    class Meta:
        model = District
        fields = ('name', 'province')  # You can add more fields as needed
        import_id_fields = ('name',)

class WardResource(resources.ModelResource):
    class Meta:
        model = Ward
        fields = ('name', 'district')  # You can add more fields as needed
        import_id_fields = ()

class ProvinceAdmin(ImportExportModelAdmin, BaseAdmin):

    resource_class = ProvinceResource
    list_display = ('province_id','name','row_actions')
    search_fields = ('name',)

class DistrictAdmin(ImportExportModelAdmin, BaseAdmin):
    
    resource_class = DistrictResource
    list_display = ('district_id','name','row_actions')
    search_fields = ('name',)

class WardAdmin(ImportExportModelAdmin, BaseAdmin):
    resource_class = WardResource
    list_display = ('ward_id','name','row_actions')
    search_fields = ('name',)

class TitleBlogAdmin(ImportExportModelAdmin, BaseAdmin):
    def has_module_permission(self, request):
        """Ẩn model khỏi trang admin chính"""
        return False
    resource_class = TitleBlogResource
    list_display = ('id','formatted_name', 'formatted_created_at', 'row_actions')
    search_fields = ('name',)
    ordering = ('name','created_at',)

    def formatted_name(self, obj):
        return obj.name 
    formatted_name.short_description = 'Title'

    def formatted_created_at(self, obj):
        return obj.created_at
    formatted_created_at.short_description = 'Ngày tạo'


class BlogAdmin(ImportExportModelAdmin, BaseAdmin):
    def has_module_permission(self, request):
        """Ẩn model khỏi trang admin chính"""
        return False
    resource_class = BlogDetailResource
    list_display = ('formatted_title', 'formatted_create_date', 'row_actions')
    search_fields = ('title',)
    ordering = ('create_date',)
    list_filter=('title_blog',)
    def formatted_title(self, obj):
        return obj.title
    formatted_title.short_description = 'Title'

    def formatted_create_date(self, obj):
        return obj.create_date
    formatted_create_date.short_description = 'Ngày tạo'

# CustomAdminSite
class CustomAdminSite(admin.AdminSite):
    site_header = "Quản trị Nông Sản Sạch"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.dashboard_view, name='admin_dashboard'),
            path('add-receipt/', self.add_receipt_view, name='add_receipt'),
            path('receipt-list/', self.receipt_list_view, name='receipt_list'),
            path('product/', self.product_view, name='product'),
            path('category/', self.category_view, name='category'),
            path('cart/', self.cart_view, name='cart'),
            path('coupon/', self.coupon_view, name='coupon'),
            path('defective_product/', self.defective_product_view, name='defective_product'),
            path('feedback/', self.feedback_view, name='feedback'),
            path('order/', self.order_view, name='order'),
            path('order_detail/', self.order_detail_view, name='order_detail'),
            path('supplier/', self.supplier_view, name='supplier'),
            path('user/', self.user_view, name='user'),
            path('blog/', self.blog_view, name='blog'),
            path('title/', self.title_blog_view, name='title_blog'),

        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        context = {
            'title': 'Dashboard',
        }
        return render(request, 'admin/dashboard.html', context)

    def add_receipt_view(self, request):
        # Logic for adding a receipt (tùy chỉnh theo yêu cầu)
        context = {
            'title': 'Thêm Phiếu Nhập',
        }
        return render(request, 'admin/add_receipt.html', context)

    def receipt_list_view(self, request):
        # Logic for listing receipts (tùy chỉnh theo yêu cầu)
        context = {
            'title': 'Danh Sách Phiếu Nhập',
        }
        return render(request, 'admin/receipt_list.html', context)
    
    def product_view(self, request):
        context = {
            'title': 'Product',
        }
        return render(request, 'NongSan/product', context)
    
    def category_view(self, request):
        context = {
            'title': 'category',
        }
        return render(request, 'NongSan/category', context)
    
    def cart_view(self, request):
        context = {
            'title': 'Product',
        }
        return render(request, 'NongSan/cart', context)
    
    def coupon_view(self, request):
        context = {
            'title': 'coupon',
        }
        return render(request, 'NongSan/coupon', context)
    
    def wishlist_view(self, request):
        context = {
            'title': 'coupon',
        }
        return render(request, 'NongSan/wishlist', context)
    
    def defective_product_view(self, request):
        context = {
            'title': 'defective_product',
        }
        return render(request, 'NongSan/defectiveproduct', context)
    
    def feedback_view(self, request):
        context = {
            'title': 'feedback',
        }
        return render(request, 'NongSan/feedback', context)
    
    def order_view(self, request):
        context = {
            'title': 'order',
        }
        return render(request, 'NongSan/order', context)
    
    def order_detail_view(self, request):
        context = {
            'title': 'order_detail',
        }
        return render(request, 'NongSan/orderdetail', context)
    
    
    def supplier_view(self, request):
        context = {
            'title': 'supplier',
        }
        return render(request, 'NongSan/supplier', context)
    
    def user_view(self, request):
        context = {
            'title': 'user',
        }
        return render(request, 'NongSan/account', context)
    
    def title_blog_view(self, request):
        context = {
            'title': 'title_blog',
        }
        return render(request, 'NongSan/titleblog', context)
    
    def blog_view(self, request):
        context = {
            'title': 'blog',
        }
        return render(request, 'NongSan/blog', context)
    

    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        # Chỉnh sửa menu admin
        app_list.insert(0, {
            'name': 'Quản Trị', 
            'app_label': 'dashboard', 
            'models': [
                {'name': 'Báo Cáo', 'admin_url': '/admin/dashboard/'},
                {'name': 'Nhập Hàng', 'admin_url': '/admin/add_receipt/'},
                {'name': 'Danh Sách Phiếu Nhập', 'admin_url': '/admin/receipts/'},
                {'name': 'Sản Phẩm', 'admin_url': 'NongSan/product/'},
                {'name': 'Danh Mục Sảm Phẩm', 'admin_url': 'NongSan/category/'},
                {'name': 'Sản Phẩm Hư Hỏng', 'admin_url': 'NongSan/defective_product/'},
                {'name': 'Khuyến Mãi', 'admin_url': 'NongSan/coupon/'},
                {'name': 'Giỏ Hàng', 'admin_url': 'NongSan/cart/'},
                {'name': 'Sản Phẩm Yêu Thích', 'admin_url': 'NongSan/wishlist/'},
                {'name': 'Đơn Hàng', 'admin_url': 'NongSan/orders/'},
                {'name': 'Chi Tiết Đơn Hàng', 'admin_url': 'NongSan/orderdetail/'},
                {'name': 'Nhà Cung Cấp', 'admin_url': 'NongSan/supplier/'},
                {'name': 'Đánh Giá', 'admin_url': 'NongSan/feedback/'},
                {'name': 'Danh Mục Blog', 'admin_url': 'NongSan/titleblog/'},
                {'name': 'Quản Lý Blog', 'admin_url': 'NongSan/blog/'},
                {'name': 'Tài Khoản', 'admin_url': 'NongSan/account/'}
            ]
        })
        return app_list




# Registering models with the Custom Admin Site
custom_admin_site = CustomAdminSite(name="custom_admin")
custom_admin_site.register(Account, AccountAdmin)
custom_admin_site.register(Category, CategoryAdmin)
# custom_admin_site.register(Province, ProvinceAdmin)
# custom_admin_site.register(District, DistrictAdmin)
# custom_admin_site.register(Ward, WardAdmin)
custom_admin_site.register(Address, AddressAdmin)
custom_admin_site.register(Orders, OrdersAdmin)
custom_admin_site.register(Coupon, CouponAdmin)
custom_admin_site.register(OrderDetail, OrderDetailAdmin)
custom_admin_site.register(Wishlist, WishlistAdmin)
custom_admin_site.register(Cart, CartAdmin)
custom_admin_site.register(Feedback, FeedbackAdmin)
custom_admin_site.register(Product, ProductAdmin)
custom_admin_site.register(Defective_Product, DefectiveProductAdmin)
custom_admin_site.register(Supplier, SupplierAdmin)
custom_admin_site.register(Blog, BlogAdmin)
custom_admin_site.register(TitleBlog, TitleBlogAdmin)
# custom_admin_site.register(Province, ProvinceAdmin)
# custom_admin_site.register(District, DistrictAdmin)
# custom_admin_site.register(Ward, WardAdmin)
# Use custom_admin_site for your site

admin.site = custom_admin_site