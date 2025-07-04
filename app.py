from flask import Flask, render_template, request, jsonify, url_for
import data as dt
from plot import gerar_grafico
import os

app = Flask(__name__)

# Estados e anos disponíveis
estados = dt.capturar_estado()
anos = dt.capturar_ano()

@app.route("/")
def index():
    return render_template("index.html", estados=estados, anos=anos)

@app.route("/grafico", methods=["POST"])
def grafico():
    estado = request.form.get("estado")
    ano = request.form.get("ano")
    fig_html, angulos = gerar_grafico(estado, ano)
    return jsonify({"grafico": fig_html, **angulos})

@app.route("/gif/<estado>")
def gif(estado):
    gif_path = f"assets/{estado}.gif"
    if os.path.exists(os.path.join("static", gif_path)):
        return jsonify({"src": url_for('static', filename=gif_path)})
    return jsonify({"src": ""})

if __name__ == "__main__":
    app.run()
