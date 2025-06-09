"""
Signals para o processamento assíncrono de tarefas do oráculo.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Treinamentos
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import os
import threading
from django.conf import settings
from .utils import gerar_documentos

@receiver(post_save, sender=Treinamentos)
def signals_treinamento_ia(sender, instance, created, **kwargs):
    """
    Signal que dispara quando um novo treinamento é criado.
    Inicia uma tarefa em thread para processar o treinamento da IA.
    
    Args:
        sender: Classe do modelo que disparou o signal
        instance: Instância do modelo que foi salva
        created: Indica se é uma nova instância
    """
    if created:
        # Cria uma thread para processar o treinamento em segundo plano
        thread = threading.Thread(target=task_treinar_ia, args=(instance.id,))
        thread.daemon = True
        thread.start()
        print(f"Treinamento #{instance.id} enfileirado para processamento")

def task_treinar_ia(instance_id):
    """
    Tarefa para treinar a IA com os documentos da instância.
    Esta função processa os documentos e atualiza a base de vetores.
    
    Args:
        instance_id: ID da instância de treinamento
    """
    # Recupera a instância do banco de dados
    instance = Treinamentos.objects.get(id=instance_id)
    
    # Gera documentos a partir dos dados do treinamento
    documentos = gerar_documentos(instance)
    if not documentos:
        print(f"Nenhum documento gerado para treinamento #{instance_id}")
        return

    # Divide os documentos em chunks menores para melhor processamento
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(documentos)
    print(f"Gerados {len(chunks)} chunks para processamento")
    
    # Inicializa o modelo de embeddings
    embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
    
    # Caminho para salvar a base de vetores
    db_path = settings.BASE_DIR / "banco_faiss"
    
    # Verifica se já existe uma base de vetores
    if (db_path / "index.faiss").exists():
        # Carrega a base existente e adiciona novos documentos
        vectordb = FAISS.load_local(str(db_path), embeddings, allow_dangerous_deserialization=True)
        vectordb.add_documents(chunks)
        print(f"Base de vetores atualizada com {len(chunks)} novos chunks")
    else:
        # Cria uma nova base de vetores
        vectordb = FAISS.from_documents(chunks, embeddings)
        print(f"Nova base de vetores criada com {len(chunks)} chunks")
    
    # Salva a base de vetores atualizada
    vectordb.save_local(str(db_path))
    print(f"Base de vetores salva em {db_path}")
    
    # Marca o treinamento como concluído
    instance.save()
