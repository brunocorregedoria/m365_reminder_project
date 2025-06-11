#!/bin/bash

echo "🏁 Encerrando trabalho no projeto M365 Reminder..."

# Ativar ambiente virtual
source .venv/bin/activate

# Executar testes antes de finalizar
echo "🧪 Executando testes finais..."
python -m pytest tests/ -v --tb=short

# Verificar formatação do código
echo "🎨 Verificando formatação do código..."
python -m black --check .

if [ $? -ne 0 ]; then
    echo "⚠️  Código precisa ser formatado. Formatando automaticamente..."
    python -m black .
fi

# Verificar status do Git
status=$(git status --porcelain)

if [ -z "$status" ]; then
    echo "✅ Nenhuma alteração para commitar."
else
    echo "📝 Alterações detectadas. Preparando para commit..."
    git add .
    
    echo "Arquivos alterados:"
    git status --short
    
    read -p "Digite a mensagem do commit: " commit_message
    
    if [ -n "$commit_message" ]; then
        git commit -m "$commit_message"
    else
        echo "❌ Commit cancelado - mensagem vazia"
        exit 1
    fi
fi

# Enviar alterações para o repositório remoto
current_branch=$(git branch --show-current)
echo "🚀 Enviando alterações para a branch $current_branch..."
git push origin $current_branch

# Atualizar requirements.txt se necessário
echo "📋 Atualizando requirements.txt..."
pip freeze > requirements.txt

# Verificar se requirements.txt foi alterado
if ! git diff --quiet requirements.txt; then
    echo "📦 Dependências atualizadas. Commitando requirements.txt..."
    git add requirements.txt
    git commit -m "chore: update requirements.txt"
    git push origin $current_branch
fi

echo "✅ Trabalho encerrado e repositório atualizado."
echo "📊 Resumo da sessão:"
git log -1 --oneline
