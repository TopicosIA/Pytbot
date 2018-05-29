from flask import Flask, render_template, request, jsonify
import spacy
import es_core_news_sm
from fuzzywuzzy import process
import random
import json
import spacy
import re
import os.path


app = Flask(__name__)

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
        #Si hay un usuario registrado ya nos podemos despedir
        if message == "adios" or message == "bye":
            if "usuarioActual" in data:
                return despedida(data)
                exit()
            else:
                return jsonify({'status':'OK','answer':'¡adiós!'})
                exit()

        if "usuarioActual" in data:
            user_ = data["usuario"]
            user = user_[data["usuarioActual"]]

            if ("nombre" in user and "edad"in user and "sexo" in user and "tiempo" in user) and user["tiempo"] != "inf":
                if "ult_rutina" in user:
                    if user["ult_rutina"]=="si":
                        return dar_rutina(user,data,database,message)
                if "rutina" in user:
                    return analizar_respuestas_usuario(user,data,database,message)

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
                    return verificar_edad(nomb,message,data)
            if not "sexo" in nomb:
                string = "¿Eres hombre o mujer?"
                escribir('./','conversacion',data)
                return jsonify({'status':'OK','answer':string})
            else:
                if nomb["sexo"]=="indef":
                    return checar_sexo(message,database,nomb,data)
                if nomb["tiempo"] == "inf":
                    return validar_tiempo_Gym(data,database,message,nomb)

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
                string = "Muy bien "+message+". Te hare una serie de preguntas, ¿estás listo?"
                return jsonify({'status':'OK','answer':string})

def analizar_respuestas_usuario(user,data,database,message):
    mensaje = "Aqui andamos traficando rutinas.."
    return jsonify({'status':'OK','answer':mensaje})

def validar_tiempo_Gym(data,database,message,nomb):
    #buscamos si ha puesto alguna informacion como dias, meses o años
    respuestas = database["tiempo_En_Gym"]
    palabraMasParecida = process.extract(message, respuestas.keys(), limit=1)[0]
    string = ""
    if palabraMasParecida[1] < 70:
        nomb["tiempo"]="inf"
        string = "Para proporcionar una mejor atención, debemos saber cuanto tiempo llevas haciando ejercicio, por ejemplo escribe: 1 mes."
    else:
        #para saber los dias 1,2,3, etc..
        numero = validar_edad(message)
        lista = []
        lista.append(numero)
        lista.append(respuestas[palabraMasParecida[0]])
        nomb["tiempo"]= lista
        if respuestas[palabraMasParecida[0]] == "nuevo":
            return rutina_nuevo(database,nomb,data)
        else:
             string = "¿Cúal/es fue el ultimo musculo/s que realizaste?"
             nomb["ult_rutina"]="si"
             escribir('./','conversacion',data)
    return jsonify({'status':'OK','answer':string})

def rutina_nuevo(database, nomb, data):
    lista = []
    lista.append(0)
    lista.append("días")
    nomb["tiempo"]= lista
    respuestas_rutinas = database["respuestas_rutinas"]
    lista_ejercicios = ["pierna","espalda","triceps","hombro","pecho","abdomen","biceps"]
    random.shuffle(lista_ejercicios)
    mensaje = "Bien novato, tu rutina será: <br>"
    dic = {}
    for i in range(4):
        ejercicio = lista_ejercicios[i]
        random.shuffle(respuestas_rutinas[ejercicio])
        dic[ejercicio] = [respuestas_rutinas[ejercicio][0],respuestas_rutinas[ejercicio][1]]
        mensaje += ejercicio +" : "+ respuestas_rutinas[ejercicio][0] +" y "+ respuestas_rutinas[ejercicio][1]+ "<br> "
    if nomb["sexo"] == "Mujer":
        mensaje += "3 sereis de 8 repeticiones todos los ejercicios."
    else:
        mensaje += "4 sereis de 8 repeticiones todos los ejercicios."
    nomb["ult_rutina"] = dic
    nomb["rutina"] = dic
    escribir('./','conversacion',data)
    return jsonify({'status':'OK','answer':mensaje})

