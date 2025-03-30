from flask import Flask, request
from datetime import datetime
from time import sleep
from flask_cors import CORS
import os
# Variaveis
hora_atual = int(datetime.now().time().strftime("%H"))  # pega a hora do sistema
mensagem_inicial = ""  # recebe bom dia, boa tarde ou boa noite de acordo com a hora
etapa = 0  # indica em qual etapa está o pedido. Ex: escolha da comida, da bebida...
escolha_atual = 0  # indica o que a pessoa escolheu na etapa

# listas de comidas, bebidas e formas de pagamentos
comidas = ("Coxinha", "Quibe", "Bolinha de queijo")
bebidas = ("Coca-Cola", "Fanta", "Sprite", "Pepsi", "Nenhuma")
pag = ("Dinheiro", "Cartão de crédito", "Cartão de débito", "Pix")
# dicionário com o resumo do que o cliente escolheu
pedido_cliente = {
    "comida": "",
    "bebida": "",
    "valor": 0.0,
    "pag": "",
    "troco": "sem troco",
    "endereco": ""
}

# quando inicia o código deixa ele funcionado em loop
app = Flask(__name__)
CORS(app,resources={r"/webhook":{"origins": "*"}})

# Método para excluir o pedido caso o cliente decida não finalizar
def resetar_pedido():
    global pedido_cliente, etapa, escolha_atual
    pedido_cliente = {
        "comida": "",
        "bebida": "",
        "valor": 0.0,
        "pag": "",
        "troco": 0,
        "endereco": ""
    }
    etapa = 0
    escolha_atual = 0


