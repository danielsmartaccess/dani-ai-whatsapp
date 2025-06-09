from langchain.docstore.document import Document
from typing import List
from langchain_community.document_loaders import PyPDFLoader
import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
from django.core.cache import cache
import datetime
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from django.conf import settings
from pathlib import Path

# Inicialização do scheduler para tarefas em background
scheduler = BackgroundScheduler()
scheduler.start()

def html_para_texto_rag(html_str: str) -> str:
    """
    Converte HTML em texto estruturado para ser usado no RAG.
    
    Args:
        html_str: String contendo o HTML da página
        
    Returns:
        Texto limpo e formatado para o RAG
    """
    soup = BeautifulSoup(html_str, "html.parser")
    texto_final = []

    # Extrair texto de tags relevantes
    for tag in soup.find_all(["h1", "h2", "h3", "p", "li"]):
        texto = tag.get_text(strip=True)

        if not texto:
            continue

        # Formatar diferentemente de acordo com o tipo de elemento
        if tag.name in ["h1", "h2", "h3"]:
            texto_formatado = f"\n\n### {texto.upper()}"
        elif tag.name == "li":
            texto_formatado = f" - {texto}"
        else:
            texto_formatado = texto

        texto_final.append(texto_formatado)
        
    return "\n".join(texto_final).strip()

def gerar_documentos(instance) -> List[Document]:
    """
    Gera documentos para processamento pela IA a partir dos dados fornecidos.
    
    Args:
        instance: Instância de treinamento contendo documento, conteúdo ou URL
        
    Returns:
        Lista de documentos processados prontos para embeddings
    """
    documentos = []
    # Processamento de documentos (PDFs)
    if instance.documento:
        extensao = instance.documento.name.split('.')[-1].lower()
        if extensao == 'pdf':
            loader = PyPDFLoader(instance.documento.path)
            pdf_doc = loader.load()
            for doc in pdf_doc:
                doc.metadata['url'] = instance.documento.url
            documentos += pdf_doc
            
    # Processamento de texto direto
    if instance.conteudo:
        documentos.append(Document(page_content=instance.conteudo))
        
    # Processamento de sites/URLs
    if instance.site:
        site_url = instance.site if instance.site.startswith('https://') else f'https://{instance.site}'
        try:
            content = requests.get(site_url, timeout=10).text
            content = html_para_texto_rag(content)
            documentos.append(Document(page_content=content))
        except Exception as e:
            print(f"Erro ao processar site {site_url}: {str(e)}")

    return documentos

# Funções para integração com WhatsApp
class BaseEvolutionAPI:
    """
    Classe base para interação com a Evolution API.
    Gerencia requisições HTTP para a API do WhatsApp.
    """
    def __init__(self):
        # Tenta obter configuração do banco de dados
        from .models import WhatsAppConfig
        
        config = WhatsAppConfig.get_active()
        
        if config:
            self._BASE_URL = config.api_url
            self._API_KEY = {config.instance_name: config.api_key}
            self._INSTANCE_NAME = config.instance_name
            self._WELCOME_MESSAGE = config.welcome_message
        else:
            # Configuração de fallback das settings
            self._BASE_URL = settings.EVOLUTION_API_URL if hasattr(settings, 'EVOLUTION_API_URL') else 'https://evolution-api.your-domain.com'
            self._API_KEY = settings.EVOLUTION_API_KEYS if hasattr(settings, 'EVOLUTION_API_KEYS') else {
                'arcane': 'sua_api_key_aqui'  # Chave de API para o instance 'arcane'
            }
            self._INSTANCE_NAME = 'arcane'
            self._WELCOME_MESSAGE = 'Olá! Eu sou Dani AI, seu assistente virtual. Como posso ajudar você hoje?'

    def _send_request(
        self,
        path,
        method='GET',
        body=None,
        headers={},
        params_url={}
    ):
        """
        Envia uma requisição para a Evolution API.
        
        Args:
            path: Caminho da API
            method: Método HTTP
            body: Corpo da requisição
            headers: Cabeçalhos HTTP
            params_url: Parâmetros de URL
            
        Returns:
            Resposta da requisição
        """
        method = method.upper()
        url = self._mount_url(path, params_url)

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
        """
        Monta a URL completa para a requisição.
        
        Args:
            path: Caminho da API
            params_url: Parâmetros de URL
            
        Returns:
            URL completa
        """
        parameters = ''
        if isinstance(params_url, dict) and params_url:
            from urllib.parse import urlencode
            parameters = urlencode(params_url)

        from urllib.parse import urljoin
        url = urljoin(self._BASE_URL, path)
        
        if parameters:
            url = url + '?' + parameters

        return url
    
    def _get_instance(self, path):
        """
        Extrai o nome da instância do caminho da API.
        
        Args:
            path: Caminho da API
            
        Returns:
            Nome da instância
        """
        return path.strip('/').split('/')[-1]
    

