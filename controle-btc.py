import requests
import csv
from datetime import datetime
from tabulate import tabulate

ARQUIVO = "depositos_btc.csv"

def get_btc_price(date=None):
    """
    Retorna o preço do BTC em reais.
    Se date=None -> pega preço atual
    Se date for string 'dd-mm-yyyy' -> pega preço histórico
    """
    if date:
        url = f"https://api.coingecko.com/api/v3/coins/bitcoin/history?date={date}&localization=false"
        r = requests.get(url).json()
        try:
            return r["market_data"]["current_price"]["brl"]
        except KeyError:
            raise ValueError(f"Preço histórico não disponível para a data {date}. Resposta da API: {r}")
    else:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=brl"
        r = requests.get(url).json()
        return r["bitcoin"]["brl"]

def registrar_deposito(valor_reais, data_deposito):
    # data_deposito deve ser no formato "dd-mm-yyyy"
    preco_no_dia = get_btc_price(data_deposito)
    preco_atual = get_btc_price()

    # Quanto de BTC foi comprado na época
    btc_comprado = valor_reais / preco_no_dia

    # Valor atual desse BTC
    valor_atual = btc_comprado * preco_atual

    # Lucro/prejuízo
    lucro = valor_atual - valor_reais

    # Salvar em CSV
    with open(ARQUIVO, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([valor_reais, data_deposito, preco_no_dia, preco_atual, lucro])

    print(f"Depósito registrado! Valor investido: R${valor_reais}")
    print(f"Preço BTC no dia: R${preco_no_dia:.2f}")
    print(f"Preço BTC hoje: R${preco_atual:.2f}")
    print(f"Lucro/Prejuízo: R${lucro:.2f}")

def exibir_depositos():
    dados = []
    try:
        with open(ARQUIVO, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                # converte números para float pra exibir bonitinho
                row_float = [
                    float(row[0]),       # investido
                    row[1],              # data
                    float(row[2]),       # BTC no dia
                    float(row[3]),       # BTC hoje
                    float(row[4])        # lucro/prejuízo
                ]
                dados.append(row_float)
    except FileNotFoundError:
        print("Nenhum depósito registrado ainda.")
        return

    if dados:
        print(tabulate(dados, headers=["Investido (R$)", "Data", "BTC no dia (R$)", "BTC hoje (R$)", "Lucro/Prejuízo (R$)"], floatfmt=".2f"))
    else:
        print("Nenhum depósito registrado ainda.")

# -------------------------
# Exemplo de uso:

# Registrar um depósito (descomente se quiser testar)
registrar_deposito(200, "10-08-2025")

# Exibir todos os depósitos registrados
exibir_depositos()
