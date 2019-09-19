from django.http import HttpResponse
from django.shortcuts import render
from loginUser.models import *
import hashlib
from django.http import HttpResponseRedirect


def wrapper(func):
    def inner(request, *args, **kwargs):
        username1 = request.COOKIES.get('email')
        username2 = request.session.get('email')
        if username1 and username2 and username1 == username2:
            return func(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('/login/')

    return inner


def setmd5(password):
    md5 = hashlib.md5()  # 创建一个md5的实例化对象
    md5.update(password.encode())  # 进行加密
    result = md5.hexdigest()
    return result


def register(request):
    if request.method == "POST":
        feedback = ''
        data = request.POST
        email = data.get('email')
        password1 = data.get('password1')
        password2 = data.get('password2')

        if email and password1 and password2:
            if password1 != password2:
                feedback = '两次输入密码不相同'
            else:
                loginuser = LoginUser.objects.filter(email=email).first()
                if loginuser and email == loginuser.email:
                    feedback = '此账号已经注册,请直接登录'
                else:
                    loginuser = LoginUser()
                    loginuser.email = email
                    loginuser.password = setmd5(password1)
                    loginuser.save()
                    feedback = '注册成功,去登录吧'
        else:
            feedback = '请填写所有信息进行注册'

    return render(request, 'register.html', locals())


def login(request):
    if request.method == "POST":
        feedback = ''
        data = request.POST
        email = data.get('email')
        password = setmd5(data.get('password'))
        if email and password:
            loginuser = LoginUser.objects.filter(email=email).first()
            if loginuser and email == loginuser.email:
                if password and password == loginuser.password:

                    response = HttpResponseRedirect('/index/')
                    response.set_cookie('email', loginuser.email)
                    request.session['email'] = loginuser.email
                    return response

                else:
                    feedback = '密码不对啊小老弟'
            else:
                feedback = '此账号不存在'
        else:
            feedback = '账号为空'

    return render(request, 'login.html', locals())


@wrapper
def index(request):
    return render(request, 'index.html', locals())


def logout(request):
    response = HttpResponseRedirect('/login/')
    keys = request.COOKIES.keys()
    for one in keys:
        response.delete_cookie(one)
    request.session.flush()
    return response
