# Generated by Django 5.1.3 on 2024-12-09 16:22

import ckeditor.fields
import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('category_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('image', models.ImageField(blank=True, null=True, upload_to='category_images/')),
            ],
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('coupon_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('discount', models.DecimalField(decimal_places=0, max_digits=5)),
                ('posting_date', models.DateTimeField(blank=True, null=True)),
                ('expiry_date', models.DateTimeField(blank=True, null=True)),
                ('decription', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('order_id', models.AutoField(primary_key=True, serialize=False)),
                ('order_time', models.DateTimeField(auto_now_add=True)),
                ('delivery_time', models.DateTimeField(null=True)),
                ('status_order', models.CharField(choices=[('Chờ xác nhận', 'Chờ xác nhận'), ('Chờ lấy hàng', 'Chờ lấy hàng'), ('Đang vận chuyển', 'Đang vận chuyển'), ('Đã giao', 'Đã giao'), ('Đã hủy', 'Đã hủy')], default='Chờ xác nhận', max_length=50)),
                ('address_detail', models.CharField(max_length=255)),
                ('price', models.DecimalField(decimal_places=0, max_digits=10)),
                ('payment_method', models.CharField(choices=[('Chuyển khoản qua ngân hàng', 'Chuyển khoản qua ngân hàng'), ('Thanh toán khi nhận hàng', 'Thanh toán khi nhận hàng')], default='Thanh toán khi nhận hàng', max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Province',
            fields=[
                ('province_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Receipt',
            fields=[
                ('receipt_id', models.AutoField(primary_key=True, serialize=False)),
                ('date_receipt', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('supplier_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('address', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('phone_number', models.CharField(blank=True, default='', max_length=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TitleBlog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('product_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('price', models.FloatField(default=0)),
                ('image', models.ImageField(blank=True, default='product_images/default.jpg', null=True, upload_to='product_images/')),
                ('quantity', models.IntegerField(default=0)),
                ('detail', ckeditor.fields.RichTextField()),
                ('posting_date', models.DateTimeField(auto_now_add=True)),
                ('unit', models.CharField(choices=[('g', 'g'), ('kg', 'kg')], max_length=5)),
                ('short_descrip', models.CharField(blank=True, default=' ', max_length=100, null=True)),
                ('status', models.CharField(choices=[('Còn hàng', 'Còn hàng'), ('Hết hàng', 'Hết hàng')], default='Còn hàng', max_length=20)),
                ('ex_date', models.DateTimeField(blank=True, null=True)),
                ('display_product', models.BooleanField(blank=True, default=True, null=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='NongSan.category')),
                ('coupon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='NongSan.coupon')),
            ],
        ),
        migrations.CreateModel(
            name='OrderDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('coupon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='NongSan.coupon')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='NongSan.orders')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='NongSan.product')),
            ],
        ),
        migrations.CreateModel(
            name='Defective_Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('date_reported', models.DateTimeField(auto_now_add=True)),
                ('reason', models.TextField()),
                ('status', models.CharField(max_length=100)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='NongSan.product')),
            ],
        ),
        migrations.CreateModel(
            name='District',
            fields=[
                ('district_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('province', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='NongSan.province')),
            ],
        ),
        migrations.CreateModel(
            name='Receipt_Detail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expiry_date', models.DateTimeField(blank=True, null=True)),
                ('quantity', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=0, max_digits=10)),
                ('unit', models.CharField(max_length=50)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='NongSan.product')),
                ('receipt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='details', to='NongSan.receipt')),
            ],
        ),
        migrations.AddField(
            model_name='receipt',
            name='supplier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='NongSan.supplier'),
        ),
        migrations.CreateModel(
            name='Ward',
            fields=[
                ('ward_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('district', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='NongSan.district')),
            ],
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/')),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('default_address', models.CharField(blank=True, max_length=255, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('wishlist_id', models.AutoField(primary_key=True, serialize=False)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='NongSan.product')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='orders',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('feedback_id', models.AutoField(primary_key=True, serialize=False)),
                ('rating_star', models.IntegerField()),
                ('status', models.CharField(max_length=255)),
                ('img_feedback', models.ImageField(blank=True, null=True, upload_to='img_feedback/')),
                ('feedback_content', models.TextField()),
                ('posting_date', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='NongSan.product')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='NongSan.product')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('image_1', models.ImageField(blank=True, default='default.jpg', null=True, upload_to='blog_images/')),
                ('short_descrip', models.CharField(blank=True, max_length=500, null=True)),
                ('detail', ckeditor.fields.RichTextField()),
                ('link', models.URLField(blank=True, null=True)),
                ('title_blog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='NongSan.titleblog')),
                ('account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('address_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('ward', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='NongSan.ward')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
