# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goodssku',
            name='desc',
            field=models.CharField(verbose_name='商品简介', max_length=256, default='商品简介...'),
        ),
        migrations.AlterField(
            model_name='goodssku',
            name='price',
            field=models.DecimalField(verbose_name='商品价格', max_digits=10, decimal_places=2, default=20),
        ),
        migrations.AlterField(
            model_name='goodssku',
            name='unite',
            field=models.CharField(verbose_name='商品单位', max_length=20, default='kg'),
        ),
        migrations.AlterField(
            model_name='indexpromotionbanner',
            name='url',
            field=models.CharField(verbose_name='活动链接', max_length=256),
        ),
    ]
