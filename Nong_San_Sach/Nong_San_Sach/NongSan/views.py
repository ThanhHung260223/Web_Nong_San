from collections import defaultdict
from django.forms import modelformset_factory
from django.shortcuts import render,get_object_or_404, redirect
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Cart, Category, Wishlist, Province, District, Ward, Orders, OrderDetail, Coupon, Feedback, Account, Receipt, Supplier, Receipt_Detail, Defective_Product, Blog, TitleBlog
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from decimal import Decimal
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views import View
from .forms import UpdateUserForm, RegisterForm, LoginForm, UpdateProfileForm, ReceiptForm, ProductForm, SupplierForm, ReceiptDetailForm, CateForm, ProductForm1
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from datetime import datetime
from django.utils.timezone import now
from django.db.models import Avg
from django.utils.text import slugify
@never_cache
def index(request):
    products = Product.objects.filter(display_product=True)
    total_quantity = 0
    total_wishlist = 0
    categories = Category.objects.all()
    

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(account=request.user)
        total_quantity = sum(item.quantity for item in cart_items)
        
        wishlist_items = Wishlist.objects.filter(account=request.user)
        total_wishlist = wishlist_items.count()

    products_with_discounts = []
    for product in products:
        if product.coupon and product.coupon.expiry_date >= now():
            discounted_price = product.price * (1 - float(product.coupon.discount) / 100)
        else:
            discounted_price = product.price
        products_with_discounts.append({
            'product': product,
            'discounted_price': discounted_price,
        })

     # Sắp xếp sản phẩm theo danh mục và giới hạn mỗi danh mục 12 sản phẩm
    categorized_products = defaultdict(list)
    for item in products_with_discounts:
        categorized_products[item['product'].category].append(item)

    # Cắt danh sách mỗi danh mục chỉ lấy tối đa 12 sản phẩm
    limited_categorized_products = {
        category: products[:8] for category, products in categorized_products.items()
    }
    # Sản phẩm bán chạy
    top_products = (
        Product.objects.annotate(total_sold=Sum('orderdetail__quantity'))
        .filter(total_sold__isnull=False, display_product=True)  # Chỉ lấy các sản phẩm có lượt mua
        .order_by('-total_sold')[:10]  # Lấy top 10 sản phẩm
    )


    context = {
        'limited_categorized_products': limited_categorized_products,  # Sản phẩm theo danh mục đã giới hạn
        'categories': categories,
        'products_with_discounts': products_with_discounts,  # Sản phẩm kèm giá giảm
        
        'total_quantity': total_quantity,
        'total_wishlist': total_wishlist,
        'categories': categories,
        'top_products': top_products,
        'now': now()
    }
    
    return render(request, 'pages/home.html', context)


def top_selling_products(request):
    # Truy vấn lấy sản phẩm và tổng số lượng bán
    top_products = (
        OrderDetail.objects.values('product')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:5]
    )
    return render(request, 'pages/home.html', {'top_products': top_products})
def blog(request):
    total_quantity = 0
    total_wishlist = 0
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(account=request.user)
        total_quantity = sum(item.quantity for item in cart_items)
        
        wishlist_items = Wishlist.objects.filter(account=request.user)
        total_wishlist = wishlist_items.count()
    context = {
        'total_quantity': total_quantity,
        'total_wishlist': total_wishlist
    }
    return render(request, 'pages/blog.html', context)

from .models import Product

def product_list(request):
    products = Product.objects.all()  # Lấy tất cả sản phẩm
    return render(request, 'pages/home.html', {'products': products})

def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')
    # Lấy sản phẩm theo ID
    product = get_object_or_404(Product, pk=product_id)
    
    # Kiểm tra xem sản phẩm có tồn tại trong giỏ hàng của user không
    cart_item, created = Cart.objects.get_or_create(product=product, account=request.user)
    
    # Nếu sản phẩm đã có trong giỏ, tăng số lượng
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f'Sản phẩm {product.name} đã được thêm vào giỏ hàng (tăng số lượng).')
    else:
        # Gán giá trị mặc định cho số lượng là 1 khi sản phẩm được thêm lần đầu
        cart_item.quantity = 1
        cart_item.save()
        messages.success(request, f'Sản phẩm {product.name} đã được thêm vào giỏ hàng.')

    # Chuyển hướng về trang giỏ hàng
    return redirect('cart')  # Điều chỉnh URL name của trang giỏ hàng

def cart_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    cart_items = Cart.objects.filter(account=request.user)
    total_price = 0
    for item in cart_items:
        # Kiểm tra xem sản phẩm có mã giảm giá không
        if item.product.coupon:
            discount = item.product.coupon.discount  # Phần trăm giảm giá
            discounted_price = item.product.price * (1 - float(discount) / 100)  # Tính giá sau giảm
            item.discounted_price = discounted_price  # Gán giá giảm vào item
        else:
            item.discounted_price = item.product.price  # Không có khuyến mãi, giữ nguyên giá gốc
        
        # Cộng dồn giá giảm vào tổng giá
        total_price += item.discounted_price * item.quantity

    # Tính tổng số lượng sản phẩm
    total_quantity = sum(item.quantity for item in cart_items)

    wishlist_items = Wishlist.objects.filter(account=request.user)
    total_wishlist = wishlist_items.count()

    context = {
        'cart_items': cart_items,   
        'total_price': total_price,
        'total_quantity': total_quantity,
        'total_wishlist': total_wishlist,
        'now': now()
    }
    return render(request, 'pages/cart.html', context)
#@login_required
def checkout(request):
    # Logic xử lý thanh toán sẽ đặt ở đây
    return render(request, 'pages/checkout.html')


def update_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        cart_item, created = Cart.objects.get_or_create(account=request.user, product_id=product_id)
        product = Product.objects.get(product_id=product_id)

        if action == 'add':
            print(f"Số lượng hiện tại trong giỏ hàng: {cart_item.quantity}, Số lượng trong kho: {product.quantity}")
            if cart_item.quantity < product.quantity:
                cart_item.quantity += 1
            else:
                return render(request, 'pages/cart.html', {
                    'message': f"Không đủ số lượng sản phẩm {product.name} trong kho. Sản phẩm hiện có {product.quantity} trong kho.",
                    'cart_items': Cart.objects.filter(account=request.user)
                })
        elif action == 'remove':
            cart_item.quantity -= 1
            if cart_item.quantity <= 0:
                cart_item.delete()
                return redirect('cart')

        cart_item.save()
        return redirect('cart')

