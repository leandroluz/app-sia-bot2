import os

import fdb
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials


def load_env_file(path=".env"):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def get_required_env(key):
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"Variavel de ambiente obrigatoria ausente: {key}. Configure no arquivo .env.")
    return value


def criar_planilha_google(df):
    df = df.map(str)

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    google_credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credencial/google-service-account.json")
    credentials = ServiceAccountCredentials.from_json_keyfile_name(google_credentials_file, scope)
    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key(get_required_env("SENTENCIADOS_PLANILHA_ID"))
    sheet = spreadsheet.sheet1

    sheet.clear()

    rows = df.values.tolist()
    rows.insert(0, df.columns.to_list())
    sheet.update(values=rows, range_name="A1")
    print(f"Planilha sentenciados atualizada com {len(df)} linhas.")


def pega_dados_sia(sql):
    con = fdb.connect(
        host=get_required_env("FIREBIRD_HOST"),
        database=get_required_env("FIREBIRD_DB"),
        user=get_required_env("FIREBIRD_USER"),
        password=get_required_env("FIREBIRD_PASSWORD"),
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
AND (UPPER(TRIM(tipo_inc.transito_comum)) STARTING WITH 'N')
AND (UPPER(TRIM(tipo_inc.transito_provisorio)) STARTING WITH 'N')
ORDER BY i.inc_raio, i.inc_cela
"""


if __name__ == "__main__":
    load_env_file()
    dados = pega_dados_sia(sql_sentenciados)
    print(f"Consulta sentenciados retornou {len(dados)} linhas.")
    criar_planilha_google(dados)


