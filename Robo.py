from glob import glob
from shutil import move
from os.path import realpath, isfile, dirname, exists, isdir
from os import makedirs, chdir, remove, rename, getenv, getcwd

from time import sleep

from pyscreeze import Box
from pyautogui import ImageNotFoundException, hotkey, locateOnScreen, locateCenterOnScreen, \
                      click, size, screenshot, center, press

from typing import Any, List, Literal, Union, Sequence, Tuple

from Source.Config import *
from Source.Log import mainlog
from Source.Gerenciador import AppManager, PlanManager

#? Configurando variáveis globais
class RoboBase:
    images = {}
    infosExec = []
    now = PATH_TEMP
    caminhoTemp = PATH_TEMP
    caminhoArquivo = PATH_PDF
    
    
    def __init__(self, imgs:str, fase:Union[int, str], filtro:Union[bool, None]=None) -> None:
        self.fase = str(fase)
        self.maxX, self.maxY = size()
        
        self.resolution = getenv("PATH_IMAGES") if(f"{self.maxX}x{self.maxY}" == getenv("RESOLUTION")) else ""

        if(self.resolution):
            for arq in glob(BRR.join([self.resolution, imgs, "*.png"])):
                self.images[arq.split(BRR)[-1].split('.png')[0]] = arq

        if(isfile(PATH_INFOS + 'Jsons' + BRR + 'cache.json')):
            self.cache = PlanManager().LerJsonInfo(PATH_INFOS + 'Jsons' + BRR + 'cache.json')
        else:
            self.cache = { 'Lancamento' : True }
            PlanManager().SalvarJsonInfo(self.cache, PATH_INFOS + 'Jsons' + BRR + 'cache.json')
        
        self.json = PlanManager().LerJsonInfo()
        self.infosExec = self.GerarLista(fase, filtro)
        
        self.__staring__()

    
    def GerarLista(self, fase:Union[int, str], filtro:Union[bool, None]=None) -> list:
        "Cria e retorna uma lista com as empresa com o status passado"

        lista = []
        if(filtro is not None):
            for key in self.json.keys():
                if(int(self.json[key]['Status']) == int(fase) and
                   self.json[key]['Nota']['Tipo'] == filtro):
                    lista.append(key)
        
        else:
            for key in self.json.keys():
                if(int(self.json[key]['Status']) == int(fase)):
                    lista.append(key)

        return lista

    def FinalizarExecucao(self, items:Sequence[str], key:str, fase:Union[str, int]) -> None:
        """
            Vericia se todos os items passados estão no caminho padrão, altera o arquivo de execução
            de acordo com o resultado 200 = Sucesso | 500 = Erro
        """
        
        for x in items: fase = fase if(glob(self.caminhoArquivo+BRR+x)) else 500
        self.json[key]['Status'] = fase


    def MoverTempPadrao(self, arquivo:str, reName:str='', rmErro:bool=True, salvarErro:bool=True) -> None:
        """Move o arquivo passado de dentro do diretório temporario para o diretório padrão
        (self.caminhoArquivo), se o parâmetro reName é passado, o arquivo é renomeado.
        
        Se rmErro é verdadeiro, o arquivo original é apagado.
        
        Se salvarErro é verdadeiro, caso não há nenhum arquivo seja encontrado, salva uma screenshot.
        """
        
        if(glob(self.caminhoTemp+arquivo)):
            for arq in glob(self.caminhoTemp+arquivo):
                try:
                    if(reName): rename(move(arq, self.caminhoArquivo), self.caminhoArquivo+reName)
                    else: move(arq, self.caminhoArquivo)
                except:
                    if(rmErro): 
                        try: remove(arq)
                        except: pass
        else:
            if(salvarErro):
                self.Print(f"Não foi encontrado nenhum arquivo: {self.caminhoTemp+arquivo}")

 
    def MoverDirPadrao(self, arquivo:str, reName:str='', rmErro:bool=True, salvarErro:bool=True) -> None:
        """Move o arquivo passado para o diretorio padrão(self.caminhoArquivo), se o parâmetro reName é
        passado, o arquivo é renomeado.
        
        Se rmErro é verdadeiro, o arquivo original é apagado.
        
        Se salvarErro é verdadeiro, caso não há nenhum arquivo seja encontrado, salva uma screenshot.
        """
        
        if(glob(arquivo)):
            for arq in glob(arquivo):
                try:
                    if(reName): rename(move(arq, self.caminhoArquivo), self.caminhoArquivo+reName)
                    else: move(arq, self.caminhoArquivo)
                except:
                    if(rmErro): 
                        try: remove(arq)
                        except: pass
        else:
            if(salvarErro):
                self.Print(f"Não foi encontrado nenhum arquivo: {self.caminhoTemp+arquivo}")


    def VerificarArqPadrao(self, arquivo:str, reName:str='') -> bool:
        """Verifica se o arquivo passado está dentro do diretório padrão, usado principalmente
        para renomear o arquivo"""
        
        if(glob(self.caminhoArquivo+arquivo)):
            for arq in glob(self.caminhoArquivo+arquivo):
                try:
                    if(reName): rename(arq, self.caminhoArquivo+reName)
                    return True
                except: return False
        else: return False

      
    def SalvarFoto(self, NomeArquivo='screenshot_error') -> None:
        """Salva uma foto da tela com o nome passado"""
        
        try: screenshot(self.caminhoArquivo+NomeArquivo+'.png')
        except Exception as e: self.Print(f'Erro em salvar screenshot: {e}', 3)


    def Tentar(self, func, arg:str, tentativas:int=5, **args) -> Any:
        """Executa a função com os argumentos passados o número pelo número de tentativas"""
        
        for _ in range(tentativas):
            retorno = func(*arg)
            if(retorno): return retorno
            else: sleep(args.get('tempo', 1))
        else: return False


    def Clicar(self, img:Union[Sequence[str], str], co:Union[int, float]=0.8, **args) -> bool:
        """Procura e clica na imagem passada, o parâmetro co define a porcentagem de concordância
        com a imagem passada. É recomendado não deixar acima de 0.85"""
        
        def clk(info):
            pos = locateCenterOnScreen(self.images[info], confidence=co, grayscale=True)
            if(not pos): raise ImageNotFoundException
            else:
                click(x=pos.x, y=pos.y)
                return True
            
        return self.__looping__(img, clk, **args)


    def Localizar(self, img:Union[Sequence[str], str], co:Union[int, float]=0.8, **args) -> Box:
        """Procura a imagem passada e retorna uma classe Box com as cordenadas das imagens,  o 
        parâmetro co define a porcentagem de concordânciacom a imagem passada. É recomendado não deixar
        acima de 0.85"""
        
        return self.__looping__(img, lambda x: locateOnScreen(self.images[x], confidence=co, grayscale=True), **args)

 
    def IfLocalClick(self,
                     locate:Union[Sequence[str], str],
                     click:Union[Sequence[str], str],
                     tent:int=1) -> bool:
        """Localiza a imagem passada, se ela for encontrada, ele localiza e clica a segunda imagem"""
        
        if(self.Tentar(self.Localizar, (locate,), tentativas=tent)): 
            self.Tentar(self.Clicar, (click,), tentativas=tent); return True
        else: return False


    def IfLocal(self,
                locate1:Union[Sequence[str], str],
                locate2:Union[Sequence[str], str],
                tent:int=1) -> bool:
        """Localiza a imagem passada, se ela for encontrada, ele localiza e retorna Box com as
        cordenadas da segunda imagem"""
        
        if(self.Tentar(self.Localizar, (locate1,), tentativas=tent)):
            return self.Tentar(self.Localizar, (locate2,), tentativas=tent)
        else: return False


    def IfLocalClickCoordenadas(self,
                                locate:Union[Sequence[str], str],
                                x:int=0,
                                y:int=0,
                                tent:int=5,
                                Center:bool=False) -> bool:
        
        """Localiza a imagem passada, se ela for encontrada, é feito um clique nas coordenadas passadas
        utilizando a imagem como referência. Usando principalmente para mapeamento de janelas"""
        
        image = self.Tentar(self.Localizar, (locate, ), tentativas=tent)
        if(image):
            if(Center): click(x=center(image).x+x, y=center(image).y+y); return True
            else: click(x=image.left+x, y=image.top+y); return True
        else: return False


    def Print(self, msg:str, tipo:Literal[1, 2, 3, 4]=1) -> None: 
        mainlog(f"{self.__class__.__name__};{msg}", tipo, arq=PATH_LOG+'log.log')
    

    def __looping__(self, item:Union[Sequence[str], str], func, **args) -> Any:
        if(isinstance(item, (list, tuple, set))): 
            for i in item:
                retorno = self.__trying__(func, i)
                if(retorno): return retorno
                else: sleep(args.get('tempo', 0.1))
        else: return self.__trying__(func, item)
            
        return False


    def __trying__(self, func, *args) -> Any:
        try: return func(*args)
        except ImageNotFoundException as e: print(f"Imagem {args} nao encontrada: {e}", 2); return False
        except Exception as e: self.Print(f"Ocorreu um erro ao executar a funcao: {e}", 3); return False
    
    
    def __staring__(self) -> None:
        from os import get_terminal_size
        msg = f" Iniciando fase {self.fase} - Data: {TIME_NOW.strftime('%m/%Y')} "
        
        x, _ = get_terminal_size()
        tracos = "=" * ((x-len(msg))//2)
        mainlog(tracos+msg+tracos[:-1], 2, arq=PATH_LOG+'log.log')
    

    def __del__(self) -> None:
        PlanManager().SalvarJsonInfo(self.json)
        PlanManager().SalvarJsonInfo(self.cache, PATH_INFOS + 'Jsons' + BRR + 'cache.json')
        
        from os import get_terminal_size
        msg = f" Finalizando script - Data: {TIME_NOW.strftime('%m/%Y')} "
        
        x, _ = get_terminal_size()
        tracos = "=" * ((x-len(msg))//2)
        mainlog(tracos+msg+tracos[:-1], 2, arq=PATH_LOG+'log.log')