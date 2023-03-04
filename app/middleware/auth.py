from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render,HttpResponse,redirect
class AuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        # 排除不需要登录就能访问的页面
        if request.path_info in ["/login/","/image/code/"]:
            return

        # 读取当前访问的用户的session信息
        info_dict = request.session.get("info")
        if info_dict:
            return

        return redirect('/login/')

    def process_response(self, request, response):
        return response