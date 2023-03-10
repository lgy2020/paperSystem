# Generated by Django 4.1.3 on 2022-11-20 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_admin_alter_userinfo_rank'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaperInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=96, verbose_name='题名')),
                ('author', models.CharField(max_length=32, verbose_name='作者')),
                ('source', models.CharField(max_length=32, verbose_name='来源')),
                ('create_time', models.DateField(verbose_name='发表时间')),
                ('filepath', models.CharField(max_length=128, verbose_name='文档')),
            ],
        ),
    ]
