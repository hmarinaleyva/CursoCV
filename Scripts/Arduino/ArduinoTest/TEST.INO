String message; 
#define PIN_BUZZER  11  // Definir el pin de salida del BUZZER
#define PIN_UP      5   // Definir el pin de salida del BUZZER
#define PIN_DOWN    4   // Definir el pin de salida del BUZZER
#define PIN_LEFT    3   // Definir el pin de salida del BUZZER
#define PIN_RIGHT   2   // Definir el pin de salida del BUZZER

void setup() {
    // Inicializar el buzzer
    pinMode(PIN_BUZZER, OUTPUT);
    Serial.begin(9600); // opens serial port, sets data rate to 9600 bps
}

void loop() {
  
    // Melodía de inicio
    tone(PIN_BUZZER, 880, 150); delay(50); tone(PIN_BUZZER, 440, 150);
    
    // Comunicación serial
    while(1){
        while (Serial.available() == 0) {}  //wait for data available
        message = Serial.readString();      //read until timeout
        message.trim();                     // remove any \r \n whitespace at the end of the String
        if (message == "HAND_OUT"){
            tone(PIN_BUZZER, 440, 50); delay(50); tone(PIN_BUZZER, 220, 50);
        }
        if (message == "HAND_IN"){
            tone(PIN_BUZZER, 220, 50); delay(50); tone(PIN_BUZZER, 440, 50);
        }
        if (message == "UP"){
            tone(PIN_UP, 220, 100);
        }
        if (message == "DOWN"){
            tone(PIN_DOWN, 220, 100);
        }
        if (message == "LEFT"){
            tone(PIN_LEFT, 220, 100);
        }
        if (message == "RIGHT"){
            tone(PIN_RIGHT, 220, 100);
        }
        Serial.println(message);
    }
}