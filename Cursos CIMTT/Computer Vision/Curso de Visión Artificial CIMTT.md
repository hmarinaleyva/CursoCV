# Curso de Visión Artificial CIMTT

#### Cuenta cursos.cimtt@gmail.com
![](https://i.imgur.com/SOyQBhn.png)

#### Cuenta [GitHub](https://github.com/)
![](https://i.imgur.com/gEL1AIV.png)

## Guía de installación en Windows

### Configuración para empezar
###### Usando PowerShell

1. Cambiar la [directiva de ejecución](https://docs.microsoft.com/es-es/powershell/module/microsoft.powershell.core/about/about_execution_policies) de PowerShell en el equipo Windows usando el comando `Set-ExecutionPolicy`.
```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Get-ExecutionPolicy -List
```
2. Instalar y configurar [Git](https://git-scm.com/). En este caso se configura Git con la cuenta GitHub `CimttGit`. 

```
winget install --id Git.Git -e --source winget
git config --global user.name CimttGit
git config --global user.email cursos.cimtt@gmail.com
```
2. Crear repositorio local para el proyecto de visión artificial mediante [Git](https://git-scm.com/).

2. [Instalar virtualenv usando pip](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) para administrar paquetes de Python para diferentes proyectos. (Se recomienda instalar [python3.7.0](https://www.python.org/downloads/release/python-370/))
```
py -m pip install --upgrade pip
py -m pip install --user virtualenv
```

3. Crear entorno virtual `test` dentro de la carpeta principal de nuestro proyecto. Para activar y desactivar el entorno virtual ejecute los archivos `activate.bat` y `desactivate.bat` que se encuentran en la carpeta creada `.\test\Scripts`.

```
mkdir ProjectCV
cd .\ProjectCV\
py -m venv test
.\test\Scripts\activate
```
4. Instalar paquetes en el entorno virtual `test`.
```
py -m pip install --upgrade pip
pip install mediapipe
pip install easyocr
```

### Instalación de programas y requerimientos
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


### Installación de [Visual Studio Code](https://code.visualstudio.com/docs/?dv=win)
![](https://i.imgur.com/5tfa7up.png)
![](https://i.imgur.com/0Nqe6mK.png)
![](https://i.imgur.com/gbNHnJL.png)
![](https://i.imgur.com/8r1sDFY.png)
![](https://i.imgur.com/T7t1Ht1.png)
![](https://i.imgur.com/qviXMLc.png)

![](https://i.imgur.com/lEygfaJ.png)
![](https://i.imgur.com/UNsMgHQ.png)

```
git clone https://github.com/NicoGitSoft/BVI.git
```
![](https://i.imgur.com/vk6HpnL.png)


```
python -m pip install --user virtualenv
mkdir ProjectCV
cd .\ProjectCV\
virtualenv --system-site-packages -p python3 ./venv
.\venv\Scripts\activate
set PATH=%PATH%;C:\Users\USER\AppData\Roaming\Python\Python38\Scripts

```

```
python -m pip install -U wheel setuptools
pip install mediapipe
```
