from flask import Flask, render_template, request, jsonify
import spacy
from fuzzywuzzy import process
import random
import json
import spacy
import re
import os.path


app = Flask(__name__)
nlp = spacy.load('es')
os.environ['NLTK_DATA'] = os.getcwd() + '/nltk_data'

#logging.basicConfig()
#logger = logging.getLogger()
#logger.setLevel(logging.DEBUG)

@app.route("/")
def inicio():
    return render_template('chat.html')

@app.route("/ask", methods=['POST'])

#from textblob import TextBlob

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

def checar_saludo(mensaje):
    saludos=["hola", "que tal?", "que onda?","hey","mucho gusto"]
    respuestas=["Hola amig@!", "Hola!", "Bienvenido!", "¿Qué tal?!", "Eey!", "Hola de nuevo!", "¡¿Qué hay?!"]
    
    palabraMasParecida = process.extract(mensaje, saludos, limit=1)[0]
    prob = palabraMasParecida[1]
    
    if(prob < 50):
        esSaludo=False
        respuesta=None
    else:
        esSaludo=True
        respuesta = random.choice(respuestas)
    return respuesta,esSaludo

"""def find_pronoun(sent):
    #Given a sentence, find a preferred pronoun to respond with. Returns None if no candidate pronoun is found in the input
    pronoun = None

    for word, part_of_speech in sent.pos_tags:
        # Disambiguate pronouns
        if part_of_speech == 'PRP' and word.lower() == 'tu':
            pronoun = 'yo'
        elif part_of_speech == 'PRP' and word == 'yo':
            # If the user mentioned themselves, then they will definitely be the pronoun
            pronoun = 'tu'
    return pronoun"""

def check_for_comment_about_bot(pronoun, noun, adjective,det):
    SELF_VERBS_WITH_NOUN_LOWER = [ "Yeah but I know a lot about {noun}", "My bros always ask me about {noun}"]
    SELF_VERBS_WITH_ADJECTIVE = ["I'm personally building the {adjective} Economy","I consider myself to be a {adjective} preneur"]
    COMMENTS_ABOUT_SELF = ["Puedo ser de gran ayuda","En que te puedo ayudar?"]
    
    resp = None
    if pronoun is not "":
        if pronoun.text =='tú' or pronoun.text == 'tu' and (noun or adjective):
            if noun is not "":
                if random.choice((True, False)):
                    resp = random.choice(SELF_VERBS_WITH_NOUN_CAPS_PLURAL).format(**{'noun': sing_to_plural(noun)})
                else:
                    resp = random.choice(SELF_VERBS_WITH_NOUN_LOWER).format(**{'noun': noun})
            else:
                resp = random.choice(SELF_VERBS_WITH_ADJECTIVE).format(**{'adjective': adjective})
    return resp

def check_for_routine(mensaje, noun):
    respuestas_rutinas = {
       "rutinas":["Tengo estas rutinas de ejercicio: \n"+
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
				   ]
    }
    
    respuesta_cantidad = ["repeticiones", "cuantas"]
    rep = "Haz "+str(random.choice((3,4,5,6)))+" series de "+str(random.choice((8,12,15,20))) +" cada una."
        
    palabraMasParecida = process.extract(mensaje, respuestas_rutinas, limit=1)[0]
    prob = palabraMasParecida[1]
    respuesta=None
    if(prob < 50):
        esRutina=False
        resuesta = None
    else:
        esRutina=True
        if palabraMasParecida[0] == respuestas_rutinas['rutinas']:
            respuesta = respuestas_rutinas['rutinas']
            print("check comment rutina: ",respuesta)
        else:
            respuesta = random.choice(respuestas_rutinas.get(palabraMasParecida[0]))
        
        #palabraMasPar = process.extract(noun, respuesta_cantidad, limit=1)[0]
        #prob2 = palabraMasPar[1]
    
        #if (prob2>50):
        #    respuesta.append(rep)
    return respuesta,esRutina

def find_candidate_parts_of_speech(parsed):
    indice=0
    
    pronoun, aux, noun, adjective, verb, det = [], [], [], [], [], []
    for text in parsed:
        print(text.pos_,text.tag_)
        if text.pos_== 'PRON' or text.tag_ == 'PRON':
            pronoun.append(text)
        elif text.pos_ is "AUX" or text.tag_ is "AUX":
            aux.append(text)    
        elif text.pos_ == 'NOUN' or text.tag_ == 'NOUN':
            noun.append(text)
        elif text.pos_ == 'ADJ' or text.tag_ == 'ADJ':
            adjective.append(text)
        elif text.pos_ == 'VERB' or text.tag_ == 'VERB':
            verb.append(text)
        elif text.pos_ == 'DET' or text.tag_ == 'DET':
            det.append(text) 
            
    pronoun.append('')
    aux.append('')
    noun.append('')
    adjective.append('')
    verb.append('')
    det.append('')

    print(pronoun, aux, noun, adjective, verb, det)
    #logger.info("Pronoun=%s, noun=%s, adjective=%s, verb=%s", pronoun[0], noun[0], adjective[0], verb[0])             

    return pronoun[0],aux[0], noun[0], adjective[0], verb[0], det[0]

def respuesta(mensaje):
    parsed = nlp(str(mensaje))
    
    pronoun,aux, noun, adjective, verb,det = find_candidate_parts_of_speech(parsed)
    resp = check_for_comment_about_bot(pronoun, noun, adjective,det)
    print("RESP",resp)
    #***************************************************************************
    noEntendi = ["Puedes ser un poco más claro", "Podrías ser mas especifico",
    "No te entiendo -.-", "Ni idea!", "Preguntas serias por favor!"]
    
    respuestas = {
         #"Hola": ["Hola amig@!", "Hola!", "Bienvenido!", "¿Qué tal?!"],
        #"Hey": ["Hola!", "Eey!", "Hola de nuevo!", "¡¿Qué hay?!"],
        "Gracias": ["No hay de qué!", "Para eso estamos", "cúando quieras!", "De nada :D"],
        #"bien": ["Me alegra escuchar eso!", "Que bueno!", "Genial, porque hoy será un dá duro!", "Vamo a darle!!"], 
        "enfermo": ["Es mejor que vayas a casa compañer@"],
        "mal": ["Hay algo que pueda hacer por ti?"],
        #"repeticiones":[ "Haz "+str(random.choice((3,4,5,6)))+" series de "+str(random.choice((8,12,15,20)))+" cada una."],
    }
    palabraMasParecida = process.extract(mensaje, respuestas.keys(), limit=1)[0]
    prob = palabraMasParecida[1]
    _,esSaludo=checar_saludo(mensaje)
    _,esRutina=check_for_routine(mensaje,noun)
    
    if(prob < 50) or mensaje=="no" or mensaje=="si":
        if esSaludo == True:
            print("FUI SALUDO")
            respuesta,_=checar_saludo(mensaje)
        elif esRutina == True:
            print("FUI SALUDO")
            respuesta,_=check_for_routine(mensaje,noun)
        else:
            if resp != None:
                respuesta = resp
            else:
                respuesta  = random.choice(noEntendi)
    else:
        if resp != None:
            respuesta = resp
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
