from django.urls import path, include
from .views import *

urlpatterns = [
    path('login/', login_view, name='login'),
    path('cadastro/', cadastro_view, name='cadastro'),
    path('logout/', logout_view, name='logout'),
    path('', home_view, name='home'),
    path('agendar/', agendar_view, name='agendar'),
    path('meus_agendamentos/', meus_agendamentos_view, name='meus_agendamentos'),
    path('painel_funcionario/', painel_funcionario_view, name='painel_funcionario'),
]
