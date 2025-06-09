"""
Arquivo de migração para criar o modelo WhatsAppConfig.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oraculo', '0002_datatreinamento_pergunta'),
    ]

    operations = [
        migrations.CreateModel(
            name='WhatsAppConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instance_name', models.CharField(default='arcane', help_text='Nome da instância no Evolution API', max_length=100)),
                ('api_url', models.URLField(help_text='URL da Evolution API, ex: https://evolution-api.your-domain.com')),
                ('api_key', models.CharField(help_text='Chave API para autenticação', max_length=255)),
                ('is_active', models.BooleanField(default=False, help_text='Ativar/desativar integração com WhatsApp')),
                ('welcome_message', models.TextField(default='Olá! Eu sou Dani AI, seu assistente virtual. Como posso ajudar você hoje?', help_text='Mensagem de boas-vindas para novos contatos')),
            ],
            options={
                'verbose_name': 'Configuração do WhatsApp',
                'verbose_name_plural': 'Configurações do WhatsApp',
            },
        ),
    ]
