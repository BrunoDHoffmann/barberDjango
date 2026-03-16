from django.db import models
from datetime import datetime

class Usuario(models.Model):
    nome = models.CharField(max_length=255, null=False, blank=False)
    email = models.EmailField(max_length=255, unique=True)
    telefone = models.CharField(max_length=20, unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        
    def __str__(self):
        return self.nome
    
class Funcionario(models.Model):
    nome = models.CharField(max_length=255, null=False, blank=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'funcionarios'
        verbose_name = 'Funcionario'
        verbose_name_plural = 'Funcionarios'
        
    def __str__(self):
        return self.nome
    
class Servico(models.Model):
    nome = models.CharField(max_length=100, null=False, blank=False)
    duracao_minutos = models.IntegerField(null=False, blank=False)
    preco_centavos = models.IntegerField(null=False, blank=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'servicos'
        verbose_name = 'Serviço'
        verbose_name_plural = 'Serviços'
    
    def __str__(self):
        return self.nome
    
class DisponibilidadeFuncionario(models.Model):
    DIAS = [(i, d) for i, d in enumerate(
        ['Segunda','Terça','Quarta','Quinta','Sexta','Sábado','Domingo']
    )]
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, null=False, blank=False, related_name='disponibilidades')
    dia_semana = models.IntegerField(choices=DIAS, null=False, blank=False)
    hora_inicio = models.TimeField(null=False, blank=False)
    hora_fim = models.TimeField(null=False, blank=False)
    
    class Meta:
        db_table = 'disponibilidade_funcionario'
        verbose_name = 'Disponibilidade de Funcionario'
        verbose_name_plural = 'Disponibilidade de Funcionarios'
        
    def __str__(self):
        return self.funcionario
    
class Agendamento(models.Model):
    STATUS = [(i, d) for i, d in enumerate(
        ['Pendente','Agendado','Cancelado','Concluido']
    )]
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=False, blank=False, related_name='agendamentos')
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, null=False, blank=False, related_name='agendamentos')
    data = models.DateField(null=False, blank=False)
    hora_inicio = models.TimeField(null=False, blank=False)
    hora_fim = models.TimeField(null=False, blank=False)
    status = models.IntegerField(choices=STATUS)
    
    class Meta:
        db_table = 'agendamentos'
        verbose_name = 'Agendamento'
        verbose_name_plural = 'Agendamentos'
        
    def __str__(self):
        return f"{self.usuario.nome} com {self.funcionario.nome} em {self.data}"
    
class AgendamentoServico(models.Model):
    agendamento = models.ForeignKey(Agendamento, on_delete=models.CASCADE, related_name='agendamento_servicos')
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE, related_name='agendamento_servicos')
    
    class Meta:
        db_table = 'agendamento_servicos'
        verbose_name = 'Agendamento Serviço'
        verbose_name_plural = 'Agendamento Serviços'
    
    def __str__(self):
        return f"{self.funcionario.nome} - {self.get_dia_semana_display()}"
    
class Pagamento(models.Model):
    """
    Armazena a cobrança criada na AbacatePay.
    Cada agendamento pode ter um pagamento vinculado.
    """

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

    # Dados que vêm da AbacatePay ao criar a cobrança
    abacatepay_id = models.CharField(max_length=100, unique=True)
    url_checkout = models.URLField()
    valor_centavos = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    # Dados do PIX (QR Code)
    br_code = models.TextField(blank=True)        # código copia-e-cola
    br_code_base64 = models.TextField(blank=True) # imagem do QR Code em base64

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pagamento {self.abacatepay_id} - {self.status}"


class WebhookAbacatePay(models.Model):
    """
    Registra cada notificação recebida da AbacatePay.
    Útil para auditoria e para reprocessar eventos se necessário.
    """

    pagamento = models.ForeignKey(
        Pagamento,
        on_delete=models.CASCADE,
        related_name='webhooks'
    )

    evento = models.CharField(max_length=100)   # ex: "billing.paid"
    payload = models.JSONField()                 # corpo completo do webhook
    recebido_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Webhook {self.evento} - {self.recebido_em}"