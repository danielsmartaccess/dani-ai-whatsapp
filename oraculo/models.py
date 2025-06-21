from django.db import models

class WhatsAppConfig(models.Model):
    instance_name = models.CharField(max_length=100, default='arcane', help_text='Nome da instância no Evolution API')
    api_url = models.URLField(help_text='URL da Evolution API, ex: https://evolution-api.your-domain.com')
    api_key = models.CharField(max_length=255, help_text='Chave API para autenticação')
    is_active = models.BooleanField(default=False, help_text='Ativar/desativar integração com WhatsApp')
    welcome_message = models.TextField(
        default='Olá! Eu sou Dani AI, seu assistente virtual. Como posso ajudar você hoje?',
        help_text='Mensagem de boas-vindas para novos contatos'
    )
    
    class Meta:
        verbose_name = 'Configuração do WhatsApp'
        verbose_name_plural = 'Configurações do WhatsApp'
    
    def __str__(self):
        return f"Configuração WhatsApp - {self.instance_name} ({'Ativo' if self.is_active else 'Inativo'})"
    
    @classmethod
    def get_active(cls):
        """Retorna a configuração ativa ou None se não houver nenhuma"""
        return cls.objects.filter(is_active=True).first()

class Treinamentos(models.Model):
    site = models.URLField()
    conteudo = models.TextField()
    documento = models.FileField(upload_to='documentos')

    def __str__(self):
        return self.site

class DataTreinamento(models.Model):
    metadata = models.JSONField(null=True, blank=True)
    texto = models.TextField(null=True, blank=True)

class Pergunta(models.Model):
    data_treinamento = models.ManyToManyField(DataTreinamento)
    pergunta = models.TextField()

    def __str__(self):
        return self.pergunta

class EstagioFunil(models.Model):
    nome = models.CharField(max_length=100)
    ordem = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.nome

class Contato(models.Model):
    nome = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    estagio_funil = models.ForeignKey(EstagioFunil, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.CharField(max_length=255, blank=True)
    ultima_interacao = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, default='ativo')
    def __str__(self):
        return f"{self.nome} ({self.telefone})"

class Campanha(models.Model):
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    data_inicio = models.DateTimeField()
    status = models.CharField(max_length=50, default='ativa')
    def __str__(self):
        return self.nome

class SequenciaMensagem(models.Model):
    campanha = models.ForeignKey(Campanha, on_delete=models.CASCADE)
    ordem = models.IntegerField()
    conteudo = models.TextField()
    atraso = models.DurationField(help_text='Atraso após mensagem anterior')
    condicao_envio = models.JSONField(default=dict, blank=True)
    def __str__(self):
        return f"{self.campanha.nome} - Passo {self.ordem}"
