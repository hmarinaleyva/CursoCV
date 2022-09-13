# Curso CIMTT - Visión Artificial y accionamiento remoto
![](https://i.imgur.com/juUG1xu.png)

E-mail: cursos.cimtt@gmail.com

## Guía de instalación en Windows

### 1. Instalación de [Git](https://git-scm.com/)

 Cambiar la [directiva de ejecución](https://docs.microsoft.com/es-es/powershell/module/microsoft.powershell.core/about/about_execution_policies) de PowerShell en el equipo Windows usando el comando `Set-ExecutionPolicy`.

```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Verificar cambios de la directiva de ejecución.

```
Get-ExecutionPolicy -List
```

Instalar Git
```
winget install --id Git.Git -e --source winget
```

Configurar Git
```
git config --global user.name CimttGit
git config --global user.email cursos.cimtt@gmail.com
git config --global credential.helper store
git config --list
```

Crear en una carpeta local `CursosCIMTT` en el escritorio para almacenar el repositorio del curso CIMTT.

```
mkdir ~\Desktop\CursosCIMTT
cd ~\Desktop\CursosCIMTT
```

Clonar repositorio en la carpeta local.

```
git clone https://github.com/CimttGit/CursoCV.git
```

### 2. Crear un entorno de programación

[Instalar virtualenv usando pip](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) para administrar paquetes de Python para diferentes proyectos. (Se recomienda instalar [python3.8.3](https://www.python.org/downloads/release/python-383/))

```
py -m pip install --user virtualenv
```

Crear entorno virtual `VirtualTest` dentro de la carpeta `CursosCIMTT` junto a la carpeta del repositorio clonado `CursoCV`. 

```
virtualenv VirtualTest
.\VirtualTest\Scripts\activate
```

**NOTA:** Para desactivar el entorno virtual (`VirtualTest`) use el comando `deactivate`.

### 3. Instalar requerimientos para el entorno virtual

Instalar paquetes en el entorno virtual `VirtualTest`.

```
pip install mediapipe
```

Con el comando `pip freeze` podemos ver los paquetes instalados en nuestro virtual `VirtualTest`.

### 4. Verificar la instalación

Para verificar que se haya instalado correctamente el entorno virtual y que se haya instalado correctamente los paquetes hacemos correr el script `Test.py` con los siguientes comandos:

```
cd ~\Desktop\CursosCIMTT\
& .\VirtualTest\Scripts\python.exe .\CursoCV\Scripts\Test.py
```
![](https://i.imgur.com/VDtsdU2.gif)

## Guía de instalación de requerimientos en Raspbian (Raspberry Pi OS)

### 1. Instalación de mediapipe para RaspberryPi

Instalar dependencias
```
sudo apt install \
    ffmpeg python3-opencv python3-pip libxcb-shm0 \
    libcdio-paranoia-dev libsdl2-2.0-0 libxv1 libtheora0 libva-drm2 \
    libva-x11-2 libvdpau1 libharfbuzz0b libbluray2 libatlas-base-dev \
    libhdf5-103 libgtk-3-0 libdc1394-22 libopenexr23
```
Instalar el paquete de mediapipe para RaspberryPi

Para RaspberryPi 3 instalar el paquete [mediapipe-rpi3 mediante PyPI](https://pypi.org/project/mediapipe-rpi4/)

```
sudo pip3 install mediapipe-rpi3
```

Para RaspberryPi 4 instalar el paquete [mediapipe-rpi4 mediante PyPI](https://pypi.org/project/mediapipe-rpi4/)

```
sudo pip3 install mediapipe-rpi4
```

### 2. Instalación de depthia para Raspbian (para sensores de profundidad)
Instalar las dependencias depthia en el sistema opetativo

```
sudo apt install curl
sudo curl -fL https://docs.luxonis.com/install_dependencies.sh | bash
```
Reglas USB
```
echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="03e7", MODE="0666"' | sudo tee /etc/udev/rules.d/80-movidius.rules
sudo udevadm control --reload-rules && sudo udevadm trigger
```

Instalar de depthia a través de PyPi:

```
python3 -m pip install depthai
```

Clonar repositorios asosiados a depthia

```
git clone https://github.com/luxonis/depthai.git
git clone https://github.com/luxonis/depthai-python.git
```

Clonar otros repositorios de interés inteligencia artificial

```
git clone https://github.com/geaxgx/depthai_hand_tracker.git
```

3. Crear un entorno de programación
Crear en una carpeta local `CursosCIMTT` en el escritorio para almacenar el repositorio del curso CIMTT.

```
mkdir ~/Desktop/CursosCIMTT
cd ~/Desktop/CursosCIMTT
```

Clonar repositorio del curso de visión artificial en la carpeta local.

```
git clone https://github.com/CimttGit/CursoCV.git
```


Instalar [virtualenv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) en Raspbian usando pip para administrar paquetes de Python para diferentes proyectos.

```
python3 -m pip install --user virtualenv
```

Crear entorno virtual `VirtualTest` dentro de la carpeta del repositorio clonado `CursoCV`. 

```
virtualenv VirtualTest
source ./VirtualTest/bin/activate
```

Para desactivar el entorno virtual (`VirtualTest`) use el comando `deactivate`.

### 3. Provisionar entorno virtual

Instalar paquetes dentro del entorno virtual `VirtualTest`.

```
pip install mediapipe
pip install pyserial
```

Con el comando `pip freeze` podemos ver los paquetes instalados en nuestro virtual `VirtualTest`.

### 4. Verificar la instalación

Para verificar que se haya instalado correctamente el entorno virtual y que se haya instalado correctamente los paquetes hacemos correr el script `Test.py` con los siguientes comandos:

```
cd ~/Desktop/CursosCIMTT/
./VirtualTest/bin/python ./CursoCV/Scripts/Test.py
```

## Instalación de arduino-cli para Raspbian

```
cd
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
PATH=$PATH:/home/pi/bin
sudo reboot
```

### 2. Crear un sketch usando arduino-cli desde Raspbian

```
arduino-cli config init
arduino-cli sketch new ~/Desktop/CursosCIMTT/CursoCV/Scripts/Arduino/ArduinoTest
nano ~/Desktop/CursosCIMTT/CursoCV/Scripts/Arduino/ArduinoTest/ArduinoTest.ino
```

### 3. Editar sketch arduino

Usando nano editor:
```
nano ~/Desktop/CursosCIMTT/CursoCV/Scripts/Arduino/ArduinoTest/ArduinoTest.ino
```

En primera instancia, se visualizara el archivo creado de la siguiente manera:

```
void setup() {
}

void loop() {
}
```

En este caso, modificar el archivo para que contenga el siguiente código de modo que se suene un BUZZER conectado al PIN 11 de un arduinio conectado a la Raspberry Pi. (Véase pin-out de un Arduino UNO R3 [aquí](https://elosciloscopio.com/wp-content/uploads/2021/03/Tutorial-de-Arduino-Uno-Pinout.png) ).


```
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
```

Anote el puerto y el fqbn de su placa de arduino (en este caso, el puerto es `/dev/ttyACM0` y el fqbn es `arduino:avr:mega` para un Arduino Mega)

```
arduino-cli board list
```

Instale el core dasosiado a su placa Arduino (en este caso `arduino:avr`)

```
arduino-cli core install arduino:avr
```

Luego, compilar el código desde la carpeta contenedora de proyectos `Arduino` para un arduino mega

```
cd ~/Desktop/CursosCIMTT/CursoCV/Scripts/Arduino
arduino-cli compile --fqbn arduino:avr:mega ./ArduinoTest
```

y finalmente subir el skech a la placa de Arduino

```
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:mega ./ArduinoTest
```

Nota: en linux se se otorgan los permidod al puerto ttyACM0 para poder subir el skech

```
ls /dev/ttyACM0
sudo chmod a+rw /dev/ttyACM0
```

Para ejecutar desde un script python para compilar y subir un skech para una placa Arduino Uno conectada al puerto `/dev/ttyACM0`

```
import os

MainDir = os.path.dirname(os.path.abspath(__file__))
ArduinoSketchDir = os.path.join(MainDir, '.', 'Arduino/ArduinoTest')
os.chdir(ArduinoSketchDir)

try:
    os.system("arduino-cli compile --fqbn arduino:avr:uno")
    os.system("arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:uno")
except:
    os.system("arduino-cli config init --overwrite")
    os.system("arduino-cli core install arduino:avr")
    os.system("sudo chmod a+rw /dev/ttyACM0")
    os.system("arduino-cli compile --fqbn arduino:avr:uno")
    os.system("arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:uno")
```

## Ilustraciones de instalación manual de programas requeridos en Windows
### Instalación de [Visual Studio Code](https://code.visualstudio.com/docs/?dv=win)
![](https://i.imgur.com/5tfa7up.png)
![](https://i.imgur.com/0Nqe6mK.png)
![](https://i.imgur.com/gbNHnJL.png)
![](https://i.imgur.com/8r1sDFY.png)
![](https://i.imgur.com/T7t1Ht1.png)
![](https://i.imgur.com/qviXMLc.png)

![](https://i.imgur.com/lEygfaJ.png)
![](https://i.imgur.com/UNsMgHQ.png)

#### Instalación de [Python 3.7.0](https://www.python.org/downloads/release/python-370/)
![](https://i.imgur.com/uXoiysa.png)
![](https://i.imgur.com/1vPWl7H.png)
![](https://i.imgur.com/qbUFs15.png)
![](https://i.imgur.com/GKTVXrr.png)
![](https://i.imgur.com/UtamXxG.png)

### Instalación de [git](https://git-scm.com/download/win)
![](https://i.imgur.com/PRnouTE.png)
![](https://i.imgur.com/Ulm0K9I.png)
![](https://i.imgur.com/kqXFfrO.png)
![](https://i.imgur.com/LFDnSXQ.png)
![](https://i.imgur.com/xayzdCs.png)
![](https://i.imgur.com/SdBiSyj.png)
![](https://i.imgur.com/O82BH1T.png)
![](https://i.imgur.com/W4UDwMz.png)
![](https://i.imgur.com/MNj1KFq.png)
![](https://i.imgur.com/xbMeeMM.png)
![](https://i.imgur.com/7wiEv2o.png)
![](https://i.imgur.com/BA1QQUA.png)
![](https://i.imgur.com/OwtjZCV.png)
![](https://i.imgur.com/lRJCFIX.png)
![](https://i.imgur.com/YJizwQl.png)

![](https://i.imgur.com/sR7fT1E.png)


Link YoloV7:
https://drive.google.com/uc?export=download&id=1TmtLbJdcKftUZ9ybVOlSkKQr-pCD6bYL