def validar_ultima_rutina(user,data,database,message):
    #separamos el mensaje del usuario
    rutina = message.split( )
    lista_ej = ["pierna","espalda","triceps","hombro","pecho","abdomen","biceps"]
    ejercicios = database["lista_ejercicios"]
    for musculo in rutina:
        #quitamos los ejercicios que ya hizo ayer
        palabraMasParecida = process.extract(musculo, ejercicios.keys(), limit=1)[0]
        if palabraMasParecida[0] in lista_ej:
            lista_ej.remove(palabraMasParecida[0]);
    random.shuffle(lista_ej)

    return lista_ej

def dar_rutina(user,data,database,message):
    lista_ejercicios = validar_ultima_rutina(user,data,database,message)
    respuestas_rutinas = database["respuestas_rutinas"]
    mensaje = ""
    dic = {}
    if len(lista_ejercicios) == 6:
        mensaje += "Bien, como no sabes que hiciste la última vez entonces y analizando tu informacion "+ user["nombre"]+" harás lo siguiente: <br>"
    else:
        mensaje += "Analizando todo lo que me acabas de decir "+user["nombre"]+" tu rutina será la siguiente: <br>"

    if user["sexo"] == "Hombre":
        if user["tiempo"][1] == "días" or user["tiempo"][1] == "semanas" or user["tiempo"][1] == "mes":
            if user["edad"] < 12 and user["edad"] > 45:
                #Le ponemos 3 musculos, pero pocos ejercicios
                for i in range(3):
                    ejercicio = lista_ejercicios[i]
                    random.shuffle(respuestas_rutinas[ejercicio])
                    dic[ejercicio] = [respuestas_rutinas[ejercicio][0],respuestas_rutinas[ejercicio][1]]
                    mensaje += ejercicio +" : "+ respuestas_rutinas[ejercicio][0] +" y "+ respuestas_rutinas[ejercicio][1]+ ",<br> "
                    mensaje += "4 sereis de 8 repeticiones todos los ejercicios."
            else:
                for i in range(4):
                    ejercicio = lista_ejercicios[i]
                    random.shuffle(respuestas_rutinas[ejercicio])
                    dic[ejercicio] = [respuestas_rutinas[ejercicio][0],respuestas_rutinas[ejercicio][1]]
                    mensaje += ejercicio +" : "+ respuestas_rutinas[ejercicio][0] +" y "+ respuestas_rutinas[ejercicio][1]+ ",<br> "
                    mensaje += "4 sereis de 10 repeticiones todos los ejercicios."
        elif user["tiempo"][1]== "meses":
            for i in range(2):
                ejercicio = lista_ejercicios[i]
                random.shuffle(respuestas_rutinas[ejercicio])
                dic[ejercicio] = [respuestas_rutinas[ejercicio][0],respuestas_rutinas[ejercicio][1],respuestas_rutinas[ejercicio][2]]
                mensaje += ejercicio +" : "+ respuestas_rutinas[ejercicio][0] +" y "+ respuestas_rutinas[ejercicio][1]+ ",<br> "
                mensaje += "4 sereis de 12 repeticiones todos los ejercicios."
        else:
            for i in range(2):
                ejercicio = lista_ejercicios[i]
                random.shuffle(respuestas_rutinas[ejercicio])
                dic[ejercicio] = [respuestas_rutinas[ejercicio][0],respuestas_rutinas[ejercicio][1],respuestas_rutinas[ejercicio][2],respuestas_rutinas[ejercicio][3]]
                mensaje += ejercicio +" : "+ respuestas_rutinas[ejercicio][0] +" y "+ respuestas_rutinas[ejercicio][1]+ ",<br> "
                mensaje += "4 sereis de 15 a 20 repeticiones todos los ejercicios."
    else:
        if user["tiempo"][1] == "días" or user["tiempo"][1] == "semanas" or user["tiempo"][1] == "mes":
            if user["edad"] < 12 and user["edad"] > 45:
                #Le ponemos 3 musculos, pero pocos ejercicios
                for i in range(3):
                    ejercicio = lista_ejercicios[i]
                    random.shuffle(respuestas_rutinas[ejercicio])
                    dic[ejercicio] = [respuestas_rutinas[ejercicio][0],respuestas_rutinas[ejercicio][1],respuestas_rutinas[ejercicio][3]]
                    mensaje += ejercicio +" : "+ respuestas_rutinas[ejercicio][0] +" y "+ respuestas_rutinas[ejercicio][1]+ ",<br> "
                    mensaje += "2 sereis de 8 repeticiones todos los ejercicios."
            else:
                for i in range(4):
                    ejercicio = lista_ejercicios[i]
                    random.shuffle(respuestas_rutinas[ejercicio])
                    dic[ejercicio] = [respuestas_rutinas[ejercicio][0],respuestas_rutinas[ejercicio][1]]
                    mensaje += ejercicio +" : "+ respuestas_rutinas[ejercicio][0] +" y "+ respuestas_rutinas[ejercicio][1]+ ",<br> "
                    mensaje += "3 sereis de 10 repeticiones todos los ejercicios."
        elif user["tiempo"][1]== "meses":
            for i in range(2):
                ejercicio = lista_ejercicios[i]
                random.shuffle(respuestas_rutinas[ejercicio])
                dic[ejercicio] = [respuestas_rutinas[ejercicio][0],respuestas_rutinas[ejercicio][1],respuestas_rutinas[ejercicio][2]]
                mensaje += ejercicio +" : "+ respuestas_rutinas[ejercicio][0] +" y "+ respuestas_rutinas[ejercicio][1]+ ",<br> "
                if(ejercicio == "pierna"):
                    mensaje += "4 sereis de 15 repeticiones todos los ejercicios."
                else:
                    mensaje += "4 sereis de 10 repeticiones todos los ejercicios."
        else:
            for i in range(2):
                ejercicio = lista_ejercicios[i]
                random.shuffle(respuestas_rutinas[ejercicio])
                dic[ejercicio] = [respuestas_rutinas[ejercicio][0],respuestas_rutinas[ejercicio][1],respuestas_rutinas[ejercicio][2],respuestas_rutinas[ejercicio][3]]
                mensaje += ejercicio +" : "+ respuestas_rutinas[ejercicio][0] +" y "+ respuestas_rutinas[ejercicio][1]+ ",<br> "
                if(ejercicio == "pierna"):
                    mensaje += "4 sereis de 20 repeticiones todos los ejercicios."
                else:
                    mensaje += "4 sereis de 12 repeticiones todos los ejercicios."

    user["ult_rutina"] = dic
    user["rutina"] = dic
    escribir('./','conversacion',data)
    return jsonify({'status':'OK','answer':mensaje})
