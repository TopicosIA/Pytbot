from flask import Flask, render_template, request, jsonify
import spacy
from fuzzywuzzy import process
import random
app = Flask(__name__)

@app.route("/")
def inicio():
    return render_template('chat.html')

@app.route("/ask", methods=['POST'])

def ask():
    message = str(request.form['messageText'])
    while True:
        if message == "adios":
            exit()
        else:
            pybot = respuesta(message)
            return jsonify({'status':'OK','answer':pybot})

def respuesta(mensaje):
    #choices = ["Atlanta Falcons", "New York Jets", "New York Giants", "Dallas Cowboys"]
    saludo = ["Hola", "¿Qué tal?", "Bienvenido", "Mucho gusto"]

    respuestas = {
        "Hola": ["Hola amigo!", "Hola!", "Bienvenido!", "¿Qué tal?!"],
        "Hey": ["Hola!", "Eey!", "Hola de nuevo!", "¿Qué hay?!"],
        "pierna": ["Sentadillas con Extenciones",
                          "Extensiones y prensa",
                          "Leg curl y Desplantes",
                          "Prensa y sentadillas",
                          "Desplantes",
                          "Desplantes con barra/mancuerna"],
        "espalda":["Remo con barra/mancuernas",
                          "Peso muerto y Remo con mancuernas",
                          "Jalón al frente"
                          "Polea Tras-Nuca",
                          "Polea al Pecho",
                          "Remo en Maquina",
                          "Barra T"
        ],
    }
    palabraMasParecida = process.extract(mensaje, respuestas.keys(), limit=1)[0]

    #process.extract(mensaje, choices, limit=2)
    #var = process.extractOne(mensaje, choices)
    #var = process.extract(mensaje, saludo)
    ##arreglo = var[0]
    #print(arreglo[1])
    return random.choice(respuestas.get(palabraMasParecida[0]))

if __name__ == "__main__":
    app.run(debug=True,use_reloader=True)

#tener llaves con los nombres de las llaves del diccionario json
#despues de hacer el string
#checamos si es saludo

#saludo, rutina, ejercicio

