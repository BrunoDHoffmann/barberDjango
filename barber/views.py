from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Usuario

def anonymous_required(view_func):
    return user_passes_test(lambda u: u.is_anonymous, login_url='/', redirect_field_name=None)(view_func)

@anonymous_required
def cadastro_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        telefone = request.POST.get('telefone')
        
        if senha != confirmar_senha:
            messages.error(request, 'As senhas não coincidem.')
            return render(request, 'cadastro.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Usuario inválido.')
            return render(request, 'cadastro.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email invalido.')
            return render(request, 'cadastro.html')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=senha,
            first_name=first_name,
            last_name=last_name
        )
        Usuario.objects.create(user=user, telefone=telefone)
        
        messages.success(request, 'Cadastro realizado! Faça login para continuar.')
        return redirect('login')
    return render(request, 'cadastro.html')

@anonymous_required
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method=='POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        
        user = authenticate(request, username=username, password=senha)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
        
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home_view(request):
    return render(request, 'home.html')

@login_required
def agendar_view(request):
    return render(request, 'meus_agendamentos.html')

@login_required
def meus_agendamentos_view(request):
    pass

@login_required
def painel_funcionario_view(request):
    pass