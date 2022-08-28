#define PIN_BUZZER 11 // Definir el pin de salida del BUZZER
int incomingByte; // Para la entrada de datos en serie
int pinVibrator = 3;  // Para selecionar pin de salida del vibrador

void setup() {
    // Inicializar el buzzer
    pinMode(PIN_BUZZER, OUTPUT);
    digitalWrite(PIN_BUZZER, LOW);
    Serial.begin(9600); // opens serial port, sets data rate to 9600 bps
}

void loop() {
  
  // Hacer sonar el buzzer con una frecuencia de 440Hz (Nota A4) y duración de 1 segundo (1000 milisegundos)
  tone(PIN_BUZZER, 440, 1000);
  // Esperar media segundo
  delay(500);     
  // Hacer sonar el buzzer con una frecuencia de 880Hz (Nota B4) y duración de 1 segundo
  tone(PIN_BUZZER, 880, 1000);
  

  while(1){
    if (Serial.available() > 0) { // send data only when you receive data:
      incomingByte = Serial.read()-48;
      if (incomingByte == 1)
        pinVibrator = 3;
      if (incomingByte == 2)
        pinVibrator = 5;
      if (incomingByte == 3)
        pinVibrator = 6;
      if (incomingByte == 4)
        pinVibrator = 11;
      Serial.println(incomingByte);
      tone(pinVibrator, 440, 100);
    }
  }
}
