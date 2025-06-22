# Oráculo AI - Sistema de Chat com RAG

Sistema de chat com RAG (Retrieval-Augmented Generation) que permite treinar uma IA com documentos, sites e textos para responder perguntas específicas sobre o conteúdo fornecido.

## Funcionalidades

- **Processamento de dados**: Upload de PDFs, URLs e texto para treinamento da IA
- **Chat inteligente**: Interface para fazer perguntas e receber respostas baseadas nos dados fornecidos
- **Visualização de fontes**: Verificação das fontes usadas pela IA para responder cada pergunta
- **Integração com WhatsApp**: Possibilidade de interagir via WhatsApp (Evolution API)

## Requisitos

- Python 3.10+
- Django 5.2+
- OpenAI API Key
- Evolution API (para integração com WhatsApp)
- Redis (para gerenciamento de filas com Celery)

## Instalação

1. Clone o repositório
2. Crie um arquivo `.env` na raiz do projeto com base no arquivo `.env.example`
3. Configure suas credenciais de API no arquivo `.env`:
   ```
   OPENAI_API_KEY=sua_chave_da_api_openai
   EVOLUTION_API_BASE_URL=url_da_sua_api_evolution
   EVOLUTION_API_KEY=sua_chave_da_api_evolution
   REDIS_URL=redis://localhost:6379/0
   ```
```bash
git clone https://github.com/seu-usuario/base-arcane.git
cd base-arcane
```

2. Crie e ative um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

3. Instale as dependências
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. Execute as migrações
```bash
python manage.py migrate
```

6. Crie um superusuário
```bash
python manage.py createsuperuser
```

7. Inicie o servidor
```bash
python manage.py runserver
```

8. (Opcional) Inicie o worker do Celery em um terminal separado
```bash
celery -A seu_projeto worker --loglevel=info
```

## Uso

1. Acesse o admin em `http://localhost:8000/admin/` e faça login
2. Vá para `http://localhost:8000/oraculo/treinar_ia` para adicionar documentos para treinamento
3. Acesse `http://localhost:8000/oraculo/chat` para interagir com a IA

## Integração com WhatsApp

1. Configure a Evolution API seguindo a [documentação oficial](https://github.com/evolution-api/evolution-api)
2. Configure as variáveis de ambiente relacionadas à Evolution API no arquivo `.env`
3. A rota do webhook é `http://seu-dominio.com/oraculo/webhook_whatsapp`

## Produção

Para ambientes de produção, recomenda-se:

1. Usar um servidor web como Nginx ou Apache
2. Configurar gunicorn ou uWSGI como servidor WSGI
3. Configurar um certificado SSL
4. Usar um banco de dados como PostgreSQL em vez de SQLite
5. Executar o deploy com o script `deploy.sh`
6. Configurar o Celery para produção, utilizando um broker como Redis ou RabbitMQ
7. Garantir que as variáveis de ambiente estejam corretamente configuradas no servidor de produção

## Licença

Este projeto está sob a licença [MIT](LICENSE).
