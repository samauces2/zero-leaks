from flask import Flask, request, jsonify
import hashlib,hmac,json,requests

app = Flask(__name__)
# Configurar el modo desarrollo
app.config['ENV'] = 'development'
app.config['DEBUG'] = True  # Activa el modo debug

'''# Ruta para manejar un GET
@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"message": "Datos recibidos correctamente", "data": [1, 2, 3, 4]})

# Ruta para manejar un POST
 @app.route('/api/data', methods=['POST']) 
def create_data():
    data = request.json  # Obtener datos enviados en el cuerpo de la solicitud
    return jsonify({"message": "Datos creados", "data": data}), 201

# Ruta para manejar un PUT
@app.route('/api/data/<int:item_id>', methods=['PUT'])
def update_data(item_id):
    data = request.json
    return jsonify({"message": f"Datos del ID {item_id} actualizados", "data": data})

# Ruta para manejar un DELETE
@app.route('/api/data/<int:item_id>', methods=['DELETE'])
def delete_data(item_id):
    return jsonify({"message": f"Datos del ID {item_id} eliminados"}), 204

if __name__ == '__main__':
    app.run(debug=True, port=8000)'''


'''
para configurar flask y usar certificados TLS, tienes que crearlos y los proporcionas aqui, checar como adaptar esto a azure function

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context=('cert.pem', 'key.pem'))'''

SECRET_TOKEN = "mi_token_secreto"#cambiar en produccion
WEBHOOK_VERIFY_TOKEN=SECRET_TOKEN
GRAPH_API_TOKEN=""
PORT="8000"

def whats_app_send_message():
    return

def whats_app_read_message():
    return

def turn_off_faucet():
    return

def turn_on_faucet():
    return

def counter(contact:str) -> str:
    return

def other_alert(request_dict:dict)->str:
    #aqui debes enviar un correo con el contenido json para analizarlo y poder seguir editando codigo 
    return "correo enviado"


@app.route('/')
def home():
    return "¡Hola, Flask está en modo desarrollo!"


@app.route('/webhook', methods=['GET'])
def webhook_get():
    '''
    const mode = req.query["hub.mode"];
    const token = req.query["hub.verify_token"];
    const challenge = req.query["hub.challenge"];
    // check the mode and token sent are correct
  if (mode === "subscribe" && token === WEBHOOK_VERIFY_TOKEN) {
    // respond with 200 OK and challenge token from the request
    res.status(200).send(challenge);
    console.log("Webhook verified successfully!");
  } else {
    // respond with '403 Forbidden' if verify tokens do not match
    res.sendStatus(403);
  }
});
    '''
    print("accediste a la funcion")
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    print(mode,token,challenge) 
    # check the mode and token sent are correct
    if mode=="subscribe" and token == SECRET_TOKEN:
        #respond with 200 OK and challenge token from the request
        print("webhook verified successfully")
        return challenge, 200
    else:
        #respond with '403 Forbidden' if verify tokens do not match
        return "Forbidden", 403


