import logging
from datetime import time
from gzip import open as openg
from logging.handlers import RotatingFileHandler


from os.path import dirname, exists, isdir
from os import remove, getcwd, rename, makedirs


from Source.Config import BRR



class Log(RotatingFileHandler):
    def __init__(self, filename=r'log\log.txt', **kws):
        try:
            self.check_dir_exist(dirname(filename))
            backupCount = kws.get('backupCount', 0)
            self.backup_count = backupCount
            self.filename = filename
            RotatingFileHandler.__init__(self, filename, **kws)
        except Exception as e: print(f'ERRO EM INICIAR CLASSE {filename} {e}')


    def doArchive(self, old_log):
        try:
            with open(old_log) as log:
                with openg(old_log + '.gz', 'wb') as comp_log:
                    comp_log.writelines(map(lambda x: bytes(x, "utf8"), log.readlines()))
            remove(old_log)
        except Exception as e: print(f'ERRO EM COMPACTAR {old_log} {e}')


    def doRollover(self):
        try:
            if self.stream:
                self.stream.close()
                self.stream = None
            if self.backup_count > 0:
                for i in range(self.backup_count - 1, 0, -1):
                    sfn = "%s.%d.gz" % (self.baseFilename, i)
                    dfn = "%s.%d.gz" % (self.baseFilename, i + 1)
                    if exists(sfn):
                        if exists(dfn):
                           remove(dfn)

                        # rename(sfn -> dfn)
                        with openg(sfn, "rb") as s, openg(dfn, "wb") as d:
                            d.writelines(s.readlines())
                        
                        remove(sfn)
            
            dfn = self.baseFilename + f".1"
            if exists(dfn):
                remove(dfn)
            if exists(self.baseFilename):
                rename(self.baseFilename, dfn)
                self.doArchive(dfn)
            if not self.delay:
                self.stream = self._open()
        except Exception as e: print(f'ERRO NA ROTACAO DO LOG {e}')


    def check_dir_exist(self, caminho):
        try: 
            if(not isdir(caminho)): makedirs(caminho); print(f'CRIANDO A PASTA {caminho} COM SUCESSO')
        except Exception as erro: print(f'ERRO EM CRIAR A PASTA {erro}')



def mainlog(msg, tipo=1, arq=getcwd()+BRR+'log'+BRR+'log.log', 
            mask_g='%(asctime)s - (%(levelname)-8s): %(message)s',
            mask_d='%d/%m/%Y %H:%M:%S', size_max=50000000, size_rotate=10):
    try:
        tipos = {1: 'info', 2: 'warning', 3: 'error', 4: 'critical'}

        tipo = tipo if isinstance(tipo, int) else 1 if tipo else 2 if not tipo else tipo
        
        colors = {1: f"\033[94m{msg}\033[0;0m", 2: f"\033[93m{msg}\033[0;0m", 
                3: f"\033[1;35m{msg}\033[0;0m", 4: f"\033[91m{msg}\033[0;0m"}
        print(colors[tipo])
    
        f = lambda x: eval(f"logging.{tipos[tipo].upper()}")
        
        logging.basicConfig(handlers=[Log(arq, maxBytes=size_max,
                                          backupCount=size_rotate)],
                            level=f(tipo),
                            format= mask_g, datefmt=mask_d)
        log = {x: eval(f"logging.{tipos[x]}") for x in tipos}
        log[tipo](msg)
    except Exception as e: print(f'ERRO EM IMPRIMIR O LOG E GRAVAR EM ARQUIVO {e}')



def calcularTempo(f):
    def method(*args, **kwargs):
        tempoIni = time()
        r = f(*args, **kwargs)
        mainlog(f'TEMPO LEVADO PARA ({f.__name__}) REALIZAR {time() - tempoIni}', None)
        return r
    return method



def log(func):
    def method(*args):
        try:
            argumentos = func(*args)
            log = argumentos[0] if(isinstance(argumentos, tuple)) else argumentos

            try: tipo = argumentos[1]
            except: tipo = True
            
            try: log = argumentos[0]
            except: log = None

            mainlog(msg=log, tipo=tipo)
            return argumentos
        except Exception as erro: return f"ERRO EM GERAR LOG {func} --- {args}"
    return method
