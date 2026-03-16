from django.test import TestCase
from datetime import date, time
from django.db import IntegrityError
from .models import (
    Usuario, Funcionario, Servico,
    DisponibilidadeFuncionario, Agendamento,
    AgendamentoServico, Pagamento
)


# ─────────────────────────────────────────
# Funções auxiliares para criar dados de teste
# ─────────────────────────────────────────

def criar_usuario(**kwargs):
    dados = {
        'nome': 'João Silva',
        'email': 'joao@email.com',
        'telefone': '51999999999',
    }
    dados.update(kwargs)
    return Usuario.objects.create(**dados)


def criar_funcionario(**kwargs):
    dados = {'nome': 'Carlos Barbeiro'}
    dados.update(kwargs)
    return Funcionario.objects.create(**dados)


def criar_servico(**kwargs):
    dados = {
        'nome': 'Corte',
        'duracao_minutos': 30,
        'preco_centavos': 3000,
    }
    dados.update(kwargs)
    return Servico.objects.create(**dados)


def criar_agendamento(usuario, funcionario, **kwargs):
    dados = {
        'usuario': usuario,
        'funcionario': funcionario,
        'data': date(2026, 6, 10),
        'hora_inicio': time(10, 0),
        'hora_fim': time(10, 30),
        'status': 0,
    }
    dados.update(kwargs)
    return Agendamento.objects.create(**dados)


# ─────────────────────────────────────────
# Testes de Usuario
# ─────────────────────────────────────────

class UsuarioModelTest(TestCase):

    def test_criar_usuario(self):
        """Verifica se um usuário é criado e salvo corretamente"""
        usuario = criar_usuario()
        self.assertEqual(Usuario.objects.count(), 1)
        self.assertEqual(usuario.nome, 'João Silva')

    def test_usuario_ativo_por_padrao(self):
        """Verifica se is_active começa como True"""
        usuario = criar_usuario()
        self.assertTrue(usuario.is_active)

    def test_str_usuario(self):
        """Verifica se __str__ retorna o nome"""
        usuario = criar_usuario()
        self.assertEqual(str(usuario), 'João Silva')

    def test_email_unico(self):
        """Verifica que dois usuários não podem ter o mesmo email"""
        criar_usuario()
        with self.assertRaises(IntegrityError):
            criar_usuario()  # mesmo email → deve lançar erro


# ─────────────────────────────────────────
# Testes de Funcionario
# ─────────────────────────────────────────

class FuncionarioModelTest(TestCase):

    def test_criar_funcionario(self):
        """Verifica se um funcionário é criado corretamente"""
        funcionario = criar_funcionario()
        self.assertEqual(Funcionario.objects.count(), 1)
        self.assertEqual(funcionario.nome, 'Carlos Barbeiro')

    def test_funcionario_ativo_por_padrao(self):
        """Verifica se is_active começa como True"""
        funcionario = criar_funcionario()
        self.assertTrue(funcionario.is_active)

    def test_str_funcionario(self):
        """Verifica se __str__ retorna o nome"""
        funcionario = criar_funcionario()
        self.assertEqual(str(funcionario), 'Carlos Barbeiro')


# ─────────────────────────────────────────
# Testes de Servico
# ─────────────────────────────────────────

class ServicoModelTest(TestCase):

    def test_criar_servico(self):
        """Verifica se um serviço é criado corretamente"""
        servico = criar_servico()
        self.assertEqual(Servico.objects.count(), 1)
        self.assertEqual(servico.preco_centavos, 3000)

    def test_servico_ativo_por_padrao(self):
        """Verifica se is_active começa como True"""
        servico = criar_servico()
        self.assertTrue(servico.is_active)

    def test_str_servico(self):
        """Verifica se __str__ retorna o nome"""
        servico = criar_servico()
        self.assertEqual(str(servico), 'Corte')


# ─────────────────────────────────────────
# Testes de DisponibilidadeFuncionario
# ─────────────────────────────────────────

class DisponibilidadeFuncionarioModelTest(TestCase):

    def setUp(self):
        # setUp é executado antes de cada teste desta classe
        self.funcionario = criar_funcionario()

    def test_criar_disponibilidade(self):
        """Verifica se a disponibilidade é criada corretamente"""
        disp = DisponibilidadeFuncionario.objects.create(
            funcionario=self.funcionario,
            dia_semana=0,  # Segunda
            hora_inicio=time(8, 0),
            hora_fim=time(18, 0),
        )
        self.assertEqual(DisponibilidadeFuncionario.objects.count(), 1)
        self.assertEqual(disp.dia_semana, 0)

    def test_str_disponibilidade(self):
        """Verifica se __str__ retorna nome do funcionário e dia"""
        disp = DisponibilidadeFuncionario.objects.create(
            funcionario=self.funcionario,
            dia_semana=0,
            hora_inicio=time(8, 0),
            hora_fim=time(18, 0),
        )
        self.assertIn('Carlos Barbeiro', str(disp.funcionario.nome))
        self.assertIn('Segunda', disp.get_dia_semana_display())

    def test_funcionario_tem_multiplos_dias(self):
        """Verifica se um funcionário pode ter disponibilidade em vários dias"""
        for dia in [0, 1, 2]:  # Segunda, Terça, Quarta
            DisponibilidadeFuncionario.objects.create(
                funcionario=self.funcionario,
                dia_semana=dia,
                hora_inicio=time(8, 0),
                hora_fim=time(18, 0),
            )
        self.assertEqual(self.funcionario.disponibilidades.count(), 3)


