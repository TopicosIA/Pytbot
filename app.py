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
        if message == "adios" or message == "bye":
            exit()
        else:
            pybot = respuesta(message)
            #data = {}
            data[pybot] = message
            escribir('./','conversacion',data)
            return jsonify({'status':'OK','answer':pybot})

def saludo(mensaje):
    saludos=["hola", "que tal?", "que onda?","hey","mucho gusto"]
    respuestas=["Hola amig@!", "Hola!", "Bienvenido!", "¿Qué tal?!", "Eey!", "Hola de nuevo!", "¡¿Qué hay?!"]
    
    palabraMasParecida = process.extract(mensaje, respuestas, limit=1)[0]
    prob = palabraMasParecida[1]
    
    if(prob < 50) or mensaje=="no" or mensaje=="si":
        esSaludo=False
    else:
        esSaludo=True
        respuesta = random.choice(respuestas)
    return respuesta,esSaludo
    
    
def respuesta(mensaje):
    noEntendi = ["Puedes ser un poco más claro", "Podrías ser mas especifico",
    "No te entiendo -.-", "Ni idea!", "Preguntas serias por favor!"]
    
    respuestas = {
        #"Hola": ["Hola amig@!", "Hola!", "Bienvenido!", "¿Qué tal?!"],
        #"Hey": ["Hola!", "Eey!", "Hola de nuevo!", "¡¿Qué hay?!"],
        "Gracias": ["No hay de qué!", "Para eso estamos", "cúando quieras!", "De nada :D"],
        "Bien": ["Me alegra escuchar eso!", "Que bueno!", "Genial, porque hoy será un dá duro!",
         "Vamo a darle!!"],
       "ejercicio":["Tengo estas rutinas de ejercicio: \n"+
             "pierna, "
    "espalda, "
    "biceps, "
    "triceps, "
    "hombro, "
    "pecho, "
    "abdomen, "
    "bicep, "
    "tricep"],
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
		"biceps": ["Curl conmancuernas sentado",
				   "Curl en martillo",
				   "Curl concentracion con mancuerna",
				   "Predicador con barra",
				   "Predicador con poleas",
				   "Curl en banca inclinada"
				  ],
		"triceps": ["Crossface",
					"Extensiones sobre cabeza con mancuerna",
					"Extensiones posteriores",
					"Press frances",
					"Extensiones sobre cabeza con barra",
					"Press de banca con agarre cerrado"
				   ],
		"hombro": ["Face pull",
				   "Press militar con barra o mancuernas",
				   "Press sentado con mancuernas",
				   "Elevación de hombros con barra o mancuernas",
				   "Elevacion de frontal de pie",
				   "Press sentado posterior"
				  ],
		"pecho": ["Cruces en polea",
				  "Press banca inclinada"
				  "Aperturas planas",
				  "Pectoral contractor",
				  "Fondos militares o lagartijas",
				  "Pullover",
				  "Press de banca plana con mancuernas"
				 ],
		"abdomen": ["Curl abdominal",
					"Flexiones laterales con mancuernas",
					"Curl abdominal declinado",
					"Flexión de piernas en banca",
					"Elevación de piernas en banca",
				   ],
        "repeticiones":[ "Haz "+str(random.choice((3,4,5,6)))+" series de "+str(random.choice((8,12,15,20)))+" cada una."],
    }
    palabraMasParecida = process.extract(mensaje, respuestas.keys(), limit=1)[0]
    prob = palabraMasParecida[1]
    _,esSaludo=saludo(mensaje)
    if(prob < 50) or mensaje=="no" or mensaje=="si":
        if esSaludo:
            respuesta,_=saludo(mensaje)
        else:
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
