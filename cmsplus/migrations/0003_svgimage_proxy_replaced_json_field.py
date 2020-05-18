# Generated by Django 2.2.12 on 2020-05-07 10:03

import cmsplus.models
import cmsplus.utils
from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplus', '0002_bootstrapimagepluginmodel_osmmarkermodel_textlinkpluginmodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='SvgImagePluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplus.plusplugin', cmsplus.models.LinkPluginMixin),
        ),
        migrations.AlterField(
            model_name='plusplugin',
            name='_json',
            field=jsonfield.fields.JSONField(dump_kwargs={'cls': cmsplus.utils.JSONEncoder}),
        ),
    ]
