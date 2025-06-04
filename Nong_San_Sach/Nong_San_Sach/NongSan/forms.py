import re
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate
from .models import Account, Product, Cart, Category, Orders, Wishlist, Receipt, Receipt_Detail, Supplier


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

class CartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = '__all__'

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'

class OrdersForm(forms.ModelForm):
    class Meta:
        model = Orders
        fields = '__all__'

class WishlistForm(forms.ModelForm):
    class Meta:
        model = Wishlist
        fields = '__all__'



# class DangKy(forms.ModelForm):
#     pass1 = forms.CharField(label='Mật khẩu', widget=forms.PasswordInput())
#     pass2 = forms.CharField(label='Nhập lại mật khẩu', widget=forms.PasswordInput())
    
#     class Meta:
#         model = Account
#         fields = ['username', 'email', 'phone_number']  # Chỉ giữ lại các trường cần thiết

#     def clean_pass2(self):
#         if 'pass1' in self.cleaned_data:
#             pass1 = self.cleaned_data['pass1']
#             pass2 = self.cleaned_data['pass2']
#             if pass1 == pass2 and pass1:
#                 return pass2
#         raise forms.ValidationError("Mật khẩu không khớp")

#     def clean_username(self):
#         username = self.cleaned_data.get('username')
#         if Account.objects.filter(username=username).exists():
#             raise forms.ValidationError("Tài khoản đã tồn tại")
#         return username


# class DangNhap(forms.Form):
#     username = forms.CharField(label='Tài khoản', max_length=30)
#     password = forms.CharField(label='Mật khẩu', widget=forms.PasswordInput())

#     def clean(self):
#         cleaned_data = super().clean()
#         username = cleaned_data.get('username')
#         password = cleaned_data.get('password')

#         if username and password:
#             user = authenticate(username=username, password=password)
#             if not user:
#                 raise forms.ValidationError("Tài khoản hoặc mật khẩu không đúng")
#         return cleaned_data


#=========>Form đăng nhập, đăng kí <=========
from .models import Account
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _


class RegisterForm(UserCreationForm):
    # fields we want to include and customize in our form
    first_name = forms.CharField(max_length=100,
                                 required=True,
                                 widget=forms.TextInput(attrs={'placeholder': _('Tên'),'class': 'form-control'}),
                                 error_messages={
                                     'required': _('Vui lòng nhập họ tên.'),
                                    'max_length': _('Tên không được vượt quá 100 ký tự.')
                                 }  )
    
    last_name = forms.CharField(max_length=100,
                                required=True,
                                widget=forms.TextInput(attrs={'placeholder': _('Họ'),
                                                              'class': 'form-control'
                                                              }),
                                error_messages={
                                      'required': _('Vui lòng nhập họ.'),
                                      'max_length': _('Họ không được vượt quá 100 ký tự.')
                                 }  )                              
                                                              
                                                              
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'placeholder': _('Tên đăng nhập'),
                                                             'class': 'form-control'
                                                             }),
                                error_messages={
                                         'required': _('Vui lòng nhập tên đăng nhập.'),
            'max_length': _('Tên đăng nhập không được vượt quá 100 ký tự.')
                                                }
                                     )
    email = forms.EmailField(required=True,
                             widget=forms.TextInput(attrs={'placeholder': _('Email'),
                                                           'class': 'form-control'
                                                           }),
                              error_messages={
                                    'required': _('Vui lòng nhập địa chỉ email.'),
            'invalid': _('Địa chỉ email không hợp lệ!')
                                        }
                                    )                             
    
    password1 = forms.CharField(max_length=50,
                                required=True,
                                widget=forms.PasswordInput(attrs={'placeholder': _('Mật khẩu'),
                                                                  'class': 'form-control',
                                                                  'data-toggle': 'password',
                                                                  'id': 'password'
                                                                  }),
                                 error_messages={
                                        'required': _('Vui lòng nhập mật khẩu.'),
            'max_length': _('Mật khẩu không được vượt quá 50 ký tự.')
                                    }                                 
                                                                  )
    password2 = forms.CharField(max_length=50,
                                required=True,
                                widget=forms.PasswordInput(attrs={'placeholder': _('Xác nhận mật khẩu'),
                                                                  'class': 'form-control',
                                                                  'data-toggle': 'password',
                                                                  'id': 'password'
                                                                  }),
                                error_messages={
                                            'required': _('Vui lòng xác nhận mật khẩu.'),
            'max_length': _('Mật khẩu không được vượt quá 50 ký tự.')
                                        }                                 
                                                                  )
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name:
            raise forms.ValidationError(_('Tên không được bỏ trống.'))
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name:
            raise forms.ValidationError(_('Họ không được bỏ trống.'))
        return last_name

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Account.objects.filter(username=username).exists():
            raise forms.ValidationError(_('Tên người dùng đã tồn tại.'))
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Account.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Email đã tồn tại.'))
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            raise forms.ValidationError(_('Email không hợp lệ.'))
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 8:
            raise forms.ValidationError(_('Mật khẩu phải có ít nhất 8 ký tự.'))
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError(_('Mật khẩu phải chứa ít nhất một chữ cái viết hoa.'))
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise forms.ValidationError(_('Mật khẩu phải chứa ít nhất một ký tự đặc biệt.'))
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        
        if password1 and password2 and password1 != password2:
            self.add_error('password2', _("Mật khẩu không khớp."))
            
        return cleaned_data
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']
    
