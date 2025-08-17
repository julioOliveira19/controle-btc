import requests
import csv
from datetime import datetime
from tabulate import tabulate

ARQUIVO = "controle-btc.csv"

def get_btc_price(date=None):
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

def registrar_deposito(valor, data_deposito, moeda="BRL"):
    preco_no_dia = get_btc_price(data_deposito)
    preco_atual = get_btc_price()

    if moeda.upper() == "BTC":
        btc_comprado = valor
        valor_reais = btc_comprado * preco_no_dia
    else:  # entrada em reais
        valor_reais = valor
        btc_comprado = valor_reais / preco_no_dia

    valor_atual = btc_comprado * preco_atual
    lucro = valor_atual - valor_reais

    with open(ARQUIVO, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([valor_reais, data_deposito, preco_no_dia, preco_atual, lucro])

    print(f"\nDepósito registrado!")
    print(f"Valor investido: R${valor_reais:.2f}")
    print(f"BTC comprado: {btc_comprado:.8f}")
    print(f"Preço BTC no dia: R${preco_no_dia:.2f}")
    print(f"Preço BTC hoje: R${preco_atual:.2f}")
    print(f"Lucro/Prejuízo: R${lucro:.2f}")

def exibir_depositos():
    dados = []
    try:
        with open(ARQUIVO, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                row_float = [
                    float(row[0]),
                    row[1],
                    float(row[2]),
                    float(row[3]),
                    float(row[4])
                ]
                dados.append(row_float)
    except FileNotFoundError:
        print("Nenhum depósito registrado ainda.")
        return

    if dados:
        print("\nHistórico de Depósitos:\n")
        print(tabulate(
            dados,
            headers=["Investido (R$)", "Data", "BTC no dia (R$)", "BTC hoje (R$)", "Lucro/Prejuízo (R$)"],
            floatfmt=".2f"
        ))

        total_investido = sum(d[0] for d in dados)
        total_lucro = sum(d[4] for d in dados)
        valor_final = total_investido + total_lucro

        print("\nResumo Geral:")
        print(f"Total Investido: R${total_investido:.2f}")
        print(f"Lucro/Prejuízo: R${total_lucro:.2f}")
        print(f"Valor Atual:    R${valor_final:.2f}")
    else:
        print("Nenhum depósito registrado ainda.")

# -------------------------
# Menu interativo

while True:
    print("\n--- Controle de BTC ---")
    print("1 - Inserir novo depósito")
    print("2 - Consultar histórico")
    print("3 - Sair")
    opcao = input("Escolha uma opção: ")

    if opcao == "1":
        tipo = input("Você quer informar em (BRL) reais ou (BTC)? ").strip().upper()
        valor_str = input("Informe o valor: ").replace(",", ".")
        data_str = input("Informe a data do depósito (formato dd/mm/yyyy): ")

        valor = float(valor_str)
        data_formatada = datetime.strptime(data_str, "%d/%m/%Y").strftime("%d-%m-%Y")

        registrar_deposito(valor, data_formatada, tipo)

    elif opcao == "2":
        exibir_depositos()

    elif opcao == "3":
        print("Saindo...")
        break

    else:
        print("Opção inválida! Tente novamente.")