def remove_from_cart(request, product_id):
    if request.user.is_authenticated:
        cart_item = get_object_or_404(Cart, account=request.user, product__product_id=product_id)
        cart_item.delete()
        return redirect('cart')
    return redirect('login')

def add_to_wishlist(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')
    # Lấy sản phẩm theo ID
    product = get_object_or_404(Product, pk=product_id)
    
    # Kiểm tra xem sản phẩm có tồn tại trong giỏ hàng của user không
    wish_lists, created = Wishlist.objects.get_or_create(product=product, account=request.user)
    
    # Nếu sản phẩm đã có trong giỏ, tăng số lượng
    if not created:
        wish_lists.quantity = 1
        wish_lists.save()
        messages.success(request, f'Sản phẩm {product.name} đã được thêm vào giỏ hàng (tăng số lượng).')
    else:
        # Gán giá trị mặc định cho số lượng là 1 khi sản phẩm được thêm lần đầu
        wish_lists.quantity = 1
        wish_lists.save()
        messages.success(request, f'Sản phẩm {product.name} đã được thêm vào giỏ hàng.')

    # Chuyển hướng về trang giỏ hàng
    return redirect('wishlist')  # Điều chỉnh URL name của trang giỏ hàng

         
def wishlist_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    wish_lists = Wishlist.objects.filter(account=request.user)
    cart_items = Cart.objects.filter(account=request.user)
    total_quantity = sum(item.quantity for item in cart_items)
    total_wishlist = wish_lists.count()
    # Đảm bảo lấy thời gian hiện tại
    for item in wish_lists:
        # Kiểm tra xem sản phẩm có mã giảm giá không
        if item.product.coupon:
            discount = item.product.coupon.discount  # Phần trăm giảm giá
            discounted_price = item.product.price * (1 - float(discount) / 100)  # Tính giá sau giảm
            item.discounted_price = discounted_price  # Gán giá giảm vào item
            
        else:
            item.discounted_price = item.product.price  # Không có khuyến mãi, giữ nguyên giá gốc
    context = {
        'cart_items': cart_items, 
        'wishlist_items': wish_lists,
        'total_wishlist': total_wishlist,
        'total_quantity': total_quantity,
        'now': now()
    }
    return render(request, 'pages/wishlist.html', context)

def remove_from_wishlist(request, product_id):
    if request.user.is_authenticated:
        wishlist_items = get_object_or_404(Wishlist, account=request.user, product__product_id=product_id)
        wishlist_items.delete()
        return redirect('wishlist')
    return redirect('login')


def checkout(request):

    total_wishlist = 0
    total_quantity = 0

    # Lấy dữ liệu giỏ hàng và danh sách yêu thích nếu người dùng đăng nhập
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(account=request.user)
        total_quantity = sum(item.quantity for item in cart_items)
            
        wishlist_items = Wishlist.objects.filter(account=request.user)
        total_wishlist = wishlist_items.count()

    provinces = Province.objects.all()
    
    # Giả sử bạn đã có mô hình Cart hoặc Order liên kết với người dùng
    cart_items = Cart.objects.filter(account=request.user)    
    items_with_totals = []
    total_price = 0

    total_price = Decimal('0.0')  # Tổng tiền sử dụng Decimal

    # Tính tổng tiền đơn hàng sau giảm giá
    removed_products = []
    # Tính tổng tiền đơn hàng sau giảm giá
    for item in cart_items:
        if item.product.quantity < item.quantity:
            # Thêm sản phẩm vào danh sách tạm
            removed_products.append(item.product.name)
            # Xóa sản phẩm khỏi giỏ hàng
            item.delete()
            continue  # Bỏ qua xử lý cho sản phẩm này
        original_price = item.product.price  # Giá gốc (Decimal)
        coupon = item.product.coupon
        discount = float('0.0')  # Mặc định giảm giá là 0
        
        # Kiểm tra xem sản phẩm có coupon và coupon còn hiệu lực không
        if coupon and coupon.expiry_date >= now():
            discount = float(coupon.discount)  # Lấy giá trị giảm giá nếu hợp lệ
        
        # Tính giá sau giảm
        discounted_price = original_price * (float('1.0') - discount / float('100.0'))
        discounted_price = Decimal(discounted_price)
        # Tổng tiền cho từng sản phẩm trong giỏ hàng
        item_total = discounted_price * item.quantity
        total_price += item_total

        # Thêm thông tin vào danh sách
        items_with_totals.append({
            'product': item.product,
            'quantity': item.quantity,
            'original_price': original_price,
            'discount': discount,
            'discounted_price': discounted_price,
            'item_total': item_total,
            
        })
    
    context = {
        'items_with_totals': items_with_totals,
        'total_price': total_price,
        'provinces': provinces,
        'total_wishlist':total_wishlist,
        'total_quantity':total_quantity,
        'removed_products': removed_products,
        'now': now()
    }
    
    return render(request, 'pages/checkout.html', context)

def get_districts(request):
    province_id = request.GET.get('province_id')
    districts = District.objects.filter(province_id=province_id).values('district_id', 'name')
    
    district_list = list(districts)
    
    if not district_list:
        return JsonResponse({'error': 'No districts found'}, status=404)
    
    return JsonResponse(district_list, safe=False)

def get_wards(request):
    district_id = request.GET.get('district_id')
    if not district_id:
        return JsonResponse({'error': 'District ID is required'}, status=400)

    wards = Ward.objects.filter(district_id=district_id).values('ward_id', 'name')
    ward_list = list(wards)
    
    if not ward_list:
        return JsonResponse({'error': 'No wards found'}, status=404)
    
    return JsonResponse(ward_list, safe=False)

@csrf_exempt
def confirm_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        # Lấy thông tin từ dữ liệu
        payment_method = data.get('payment_method')
        account = request.user  # ID của tài khoản người dùng
        address_detail = data.get('address_detail')  # Địa chỉ chi tiết
        total_price_str = data.get('total_prices')  # Tổng giá trị đơn hàng
        order_items = data.get('order_items')  # Danh sách sản phẩm trong đơn hàng
        order_items = [
            {
                'product_id': item.product.product_id,
                'quantity': item.quantity,  # Lấy số lượng từ giỏ hàng
            }
            for item in Cart.objects.filter(account=request.user)
        ]
        total_price_str = total_price_str.replace('₫', '').replace('Tổng Tiền: ', '').replace(' đ', '').replace(',', '').strip()
        total_price = float(total_price_str) / 1000.0
        # In ra các giá trị để kiểm tra
        print(f"Account ID: {account}")  # In ra ID tài khoản
        print(f"Address Detail: {address_detail}")  # In ra địa chỉ
        print(f"Total Price: {total_price}")  # In ra tổng giá trị
        print(f"Order Items: {order_items}")  # In ra danh sách sản phẩm
        print('phuong thuc thanh toán', payment_method)
        # Kiểm tra xem các trường cần thiết có hợp lệ không
        if not account:
            return JsonResponse({'status': 'fail', 'message': 'Thiếu ID tài khoản.'}, status=400)
        if not address_detail:
            return JsonResponse({'status': 'fail', 'message': 'Thiếu địa chỉ.'}, status=400)
        if not total_price:
            return JsonResponse({'status': 'fail', 'message': 'Thiếu tổng giá trị.'}, status=400)
        if not order_items:
            return JsonResponse({'status': 'fail', 'message': 'Thiếu sản phẩm trong đơn hàng.'}, status=400)
        
        # Tạo đơn hàng mới
        order = Orders.objects.create(
            account_id=account.id,
            address_detail=address_detail,
            price=total_price,
            status_order='Chờ xác nhận',
            payment_method=payment_method
        )

        # Lưu từng sản phẩm vào OrderDetail
        for item in order_items:
            product_id = item.get('product_id')
            quantity = item.get('quantity')
            coupon_id = item.get('coupon_id')

            # Kiểm tra xem sản phẩm có tồn tại và có đủ số lượng không
            product = Product.objects.filter(product_id=product_id).first()
            if product and product.quantity >= quantity:
                OrderDetail.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    coupon_id=coupon_id
                )
                # Cập nhật số lượng sản phẩm trong kho
                product.quantity -= quantity
                product.save()
            else:
                return JsonResponse({'status': 'fail', 'message': f'Sản phẩm {product_id} không đủ số lượng.'}, status=400)
        # Áp dụng mã giảm giá cho toàn bộ đơn hàng nếu có
        # discount_amount = Decimal(0)
        # if coupon_id:
        #     coupon = Coupon.objects.filter(name=coupon).first()
        #     if coupon and coupon.expiry_date >= timezone.now():
        #         discount_amount = (total_price * coupon.discount) / Decimal(100)
        #         total_price -= discount_amount  # Tổng giá trị sau khi giảm giá

        # Cập nhật tổng giá trị đơn hàng sau khi áp dụng giảm giá
        order.price = total_price
        order.save()

        Cart.objects.filter(account=request.user).delete()
        return JsonResponse({'status': 'success', 'order_id': order.order_id})
    redirect('track_orders')

    return JsonResponse({'status': 'fail'}, status=400)





