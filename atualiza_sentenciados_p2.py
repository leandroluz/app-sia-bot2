import os

import fdb
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials


def criar_planilha_google(df):
    df = df.map(str)

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    google_credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credencial/google-service-account.json")
    credentials = ServiceAccountCredentials.from_json_keyfile_name(google_credentials_file, scope)
    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key(os.environ["SENTENCIADOS_PLANILHA_ID"])
    sheet = spreadsheet.sheet1

    sheet.clear()

    rows = df.values.tolist()
    rows.insert(0, df.columns.to_list())
    sheet.update("A1", rows)


def pega_dados_sia(sql):
    con = fdb.connect(
        host=os.environ["FIREBIRD_HOST"],
        database=os.environ["FIREBIRD_DB"],
        user=os.environ["FIREBIRD_USER"],
        password=os.environ["FIREBIRD_PASSWORD"],
        charset="ISO8859_1",
    )

    try:
        cursor = con.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        return pd.DataFrame(rows, columns=columns)
    finally:
        con.close()


sql_sentenciados = """
SELECT
    d.det_matricula,
    d.det_nome,
    p.nome as nome_pavilhao
FROM detentos d
JOIN inclusao i ON (i.inc_matricula = d.det_matricula)
JOIN inclusaotipo tipo_inc ON (tipo_inc.id = i.inc_inclusaotipo_id)
JOIN regime r ON (r.id = d.det_regime_id)
LEFT JOIN pavilhao p ON (p.id = i.inc_raio)
WHERE (i.inc_exclusao=0)
AND (i.inc_raio IS NOT NULL)
AND (i.inc_cela IS NOT NULL)
AND (tipo_inc.transito_comum ='NAO')
AND (tipo_inc.transito_provisorio ='NAO')
ORDER BY i.inc_raio, i.inc_cela
"""


if __name__ == "__main__":
    dados = pega_dados_sia(sql_sentenciados)
    criar_planilha_google(dados)