# Define la ruta para el webhook
@app.route('/webhook', methods=['post'])
def webhook_post():
    print("testing")
    print("Incoming webhook message:", json.dumps(request.json, indent=2))
    # Extrae el mensaje del cuerpo del webhook
    # Más detalles sobre el payload: https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/payload-examples#text-messages
    message = (
        request.json.get("entry", [{}])[0]
        .get("changes", [{}])[0]
        .get("value", {})
        .get("messages", [{}])[0]
    )
     # Verifica si el mensaje entrante contiene texto
    if message.get("type") == "text":
        # Extrae el ID del número de teléfono de la empresa
        business_phone_number_id = (
            request.json.get("entry", [{}])[0]
            .get("changes", [{}])[0]
            .get("value", {})
            .get("metadata", {})
            .get("phone_number_id")
        )
        alert_type= (
            request.json.get("entry",[{}])[0]
            .get("changes",[{}])[0]
            .get("field")#.get("field",[{}])
        )

        if alert_type == "messages":
            contact= (
            request.json.get("entry",[{}])[0]
            .get("changes",[{}])[0]
            .get("value",{})
            .get("contacts",[{}])[0]
            .get("wa_id","")#aqui obtiene el numero de whatsapp
            )
            message_type= (
            request.json.get("entry",[{}])[0]
            .get("changes",[{}])[0]
            .get("value",{})
            .get("messages",[{}])[0]
            .get("type","")
            )
            if message_type == "text":
                message_body= (
                request.json.get("entry",[{}])[0]
                .get("changes",[{}])[0]
                .get("value",{})
                .get("messages",[{}])[0]
                .get("text",{})
                .get("body")#aqui obtiene el numero de whatsapp
                )
                if message_body=="checado":
                    counter(contact)

        # Enviar un mensaje de respuesta
        try:
            url = f"https://graph.facebook.com/v18.0/{business_phone_number_id}/messages"
            headers = {"Authorization": f"Bearer {GRAPH_API_TOKEN}"}

            # Enviar respuesta
            response = requests.post(
                url,
                headers=headers,
                json={
                    "messaging_product": "whatsapp",
                    "to": message["from"],
                    "text": {"body": "Echo: " + message["text"]["body"]},
                    "context": {"message_id": message["id"]},
                },
            )
            print("Reply sent:", response.status_code, response.text)

            # Marcar el mensaje entrante como leído
            mark_read_response = requests.post(
                url,
                headers=headers,
                json={
                    "messaging_product": "whatsapp",
                    "status": "read",
                    "message_id": message["id"],
                },
            )
            print("Message marked as read:", mark_read_response.status_code, mark_read_response.text)

        except Exception as e:
            print("Error sending message:", str(e))

    return "", 200
    '''# Obtén los datos enviados en la solicitud
    data = request.get_json()
    print(data)
    #print(request.headers)
    # Obtener el contenido del cuerpo y el header con la firma
    #payload = request.data
    received_signature = request.headers.get('X-Signature')
    # Generar la firma esperada
    token = request.headers.get('Authorization')
    expected_signature = hmac.new(token.encode(), payload, hashlib.sha256).hexdigest()
    print(expected_signature)
    print(received_signature)
    # Validar el token
    if token != f"Bearer {SECRET_TOKEN}":
        return jsonify({"error": "Token no válido"}), 403
    else: 
        print("token accepted")
    # Validar la firma
    '''
    '''if not hmac.compare_digest(received_signature, expected_signature):
        return jsonify({"error": "Firma no válida"}), 403
    else:
        print("has accepted")'''
    #print(payload)
    #return jsonify({"message": "processed correctly"})
    '''
    aqui tienes que empezar a procesar los datos, estas son sugerencias en base al tipo de eventos:
    en cada evento obtener los datos
    -tipo de evento
    -display phone number
    -texto
    -timestamp

    para recibir las respuestas de los vecinos, el nombre y la hora
    '''
    # Imprime los datos en la consola (puedes procesarlos aquí)
    #print("Datos recibidos:", data)
    
    # Envía una respuesta al servidor que llamó al webhook
    #return jsonify({"message": "Webhook recibido con éxito"}), 200



# Ruta para manejar un GET
@app.route('/api/leak_detected', methods=['GET'])
def get_data_sensor():
    #cuando se recibe el mensaje de que se detecto una fuga de aga, se procede a cerrar llave de paso y notificar a vecinos por whatsapp
    #turn_off_faucet()
    #whats_app_send_message()
    return jsonify({"message": "fuga de agua detectada, llave de paso cerrada"})


# Ruta para manejar un GET
@app.route('/api/leak_sealed', methods=['GET'])
def get_data_whatsapp():
    #cuando se recibe un mensaje de whatsapp de un vecino, se junta en un contador, hasta el total de 4 vecinos confirmen, la llave se veulve a abrir
    #seal_process()
    return jsonify({"message": "un vecino ya verifico que no haya fugas, esperando a los demas"})




if __name__ == '__main__':
    app.run(debug=True, port=8000)
