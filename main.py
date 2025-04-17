import os
import math
import requests
import random
import tkinter as tk
import ttkbootstrap as tb
import matplotlib.pyplot as plt
from tkinter import ttk
from tkinter import StringVar, messagebox
from ttkbootstrap.constants import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from binance.client import Client
from dotenv import load_dotenv
from binance_balance import obter_saldo_real

# Carregar as variáveis do arquivo .env
load_dotenv()

# Obter as credenciais da Binance e os ativos do arquivo .env
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_SECRET_KEY")
BASE_ASSET = os.getenv("BASE_ASSET", "USDT")
QUOTE_ASSET = os.getenv("QUOTE_ASSET", "USDT")

# Verificar se as variáveis foram carregadas corretamente
if not API_KEY or not API_SECRET:
    print("Erro: As credenciais da Binance não foram encontradas no arquivo .env")
    exit()

print(f"API_KEY e API_SECRET carregados com sucesso! Base asset: {BASE_ASSET}, Quote asset: {QUOTE_ASSET}")

# Inicializar o cliente Binance com API Key e Secret
client = Client(API_KEY, API_SECRET)

# Variável global para controlar o estado do robô
robo_em_funcionamento = False

#posicao_atual = None  # Pode ser 'comprado', 'vendido', ou None
ultimo_tipo = None    # 'compra' ou 'venda'
saldo = 0.0

# Função para obter a posição do robo.
def executar_operacao():
    global posicao_atual, ultimo_tipo, saldo

    if posicao_atual is None:
# Primeira entrada baseada no saldo
        if saldo >= 0:
            posicao_atual = 'comprado'
            ultimo_tipo = 'compra'
            registrar_log("Entrando comprado (inicial)")
        else:
            posicao_atual = 'vendido'
            ultimo_tipo = 'venda'
            registrar_log("Entrando vendido (inicial)")
    else:
# Alternância: se última foi compra → vende; se última foi venda → compra
        if ultimo_tipo == 'compra':
            posicao_atual = 'vendido'
            ultimo_tipo = 'venda'
            registrar_log("Invertendo posição: entrando vendido")
        else:
            posicao_atual = 'comprado'
            ultimo_tipo = 'compra'
            registrar_log("Invertendo posição: entrando comprado")

# Simula lucro/prejuízo na operação (exemplo)
    resultado = random.uniform(-10, 10)
    saldo += resultado
    registrar_log(f"Resultado da operação: {resultado:.2f} | Novo saldo: {saldo:.2f}")


# Função para obter o preço do ativo
def obter_preco_binance(ativo):
    try:
        ticker = client.get_symbol_ticker(symbol=f'{ativo}{QUOTE_ASSET}')
        return float(ticker['price'])
    except Exception as e:
        registrar_log(f"Erro ao buscar preço: {e}")
        return None

# Função para registrar logs na interface
def registrar_log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_text.insert(tk.END, f"[{timestamp}] {msg}\n")
    log_text.see(tk.END)

# Função para validar entradas
def validar_entradas():
    try:
        quantidade = float(entry_qtd.get())
        margem_lucro = float(entry_lucro.get())
        if quantidade <= 0 or margem_lucro <= 0:
            raise ValueError("Valores devem ser positivos.")
        return True
    except ValueError as e:
        registrar_log(f"Entrada inválida: {e}")
        return False

# Função para ajustar a precisão das quantidades
def ajustar_precisao(quantidade, ativo):
    try:
        info = client.get_symbol_info(f"{ativo}{QUOTE_ASSET}")
        step_size = float([f for f in info['filters'] if f['filterType'] == 'LOT_SIZE'][0]['stepSize'])
        precision = int(round(-math.log(step_size, 10), 0))
        return round(quantidade, precision)
    except Exception as e:
        registrar_log(f"Erro ao ajustar precisão: {e}")
        return quantidade

# Função principal para alternar entre iniciar e parar o robô
def alternar_robo():
    global robo_em_funcionamento
    if robo_em_funcionamento:
        parar_robo()
    else:
        if validar_entradas():
            iniciar_robo()

