# Generated by Django 4.2.5 on 2023-11-20 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herbal', '0002_alter_sanpham_anhsp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sanpham',
            name='anhsp',
            field=models.TextField(),
        ),
    ]
