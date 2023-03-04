
from django.contrib import admin
from django.urls import path

from app import views

urlpatterns = [
    path('user/list/', views.user_list),
    path('user/add/', views.user_add),
    path('user/<int:nid>/delete/', views.user_delete),
    path('user/<int:nid>/edit/',views.user_edit),

    path('admin/list/', views.admin_list),
    path('admin/add/', views.admin_add),
    path('admin/<int:nid>/delete/', views.admin_delete),
    path('admin/<int:nid>/edit/', views.admin_edit),
    path('admin/<int:nid>/reset/', views.admin_reset),

    path('login/', views.login),
    path('logout/', views.logout),
    path('image/code/', views.image_code),

    path('admin/paper/list/', views.admin_paper_list),
    path('user/paper/add/', views.user_paper_add),
    path('vip/paper/add/', views.vip_paper_add),
    path('paper/<int:nid>/delete/', views.paper_delete),
    path('paper/<int:nid>/edit/', views.paper_edit),

    path('user/paper/list/', views.user_paper_list),
    path('vip/paper/list/', views.vip_paper_list),
    path('pay/list/', views.pay_list),
    path('user/mypaper/list/', views.user_mypaper_list),
    path('vip/mypaper/list/', views.vip_mypaper_list),

    path('paper/store/add/', views.paper_store_add),
    path('paper/store/delete/', views.paper_store_delete),
    path('user/paper/store/list/', views.user_paper_store_list),
    path('vip/paper/store/list/', views.vip_paper_store_list),
    path('problem/list/', views.problem_list),
]