# Função para iniciar o robô
def iniciar_robo():
    global robo_em_funcionamento
    robo_em_funcionamento = True
    btn_iniciar.config(text="Parar Robô")
    registrar_log("Robô iniciado!")
    atualizar_preco_em_tempo_real()

# Função para parar o robô
def parar_robo():
    global robo_em_funcionamento
    robo_em_funcionamento = False
    btn_iniciar.config(text="Iniciar Robô")
    registrar_log("Robô parado!")

# Função para atualizar o preço em tempo real
def atualizar_preco_em_tempo_real():
    if not robo_em_funcionamento:
        return
    ativo = ativo_selecionado.get().upper()
    symbol = f"{ativo}{QUOTE_ASSET}"
    try:
        preco = obter_preco_binance(ativo)
        if preco is not None:
            preco_atual_var.set(f"{preco:.2f}")
            verificar_preco_alvo(preco)
        else:
            registrar_log(f"Erro ao obter preço para {ativo}")
            preco_atual_var.set("Erro ao obter preço")
    except Exception as e:
        registrar_log(f"Erro ao atualizar preço: {e}")
        preco_atual_var.set("Erro ao atualizar preço")
    app.after(1000, atualizar_preco_em_tempo_real)
     


# Função para calcular o preço alvo de venda
def calcular_preco_alvo_venda(preco_atual, margem_lucro):
    return preco_atual * (1 + margem_lucro / 100)

# Função para calcular o preço alvo de compra
def calcular_preco_alvo_compra(preco_atual, margem_desconto):
    return preco_atual * (1 - margem_desconto / 100)

# Função para verificar se o preço atingiu o alvo de compra ou venda
def verificar_preco_alvo(preco_atual):
    try:
        preco_alvo_venda = float(preco_alvo_venda_var.get())
        preco_alvo_compra = float(preco_alvo_compra_var.get())

        if preco_atual >= preco_alvo_venda:
            registrar_log(f"Preço atingiu o alvo de venda! ({preco_atual:.2f})")
            realizar_venda(preco_atual)

        elif preco_atual <= preco_alvo_compra:
            registrar_log(f"Preço atingiu o alvo de compra! ({preco_atual:.2f})")
            realizar_compra(preco_atual)
    except Exception as e:
        registrar_log(f"Erro ao verificar preço-alvo: {e}")


# Função para realizar a venda
def realizar_venda(preco_atual):
    try:
        quantidade = float(saldo_var.get())  # Vamos vender o que está em saldo
        
        if quantidade > 0:
            symbol = f"{ativo_selecionado.get().upper()}{QUOTE_ASSET}"
            
            # Realizando a venda no mercado
            order = client.order_market_sell(
                symbol=symbol,
                quantity=quantidade
            )
                        
            registrar_log(f"Venda realizada! Quantidade: {quantidade} a {preco_atual:.2f} USDT")
            posicao_var.set("Venda realizada")
            saldo_var.set("0.00")
    except Exception as e:
        registrar_log(f"Erro ao realizar venda: {e}")

# Função para realizar a compra       
def realizar_compra(preco_atual):
    try:
        quantidade = float(entry_qtd.get())
        symbol = f"{ativo_selecionado.get().upper()}{QUOTE_ASSET}"
        
        # Realizando a compra no mercado
        order = client.order_market_buy(
            symbol=symbol,
            quantity=quantidade
        )
        
        registrar_log(f"Compra realizada! Quantidade: {quantidade} a {preco_atual:.2f} USDT")
        posicao_var.set("Compra realizada")
        
        # Aqui você pode atualizar o saldo, se quiser refletir a nova posição
        # saldo_var.set(str(quantidade))  # opcional
    except Exception as e:
        registrar_log(f"Erro ao realizar compra: {e}")

# Função para atualizar o gráfico com horários reais
def atualizar_grafico(precos, maior_preco, menor_preco, horarios):
    ax.clear()
    ax.plot(horarios, precos, color="#00ffcc", marker="o", label="Preço")