class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'pages/register.html'

    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return redirect(to='/')

        # else process dispatch as it otherwise normally would
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')

            return redirect(to='login')

        return render(request, self.template_name, {'form': form})
    

class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'pages/login.html'

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # Set session to expire when the browser closes
            self.request.session.set_expiry(0)
            self.request.session.modified = True

        return super().form_valid(form)

    def get_success_url(self):
        # Redirect staff users to admin site, others to the homepage
        if self.request.user.is_staff:
            return reverse_lazy('admin:index')
        else:
            return reverse_lazy('index')
        
        
class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'pages/password_reset.html'
    email_template_name = 'pages/password_reset_email.html'
    subject_template_name = 'pages/password_reset_subject'
    success_message = "Chúng tôi đã gửi cho bạn hướng dẫn đặt mật khẩu qua email, " \
                      "nếu có tài khoản tồn tại với email bạn đã nhập. Bạn sẽ nhận được chúng trong thời gian ngắn." \
                      " Nếu bạn không nhận được email, " \
                      "vui lòng đảm bảo rằng bạn đã nhập địa chỉ bạn đã đăng ký và kiểm tra thư mục thư rác."
    success_url = reverse_lazy('index')

class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'pages/change_password.html'
    success_message = "Đã đổi mật khẩu thành công"
    success_url = reverse_lazy('index')

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user, current_user=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Thông tin của bạn đã được cập nhật thành công')
            return redirect('profile')
    else:
        user_form = UpdateUserForm(instance=request.user, current_user=request.user)
        profile_form = UpdateProfileForm(instance=request.user)

    return render(request, 'pages/profile.html', {'user_form': user_form, 'profile_form': profile_form})
#admin

from django.db.models import Sum, Count
from django.utils import timezone
import datetime
from django.db.models.functions import ExtractMonth, ExtractDay
import pandas as pd
import matplotlib.pyplot as plt
import os
from django.conf import settings  
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.timezone import now, timedelta
from django.db.models.functions import TruncMonth, TruncDay, TruncYear


####
from django.db.models import Sum, Count
from django.utils.timezone import now
from django.db.models.functions import TruncMonth
from datetime import datetime

