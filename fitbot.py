import re
import spacy
import random
import logging
import os
import re

nlp = spacy.load('es')
os.environ['NLTK_DATA'] = os.getcwd() + '/nltk_data'
from textblob import TextBlob

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

#usar la coincidencia de palabras clave simple, similar a cómo se modelaron ELIZA y otras IU de conversación iniciales.
#Ejemplo de saludo
GREETING_KEYWORDS = ("hola", "que tal", "mucho gusto")#,"que pasa?")
GREETING_RESPONSES = ["Hola!", "Hey", "Que onda","List@ para entrenar?"]
#Oraciones con las que responderemos si no tenemos idea de lo que el usuario acaba de decir
NONE_RESPONSES = [
    "uh como te sientas hoy",
    "Tu puedes!",
    "Trabaja duro",
    "No pain no gain",
    "Que haras despues de entrenar?",
    "Deberias de tomar un descanso",
]
#estado de animo
ANIMO = [
    "Como estas el día de hoy?",
    "Que quieres realizar?"
    "Perfecto"
]

#Comentarios hacerca de ejercicio
COMENTARIOS_RUTINAS = [
    "pierna",
    "espalda",
    "biceps",
    "triceps",
    "hombro",
    "pecho",
    "abdomen",
    "bicep",
    "tricep"
]

EJERCICIOS_PIERNA = [
    "Sentadillas",
    "Extensiones",
    "Leg curl",
    "Prensa",
    "Desplantes",
    "Desplantes con barra/mancuerna"
]

EJERCICIOS_ESPALDA = [
    "Remo con barra/mancuernas",
    "peso muerto",
    "Polea Tras-Nuca",
    "Polea al Pecho",
    "Remo en Maquina",
    "Barra al Mentón"
]

EJERCICIOS_BICEPS = [
    "curl con mancuernas sentado",
    "Curl en Martillo",
    "Curl Concentracion con Mancuerna",
    "Predicador con Barra",
    "Predicador con Poleas",
    "Curl en Banca Inclinada"
]

EJERCICIOS_TRICEPS = [
    "Crossface",
    "Extensiones sobre cabeza con mancuerna",
    "Extensión Posterior para Triceps",
    "Press frances",
    "Extensiones sobre cabeza con barra",
    "Press de Banca con Agarre Cerrado"
]

EJERCICIOS_HOMBRO = [
    "face pull",
    "Press militar con barra/mancuernas",
    "Press Sentado con Mancuernas",
    "Elevación de Hombros con Mancuernas",
    "Elevación Frontal de Pie",
    "Press Sentado Posterior"
]

EJERCICIOS_PECHO = [
    "cruces en polea",
    "Press banca inclinada", #hombro y triceps
    "Aperturas Planas",
    "Pectoral Contractor",
    "Fondos Militares o Lagartijas",
    "Pullover",
    "Press de Banca Plana con Mancuernas"
]

EJERCICIOS_ABDOMEN = [
    "Curl Abdominal",
    "Flexiones Laterales con mancuernas",
    "Curl Abdominal Declinado",
    "Flexion de Piernas en Banca",
    "Elevación de piernas"
]
#INformacion obtenida de: http://www.gimnasiototal.com

# Template for responses that include a direct noun which is indefinite/uncountable
SELF_VERBS_WITH_NOUN_CAPS_PLURAL = [
    "My last startup totally crushed the {noun} vertical",
    "I really consider myself an expert on {noun}",
]

SELF_VERBS_WITH_NOUN_LOWER = [
    "Yeah but I know a lot about {noun}",
    "My bros always ask me about {noun}",
]

SELF_VERBS_WITH_ADJECTIVE = [
    "I'm personally building the {adjective} Economy",
    "I consider myself to be a {adjective}preneur",
]

COMMENTS_ABOUT_SELF = [
    "Puedo ser de gran ayuda",
    "En que te puedo ayudar?"
]
# end

def check_for_greeting(sentence):
    """If any of the words in the user's input was a greeting, return a greeting response"""
    for word in sentence:
        if word.text.lower() in GREETING_KEYWORDS:
            return random.choice(GREETING_RESPONSES)

class UnacceptableUtteranceException(Exception):
    """Raise this (uncaught) exception if the response was going to trigger our blacklist"""
    pass

def starts_with_vowel(word):
    """Check for pronoun compability -- 'a' vs. 'an'"""
    return True if word[0] in 'aeiou' else False