# Linhas horizontais
    ax.axhline(y=maior_preco, color='green', linestyle='--', linewidth=1.5, label=f"Maior: {maior_preco:.2f}")
    ax.axhline(y=menor_preco, color='red', linestyle='--', linewidth=1.5, label=f"Menor: {menor_preco:.2f}")

    ax.set_title("Preço durante o dia", color="white", fontsize=12)
    ax.tick_params(colors='white', rotation=45)  # Deixa as horas inclinadas
    ax.set_facecolor("#2b2b2b")

    for spine in ax.spines.values():
        spine.set_color("white")

    ax.legend(facecolor="#2b2b2b", edgecolor="white", labelcolor="white", fontsize=9)
    fig.tight_layout()
    canvas.draw()


# Função principal para iniciar o robô
def iniciar_robo():
    global robo_em_funcionamento
    robo_em_funcionamento = True
    btn_iniciar.config(text="Parar Robô")
    
    ativo = ativo_selecionado.get().upper()
    symbol = f"{ativo}{QUOTE_ASSET}"
    
    registrar_log("Robô iniciado!")
    atualizar_preco_em_tempo_real()  # Começa atualização contínua
    
    try:
# Busca os últimos 24 candles de 1 hora
        klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1HOUR, limit=24)
        precos = [float(k[4]) for k in klines]  # preço de fechamento
        horarios = [datetime.fromtimestamp(k[0] / 1000).strftime("%H:%M") for k in klines]
        
        maior_preco = max(precos)
        menor_preco = min(precos)
        preco_atual = precos[-1]
        
        margem_lucro = float(entry_lucro.get())
        preco_alvo_compra = calcular_preco_alvo_compra(preco_atual, margem_lucro)
        preco_alvo_venda = calcular_preco_alvo_venda(preco_atual, margem_lucro)

# Atualiza os dados no painel
        preco_atual_var.set(f"{preco_atual:.2f}")
        preco_alvo_compra_var.set(f"{preco_alvo_compra:.2f}")
        preco_alvo_venda_var.set(f"{preco_alvo_venda:.2f}")
        posicao_var.set("Sem posição")

        saldo_real = obter_saldo_real()
        saldo_var.set(f"{saldo_real:.2f}")
        
        quantidade = saldo_real / preco_atual
        entry_qtd.delete(0, tk.END)
        entry_qtd.insert(0, f"{quantidade:.6f}")
       
        registrar_log(f"Robô Trader iniciado para {symbol}!")
        atualizar_grafico(precos, maior_preco, menor_preco, horarios)

    except Exception as e:
        registrar_log(f"Erro ao iniciar robô para {symbol}: {e}")



# Configuração inicial do app
app = tb.Window(themename="darkly")
app.title("Robô de Negociação Binance")
app.geometry("790x720")
app.resizable(False, False)

frame_top = ttk.Frame(app, padding=10)
frame_top.pack(fill=X)

# Inicializando o estilo
style = tb.Style()
style.configure("TLabel", font=("Segoe UI", 10))
style.configure("TButton", font=("Segoe UI", 10, "bold"))

# Criar a variável StringVar após a janela principal ser criada
ativo_selecionado = StringVar(value=BASE_ASSET)

# ---------------------- Entrada de parâmetros ----------------------
frame_top = ttk.LabelFrame(app, text="Parâmetros de Configuração", padding=10)
frame_top.pack(fill=X, padx=10, pady=5)

