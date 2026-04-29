# blibliotecas firebird e pandas 
import fdb
import pandas as pd


# blibliotecas google
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def criar_planilha_google(df):

    # Converte todas as colunas do DataFrame para string, isso vai garantir que todos os dados sejam serializáveis
    df = df.map(str)

    # Define os escopos
    scope = [
        "https://spreadsheets.google.com/feeds", 
        "https://www.googleapis.com/auth/drive"
    ]

    # Carrega as credenciais da conta de serviço do Google
    credentials = ServiceAccountCredentials.from_json_keyfile_name('integra-sia-14460c816ae0.json', scope)
    print("Autenticado no Google Docs com sucesso!")


    # Autentica e cria um cliente gspread
    client = gspread.authorize(credentials)

    # Abre uma planilha existente ou cria uma nova
    spreadsheet = client.open("sia-sentenciados")  # Substitua pelo nome da sua planilha
    sheet = spreadsheet.sheet1  # Assume que você está trabalhando com a primeira aba
    print("Planilha sentenciados-sia aberta!")

    # Limpa todo o conteúdo da planilha
    sheet.clear()
    print("Dados da planilha sentenciados-sia apagados!")

    # Converte o DataFrame para uma lista de listas
    rows = df.values.tolist()

    # Inclui os cabeçalhos do DataFrame
    rows.insert(0, df.columns.to_list())

    # Atualiza a planilha com os novos dados
    sheet.update('A1', rows)  # Atualiza começando da célula A1

    # Compartilha a planilha com sua conta pessoal do Google
    email_pessoal = "tic.p2guarei@gmail.com"  # Substitua pelo seu e-mail
    spreadsheet.share(email_pessoal, perm_type='user', role='writer')
    print("Planilha atualizada no google com sucesso!")



def pega_dados_sia(sql):

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

    # Executar a consulta Sentenciados e armazenar o resultado em um DataFrame do Pandas
    try:
        cursor = con.cursor()
        cursor.execute(sql_sentenciados)
        rows = cursor.fetchall()

        # Define os nomes das colunas como os nomes dos campos retornados pela consulta
        columns = [column[0] for column in cursor.description]

        # Cria um DataFrame com os resultados
        df = pd.DataFrame(rows, columns=columns)
        return df
    
    except Exception as e:
        print(f'Ocorreu um erro: {e}')
    finally:
        # Fechar a conexão com o banco de dados
        if con:
            con.close()
    




# Consulta SQL 
sql_sentenciados = """
SELECT 
    d.det_matricula, 
    d.det_nome, 
    ---d.det_matricula || '-' || COALESCE(d.det_digito, '') AS matricula_digito,
    ---i.inc_datainclusao, 
    ---i.inc_procedencia, 
    ---i.inc_raio, 
    ---i.inc_cela, 
    p.nome as nome_pavilhao
    ---r.tipo AS regime, 
    ---d.det_condenado, 
    --p.seguro, 
    --p.disciplinar
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
AND (i.inc_raio IS NOT NULL)
AND (i.inc_cela IS NOT NULL)
AND 
    (tipo_inc.transito_comum ='NÃO') 
AND 
    (tipo_inc.transito_provisorio ='NÃO')
ORDER BY 
    i.inc_raio, 
    i.inc_cela
"""


dados = pega_dados_sia(sql_sentenciados)

criar_planilha_google(dados)





