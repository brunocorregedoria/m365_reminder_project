import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    TENANT_ID = os.getenv("TENANT_ID")
    LOG_FILE = os.getenv("LOG_FILE", "/tmp/m365_meeting_reminder.log")
    TIMEZONE_OFFSET = int(os.getenv("TIMEZONE_OFFSET", -3))
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

    FRASES_SEM_COMPROMISSOS = [
        "Que tal aproveitar o dia para colocar suas tarefas em dia?",
        "Um dia livre é uma oportunidade para inovar e criar!",
        "Dia sem reuniões? Perfeito para focar em projetos importantes!",
        "Sua agenda está livre hoje. Que tal planejar os próximos passos de seus projetos?",
        "Dia livre de compromissos! Uma ótima chance para aprender algo novo.",
    ]

    EMOJIS_BOM_DIA = ["🌞", "🌻", "☀️", "🌅", "🌄", "🌹", "🌈", "✨"]
    EMOJIS_REUNIAO = ["📅", "🗓️", "📊", "👥", "💼", "🤝", "📌", "🔔"]
    EMOJIS_SEM_COMPROMISSO = ["🏖️", "🎯", "📚", "💡", "🧠", "🚀", "🔍", "📝"]