ttk.Label(frame_top, text="Quantidade:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
entry_qtd = ttk.Entry(frame_top, width=10)
entry_qtd.grid(row=0, column=1, padx=5, pady=5)
entry_qtd.insert(0, "0.1")

ttk.Label(frame_top, text="Margem de lucro (%):").grid(row=0, column=2, sticky=W, padx=5, pady=5)
entry_lucro = ttk.Entry(frame_top, width=10)
entry_lucro.grid(row=0, column=3, padx=5, pady=5)
entry_lucro.insert(0, "2.5")

# Dropdown de Ativos
ttk.Label(frame_top, text="Ativo:").grid(row=0, column=4, sticky=W, padx=5, pady=5)
ativos = ["BTC", "ETH", "SOL", "ADA", "DOGE", "AVAX"]
combobox_ativo = ttk.Combobox(frame_top, textvariable=ativo_selecionado, values=ativos, state="readonly", width=10)
combobox_ativo.grid(row=0, column=5, padx=5, pady=5)

# Variável global para controlar o estado do robô
robo_em_funcionamento = False

# Criando um estilo vermelho para o texto
style.configure("Red.TLabel", foreground="red")

# Função para parar o robô sem perguntar
def parar_robo():
    global robo_ativo
    robo_ativo = False
    print("Robô parado")
    

# Função para alternar entre iniciar e parar o robô
def alternar_robo():
    global robo_em_funcionamento
    
    if robo_em_funcionamento:
# Se o robô estiver em funcionamento, parar o robô
        print("Robô parado")
        robo_em_funcionamento = False
        btn_iniciar.config(text="Iniciar Robô")  # Muda o texto do botão para 'Iniciar Robô'
        posicao_var.set("Robô parado")  # Atualiza o status para "Robô parado"
        posicao_var_label.config(style="Red.TLabel")  # Aplica o estilo vermelho ao status
        parar_robo()  # Chama a função parar_robo() sem a caixa de mensagem
    else:
# Se o robô não estiver em funcionamento, iniciar
        robo_em_funcionamento = True
        btn_iniciar.config(text="Parar Robô")  # Muda o texto do botão para 'Parar Robô'
        print("Robô iniciado")
        iniciar_robo()  # Certifique-se de que a função iniciar_robo() está configurada corretamente

# Configuração do botão
btn_iniciar = ttk.Button(frame_top, text="Iniciar Robô")
btn_iniciar.grid(row=0, column=6, padx=10)
btn_iniciar.config(command=alternar_robo)

## ---------------------- Painel de Status ----------------------
frame_status = ttk.LabelFrame(app, text="Painel de Status", padding=10)
frame_status.pack(fill=X, padx=10, pady=5)

def create_status_row(parent, label_text, row):
    ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky=W, padx=5, pady=2)
    var = tk.StringVar(value="0.00")
    label = ttk.Label(parent, textvariable=var, style="Info.TLabel")
    label.grid(row=row, column=1, sticky=W, padx=5)
    return var
        
preco_atual_var = create_status_row(frame_status, "Preço atual (USDT):", 0)
preco_alvo_compra_var = create_status_row(frame_status, "Alvo de compra (USDT):", 1)
preco_alvo_venda_var = create_status_row(frame_status, "Alvo de venda (USDT):", 2)
posicao_var = create_status_row(frame_status, "Posição atual:", 3)
saldo_var = create_status_row(frame_status, "Saldo em USDT:", 4)

# Referência ao label de status da posição, para permitir mudar a cor depois
posicao_var_label = ttk.Label(frame_status, textvariable=posicao_var, style="TLabel")
posicao_var_label.grid(row=3, column=1, sticky=W, padx=5)

# ---------------------- Log de Execução ----------------------
frame_log = ttk.LabelFrame(app, text="Histórico de Execução", padding=10)
frame_log.pack(fill=X, padx=10, pady=5)

log_text = tk.Text(frame_log, height=5, bg="#1e1e1e", fg="#00ffcc", insertbackground="white",
                   font=("Consolas", 10), relief="solid", borderwidth=1)
log_text.pack(fill=X, padx=10, pady=5)

# ---------------------- Gráfico ----------------------
frame_graph = ttk.LabelFrame(app, text="Gráfico de Preço Simulado", padding=10)
frame_graph.pack(fill=BOTH, expand=True, padx=10, pady=5)

fig, ax = plt.subplots(figsize=(10, 4), dpi=100)

ax.set_facecolor("#2b2b2b")
fig.patch.set_facecolor("#2b2b2b")
ax.tick_params(colors='white')

canvas = FigureCanvasTkAgg(fig, master=frame_graph)
canvas.get_tk_widget().pack(fill=BOTH, expand=True)


# Inicia o app
app.mainloop()
