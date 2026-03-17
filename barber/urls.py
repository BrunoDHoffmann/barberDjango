from django.urls import path, include
from .views import *

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('cadastro/', cadastro_view, name='cadastro'),
    path('logout/', logout_view, name='logout'),
    path('agendar/', agendar_view, name='agendar'),
    path('meus-agendamentos/', meus_agendamentos_view, name='meus_agendamentos'),
    path('cancelar-agendamento/<int:pk>/', cancelar_agendamento_view, name='cancelar_agendamento'),
    path('painel/', painel_funcionario_view, name='painel_funcionario'),
]
