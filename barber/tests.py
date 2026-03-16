from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date, time
from .models import (
    Usuario, Funcionario, Servico,
    DisponibilidadeFuncionario, Agendamento,
    AgendamentoServico, Pagamento
)


def criar_usuario(**kwargs):
    user = User.objects.create_user(
        username=kwargs.pop('username', 'joaosilva'),
        email=kwargs.pop('email', 'joao@email.com'),
        password=kwargs.pop('password', 'senha123'),
        first_name=kwargs.pop('first_name', 'João'),
        last_name=kwargs.pop('last_name', 'Silva'),
    )
    return Usuario.objects.create(
        user=user,
        telefone=kwargs.pop('telefone', '51999999999'),
    )


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


class UsuarioModelTest(TestCase):

    def test_criar_usuario(self):
        """Verifica se um usuário é criado corretamente"""
        usuario = criar_usuario()
        self.assertEqual(Usuario.objects.count(), 1)

    def test_usuario_tem_telefone(self):
        """Verifica se o telefone é salvo corretamente"""
        usuario = criar_usuario()
        self.assertEqual(usuario.telefone, '51999999999')

    def test_str_usuario_retorna_nome_completo(self):
        """Verifica se __str__ retorna o nome completo do User"""
        usuario = criar_usuario()
        self.assertEqual(str(usuario), 'João Silva')

    def test_acessar_email_pelo_user(self):
        """Verifica se é possível acessar o email pelo User vinculado"""
        usuario = criar_usuario()
        self.assertEqual(usuario.user.email, 'joao@email.com')

    def test_deletar_user_deleta_perfil(self):
        """Verifica o CASCADE: deletar o User apaga o perfil Usuario"""
        usuario = criar_usuario()
        usuario.user.delete()
        self.assertEqual(Usuario.objects.count(), 0)


class FuncionarioModelTest(TestCase):

    def test_criar_funcionario(self):
        funcionario = criar_funcionario()
        self.assertEqual(Funcionario.objects.count(), 1)

    def test_funcionario_ativo_por_padrao(self):
        funcionario = criar_funcionario()
        self.assertTrue(funcionario.is_active)

    def test_str_funcionario(self):
        funcionario = criar_funcionario()
        self.assertEqual(str(funcionario), 'Carlos Barbeiro')


class ServicoModelTest(TestCase):

    def test_criar_servico(self):
        servico = criar_servico()
        self.assertEqual(Servico.objects.count(), 1)

    def test_servico_ativo_por_padrao(self):
        servico = criar_servico()
        self.assertTrue(servico.is_active)

    def test_str_servico(self):
        servico = criar_servico()
        self.assertEqual(str(servico), 'Corte')


class DisponibilidadeFuncionarioModelTest(TestCase):

    def setUp(self):
        self.funcionario = criar_funcionario()

    def test_criar_disponibilidade(self):
        disp = DisponibilidadeFuncionario.objects.create(
            funcionario=self.funcionario,
            dia_semana=0,
            hora_inicio=time(8, 0),
            hora_fim=time(18, 0),
        )
        self.assertEqual(DisponibilidadeFuncionario.objects.count(), 1)

    def test_str_disponibilidade(self):
        disp = DisponibilidadeFuncionario.objects.create(
            funcionario=self.funcionario,
            dia_semana=0,
            hora_inicio=time(8, 0),
            hora_fim=time(18, 0),
        )
        self.assertIn('Carlos Barbeiro', str(disp))
        self.assertIn('Segunda', disp.get_dia_semana_display())

    def test_funcionario_tem_multiplos_dias(self):
        for dia in [0, 1, 2]:
            DisponibilidadeFuncionario.objects.create(
                funcionario=self.funcionario,
                dia_semana=dia,
                hora_inicio=time(8, 0),
                hora_fim=time(18, 0),
            )
        self.assertEqual(self.funcionario.disponibilidades.count(), 3)


class AgendamentoModelTest(TestCase):

    def setUp(self):
        self.usuario = criar_usuario()
        self.funcionario = criar_funcionario()

    def test_criar_agendamento(self):
        agendamento = criar_agendamento(self.usuario, self.funcionario)
        self.assertEqual(Agendamento.objects.count(), 1)

    def test_status_padrao_pendente(self):
        agendamento = criar_agendamento(self.usuario, self.funcionario)
        self.assertEqual(agendamento.status, 0)

    def test_str_agendamento(self):
        agendamento = criar_agendamento(self.usuario, self.funcionario)
        self.assertIn('Carlos Barbeiro', str(agendamento))

    def test_cancelar_agendamento(self):
        agendamento = criar_agendamento(self.usuario, self.funcionario)
        agendamento.status = 2
        agendamento.save()
        agendamento.refresh_from_db()
        self.assertEqual(agendamento.status, 2)

    def test_agendamento_deletado_ao_deletar_usuario(self):
        criar_agendamento(self.usuario, self.funcionario)
        self.usuario.delete()
        self.assertEqual(Agendamento.objects.count(), 0)


class AgendamentoServicoModelTest(TestCase):

    def setUp(self):
        self.usuario = criar_usuario()
        self.funcionario = criar_funcionario()
        self.agendamento = criar_agendamento(self.usuario, self.funcionario)
        self.servico = criar_servico()

    def test_vincular_servico_ao_agendamento(self):
        AgendamentoServico.objects.create(
            agendamento=self.agendamento,
            servico=self.servico,
        )
        self.assertEqual(self.agendamento.agendamento_servicos.count(), 1)

    def test_multiplos_servicos_por_agendamento(self):
        servico2 = criar_servico(nome='Barba', duracao_minutos=20, preco_centavos=2000)
        AgendamentoServico.objects.create(agendamento=self.agendamento, servico=self.servico)
        AgendamentoServico.objects.create(agendamento=self.agendamento, servico=servico2)
        self.assertEqual(self.agendamento.agendamento_servicos.count(), 2)

    def test_servico_deletado_ao_deletar_agendamento(self):
        AgendamentoServico.objects.create(agendamento=self.agendamento, servico=self.servico)
        self.agendamento.delete()
        self.assertEqual(AgendamentoServico.objects.count(), 0)


class PagamentoModelTest(TestCase):

    def setUp(self):
        self.usuario = criar_usuario()
        self.funcionario = criar_funcionario()
        self.agendamento = criar_agendamento(self.usuario, self.funcionario)

    def test_criar_pagamento(self):
        pagamento = Pagamento.objects.create(
            agendamento=self.agendamento,
            valor_centavos=3000,
        )
        self.assertEqual(Pagamento.objects.count(), 1)

    def test_status_padrao_pending(self):
        pagamento = Pagamento.objects.create(
            agendamento=self.agendamento,
            valor_centavos=3000,
        )
        self.assertEqual(pagamento.status, 'PENDING')

    def test_pagamento_unico_por_agendamento(self):
        from django.db import IntegrityError
        Pagamento.objects.create(agendamento=self.agendamento, valor_centavos=3000)
        with self.assertRaises(IntegrityError):
            Pagamento.objects.create(agendamento=self.agendamento, valor_centavos=3000)

    def test_acessar_pagamento_pelo_agendamento(self):
        Pagamento.objects.create(agendamento=self.agendamento, valor_centavos=3000)
        self.assertEqual(self.agendamento.pagamento.valor_centavos, 3000)