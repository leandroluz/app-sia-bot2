import fdb
import pandas as pd



import pandas as pd
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os

# Função para criar uma planilha no Google Sheets e preencher com dados do DataFrame
def exportar_para_google_sheets(df, sheet_title):
    # Caminho para o arquivo de credenciais
    CREDENTIALS_FILE = 'credencial/botpegii-gkwg-c7c6829555ec.json'

    # Escopos necessários
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    creds = None
    # O arquivo token.pickle armazena os tokens de acesso e atualização do usuário, e é
    # criado automaticamente quando o fluxo de autorização é concluído pela primeira vez.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # Se não existirem credenciais válidas disponíveis, faz o usuário se logar.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Salva as credenciais para a próxima execução
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Cria uma nova planilha
    spreadsheet = {
        'properties': {
            'title': sheet_title
        }
    }
    spreadsheet = service.spreadsheets().create(body=spreadsheet,
                                                fields='spreadsheetId').execute()
    spreadsheet_id = spreadsheet.get('spreadsheetId')

    # Converte o DataFrame em uma lista de listas para o Google Sheets
    values = [df.columns.values.tolist()] + df.values.tolist()

    # Preenche a planilha com os dados do DataFrame
    body = {
        'values': values
    }
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range='A1',
        valueInputOption='RAW', body=body).execute()

    print(f'Planilha criada com sucesso: {spreadsheet_id}')







# Configurações da conexão com o banco de dados Firebird
firebird_host = '172.16.0.2'    # ou o IP do servidor onde o banco de dados está
firebird_db = '/home/sia/banco/dbsia.fdb'
firebird_user = 'SYSDBA'
firebird_password = 'hiper768WaupdatE'

# Conectar ao banco de dados
con = fdb.connect(
    host=firebird_host,
    database=firebird_db,
    user=firebird_user,
    password=firebird_password,
    charset='ISO8859_1'  # ajuste para a codificação apropriada 
)

# Consulta SQL 
sql_sentenciados = """
SELECT 
    d.det_matricula, 
    d.det_nome, 
    d.det_matricula || '-' || COALESCE(d.det_digito, '') AS matricula_digito,
    i.inc_datainclusao, 
    i.inc_procedencia, 
    i.inc_raio, 
    i.inc_cela, 
    p.nome as nome_pavilhao,
    r.tipo AS regime, 
    d.det_condenado, 
    p.seguro, 
    p.disciplinar
FROM 
    detentos d
JOIN 
    inclusao i ON (i.inc_matricula = d.det_matricula)
JOIN 
    inclusaotipo tipo_inc ON (tipo_inc.id = i.inc_inclusaotipo_id)
JOIN 
    regime r ON (r.id = d.det_regime_id)
LEFT JOIN 
    pavilhao p ON (p.id = i.inc_raio)
WHERE (i.inc_exclusao=0) 
AND 
    (tipo_inc.transito_comum ='NÃO') 
AND 
    (tipo_inc.transito_provisorio ='NÃO')
ORDER BY 
    i.inc_raio, 
    i.inc_cela
"""


# SQL Visitantes Ativos
sql_visitantes = """
SELECT
    dv.dvi_id,
    v.vis_id,
    dv.dvi_visita,
    dv.dvi_parentesco,
    dv.dvi_status,
    v.vis_nome,
    v.vis_cpf,
    v.vis_rg
FROM 
    detentovisita dv
JOIN 
    visitas v ON (v.vis_id = dv.dvi_id)
WHERE
    dv.dvi_status != 'EXCLUÍDO(A)'

"""
sql_visitantes2 = """
SELECT 
    v.vis_id, 
    v.vis_nome, 
    v.vis_rg, 
    v.vis_orgao, 
    v.vis_datanascimento,
    (case when (extract(month from CURRENT_DATE) < extract(month from v.vis_datanascimento) 
    or
    (extract(month from v.vis_datanascimento) = extract(month from CURRENT_DATE) and extract(day from CURRENT_DATE) < extract(day from v.vis_datanascimento))) then
    extract(YEAR from CURRENT_DATE) - extract(YEAR from v.vis_datanascimento) - 1
    else extract(YEAR from CURRENT_DATE) - extract(YEAR from v.vis_datanascimento) end) as vis_idade,
    v.vis_emancipado, v.vis_sexo, v.vis_endereco, v.vis_bairro, v.vis_cidade, v.vis_celular,
    v.vis_telefone, v.vis_datacadastro, v.vis_dataalteracao, dv.dvi_id, 
    dv.dvi_data, dv.dvi_parentesco, dv.dvi_tipovisita, dv.dvi_status, 
    v.vis_parlatorio, v.vis_obs, v.vis_endereco_st, v.vis_responsavel, 
    v.vis_vencimento, v.vis_endereco_venc
    FROM visitas v
    JOIN detentovisita dv ON (dv.dvi_visita=v.vis_id)
    JOIN detentos d ON (d.det_matricula=dv.dvi_matricula)
    WHERE (dv.dvi_matricula=:pmatricula)
    ORDER BY v.vis_nome ASC

"""




# Executar a consulta Sentenciados e armazenar o resultado em um DataFrame do Pandas
try:
    cursor = con.cursor()
    cursor.execute(sql_sentenciados)
    rows = cursor.fetchall()

    # Define os nomes das colunas como os nomes dos campos retornados pela consulta
    columns = [column[0] for column in cursor.description]

    # Cria um DataFrame com os resultados
    df = pd.DataFrame(rows, columns=columns)

    # Exportar para Google Sheets
    exportar_para_google_sheets(df, 'sentenciados')
    

except Exception as e:
    print(f'Ocorreu um erro: {e}')


# Executar a consulta Visitantes e armazenar o resultado em um DataFrame do Pandas
try:
    cursor = con.cursor()
    cursor.execute(sql_visitantes)
    rows = cursor.fetchall()

    # Define os nomes das colunas como os nomes dos campos retornados pela consulta
    columns = [column[0] for column in cursor.description]

    # Cria um DataFrame com os resultados
    df = pd.DataFrame(rows, columns=columns)

    # Exportar para Google Sheets
    exportar_para_google_sheets(df, 'visitantes')

except Exception as e:
    print(f'Ocorreu um erro: {e}')
finally:
    # Fechar a conexão com o banco de dados
    if con:
        con.close()



