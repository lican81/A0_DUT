# A0_DUT

README for setting up python environment and microcontroller on host PC

1) Install python 3 on host PC (https://www.python.org/). Use whatever IDE you like, but VS Code is pretty great and comes built in to HP laptops

2) pip should be installed with python, check in powershell/terminal with pip --version to ensure pip is installed
  a. NOTE: on the hpe network, we can frequently run into SSL firewall issues. if you're getting repeated SSL errors while using github or pip for installations, you need to use "pip install program --proxy=https://web-proxy.labs.hpecorp.net:8088"
  b. Not an issue generally on hpeinternet wifi.

3) (Optional) set up virtual environment for python (makes easy to manage installations)
  a. https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/
  b. install venv package with (for windows Powershell only. Follow the above link for Linux/Mac)
  
        $ py -m pip install --upgrade pip
        $ py -m pip install --user virtualenv
        $ py -m venv ~/.venvs/py37 
    
  c. activate the virtual environment
  
        $ ~/.venvs/py37/Scripts/activate.ps1
        
  d. In vscode (after you've installed the Python extension), open settings (file->preferences->settings) and search for python or venv. You should eventually get to a settings.json file that vs code tells you to edit. in this file type 
  $ "python.pythonPath" : "C:\\Users\\localuser\\...." 
  
  where inside the " " should be the python.exe file location for your virual environment. e.g. "C:\\Users\\localuser\\~\\.venvs\\py37\\Scripts\\python.exe"
    

4) Pull code from this Github repository to your host PC, note the project folder location
  a. If using GItHub desktop and you need to get the proxy working, 
    1)	Make sure you’ve downloaded git, and have opened github desktop
    2)	Under C:->users -> *your username* you should find a .gitconfig fie
    3)	Add the following lines to this file
      [http]
	      proxy = http://web-proxy-pa.labs.hpecorp.net:8088
      [https]
	      proxy = https://web-proxy-pa.labs.hpecorp.net:8088

5) Get all the packages you'll need to run the code. Two ways:

      a. In the github repository, there is a txt file with all modules, so just run:
    
        $ pip install -r requirements.txt
  
      b. Use pipenv. Pipenv manages dependencies on a per-project basis. To install packages, change into the project’s directory (where ...A0_DUT\notebooks is located) and run:

        $ cd project_folder
        $ pipenv install requests

      Pipenv will install the excellent Requests library and create a Pipfile for you in your project’s directory. The Pipfile is used to track which dependencies your project needs in case you need to re-install them, such as when you share your project   with others. Then in commend line, run:

        $ pipenv run python setup.py

      which will create a pipfile for the project

  Both a,b should work, requirements.txt just needs to be kept up to date.
  
  Optional: if you want the jupyterlab variable inspector (matlab-like, see https://github.com/lckr/jupyterlab-variableInspector    /blob/master/README.md), you'll also need to do the following:
    
    $ jupyter labextension install @lckr/jupyterlab_variableinspector

6) While in github repository location, run 'jupyter lab' and an interactive python notebook will open in the browser

7) Plug in USB cables to PIC microcontroller. Open 'Device Manager'. You will see two USB COM ports become active in the Device Manager list under 'Ports'. One of these COM ports will be the communication to the PIC that you will need to change in the python code. The other COM port is a 'listening' port to check that the PIC is active. If you want to use this monitoring, open Putty (or other SSH/serial utility), specify a serial connection on (e.g.) COM9 with speed 115200. 
