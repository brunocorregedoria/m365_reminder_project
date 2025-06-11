#!/bin/bash

echo "🚀 Iniciando trabalho no projeto M365 Reminder..."

# Ativar ambiente virtual
echo "📦 Ativando ambiente virtual..."
source .venv/bin/activate

# Verificar branch atual
current_branch=$(git branch --show-current)
echo "🌿 Branch atual: $current_branch"

# Atualizar repositório local
echo "🔄 Atualizando repositório local..."
git pull origin $current_branch

# Mostrar status do Git
echo "📊 Status do repositório:"
git status

# Mostrar últimas 3 mensagens de commit
echo "📝 Últimos commits:"
git log -3 --oneline

# Verificar se há dependências desatualizadas
echo "🔍 Verificando dependências..."
pip list --outdated

echo "✅ Ambiente preparado e repositório atualizado. Pronto para começar a trabalhar!"
echo "💡 Lembre-se: use 'scripts/end_work.sh' para encerrar o trabalho"
