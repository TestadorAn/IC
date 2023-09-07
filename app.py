from flask import Flask, render_template, request
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
import skfuzzy as fuzz
from skfuzzy import control as ctrl

app = Flask(__name__)

# Defina as variáveis fuzzy e regras aqui (como no seu código original)
# Definindo as variáveis do universo
preco = ctrl.Antecedent(np.arange(0, 1.1, 0.1), "preco")
produto = ctrl.Antecedent(np.arange(0, 1.1, 0.1), "produto")
mercado = ctrl.Consequent(np.arange(0, 1.1, 0.1), "mercado")

# Definindo as funções de pertinência
preco.automf(number=3, names=["barato", "meio_caro", "caro"])
produto.automf(number=3, names=["feio", "meio_feio", "bonito"])
mercado["nao_comprar"] = fuzz.trimf(mercado.universe, [0, 0, 0.5])
mercado["comprar_medio"] = fuzz.trimf(mercado.universe, [0, 0.5, 1])
mercado["comprar_alto"] = fuzz.trimf(mercado.universe, [0.5, 1, 1])

# Definindo as regras
rule1 = ctrl.Rule(preco["caro"] & produto["bonito"], mercado["comprar_medio"])
rule2 = ctrl.Rule(preco["caro"] & produto["meio_feio"], mercado["nao_comprar"])
rule3 = ctrl.Rule(preco["meio_caro"] & produto["bonito"], mercado["comprar_alto"])
rule4 = ctrl.Rule(preco["meio_caro"] & produto["meio_feio"], mercado["nao_comprar"])

# Adicionando as regras ao sistema de controle
investimento_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4])


# Criando o simulador
simulando_investimento = ctrl.ControlSystemSimulation(investimento_ctrl)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        preco_input = float(request.form["preco"])/100
        produto_input = float(request.form["produto"])/100

        # Cálculos fuzzy aqui
        # Define os valores de entrada do simulador fuzzy
        simulando_investimento.input["preco"] = preco_input
        simulando_investimento.input["produto"] = produto_input

        # Computa os valores fuzzy
        simulando_investimento.compute()

        # Obtém a saída do sistema fuzzy
        output_mercado = simulando_investimento.output["mercado"]

        # Criar gráficos e convertê-los em base64
        fig, axs = plt.subplots(3, 1, figsize=(10, 18))
        preco.view(sim=simulando_investimento, ax=axs[0])
        preco.view(sim=simulando_investimento, ax=axs[0])
        axs[0].set_title("Função de Pertinência - Preço")
        axs[0].set_xlabel("Preço")
        axs[0].set_ylabel("Pertinência")

        produto.view(sim=simulando_investimento, ax=axs[1])
        axs[1].set_title("Função de Pertinência - Produto")
        axs[1].set_xlabel("Produto")
        axs[1].set_ylabel("Pertinência")

        mercado.view(sim=simulando_investimento, ax=axs[2])
        axs[2].set_title("Função de Pertinência - Mercado")
        axs[2].set_xlabel("Mercado")
        axs[2].set_ylabel("Pertinência")
        buffer = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format="png")
        plt.close()
        buffer.seek(0)
        plot_data = base64.b64encode(buffer.read()).decode("utf-8")

        output_mercado = round(simulando_investimento.output["mercado"]*100,2)

        # Print do valor de saída
        #print("Valor de saída do sistema fuzzy (mercado):", output_mercado)
        
        
        return render_template("index.html", plot_data=plot_data, output_mercado=output_mercado)

    return render_template("index.html", plot_data=None)


if __name__ == "__main__":
    app.run(debug=True)
