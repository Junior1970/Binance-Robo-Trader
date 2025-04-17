from binance.client import Client
import os
from dotenv import load_dotenv

# Carregar as variáveis do arquivo .env
load_dotenv()

# Obter as credenciais da Binance
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_SECRET_KEY")
BASE_ASSET = "USDT"  # A moeda base para consultar saldo

# Verificar se as variáveis foram carregadas corretamente
if not API_KEY or not API_SECRET:
    print("Erro: As credenciais da Binance não foram encontradas no arquivo .env")
    exit()

# Inicializar o cliente Binance com API Key e Secret
client = Client(API_KEY, API_SECRET)

# Função para obter o saldo de USDT
def obter_saldo_real():
    try:
        # Buscar o saldo do ativo 'USDT'
        balance = client.get_asset_balance(asset=BASE_ASSET)
        
        if balance:
            saldo_real = float(balance['free'])  # Pega o saldo disponível (livre)
            return saldo_real
        else:
            print(f"Erro: Saldo de {BASE_ASSET} não encontrado!")
            return 0.0
    except Exception as e:
        print(f"Erro ao obter saldo de {BASE_ASSET}: {e}")
        return 0.0

# Função para exibir saldo
def exibir_saldo_real():
    saldo = obter_saldo_real()
    print(f"Saldo disponível de {BASE_ASSET}: {saldo:.2f}")