# ─────────────────────────────────────────
# Testes de Agendamento
# ─────────────────────────────────────────

class AgendamentoModelTest(TestCase):

    def setUp(self):
        self.usuario = criar_usuario()
        self.funcionario = criar_funcionario()

    def test_criar_agendamento(self):
        """Verifica se um agendamento é criado corretamente"""
        agendamento = criar_agendamento(self.usuario, self.funcionario)
        self.assertEqual(Agendamento.objects.count(), 1)

    def test_status_padrao_pendente(self):
        """Verifica se o status começa como 0 (Pendente)"""
        agendamento = criar_agendamento(self.usuario, self.funcionario)
        self.assertEqual(agendamento.status, 0)

    def test_str_agendamento(self):
        """Verifica se __str__ contém nome do usuário e funcionário"""
        agendamento = criar_agendamento(self.usuario, self.funcionario)
        self.assertIn('João Silva', str(agendamento))
        self.assertIn('Carlos Barbeiro', str(agendamento))

    def test_cancelar_agendamento(self):
        """Verifica se o status pode ser alterado para Cancelado (2)"""
        agendamento = criar_agendamento(self.usuario, self.funcionario)
        agendamento.status = 2
        agendamento.save()
        agendamento.refresh_from_db()  # recarrega do banco para confirmar
        self.assertEqual(agendamento.status, 2)

    def test_agendamento_deletado_ao_deletar_usuario(self):
        """Verifica o CASCADE: deletar usuário apaga seus agendamentos"""
        criar_agendamento(self.usuario, self.funcionario)
        self.usuario.delete()
        self.assertEqual(Agendamento.objects.count(), 0)


# ─────────────────────────────────────────
# Testes de AgendamentoServico
# ─────────────────────────────────────────

class AgendamentoServicoModelTest(TestCase):

    def setUp(self):
        self.usuario = criar_usuario()
        self.funcionario = criar_funcionario()
        self.agendamento = criar_agendamento(self.usuario, self.funcionario)
        self.servico = criar_servico()

    def test_vincular_servico_ao_agendamento(self):
        """Verifica se um serviço é vinculado ao agendamento corretamente"""
        AgendamentoServico.objects.create(
            agendamento=self.agendamento,
            servico=self.servico,
        )
        self.assertEqual(self.agendamento.agendamento_servicos.count(), 1)

    def test_multiplos_servicos_por_agendamento(self):
        """Verifica se um agendamento aceita mais de um serviço"""
        servico2 = criar_servico(nome='Barba', duracao_minutos=20, preco_centavos=2000)
        AgendamentoServico.objects.create(agendamento=self.agendamento, servico=self.servico)
        AgendamentoServico.objects.create(agendamento=self.agendamento, servico=servico2)
        self.assertEqual(self.agendamento.agendamento_servicos.count(), 2)

    def test_servico_deletado_ao_deletar_agendamento(self):
        """Verifica o CASCADE: deletar agendamento apaga os serviços vinculados"""
        AgendamentoServico.objects.create(agendamento=self.agendamento, servico=self.servico)
        self.agendamento.delete()
        self.assertEqual(AgendamentoServico.objects.count(), 0)


# ─────────────────────────────────────────
# Testes de Pagamento
# ─────────────────────────────────────────

class PagamentoModelTest(TestCase):

    def setUp(self):
        self.usuario = criar_usuario()
        self.funcionario = criar_funcionario()
        self.agendamento = criar_agendamento(self.usuario, self.funcionario)

    def test_criar_pagamento(self):
        """Verifica se um pagamento é criado e vinculado ao agendamento"""
        pagamento = Pagamento.objects.create(
            agendamento=self.agendamento,
            valor_centavos=3000,
        )
        self.assertEqual(Pagamento.objects.count(), 1)
        self.assertEqual(pagamento.status, 'PENDING')

    def test_status_padrao_pending(self):
        """Verifica se o status começa como PENDING"""
        pagamento = Pagamento.objects.create(
            agendamento=self.agendamento,
            valor_centavos=3000,
        )
        self.assertEqual(pagamento.status, 'PENDING')

    def test_pagamento_unico_por_agendamento(self):
        """Verifica que um agendamento não pode ter dois pagamentos (OneToOne)"""
        from django.db import IntegrityError
        Pagamento.objects.create(agendamento=self.agendamento, valor_centavos=3000)
        with self.assertRaises(IntegrityError):
            Pagamento.objects.create(agendamento=self.agendamento, valor_centavos=3000)

    def test_acessar_pagamento_pelo_agendamento(self):
        """Verifica se é possível acessar o pagamento a partir do agendamento"""
        Pagamento.objects.create(agendamento=self.agendamento, valor_centavos=3000)
        self.assertEqual(self.agendamento.pagamento.valor_centavos, 3000)