from m365_reminder_project.api import (
    get_access_token,
    get_all_users,
    get_todays_events,
    log_action,
)
from m365_reminder_project.notifications import (
    send_email_reminder,
    send_teams_message,
    create_onedrive_file,
    send_admin_notification,
)
from m365_reminder_project.models import Event, User
from m365_reminder_project.utils import detect_conflicts, suggest_focus_blocks
from config import Config


def main():
    log_action("Iniciando script de lembretes de compromissos...")

    if not all([Config.CLIENT_ID, Config.CLIENT_SECRET, Config.TENANT_ID]):
        log_action(
            "ERRO: As credenciais do aplicativo não foram configuradas. Verifique o arquivo .env.",
            success=False,
        )
        send_admin_notification(
            "Erro de Configuração do Script M365 Reminder",
            "As credenciais do aplicativo (CLIENT_ID, CLIENT_SECRET, TENANT_ID) não foram configuradas. Verifique o arquivo .env.",
        )
        return

    token = get_access_token()
    if not token:
        log_action(
            "Não foi possível obter token de acesso. Encerrando script.", success=False
        )
        send_admin_notification(
            "Erro de Autenticação do Script M365 Reminder",
            "Não foi possível obter o token de acesso para a API do Microsoft Graph.",
        )
        return

    users = get_all_users(token)
    if not users:
        log_action(
            "Não foi possível obter a lista de usuários. Encerrando script.",
            success=False,
        )
        send_admin_notification(
            "Erro ao Obter Usuários do Script M365 Reminder",
            "Não foi possível obter a lista de usuários do Microsoft Graph.",
        )
        return

    log_action(f"Processando lembretes para {len(users)} usuários...")

    for user_data in users:
        user_id = user_data.get("id")
        user_name = user_data.get("displayName", "Usuário")
        user_email = user_data.get("mail") or user_data.get("userPrincipalName")

        if not user_id or not user_email:
            log_action(
                f"Usuário {user_name} não possui ID ou e-mail válido. Pulando.",
                success=False,
            )
            continue

        log_action(f"Processando usuário: {user_name} ({user_email})")

        events_data = get_todays_events(token, user_id)
        events = [Event.from_dict(e) for e in events_data] if events_data else []

        # Detecção de Conflitos
        conflicts = detect_conflicts(events)
        if conflicts:
            log_action(
                f"Conflitos de horário detectados para {user_name}: {len(conflicts)} conflito(s)."
            )
            # Aqui você pode adicionar lógica para notificar o usuário sobre os conflitos
            # Por exemplo, adicionar uma seção ao e-mail ou mensagem do Teams.

        # Sugestão de Blocos de Foco
        focus_blocks = suggest_focus_blocks(events)
        if focus_blocks:
            log_action(
                f"Blocos de foco sugeridos para {user_name}: {len(focus_blocks)} bloco(s)."
            )
            # Similarmente, você pode adicionar essa informação aos lembretes.

        # Email Reminder
        email_sent = send_email_reminder(token, user_email, user_name, events)

        # Teams Message
        # teams_sent = send_teams_message(token, user_id, user_name, events)

        # OneDrive File
        onedrive_file_created = create_onedrive_file(token, user_id, user_name, events)

        # Feedback do Usuário (simulado)
        # Em um ambiente real, isso envolveria um link no e-mail/Teams que leva a um formulário
        # ou a um endpoint que registra o feedback.
        log_action(
            f"Lembretes enviados para {user_name}. Feedback do usuário pode ser coletado via plataforma externa."
        )
        teams_sent = True  # não vamos mexer com teams
        if email_sent and teams_sent and onedrive_file_created:
            log_action(f"Lembretes enviados com sucesso para {user_name}!")
        else:
            log_action(
                f"Alguns lembretes não puderam ser enviados para {user_name}.",
                success=False,
            )
            send_admin_notification(
                f"Falha no Envio de Lembretes para {user_name}",
                f"Alguns lembretes (e-mail, Teams, OneDrive) não puderam ser enviados para {user_name}.",
            )

    log_action("Script de lembretes de compromissos concluído!")


if __name__ == "__main__":
    main()
