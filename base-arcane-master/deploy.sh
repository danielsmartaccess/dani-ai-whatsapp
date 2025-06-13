#!/bin/bash

echo "Iniciando deploy do sistema Oráculo AI..."

# Atualizar código do repositório
echo "Atualizando código do repositório..."
git pull

# Atualizar dependências
echo "Atualizando dependências..."
pip install -r requirements.txt

# Aplicar migrações do banco de dados
echo "Aplicando migrações do banco de dados..."
python manage.py migrate

# Coletar arquivos estáticos
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Reiniciar serviço (usando supervisor ou systemd)
echo "Reiniciando serviço..."
# systemctl restart oraculo_ai  # Descomente para usar systemd
# supervisorctl restart oraculo_ai  # Descomente para usar supervisor

echo "Deploy concluído com sucesso!"
