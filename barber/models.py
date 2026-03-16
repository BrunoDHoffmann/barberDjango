from django.db import models
from django.contrib.auth.models import User


class Usuario(models.Model):
    """
    Perfil do usuário. O login é gerenciado pelo User do Django.
    Aqui guardamos apenas os dados extras.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil'
    )
    telefone = models.CharField(max_length=20)
    criado_em = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Funcionario(models.Model):
    nome = models.CharField(max_length=255)
    criado_em = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'funcionarios'
        verbose_name = 'Funcionário'
        verbose_name_plural = 'Funcionários'

    def __str__(self):
        return self.nome


class Servico(models.Model):
    nome = models.CharField(max_length=100)
    duracao_minutos = models.IntegerField()
    preco_centavos = models.IntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'servicos'
        verbose_name = 'Serviço'
        verbose_name_plural = 'Serviços'

    def __str__(self):
        return self.nome


class DisponibilidadeFuncionario(models.Model):
    DIAS = [(i, d) for i, d in enumerate(
        ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    )]
    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        related_name='disponibilidades'
    )
    dia_semana = models.IntegerField(choices=DIAS)
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()

    class Meta:
        db_table = 'disponibilidade_funcionario'
        verbose_name = 'Disponibilidade de Funcionário'
        verbose_name_plural = 'Disponibilidades de Funcionários'

    def __str__(self):
        return f"{self.funcionario.nome} - {self.get_dia_semana_display()}"


class Agendamento(models.Model):
    STATUS = [
        (0, 'Pendente'),
        (1, 'Agendado'),
        (2, 'Cancelado'),
        (3, 'Concluído'),
    ]
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='agendamentos'
    )
    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        related_name='agendamentos'
    )
    data = models.DateField()
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    status = models.IntegerField(choices=STATUS, default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'agendamentos'
        verbose_name = 'Agendamento'
        verbose_name_plural = 'Agendamentos'

    def __str__(self):
        return f"{self.usuario} com {self.funcionario.nome} em {self.data}"


class AgendamentoServico(models.Model):
    agendamento = models.ForeignKey(
        Agendamento,
        on_delete=models.CASCADE,
        related_name='agendamento_servicos'
    )
    servico = models.ForeignKey(
        Servico,
        on_delete=models.CASCADE,
        related_name='agendamento_servicos'
    )

    class Meta:
        db_table = 'agendamento_servicos'
        verbose_name = 'Agendamento Serviço'
        verbose_name_plural = 'Agendamento Serviços'

    def __str__(self):
        return f"{self.agendamento} - {self.servico.nome}"


class Pagamento(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendente'),
        ('PAID', 'Pago'),
        ('CANCELLED', 'Cancelado'),
        ('EXPIRED', 'Expirado'),
    ]
    agendamento = models.OneToOneField(
        Agendamento,
        on_delete=models.CASCADE,
        related_name='pagamento'
    )
    abacatepay_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    url_checkout = models.URLField(blank=True, null=True)
    valor_centavos = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    br_code = models.TextField(blank=True)
    br_code_base64 = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pagamentos'
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'

    def __str__(self):
        return f"Pagamento de {self.agendamento} - {self.status}"


class WebhookAbacatePay(models.Model):
    pagamento = models.ForeignKey(
        Pagamento,
        on_delete=models.CASCADE,
        related_name='webhooks'
    )
    evento = models.CharField(max_length=100)
    payload = models.JSONField()
    recebido_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'webhooks_abacatepay'
        verbose_name = 'Webhook AbacatePay'
        verbose_name_plural = 'Webhooks AbacatePay'

    def __str__(self):
        return f"Webhook {self.evento} - {self.recebido_em}"