def dashboard(request):
    # Lấy tham số từ query string
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    month_filter = request.GET.get('month')
    year_filter = request.GET.get('year')

    # Chuyển đổi start_date và end_date thành kiểu datetime nếu có
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Tổng doanh thu
    if start_date and end_date:
        total_revenue = Orders.objects.filter(order_time__range=(start_date, end_date)).aggregate(total=Sum('price'))['total'] or 0
    elif month_filter and year_filter:
        total_revenue = Orders.objects.filter(order_time__month=month_filter, order_time__year=year_filter).aggregate(total=Sum('price'))['total'] or 0
    elif year_filter:
        total_revenue = Orders.objects.filter(order_time__year=year_filter).aggregate(total=Sum('price'))['total'] or 0
    else:
        total_revenue = Orders.objects.aggregate(total=Sum('price'))['total'] or 0

    # Số khách hàng mới trong khoảng thời gian
    if start_date and end_date:
        new_customers = Account.objects.filter(date_joined__range=(start_date, end_date)).count()
    elif month_filter and year_filter:
        new_customers = Account.objects.filter(date_joined__month=month_filter, date_joined__year=year_filter).count()
    elif year_filter:
        new_customers = Account.objects.filter(date_joined__year=year_filter).count()
    else:
        new_customers = Account.objects.count()

    # Số lượng đơn hàng
    if start_date and end_date:
        total_orders = Orders.objects.filter(order_time__range=(start_date, end_date)).count()
    elif month_filter and year_filter:
        total_orders = Orders.objects.filter(order_time__month=month_filter, order_time__year=year_filter).count()
    elif year_filter:
        total_orders = Orders.objects.filter(order_time__year=year_filter).count()
    else:
        total_orders = Orders.objects.count()

    # Tổng sản phẩm đã bán
    if start_date and end_date:
        total_products_sold = OrderDetail.objects.filter(order__order_time__range=(start_date, end_date)).aggregate(total=Sum('quantity'))['total'] or 0
    elif month_filter and year_filter:
        total_products_sold = OrderDetail.objects.filter(order__order_time__month=month_filter, order__order_time__year=year_filter).aggregate(total=Sum('quantity'))['total'] or 0
    elif year_filter:
        total_products_sold = OrderDetail.objects.filter(order__order_time__year=year_filter).aggregate(total=Sum('quantity'))['total'] or 0
    else:
        total_products_sold = OrderDetail.objects.aggregate(total=Sum('quantity'))['total'] or 0

    # Top 5 sản phẩm bán chạy nhất
    if start_date and end_date:
        top_products = (
            OrderDetail.objects.filter(order__order_time__range=(start_date, end_date))
            .values('product__name')
            .annotate(total_sold=Sum('quantity'))
            .order_by('-total_sold')[:5]
        )
    elif month_filter and year_filter:
        top_products = (
            OrderDetail.objects.filter(order__order_time__month=month_filter, order__order_time__year=year_filter)
            .values('product__name')
            .annotate(total_sold=Sum('quantity'))
            .order_by('-total_sold')[:5]
        )
    elif year_filter:
        top_products = (
            OrderDetail.objects.filter(order__order_time__year=year_filter)
            .values('product__name')
            .annotate(total_sold=Sum('quantity'))
            .order_by('-total_sold')[:5]
        )
    else:
        top_products = (
            OrderDetail.objects.values('product__name')
            .annotate(total_sold=Sum('quantity'))
            .order_by('-total_sold')[:5]
        )

    # Tồn kho
    stock_quantity = Product.objects.values('name', 'quantity')

    # Doanh thu theo tháng
    monthly_revenue = Orders.objects.annotate(month=TruncMonth('order_time')).values('month').annotate(total=Sum('price')* 1000).order_by('month')

    # Đơn hàng theo tháng
    monthly_orders = Orders.objects.annotate(month=TruncMonth('order_time')).values('month').annotate(total=Count('order_id')).order_by('month')
    
    try:
        if not start_date or not end_date:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)
        else:
            if isinstance(start_date, str) and isinstance(end_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        # Trường hợp lỗi định dạng ngày
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)


    monthly_revenue = (
        Orders.objects.filter(order_time__range=(start_date, end_date))
        .annotate(month=TruncMonth('order_time'))
        .values('month')
        .annotate(total=Sum('price')* 1000)
        .order_by('month')
    )

    monthly_orders = (
        Orders.objects.filter(order_time__range=(start_date, end_date))
        .annotate(month=TruncMonth('order_time'))
        .values('month')
        .annotate(total=Count('order_id'))  # Đếm số lượng đơn hàng
        .order_by('month')
    )
    # Truyền tất cả dữ liệu vào template
    context = {
        'total_revenue': total_revenue,
        'new_customers': new_customers,
        'total_orders': total_orders,
        'total_products_sold': total_products_sold,
        'top_products': top_products,
        'stock_quantity': stock_quantity,
        'monthly_revenue': monthly_revenue,
        'monthly_orders': monthly_orders,
        'start_date': start_date,
        'end_date': end_date,
        'month_filter': month_filter,
        'year_filter': year_filter,
    }

    return render(request, 'admin/dashboard.html', context)


def receipt_list(request):
    receipts = Receipt.objects.all()  # Lấy tất cả các Receipt
    return render(request, 'admin/receipt_list.html', {'receipts': receipts})

# View to display the details of a specific receipt
def receipt_detail(request, receipt_id):
    receipt = get_object_or_404(Receipt, receipt_id=receipt_id)
    # Truy vấn chi tiết các sản phẩm trong receipt thông qua mối quan hệ với Receipt_Detail
    details = receipt.details.all()  # 'details' là related_name từ Receipt_Detail
    return render(request, 'admin/receipt_detail.html', {'receipt': receipt, 'details': details})

def add_receipt(request):
    receipt_form = ReceiptForm()
    detail_form = ReceiptDetailForm()
    added_products = request.session.get('added_products', [])
    cate_form = ProductForm1()
    if request.method == 'POST':
        # Xóa sản phẩm từ danh sách tạm thời
        if 'delete_product' in request.POST:
            delete_index_str = request.POST.get('delete_product')  # Lấy chỉ số sản phẩm từ POST
            if delete_index_str is not None:
                try:
                    delete_index = int(delete_index_str)  # Chuyển đổi chỉ số sang int
                    if 0 <= delete_index < len(added_products):  # Kiểm tra chỉ số hợp lệ
                        added_products.pop(delete_index)  # Xóa sản phẩm khỏi danh sách
                        request.session['added_products'] = added_products  # Cập nhật lại session
                except ValueError:
                    pass  # Nếu không thể chuyển đổi chỉ số, không làm gì và bỏ qua

            # Kết thúc xử lý xóa và trả về giao diện mà không cần xử lý form
            return render(request, 'admin/add_receipt.html', {
                'receipt_form': receipt_form,
                'detail_form': detail_form,
                'added_products': added_products,
                'cate_form': cate_form
            })

        # Thêm sản phẩm vào phiếu nhập
        elif 'add_product' in request.POST:
            detail_form = ReceiptDetailForm(request.POST)
            if detail_form.is_valid():
                product_data = detail_form.cleaned_data
                product = product_data['product']  # Lấy đối tượng Product
                product_info = {
                    'product_id': product.product_id,
                    'product_name': product.name,
                    'quantity': product_data['quantity'],
                    'price': str(product_data['price']),
                    'unit': product_data['unit'],
                    'expiry_date': product_data['expiry_date'].strftime('%Y-%m-%d') if product_data['expiry_date'] else None
                }
                added_products.append(product_info)  # Thêm sản phẩm vào danh sách tạm thời
                request.session['added_products'] = added_products  # Lưu vào session

        # Lưu phiếu nhập và chi tiết sản phẩm vào DB
        elif 'save_receipt' in request.POST:
            receipt_form = ReceiptForm(request.POST)
            if receipt_form.is_valid() and added_products:
                # Lưu phiếu nhập vào DB
                receipt = receipt_form.save()
                
                # Lưu chi tiết sản phẩm vào DB và cập nhật số lượng sản phẩm trong kho
                for product_info in added_products:
                    try:
                        product = Product.objects.get(product_id=product_info['product_id'])

                        # Cập nhật số lượng sản phẩm trong kho
                        product.quantity += int(product_info['quantity'])
                        product.ex_date = product_info['expiry_date']
                        product.save()  # Lưu lại sản phẩm với số lượng mới

                        # Lưu chi tiết phiếu nhập
                        Receipt_Detail.objects.create(
                            receipt=receipt,
                            product=product,
                            quantity=product_info['quantity'],
                            price=product_info['price'],
                            unit=product_info['unit'],
                            expiry_date=product_info['expiry_date']
                        )
                    except ObjectDoesNotExist:
                        continue  # Bỏ qua nếu không tìm thấy sản phẩm

                # Xóa danh sách sản phẩm sau khi lưu phiếu nhập
                request.session['added_products'] = []

                # Điều hướng đến danh sách phiếu nhập
                return redirect('receipt_list')  # Điều hướng đến danh sách phiếu nhập

    # Render lại trang mà không yêu cầu điền lại form khi xóa sản phẩm
    return render(request, 'admin/add_receipt.html', {
        'receipt_form': receipt_form,
        'detail_form': detail_form,
        'added_products': added_products,
        'cate_form': cate_form
    })

