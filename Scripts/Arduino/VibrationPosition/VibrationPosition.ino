int incomingByte; // Para la entrada de datos en serie
int pinVibrator;  // Para selecionar pin de salida del vibrador

void setup() {
  Serial.begin(9600); // opens serial port, sets data rate to 9600 bps
}

void loop() {
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
