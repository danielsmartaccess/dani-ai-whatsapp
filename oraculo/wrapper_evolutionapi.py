from urllib.parse import urlencode, urljoin
import json
import requests
from django.conf import settings

class BaseEvolutionAPI:
    def __init__(self):
        self._BASE_URL = settings.EVOLUTION_API_BASE_URL
        self._API_KEY = {
            'arcane': settings.EVOLUTION_API_KEY
        }
 
    def _send_request(
        self, 
        path, 
        method='GET', 
        body=None, 
        headers={}, 
        params_url={}): 
        
        method = method.upper()
        url = self._mount_url(path, params_url)
        parameters = ''

        if not isinstance(headers, dict):
            headers = {}

        headers.setdefault('Content-Type', 'application/json')

        instance = self._get_instance(path)
        headers['apikey'] = self._API_KEY.get(instance)
        
        request = {
            'GET': requests.get,
            'POST': requests.post,
            'PUT': requests.put,
            'DELETE': requests.delete
        }.get(method)

        return request(url, headers=headers, json=body)

    def _mount_url(self, path, params_url):
        parameters = ''
        if isinstance(params_url, dict):
            parameters = urlencode(params_url)
            
        url = urljoin(self._BASE_URL, path)
        
        if parameters:
            url = f"{url}?{parameters}"
        
        return url
    
    def _get_instance(self, path):
        return path.strip('/').split('/')[-1]


class WhatsAppAPI(BaseEvolutionAPI):
    def send_text_message(self, instance, to, message):
        """
        Envia uma mensagem de texto para um número no WhatsApp
        
        Args:
            instance: Nome da instância WhatsApp configurada na Evolution API
            to: Número de telefone do destinatário no formato internacional (ex: 5511999999999)
            message: Texto da mensagem a ser enviada
        """
        path = f'/message/sendText/{instance}'
        body = {
            "number": to,
            "options": {
                "delay": 1200,
                "presence": "composing",
                "linkPreview": True
            },
            "textMessage": {
                "text": message
            }
        }
        
        return self._send_request(path, method='POST', body=body)
    
    def send_reply(self, instance, to, message, message_id):
        """
        Envia uma resposta a uma mensagem específica
        
        Args:
            instance: Nome da instância WhatsApp configurada na Evolution API
            to: Número de telefone do destinatário no formato internacional (ex: 5511999999999)
            message: Texto da mensagem a ser enviada
            message_id: ID da mensagem original a ser respondida
        """
        path = f'/message/sendText/{instance}'
        body = {
            "number": to,
            "options": {
                "delay": 1200,
                "presence": "composing",
                "quotedMsg": message_id
            },
            "textMessage": {
                "text": message
            }
        }
        
        return self._send_request(path, method='POST', body=body)
    
    def get_instance_status(self, instance):
        """
        Verifica o status da instância do WhatsApp
        
        Args:
            instance: Nome da instância WhatsApp configurada na Evolution API
        """
        path = f'/instance/connectionState/{instance}'
        return self._send_request(path, method='GET')
    
    def generate_qr_code(self, instance):
        """
        Gera um QR Code para conectar o WhatsApp
        
        Args:
            instance: Nome da instância WhatsApp configurada na Evolution API
        """
        path = f'/instance/qrcode/{instance}'
        return self._send_request(path, method='GET')
        
    def disconnect_whatsapp(self, instance):
        """
        Desconecta o WhatsApp (logout)
        
        Args:
            instance: Nome da instância WhatsApp configurada na Evolution API
        """
        path = f'/instance/logout/{instance}'
        return self._send_request(path, method='DELETE')
    
    def enviar_mensagem_massa(self, instance, contatos, mensagem):
        """
        Envia uma mensagem de texto para uma lista de contatos.
        contatos: lista de números (strings)
        mensagem: texto da mensagem
        """
        resultados = []
        for numero in contatos:
            resp = self.send_text_message(instance, numero, mensagem)
            resultados.append({'numero': numero, 'status': resp.status_code})
        return resultados

    def agendar_mensagem(self, instance, to, message, send_at):
        """
        Agenda o envio de uma mensagem para um número em um horário futuro.
        send_at: datetime.datetime
        """
        # Exemplo simples: você pode usar Celery para agendar de verdade
        from oraculo.tasks import enviar_mensagem_agendada
        enviar_mensagem_agendada.apply_async(args=[instance, to, message], eta=send_at)
        return {'status': 'agendado', 'numero': to, 'horario': send_at}

    def verificar_status_mensagem(self, instance, message_id):
        """
        Verifica o status de uma mensagem enviada
        """
        path = f'/message/status/{instance}/{message_id}'
        return self._send_request(path, method='GET')

