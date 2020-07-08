from django.shortcuts import render, HttpResponse
from django.views.generic import ListView
from django.contrib import messages

from user.forms import RegisterForm
from user.models import Users

# Create your views here.
from user.utils.email import send_activate_mail
import uuid


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            u_tables = Users()
            u_tables.id = uuid.uuid1()
            u_tables.nickname = form.cleaned_data['nickname']
            u_tables.email = form.cleaned_data['email']
            u_tables.password = form.cleaned_data['password']
            u_tables.age = form.cleaned_data['age']
            if form.cleaned_data['sex'] == 0:
                u_tables.sex = '男'
            else:
                u_tables.sex = '女'

            token = u_tables.generate_activate_token().decode('utf-8')
            send_activate_mail(request, u_tables.email, '激活账号', 'email', token=token, username=u_tables.nickname)
            messages.add_message(request, messages.INFO, '账号注册成功，请前往邮箱激活账号！')

            u_tables.email_save()

            return render(request, 'user_info.html', context={'user': u_tables.id})
        else:
            return render(request, 'register.html', context={'form': form, 'errors': form.errors})
    else:
        form = RegisterForm()
    return render(request, 'register.html', context={'form': form})


def login(request):
    return render(request, 'login.html')


def user_info(request):
    return render(request, 'user_info.html')


class UsersList(ListView):
    model = Users


def activate(request):
    token = request.GET['token']
    result = Users.check_activate_token(token)
    return HttpResponse(result)
