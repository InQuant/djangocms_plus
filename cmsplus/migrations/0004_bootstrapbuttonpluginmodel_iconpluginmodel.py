# Generated by Django 3.0.6 on 2020-08-07 10:40

import cmsplus.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplus', '0003_svgimage_proxy_replaced_json_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='BootstrapButtonPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('cmsplus.plusplugin', cmsplus.models.LinkPluginMixin),
        ),
        migrations.CreateModel(
            name='IconPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('cmsplus.plusplugin', cmsplus.models.LinkPluginMixin),
        ),
    ]