class SendMessage(BaseEvolutionAPI):
    """
    Classe para enviar mensagens via WhatsApp usando a Evolution API.
    """
    def send_message(self, body, instance=None):
        """
        Envia uma mensagem para um contato no WhatsApp.
        
        Args:
            body: Corpo da requisição com número e mensagem
            instance: Nome da instância (opcional, usa a configurada por padrão)
            
        Returns:
            Resposta da API
        """
        instance = instance or self._INSTANCE_NAME
        path = f'/message/sendText/{instance}/'
        
        try:
            response = self._send_request(path, method='POST', body=body)
            response.raise_for_status()  # Levanta exceção para códigos de erro HTTP
            return response.json()
        except Exception as e:
            import traceback
            print(f"Erro ao enviar mensagem WhatsApp: {str(e)}")
            print(traceback.format_exc())
            return {"error": str(e)}
            
    def send_welcome_message(self, phone_number, instance=None):
        """
        Envia uma mensagem de boas-vindas para um novo contato.
        
        Args:
            phone_number: Número de telefone do contato
            instance: Nome da instância (opcional)
            
        Returns:
            Resposta da API
        """
        body = {
            "number": phone_number,
            "textMessage": {"text": self._WELCOME_MESSAGE}
        }
        return self.send_message(body, instance)


def send_message_response(phone):
    """
    Envia resposta para o WhatsApp do usuário usando IA.
    
    Args:
        phone: Número de telefone do usuário
    """
    try:
        messages = cache.get(f"wa_buffer_{phone}", [])
        if messages:
            question = "\n".join(messages)
            response = ""
            
            try:
                # Inicializa embeddings
                embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
                
                # Verifica se o banco FAISS existe
                db_path = settings.BASE_DIR / "banco_faiss"
                if not db_path.exists() or not (db_path / "index.faiss").exists():
                    response = "Desculpe, ainda não tenho informações suficientes para responder sua pergunta. Por favor, aguarde o treinamento do sistema."
                else:
                    # Carrega a base de vetores
                    vectordb = FAISS.load_local(str(db_path), embeddings, allow_dangerous_deserialization=True)
                    docs = vectordb.similarity_search(question, k=5)
                    
                    if not docs:
                        response = "Não encontrei informações suficientes para responder sua pergunta com precisão. Tente reformular ou contatar o suporte."
                    else:
                        # Prepara o contexto e gera resposta
                        context = "\n\n".join([doc.page_content for doc in docs])
                        chat_messages = [
                            {"role": "system", "content": f"Você é um assistente virtual e deve responder com precisão as perguntas sobre uma empresa.\n\n{context}"},
                            {"role": "user", "content": question}
                        ]
                        
                        llm = ChatOpenAI(
                            model_name="gpt-3.5-turbo",
                            temperature=0,
                            openai_api_key=settings.OPENAI_API_KEY
                        )
                        
                        response = llm.invoke(chat_messages).content
            
            except Exception as e:
                import traceback
                response = f"Desculpe, ocorreu um erro ao processar sua pergunta. Por favor, tente novamente mais tarde."
                print(f"Erro ao processar pergunta do WhatsApp: {str(e)}")
                print(traceback.format_exc())
            
            # Envia a resposta para o WhatsApp
            try:
                SendMessage().send_message('arcane', {
                    "number": phone,
                    "textMessage": {"text": response}
                })
            except Exception as e:
                print(f"Erro ao enviar mensagem via WhatsApp: {str(e)}")
    
    except Exception as e:
        print(f"Erro geral em send_message_response: {str(e)}")
    finally:
        # Limpa o cache após enviar a resposta
        cache.delete(f"wa_buffer_{phone}")
        cache.delete(f"wa_timer_{phone}")

