# Generated by Django 3.0.5 on 2020-04-24 09:24

import cmsplus.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplus', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BootstrapImagePluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplus.plusplugin', cmsplus.models.LinkPluginMixin),
        ),
        migrations.CreateModel(
            name='OsmMarkerModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplus.plusplugin',),
        ),
        migrations.CreateModel(
            name='TextLinkPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplus.plusplugin', cmsplus.models.LinkPluginMixin),
        ),
    ]
