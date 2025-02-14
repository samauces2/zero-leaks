import logging,json,aiohttp,requests
import azure.functions as func
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater,ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from azure.data.tables import TableServiceClient
vecinos=["123123312","123132132"] # id de telegram de los vecinos



async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Lo siento, no entiendo ese comando. Usa /ayuda para ver las opciones disponibles, recuerda usar '/' antes de la palabra")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = "Estos son los comandos disponibles:\n"
    help_text += "/start - Iniciar el bot\n"
    help_text += "/comodin - necesito 15 min de agua\n"
    help_text += "/confirmo - confirmo que no tengo fugas\n"
    help_text += "/estado - el estado de la llave, cuantas personas han confirmado tener 0 fugas\n"
    await update.message.reply_text(help_text)

async def notificar_vecinos(update: Update):
    print("funcion notificar vecinos")
    # Aquí se puede agregar tu lógica para iniciar el monitoreo
    text="se ha detectado una fuga, porfavor verifica que no tengas ninguna llave abierta y una vez hecho eso selecciona el comando /confirmo"
    text+="\n si necesitas puedes usar 15 min de uso del agua aunque no hayan confirmado los demas, solo se puede usar una vez"
    await update.message.reply_text(text)
    return

async def fuga_detectada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id  # Obtener el ID del remitente
    print(f"el usuario {user_id} ha ejecutado el comando fuga")
    bot_id = context.bot.id  # Obtener el ID del bot
    # Si el mensaje lo envió el bot mismo, lo procesamos
    if user_id == int("7572988306"):
        await update.message.reply_text("🚨 Alerta de fuga detectada desde la API.")
        cerrar_llave()
        await notificar_vecinos(update)
        return
    # Si el mensaje lo envió otro usuario
    else:
        await update.message.reply_text("❌ No tienes permiso para ejecutar este comando.")
        return

async def comodin(update: Update,context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.message.from_user.id
    respuesta=usar_comodin(user_id)
    if respuesta:
        await update.message.reply_text(f"comodin ingresado por {user_id}, abriendo llave por 15 min")
        abrir_llave(user_id)
    else:
        await update.message.reply_text(f"{user_id} ya has ingresado tu comodin, no puedo abrir llave de nuevo")
    return

async def confirmacion(update:Update,context: ContextTypes.DEFAULT_TYPE):
    print("funcion confirmacion invocada")
    #como podemos salvar la respuesta de cada vecino? storage account? variables de entorno?
    user_id = update.message.from_user.id # esta linea es lo mismo chat_id = update.message.chat_id
    cont=guardar_confirmacion(str(user_id))#la funcion te regrsaa el numero de personas faltantes por confirmar
    if cont==2:
        await update.message.reply_text(f"usuario: {user_id} tu confirmacion se ha guardado con exito, todos han confirmado, abriendo llave")
        abrir_llave()
        limpiar_datos()
    else:
        await update.message.reply_text(f"usuario: {user_id} tu confirmacion se ha guardado con exito,faltan por confirmar: {cont} ")
    return

async def status(update: Update,context: ContextTypes.DEFAULT_TYPE):
    print("funcion status ha sido invocada")
    table_client=conectar_storage_account()
    try:
        if estado_de_llave() == "abierta":
            print("el estado de la llave esta abierta, no hay fuga actualmente")
            await update.message.reply_text(f"el estado de la llave esta abierta, no hay fuga actualmente")
        else:
            confirmaciones=obtener_confirmaciones(table_client)
            text=f"el estado actual: hay una fuga, la llave esta cerrada\n"
            text+=f"faltan por confirmar: {confirmaciones} para poder abrir la llave\n"
            await update.message.reply_text(text)
    except Exception as e:
        await update.message.reply_text(f"hubo un error en la consulta {e}")
        return f"hubo un error en la consulta {e} "

async def echo(update: Update, context: CallbackContext) -> None:
    """Responde repitiendo el mensaje del usuario."""
    await update.message.reply_text(update.message.text)
    


def configurar_bot(application:ApplicationBuilder,TOKEN:str):
    print("accediste a la funcion configurar bot")
    # Configurar manejadores, esto es para ver comandos en los mensajes recibidos
    # Agregar manejador de mensajes desconocidos
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))
    application.add_handler(CommandHandler("start", lambda update, context: update.message.reply_text("Bot trabajando, usa /help para mas comandos.")))
    application.add_handler(CommandHandler("comodin", comodin))
    application.add_handler(CommandHandler("confirmo", confirmacion))
    application.add_handler(CommandHandler("estado", status))
    application.add_handler(CommandHandler("fuga", fuga_detectada))
    set_webhook(application,TOKEN)  # Establece el webhook al iniciar
    # Ejecuta el bot
    #application.run_polling()  # Reemplaza start_polling() y idle()

def set_webhook(application:ApplicationBuilder,TOKEN:str):
    #verificar si el webhook esta activado o no 
    url="link de ngrok/api/webhook"
    response = requests.get(url)
    data = response.json()
    
    if data["ok"]:
        webhook_info = data["result"]
        if webhook_info["url"]:
            print(f"Webhook está activado en la URL: {webhook_info['url']}")
        else:
            print("No hay un webhook activo.")
            WEBHOOK_URL="https://api.telegram.org/TUTOKENsetWebhook?url=https://ngrok/webhook"#la url de azure fucntions
            url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}"
            response = requests.get(url)
            if response.status_code == 200:
                print("✅ Webhook configurado correctamente")
            else:
                print("❌ Error al configurar webhook:", response.text)
    else:
        print("Error al verificar el estado del webhook.")