# View để thêm nhà cung cấp
@csrf_exempt  # Tắt kiểm tra CSRF cho yêu cầu AJAX (nếu bạn đang sử dụng fetch với CSRF token)
def add_supplier(request):
    if request.method == "POST":
        try:
            # Lấy dữ liệu từ yêu cầu AJAX
            data = json.loads(request.body)
            name = data.get('name',)
            address = data.get('address')
            phone = data.get('phone')

            # Kiểm tra nếu tên nhà cung cấp trống
            if not name and not phone and not address:
                return JsonResponse({'success': False, 'error': 'Vui lòng điền đầy đủ thongo tin!'}, status=400)

            # Tạo một đối tượng Supplier mới và lưu vào cơ sở dữ liệu
            supplier = Supplier.objects.create(name=name, address= address, phone_number=phone)

            # Trả về phản hồi thành công
            return JsonResponse({'success': True})

        except Exception as e:
            # Xử lý lỗi nếu có
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Phương thức không hợp lệ'}, status=405)

    # View để thêm sản phẩm
# View để thêm sản phẩm
@csrf_exempt
def add_product(request):
    if request.method == "POST":
        try:
            # Lấy dữ liệu từ yêu cầu AJAX
            data = json.loads(request.body)
            product_name = data.get('product_name')
            product_category = data.get('product_category')

            # Kiểm tra xem tên sản phẩm và danh mục có hợp lệ không
            if not product_name or not product_category:
                return JsonResponse({'success': False, 'error': 'Tên sản phẩm và danh mục không thể trống!'}, status=400)

            # Kiểm tra xem danh mục có tồn tại không
            try:
                category = Category.objects.get(category_id=product_category)
            except Category.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Danh mục không tồn tại!'}, status=404)

            # Tạo mới sản phẩm
            Product.objects.create(name=product_name, category=category)

            # Trả về phản hồi thành công
            return JsonResponse({'success': True, 'message': 'Sản phẩm mới đã được thêm thành công'})

        except Exception as e:
            # Xử lý lỗi
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Phương thức không hợp lệ'}, status=405)

def add_product_view(request):
    form = ProductForm()
    return render(request, 'admin/add_product.html', {'form': form})

# def products_view(request, cate_id=None):
#     category = Category.objects.all()
#     if cate_id:
#         cate_name = get_object_or_404(Category, pk=cate_id)
#         product_list = Product.objects.filter(category=cate_name)
#     else:
#         cate_name = None  # Thêm dòng này để tránh lỗi
#         product_list = Product.objects.all()

#     # Áp dụng sắp xếp dựa trên sort_option
#     sort_option = request.GET.get('sort', 'default')
#     if sort_option == 'price_asc':
#         product_list = product_list.order_by('price')
#     elif sort_option == 'price_desc':
#         product_list = product_list.order_by('-price')
#     elif sort_option == 'name':
#         product_list = product_list.order_by('name')

#     # Lấy danh sách 3 sản phẩm mới nhất được thêm trong vòng 1 ngày
#     latest_products = Product.objects.filter(posting_date__gte=timezone.now() - timezone.timedelta(days=1)).order_by('-posting_date')[:3]

#     # Xử lý giá sau giảm và gắn dữ liệu
#     now_time = timezone.now()
#     processed_products = []
#     for product in product_list:
#         discounted_price = product.price  # Giá mặc định là giá gốc
#         if product.coupon and product.coupon.expiry_date > now_time:
#             discount = Decimal(product.coupon.discount) / Decimal(100)
#             discounted_price = product.price * (1 - discount)

#         processed_products.append({
#             'product': product,
#             'discounted_price': discounted_price,
#         })

#     total_products = product_list.count()

#     # Phân trang
#     paginator = Paginator(product_list, 9)
#     page_number = request.GET.get('page', 1)
#     page_obj = paginator.get_page(page_number)

#     data = {
#         'category': category,
#         'page_obj': page_obj,
#         'cate_name': cate_name,  # cate_name giờ luôn được khởi tạo
#         'sort_option': sort_option,
#         'total_products': total_products,
#         'latest_products': latest_products,
        
#     }
#     return render(request, 'pages/products.html', data)

from django.utils.timezone import now
from decimal import Decimal

def products_view(request, cate_id=None):
    total_wishlist = 0
    total_quantity = 0

    # Lấy dữ liệu giỏ hàng và danh sách yêu thích nếu người dùng đăng nhập
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(account=request.user)
        total_quantity = sum(item.quantity for item in cart_items)
            
        wishlist_items = Wishlist.objects.filter(account=request.user)
        total_wishlist = wishlist_items.count()

    category = Category.objects.all()
    if cate_id:
        cate_name = get_object_or_404(Category, pk=cate_id)
        product_list = Product.objects.filter(category=cate_name, display_product=True)
    else:
        cate_name = None  # Thêm dòng này để tránh lỗi
        product_list = Product.objects.filter(display_product=True)

    # Áp dụng sắp xếp dựa trên sort_option
    sort_option = request.GET.get('sort', 'default')
    if sort_option == 'price_asc':
        product_list = product_list.order_by('price')
    elif sort_option == 'price_desc':
        product_list = product_list.order_by('-price')
    elif sort_option == 'name':
        product_list = product_list.order_by('name')

    # Lấy danh sách 3 sản phẩm mới nhất được thêm trong vòng 1 ngày
    latest_products = Product.objects.filter(
        posting_date__gte=timezone.now() - timezone.timedelta(days=1)
    ).order_by('-posting_date')[:3]

    # Xử lý giá sau giảm và gắn dữ liệu
    now_time = timezone.now()
    processed_products = []
    for product in product_list:
        discounted_price = product.price  # Giá mặc định là giá gốc
        if product.coupon and product.coupon.expiry_date > now_time:
            discount = Decimal(product.coupon.discount) / Decimal(100)
            discounted_price = product.price * (1 - float(discount))

        processed_products.append({
            'product': product,
            'discounted_price': discounted_price,
        })

    # Tổng số sản phẩm
    total_products = product_list.count()

    # Phân trang
    paginator = Paginator(processed_products, 9)  # Sử dụng danh sách đã xử lý giảm giá
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    data = {
        'category': category,
        'page_obj': page_obj,
        'cate_name': cate_name,
        'sort_option': sort_option,
        'total_products': total_products,
        'latest_products': latest_products,
        'total_wishlist':total_wishlist,
        'total_quantity':total_quantity,
        'now': now(),
    }
    return render(request, 'pages/products.html', data)

