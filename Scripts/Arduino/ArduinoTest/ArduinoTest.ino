int dato; 
#define PIN_BUZZER  11  // Definir el pin de salida del BUZZER
#define PIN_UP      5   // Definir el pin de salida del BUZZER
#define PIN_DOWN    4   // Definir el pin de salida del BUZZER
#define PIN_LEFT    3   // Definir el pin de salida del BUZZER
#define PIN_RIGHT   2   // Definir el pin de salida del BUZZER


void setup() {
  Serial.begin(9600, SERIAL_8N1); // opens serial port, sets data rate to 9600 bps
  pinMode(PIN_BUZZER, OUTPUT);
  
  // Melodía de inicio
  //tone(PIN_BUZZER, 880, 150); delay(50); tone(PIN_BUZZER, 440, 150);
  digitalWrite(PIN_BUZZER, LOW);
}

void loop() {
    // Comunicación serial
    if (Serial.available() > 0) { // Si hay datos en el puerto serie
        
        dato = Serial.read(); // Lee el dato enviado por el puerto serie usando código ASCII
        
        if (dato == 48){ // Si el dato enviado es 0 (48 codificado en ASCII) 
            //Serial.println(dato); // Envia el dato de regreso por el puerto serie codificado en ASCII
            Serial.write("0"); // Envia el dato por el puerto serie codificado en ASCII
        }
        
        if (dato == 49){ // Si el dato enviado es 1 (49 codificado en ASCII) 
            tone(PIN_BUZZER, 440, 50); 
            delay(50);
            tone(PIN_BUZZER, 220, 50);
        }
        if (dato == 50){ // Si el dato enviado es 2 (50 codificado en ASCII)
            tone(PIN_BUZZER, 220, 50);
            delay(50);
            tone(PIN_BUZZER, 440, 50);
        }

        // Interfaz de control háptico
        if (dato == 51){ // Si el dato enviado es 3 (51 codificado en ASCII)
            tone(PIN_UP, 220, 100); // Activa el vibrador UP por 100 ms
        }
        if (dato == 52){ // Si el dato enviado es 4 (52 codificado en ASCII)
            tone(PIN_DOWN, 220, 100); // Activa el vibrador DOWN por 100 ms
        }
        if (dato == 53){ // Si el dato enviado es 5 (53 codificado en ASCII)
            tone(PIN_LEFT, 220, 100); // Activa el vibrador LEFT por 100 ms
        }
        if (dato == 54){ // Si el dato enviado es 6 (54 codificado en ASCII)
            tone(PIN_RIGHT, 220, 100); // Activa el vibrador RIGHT por 100 ms
        }
    }
}