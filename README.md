# Projeto de Lembretes de Compromissos do Microsoft 365

Este projeto Python visa automatizar o envio de lembretes diários de compromissos para usuários do Microsoft 365 via e-mail, Microsoft Teams e OneDrive. Ele foi desenvolvido com foco em segurança, robustez, flexibilidade e inteligência.

## Funcionalidades

*   **Lembretes Diários:** Envio automático de lembretes de compromissos agendados para o dia.
*   **Múltiplos Canais de Notificação:** Suporte para e-mail, Microsoft Teams e OneDrive.
*   **Configuração Segura:** Utilização de variáveis de ambiente para credenciais sensíveis.
*   **Tratamento de Erros Robusto:** Mecanismos aprimorados para lidar com falhas na comunicação com a API do Microsoft Graph.
*   **Personalização:** Configurações flexíveis para adaptar o comportamento do script às necessidades da organização.
*   **Inteligência:** Detecção de conflitos de horário e sugestões de blocos de foco.

## Estrutura do Projeto

```
m365_reminder_project/
├── .env.example
├── config.py
├── main.py
├── requirements.txt
├── README.md
├── m365_reminder_project/
│   ├── __init__.py
│   ├── api.py
│   ├── notifications.py
│   ├── utils.py
│   └── models.py
├── templates/
│   ├── email_template.html
│   └── teams_template.txt
└── tests/
    ├── __init__.py
    └── test_api.py
```

## Configuração

1.  **Clonar o Repositório:**

    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd m365_reminder_project
    ```

2.  **Variáveis de Ambiente:**

    Crie um arquivo `.env` na raiz do projeto, baseado no `.env.example`, e preencha com suas credenciais do Azure AD e outras configurações:

    ```
    CLIENT_ID="seu_client_id"
    CLIENT_SECRET="seu_client_secret"
    TENANT_ID="seu_tenant_id"
    LOG_FILE="/var/log/m365_reminder.log"
    TIMEZONE_OFFSET=-3
    ADMIN_EMAIL="seu_email_admin@dominio.com"
    ```

3.  **Instalar Dependências:**

    ```bash
    pip install -r requirements.txt
    ```

## Execução

Para executar o script:

```bash
python main.py
```

## Agendamento (Cron)

Para agendar a execução diária do script via cron (ex: às 7h da manhã):

```bash
0 7 * * * /usr/bin/python3 /caminho/para/m365_reminder_project/main.py >> /var/log/m365_reminder_cron.log 2>&1
```

**Observação:** Certifique-se de que o caminho para o interpretador Python (`/usr/bin/python3`) e para o script `main.py` estejam corretos em seu ambiente.

## Contribuição

Sinta-se à vontade para contribuir com melhorias e novas funcionalidades. Veja o arquivo `CONTRIBUTING.md` para mais detalhes.


