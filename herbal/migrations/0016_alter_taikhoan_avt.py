# Generated by Django 4.2.5 on 2023-12-05 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herbal', '0015_rename_dathanhtoan_hoadon_dadathang'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taikhoan',
            name='avt',
            field=models.CharField(default='https://icon2.cleanpng.com/20180516/vgq/kisspng-computer-icons-google-account-icon-design-login-5afc02da4d77a2.5100382215264652423173.jpg', max_length=255),
        ),
    ]
