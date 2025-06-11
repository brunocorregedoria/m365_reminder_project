from datetime import datetime, timedelta, timezone
import requests
import json
import random
from tenacity import retry, wait_exponential, stop_after_attempt, Retrying

from config import Config


# Função para registrar ações e erros em um arquivo de log e no console
def log_action(message, success=True):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "SUCESSO" if success else "FALHA"
    log_entry = f"[{timestamp}] [{status}] {message}"
    print(log_entry)

    try:
        # Tenta escrever no arquivo de log configurado
        with open(Config.LOG_FILE, "a") as f:
            f.write(log_entry + "\n")
    except Exception as e:
        # Em caso de erro ao escrever no log, imprime no console
        print(f"Erro ao escrever no arquivo de log: {e}")


# Função para obter token de acesso do Microsoft Graph API com retentativas
@retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
def get_access_token():
    log_action("Tentando obter token de acesso...")

    # URL do endpoint de token do Azure AD
    token_url = (
        f"https://login.microsoftonline.com/{Config.TENANT_ID}/oauth2/v2.0/token"
    )
    # Dados para a requisição do token (client_credentials flow)
    token_data = {
        "grant_type": "client_credentials",
        "client_id": Config.CLIENT_ID,
        "client_secret": Config.CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default",  # Escopo para acessar o Microsoft Graph
    }

    try:
        # Envia a requisição POST para obter o token
        response = requests.post(token_url, data=token_data)
        response.raise_for_status()  # Lança exceção para erros HTTP (4xx ou 5xx)
        token_info = response.json()
        access_token = token_info.get("access_token")

        if access_token:
            log_action("Token de acesso obtido com sucesso!")
            return access_token
        else:
            log_action("Falha ao extrair token de acesso da resposta.", success=False)
            return None
    except requests.exceptions.RequestException as e:
        # Captura erros de requisição (conexão, timeout, etc.)
        log_action(f"Erro de requisição ao obter token de acesso: {e}", success=False)
        raise  # Re-lança a exceção para que o decorador @retry possa tentar novamente
    except Exception as e:
        # Captura quaisquer outros erros inesperados
        log_action(f"Erro inesperado ao obter token de acesso: {e}", success=False)
        raise


# Função genérica para chamar a API do Microsoft Graph com retentativas
@retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
def call_graph_api(token, endpoint, method="GET", data=None):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    url = f"https://graph.microsoft.com/v1.0{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        else:
            log_action(f"Método HTTP não suportado: {method}", success=False)
            return None

        response.raise_for_status()

        # Verificar se há conteúdo para decodificar como JSON
        if response.text.strip():
            return response.json()
        else:
            # Para endpoints como sendMail que retornam 204 No Content
            log_action(
                f"API retornou resposta vazia (status {response.status_code}) - operação bem-sucedida"
            )
            return {"status": "success", "message": "Operation completed successfully"}

    except requests.exceptions.HTTPError as e:
        log_action(
            f"Erro HTTP ao chamar API do Graph ({endpoint}): {e.response.status_code} - {e.response.text}",
            success=False,
        )
        raise
    except requests.exceptions.RequestException as e:
        log_action(
            f"Erro de requisição ao chamar API do Graph ({endpoint}): {e}",
            success=False,
        )
        raise
    except Exception as e:
        log_action(
            f"Erro inesperado ao chamar API do Graph ({endpoint}): {e}", success=False
        )
        raise


# Função para obter a lista de todos os usuários do tenant
def get_all_users(token):
    log_action("Obtendo lista de todos os usuários...")

    # Chama a API do Graph para obter usuários, selecionando apenas os campos necessários
    users_data = call_graph_api(
        token, "/users?$select=id,displayName,mail,userPrincipalName"
    )

    if users_data and "value" in users_data:
        users = users_data["value"]
        log_action(f"Obtidos {len(users)} usuários com sucesso!")
        return users
    else:
        log_action("Falha ao obter lista de usuários.", success=False)
        return []


# Função para obter eventos do calendário de um usuário para o dia atual
def get_todays_events(token, user_id):
    log_action(f"Obtendo eventos de hoje para o usuário {user_id}...")

    # Define o início e o fim do dia atual no timezone UTC diretamente
    today = datetime.now(timezone.utc)
    start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = today.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Converte para o formato ISO que a API do Graph espera
    start_of_day_utc = start_of_day.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-3] + "Z"
    end_of_day_utc = end_of_day.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-3] + "Z"

    # Constrói o endpoint da API
    endpoint = f"/users/{user_id}/calendar/events?$filter=start/dateTime le '{end_of_day_utc}' and end/dateTime ge '{start_of_day_utc}'&$select=id,subject,bodyPreview,start,end,location,organizer,attendees,isAllDay"

    # Chama a API do Graph para obter os eventos
    events_data = call_graph_api(token, endpoint)

    if events_data and "value" in events_data:
        events = events_data["value"]
        log_action(f"Obtidos {len(events)} eventos para hoje para o usuário {user_id}.")
        return events
    else:
        log_action(f"Falha ao obter eventos para o usuário {user_id}.", success=False)
        return []
