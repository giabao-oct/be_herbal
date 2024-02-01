from django.db import models
import random, string

avt = 'https://icon2.cleanpng.com/20180516/vgq/kisspng-computer-icons-google-account-icon-design-login-5afc02da4d77a2.5100382215264652423173.jpg'

class TaiKhoan(models.Model):
    iduser = models.AutoField(primary_key=True)
    avt = models.CharField(max_length=255,default=avt)
    tendn = models.CharField(max_length=50)
    hoten = models.CharField(max_length=100)
    gioitinh = models.CharField(max_length=10)
    sdt = models.CharField(max_length=11, unique=True)
    email = models.EmailField(unique=True)
    diachi = models.CharField(max_length=255)
    matkhau = models.CharField(max_length=255)
    quyen = models.CharField(max_length=20, default='user')
    class Meta:
        db_table = "taikhoan"
        
class SanPham(models.Model):
    idsp = models.AutoField(primary_key=True)
    anhsp = models.TextField()
    tensp = models.CharField(max_length=100)
    tenkhac = models.CharField(max_length=100, blank=True, null=True)
    tenkhoahoc = models.CharField(max_length=100, blank=True, null=True)
    congdung = models.CharField(max_length=255, blank=True, null=True)
    mota = models.TextField()
    baithuoc = models.TextField()
    giaban = models.BigIntegerField()
    SLton = models.IntegerField(default=0) 
    luottruycap = models.IntegerField(default=0)
    class Meta:
        db_table = "sanpham"
        
class PhieuNhap(models.Model):
    idpn = models.AutoField(primary_key=True)
    iduser = models.ForeignKey(TaiKhoan, on_delete=models.CASCADE)
    ngaynhap = models.DateTimeField(auto_now_add=True)
    tongtien = models.BigIntegerField()
    class Meta:
        db_table = "phieunhap"
    
class ChiTietPN(models.Model):
    idctpn = models.AutoField(primary_key=True)
    idpn = models.ForeignKey(PhieuNhap, on_delete=models.CASCADE)
    idsp = models.ForeignKey(SanPham, on_delete=models.CASCADE)
    soluongnhap = models.IntegerField()
    dongianhap = models.BigIntegerField()
    class Meta:
        db_table = "chitietpn"
        
class BenhCam(models.Model):
    idbenh = models.AutoField(primary_key=True)
    tenbenh = models.CharField(max_length=255)
    anhbenh = models.TextField()
    noidung = models.TextField()
    class Meta:
        db_table = "benhcam"
        
class TinTuc(models.Model):
    idtt = models.AutoField(primary_key=True)
    tieude = models.CharField(max_length=255)
    anhtt = models.TextField()
    mota = models.TextField()
    noidung = models.TextField()
    ngaydang = models.DateField(auto_now_add=True)
    luottruycap = models.IntegerField(default=0)
    class Meta:
        db_table = "tintuc"
        

class HoaDon(models.Model):
    idhd = models.AutoField(primary_key=True)
    iduser = models.ForeignKey(TaiKhoan, on_delete=models.CASCADE)
    ngaylap = models.DateTimeField(auto_now_add=True)
    tongtien = models.BigIntegerField(default=0)
    dadathang = models.BooleanField(default=False)
    class Meta:
        db_table = "hoadon"
        
class ChiTietHD(models.Model):
    idcthd = models.AutoField(primary_key=True)
    idhd = models.ForeignKey(HoaDon, on_delete=models.CASCADE)
    idsp = models.ForeignKey(SanPham, on_delete=models.CASCADE)
    soluong = models.IntegerField()
    class Meta:
        db_table = "chitiethd"
