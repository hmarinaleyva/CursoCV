#define PIN_BUZZER 11 // Definir el pin de salida del BUZZER
void setup() {
    // Inicializar el buzzer
    pinMode(PIN_BUZZER, OUTPUT);
    digitalWrite(PIN_BUZZER, LOW);
}

void loop() {
    // Hacer sonar el buzzer con una frecuencia de 440Hz (Nota A4) y duración de 1 segundo (1000 milisegundos)
    tone(PIN_BUZZER, 440, 1000);
    // Esperar media segundo
    delay(500);     
    // Hacer sonar el buzzer con una frecuencia de 880Hz (Nota B4) y duración de 1 segundo
    tone(PIN_BUZZER, 880, 1000);
    // detener loop de sonido con un buble infinito vacío
    while(1){ }
}