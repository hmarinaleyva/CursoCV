int message; 
#define PIN_BUZZER  11  // Definir el pin de salida del BUZZER
#define PIN_UP      5   // Definir el pin de salida del BUZZER
#define PIN_DOWN    4   // Definir el pin de salida del BUZZER
#define PIN_LEFT    3   // Definir el pin de salida del BUZZER
#define PIN_RIGHT   2   // Definir el pin de salida del BUZZER


void setup() {
  Serial.begin(9600, SERIAL_8N1); // opens serial port, sets data rate to 9600 bps
  pinMode(PIN_BUZZER, OUTPUT);
}

void loop() {
  // Melodía de inicio
    tone(PIN_BUZZER, 880, 150); delay(50); tone(PIN_BUZZER, 440, 150);
    digitalWrite(PIN_BUZZER, LOW); 

    while(1){
        // Comunicación serial
        if (Serial.available() > 0) {
            // read the incoming byte:
            message = Serial.read() - 48;
            if (message == 1){
                tone(PIN_BUZZER, 440, 50); 
                delay(50);
                tone(PIN_BUZZER, 220, 50);
                Serial.println(message);
            }
            if (message == 2){
                tone(PIN_BUZZER, 220, 50);
                delay(50);
                tone(PIN_BUZZER, 440, 50);
            }
            if (message == 3){
                tone(PIN_UP, 220, 100);
            }
            if (message == 3){
                tone(PIN_DOWN, 220, 100);
            }
            if (message == 4){
                tone(PIN_LEFT, 220, 100);
            }
            if (message == 5){
                tone(PIN_RIGHT, 220, 100);
            }
        }
    }
}