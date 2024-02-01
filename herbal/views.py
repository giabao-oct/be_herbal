from django.shortcuts import render
from django.http import JsonResponse,HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.db.models import Q
from django.core.mail import send_mail
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.conf import settings
from itsdangerous import URLSafeTimedSerializer
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from pyotp import TOTP
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum

import cv2
import os
import numpy as np
from keras.models import load_model

from .models import *
from .serializers import *

# CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

def index(request):
    return HttpResponse('This is a custom index page.')
# Create your views here.

# region TaiKhoan
@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        EmailOrPhone = request.data.get('EmailOrPhone', '')
        matkhau = request.data.get('matkhau', '')

        try:
            user = TaiKhoan.objects.get(Q(sdt=EmailOrPhone) | Q(email=EmailOrPhone), matkhau=matkhau)
        except TaiKhoan.DoesNotExist:
            return Response({'message': 'Invalid login credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = TaiKhoanSerializer(user)

        response_data = {
            'iduser': serializer.data['iduser'],
            'avt': serializer.data['avt'],
            'tendn': serializer.data['tendn'],
            'quyen': serializer.data['quyen'],
        }

        return Response(response_data)
    else:
        return Response({'message': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def register(request):
    data = request.data

    if TaiKhoan.objects.filter(sdt=data['sdt']).exists():
        return Response({'Số điện thoại đã tồn tại'}, status=status.HTTP_400_BAD_REQUEST)

    if TaiKhoan.objects.filter(email=data['email']).exists():
        return Response({'Email đã tồn tại'}, status=status.HTTP_400_BAD_REQUEST)

    Account_data = {
        'tendn': data['tendn'],
        'hoten': data['hoten'],
        'gioitinh': data['gioitinh'],
        'sdt': data['sdt'],
        'email': data['email'],
        'diachi': data['diachi'],
        'matkhau': data['matkhau'],
    }

    serializer = TaiKhoanSerializer(data=Account_data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response('Đăng ký thành công!', status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def check_email_view(request):
    email = request.data.get('email')
    try:
        user = TaiKhoan.objects.get(email=email)
        
        serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
        token = serializer.dumps(user.iduser, salt='reset-password')
        cache_key = f'password_reset_token_{user.iduser}'
        cache.set(cache_key, token,900)

        subject = 'ĐẶT LẠI MẬT KHẨU'
        message = f'Xin chào {user.hoten}.\nVui lòng nhấn vào đường dẫn sau để đặt lại mật khẩu: {settings.BASE_URL}/reset-password?token={token}/'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        send_mail(subject, message, from_email, recipient_list)

        return Response({'message': 'Email đặt lại mật khẩu đã được gửi thành công.'}, status=status.HTTP_200_OK)
    except TaiKhoan.DoesNotExist:
        return Response({'message': 'Email không tồn tại.'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
def reset_password(request):
    token = request.data.get('token')
    new_password = request.data.get('new_password')
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        user_id = serializer.loads(token, salt='reset-password', max_age=900)
    except:
        return Response({'message': 'Mã token không hợp lệ hoặc đã hết hạn.'}, status=status.HTTP_401_UNAUTHORIZED)
   
    cache_key = f'password_reset_token_{user_id}'
    if cache.get(cache_key) is None:
        return Response({'message': 'Mã token đã được sử dụng.'}, status=status.HTTP_401_UNAUTHORIZED)
    user = get_object_or_404(TaiKhoan, iduser=user_id)
    user.matkhau = new_password
    user.save()
    cache.delete(cache_key)

    return Response({'message': 'Đặt lại mật khẩu thành công.'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def get_Account(request):
    accounts = TaiKhoan.objects.all()
    serializer = TaiKhoanSerializer(accounts, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def get_AccountDetail(request):
    iduser = request.data.get('iduser')
    acc = TaiKhoan.objects.get(iduser=iduser)
    serializer = TaiKhoanSerializer(acc)
    return Response(serializer.data)

@api_view(['PUT'])
def update_Account(request, iduser):
    account = TaiKhoan.objects.get(iduser=iduser)
    data = request.data 
    acc_data = {
        'avt': data.get('avt', account.avt),
        'tendn': data.get('tendn', account.tendn),
        'hoten': data.get('hoten', account.hoten),
        'gioitinh': data.get('gioitinh', account.gioitinh),
        'sdt': data.get('sdt', account.sdt),
        'email': data.get('email', account.email),
        'diachi': data.get('diachi', account.diachi),
        'matkhau': data.get('matkhau', account.matkhau),
        'quyen': data.get('quyen', account.quyen)
    }
    serializer = TaiKhoanSerializer(account, data=acc_data)
    if serializer.is_valid():
        serializer.save()
        return Response("Cập nhật thành công!", status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_Account(request, iduser):
    account = TaiKhoan.objects.get(iduser=iduser)
    account.delete()
    return Response({'message': 'Tài khoản đã được xoá thành công'}, status=status.HTTP_204_NO_CONTENT)
#endregion

#region SanPham
@api_view(['GET'])
def get_Product(request):
    products = SanPham.objects.all()
    serializer = SanPhamSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def increase_View_Count(request, id):
    product = get_object_or_404(SanPham, idsp=id)
    product.luottruycap += 1
    product.save()
    return Response({'luottruycap': product.luottruycap})

@api_view(['GET'])
def top_Viewed_Products(request):
    top_products = SanPham.objects.order_by('-luottruycap')[:4]
    serializer = SanPhamSerializer(top_products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def top_BestSelling(request):
    top_products = SanPham.objects.filter(chitiethd__idhd__dadathang=True).annotate(tong_so_luong=Sum('chitiethd__soluong')).order_by('-tong_so_luong')[:4]
    result = []
    for product in top_products:
        result.append({
            'idsp': product.idsp,
            'anhsp': product.anhsp,
            'tensp': product.tensp,
            'tenkhoahoc':product.tenkhoahoc,
            'giaban': product.giaban,
            'tong_so_luong': product.tong_so_luong,
        })
    return Response(result)

@api_view(['GET'])
def get_ProductDetail(request, idsp):
    product = SanPham.objects.get(idsp=idsp)
    serializer = SanPhamSerializer(product)
    return Response(serializer.data)

@api_view(['GET'])
def product_Checkout(request, idsp):
    product = SanPham.objects.filter(idsp=idsp)
    serializer = SanPhamSerializer(product, many = True)
    return Response(serializer.data)

@api_view(['POST'])
def add_Product(request):
    if request.method == 'POST':
        data = request.data
        product_data = {
            'anhsp': data['anhsp'],
            'tensp': data['tensp'],
            'tenkhac': data['tenkhac'],
            'tenkhoahoc': data['tenkhoahoc'],
            'congdung': data['congdung'],
            'mota': data['mota'],
            'baithuoc': data['baithuoc'],
            'giaban': data['giaban'],
            # 'SLton': data['SLton'],
        }

        serializer = SanPhamSerializer(data=product_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response('Thêm sản phẩm thành công!', status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      
@api_view(['PUT'])
def update_Product(request, idsp):
    product = SanPham.objects.get(idsp=idsp)
    data = request.data 
    product_data = {
         'anhsp': data['anhsp'],
            'tensp': data['tensp'],
            'tenkhac': data['tenkhac'],
            'tenkhoahoc': data['tenkhoahoc'],
            'congdung': data['congdung'],
            'mota': data['mota'],
            'baithuoc': data['baithuoc'],
            'giaban': data['giaban'],
            'SLton': data['SLton'],
    }

    serializer = SanPhamSerializer(instance=product, data=product_data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response('Cập nhật sản phẩm thành công!', status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['DELETE'])
def delete_Product(request, idsp):
    product = SanPham.objects.get(idsp=idsp)
    product.delete()
    return Response({'message': 'Sản phẩm đã được xoá thành công'}, status=status.HTTP_204_NO_CONTENT)

#endregion

#region PhieuNhap
@api_view(['GET'])
def get_Receipt(request):
    receipt = PhieuNhap.objects.all()
    serializer = PhieuNhapSerializer(receipt, many=True)
    data = []
    for receipt_data in serializer.data:
        account = receipt_data['iduser']
        account_info = TaiKhoan.objects.get(iduser=account)
        phieunhap_info = {
            'idpn':receipt_data['idpn'],
            'hoten': account_info.hoten,
            'ngaynhap': receipt_data['ngaynhap'],
            'tongtien': receipt_data['tongtien'],
        }
        data.append(phieunhap_info)
    return Response(data)

@api_view(['POST'])
def create_phieu_nhap(request):
    iduser = request.data.get('iduser')
    receipt_detail = request.data.get('chi_tiet_phieu_nhap')
    user = TaiKhoan.objects.get(iduser=iduser)
    receipt_Serializer = PhieuNhapSerializer(data={'iduser': user.iduser, 'tongtien': 0})
    receipt_Serializer.is_valid(raise_exception=True)
    receipt = receipt_Serializer.save()
    total_amount = 0
    for item in receipt_detail:
        idsp = item.get('idsp')
        soluongnhap = item.get('soluongnhap')
        dongianhap = item.get('dongianhap')

        product = SanPham.objects.get(idsp=idsp)
        product.SLton += float(soluongnhap)
        product.save()
        total_amount_item = float(dongianhap) * float(soluongnhap)
        total_amount += total_amount_item
        
        chi_tiet_pn_data = {
            'idpn': receipt.idpn,
            'idsp': product.idsp,
            'soluongnhap': soluongnhap,
            'dongianhap': dongianhap,
        }
        chi_tiet_pn_serializer = ChiTietPNSerializer(data=chi_tiet_pn_data)
        chi_tiet_pn_serializer.is_valid(raise_exception=True)
        chi_tiet_pn_serializer.save()
    receipt.tongtien = total_amount
    receipt.save()

    return Response({'message': 'Phiếu nhập đã được tạo thành công.'}, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
def delete_Receipt(request, idpn):
    try:
        # Sử dụng transaction để đảm bảo tính nhất quán dữ liệu
        with transaction.atomic():
            receipt = PhieuNhap.objects.get(idpn=idpn)
            receipt_detail_list = ChiTietPN.objects.filter(idpn=receipt)

            for receipt_detail in receipt_detail_list:
                product = receipt_detail.idsp
                product.SLton -= receipt_detail.soluongnhap
                product.save()
                receipt_detail.delete()

            receipt.delete()

            return Response({'message': 'Xóa phiếu nhập thành công'}, status=status.HTTP_204_NO_CONTENT)

    except PhieuNhap.DoesNotExist:
        return Response({'message': 'Phiếu nhập không tồn tại'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def get_receipt_details(request, idpn):
        receipt_details_list = ChiTietPN.objects.filter(idpn=idpn)
        serializer = ChiTietPNSerializer(receipt_details_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
#endregion

#region Benh
@api_view(['GET'])
def get_Disease(request):
    disease = BenhCam.objects.all()
    serializer = BenhCamSerializer(disease, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_DiseaseDetail(request, idbenh):
    disease = BenhCam.objects.get(idbenh=idbenh)
    serializer = BenhCamSerializer(disease)
    return Response(serializer.data)

@api_view(['POST'])
def add_Disease(request):
    if request.method == 'POST':
        data = request.data
        disease_data = {
            'tenbenh': data['tenbenh'],
            'anhbenh': data['anhbenh'],
            'noidung': data['noidung'],
        }

        serializer = BenhCamSerializer(data=disease_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response('Thêm bệnh cảm thành công!', status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      
@api_view(['PUT'])
def update_Disease(request, idbenh):
    disease = BenhCam.objects.get(idbenh=idbenh)
    data = request.data 
    disease_data = {
            'tenbenh': data['tenbenh'],
            'anhbenh': data['anhbenh'],
            'noidung': data['noidung'],
    }

    serializer = BenhCamSerializer(instance=disease, data=disease_data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response('Cập nhật bệnh cảm thành công!', status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['DELETE'])
def delete_Disease(request, idbenh):
    disease = BenhCam.objects.get(idbenh=idbenh)
    disease.delete()
    return Response({'message': 'Bệnh cảm đã được xoá thành công'}, status=status.HTTP_204_NO_CONTENT)
#endregion

#region TinTuc
@api_view(['GET'])
def get_News(request):
    news = TinTuc.objects.order_by('-ngaydang')
    serializer = TinTucSerializer(news, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def increase_View_News(request, id):
    news = get_object_or_404(TinTuc, idtt=id)
    news.luottruycap += 1
    news.save()
    return Response({'luottruycap': news.luottruycap})

@api_view(['GET'])
def top_Viewed_News(request):
    top_news = TinTuc.objects.order_by('-luottruycap')
    serializer = TinTucSerializer(top_news, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_NewsDetail(request, idtt):
    news = TinTuc.objects.get(idtt=idtt)
    serializer = TinTucSerializer(news)
    return Response(serializer.data)

@api_view(['POST'])
def add_News(request):
    if request.method == 'POST':
        data = request.data
        news_data = {
            'tieude': data['tieude'],
            'anhtt': data['anhtt'],
            'mota': data['mota'],
            'noidung': data['noidung'],
        }

        serializer = TinTucSerializer(data=news_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response('Thêm tin tức thành công!', status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      
@api_view(['PUT'])
def update_News(request, idtt):
    news = TinTuc.objects.get(idtt=idtt)
    data = request.data 
    news_data = {
            'tieude': data['tieude'],
            'anhtt': data['anhtt'],
            'mota': data['mota'],
            'noidung': data['noidung'], 
    }

    serializer = TinTucSerializer(instance=news, data=news_data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response('Cập nhật tin tức thành công!', status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['DELETE'])
def delete_News(request, idtt):
    news = TinTuc.objects.get(idtt=idtt)
    news.delete()
    return Response({'message': 'Tin tức đã được xoá thành công'}, status=status.HTTP_204_NO_CONTENT)
#endregion

#region GioHang
@api_view(['POST'])
def addToCart(request):
    if request.method == 'POST':
        iduser = request.data.get('iduser')
        idsp = request.data.get('idsp')
        soluong =  request.data.get('soluong')

        user = TaiKhoan.objects.get(iduser=iduser)
        product = SanPham.objects.get(idsp=idsp)

        cart = HoaDon.objects.filter(iduser=user, dadathang=False).first()

        if cart is None:
            cart = HoaDon.objects.create(iduser=user)
        
        if ChiTietHD.objects.filter(idhd=cart, idsp=product).exists():
            cart_item = ChiTietHD.objects.get(idhd=cart, idsp=product)
            cart_item.soluong += int(soluong)
            cart_item.save()
        else:
            cart_item = ChiTietHD.objects.create(idhd=cart, idsp=product, soluong=int(soluong))

        cart.tongtien = sum(item.idsp.giaban * item.soluong for item in cart.chitiethd_set.all())
        cart.save()

        return Response({'message': 'Sản phẩm đã được thêm vào giỏ hàng thành công!'}, status=status.HTTP_201_CREATED)

    return Response({'message': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def getCartInfo(request, iduser):
    try:
        cart = HoaDon.objects.get(iduser=iduser, dadathang=False)
    except HoaDon.DoesNotExist:
        return Response({'cart_info': [], 'tongtien': 0}, status=200)
    
    cart_items = ChiTietHD.objects.filter(idhd=cart)
    cart_info = [
        {
            'idsp' : item.idsp.idsp,
            'anhsp': item.idsp.anhsp,
            'tensp': item.idsp.tensp,
            'giaban': item.idsp.giaban,
            'SLton': item.idsp.SLton,
            'soluong': item.soluong,
        }
        for item in cart_items
    ]
    tongtien = sum(item.idsp.giaban * item.soluong for item in cart_items)
    response_data = {
        'cart_info': cart_info,
        'tongtien': tongtien,
    }
    return Response(response_data, status=200)

@api_view(['GET'])
def count_product(request, iduser):
    count = ChiTietHD.objects.filter(idhd__iduser=iduser, idhd__dadathang=False).count()
    return Response({'count': count}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_product_Cart(request, iduser, idsp):
        cthd = ChiTietHD.objects.get(idhd__iduser=iduser, idsp=idsp, idhd__dadathang=False)
        hd = cthd.idhd
        cthd.delete()
        check_invoice = ChiTietHD.objects.filter(idhd=hd)
        if not check_invoice.exists():
            hd.delete()
            return Response({'message': 'Xóa sản phẩm và hoá đơn thành công'}, status=status.HTTP_200_OK)
        hd.tongtien = calculate_total(hd)
        hd.save()
        return Response({'message': 'Xóa sản phẩm thành công'}, status=status.HTTP_200_OK)

def calculate_total(idhd):
    cthds = ChiTietHD.objects.filter(idhd=idhd)
    total = 0
    for cthd in cthds:
        total += cthd.idsp.giaban * cthd.soluong
    return total


@api_view(['POST'])
def update_Quantity(request):
    iduser = request.data.get('iduser')
    idsp = request.data.get('idsp')
    quantity = request.data.get('quantity')
    
    user = TaiKhoan.objects.get(iduser=iduser)
    product = SanPham.objects.get(idsp=idsp)
    cart = HoaDon.objects.get(iduser=user, dadathang=False)
    cart_item = ChiTietHD.objects.get(idhd__iduser=user, idsp=product, idhd__dadathang=False)

    cart_item.soluong = quantity
    cart_item.save()

    cart_items = ChiTietHD.objects.filter(idhd=cart.idhd)
    cart.tongtien = sum(item.idsp.giaban * item.soluong for item in cart_items)
    cart.save()

    return Response({'message': 'Cập nhật thành công'}, status=status.HTTP_200_OK)
#endregion

#region HoaDon_CTHD
@api_view(['GET'])
def get_Invoice(request):
    invoice = HoaDon.objects.all().order_by('-ngaylap')
    serializer = HoaDonSerializer(invoice, many=True)
    return Response(serializer.data, status=200)

@api_view(['GET'])
def order_Detail(request, idhd):
    invoice = HoaDon.objects.select_related('iduser').get(idhd=idhd)
    invoice_detail = ChiTietHD.objects.filter(idhd=invoice).select_related('idsp')
    product = []
    for cthd in invoice_detail:
        product.append({
            'tensp': cthd.idsp.tensp,
            'giaban':cthd.idsp.giaban,
            'soluong': cthd.soluong,
        })
    response_data = {
        'idhd': invoice.idhd,
        'ngaylap': invoice.ngaylap,
        'dadathang': invoice.dadathang,
        'hoten': invoice.iduser.hoten,
        'sdt': invoice.iduser.sdt,
        'diachi':invoice.iduser.diachi,
        'chitietsanpham': product,
        'tongtien': invoice.tongtien,
    }
    return Response(response_data, status=200)

@api_view(['GET'])
def get_ListOrder(request, iduser):
    invoices = HoaDon.objects.filter(iduser=iduser, dadathang=True).order_by('-ngaylap')
    response_data = []

    for invoice in invoices:
        invoice_detail = ChiTietHD.objects.filter(idhd=invoice).select_related('idsp')
        product = []

        for cthd in invoice_detail:
            product.append({
                'anhsp': cthd.idsp.anhsp,
                'tensp': cthd.idsp.tensp,
                'giaban': cthd.idsp.giaban,
                'soluong': cthd.soluong,
            })

        invoice_data = {
            'ngaylap': invoice.ngaylap,
            'tongtien': invoice.tongtien,
            'chitietsanpham': product
        }

        response_data.append(invoice_data)

    return Response(response_data, status=status.HTTP_200_OK)

#endregion

#region TimKiem
@api_view(['GET'])
def search_product(request):
    query_param = request.GET.get('q', '')
    # search_terms = query_param.split()
    # query = Q()
    # for term in search_terms:
    #     query |= Q(tensp__icontains=term)
    results = SanPham.objects.filter(Q(tensp__icontains=query_param)| Q(congdung__icontains=query_param))
    serializer = SanPhamSerializer(results, many=True)
    return Response(serializer.data)

# @api_view(['GET'])
# def product_suggestions(request):
#     query = request.GET.get('tensp', '')
#     if query:
#         query_no_diacritics = unidecode(query)

#         product_list = SanPham.objects.filter(
#             Q(tensp__icontains=query) | Q(tensp__icontains=query_no_diacritics)
#         )
#         serializer = SanPhamSerializer(product_list, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     else:
#         return Response([], status=status.HTTP_400_BAD_REQUEST)
#endregion

#region OTP
@api_view(['POST'])
def generate_OTP(request):
    iduser = request.data.get('iduser', None)
    user = TaiKhoan.objects.get(iduser=iduser)
    #tạo otp với 6 số
    otp = get_random_string(length=6, allowed_chars='0123456789')
    cache_key = f'otp_{iduser}'
    cache.set(cache_key,otp, timeout=60)  
    
    subject = 'XÁC NHẬN ĐẶT HÀNG'
    message = f'Xin chào {user.hoten}.\nMã OTP xác nhận đơn hàng của bạn là: {otp}.\nVui lòng không chia sẻ OTP cho bất kỳ ai.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)
    return Response({'message': 'Gửi OTP thành công!'},status=status.HTTP_200_OK)

@api_view(['POST'])
def verify_OTP(request):
    iduser = request.data.get('iduser', None)
    otp = request.data.get('otp', None)
    cache_key = f'otp_{iduser}'
    cached_otp = cache.get(cache_key)
    if otp == cached_otp:
        with transaction.atomic():
            invoice = get_object_or_404(HoaDon, iduser=iduser, dadathang=False)
            invoice_details = ChiTietHD.objects.filter(idhd=invoice) 
            for invoice_detail in invoice_details:
                product = invoice_detail.idsp
                product_quantity = product.SLton
                order_quantity = invoice_detail.soluong
                
                if product_quantity >= order_quantity:
                    invoice.ngaylap = timezone.now()
                    invoice.dadathang = True
                    invoice.save()
                    product.SLton -= order_quantity
                    product.save()
                # else:
                    # Xử lý trường hợp không đủ số lượng trong kho
        cache.delete(cache_key)
        return Response('Đặt hàng thành công!', status=status.HTTP_200_OK)
    else:

        return Response('Mã OTP không chính xác', status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
def verify_OTP_Product(request):
    if request.method == 'POST':
        iduser = request.data.get('iduser')
        idsp = request.data.get('idsp')
        quantity = request.data.get('soluong')
        otp = request.data.get('otp', None)

        user = get_object_or_404(TaiKhoan, iduser=iduser)
        product = get_object_or_404(SanPham, idsp=idsp)
        cache_key = f'otp_{iduser}'
        cached_otp = cache.get(cache_key)
        if otp == cached_otp:
            if int(quantity) > product.SLton:
                return Response("Số lượng tồn không đủ", status=status.HTTP_400_BAD_REQUEST)
            invoice = HoaDon.objects.create(iduser=user)
            invoice_details = ChiTietHD.objects.create(idhd=invoice, idsp=product, soluong=int(quantity))
            invoice.dadathang = True
            invoice.tongtien = product.giaban * invoice_details.soluong
            invoice.save()
            product.SLton -= int(quantity)
            product.save()
            cache.delete(cache_key)
            return Response('Đặt hàng thành công!', status=status.HTTP_200_OK)
        else:
            return Response('Mã OTP không chính xác', status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


#endregion

#region model
# model_path = "D:/KHOALUAN/Phan_Loai_La_Cay_Thuoc/model/best_model.h5"
model_path = os.path.join("./herbal/model/", "best_model_V3.h5")
class_names =['Bạc hà', 'Bạch đàn', 'Bàng', 'Bưởi','Đại bi', 'Dâu tằm', 'Húng chanh', 'Kinh giới','Rau má', 'Tía tô', 'Tràm', 'Tre']
model = load_model(model_path)
@api_view(['POST'])
def ImageRecognitionAPI(request):
    if 'image' in request.FILES:
        image = request.FILES['image']
        image_np = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_COLOR)

        img = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (224, 224))
        img = np.array(img, dtype=np.float32) / 255.0
        img = np.expand_dims(img, 0)

        predictions = model.predict(img)
        predicted_class_index = np.argmax(predictions)
        predicted_class = class_names[predicted_class_index]
        accuracy = predictions[0][predicted_class_index] * 100
       
        if accuracy >= 50:
            result = f"{predicted_class}"
        else:
            result = "Không thể nhận diện"
        return JsonResponse({'result': result})
    else:
        return JsonResponse({'result': 'Error: No image provided.'}, status=status.HTTP_400_BAD_REQUEST)
    
    
#endregion