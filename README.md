# Curso CIMTT - Computer Vision

E-mail: cursos.cimtt@gmail.com

## Guía de installación en Windows

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

Crear en una capteta local `CursosCIMTT` para almacenar el repocitorio del curso CIMTT.

```
mkdir ~\Desktop\CursosCIMTT
cd ~\Desktop\CursosCIMTT

```
Clonar repositorio en la carpeta local.

```
git clone https://github.com/CimttGit/CursoCV.git
```

### 2. Crear entorno de programación

[Instalar virtualenv usando pip](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) para administrar paquetes de Python para diferentes proyectos. (Se recomienda instalar [python3.8.3](https://www.python.org/downloads/release/python-383/))

```
py -m pip install --user virtualenv
```

Crear entorno virtual `VirtualCV` dentro de la carpeta del repositoro clonado `CursoCV`. 

```
virtualenv VirtualCV
.\VirtualCV\Scripts\activate
```

Para desacticar el entorno virtual use el comando `deactivate`.

### 3. Instalar requerimientos

Instalar paquetes en el entorno virtual `VirtualCV`.

```
pip install mediapipe
pip install easyocr
```

Con el comando `pip freeze` podemos ver los paquetes instalados en nuestro virtual `VirtualCV`.

### 4. Verificar la instalación

Para verificar que se haya instalado correctamente el entorno virtual y que se haya instalado correctamente los paquetes hacemos correr el scrit `Test.py` con los siguientes comandos:

```
cd ~/Desktop/CIMTT/CursosCIMTT/
& ./VirtualCV/Scripts/python.exe ./Scripts/Test.py
```
![](https://i.imgur.com/y2rYSgk.gif)

## Ilustraciónes de instalación manual de programas requeridos en Windows
### Installación de [Visual Studio Code](https://code.visualstudio.com/docs/?dv=win)
![](https://i.imgur.com/5tfa7up.png)
![](https://i.imgur.com/0Nqe6mK.png)
![](https://i.imgur.com/gbNHnJL.png)
![](https://i.imgur.com/8r1sDFY.png)
![](https://i.imgur.com/T7t1Ht1.png)
![](https://i.imgur.com/qviXMLc.png)

![](https://i.imgur.com/lEygfaJ.png)
![](https://i.imgur.com/UNsMgHQ.png)

#### Installación de [Python 3.7.0](https://www.python.org/downloads/release/python-370/)
![](https://i.imgur.com/uXoiysa.png)
![](https://i.imgur.com/1vPWl7H.png)
![](https://i.imgur.com/qbUFs15.png)
![](https://i.imgur.com/GKTVXrr.png)
![](https://i.imgur.com/UtamXxG.png)

### Installación de [git](https://git-scm.com/download/win)
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