def check_for_comment_about_bot(pronoun, noun, adjective):
    """Check if the user's input was about the bot itself, in which case try to fashion a response
    that feels right based on their input. Returns the new best sentence, or None."""
    resp = None
    if pronoun is not "":
        if pronoun.text =='tú' or pronoun.text == "tu" and (noun or adjective):
            if noun is not "":
                if random.choice((True, False)):
                    resp = random.choice(SELF_VERBS_WITH_NOUN_CAPS_PLURAL).format(**{'noun': sing_to_plural(noun)})
                else:
                    resp = random.choice(SELF_VERBS_WITH_NOUN_LOWER).format(**{'noun': noun})
            else:
                resp = random.choice(SELF_VERBS_WITH_ADJECTIVE).format(**{'adjective': adjective})
    return resp
	

def respond(sentence):
    """Parse the user's inbound sentence and find candidate terms that make up a best-fit response"""
    #cleaned = preprocess_text(sentence)
    parsed = nlp(sentence)

    # Loop through all the sentences, if more than one. This will help extract the most relevant
    # response text even across multiple sentences (for example if there was no obvious direct noun
    # in one sentence
    pronoun,aux, noun, adjective, verb,det = find_candidate_parts_of_speech(parsed)
    resp = check_for_comment_about_bot(pronoun, noun, adjective)
    
    # If we said something about the bot and used some kind of direct noun, construct the
    # sentence around that, discarding the other candidates
    # If we just greeted the bot, we'll use a return greeting
    if not resp:
         resp = check_for_comment_about_bot(pronoun, noun, adjective)
    
    if not resp:
        resp = construct_response(pronoun,aux, noun, verb,det)
        
    #if not resp:
        # If we didn't override the final sentence, try to construct a new one:
        #if pronoun == 'tu' and not verb:
        #    resp = random.choice(COMMENTS_ABOUT_SELF)

    # If we got through all that with nothing, use a random response
    if not resp:
        resp = random.choice(NONE_RESPONSES)

    logger.info("Returning phrase '%s'", resp)
    # Check that we're not going to say anything obviously offensive
    #filter_response(resp)

    return resp

def construct_response(pronoun,aux, noun, verb,det):
    """No special cases matched, so we're going to try to construct a full sentence that uses as much
    of the user's input as possible"""
    resp = []
    ejercicios = []
    
    # We always respond in the present tense, and the pronoun will always either be a passthrough
    # from the user, or 'you' or 'I', in which case we might need to change the tense for some
    # irregular verbs.
    #if pronoun is not "":
    #    resp.append(pronoun.text)
    #if det is not "":
    #    resp.append(det.text)
    if noun is not "":
        #pronoun = "an" if starts_with_vowel(noun) else "a"
        #resp.append(noun.text)

        noun_word = noun.text
        print("noun word: ", noun_word)
        
        if noun_word in COMENTARIOS_RUTINAS:
            if noun_word == "pierna":
                ejercicios=EJERCICIOS_PIERNA
            elif noun_word == "espalda":
                ejercicios=EJERCICIOS_ESPALDA
            elif noun_word == "biceps" or noun_word == "bicep":
                ejercicios=EJERCICIOS_BICEPS
            elif noun_word == "triceps" or noun_word == "tricep":
                ejercicios=EJERCICIOS_TRICEPS
            elif noun_word == 'hombro':
                ejercicios=EJERCICIOS_HOMBRO
            elif noun_word == "pecho":
                ejercicios=EJERCICIOS_PECHO
            elif noun_word == "abdomen":
                ejercicios=EJERCICIOS_ABDOMEN
                
            REPS = "Haz {} repeticiones de {} {} veces".format(random.randint(3, 5),random.choice(ejercicios),random.randint(8, 15))
            resp.append(REPS)

    resp.append(random.choice(("amig@.", ".")))

    return " ".join(resp)

def find_candidate_parts_of_speech(parsed):
    """Given a parsed input, find the best pronoun, direct noun, adjective, and verb to match their input.
    Returns a tuple of pronoun, noun, adjective, verb any of which may be None if there was no good match"""
    indice=0
    
    pronoun, aux, noun, adjective, verb, det =[], [], [], [], [], []
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
    
    for i in range(len(noun)):
        if str(noun[i]) in COMENTARIOS_RUTINAS:
            indice=i
            
    pronoun.append('')
    aux.append('')
    noun.append('')
    adjective.append('')
    verb.append('')
    det.append('')

    print("pronoun: ",pronoun, "aux: ",aux,"noun: ", noun,"adjective: ", adjective,"verb: ", verb,"det: ", det)
    logger.info("Pronoun=%s, noun=%s, adjective=%s, verb=%s", pronoun[0], noun[0], adjective[0], verb[0])             

    return pronoun[0],aux[0], noun[indice], adjective[0], verb[0], det[0]

def fitback(sentence):
    """Main program loop: select a response for the input sentence and return it"""
    logger.info("Broback: respond to %s", sentence)
    resp = respond(sentence)
    return resp
	
print(fitback('cuantas repeticiones?'))