from rest_framework import serializers
from .models import *


class TaiKhoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaiKhoan
        fields = '__all__'
        
class SanPhamSerializer(serializers.ModelSerializer):
    class Meta:
        model = SanPham
        fields = '__all__'
        
class PhieuNhapSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhieuNhap
        fields = '__all__'

class ChiTietPNSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChiTietPN
        fields = '__all__'

class BenhCamSerializer(serializers.ModelSerializer):
    class Meta:
        model = BenhCam
        fields = '__all__'

class TinTucSerializer(serializers.ModelSerializer):
    class Meta:
        model = TinTuc
        fields = '__all__'
        
class HoaDonSerializer(serializers.ModelSerializer):
    class Meta:
        model = HoaDon
        fields = '__all__'

class ChiTietHDSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChiTietHD
        fields = '__all__'
        