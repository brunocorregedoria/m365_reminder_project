#!/bin/bash
# scripts/release.sh

set -e

# Verifica se está na branch main
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    echo "Erro: Execute o release apenas na branch main"
    exit 1
fi

# Verifica se há mudanças não commitadas
if [ -n "$(git status --porcelain)" ]; then
    echo "Erro: Há mudanças não commitadas"
    exit 1
fi

# Solicita o tipo de release
echo "Tipo de release:"
echo "1) patch (1.0.0 -> 1.0.1)"
echo "2) minor (1.0.0 -> 1.1.0)"
echo "3) major (1.0.0 -> 2.0.0)"
read -p "Escolha (1-3): " choice

current_version=$(cat VERSION)
IFS='.' read -r major minor patch <<< "$current_version"

case $choice in
    1) new_version="$major.$minor.$((patch + 1))" ;;
    2) new_version="$major.$((minor + 1)).0" ;;
    3) new_version="$((major + 1)).0.0" ;;
    *) echo "Opção inválida"; exit 1 ;;
esac

echo "Atualizando versão de $current_version para $new_version"
echo "$new_version" > VERSION

# Commit e tag
git add VERSION
git commit -m "chore: bump version to $new_version"
git tag -a "v$new_version" -m "Release version $new_version"

echo "Release $new_version criado com sucesso!"
echo "Para enviar ao repositório remoto, execute:"
echo "git push origin main --tags"
