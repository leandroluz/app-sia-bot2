# blibliotecas firebird e pandas 
import fdb
import pandas as pd


# blibliotecas google
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def criar_planilha_google(df, nome_planilha):

    # Define os escopos
    scope = [
        "https://spreadsheets.google.com/feeds", 
        "https://www.googleapis.com/auth/drive"
    ]

    # Carrega as credenciais da conta de serviço
    credentials = ServiceAccountCredentials.from_json_keyfile_name('integra-sia-14460c816ae0.json', scope)

    # Autentica e cria um cliente gspread
    client = gspread.authorize(credentials)

    # Abre uma planilha existente ou cria uma nova
    spreadsheet = client.open("sia-sentenciados") # Substitua pelo nome da sua planilha
    sheet = spreadsheet.sheet1  # Assume que você está trabalhando com a primeira aba

    # Adiciona informações em colunas específicas
    # Suponha que você queira adicionar um nome na coluna A e uma idade na coluna B
    nome = "Leandro Luz"
    idade = 30

    # Adiciona os dados na próxima linha vazia
    proxima_linha = len(sheet.get_all_values()) + 1  # Calcula a próxima linha vazia
    sheet.update_cell(proxima_linha, 1, nome)  # Coluna A
    sheet.update_cell(proxima_linha, 2, idade)  # Coluna B


    # Compartilha a planilha com sua conta pessoal do Google
    email_pessoal = "tic.p2guarei@gmail.com"  # Substitua pelo seu e-mail
    spreadsheet.share(email_pessoal, perm_type='user', role='writer')
    print("Planilha enviada ao google com sucesso!")



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


dados = pega_dados_sia(sql_sentenciados)

criar_planilha_google(dados, "sentenciadosnovo")




