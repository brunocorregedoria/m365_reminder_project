from datetime import datetime, timedelta
import requests
import random
import os
from jinja2 import Environment, FileSystemLoader
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import Config
from m365_reminder_project.api import log_action, call_graph_api

# Configura o ambiente Jinja2 para carregar templates do diretório 'templates'
environment = Environment(
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "..", "templates"))
)


# Função para gerar o conteúdo HTML do e-mail com base nos eventos do usuário
def generate_email_html(user_name, events):
    # Carrega o template de e-mail
    template = environment.get_template("email_template.html")
    today_date = datetime.now().strftime("%d/%m/%Y")

    processed_events = []
    for event in events:
        # Ajusta os horários do evento para o fuso horário local configurado
        start_time = event.start_datetime + timedelta(hours=Config.TIMEZONE_OFFSET)
        end_time = event.end_datetime + timedelta(hours=Config.TIMEZONE_OFFSET)

        # Formata a string de tempo do evento
        if event.is_all_day:
            time_str = "Dia inteiro"
        else:
            time_str = f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"

        # Adiciona o evento processado à lista
        processed_events.append(
            {
                "subject": event.subject,
                "time_str": time_str,
                "location": (
                    event.location if event.location else "Local não especificado"
                ),
                "body_preview": event.body_preview,
            }
        )

    # Escolhe uma frase aleatória para dias sem compromissos
    no_events_phrase = random.choice(Config.FRASES_SEM_COMPROMISSOS)

    # Renderiza o template com os dados do usuário e eventos
    return template.render(
        user_name=user_name,
        today_date=today_date,
        events=processed_events,
        no_events_phrase=no_events_phrase,
    )


# Função para enviar o e-mail de lembrete ao usuário
def send_email_reminder(token, user_email, user_name, events):
    log_action(f"Enviando e-mail de lembrete para {user_email}...")

    # Gera o conteúdo HTML do e-mail
    email_html = generate_email_html(user_name, events)

    # Prepara os dados do e-mail para a API do Graph
    email_data = {
        "message": {
            "subject": f"Seus compromissos para hoje - {datetime.now().strftime('%d/%m/%Y')}",
            "body": {"contentType": "HTML", "content": email_html},
            "toRecipients": [{"emailAddress": {"address": user_email}}],
        },
        "saveToSentItems": "false",  # Evita que o e-mail seja salvo na caixa de itens enviados do remetente
    }

    # Envia o e-mail usando a API do Graph. O remetente é definido por Config.ADMIN_EMAIL
    result = call_graph_api(
        token, f"/users/{Config.ADMIN_EMAIL}/sendMail", "POST", email_data
    )

    # Verificar se result indica sucesso (incluindo resposta vazia)
    if result and (result.get("status") == "success" or "message" in result):
        log_action(f"E-mail enviado com sucesso para {user_email}!")
        return True
    else:
        log_action(f"Falha ao enviar e-mail para {user_email}.", success=False)
        return False


# Função para gerar o conteúdo da mensagem do Teams
def generate_teams_message(user_name, events):
    # Carrega o template de mensagem do Teams
    template = environment.get_template("teams_template.txt")
    # Escolhe um emoji de bom dia aleatoriamente
    bom_dia_emoji = random.choice(Config.EMOJIS_BOM_DIA)

    processed_events = []
    for event in events:
        # Ajusta os horários do evento para o fuso horário local configurado
        start_time = event.start_datetime + timedelta(hours=Config.TIMEZONE_OFFSET)
        end_time = event.end_datetime + timedelta(hours=Config.TIMEZONE_OFFSET)

        # Formata a string de tempo do evento
        if event.is_all_day:
            time_str = "Dia inteiro"
        else:
            time_str = f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"

        # Escolhe um emoji de reunião aleatoriamente
        event_emoji = random.choice(Config.EMOJIS_REUNIAO)

        # Adiciona o evento processado à lista
        processed_events.append(
            {
                "subject": event.subject,
                "time_str": time_str,
                "location": event.location,
                "emoji": event_emoji,
            }
        )

    # Escolhe um emoji e uma frase para dias sem compromissos
    sem_compromisso_emoji = random.choice(Config.EMOJIS_SEM_COMPROMISSO)
    no_events_phrase = random.choice(Config.FRASES_SEM_COMPROMISSOS)

    # Renderiza o template com os dados do usuário e eventos
    return template.render(
        user_name=user_name.split()[0],  # Pega apenas o primeiro nome do usuário
        bom_dia_emoji=bom_dia_emoji,
        events=processed_events,
        sem_compromisso_emoji=sem_compromisso_emoji,
        no_events_phrase=no_events_phrase,
    )


