# Curso CIMTT - Visión Artificial y Accionamiento Remoto

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

Crear entorno virtual `VirtualTest` dentro de la carpeta del repositorio clonado `CursoCV`. 

```
virtualenv VirtualTest
.\VirtualTest\Scripts\activate
```

**NOTA:** Para desactivar el entorno virtual use el comando `deactivate`.

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
sudo apt install ffmpeg python3-opencv python3-pip libxcb-shm0 libcdio-paranoia-dev libsdl2-2.0-0 libxv1  libtheora0 libva-drm2 libva-x11-2 libvdpau1 libharfbuzz0b libbluray2 libatlas-base-dev libhdf5-103 libgtk-3-0 libdc1394-22 libopenexr23
```
Instalar el paquete [mediapipe-rpi3 mediante PyPI](https://pypi.org/project/mediapipe-rpi4/)
```
sudo pip3 install mediapipe-rpi3
```

### 1. Instalación de depthia para Raspbian
Instalación de dependencias depthia en el sistema opetativo través de PyPi:
```
sudo curl -fL https://docs.luxonis.com/install_dependencies.sh | bash
```
Instalación de depthia en el sistema opetativo través de PyPi:
```
python3 -m pip install depthai
```
clonar reppositorios asosiados a depthia:
```
git clone https://github.com/luxonis/depthai.git
git clone https://github.com/luxonis/depthai-python.git
```

Crear en una carpeta local `CursosCIMTT` en el escritorio para almacenar el repositorio del curso CIMTT.

```
mkdir ~/Desktop/CursosCIMTT
cd ~/Desktop/CursosCIMTT
```

Clonar repositorio del curso de visión artificial en la carpeta local.

```
git clone https://github.com/CimttGit/CursoCV.git
```

### 2. Crear un entorno de programación

[Instalar virtualenv usando pip](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) para administrar paquetes de Python para diferentes proyectos. (Se recomienda instalar [python3.8.3](https://www.python.org/downloads/release/python-383/))

```
python3 -m pip install --user virtualenv
```

Crear entorno virtual `VirtualTest` dentro de la carpeta del repositorio clonado `CursoCV`. 

```
virtualenv VirtualTest
source ./VirtualTest/bin/activate
```

Para desactivar el entorno virtual use el comando `deactivate`.

### 3. Instalar requerimientos para el entorno virtual

Instalar paquetes en el entorno virtual `VirtualTest`.

```
pip install mediapipe
```

Con el comando `pip freeze` podemos ver los paquetes instalados en nuestro virtual `VirtualTest`.

### 4. Verificar la instalación

Para verificar que se haya instalado correctamente el entorno virtual y que se haya instalado correctamente los paquetes hacemos correr el script `Test.py` con los siguientes comandos:

```
cd ~/Desktop/CursosCIMTT/
./VirtualTest/bin/python ./CursoCV/Scripts/Test.py
```

## Instalación de arduino-cli y depthia para Raspbian

```
cd ~/
git clone https://github.com/luxonis/depthai-python.git
sudo apt update && upgrade -y
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
PATH=$PATH:/home/CursoCV/bin
sudo reboot
```

### 2. Crear un sketch de arduino-cli para accionamiento desde Raspbian 

```
arduino-cli config init
arduino-cli sketch new test
nano ~/test/test.ino
```
### 3. Accionar sketch con Visión Artificial

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
```
git config --global user.name CimttGit
git config --global user.email cursos.cimtt@gmail.com
git config --global credential.helper store
git config --list
```
![](https://i.imgur.com/sR7fT1E.png)
