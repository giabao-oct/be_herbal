from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('check-mail/', views.check_email_view, name='check_mail'),
    path('reset-password/', views.reset_password, name='reset-password'),
    path('account/', views.get_Account, name='account'),
    path('account-detail/', views.get_AccountDetail, name='account-detail'),
    path('update-account/<int:iduser>/', views.update_Account, name='update-account'),
    path('delete-account/<int:iduser>/', views.delete_Account, name='delete-account'),
    
    path('product/', views.get_Product, name='product'),
    path('increase-view-count/<int:id>/', views.increase_View_Count, name='increase-view-count'),
    path('top-viewed-products/', views.top_Viewed_Products, name='top-viewed-products'),
    path('top-best-selling/', views.top_BestSelling, name='top-best-selling'),
    path('product-detail/<int:idsp>/', views.get_ProductDetail, name='product-detail'),
    path('product-checkout/<int:idsp>/', views.product_Checkout, name='product-checkout'),
    path('add-product/', views.add_Product, name='add-product'),
    path('update-product/<int:idsp>/', views.update_Product, name='update-product'),
    path('delete-product/<int:idsp>/', views.delete_Product, name='delete-product'),
    
    path('receipt/', views.get_Receipt, name='receipt'),
    path('create-receipt/', views.create_phieu_nhap, name='create-receipt'),
    path('delete-receipt/<int:idpn>/', views.delete_Receipt, name='delete_receipt'),
    path('get-receipt-details/<int:idpn>/', views.get_receipt_details, name='get-receipt-details'),
    
    path('disease/', views.get_Disease, name='disease'),
    path('disease-detail/<int:idbenh>/', views.get_DiseaseDetail, name='disease-detail'),
    path('add-disease/', views.add_Disease, name='add-product'),
    path('update-disease/<int:idbenh>/', views.update_Disease, name='update-disease'),
    path('delete-disease/<int:idbenh>/', views.delete_Disease, name='delete-disease'),
    
    path('news/', views.get_News, name='news'),
    path('increase-view-news/<int:id>/', views.increase_View_News, name='increase-view-news'),
    path('top-viewed-news/', views.top_Viewed_News, name='top-viewed-news'),
    path('news-detail/<int:idtt>/', views.get_NewsDetail, name='news-detail'),
    path('add-news/', views.add_News, name='add-news'),
    path('update-news/<int:idtt>/', views.update_News, name='update-news'),
    path('delete-news/<int:idtt>/', views.delete_News, name='delete-news'),
    
    path('add-to-cart/', views.addToCart, name='add-to-cart'),
    path('get-cart-info/<int:iduser>/', views.getCartInfo, name='get-cart-info'),
    path('count-product/<int:iduser>/', views.count_product, name='count-product'),
    path('delete-product-cart/<int:iduser>/<int:idsp>/', views.delete_product_Cart, name='delete-product-cart'),
    path('update-quantity/', views.update_Quantity, name='update-quantity'),
    
    path('invoice/', views.get_Invoice, name='invoice'),
    path('order-detail/<int:idhd>/', views.order_Detail, name='order-detail'),
    path('get-list-order/<int:iduser>/', views.get_ListOrder, name='get-list-order'),
    
    path('generate-otp/', views.generate_OTP, name='generate-otp'),
    path('verify-otp/', views.verify_OTP, name='verify-otp'),
    path('verify-otp-product/', views.verify_OTP_Product, name='verify-otp-product'),
    
    path('search_product/', views.search_product, name='search_product'),
    # path('product-suggestions/', views.product_suggestions, name='product-suggestions'),
    
    path('image-recognition/', views.ImageRecognitionAPI, name='image-recognition'),
]