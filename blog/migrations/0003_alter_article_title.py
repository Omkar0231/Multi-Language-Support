# Generated by Django 4.1.5 on 2023-01-29 11:30

import MultiLang.custom_models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_alter_article_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='title',
            field=MultiLang.custom_models.MultiLanguageJSONField(),
        ),
    ]
