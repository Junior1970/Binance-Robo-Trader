Robô de Negociação Binance

Este é um robô de negociação automatizada para a Binance, projetado para realizar operações de compra e venda de criptomoedas com base em preços-alvo definidos pelo usuário. A interface gráfica é construída com o framework Tkinter e utiliza a biblioteca ttkbootstrap para um design moderno e funcional. O robô é capaz de monitorar o mercado em tempo real, calcular preços de compra e venda, e registrar todas as ações no log de operações.

Funcionalidades:
Configuração Personalizada: Permite ao usuário definir a quantidade de ativos a negociar e a margem de lucro desejada.
Integração com Binance API: Conecta-se à Binance para realizar ordens de compra e venda de criptomoedas.
Preço-alvo Personalizado: O robô calcula automaticamente os preços-alvo para compra e venda com base na margem de lucro configurada.
Monitoramento em Tempo Real: Atualiza o preço do ativo selecionado a cada segundo e ajusta a operação conforme as condições do mercado.
Registro de Operações: Todos os eventos e erros são registrados em um log, visível na interface gráfica.
Grafico de Preços: Visualização do preço do ativo durante o dia, destacando o maior e menor preço com base nos últimos 24 períodos de 1 hora.
Funcionalidade de Alternância: O robô pode ser iniciado ou parado com um simples clique.

Requisitos:
Python 3.10
Binance API: Para usar este robô, você precisará de uma chave da API da Binance e uma chave secreta, que devem ser armazenadas em um arquivo .env.

Bibliotecas:
python-binance
pandas
numpy
matplotlib
datetime
python-dotenv


Como Usar:

Instale as dependências necessárias:
pip install -r requirements.txt

Crie ou atualize um arquivo .env na raiz do projeto com suas credenciais da Binance: utilize o .env.example

BINANCE_API_KEY=SuaAPIKey
BINANCE_SECRET_KEY=SuaSecretKey


Execute o script:
python main.py
Configure os parâmetros de negociação e inicie o robô clicando no botão "Iniciar Robô".

Observações:
O robô realiza operações de compra e venda com base nas condições definidas pelo usuário.
Use com cautela em ambientes de teste antes de operar com quantias significativas.
O robô foi desenvolvido para funcionar com criptomoedas na Binance, mas pode ser adaptado para outras exchanges.

