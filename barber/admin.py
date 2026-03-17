from django.contrib import admin
from .models import *

class ListaFuncionarios(admin.ModelAdmin):
    list_display = ("id", "user", "is_active")
    list_display_links = ("user", "id")
    search_fields = ("user",)
    list_per_page = 10
    list_editable = ("is_active",)
    
class ListaUsuarios(admin.ModelAdmin):
    list_display = ("id", "user", "is_active")
    list_display_links = ("user", "id")
    search_fields = ("user",)
    list_per_page = 10
    list_editable = ("is_active",)
    
class ListaServicos(admin.ModelAdmin):
    list_display = ("id", "nome", "duracao_minutos", "preco_centavos", "is_active")
    list_display_links = ("nome", "id")
    search_fields = ("nome",)
    list_per_page = 10
    list_editable = ("is_active",)
    
class ListaAgendamento(admin.ModelAdmin):
    list_display = ("id", "funcionario", "usuario", "data", "status")
    list_display_links = ("id", "funcionario", "usuario")
    search_fields = ("funcionario",)
    list_per_page = 10
    list_filter = ("status",)

admin.site.register(Usuario, ListaUsuarios)
admin.site.register(Funcionario, ListaFuncionarios)
admin.site.register(Servico, ListaServicos)
admin.site.register(Agendamento, ListaAgendamento)
admin.site.register(DisponibilidadeFuncionario,)
admin.site.register(AgendamentoServico,)