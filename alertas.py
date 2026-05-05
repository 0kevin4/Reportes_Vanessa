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

alertas = df[
    (df["dias_restantes"].between(0, 20)) &
    (df["alerta_enviada"] == 0)
]

if not alertas.empty:

    html = """
    <h2 style="color:red;">⚠️ Equipos por vencer</h2>
    <table border="1" cellpadding="5" cellspacing="0">
        <tr>
            <th>Empresa</th>
            <th>Fecha</th>
            <th>Días restantes</th>
        </tr>
    """

    for _, row in alertas.iterrows():
        html += f"""
        <tr>
            <td>{row['tenant']}</td>
            <td>{row['fecha_vencimiento']}</td>
            <td>{row['dias_restantes']}</td>
        </tr>
        """

    html += "</table>"

    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "from": "onboarding@resend.dev",
            "to": "morenoramirezkevinjose@gmail.com",
            "subject": "⚠️ Equipos por vencer",
            "html": html,
        },
    )

    print(response.json())

    ids = ",".join(map(str, alertas["id"].tolist()))

    with engine.begin() as conn:
        conn.execute(text(f"""
            UPDATE equipos
            SET alerta_enviada = 1
            WHERE id IN ({ids})
        """))

    print("Correos enviados correctamente")

else:
    print("Sin alertas")