class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Tên đăng nhập',
                                                             'class': 'form-control',
                                                             }))
    password = forms.CharField(max_length=50,
                               required=True,
                               widget=forms.PasswordInput(attrs={'placeholder': 'Mật khẩu',
                                                                 'class': 'form-control',
                                                                 'data-toggle': 'password',
                                                                 'id': 'password',
                                                                 'name': 'password',
                                                                 }))
    remember_me = forms.BooleanField(required=False)

    class Meta:
        model = Account
        fields = ['username', 'password', 'remember_me']


# forms.py
from django import forms
from .models import Account
from django.core.validators import RegexValidator

class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Vui lòng nhập tên người dùng.'}
    )
    email = forms.EmailField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Vui lòng nhập email.'}
    )

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Account.objects.filter(username=username).exclude(id=self.current_user.id).exists():
            raise forms.ValidationError("Tên người dùng đã tồn tại.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Account.objects.filter(email=email).exclude(id=self.current_user.id).exists():
            raise forms.ValidationError("Email này đã được sử dụng.")
        return email
    
    class Meta:
        model = Account
        fields = ['username', 'email']


class UpdateProfileForm(forms.ModelForm):
    phone_number = forms.CharField(max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[
            RegexValidator( # type: ignore
                regex=r'^0[3|5|7|8|9]\d{8}$',
                message="Số điện thoại không hợp lệ. Vui lòng nhập số điện thoại Việt Nam hợp lệ."
            )
        ]
    )

    
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control-file'})
    )

    class Meta:
        model = Account
        fields = ['avatar', 'phone_number', 'default_address']

# Form cho Receipt
class ReceiptForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = ['supplier', 'date_receipt']
        widgets = {
            'date_receipt': forms.DateInput(attrs={'type': 'date'}),
        }

# Form cho Receipt Detail
class ReceiptDetailForm(forms.ModelForm):
    
    class Meta:
        model = Receipt_Detail
        fields = ['product', 'expiry_date','quantity', 'price', 'unit']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ProductForm1(forms.Form):
    categories = Category.objects.all()
    category_choices = [(category.category_id, category.name) for category in categories]

    category = forms.ChoiceField(
        choices=category_choices,
        widget=forms.Select(attrs={'id': 'category_id'})
    )

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name']  # Chọn các trường phù hợp với Supplier model của bạn

class CateForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Chọn danh mục",
        widget=forms.Select(attrs={'category_id': 'new_product_category'})
    )