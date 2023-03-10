# Generated by Django 4.1.3 on 2022-11-20 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=32, verbose_name='用户名')),
                ('password', models.CharField(max_length=64, verbose_name='密码')),
            ],
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='rank',
            field=models.IntegerField(choices=[(0, '否'), (1, '是')], default=0, verbose_name='是否为会员'),
        ),
    ]
