#!/bin/bash

echo "🔧 Configurando ambiente de desenvolvimento..."

# Criar ambiente virtual se não existir
if [ ! -d ".venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv .venv
fi

# Ativar ambiente virtual
source .venv/bin/activate

# Instalar dependências
echo "📥 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# Instalar ferramentas de desenvolvimento
pip install pytest black flake8

# Configurar Git hooks
echo "🔗 Configurando Git hooks..."
chmod +x .git/hooks/pre-commit

echo "✅ Ambiente configurado com sucesso!"
echo "💡 Use 'start-m365' para iniciar o trabalho"