def search(request):
    total_wishlist = 0
    total_quantity = 0

    # Lấy dữ liệu giỏ hàng và danh sách yêu thích nếu người dùng đăng nhập
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(account=request.user)
        total_quantity = sum(item.quantity for item in cart_items)
            
        wishlist_items = Wishlist.objects.filter(account=request.user)
        total_wishlist = wishlist_items.count()

    categories = Category.objects.all()
    query = request.GET.get('query', '')  
    if query:
        product_list = Product.objects.filter(name__icontains=query, display_product=True)
        
    else:
        product_list = Product.objects.filter(display_product=True)  
    # Áp dụng sắp xếp dựa trên sort_option
    sort_option = request.GET.get('sort', 'default')
    if sort_option == 'price_asc':
        product_list = product_list.order_by('price')
    elif sort_option == 'price_desc':
        product_list = product_list.order_by('-price')
    elif sort_option == 'name':
        product_list = product_list.order_by('name')

    latest_products = Product.objects.filter(posting_date__gte=timezone.now() - timezone.timedelta(days=1)).order_by('-posting_date')[:3]
    
    # Xử lý giá sau giảm và gắn dữ liệu
    now_time = timezone.now()
    processed_products = []
    for product in product_list:
        discounted_price = product.price  # Giá mặc định là giá gốc
        if product.coupon and product.coupon.expiry_date > now_time:
            discount = Decimal(product.coupon.discount) / Decimal(100)
            discounted_price = product.price * (1 - float(discount))

        processed_products.append({
            'product': product,
            'discounted_price': discounted_price,
        })

    total_products = product_list.count()
    # Phân trang
    paginator = Paginator(processed_products, 9)  
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'categories': categories,  # Hiển thị danh mục
        'page_obj': page_obj,  # Sản phẩm đã phân trang
        'query': query,  # Từ khóa tìm kiếm
        'sort_option': sort_option,  # Tùy chọn sắp xếp
        'latest_products': latest_products,  # Sản phẩm mới nhất
        'total_products': total_products,
        'total_wishlist':total_wishlist,
        'total_quantity' :total_quantity,
        'now': now()
    }
    return render(request, 'pages/search.html', context)



from django.shortcuts import render, get_object_or_404
from .models import Product

def contact(request):
    total_wishlist = 0
    total_quantity = 0

    # Lấy dữ liệu giỏ hàng và danh sách yêu thích nếu người dùng đăng nhập
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(account=request.user)
        total_quantity = sum(item.quantity for item in cart_items)
            
        wishlist_items = Wishlist.objects.filter(account=request.user)
        total_wishlist = wishlist_items.count()
    
    context ={
        'total_wishlist':total_wishlist,
        'total_quantity':total_quantity,
    }
    return render(request, 'pages/contact.html', context)

def track_orders(request):
    # Lọc đơn hàng theo từng trạng thái 
    total_wishlist = 0
    total_quantity = 0

    # Lấy dữ liệu giỏ hàng và danh sách yêu thích nếu người dùng đăng nhập
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(account=request.user)
        total_quantity = sum(item.quantity for item in cart_items)
            
        wishlist_items = Wishlist.objects.filter(account=request.user)
        total_wishlist = wishlist_items.count()

    orders_by_status = {
        'pending': Orders.objects.filter(status_order='Chờ xác nhận', account=request.user),
        'processing': Orders.objects.filter(status_order='Chờ lấy hàng', account=request.user),
        'shipping': Orders.objects.filter(status_order='Đang vận chuyển', account=request.user),
        'delivered': Orders.objects.filter(status_order='Đã giao', account=request.user),
        'cancelled': Orders.objects.filter(status_order='Đã hủy', account=request.user),
    }
    context = {
        'orders_by_status': orders_by_status,
        'total_wishlist':total_wishlist,
        'total_quantity':total_quantity

        }
    return render(request, 'pages/track_orders.html', context)


def order_detail(request, order_id):
    # Lấy đơn hàng và các chi tiết liên quan đến đơn hàng
    order = get_object_or_404(Orders, order_id=order_id, account=request.user)  # Chỉ lấy đơn hàng của người dùng hiện tại
    order_details = OrderDetail.objects.filter(order=order)  # Lấy tất cả các chi tiết của đơn hàng này
    for detail in order_details:
        product = detail.product
        if product.coupon:
            detail.discounted_price = product.price * (1 - float(product.coupon.discount) / 100)
        else:
            detail.discounted_price = product.price
    # Truyền dữ liệu đơn hàng và chi tiết đơn hàng vào template
    context = {
        'order': order,
        'order_details': order_details,
        'now': now()
    }
    return render(request, 'pages/order_detail.html', context)

def cancel_order(request, order_id):
    if request.method == 'POST':
        # Lấy đơn hàng
        order = get_object_or_404(Orders, order_id=order_id)
        
        # Kiểm tra trạng thái có thể hủy
        if order.status_order not in ['Chờ xác nhận', 'processing']:
            return JsonResponse({'error': 'Đơn hàng này không thể hủy.'}, status=400)
        
        # Cập nhật trạng thái
        order.status_order = 'Đã hủy'
        order.save()
        return JsonResponse({'success': 'Đơn hàng đã được hủy thành công.'})
    
    return JsonResponse({'error': 'Phương thức không hợp lệ.'}, status=405)

def stock_products(request):
    stock_products = Product.objects.all()
    
    return render(request, 'admin/stock_products.html', {
        'stock_products': stock_products,
    })

