"""
Script para criar dados de teste para o sistema de campanhas
"""
import os
import django
import datetime
from django.utils import timezone
from datetime import timedelta

# Configura o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Importa os modelos após configurar o Django
from oraculo.models import Campanha, SequenciaMensagem, Contato, EstagioFunil

# Cria uma campanha de teste
campanha = Campanha.objects.create(
    nome="Campanha de Boas-vindas",
    descricao="Sequência automática de boas-vindas para novos contatos",
    data_inicio=timezone.now(),
    status="ativa"
)

print(f"Campanha criada: {campanha.nome}")

# Cria uma sequência de mensagens
mensagem1 = SequenciaMensagem.objects.create(
    campanha=campanha,
    ordem=1,
    conteudo="Olá {{nome}}! Seja bem-vindo(a) ao nosso grupo. Estamos felizes em ter você conosco!",
    atraso=timedelta(minutes=1)
)

mensagem2 = SequenciaMensagem.objects.create(
    campanha=campanha,
    ordem=2,
    conteudo="{{nome}}, como podemos te ajudar hoje? Temos vários serviços disponíveis para você.",
    atraso=timedelta(hours=2)
)

mensagem3 = SequenciaMensagem.objects.create(
    campanha=campanha,
    ordem=3,
    conteudo="Aproveite este cupom especial de boas-vindas: BEMVINDO10. Válido por 7 dias!",
    atraso=timedelta(days=1)
)

print(f"Criadas {SequenciaMensagem.objects.filter(campanha=campanha).count()} mensagens para a campanha")

# Cria alguns estágios do funil
estagio1, _ = EstagioFunil.objects.get_or_create(nome="Novo Lead", ordem=1)
estagio2, _ = EstagioFunil.objects.get_or_create(nome="Qualificado", ordem=2)
estagio3, _ = EstagioFunil.objects.get_or_create(nome="Cliente", ordem=3)

print("Estágios do funil criados")

# Cria alguns contatos de teste
contatos_teste = [
    {"nome": "Maria Silva", "telefone": "11999887766", "estagio": estagio1},
    {"nome": "João Santos", "telefone": "21988776655", "estagio": estagio2},
    {"nome": "Ana Oliveira", "telefone": "31977665544", "estagio": estagio1},
    {"nome": "Carlos Pereira", "telefone": "41966554433", "estagio": estagio3}
]

for dados in contatos_teste:
    contato, criado = Contato.objects.get_or_create(
        telefone=dados["telefone"],
        defaults={
            "nome": dados["nome"],
            "estagio_funil": dados["estagio"],
            "status": "ativo"
        }
    )
    if criado:
        print(f"Contato criado: {contato.nome}")
    else:
        print(f"Contato já existe: {contato.nome}")

# Cria uma segunda campanha
campanha2 = Campanha.objects.create(
    nome="Campanha de Reengajamento",
    descricao="Para clientes inativos há mais de 30 dias",
    data_inicio=timezone.now() - timedelta(days=5),
    status="ativa"
)

print(f"Campanha criada: {campanha2.nome}")

# Adiciona sequência para a segunda campanha
mensagem1 = SequenciaMensagem.objects.create(
    campanha=campanha2,
    ordem=1,
    conteudo="Olá {{nome}}! Sentimos sua falta! Gostaria de conhecer nossas novidades?",
    atraso=timedelta(minutes=30)
)

mensagem2 = SequenciaMensagem.objects.create(
    campanha=campanha2,
    ordem=2,
    conteudo="{{nome}}, preparamos uma oferta especial só para você! Responda esta mensagem para saber mais.",
    atraso=timedelta(hours=24)
)

print("Dados de teste criados com sucesso!")
