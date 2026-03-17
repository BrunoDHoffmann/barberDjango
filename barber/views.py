from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import (Usuario, Funcionario, Servico, Agendamento, AgendamentoServico, DisponibilidadeFuncionario)
from datetime import datetime, timedelta, date
    
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
    if hasattr(request.user, 'funcionario'):
        return redirect('painel_funcionario')
    servicos = Servico.objects.filter(is_active=True)
    return render(request, 'home.html', {'servicos': servicos})

@login_required
def agendar_view(request):
    if hasattr(request.user, 'funcionario'):
        return redirect('painel_funcionario')
    
    servicos = Servico.objects.filter(is_active=True)
    funcionarios = Funcionario.objects.filter(is_active=True)
    
    barbeiro_id = request.GET.get('barbeiro_id')
    duracao = request.GET.get('duracao')
    
    if barbeiro_id and duracao:
        from django.http import JsonResponse

        duracao = int(duracao)
        hoje = date.today()
        
        dias_trabalho = DisponibilidadeFuncionario.objects.filter(
            funcionario_id=barbeiro_id
        )
        
        disp_por_dia = {d.dia_semana: d for d in dias_trabalho}
        
        resultado = []
        
        for i in range(14):
            data = hoje + timedelta(days=i)
            
            if data.weekday() not in disp_por_dia:
                continue
            
            disp = disp_por_dia[data.weekday()]
            
            horarios_possiveis = []
            atual = datetime.combine(data, disp.hora_inicio)
            fim = datetime.combine(data, disp.hora_fim)
            
            while atual < fim:
                hora_fim_servico = atual + timedelta(minutes=duracao)
                if hora_fim_servico.time() <= disp.hora_fim:
                    horarios_possiveis.append(atual.strftime('%H:%M'))
                atual += timedelta(minutes=30)
                
            agendamentos_do_dia = Agendamento.objects.filter(
                funcionario_id=barbeiro_id,
                data=data,
                status__in=[0, 1]
            )
            
            horarios_livres = []
            for horario in horarios_possiveis:
                hora_inicio_dt = datetime.strptime(horario, '%H:%M').time()
                hora_fim_dt = (datetime.combine(data, hora_inicio_dt) + timedelta(minutes=duracao)).time()

                conflito = False
                for agendamento in agendamentos_do_dia:
                    if not (hora_fim_dt <= agendamento.hora_inicio or hora_inicio_dt >= agendamento.hora_fim):
                        conflito=True
                        break
                
                if not conflito:
                    horarios_livres.append(horario)
            
            if horarios_livres:
                resultado.append({
                    'data': data.strftime('%Y-%m-%d'),
                    'data_exibicao': data.strftime('%d/%m/%Y'),
                    'dia_semana': data.strftime('%A'),
                    'horarios': horarios_livres
                })
        
        return JsonResponse({'dias': resultado})
        
    if request.method == 'POST':
        servicos_ids = request.POST.getlist('servicos')
        funcionario_id = request.POST.get('barbeiro')
        data_str = request.POST.get('data')
        hora_inicio_str = request.POST.get('hora_inicio')

        data_obj = datetime.strptime(data_str, '%Y-%m-%d').date()
        hora_inicio_obj = datetime.strptime(hora_inicio_str, '%H:%M').time()

        if not servicos_ids:
            messages.error(request, 'Selecione pelo menos 1 serviço.')
            return render(request, 'agendar.html', {'funcionarios': funcionarios, 'servicos': servicos})

        funcionario = get_object_or_404(Funcionario, id=funcionario_id)
        servicos_escolhidos = Servico.objects.filter(id__in=servicos_ids)
        total_minutos = sum(s.duracao_minutos for s in servicos_escolhidos)

        hora_inicio_dt = datetime.combine(data_obj, hora_inicio_obj)
        hora_fim_dt = hora_inicio_dt + timedelta(minutes=total_minutos)
        hora_fim_obj = hora_fim_dt.time()

        data_num = data_obj.weekday()
        func_disp = DisponibilidadeFuncionario.objects.filter(
            funcionario=funcionario,
            dia_semana=data_num
        ).first()

        if func_disp is None:
            messages.error(request, 'O funcionário não trabalha nesse dia.')
            return render(request, 'agendar.html', {'funcionarios': funcionarios, 'servicos': servicos})

        if hora_inicio_obj < func_disp.hora_inicio or hora_fim_obj > func_disp.hora_fim:
            messages.error(request, 'Horário fora do expediente do funcionário.')
            return render(request, 'agendar.html', {'funcionarios': funcionarios, 'servicos': servicos})

        conflito = Agendamento.objects.filter(
            funcionario=funcionario,
            data=data_obj,
            status__in=[0, 1]
        ).exclude(hora_fim__lte=hora_inicio_obj).exclude(hora_inicio__gte=hora_fim_obj)

        if conflito.exists():
            messages.error(request, 'Esse horário já está ocupado. Escolha outro.')
            return render(request, 'agendar.html', {'funcionarios': funcionarios, 'servicos': servicos})

        usuario = request.user.perfil

        agendamento = Agendamento.objects.create(
            usuario=usuario,
            funcionario=funcionario,
            data=data_obj,
            hora_inicio=hora_inicio_obj,
            hora_fim=hora_fim_obj,
            status=0,
        )

        for servico in servicos_escolhidos:
            AgendamentoServico.objects.create(agendamento=agendamento, servico=servico)

        messages.success(request, 'Agendamento realizado com sucesso!')
        return redirect('meus_agendamentos')

    return render(request, 'agendar.html', {'funcionarios': funcionarios, 'servicos': servicos})

@login_required
def meus_agendamentos_view(request):
    if hasattr(request.user, 'funcionario'):
        return redirect('painel_funcionario')
    usuario = request.user.perfil
    agendamentos = Agendamento.objects.filter(usuario=usuario).order_by('-data', '-hora_inicio')
    return render(request, 'meus_agendamentos.html', {'agendamentos': agendamentos})

@login_required
def cancelar_agendamento_view(request, pk):
    agendamento = get_object_or_404(Agendamento, pk=pk, usuario=request.user.perfil)
    agendamento.status = 2
    agendamento.save()
    return redirect('meus_agendamentos')

@login_required
def painel_funcionario_view(request):
    from datetime import date

    if not hasattr(request.user, 'funcionario'):
        return redirect('home')

    hoje = date.today()
    data_filtro = request.GET.get('data', str(hoje))
    data_filtro_obj = datetime.strptime(data_filtro, '%Y-%m-%d').date()

    agendamentos = Agendamento.objects.filter(
        data=data_filtro_obj
    ).order_by('hora_inicio').select_related('usuario__user', 'funcionario')

    return render(request, 'painel_funcionario.html', {
        'agendamentos': agendamentos,
        'data_filtro': data_filtro,
        'hoje': str(hoje),
    })