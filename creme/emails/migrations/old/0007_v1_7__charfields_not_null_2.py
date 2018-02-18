# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('emails', '0006_v1_7__charfields_not_null_1'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailrecipient',
            name='address',
            field=models.CharField(default='', max_length=100, verbose_name='Email address'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='entityemail',
            name='subject',
            field=models.CharField(default='', max_length=100, verbose_name='Subject', blank=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='lightweightemail',
            name='subject',
            field=models.CharField(default='', max_length=100, verbose_name='Subject', blank=True),
            preserve_default=False,
        ),
    ]