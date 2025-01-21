from flask import Flask, request, jsonify
import hashlib,hmac

app = Flask(__name__)

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

SECRET_TOKEN = "mi_token_secreto"

def whats_app_send_message():
    return

def whats_app_read_message():
    return

def turn_off_faucet():
    return

def turn_on_faucet():
    return

# Define la ruta para el webhook
@app.route('/webhook', methods=['POST'])
def webhook():

    # Obtén los datos enviados en la solicitud
    data = request.get_json()
    # Obtener el contenido del cuerpo y el header con la firma
    payload = request.data
    received_signature = request.headers.get('X-Signature')
    # Generar la firma esperada
    expected_signature = hmac.new(token, payload, hashlib.sha256).hexdigest()
    token = request.headers.get('Authorization')
    # Validar el token
    if token != f"Bearer {SECRET_TOKEN}":
        return jsonify({"error": "Token no válido"}), 403
    # Validar la firma
    if not hmac.compare_digest(received_signature, expected_signature):
        return jsonify({"error": "Firma no válida"}), 403
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
    print("Datos recibidos:", data)
    
    # Envía una respuesta al servidor que llamó al webhook
    return jsonify({"message": "Webhook recibido con éxito"}), 200



# Ruta para manejar un GET
@app.route('/api/leak_detected', methods=['GET'])
def get_data():
    #cuando se recibe el mensaje de que se detecto una fuga de aga, se procede a cerrar llave de paso y notificar a vecinos por whatsapp
    #turn_off_faucet()
    #whats_app_send_message()
    return jsonify({"message": "fuga de agua detectada, llave de paso cerrada"})


# Ruta para manejar un GET
@app.route('/api/leak_sealed', methods=['GET'])
def get_data():
    #cuando se recibe un mensaje de whatsapp de un vecino, se junta en un contador, hasta el total de 4 vecinos confirmen, la llave se veulve a abrir
    #seal_process()
    return jsonify({"message": "un vecino ya verifico que no haya fugas, esperando a los demas"})




if __name__ == '__main__':
    app.run(debug=True, port=8000)
