import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text
import os
import requests

DB_URL = os.getenv("DB_URL")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

engine = create_engine(DB_URL, connect_args={"sslmode": "require"})

df = pd.read_sql("SELECT * FROM equipos", engine)

df["fecha_vencimiento"] = pd.to_datetime(df["fecha_vencimiento"], errors="coerce")

hoy = datetime.now()
df["dias_restantes"] = (df["fecha_vencimiento"] - hoy).dt.days

# =========================
# ALERTA 20 DÍAS
# =========================
alertas_20 = df[
    (df["dias_restantes"].between(6, 20)) &
    (df["alerta_20"].fillna(False)== False)
]

# =========================
# ALERTA 5 DÍAS
# =========================
alertas_5 = df[
    (df["dias_restantes"].between(0, 5)) &
    (df["alerta_5"].fillna(False)== False)
]

# =========================
# FUNCIÓN PARA ENVIAR
# =========================
def enviar_correo(asunto, html):
    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "from": "onboarding@resend.dev",
            "to": ["morenoramirezkevinjose@gmail.com"],
            "subject": asunto,
            "html": html,
        },
    )
    print(response.json())

# =========================
# PROCESAR ALERTA 20
# =========================
if not alertas_20.empty:

    html = "<h2>⚠️ Equipos por vencer (20 días)</h2><ul>"

    for _, row in alertas_20.iterrows():
        html += f"<li>{row['tenant']} - {row['dias_restantes']} días</li>"

    html += "</ul>"

    enviar_correo("⚠️ Alerta 20 días", html)

    ids = ",".join(map(str, alertas_20["id"].tolist()))

    with engine.begin() as conn:
        conn.execute(text(f"""
            UPDATE equipos SET alerta_20 = TRUE
            WHERE id IN ({ids})
        """))

# =========================
# PROCESAR ALERTA 5
# =========================
if not alertas_5.empty:

    html = "<h2 style='color:red;'>🚨 URGENTE (5 días)</h2><ul>"

    for _, row in alertas_5.iterrows():
        html += f"<li>{row['tenant']} - {row['dias_restantes']} días</li>"

    html += "</ul>"

    enviar_correo("🚨 URGENTE: 5 días", html)

    ids = ",".join(map(str, alertas_5["id"].tolist()))

    with engine.begin() as conn:
        conn.execute(text(f"""
            UPDATE equipos SET alerta_5 = TRUE
            WHERE id IN ({ids})
        """))

print("Proceso terminado")