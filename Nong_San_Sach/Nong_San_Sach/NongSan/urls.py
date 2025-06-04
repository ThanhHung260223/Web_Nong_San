from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import  RegisterView, CustomLoginView, ResetPasswordView, ChangePasswordView
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from .views import profile

urlpatterns = [
    path("",views.index, name='index'),
    path("contact/", views.contact, name='contact'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),  # Thêm URL cho giỏ hàng  
    path('checkout/', views.checkout, name='checkout'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('add-to-wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/', views.wishlist_view, name='wishlist'),    
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('get_districts/', views.get_districts, name='get_districts'),
    path('get_wards/', views.get_wards, name='get_wards'),
    path('confirm-order/', views.confirm_order, name='confirm_order'),
    # path đăng nhập , đăng kí, đăng xuất
    path('register/', RegisterView.as_view(), name='users-register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='pages/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
         
    path('profile/', profile, name='profile'),
    path('password-change/', ChangePasswordView.as_view(), name='password_change'),
     #path('admin/report/', views.report_view, name='admin_report'),

    path('admin/dashboard/', views.dashboard, name='dashboard'),
     path('admin/add_receipt/', views.add_receipt, name='add_receipt'),
    path('admin/add_supplier/', views.add_supplier, name='add_supplier'),
    path('admin/add_product/', views.add_product, name='add_product'),
     path('admin/receipts/', views.receipt_list, name='receipt_list'),
    path('admin/receipts/<int:receipt_id>/', views.receipt_detail, name='receipt_detail'),
    #     path('danhmuc',views.category_list, name='danhmuc'),
    path('shop-details/<int:id>/', views.product_detail, name='product_detail'),
    path('products/', views.products_view, name='products'),
    path('products/<int:cate_id>/', views.products_view, name='products_by_category'),
    path("contact/", views.contact, name='contact'),
    path('search/', views.search, name='search'),
     path('track_orders/', views.track_orders, name='track_orders'),
     path('order/<int:order_id>/', views.order_detail, name='order_detail'),
     path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
     path('admin/stock_products/', views.stock_products, name='stock_products'),
     path('admin/defective_Product/', views.defective_product_view, name='defective_Product'),
     path('apply_coupon/', views.apply_coupon, name='apply_coupon'),
     path('products/<int:product_id>/review/', views.product_review, name='product_review'),
     path('backup/', views.backup_database, name='backup_database'),
    path('restore/', views.restore_database, name='restore_database'),
    path('update-defective-products/', views.update_defective_products),
    
    path('add-to-cart/', views.add_to_cart_detail, name='add_to_cart_detail'),
     path("blog/", views.blog_view, name='blog_view'),
    path('blog/<int:blog_id>/', views.blog_view, name='blog_by_title'),
    path('blogdetail/<int:blog_id>/', views.blog_detail, name='blog_detail'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
