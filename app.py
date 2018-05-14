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
    database = leer('respuestas')
    if os.path.isfile('conversacion.json'):
        data = leer('conversacion')
    else:
        data = {}

    while True:
        if message == "adios" or message == "bye":
            var ="Bais "+data["usuarioActual"]
            del data["usuarioActual"]
            data["inicio"]="True"
            escribir('./','conversacion',data)
            return jsonify({'status':'OK','answer':var})
            exit()
        if "usuarioActual" in data:
            #print("ENTREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
            user_ = data["usuario"]
            user = user_[data["usuarioActual"]]
            
            if ("nombre" in user and "edad"in user and "sexo" in user and "tiempo" in user) and user["tiempo"] != "inf":
                #print("TENGO TODOS LOS CAMPOS AJUUUUUA")
                #return jsonify({'status':'OK','answer':'ARRR SOY UN PIRATA'})
                pybot = respuesta(message,database)
                #data = {}
                data[pybot] = message
                #escribir('./','conversacion',data)
                return jsonify({'status':'OK','answer':pybot})
            
        if 'inicio' in data:
            if data["inicio"]=="True":
                resp = "Bienvenido, ¿eres nuevo usando FitBot?"
                data["inicio"] = "False"
                escribir('./','conversacion',data)
                return jsonify({'status':'OK','answer':resp})
                
            pybot = checar_inicio(message,database)
            if data["inicio"] == "False" and pybot=='No':
                resp = "Se me ha olvidado tú nombre, ¿Cómo te llamas?"
                return jsonify({'status':'OK','answer':resp})
            elif data["inicio"] == "False" and pybot=='Si':
                resp = "Perfecto, ¿Cúal es tú nombre?"
                del data['inicio']
                #Ya deberiamos de tener la estructura usuario
                data["usuario"]={}
                escribir('./','conversacion',data)
                return jsonify({'status':'OK','answer':resp})
        elif not "usuario" in  data:
            data["inicio"] = "False"
            resp = "Bienvenido, ¿eres nuevo usando FitBot?"
            escribir('./','conversacion',data)
            return jsonify({'status':'OK','answer':resp})
        usuario = data["usuario"]
        if "usuarioActual" in data:
            user = data["usuario"]
            nomb = user[data["usuarioActual"]]
            if not "edad" in nomb:
                string = "¿Cuantos años tienes "+nomb["nombre"]+"?"
                nomb["edad"]=-1
                escribir('./','conversacion',data)
                return jsonify({'status':'OK','answer':string})
            else:
                if nomb["edad"] == -1:
                    nomb["edad"]=message
                    #verificamos si es edad si no es
                    #del nomb["edad"]
                    #Si pone la edad bien pasar a  la pregunta de sexo
                    string = "Muy bien "+nomb["nombre"]+"¿eres Hombre o Mujer?"
                    nomb["sexo"]="indef"
                    escribir('./','conversacion',data)
                    return jsonify({'status':'OK','answer':string})
            if not "sexo" in nomb:
                string = "¿Eres hombre o mujer?"
                escribir('./','conversacion',data)
                return jsonify({'status':'OK','answer':string})
            else:
                if nomb["sexo"]=="indef":
                    sex = checar_sexo(message,database)
                    nomb["sexo"]=sex
                    string = "¿Cuanto tiempo llevas en el gym?"
                    nomb["tiempo"]="inf"
                    escribir('./','conversacion',data)
                    return jsonify({'status':'OK','answer':string})
                if nomb["tiempo"] == "inf":
                    nomb["tiempo"]= message
                    escribir('./','conversacion',data)
                    string = "Perfecto"
                    return jsonify({'status':'OK','answer':string})
        else:
            if message in usuario:
                nombre = data["usuarioActual"]
                data["usuarioActual"] = message
                escribir('./','conversacion',data)
                string = "Es un gusto tenerte de regreso "+message
                return jsonify({'status':'OK','answer':string})
            else:
                dic = data["usuario"]
                dic[message] = {"nombre":message}
                data["usuarioActual"] = message
                escribir('./','conversacion',data)
                string = "Bienvenido "+message+". Te hare una serie de preguntas"
                return jsonify({'status':'OK','answer':string})
               
        
def checar_inicio(mensaje,database):
    respuestas = database["respuestas_Si_No"]
    palabraMasParecida = process.extract(mensaje, respuestas, limit=1)[0]
    return respuestas.get(palabraMasParecida[0])

def checar_sexo(mensaje,database):
    respuestas = database["respuestas_Sexo"]
    print(respuestas)
    palabraMasParecida = process.extractBests(mensaje, respuestas, limit=1)[0]
    print(palabraMasParecida)
    return respuestas.get(palabraMasParecida[0])

    
