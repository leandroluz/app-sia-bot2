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
    nome = "João Silva"
    idade = 30

    # Adiciona os dados na próxima linha vazia
    proxima_linha = len(sheet.get_all_values()) + 1  # Calcula a próxima linha vazia
    sheet.update_cell(proxima_linha, 1, nome)  # Coluna A
    sheet.update_cell(proxima_linha, 2, idade)  # Coluna B


    # Compartilha a planilha com sua conta pessoal do Google
    email_pessoal = "tic.p2guarei@gmail.com"  # Substitua pelo seu e-mail
    spreadsheet.share(email_pessoal, perm_type='user', role='writer')
