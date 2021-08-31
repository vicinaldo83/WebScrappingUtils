from IPython.terminal.interactiveshell import TerminalInteractiveShell
TerminalInteractiveShell.instance()

from sys import path
from os.path import realpath
from datetime import datetime
from dotenv import load_dotenv
from os import getenv, chdir, makedirs, getcwd

BRR = '\\'


load_dotenv(getcwd() + r'\Source\options.env')


DEBUG = bool(int(getenv("DEBUG")))

DATA = getenv("DATA").split("/") if(getenv("DATA")) else None

TIME_NOW = datetime(year=int(input("Ano:")), month=int(input("Mes:")), day=int(input("Dia:"))) if(DEBUG) else \
           datetime(year=int(DATA[2]), month=int(DATA[1]), day=int(DATA[0])) if(getenv("DATA")) else \
           datetime.now()
           
PATH_APP_GESCON = getenv("PATH_APP_GESCON")

PATH_APP_DRIVER = getenv("PATH_APP_DRIVER")

PATH_APP_SISCOB = getenv("PATH_APP_SISCOB")

PATH_SCRIPT = getenv("PATH_SCRIPT")

PATH_FILES = getenv("PATH_FILES")

PATH_INFOS = getenv("PATH_INFOS")

PATH_PLAN = getenv("PATH_PLAN")

PATH_TEMP = getenv("PATH_TEMP")

PATH_PDF = getenv("PATH_PDF")

PATH_LOG = getenv("PATH_LOG")

#? Cria todos os diretorios de producao utilizados caso nao existem
chdir(realpath(PATH_SCRIPT))
for i in [PATH_SCRIPT, PATH_FILES, PATH_PLAN, PATH_TEMP, PATH_INFOS, PATH_PDF, PATH_LOG]:
    makedirs(realpath(i), exist_ok=True)
    path.append(i)
    

URL_GOV = getenv('URL_GOV')

LOGIN_GOV = getenv('LOGIN_GOV')

SENHA_GOV = getenv('SENHA_GOV')