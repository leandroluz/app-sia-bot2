from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle

# Caminho para o arquivo de credenciais
CREDENTIALS_FILE = 'credencial/botpegii-gkwg-c7c6829555ec.json'

# Inicializa a variável creds
creds = None

# Se o arquivo token.pickle existe, usa as credenciais salvas, caso contrário, realiza o fluxo OAuth
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)

# Se não há credenciais disponíveis, ou se as credenciais estão invalidadas, realiza o fluxo de login
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/drive'])
        creds = flow.run_local_server(port=0)
    # Salva as credenciais para a próxima execução
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

# Constrói o serviço do Google Drive
service = build('drive', 'v3', credentials=creds)

# Caminho do arquivo que você quer enviar
file_path = 'sentenciados.xsl'

# Cria metadados do arquivo e realiza o upload
file_metadata = {'name': 'sentenciados.xsl'}
media = MediaFileUpload(file_path, mimetype='application/vnd.ms-excel')
file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

print(f'Arquivo enviado com sucesso, ID: {file.get("id")}')