def defective_product_view(request):
    defective_products = Defective_Product.objects.all()
    
    return render(request, 'admin/Defective_Product.html', {
        'defective_products': defective_products,
    })

def apply_coupon(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)

        coupon_code = data.get("coupon")
        total_price = data.get("total_price", 0)

        try:
            coupon = Coupon.objects.get(name=coupon_code)

            if not coupon.is_valid:
                return JsonResponse({
                    "success": False,
                    "message": "Mã khuyến mãi không hợp lệ hoặc đã hết hạn."
                })

            discount = float(coupon.discount)
            new_total = total_price - (total_price * discount / 100)

            return JsonResponse({
                "success": True,
                "new_total": new_total,
                "message": f"Áp dụng mã {coupon_code} thành công! Bạn được giảm {discount}%.",
            })
        except Coupon.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": "Mã khuyến mãi không tồn tại."
            })

    return JsonResponse({"success": False, "message": "Phương thức không được hỗ trợ."})


def admin_order_list(request):
    if not request.user.is_staff:
        return JsonResponse({'status': 'fail', 'message': 'Unauthorized'}, status=403)

    status_filter = request.GET.get('status')
    query = Orders.objects.all()

    if status_filter:
        query = query.filter(status_order=status_filter)

    orders = query.order_by('-order_time').values(
        'order_id', 'order_time', 'status_order', 'price', 'account__username', 'address_detail'
    )

    return JsonResponse({'status': 'success', 'orders': list(orders)})

def admin_order_detail(request, order_id):
    if not request.user.is_staff:
        return JsonResponse({'status': 'fail', 'message': 'Unauthorized'}, status=403)

    order = Orders.objects.filter(order_id=order_id).first()
    if not order:
        return JsonResponse({'status': 'fail', 'message': 'Order not found'}, status=404)

    details = order.details.values('product__name', 'quantity', 'price')
    data = {
        'order_id': order.order_id,
        'order_time': order.order_time,
        'delivery_time': order.delivery_time,
        'status_order': order.status_order,
        'address_detail': order.address_detail,
        'account': order.account.username,
        'price': order.price,
        'details': list(details),
    }

    return JsonResponse({'status': 'success', 'order': data})


# Admin update order status
@csrf_exempt
def admin_update_status(request, order_id):
    if not request.user.is_staff:
        return JsonResponse({'status': 'fail', 'message': 'Unauthorized'}, status=403)

    order = Orders.objects.filter(order_id=order_id).first()
    if not order:
        return JsonResponse({'status': 'fail', 'message': 'Order not found'}, status=404)

    data = json.loads(request.body)
    new_status = data.get('status')
    if new_status not in dict(Orders.STATUS_CHOICES):
        return JsonResponse({'status': 'fail', 'message': 'Invalid status'}, status=400)

    order.status_order = new_status
    if new_status == 'delivered':
        order.delivery_time = timezone.now()
    order.save()

    return JsonResponse({'status': 'success', 'message': 'Order updated successfully'})

