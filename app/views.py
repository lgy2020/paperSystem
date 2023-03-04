import os
from django.shortcuts import render
import json
from django.http import JsonResponse
from django.shortcuts import render,HttpResponse,redirect
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django import forms
from django.utils.safestring import mark_safe
from django.http.request import QueryDict
import random
from datetime import datetime
import copy
from io import BytesIO
from app import models
from app.utils.pagination import Pagination
from app.utils.codepicture import check_code
class LoginForm(forms.Form):

    username = forms.CharField(
        label="用户名",
        widget=forms.TextInput,
        required=True,
    )
    password = forms.CharField(
        label="密码",
        widget=forms.PasswordInput(render_value=True),
        required=True,
    )

    code = forms.CharField(
        label="验证码",
        widget=forms.TextInput,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs = {"class": "form-control", "placeholder": field.label}

def login(request):
    if request.method == "GET":
        form = LoginForm()
        return render(request, 'login.html',{'form':form})

    form = LoginForm(data=request.POST)
    if form.is_valid():
        user_input_code = form.cleaned_data.pop('code')
        print(user_input_code)
        code = request.session.get('image_code',"")
        if code.upper() != user_input_code.upper():
            form.add_error("code","验证码错误")
            return render(request, 'login.html',{'form': form})
        admin_object = models.Admin.objects.filter(**form.cleaned_data).first()
        # print("admin:")
        # print(admin_object)
        if admin_object:
            request.session["info"] = {'id': admin_object.id, 'name': admin_object.username}
            request.session.set_expiry(60 * 60 * 24)
            return redirect("/admin/paper/list/")

        user_name = form.cleaned_data.get('username')
        user_password = form.cleaned_data.get('password')
        VIP_object = models.UserInfo.objects.filter(name=user_name, password=user_password, rank=1).first()
        user_object = models.UserInfo.objects.filter(name=user_name, password=user_password).first()

        if VIP_object:
            request.session["info"] = {'id': VIP_object.id, 'name': VIP_object.name}
            request.session.set_expiry(60 * 60 * 24)
            return redirect("/vip/paper/list/")

        if user_object:
            request.session["info"] = {'id': user_object.id, 'name': user_object.name}
            request.session.set_expiry(60 * 60 * 24)
            return redirect("/user/paper/list/")


    form.add_error("password", "用户名或密码错误")
    return(request,'login.html',{'form':form})

def logout(request):
    request.session.clear()

    return redirect('/login/')

def image_code(request):
    img, code_string = check_code()
    print(code_string)
    request.session['image_code'] = code_string
    request.session.set_expiry(60)

    stream = BytesIO()
    img.save(stream,'png')
    return HttpResponse(stream.getvalue())

def user_list(request):

    # 获取数据
    queryset = models.UserInfo.objects.all()

    page_object = Pagination(request, queryset, page_size=10)

    context = {
        "queryset": page_object.page_queryset,  # 分完页的数据
        "page_string": page_object.html()       # 生成页码
    }

    return render(request,'user_list.html', context)

class UserModelForm(forms.ModelForm):
    class Meta:
        model = models.UserInfo
        fields = ["name", "password", "age", "gender", "mobile", "rank"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs = {"class": "form-control", "placeholder": field.label}

def user_add(request):
    title = "新建用户"
    if request.method == "GET":
        form = UserModelForm()
        return render(request, 'change.html', {"form": form, "title": title})

    form = UserModelForm(data=request.POST)
    # print(form)
    if form.is_valid():
        form.save()
        return redirect('/user/list/')

    return render(request, 'change.html', {"form": form, "title": title})

def user_delete(request, nid):
    models.UserInfo.objects.filter(id=nid).delete()
    return redirect("/user/list/")

def user_edit(request, nid):
    row_object = models.UserInfo.objects.filter(id=nid).first()
    if request.method == "GET":

        form = UserModelForm(instance=row_object)
        return render(request,'user_edit.html', {"form":form})

    form = UserModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect("/user/list/")
    return render(request, 'user_edit.html', {"form": form})

def admin_list(request):
    # 构造搜索
    data_dict = {}
    search_data = request.GET.get('q', "")
    if search_data:
        data_dict["username__contains"] = search_data

    queryset = models.Admin.objects.filter(**data_dict)
    page_object = Pagination(request, queryset)

    context = {
        "search_data": search_data,
        "queryset": page_object.page_queryset,
        "page_string": page_object.html()
    }

    return render(request,'admin_list.html',context)

class AdminModelForm(forms.ModelForm):
    confirm_password = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput(render_value=True),
    )
    class Meta:
        model = models.Admin
        fields = ["username", "password","confirm_password"]
        widgets = {
            "password": forms.PasswordInput(render_value=True),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs = {"class": "form-control", "placeholder": field.label}


    def clean_confirm_password(self):
        pwd = self.cleaned_data.get("password")
        confirm = self.cleaned_data.get("confirm_password")
        if confirm != pwd:
            raise ValidationError("密码不一致")
        return confirm

def admin_add(request):
    title = "新建管理员"
    if request.method == "GET":
        form = AdminModelForm()
        return render(request,'change.html', {"form":form, "title":title})

    form = AdminModelForm(data=request.POST)
    # print(form)
    if form.is_valid():
        form.save()
        return redirect('/admin/list/')

    return render(request, 'change.html',{"form":form, "title":title})

def admin_delete(request, nid):
    models.Admin.objects.filter(id=nid).delete()
    return redirect("/admin/list/")

class AdminEditModelForm(forms.ModelForm):

    class Meta:
        model = models.Admin
        fields = ["username"]
        # fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs = {"class": "form-control", "placeholder": field.label}

def admin_edit(request, nid):
    row_object = models.Admin.objects.filter(id=nid).first()
    if request.method == "GET":
        form = AdminEditModelForm(instance=row_object)
        return render(request,'admin_edit.html', {"form":form})

    form = AdminEditModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect("/admin/list/")
    return render(request, 'admin_edit.html', {"form": form})

class AdminResetModelForm(forms.ModelForm):
    confirm_password = forms.CharField(
        label="确认密码",
    )

    class Meta:
        model = models.Admin
        fields = ["password", "confirm_password"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs = {"class": "form-control", "placeholder": field.label}


    def clean_confirm_password(self):
        pwd = self.cleaned_data.get("password")
        confirm = self.cleaned_data.get("confirm_password")
        if confirm != pwd:
            raise ValidationError("密码不一致")
        return confirm

def admin_reset(request, nid):
    row_object = models.Admin.objects.filter(id=nid).first()
    if not row_object:
        return redirect('/admin/list')

    title = "重置密码 = {}".format(row_object.username)
    if request.method == "GET":
        form = AdminResetModelForm(instance=row_object)
        return render(request,'change.html',{"title" : title,"form":form})

    form = AdminResetModelForm(data=request.POST,instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/admin/list/')
    return render(request, 'change.html',{"title" : title,"form":form})

def admin_paper_list(request):
    data_dict = {}
    search_data = request.GET.get('q', "")
    if search_data:
        data_dict["title__contains"] = search_data

    queryset = models.Paper.objects.filter(**data_dict)
    page_object = Pagination(request, queryset)

    context = {
        "search_data": search_data,
        "queryset": page_object.page_queryset,
        "page_string": page_object.html()
    }

    return render(request,'admin_paper_list.html',context)

class PaperForm(forms.Form):

    title = forms.CharField(label="题名")
    author = forms.CharField(label="作者")
    source = forms.CharField(label="来源")
    create_time = forms.DateField(label="发表时间")
    filepath = forms.FileField(label="文档")

    exclude_fields = ['filepath']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name in self.exclude_fields:
                continue
            field.widget.attrs = {"class": "form-control", "placeholder": field.label}

def user_paper_add(request):
    title = "文档上传"
    if request.method == "GET":
        form = PaperForm()
        context = {
            "form": form,
            "title": title
        }
        return render(request, 'user_paper_add.html', context)

    form = PaperForm(data=request.POST, files=request.FILES)
    if form.is_valid():
        image_object = form.cleaned_data.get("filepath")
        db_file_path = os.path.join("static", "file", image_object.name)
        file_path = os.path.join("app", db_file_path)
        f = open(file_path, mode='wb')
        for chunk in image_object.chunks():
            f.write(chunk)
        f.close()

        upload_object = models.UserInfo.objects.filter(name=request.session.get("info")['name']).first()
        models.Paper.objects.create(
            title=form.cleaned_data['title'],
            author=form.cleaned_data['author'],
            source=form.cleaned_data['source'],
            create_time=form.cleaned_data['create_time'],
            uploader=upload_object,
            filepath=db_file_path,
        )
        return redirect('/user/paper/list/')


    data_dict = {}
    search_data = request.GET.get('q', "")
    if search_data:
        data_dict["username__contains"] = search_data

    queryset = models.Admin.objects.filter(**data_dict)
    page_object = Pagination(request, queryset)

    context = {
        "search_data": search_data,
        "queryset": page_object.page_queryset,
        "page_string": page_object.html()
    }

    return render(request,'user_list.html',context)

def vip_paper_add(request):
    title = "文档上传"
    if request.method == "GET":
        form = PaperForm()
        context = {
            "form": form,
            "title": title
        }
        return render(request, 'vip_paper_add.html', context)

    form = PaperForm(data=request.POST, files=request.FILES)
    if form.is_valid():
        image_object = form.cleaned_data.get("filepath")
        db_file_path = os.path.join("static", "file", image_object.name)
        file_path = os.path.join("app", db_file_path)
        f = open(file_path, mode='wb')
        for chunk in image_object.chunks():
            f.write(chunk)
        f.close()

        upload_object = models.UserInfo.objects.filter(name=request.session.get("info")['name']).first()
        models.Paper.objects.create(
            title=form.cleaned_data['title'],
            author=form.cleaned_data['author'],
            source=form.cleaned_data['source'],
            create_time=form.cleaned_data['create_time'],
            uploader=upload_object,
            filepath=db_file_path,
        )
        return redirect('/vip/paper/list/')

    data_dict = {}
    search_data = request.GET.get('q', "")
    if search_data:
        data_dict["username__contains"] = search_data

    queryset = models.Admin.objects.filter(**data_dict)
    page_object = Pagination(request, queryset)

    context = {
        "search_data": search_data,
        "queryset": page_object.page_queryset,
        "page_string": page_object.html()
    }

    return render(request, 'vip_paper_list.html', context)

def paper_delete(request, nid):
    models.Paper.objects.filter(id=nid).delete()
    return redirect("/admin/paper/list/")

class PaperModelForm(forms.ModelForm):
    class Meta:
        model = models.Paper
        fields = ["title", "author", "source", "create_time","uploader"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs = {"class": "form-control", "placeholder": field.label}

def paper_edit(request, nid):
    row_object = models.Paper.objects.filter(id=nid).first()
    if request.method == "GET":
        form = PaperModelForm(instance=row_object)
        return render(request,'paper_edit.html', {"form":form})

    form = PaperModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect("/admin/paper/list/")
    return render(request, 'paper_edit.html', {"form": form})

def user_paper_list(request):
    data_dict = {}
    search_data = request.GET.get('q', "")
    if search_data:
        data_dict["title__contains"] = search_data

    paperset = models.Paper.objects.filter(**data_dict)
    include_object = models.Paper.objects.filter(**data_dict, uploader=request.session.get("info")['id'])
    include_set = set()
    for obj in include_object:
        include_set.add(obj.uploader)

    queryset = list()
    for obj in paperset:
        if obj.uploader in include_set:
            continue
        else:
            queryset.append(obj)

    page_object = Pagination(request, queryset)

    storequery = models.Store.objects.filter(user=request.session.get("info")['id'])
    storeset = set()
    for obj in storequery:
        storeset.add(obj.paper_id)

    context = {
        "search_data": search_data,
        "queryset": page_object.page_queryset,
        "storeset": storeset,
        "page_string": page_object.html(),
    }

    return render(request, 'user_paper_list.html', context)

def vip_paper_list(request):

    nowid = request.session.get("info")['id']
    models.UserInfo.objects.filter(id=nowid).update(rank=1)

    data_dict = {}
    search_data = request.GET.get('q', "")
    if search_data:
        data_dict["title__contains"] = search_data

    paperset = models.Paper.objects.filter(**data_dict)
    include_object = models.Paper.objects.filter(**data_dict, uploader=request.session.get("info")['id'])
    include_set = set()
    for obj in include_object:
        include_set.add(obj.uploader)

    queryset = list()
    for obj in paperset:
        if obj.uploader in include_set:
            continue
        else:
            queryset.append(obj)

    page_object = Pagination(request, queryset)

    storequery = models.Store.objects.filter(user=request.session.get("info")['id'])
    storeset = set()
    for obj in storequery:
        storeset.add(obj.paper_id)

    context = {
        "search_data": search_data,
        "queryset": page_object.page_queryset,
        "storeset": storeset,
        "page_string": page_object.html(),
    }

    return render(request, 'vip_paper_list.html', context)

def pay_list(request):
    return render(request, 'pay_list.html')

def user_mypaper_list(request):
    data_dict = {}
    search_data = request.GET.get('q', "")
    if search_data:
        data_dict["title__contains"] = search_data

    queryset = models.Paper.objects.filter(**data_dict,uploader=request.session.get("info")['id'])
    page_object = Pagination(request, queryset)

    context = {
        "search_data": search_data,
        "queryset": page_object.page_queryset,
        "page_string": page_object.html()
    }

    return render(request, 'user_mypaper_list.html', context)

def vip_mypaper_list(request):
    data_dict = {}
    search_data = request.GET.get('q', "")
    if search_data:
        data_dict["title__contains"] = search_data

    queryset = models.Paper.objects.filter(**data_dict,uploader=request.session.get("info")['id'])
    page_object = Pagination(request, queryset)

    context = {
        "search_data": search_data,
        "queryset": page_object.page_queryset,
        "page_string": page_object.html()
    }

    return render(request, 'vip_mypaper_list.html', context)

@csrf_exempt
def paper_store_add(request):
    print(request.POST)
    # 1.用户发来数据的校验
    paperid = request.POST.get('paperid')

    user_object = models.UserInfo.objects.filter(name=request.session.get("info")['name']).first()
    paper_object = models.Paper.objects.filter(id=paperid).first()
    models.Store.objects.create(
        user=user_object,
        paper=paper_object,
    )
    return JsonResponse({"status": True})

@csrf_exempt
def paper_store_delete(request):
    print(request.POST)
    # 1.用户发来数据的校验
    paperid = request.POST.get('paperid')
    user_object = models.UserInfo.objects.filter(name=request.session.get("info")['name']).first()
    models.Store.objects.filter(user=user_object.id,paper=paperid).delete()
    return JsonResponse({"status": True})

def user_paper_store_list(request):
    data_dict = {}
    search_data = request.GET.get('q', "")
    if search_data:
        data_dict["title__contains"] = search_data

    storeset = models.Store.objects.filter(**data_dict, user=request.session.get("info")['id'])

    paperset = set()
    for obj in storeset:
        paperset.add(obj.paper_id)

    queryset = list()
    super_object = models.Paper.objects.filter(**data_dict)
    for obj in super_object:
        if obj.id in paperset:
            queryset.append(obj)

    page_object = Pagination(request, queryset)
    context = {
        "search_data": search_data,
        "queryset": page_object.page_queryset,
        "page_string": page_object.html()
    }

    return render(request, 'user_paper_store_list.html', context)

def vip_paper_store_list(request):
    data_dict = {}
    search_data = request.GET.get('q', "")
    if search_data:
        data_dict["title__contains"] = search_data

    storeset = models.Store.objects.filter(**data_dict, user=request.session.get("info")['id'])

    paperset = set()
    for obj in storeset:
        paperset.add(obj.paper_id)

    queryset = list()
    super_object = models.Paper.objects.filter(**data_dict)
    for obj in super_object:
        if obj.id in paperset:
            queryset.append(obj)

    page_object = Pagination(request, queryset)

    context = {
        "search_data": search_data,
        "queryset": page_object.page_queryset,
        "page_string": page_object.html()
    }

    return render(request, 'vip_paper_store_list.html', context)

def problem_list(request):

    return render(request,'problem_list.html')


