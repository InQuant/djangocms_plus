# Generated by Django 2.2.15 on 2020-09-08 08:19

import cmsplus.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplus', '0004_bootstrapbuttonpluginmodel_iconpluginmodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='SlidePluginModel',
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