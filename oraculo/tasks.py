from celery import shared_task
from .wrapper_evolutionapi import WhatsAppAPI
from django.utils import timezone
from .models import Campanha, SequenciaMensagem, Contato
from .utils import gerar_mensagem_personalizada
from datetime import timedelta

@shared_task
def enviar_mensagem_agendada(instance, to, message):
    api = WhatsAppAPI()
    api.send_text_message(instance, to, message)

@shared_task
def processar_campanha(campanha_id):
    """
    Processa uma campanha disparando as mensagens da sequência para todos os contatos.
    Personaliza cada mensagem usando LLM/RAG (função utilitária).
    """
    try:
        campanha = Campanha.objects.get(id=campanha_id)
    except Campanha.DoesNotExist:
        return
    contatos = Contato.objects.filter(status='ativo')
    sequencias = SequenciaMensagem.objects.filter(campanha=campanha).order_by('ordem')
    now = timezone.now()
    for contato in contatos:
        agendamento = now
        for seq in sequencias:
            mensagem = gerar_mensagem_personalizada(contato, campanha, seq)
            # Agendamento: atraso cumulativo por etapa
            agendamento += seq.atraso if seq.atraso else timedelta()
            enviar_mensagem_agendada.apply_async(args=[campanha.nome, contato.telefone, mensagem], eta=agendamento)

@shared_task
def verificar_status_mensagens():
    # Lógica para verificar status de mensagens em lote
    pass