# Função para enviar mensagem no Teams para o usuário
def send_teams_message(token, user_id, user_name, events):
    log_action(f"Enviando mensagem do Teams para o usuário {user_id}...")

    # Gera o conteúdo da mensagem do Teams
    message = generate_teams_message(user_name, events)

    # Prepara os dados para criar um chat one-on-one com o usuário
    chat_data = {
        "chatType": "oneOnOne",
        "members": [
            {
                "@odata.type": "#microsoft.graph.aadUserConversationMember",
                "roles": ["owner"],
                "user@odata.bind": f"https://graph.microsoft.com/v1.0/users/{Config.ADMIN_EMAIL}",  # O remetente da mensagem
            },
            {
                "@odata.type": "#microsoft.graph.aadUserConversationMember",
                "roles": ["owner"],
                "user@odata.bind": f"https://graph.microsoft.com/v1.0/users/{user_id}",  # O destinatário da mensagem
            },
        ],
    }

    # Tenta criar um chat (se já existir, a API retorna o chat existente)
    chat_result = call_graph_api(token, "/chats", method="POST", data=chat_data)

    if not chat_result or "id" not in chat_result:
        log_action(f"Falha ao criar chat com o usuário {user_id}.", success=False)
        return False

    chat_id = chat_result["id"]

    # Prepara os dados da mensagem a ser enviada no chat
    message_data = {"body": {"content": message, "contentType": "text"}}

    # Envia a mensagem para o chat criado/existente
    message_result = call_graph_api(
        token, f"/chats/{chat_id}/messages", method="POST", data=message_data
    )

    # Verifica o resultado do envio da mensagem
    if message_result and "id" in message_result:
        log_action(f"Mensagem do Teams enviada com sucesso para o usuário {user_id}!")
        return True
    else:
        log_action(
            f"Falha ao enviar mensagem do Teams para o usuário {user_id}.",
            success=False,
        )
        return False


# Função para criar um arquivo de lembrete no OneDrive do usuário
def create_onedrive_file(token, user_id, user_name, events):
    log_action(f"Criando arquivo de lembrete no OneDrive do usuário {user_id}...")

    today_date = datetime.now().strftime("%d/%m/%Y")
    content = f"Convite para a reunião - {today_date}\n"
    content += f"Usuário: {user_name}\n\n"

    if events:
        content += "COMPROMISSOS DE HOJE:\n"
        content += "====================\n\n"

        for i, event in enumerate(events, 1):
            # Ajusta os horários do evento para o fuso horário local configurado
            start_time = event.start_datetime + timedelta(hours=Config.TIMEZONE_OFFSET)
            end_time = event.end_datetime + timedelta(hours=Config.TIMEZONE_OFFSET)

            # Formata a string de tempo do evento
            if event.is_all_day:
                time_str = "Dia inteiro"
            else:
                time_str = (
                    f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
                )

            # Adiciona os detalhes do evento ao conteúdo do arquivo
            content += f"Compromisso {i}:\n"
            content += f"Título: {event.subject}\n"
            content += f"Horário: {time_str}\n"

            if event.location:
                content += f"Local: {event.location}\n"

            if event.organizer and event.organizer.get("name"):
                content += f"Organizador: {event.organizer.get('name')}\n"

            if event.body_preview:
                content += f"Descrição: {event.body_preview}\n"

            content += "\n"
    else:
        # Conteúdo para dias sem compromissos
        content += "Você não tem compromissos agendados para hoje.\n\n"
        content += random.choice(Config.FRASES_SEM_COMPROMISSOS)

    file_name = f"Convite para a reunião - {today_date}.txt"
    file_content = content.encode("utf-8")

    # Prepara os cabeçalhos para o upload do arquivo
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "text/plain; charset=utf-8",
    }

    # URL para upload do arquivo no OneDrive do usuário
    url = f"https://graph.microsoft.com/v1.0/users/{user_id}/drive/root:/{file_name}:/content"

    try:
        # Envia a requisição PUT para criar/atualizar o arquivo
        response = requests.put(url, headers=headers, data=file_content)
        response.raise_for_status()

        log_action(f"Arquivo criado com sucesso no OneDrive do usuário {user_id}!")
        return True
    except requests.exceptions.HTTPError as e:
        log_action(
            f"Erro HTTP ao criar arquivo no OneDrive do usuário {user_id}: {e.response.status_code} - {e.response.text}",
            success=False,
        )
        return False
    except requests.exceptions.RequestException as e:
        log_action(
            f"Erro de requisição ao criar arquivo no OneDrive do usuário {user_id}: {e}",
            success=False,
        )
        return False
    except Exception as e:
        log_action(
            f"Erro inesperado ao criar arquivo no OneDrive do usuário {user_id}: {e}",
            success=False,
        )
        return False


# Função para enviar notificações de erro para o administrador via e-mail
def send_admin_notification(subject, message):
    # Verifica se o e-mail do administrador está configurado
    if not Config.ADMIN_EMAIL:
        log_action(
            "ADMIN_EMAIL não configurado. Não é possível enviar notificação de erro.",
            success=False,
        )
        return False

    # Configurações SMTP (exemplo - você precisará configurar seu próprio servidor SMTP)
    # Estas variáveis devem ser carregadas do .env para segurança
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")

    # Verifica se as configurações SMTP estão completas
    if not all([smtp_server, smtp_username, smtp_password]):
        log_action(
            "Configurações SMTP incompletas. Não é possível enviar notificação de erro por e-mail.",
            success=False,
        )
        return False

    # Cria a mensagem de e-mail
    msg = MIMEMultipart()
    msg["From"] = smtp_username
    msg["To"] = Config.ADMIN_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))

    try:
        # Conecta ao servidor SMTP e envia o e-mail
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Inicia a criptografia TLS
            server.login(smtp_username, smtp_password)  # Autentica no servidor
            server.send_message(msg)
        log_action(
            f"Notificação de erro enviada para o administrador ({Config.ADMIN_EMAIL})."
        )
        return True
    except Exception as e:
        log_action(
            f"Falha ao enviar notificação de erro para o administrador: {e}",
            success=False,
        )
        return False