def validar_edad(message):
    var = re.sub("[^0-9]", "", message)
    if (var == ""):
        var = 0
    return var

def verificar_edad(nomb,message,data):
    edad = validar_edad(message)
    string = ""
    if float(edad) <= 5 :
        string = "¡Por favor!, dime tu edad para poder ayudarte"
    else:
        string = "Bien, ¿Eres Hombre ó Mujer?"
        nomb["edad"]=edad
        nomb["sexo"]="indef"
        escribir('./','conversacion',data)
    return jsonify({'status':'OK','answer':string})

def despedida(data):
    var ="Hasta pronto "+data["usuarioActual"]
    del data["usuarioActual"]
    data["inicio"]="True"
    escribir('./','conversacion',data)
    return jsonify({'status':'OK','answer':var})

def checar_inicio(mensaje,database):
    respuestas = database["respuestas_Si_No"]
    palabraMasParecida = process.extract(mensaje, respuestas.keys(), limit=1)[0]
    return respuestas.get(palabraMasParecida[0])

def checar_sexo(mensaje,database,nomb,data):
    respuestas = database["respuestas_Sexo"]
    palabraMasParecida = process.extract(mensaje, respuestas.keys(), limit=1)[0]
    sexo = palabraMasParecida[0]
    if palabraMasParecida[1] < 70:
        nomb["sexo"]="indef"
        string = "Saber tu sexo es indispensable, ¿cúal es?"
    else:
        nomb["sexo"]=respuestas[sexo]
        string = "¿Cuanto tiempo llevas en el gym?"
        nomb["tiempo"]="inf"
    escribir('./','conversacion',data)
    return jsonify({'status':'OK','answer':string})


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
    nlp = es_core_news_sm.load()
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
    app.run()