def estado_de_llave()->str:
    #desarrollar funcion que obtenga el estado actual de la llave de paso
    return "abierto"

def conectar_storage_account():
    print("funcion conectar_storage_accout invocada")
    connection_string=""
    table_name = "tequis"
    table_service = TableServiceClient.from_connection_string(conn_str=connection_string)
    table_client = table_service.get_table_client(table_name)
    print("conectado a la tabla\n",table_client )
    return table_client
# termina declaracion de funciones de telegram

def usar_comodin(user_id):
    table_client=conectar_storage_account()
    if (verificar_comodin(user_id,table_client)) ==  False:
        entity = {
            "PartitionKey": "confirmaciones",
            "RowKey": str(user_id),
            "comodin": "True"
        }
        table_client.upsert_entity(entity)  # Guarda o actualiza el estado del usuario
        #comodin(True)
        print(f"valor del comodin para el usuario {user_id} ha sido actualizado")
        return(True)
    else:
        print(f"ERROR: usuario={user_id}, tu comodin ya ha sido utilizado")
        #comodin(False)
        return (False)

def verificar_comodin(user_id,table_client):
    try:
        entity = table_client.get_entity("confirmaciones", str(user_id))
        entity.get()
        return entity.get("comodin", False)#si la entiedad del usuario userId existe, entrega True, sino, entrega False (valor por defecto) si no lo pones puede devolver NOne al no existir el valor
    except:
        return False


def guardar_confirmacion(user_id:str) -> int:
    print("funcion guardar_confirmacion invocada")
    table_client=conectar_storage_account()
    entity = {
        "PartitionKey": "confirmaciones",
        "RowKey": user_id,
        "confirmado": "True"
    }
    table_client.upsert_entity(entity)  # Guarda o actualiza el estado del usuario
    verificar_confirmacion(user_id,table_client)
    return todos_confirman(table_client)

def verificar_confirmacion(user_id,table_client):
    print("funcion verificar_informacion invocada")
    try:
        entity = table_client.get_entity("confirmaciones", str(user_id))
        return entity.get("confirmado", False)
    except:
        return False

def cerrar_llave(user_id:str="todos"):
  if user_id=="todos":
    print(f"se cierra  la llave")
    #aqui creas una logci app con un delay de 15 minutos  que vuelva a cerrar la llave :p
  else:
    print(f"se abre la llave, el usuario {user_id} ha usado comodin, se cerrara en 15 min")
  return

def abrir_llave(user_id:str="todos"):
    if user_id=="todos":
        print(f"se abre la llave, ya todos confirmaron")
    else:
        print(f"se abre la llave, el usuario {user_id} ha usado comodin, se cerrara en 15 min")
         #aqui creas una logci app con un delay de 15 minutos  que vuelva a cerrar la llave :p
    return


def todos_confirman(table_client)-> int:
    print("funcion todos_confirman invocada")
    #vecinos=["vecino1","vecino2","vecino3","vecino4"] #remplazar por userIDs
    global vecinos
    cont=0
    try:
        for vecino in vecinos:
            entity = table_client.get_entity("confirmaciones", vecino)
            print("entity: ",entity)
            if entity.get("confirmado", False) == "True":
                cont+=1
        if cont==2:
            print("todos confirmaron")
            limpiar_datos()
            return 2
        else:
            print("aun faltan por confirmar: ",(2-cont))
            return cont        
    except Exception as e:
        return f"excception occured : {e}"
    
def limpiar_datos():
    print("funcion limpiar_datos invocada")
    table_client=conectar_storage_account()
    #vecinos=["vecino1","vecino2","vecino3","vecino4"]#remplazar por userIds
    global vecinos
    for vecino in vecinos:
        entity = {
            "PartitionKey": "confirmaciones",
            "RowKey": vecino,
            "confirmado": "False",
            "comodin": "False"
        }
        table_client.upsert_entity(entity)  # Guarda o actualiza el estado del usuario
        verificar_confirmacion(vecino,table_client)


def obtener_confirmaciones(table_client):
    print("funcion obtener confirmaciones ha sido invocada")
    #vecinos=["vecino1","vecino2","vecino3","vecino4"]
    global vecinos
    cont=0
    try:
        for vecino in vecinos:
            entity = table_client.get_entity("confirmaciones", vecino)
            print(f"entity {entity}")
            if entity.get("confirmado", False) == "True":
                print("uno confirmado aumentando contador")
                cont+=1
        print(f"el contador es: {cont}")
        return cont        
    except Exception as e:
        return f"eexecption occured: {e}"






# Función de manejo de solicitudes HTTP para Azure Functions
async def telegram_webhook(req: func.HttpRequest) -> func.HttpResponse:
    try:
        data=req.get_json()
        print(data)
        if not telegram_app.bot:  # Verificar si el bot no está inicializado
            print("no inicio")
            await telegram_app.initialize()  # Inicializar el bot antes de procesar la actualización
        update = Update.de_json(data, telegram_app.bot)
        print("debug")
        await telegram_app.initialize()
        await telegram_app.process_update(update)  # Ahora usamos await directamente
        return func.HttpResponse("OK", status_code=200)
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

# Activa el logging para depuración
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

#app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
# Token del bot (reemplázalo con tu propio token)
TOKEN = ""

telegram_app = Application.builder().token(TOKEN).build()
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Inicializa la Azure Function App
configurar_bot(telegram_app,TOKEN)
function_app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
function_app.route("webhook", methods=["POST"])(telegram_webhook)






