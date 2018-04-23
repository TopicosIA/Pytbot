from flask import Flask, render_template, request, jsonify
import spacy
from fuzzywuzzy import process
import random
import json
import os.path

app = Flask(__name__)

@app.route("/")
def inicio():
    return render_template('chat.html')

@app.route("/ask", methods=['POST'])

def ask():
    message = str(request.form['messageText'])
    if os.path.isfile('conversacion.json'):
        data = leer('conversacion')
    else:
        data = {}

    while True:
        if message == "adios":
            exit()
        else:
            pybot = respuesta(message)
            #data = {}
            data[pybot] = message
            escribir('./','conversacion',data)
            return jsonify({'status':'OK','answer':pybot})

def respuesta(mensaje):
    #choices = ["Atlanta Falcons", "New York Jets", "New York Giants", "Dallas Cowboys"]
    noEntendi = ["Puedes ser un poco más claro", "Podrías especificar más",
    "No te entiendo -.-", "Ni idea!", "Preguntas serias por favor!"]

    respuestas = {
        "Hola": ["Hola amigo!", "Hola!", "Bienvenido!", "¿Qué tal?!"],
        "Hey": ["Hola!", "Eey!", "Hola de nuevo!", "¿Qué hay?!"],
        "Gracias": ["No hay de qué!", "Para eso estamos", "cúando quieras!", "De nada :D"],
        "Bien": ["Me alegra escuchar eso!", "Que bueno!", "Genial, porque hoy será un dá duro!",
         "Vamo a darle!!"],
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
    prob = palabraMasParecida[1]
    if(prob < 50):
        respuesta  = random.choice(noEntendi)
    else:
        respuesta = random.choice(respuestas.get(palabraMasParecida[0]))

    return respuesta

def escribir(path, fileName, data):
    filePathNameWExt = './' + path + '/' + fileName + '.json'
    with open(filePathNameWExt, 'w') as fp:
        json.dump(data, fp)
def leer(nombre):
    with open('./'+nombre+'.json') as js:
        return json.load(js)

if __name__ == "__main__":
    app.run(debug=True,use_reloader=True)

#tener llaves con los nombres de las llaves del diccionario json
#despues de hacer el string
#checamos si es saludo

#saludo, rutina, ejercicio
