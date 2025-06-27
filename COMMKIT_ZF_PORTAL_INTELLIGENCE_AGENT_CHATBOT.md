# COMMKIT — ZF Portal Intelligence Agent — Chatbot Inteligente

## 1. Resumo Executivo

O módulo de Chatbot Inteligente do ZF Portal Intelligence Agent automatiza o atendimento, qualificação de leads e suporte via web e WhatsApp, utilizando IA generativa (OpenAI) e integração com documentos e campanhas. O sistema está funcional, sem autenticação obrigatória, e pronto para integração final com WhatsApp e expansão de funcionalidades.

## 2. Principais Funcionalidades

- Chatbot com IA (OpenAI GPT-3.5/4o) para atendimento e dúvidas
- Treinamento customizado via upload de documentos, textos e links
- Interface web para treinamento, chat, campanhas e importação de contatos
- Estrutura para campanhas, funil de marketing e dashboard
- Integração WhatsApp pronta (aguardando autenticação)

## 3. Tecnologias Utilizadas

- **Backend:** Python 3.11+, Django 5.x
- **IA/ML:** OpenAI GPT-3.5/4o, LangChain
- **Banco de Dados:** SQLite (dev), PostgreSQL (prod)
- **Interface Web:** Django Templates, HTML5, TailwindCSS
- **Integração WhatsApp:** Webhook, API REST
- **Containerização:** Docker (opcional)

## 4. Status Atual (27/06/2025)

- Aplicação rodando em http://localhost:8000/
- Todas as páginas principais acessíveis sem login
- Upload, chat, dashboard e importação de contatos funcionais
- Integração WhatsApp pronta para testes finais

## 5. Como Executar

1. Clone o repositório e acesse a pasta do projeto
2. Crie e ative um ambiente virtual:

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Execute as migrações:

   ```bash
   python manage.py migrate
   ```

5. Inicie o servidor:

   ```bash
   python manage.py runserver
   ```

6. (Opcional) Inicie o worker do Celery:

   ```bash
   celery -A core worker --loglevel=info
   ```

7. Acesse http://localhost:8000/ no navegador

## 6. Próximos Passos

- Finalizar autenticação e testes do canal WhatsApp
- Implementar analytics e métricas de uso
- Otimizar prompts e personalização das respostas
- Testes de carga e performance

## 7. Contato

Para dúvidas técnicas ou sugestões, entre em contato com a equipe de desenvolvimento.