# review 
def product_review(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    reviews = Feedback.objects.filter(product=product).order_by('-posting_date')
    star_range = range(1, 6)

    # Lấy đánh giá của người dùng hiện tại (nếu có)
    user_review = reviews.filter(account=request.user).first()

    if request.method == 'POST':
        try:
            # Lấy dữ liệu từ form
            rating = int(request.POST.get('rating', 0))  # Lấy số sao
            feedback = request.POST.get('feedback', '').strip()
            img_feedback = request.FILES.get('img_feedback')  # Lấy file ảnh

            if rating < 1 or rating > 5:
                return JsonResponse({'error': 'Xếp hạng không hợp lệ'}, status=400)

            # Nếu người dùng đã đánh giá trước đó
            if user_review:
                user_review.rating_star = rating
                user_review.feedback_content = feedback
                if img_feedback:
                    user_review.img_feedback = img_feedback  # Cập nhật ảnh nếu có
                user_review.save()
            else:
                # Nếu đây là đánh giá mới
                Feedback.objects.create(
                    rating_star=rating,
                    feedback_content=feedback,
                    img_feedback=img_feedback,
                    account=request.user,
                    product=product
                )

            # Tải lại danh sách đánh giá
            reviews = Feedback.objects.filter(product=product).order_by('-posting_date')
            user_review = reviews.filter(account=request.user).first()

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    context = {
        'product': product,
        'reviews': reviews,
        'star_range': star_range,
        'user_review': user_review,
    }
    return render(request, 'pages/product_review.html', context)

def product_detail(request, id):
    total_wishlist = 0
    total_quantity = 0

    # Lấy dữ liệu giỏ hàng và danh sách yêu thích nếu người dùng đăng nhập
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(account=request.user)
        total_quantity = sum(item.quantity for item in cart_items)
            
        wishlist_items = Wishlist.objects.filter(account=request.user)
        total_wishlist = wishlist_items.count()

    product = Product.objects.get(product_id =id)
    reviews = Feedback.objects.filter(product=product).order_by('-posting_date')
    star_range = range(1, 6)
    # Lấy đánh giá của người dùng hiện tại (nếu có)
    if request.user.is_authenticated:
        # Lấy đánh giá của người dùng hiện tại (nếu có)
        user_review = reviews.filter(account=request.user).first()
    else:
        user_review = None  # If not authenticated, set it to None
    count_review =reviews.count()
    #initial_reviews = reviews[:4]  # Chỉ lấy 4 đánh giá ban đầu
    # Tính trung bình rating_star, làm tròn số nguyên gần nhất
    average_rating = reviews.aggregate(Avg('rating_star'))['rating_star__avg']
    average_rating_rounded = round(average_rating) if average_rating else 0

    # Tạo danh sách số sao đầy đủ và sao trống
    stars_full = list(range(average_rating_rounded))
    stars_empty = list(range(5 - average_rating_rounded))
    if product.coupon and product.coupon.expiry_date > now():
        discounted_price = product.price * (1 - float(product.coupon.discount) / 100)
    else:
        discounted_price = product.price
    context = {
        'product': product,
        'reviews': reviews,
        'star_range': star_range,
        'user_review': user_review,
        'count_review':count_review,
        'discounted_price': discounted_price,
        'stars_full': stars_full,
        'stars_empty': stars_empty,
        'total_wishlist': total_wishlist ,
        'total_quantity' : total_quantity ,
        'now': now(),
        
    }
    return render(request, 'pages/product_details.html', context)

def update_defective_products(request):
    # Logic để tìm sản phẩm hết hạn và cập nhật
    expired_products = Product.objects.filter(ex_date__lt=now(), status='Còn hàng')
    
    for product in expired_products:
        Defective_Product.objects.create(
            product=product,
            quantity=product.quantity,
            reason='Hết hạn sử dụng',
            status='Hỏng'
        )
        product.status = 'Hết hàng'
        product.quantity = 0
        product.save()
    
    return HttpResponse("Sản phẩm đã được cập nhật.")

import shutil
from django.core.management import call_command

def backup_database(request):
    try:
        # For SQLite (copying the database file)
        if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
            backup_file = os.path.join(settings.BASE_DIR, 'db_backup.sqlite3')
            shutil.copy(os.path.join(settings.BASE_DIR, 'db.sqlite3'), backup_file)
        
        # For PostgreSQL (using dumpdata or pg_dump)
        elif settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
            # Using Django dumpdata
            call_command('dumpdata', output='db_backup.json')
        
        return JsonResponse({'status': 'success', 'message': 'Database backup completed successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
def restore_database(request):
    try:
        # For SQLite (copying the database file)
        if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
            backup_file = os.path.join(settings.BASE_DIR, 'db_backup.sqlite3')
            shutil.copy(backup_file, os.path.join(settings.BASE_DIR, 'db.sqlite3'))

        # For PostgreSQL (using loaddata or pg_restore)
        elif settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
            call_command('loaddata', 'db_backup.json')

        return JsonResponse({'status': 'success', 'message': 'Database restored successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
def update_cart_detail(request, product_id):
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        quantity = int(request.POST.get('quantity'))

        # Lấy sản phẩm từ giỏ hàng
        cart_item = Cart.objects.get(product_id=product_id, user=request.user)

        # Xử lý tăng/giảm số lượng
        if action == "add":
            cart_item.quantity += 1
        elif action == "remove" and cart_item.quantity > 1:
            cart_item.quantity -= 1

        # Lưu lại thông tin giỏ hàng
        cart_item.save()

        return JsonResponse({'success': True, 'quantity': cart_item.quantity})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Product, Cart

def add_to_cart_detail(request):
    if not request.user.is_authenticated:
        return  JsonResponse({'error': 'Bạn cần đăng nhập để thêm vào giỏ hàng.'}, status=401)

    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        # Lấy sản phẩm từ cơ sở dữ liệu
        product = get_object_or_404(Product, product_id=product_id)

        # Kiểm tra số lượng sản phẩm trong kho
        if quantity > product.quantity:
            return JsonResponse({'error': 'Số lượng trong kho không đủ!'}, status=400)

        # Tìm hoặc tạo mới mục trong giỏ hàng
        cart_item, created = Cart.objects.get_or_create(account=request.user, product=product)
        
        # Nếu sản phẩm đã có trong giỏ, cập nhật số lượng
        if not created:
            # Kiểm tra xem tổng số lượng trong giỏ hàng cộng với số lượng mới có vượt quá số lượng trong kho không
            if cart_item.quantity + quantity > product.quantity:
                return JsonResponse({'error': 'Số lượng trong kho không đủ!'}, status=400)
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity

        # Lưu lại vào giỏ hàng
        cart_item.save()

        # Tính tổng số lượng sản phẩm trong giỏ hàng
        total_quantity = Cart.objects.filter(account=request.user).aggregate(total=Sum('quantity'))['total']
        
        return JsonResponse({
            'message': 'Thêm vào giỏ hàng thành công!',
            'total_quantity': total_quantity
        })

    return JsonResponse({'error': 'Yêu cầu không hợp lệ.'}, status=400)

from django.db.models import Q

def blog_view(request, blog_id=None):
    total_wishlist = 0
    total_quantity = 0

    # Lấy dữ liệu giỏ hàng và danh sách yêu thích nếu người dùng đăng nhập
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(account=request.user)
        total_quantity = sum(item.quantity for item in cart_items)
            
        wishlist_items = Wishlist.objects.filter(account=request.user)
        total_wishlist = wishlist_items.count()
    
    # Lấy danh mục blog
    title_blog = TitleBlog.objects.annotate(blog_count=Count('blog'))
    # Lấy danh mục blog kèm số lượng bài viết

    # Xử lý tìm kiếm
    search_query = request.GET.get('search', '')
    if search_query:
        blog_list = Blog.objects.filter(
            Q(title__icontains=search_query)  # Sửa từ `content` thành `detail`
        ).order_by('-create_date')
        blog_name = None
    elif blog_id:
        # Lọc bài viết theo danh mục
        blog_name = get_object_or_404(TitleBlog, pk=blog_id)
        blog_list = Blog.objects.filter(title_blog=blog_name).order_by('-create_date')
    else:
        blog_name = None
        blog_list = Blog.objects.all().order_by('-create_date')


    total_blog = blog_list.count()
    recent_blogs = Blog.objects.all().order_by('-create_date')[:3]
    # Thêm phân trang cho blog_list


    paginator = Paginator(blog_list, 4)  # Hiển thị 4 bài viết mỗi trang
    page_number = request.GET.get('page')
    blogs = paginator.get_page(page_number)

    context = {
        'blogs': blogs,  # Danh sách bài viết đã phân trang
        'title_blog': title_blog,
        'recent_blogs':recent_blogs,
        'total_blog':total_blog,
        'total_quantity': total_quantity,
        'total_wishlist': total_wishlist,
        'search_query': search_query,  # Truyền search_query vào context
    }
    return render(request, 'pages/blog.html', context)


def blog_detail(request, blog_id):
    total_wishlist = 0
    total_quantity = 0

    # Lấy dữ liệu giỏ hàng và danh sách yêu thích nếu người dùng đăng nhập
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(account=request.user)
        total_quantity = sum(item.quantity for item in cart_items)
            
        wishlist_items = Wishlist.objects.filter(account=request.user)
        total_wishlist = wishlist_items.count()
    
    blog = get_object_or_404(Blog, id =blog_id)
    blog_title = TitleBlog.objects.all()
     # Lấy thông tin tác giả (admin)
    author = blog.account  # Assuming `author` is a ForeignKey to User or similar
    author_image = author.avatar.url if author.avatar else None
    author_name = author.get_full_name() or author.username  # Fetching full name or username if no full name
    context = {
        'blog_title':blog_title,
        'blog':blog,
        'total_quantity': total_quantity,
        'total_wishlist': total_wishlist,
        'author_image':author_image,
        'author_name':author_name
    }
    return render(request, 'pages/blog_detail.html', context)