def checar_saludo(mensaje):
    saludos=["hola", "que tal?", "que onda?","hey","mucho gusto"]
    respuestas=["Hola amig@!", "Hola!", "Bienvenido!", "¿Qué tal?!", "Eey!", "Hola de nuevo!", "¡¿Qué hay?!"]

    palabraMasParecida = process.extract(mensaje, saludos, limit=1)[0]
    prob = palabraMasParecida[1]

    if(prob < 70):
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
    #SELF_VERBS_WITH_NOUN_LOWER = [ "Yeah but I know a lot about {noun}", "My bros always ask me about {noun}"]
    #SELF_VERBS_WITH_ADJECTIVE = ["I'm personally building the {adjective} Economy","I consider myself to be a {adjective} preneur"]
    COMMENTS_ABOUT_SELF = ["Soy FitBot el mejor chat-robot para ejercicios","Soy FitBot y puedo ser de gran ayuda a la hora de hacer ejercicio.",]
    comment_about_animo = ["estoy de maravilla, ¿como estas tu?", "feliz y dispuesto a ayudarte en lo que necesites"]
    
    resp = None
    if pronoun is not "":
        if pronoun.text =='tú' or pronoun.text == 'tu' or pronoun.text == 'quien' or pronoun.text == 'eres':# and (noun or adjective):
            resp = random.choice(COMMENTS_ABOUT_SELF)
            #if noun is not "":
            #if random.choice((True, False)):
            #   resp = random.choice(SELF_VERBS_WITH_NOUN_CAPS_PLURAL).format(**{'noun': sing_to_plural(noun)})
            #else:
            #   resp = random.choice(SELF_VERBS_WITH_NOUN_LOWER).format(**{'noun': noun})
        elif pronoun.text == 'estas' or pronoun.text == 'esta':
            resp= random.choice(comment_about_animo)
    return resp

def check_for_routine(mensaje, noun,database):
    respuestas_rutinas = database["respuestas_rutinas"]
        
    palabraMasParecida = process.extract(mensaje, respuestas_rutinas.keys(), limit=1)[0]
    prob = palabraMasParecida[1]
    respuesta=None
    if(prob < 50) :
        esRutina=False
    else:
        esRutina=True
        #print("PALABRA MAS PARECIDA ",palabraMasParecida[0])
        respuesta = random.choice(respuestas_rutinas.get(palabraMasParecida[0]))

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

def respuesta(mensaje,database):
    parsed = nlp(str(mensaje))
    pronoun,aux, noun, adjective, verb,det = find_candidate_parts_of_speech(parsed)
    respuesta = check_for_comment_about_bot(pronoun, noun, adjective,det)
    #esNuevo = check_for_experience(pronoun,aux,noun,verb,det)
    print("respuesta",respuesta)
    noEntendi = ["Puedes ser un poco más claro", "Podrías ser mas especifico", "No te entiendo -.-", "Ni idea!", "Preguntas serias por favor!","En que te puedo ayudar?"]
    
    if not respuesta:
        respuesta = construir_respuesta(mensaje,pronoun,aux, noun, verb,det,database)
        
    if not respuesta:
        respuesta = random.choice(noEntendi)

    #logger.info("Returning phrase '%s'", resp)
    return respuesta

def construir_respuesta(mensaje,pronoun,aux, noun, verb,det,database):
    ejercicio = ["pierna","espalda","biceps","triceps","hombro","pecho","abdomen","bicep","tricep"]
    respuesta_cantidad = ["repeticiones", "cuantas", "series"]
   
    respuestas = {
        #"Hola": ["Hola amig@!", "Hola!", "Bienvenido!", "¿Qué tal?!"],
        #"Hey": ["Hola!", "Eey!", "Hola de nuevo!", "¡¿Qué hay?!"],
        "Gracias": ["No hay de qué!", "Para eso estamos", "cúando quieras!", "De nada :D"],
        #"bien": ["Me alegra escuchar eso!", "Que bueno!", "Genial, porque hoy será un dá duro!", "Vamo a darle!!"], 
        "enfermo": ["Es mejor que vayas a casa compañer@"],
        "recomendar": ["Te recomiendo hacer "+random.choice(ejercicio)],
        #"mal": ["Hay algo que pueda hacer por ti?"],
        "ejercicios":["Tengo estas rutinas de ejercicio: \n"+"pierna, ""espalda, ""biceps, ""triceps, ""hombro, ""pecho, ""abdomen, ""bicep, " "tricep"],
       "repeticiones":[ "Haz "+str(random.choice((3,4,5,6)))+" series de "+str(random.choice((8,12,15,20)))+" cada una."]
    }
    
    palabraMasParecida = process.extract(mensaje, respuestas.keys(), limit=1)[0]
    prob = palabraMasParecida[1]
    respuesta= None
    esSaludo,esRutina = False,False

    _,esRutina=check_for_routine(mensaje,noun,database)
    _,esSaludo=checar_saludo(mensaje)    
    
    if(prob < 60) or mensaje=="no" or mensaje=="si":
        if esSaludo == True:
            print("FUI SALUDO")
            respuesta,_=checar_saludo(mensaje)
        elif esRutina == True:
            print("FUI RUTINA")
            respuesta,_=check_for_routine(mensaje,noun,database)
    else:
        if noun.text in ejercicio and verb.text == 'hice':
            respuesta = "Te recomiendo hacer "+random.choice(ejercicio)
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
