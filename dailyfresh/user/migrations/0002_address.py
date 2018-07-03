# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(verbose_name='更新时间', auto_now=True)),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('receiver', models.CharField(verbose_name='收件人', max_length=20)),
                ('addr', models.CharField(verbose_name='收件地址', max_length=256)),
                ('zip_code', models.CharField(null=True, verbose_name='邮政编码', max_length=6)),
                ('phone', models.CharField(verbose_name='联系电话', max_length=11)),
                ('is_default', models.BooleanField(default=False, verbose_name='是否默认')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='所属账户')),
            ],
            options={
                'verbose_name_plural': '地址',
                'verbose_name': '地址',
                'db_table': 'df_address',
            },
        ),
    ]
