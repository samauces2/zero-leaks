volatile unsigned long startTime = 0;  // Tiempo de inicio cuando se activa el sensor
volatile unsigned long endTime = 0;   // tiempo de final de uso del sensor
volatile unsigned long duration = 0;  // Duración durante la cual el sensor estuvo activado
volatile bool sensorActive = false;    // Estado del sensor (activo o no)

const int sensorPin = 4;  // Pin donde está conectado el sensor (por ejemplo, pin 2)

void setup() {
  Serial.begin(9600);            // Iniciar comunicación serial
  pinMode(sensorPin, INPUT);     // Configurar el pin del sensor como entrada
  attachInterrupt(digitalPinToInterrupt(sensorPin), sensorInterrupt, CHANGE);  // Interrupción en flanco de subida o bajada
}

void loop() {
  // Verificamos si el sensor estuvo activo
  if (sensorActive) {
    // Si el sensor estuvo activo, mostramos el tiempo que estuvo activado
    Serial.print("Tiempo activado: ");
    Serial.print(endTime);   // Muestra la duración en milisegundos
    Serial.println(" ms");
    duration=duration+endTime;
    if(((duration/1000)/60)>1)
    {
    Serial.print("tiempo acumulado: ");
    Serial.print(((duration/1000)/60));
    Serial.println(" min");
    Serial.print(((duration/1000)));
    }
    
    sensorActive = false;     // Restablecer el estado para la próxima medición
  }
}

// Función de interrupción que se ejecuta cuando el estado del sensor cambia
void sensorInterrupt() {
  if (digitalRead(sensorPin) == HIGH) {
    // El sensor se activó (por ejemplo, cuando pasa agua)
    startTime = millis();  // Guardamos el tiempo de inicio
  } else {
    // El sensor se desactivó
    endTime = millis() - startTime;  // Calculamos el tiempo transcurrido desde que se activó
    sensorActive = true;  // Marcamos que el sensor estuvo activo
  }
}
