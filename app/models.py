from django.db import models

# Create your models here.
class UserInfo(models.Model):
    # user表
    name = models.CharField(verbose_name='姓名', max_length=16)
    password = models.CharField(verbose_name='密码', max_length=64)
    age = models.IntegerField(verbose_name='年龄')
    gender_choices = (
        (1,"男"),
        (2,"女"),
    )
    gender = models.SmallIntegerField(verbose_name="性别",choices=gender_choices)
    mobile = models.CharField(verbose_name="电话", max_length=11)
    rank_choices = (
        (0, "否"),
        (1, "是"),
    )
    rank = models.IntegerField(verbose_name='是否为会员',choices=rank_choices, default=0)

    def __str__(self):
        return self.name

class Admin(models.Model):
    username = models.CharField(verbose_name="用户名", max_length=32)
    password = models.CharField(verbose_name="密码", max_length=64)

    def __str__(self):
        return self.username

class Paper(models.Model):
    # paper表
    title = models.CharField(verbose_name='题名', max_length=96)
    author = models.CharField(verbose_name='作者', max_length=32)
    source = models.CharField(verbose_name='来源', max_length=32)
    create_time = models.DateField(verbose_name="发表时间")
    filepath = models.CharField(verbose_name="文档", max_length=128)
    uploader = models.ForeignKey(verbose_name="上传者", to="UserInfo", on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Store(models.Model):
    user = models.ForeignKey(verbose_name="姓名", to="UserInfo", on_delete=models.CASCADE)
    paper = models.ForeignKey(verbose_name="标题", to="Paper", on_delete=models.CASCADE)


