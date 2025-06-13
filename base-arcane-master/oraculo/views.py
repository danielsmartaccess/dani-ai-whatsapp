from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from rolepermissions.checkers import has_permission
from pathlib import Path
from django.conf import settings
from django.utils import timezone

from .models import Treinamentos, Pergunta, DataTreinamento
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS

from .utils import sched_message_response

def treinar_ia(request):
    """
    View para página de treinamento da IA.
    Permite enviar novos dados para treinamento e listar treinamentos já realizados.
    
    Args:
        request: Objeto de requisição HTTP
    
    Returns:
        Renderiza o template com os treinamentos ou redireciona após salvar
    """
    # Verifica permissões
    if not has_permission(request.user, 'treinar_ia'):
        raise Http404()
        
    if request.method == 'GET':
        # Carrega todos os treinamentos para exibir na interface
        treinamentos = Treinamentos.objects.all().order_by('-id')
        return render(request, 'treinar_ia.html', {'treinamentos': treinamentos})
        
    elif request.method == 'POST':
        # Processa dados do formulário
        site = request.POST.get('site')
        conteudo = request.POST.get('conteudo')
        documento = request.FILES.get('documento')

        # Cria novo registro de treinamento
        treinamento = Treinamentos(
            site=site,
            conteudo=conteudo,
            documento=documento
        )
        treinamento.save()
        
        # O signal será disparado automaticamente para processar o treinamento

        return redirect('treinar_ia')


