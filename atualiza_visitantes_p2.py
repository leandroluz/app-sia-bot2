import os
import fdb
import gspread
import pandas as pd
from google.oauth2 import service_account as google_service_account


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


def format_date_columns(df):
    for col in df.columns:
        converted = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
        if converted.notna().any():
            df[col] = converted.dt.strftime("%d/%m/%Y").where(converted.notna(), "")

    if "CPF" in df.columns:
        df["CPF"] = df["CPF"].astype(str).str.replace(r"[^\d]", "", regex=True)
        df.loc[df["CPF"].str.lower() == "nan", "CPF"] = ""

    return df


def criar_planilha_google(df):
    df = df.fillna("")
    df = df.astype(str)

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    google_credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credencial/google-service-account.json")
    credentials = google_service_account.Credentials.from_service_account_file(
        google_credentials_file,
        scopes=scope,
    )
    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key(get_required_env("VISITANTES_PLANILHA_ID"))
    sheet = spreadsheet.get_worksheet_by_id(int(get_required_env("VISITANTES_ABA_ID")))

    sheet.clear()

    rows = df.values.tolist()
    rows.insert(0, df.columns.to_list())
    sheet.update(values=rows, range_name="A1")
    print(f"Planilha visitantes atualizada com {len(df)} linhas.")


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


sql_visitantes = """
WITH detentos_atuais AS (
    SELECT DISTINCT i.inc_matricula
    FROM inclusao i
    JOIN inclusaotipo tipo_inc ON (tipo_inc.id = i.inc_inclusaotipo_id)
    WHERE i.inc_exclusao = 0
      AND i.inc_raio IS NOT NULL
      AND i.inc_cela IS NOT NULL
      AND UPPER(TRIM(tipo_inc.transito_comum)) STARTING WITH 'N'
      AND UPPER(TRIM(tipo_inc.transito_provisorio)) STARTING WITH 'N'
)
SELECT DISTINCT
    v.vis_cpf AS CPF,
    v.vis_nome AS NOME,
    dv.dvi_status AS STATUS,
    v.vis_vencimento AS VENCIMENTO,
    v.vis_datanascimento AS NASCIMENTO
FROM detentovisita dv
JOIN visitas v ON (v.vis_id = dv.dvi_visita)
JOIN detentos_atuais da ON (da.inc_matricula = dv.dvi_matricula)
ORDER BY NOME
"""


if __name__ == "__main__":
    load_env_file()
    dados = pega_dados_sia(sql_visitantes)
    dados = format_date_columns(dados)
    print(f"Consulta visitantes retornou {len(dados)} linhas.")
    criar_planilha_google(dados)