# Esse é o método principal, ele é acionado toda vez que uma mensagem é enviada a sandbox do twilio
@app.route("/webhook", methods=[ 'POST'])
def responder_msg():
    global etapa, escolha_atual, mensagem_inicial  # identifica as variáveis como globais


    resumo_pedido = ("Resumo do pedido:\nComida: {}\nBebida: {}\nValor: R${:.2f}\nForma de pagamento: {}\nTroco para: "
                     "{}").format(
        pedido_cliente["comida"], pedido_cliente["bebida"], pedido_cliente["valor"], pedido_cliente["pag"],
        pedido_cliente["troco"])

    # verifica a hora atual para responder de acordo
    if hora_atual < 12:
        mensagem_inicial = "Bom dia"
    elif hora_atual < 18:
        mensagem_inicial = "Boa tarde"
    else:
        mensagem_inicial = "Boa noite"

    # Recebe a mensagem do usuário e inicia a resposta
    data = request.get_json()
    client_msg = data.get('Body', "").lower()
    resposta = responder_msg()
    # a escolha atual recebe a msg que a pessoa digitou(string) e converte para int
    # se a msg for um texto, a escolha atual recebe -1

    

    try:
        escolha_atual = int(client_msg)
    except ValueError:
        escolha_atual = -1
    # se a msg for menor que 0, a escolha atual também recebe -1
    if escolha_atual < 0:
        escolha_atual = -1
    # Essa parte da escolha atual receber -1 é útil para caso a pessoa
    # digite um valor que não é uma opção  não dar nenhum erro

    '''Responde de acordo com a mensagem do usuário'''
    # 1° etapa: Qualquer mensagem que o cliente digitar o twilio responde com o cardápio e pede pra escolher
    if etapa == 0:
        resposta.message(
            f"{mensagem_inicial}. Aqui segue o nosso cardápio:\n1-Coxinha\n2-Quibe\n3-Bolinha de queijo")
        sleep(0.1)
        resposta.message("Digite 0 a qualquer momento para cancelar o pedido")
        etapa += 1
    # 2° etapa: Armazena a escolha da comida e pede pra escolher a bebida
    elif etapa == 1:
        if escolha_atual == 0:
            resetar_pedido()
            resposta.message("Pedido cancelado")
        elif escolha_atual in (1, 2, 3):
            pedido_cliente["comida"] = comidas[escolha_atual - 1]
            resposta.message(
                "Boa escolha. Agora escolha um refrigerante:\n1-Coca-Cola\n2-Fanta\n3-Sprite\n4-Pepsi\n5-Nenhuma")
            etapa += 1
    # 3° etapa: Armazena a escolha da bebida e o valor do pedido, mostra
    #           o valor do pedido e pede pra escolher a forma de pagamento
    elif etapa == 2:
        if escolha_atual == 0:
            resetar_pedido()
            resposta.message("Pedido cancelado")
        elif escolha_atual in (1, 2, 3, 4, 5):
            pedido_cliente["bebida"] = bebidas[escolha_atual - 1]
            resposta.message("Subtotal:R$32,50\nFrete:R$5,00\nTotal:R$37,50")
            pedido_cliente["valor"] = 37.50
            sleep(0.01)
            resposta.message(
                "Escolha a forma de pagamento:\n1-Dinheiro\n2-Cartão de crédito\n3-Cartão de débito\n4-Pix")
            etapa += 1
    # 4° etapa: Armazena a forma de pagamento.Se o cliente escolheu dinheiro pergunta se quer troco,
    #           se ele escolheu outra forma mostra o resumo do pedido, e pergunta se quer finalizar.
    elif etapa == 3:
        if escolha_atual == 0:
            resetar_pedido()
            resposta.message("Pedido cancelado")
        elif escolha_atual == 1:
            pedido_cliente["pag"] = pag[escolha_atual - 1]
            resposta.message("Vai precisar de troco?\n1-Sim\n2-Não")
            etapa += 1
        elif escolha_atual in (2, 3, 4):
            pedido_cliente["pag"] = pag[escolha_atual - 1]
            resposta.message(resumo_pedido)
            sleep(0.1)
            resposta.message("Gostaria de finalizar o pedido?\n3-Sim\n4-Não")
            etapa += 1
    # 5° etapa: Se o cliente quis troco pergunta troco pra quanto, se ele não quis troco, mostra
    #           o resumo do pedido e pergunta se quer finalizar. Se ele escolheu cartão ou pix
    #           e confirmou o pedido na etapa anterior mostra que foi finalizado
    elif etapa == 4:
        if escolha_atual == 0:
            resetar_pedido()
            resposta.message("Pedido cancelado")
        elif escolha_atual == 1:
            resposta.message("Precisa de troco pra quanto?")
            etapa += 1
        elif escolha_atual == 2:
            resposta.message("Ok.")
            sleep(0.1)
            resposta.message(resumo_pedido)
            sleep(0.1)
            resposta.message("Gostaria de finalizar o pedido?\n3-Sim\n4-Não")
            etapa += 1
        elif escolha_atual == 3:
            resposta.message("Pedido finalizado com sucesso!")
            sleep(0.1)
            resposta.message("Seu pedido será entregue em até 80 minutos")
        elif escolha_atual == 4:
            resposta.message("Pedido cancelado com sucesso")
            resetar_pedido()
    # armazena pra quanto ele quer o troco e mostra o resumo do pedido, e pergunta se quer finalizar
    elif etapa == 5:
        if escolha_atual == 0:
            resetar_pedido()
            resposta.message("Pedido cancelado")
        elif escolha_atual == 3:
            resposta.message("Pedido finalizado com sucesso!")
            sleep(0.1)
            resposta.message("Seu pedido será entregue em até 80 minutos")
        elif escolha_atual == 4:
            resposta.message("Pedido cancelado com sucesso")
            resetar_pedido()
        if escolha_atual > pedido_cliente["valor"]:
            pedido_cliente["troco"] = "R${:.2f}".format(escolha_atual)
            resumo_pedido = (
                "Resumo do pedido:\nComida: {}\nBebida: {}\nValor: R${:.2f}\nForma de pagamento: {}\nTroco para: "
                "{}").format(
                pedido_cliente["comida"], pedido_cliente["bebida"], pedido_cliente["valor"], pedido_cliente["pag"],
                pedido_cliente["troco"])
            resposta.message(resumo_pedido)
            sleep(0.1)
            resposta.message("Gostaria de finalizar o pedido?\n3-Sim\n4-Não")
            etapa += 1
    elif etapa == 6:
        if escolha_atual == 0:
            resetar_pedido()
            resposta.message("Pedido cancelado")
        elif escolha_atual == 3:
            resposta.message("Pedido finalizado com sucesso!")
            sleep(0.1)
            resposta.message("Seu pedido será entregue em até 80 minutos")
        elif escolha_atual == 4:
            resposta.message("Pedido cancelado com sucesso")
            resetar_pedido()

    return str(resposta)


if __name__ == "__main__":
    app.run(debug=True)