@csrf_exempt
def chat(request):
    """
    View para página de chat com a IA.
    
    Args:
        request: Objeto de requisição HTTP
    
    Returns:
        Renderiza o template de chat ou retorna o ID da pergunta salva
    """
    if request.method == 'GET':
        return render(request, 'chat.html')
    elif request.method == 'POST':
        # Obtém a pergunta do usuário
        pergunta_user = request.POST.get('pergunta')
        
        print(f"Recebida pergunta: {pergunta_user}")

        # Salva a pergunta no banco
        try:
            pergunta = Pergunta(
                pergunta=pergunta_user
            )
            pergunta.save()
            print(f"Pergunta salva com ID {pergunta.id}")
            
            # Retorna o ID para ser usado pelo frontend no streaming
            return JsonResponse({'id': pergunta.id})
        except Exception as e:
            print(f"Erro ao salvar pergunta: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
def stream_response(request):
    """
    View para streaming de respostas da IA.
    Processa a pergunta e retorna a resposta em tempo real.
    
    Args:
        request: Objeto de requisição HTTP
    
    Returns:
        Streaming da resposta da IA
    """
    id_pergunta = request.POST.get('id_pergunta')
    
    try:
        pergunta = Pergunta.objects.get(id=id_pergunta)
        print(f"Encontrou pergunta com ID {id_pergunta}")
    except Pergunta.DoesNotExist:
        # Se a pergunta não existir, retorna uma mensagem de erro
        print(f"Erro: Pergunta com ID {id_pergunta} não encontrada")
        return StreamingHttpResponse(("Erro: Pergunta não encontrada. Por favor, tente novamente."), 
                                   content_type='text/plain; charset=utf-8')
    
    def stream_generator():
        try:
            # Inicializa o modelo de embeddings
            print(f"Inicializando embeddings com API key: {settings.OPENAI_API_KEY[:10]}...")
            embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
            
            # Carrega a base de vetores
            db_path = str(settings.BASE_DIR / "banco_faiss")
            print(f"Tentando carregar banco FAISS de: {db_path}")
            vectordb = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
            print("Banco FAISS carregado com sucesso")

            # Busca documentos similares à pergunta
            print(f"Buscando documentos similares para: {pergunta.pergunta}")
            docs = vectordb.similarity_search(pergunta.pergunta, k=5)
            print(f"Encontrados {len(docs)} documentos similares")
            
            # Salva os documentos relacionados à pergunta
            for doc in docs:
                dt = DataTreinamento.objects.create(
                    metadata=doc.metadata,
                    texto=doc.page_content
                )
                pergunta.data_treinamento.add(dt)
            print("Documentos salvos no banco de dados")

            # Cria o contexto para o modelo de IA
            contexto = "\n\n".join([
                f"Material: {Path(doc.metadata.get('source', 'Desconhecido')).name}\n{doc.page_content}"
                for doc in docs
            ])

            # Prepara as mensagens para o modelo
            messages = [
                {"role": "system", "content": f"Você é um assistente virtual e deve responder com precisão as perguntas sobre uma empresa.\n\n{contexto}"},
                {"role": "user", "content": pergunta.pergunta}
            ]
            print("Mensagens preparadas para o chat")

            # Inicializa o modelo de linguagem
            llm = ChatOpenAI(
                model_name="gpt-3.5-turbo",
                streaming=True,
                temperature=0,
                openai_api_key=settings.OPENAI_API_KEY
            )
            print("Modelo de linguagem inicializado")

            # Gera a resposta em streaming
            print("Iniciando streaming da resposta...")
            for chunk in llm.stream(messages):
                token = chunk.content
                if token:
                    yield token
                    
        except Exception as e:
            print(f"Erro no stream_generator: {str(e)}")
            # Yield erro como parte da resposta para o usuário ver
            yield f"Erro ao processar sua pergunta: {str(e)}. Por favor, tente novamente mais tarde."

    # Retorna um streaming HTTP response
    return StreamingHttpResponse(stream_generator(), content_type='text/plain; charset=utf-8')

def ver_fontes(request, id):
    """
    View para exibir as fontes de uma resposta.
    
    Args:
        request: Objeto de requisição HTTP
        id: ID da pergunta
    
    Returns:
        Renderiza o template com as fontes da resposta
    """
    pergunta = Pergunta.objects.get(id=id)
    return render(request, 'ver_fontes.html', {'pergunta': pergunta})

def whatsapp_config(request):
    """
    View para configuração da integração com WhatsApp.
    
    Args:
        request: Objeto de requisição HTTP
    
    Returns:
        Renderiza o template de configuração
    """
    from .models import WhatsAppConfig
    from django.contrib import messages
    
    # Verifica permissões
    if not has_permission(request.user, 'admin'):
        raise Http404()
    
    # Obtém ou cria configuração
    config, created = WhatsAppConfig.objects.get_or_create(
        pk=1,
        defaults={
            'instance_name': 'arcane',
            'api_url': '',
            'api_key': '',
            'is_active': False,
            'welcome_message': 'Olá! Eu sou Dani AI, seu assistente virtual. Como posso ajudar você hoje?'
        }
    )
    
    if request.method == 'POST':
        # Atualiza configuração
        config.instance_name = request.POST.get('instance_name', 'arcane')
        config.api_url = request.POST.get('api_url', '')
        config.api_key = request.POST.get('api_key', '')
        config.is_active = request.POST.get('is_active') == 'on'
        config.welcome_message = request.POST.get('welcome_message', '')
        config.save()
        
        # Atualiza variáveis de ambiente dinâmicas
        settings.EVOLUTION_API_BASE_URL = config.api_url
        settings.EVOLUTION_API_KEY = config.api_key
        
        messages.success(request, "Configurações do WhatsApp atualizadas com sucesso!")
    
    return render(request, 'whatsapp_config.html', {
        'config': config,
    })

@csrf_exempt
def whatsapp_status(request):
    """
    View para verificar o status da conexão com WhatsApp.
    
    Args:
        request: Objeto de requisição HTTP
    
    Returns:
        JSON com o status da conexão
    """
    from .models import WhatsAppConfig
    from .wrapper_evolutionapi import WhatsAppAPI
    
    # Verifica permissões
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Não autorizado'}, status=401)
    
    config = WhatsAppConfig.get_active()
    if not config:
        return JsonResponse({
            'connected': False,
            'message': 'Integração com WhatsApp não está ativa'
        })
    
    try:
        settings.EVOLUTION_API_BASE_URL = config.api_url
        settings.EVOLUTION_API_KEY = config.api_key
        
        api = WhatsAppAPI()
        response = api.get_instance_status(config.instance_name)
        
        if response.ok:
            data = response.json()
            if data.get('state') == 'open':
                return JsonResponse({
                    'connected': True,
                    'id': data.get('id', ''),
                    'pushName': data.get('pushName', '')
                })
            else:
                return JsonResponse({
                    'connected': False,
                    'message': 'WhatsApp não está conectado',
                    'state': data.get('state', '')
                })
        else:
            return JsonResponse({
                'connected': False,
                'message': f'Erro ao verificar status: {response.text}'
            })
    
    except Exception as e:
        return JsonResponse({
            'connected': False,
            'message': f'Erro: {str(e)}'
        })

@csrf_exempt
def whatsapp_qrcode(request):
    """
    View para gerar QR code para conexão com WhatsApp.
    
    Args:
        request: Objeto de requisição HTTP
    
    Returns:
        JSON com o QR code
    """
    from .models import WhatsAppConfig
    from .wrapper_evolutionapi import WhatsAppAPI
    
    # Verifica permissões
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Não autorizado'}, status=401)
    
    config = WhatsAppConfig.get_active()
    if not config:
        return JsonResponse({
            'error': 'Integração com WhatsApp não está ativa'
        }, status=400)
    
    try:
        settings.EVOLUTION_API_BASE_URL = config.api_url
        settings.EVOLUTION_API_KEY = config.api_key
        
        api = WhatsAppAPI()
        response = api.generate_qr_code(config.instance_name)
        
        if response.ok:
            data = response.json()
            return JsonResponse({
                'success': True,
                'qrcode': data.get('qrcode', '')
            })
        else:
            return JsonResponse({
                'error': f'Erro ao gerar QR code: {response.text}'
            }, status=500)
    
    except Exception as e:
        return JsonResponse({
            'error': f'Erro: {str(e)}'
        }, status=500)

@csrf_exempt
def whatsapp_disconnect(request):
    """
    View para desconectar o WhatsApp.
    
    Args:
        request: Objeto de requisição HTTP
    
    Returns:
        JSON com o resultado da operação
    """
    from .models import WhatsAppConfig
    from .wrapper_evolutionapi import WhatsAppAPI
    
    # Verifica permissões
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Não autorizado'}, status=401)
    
    config = WhatsAppConfig.get_active()
    if not config:
        return JsonResponse({
            'error': 'Integração com WhatsApp não está ativa'
        }, status=400)
    
    try:
        settings.EVOLUTION_API_BASE_URL = config.api_url
        settings.EVOLUTION_API_KEY = config.api_key
        
        api = WhatsAppAPI()
        response = api.disconnect_whatsapp(config.instance_name)
        
        if response.ok:
            return JsonResponse({
                'success': True,
                'message': 'WhatsApp desconectado com sucesso'
            })
        else:
            return JsonResponse({
                'error': f'Erro ao desconectar WhatsApp: {response.text}'
            }, status=500)
    
    except Exception as e:
        return JsonResponse({
            'error': f'Erro: {str(e)}'
        }, status=500)

@csrf_exempt
def webhook_whatsapp(request):
    """
    Webhook para receber mensagens do WhatsApp.
    
    Args:
        request: Objeto de requisição HTTP
    
    Returns:
        HTTP 200 OK
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'Method not allowed'}, status=405)
        
    # Verifica se a integração está ativa
    from .models import WhatsAppConfig
    config = WhatsAppConfig.get_active()
    if not config:
        return JsonResponse({'status': 'WhatsApp integration not active'}, status=400)
        
    # Processa os dados recebidos
    import json
    try:
        data = json.loads(request.body)
        
        # Log para debugging
        print(f"Webhook recebido: {data}")
        
        # Verifica se é uma mensagem de texto
        if data.get('event') == 'messages.upsert':
            message_data = data.get('data', {})
            
            # Extrai informações da mensagem
            messages = message_data.get('messages', [])
            if messages:
                message = messages[0]
                message_type = message.get('type')
                
                # Processa apenas mensagens de texto
                if message_type == 'conversation' or message_type == 'extendedTextMessage':
                    # Obtém texto da mensagem
                    message_text = message.get('conversation', message.get('extendedTextMessage', {}).get('text', ''))
                    
                    # Obtém número do remetente
                    sender = message.get('key', {}).get('remoteJid', '').split('@')[0]
                    
                    # Obtém ID da mensagem para resposta
                    message_id = message.get('key', {}).get('id')
                    
                    # Inicia processamento assíncrono da resposta
                    sched_message_response(
                        instance=config.instance_name, 
                        sender=sender, 
                        message=message_text, 
                        message_id=message_id
                    )
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        print(f"Erro no webhook: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