def sched_message_response(instance, sender, message, message_id=None):
    """
    Agenda o processamento e envio de resposta via WhatsApp.
    Aguarda alguns segundos para acumular mensagens do usuário e evitar processamento desnecessário.
    
    Args:
        instance: Nome da instância do WhatsApp na Evolution API
        sender: Número de telefone do remetente
        message: Texto da mensagem recebida
        message_id: ID da mensagem original (opcional, para resposta direta)
    """
    # Guarda a mensagem em cache para processamento posterior
    mensagens_anteriores = cache.get(f"wa_msgs_{sender}", [])
    mensagens_anteriores.append(message)
    cache.set(f"wa_msgs_{sender}", mensagens_anteriores, timeout=3600)  # Guarda por 1 hora
    
    # Verifica se já existe um job agendado para este remetente
    if not cache.get(f"wa_timer_{sender}"):
        # Agenda o processamento para daqui a 5 segundos
        scheduler.add_job(
            send_message_response,
            'date',
            run_date=datetime.datetime.now() + datetime.timedelta(seconds=5),
            kwargs={
                "instance": instance,
                "sender": sender,
                "message_id": message_id
            },
            misfire_grace_time=60
        )
        cache.set(f"wa_timer_{sender}", True, timeout=60)

def send_message_response(instance, sender, message_id=None):
    """
    Processa a mensagem do WhatsApp e envia resposta.
    Usa o RAG para gerar respostas baseadas nos documentos treinados.
    
    Args:
        instance: Nome da instância do WhatsApp na Evolution API
        sender: Número de telefone do remetente
        message_id: ID da mensagem original (opcional, para resposta direta)
    """
    from .models import WhatsAppConfig, Pergunta, DataTreinamento
    from .wrapper_evolutionapi import WhatsAppAPI
    
    try:
        # Remove o timer do cache
        cache.delete(f"wa_timer_{sender}")
        
        # Recupera as mensagens acumuladas
        mensagens = cache.get(f"wa_msgs_{sender}", [])
        if not mensagens:
            return
            
        # Limpa as mensagens do cache
        cache.delete(f"wa_msgs_{sender}")
        
        # Concatena todas as mensagens em uma única
        pergunta_completa = "\n".join(mensagens)
        
        # Salva a pergunta no banco
        pergunta = Pergunta(
            pergunta=pergunta_completa
        )
        pergunta.save()
        
        # Inicializa o modelo de embeddings
        print(f"Inicializando embeddings para resposta WhatsApp...")
        embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        
        # Carrega a base de vetores
        db_path = str(settings.BASE_DIR / "banco_faiss")
        vectordb = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
        
        # Busca documentos similares à pergunta
        docs = vectordb.similarity_search(pergunta_completa, k=5)
        
        # Salva os documentos relacionados à pergunta
        for doc in docs:
            dt = DataTreinamento.objects.create(
                metadata=doc.metadata,
                texto=doc.page_content
            )
            pergunta.data_treinamento.add(dt)
        
        # Se não encontrou documentos relevantes
        if not docs:
            # Obtém configuração ativa
            config = WhatsAppConfig.get_active()
            api = WhatsAppAPI()
            
            # Envia mensagem de erro
            resposta = "Desculpe, não encontrei informações suficientes para responder sua pergunta."
            
            # Envia mensagem com ou sem resposta direta
            if message_id:
                api.send_reply(instance, sender, resposta, message_id)
            else:
                api.send_text_message(instance, sender, resposta)
                
            return
        
        # Cria o contexto para o modelo de IA
        contexto = "\n\n".join([
            f"Material: {Path(doc.metadata.get('source', 'Desconhecido')).name}\n{doc.page_content}"
            for doc in docs
        ])

        # Prepara as mensagens para o modelo
        messages = [
            {"role": "system", "content": f"Você é Dani AI, um assistente virtual e deve responder com precisão as perguntas sobre uma empresa.\n\n{contexto}"},
            {"role": "user", "content": pergunta_completa}
        ]

        # Inicializa o modelo de linguagem
        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Gera a resposta
        response = llm.invoke(messages)
        resposta = response.content
        
        # Obtém configuração ativa do WhatsApp
        config = WhatsAppConfig.get_active()
        api = WhatsAppAPI()
        
        # Envia resposta via WhatsApp
        if message_id:
            api.send_reply(instance, sender, resposta, message_id)
        else:
            api.send_text_message(instance, sender, resposta)
            
    except Exception as e:
        print(f"Erro ao processar mensagem do WhatsApp: {str(e)}")
        
        # Em caso de erro, tenta enviar uma mensagem de erro ao usuário
        try:
            api = WhatsAppAPI()
            api.send_text_message(
                instance, 
                sender, 
                "Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente mais tarde."
            )
        except:
            pass