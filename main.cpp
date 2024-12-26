#include <LiquidCrystal.h>//for LCD
#define LED_BUILTIN 2
volatile int rpmcont;//mide los flancos ascendetes de la senial
int Calc;
int pin_sensor =2; //pin del sensor
void rpm () //funcion que llama a la interrupcion y conteo de liquido
{
  rpmcont++;//mide la senial ascendete y descendente del sesnor de efecto hall
}

// the setup function runs once when you press reset or power the board
void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  //pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  Serial.println("this is a test: medidor de flujo");
  delay(1000);
  rpmcont=0;
  /*sintaxis = attachInterrupt(interrupcion, funcion, modo)
  interrupcion el numero de la interrupcion externa: EXTERNAL_INTERRUPT_0,EXTERNAL
  funcion= el nombre de la funcion que sera llamda cuando el evento de interrupcion
  modo = LOW,CHANGE,RISING o FALLING: el modo en el que la interrupcion external es generada
  retorna = ninguno 
  */
  attachInterrupt(1,rpm,RISING);// especifica la funcion a la que invocar cuando se 
  /* arduino tiene dos interrupciones externas: las numero 0 (en el pin digital 2) y la 
  RISING para disparar la interrupcion cuando el pin pase de valor alto (HIGH) a bajo (LOW)
  FALLING para cuando el pin cambie de valor alto (HIGH) a bajo (LOW)
  rpm = llama a la funcion
  */
}

// the loop function runs over and over again forever
void loop() {
  rpmcont=0; //coloca a variable en cero listos para calcular
  sei(); //habilita interrupciones
  delay(1000);
  cli(); //deshabilitar las interrupciones globales
  Calc=(rpmcont *60 /350);//(pulso de frencuencia * 60  ) / 5.5q = caudal en ltrs/hora
  Serial.print(Calc,DEC); //imprime el numero de caudal en litros
  Serial.print("L/min\r\n");

  attachInterrupt(1,rpm,RISING);
  digitalWrite(LED_BUILTIN, HIGH);  // turn the LED on (HIGH is the voltage level)
  delay(1000);                      // wait for a second
  digitalWrite(LED_BUILTIN, LOW);   // turn the LED off by making the voltage LOW
  delay(1000);                      // wait for a second
}
