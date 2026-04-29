import requests
from bs4 import BeautifulSoup

# Número do processo no formato CNJ
numero_processo = "1001400-43.2024.8.26.0470"

# Monta a URL de consulta
url = f"https://esaj.tjsp.jus.br/cpopg/show.do?processo.codigo=8TJ000{numero_processo.replace('-', '').replace('.', '').replace('/', '')}&gateway=true"

# Headers para simular navegador
headers = {
    'User-Agent': 'Mozilla/5.0'
}

# Requisição
response = requests.get(url, headers=headers)

# Verifica se carregou corretamente
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    movimentacoes = soup.select('.historico .descricaoMovimentacao')
    datas = soup.select('.historico .dataMovimentacao')

    print("📄 Movimentações mais recentes:")
    for data, mov in zip(datas, movimentacoes):
        print(f"{data.text.strip()} - {mov.text.strip()}")
else:
    print("Erro ao acessar o site do TJSP.")
