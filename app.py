from flask import Flask, render_template, request, jsonify
import os

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
	        pybot = responde(message)
	        return jsonify({'status':'OK','answer':pybot})

def responde(mensaje):
    var = "holaaa holala"
    return var
if __name__ == "__main__":
    app.run(debug=True,use_reloader=True)
