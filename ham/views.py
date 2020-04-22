from django.shortcuts import HttpResponse, render, redirect
from django import forms
from .models import Ham
from .tasks import ham_run
from django.urls import reverse
from django.contrib import messages
# Create your views here.


def ham(request):
    return render(request, 'ham/welcome.html')


def sign_up(request):
    if request.method == 'POST':
        form = forms.Form(request.POST)
        username = form.data['username']
        IMEI = form.data['IMEI']
        sex = form.data['sex']
        if len(sex)*len(IMEI)*len(username) == 0:
            messages.error(request, '填写信息不能为空')
            return render(request, 'ham/sign_up.html')
        if Ham.objects.filter(username=username).count() != 0:
            messages.error(request, username+'已被注册, 请更换其他用户名')
            return render(request, 'ham/sign_up.html')
        if len(IMEI) != 32:
            messages.error(request, 'IMEI长度应为32位, 请重新输入')
            return render(request, 'ham/sign_up.html')
        if Ham.objects.filter(IMEI=IMEI).count() != 0:
            messages.error(request, IMEI+"已经存在于数据库中, 无需重复注册\n其对应的用户名为"+Ham.objects.get(IMEI=IMEI).username)
            return render(request, 'ham/sign_up.html')
        obj = Ham.objects.create(IMEI=IMEI, username=username, sex=sex)
        obj.save()
        messages.success(request, '恭喜你，注册成功!')
        return redirect(reverse('ham:sign_in'))
    else:
        return render(request, 'ham/sign_up.html')


def sign_in(request):
    if request.method == 'POST':
        form = forms.Form(request.POST)
        username = form.data['username']
        if Ham.objects.filter(username=username).count() == 0:
            messages.error(request, '无法在数据库中找到'+username+'的信息')
            return render(request, 'ham/sign_in.html')
        obj = Ham.objects.get(username=username)
        obj.is_running = True
        obj.save()
        ham_run(username)
        return render(request, 'notice.html', {'notice': "已经开始处理请求，稍后请在查询页查看您的跑步状态"})
    else:
        return render(request, 'ham/sign_in.html')


def check(request):
    if request.method == 'POST':
        form = forms.Form(request.POST)
        username = form.data['username']
        if Ham.objects.filter(username=username).count() == 0:
            messages.error(request, '该账户未注册')
            return render(request, 'ham/check.html')
        obj = Ham.objects.get(username=username)
        if obj.is_running:
            messages.info(request, '正在跑步中，请稍候再来')
            return render(request, 'ham/check.html')
        if obj.recent_result:
            messages.success(request, '跑步已完成')
            return render(request, 'ham/check.html')
        else:
            messages.error(request, '该账户IMEI已过期，请更新IMEI')
            request.session['username'] = username
            return redirect(reverse('ham:update'))
    else:
        return render(request, 'ham/check.html')


def update(request):
    if request.method == 'POST':
        form = forms.Form(request.POST)
        IMEI = form.data['IMEI']
        if len(IMEI) != 32:
            messages.error(request, 'IMEI长度应为32位, 请重新输入')
            return render(request, 'ham/update.html')
        obj = Ham.objects.get(username=request.session['username'])
        if IMEI == obj.IMEI:
            messages.error(request, '新IMEI不能与旧IMEI相同')
            return render(request, 'ham/update.html')
        obj.IMEI = IMEI
        messages.success(request, 'IMEI更新成功，即将跳转到登录页面')
        return redirect(reverse('ham:sign_in'))
    else:
        return render(request, 'ham/update.html')