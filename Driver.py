from typing import Sequence, Tuple, Union, Literal

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from time import sleep
from datetime import datetime

from PIL import Image
from io import BytesIO

from Source.Config import PATH_APP_DRIVER, PATH_TEMP, PATH_LOG
from Source.Log import mainlog

class Driver:
    def __init__(self, tempolimite=60):
        options = Options()
        
        options.add_argument("--start-maximized")
        options.add_argument('--disable-dev-shm-usage')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--ignore-certificate-erros')
        options.add_argument('--no-sandbox')
        #options.add_argument('--kiosk-printing')

        options.add_experimental_option('prefs',{
            "download.default_directory": PATH_TEMP,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "plugins.plugins_disabled": ["Chrome PDF Viewer"],
            "plugins.always_open_pdf_externally": True
        })
        
        dr = PATH_APP_DRIVER
        self.dr = webdriver.Chrome(options=options, executable_path=dr)
        self.Print("Chrome driver iniciado com sucesso")
        
        self.dr.set_script_timeout(tempolimite)
        self.dr.set_page_load_timeout(tempolimite)
        self.dr.implicitly_wait(1) # Tempo de interacao com a pagina
    

    def FecharAba(self) -> None:
        "Fecha a aba ativa e troca para a ultima disponivel"
        
        try:
            self.dr.close()		
            sleep(1)
            self.IrUltimaJanela()
            self.Print("Janela fechada com sucesso!")
        except Exception as e: self.Print(f"Erro em fechar janela: {e}", 3)
    
    
    def FecharUltimaAba(self) -> None:
        "Fecha a ultima aba aberta e troca para a ultima disponivel"
        
        try:
            self.IrUltimaJanela()
            self.dr.close()
            self.IrUltimaJanela()
            self.Print("Janela fechada com sucesso!")
        except Exception as e: self.Print(f"Erro em fechar janela: {e}", 3)
    
    
    def FecharAbasLimite(self, limite:int=1) -> None:
        "Fecha as todas as abas ate o numero de abas chegar no limite informado [padrao = 1]"
        
        try:
            if(limite <= 0): return
            
            count = 0
            while(self.VerificaQuantidadeAbas() > limite): 
                self.FecharUltimaAba()
                count += 1
            self.Print(f"Foram fechadas um total de {count} abas")
        except Exception as e: self.Print(f"Não foi possível fechar as últimas abas: {e}", 3)
    
    
    def IrUltimaJanela(self) -> None:
        "Troca para a ultima janela disponivel"
        
        try: self.dr.switch_to_window(self.dr.window_handles[-1])
        except: pass
    
    
    def VerificaQuantidadeAbas(self) -> int:
        "Retorna a quantidades de abas abertas no navegador"
        
        try: return len(self.dr.window_handles)
        except: return 0


    def RecarregarPagina(self) -> None:
        "Recarrega a pagina na aba ativa"
        
        self.dr.refresh()
        self.Print(f"Recarregando página {self.dr.current_url}")


    def AbrirUrl(self, link:str) -> None:
        "Abre uma nova aba com a url passada"
        
        try: 
            self.dr.execute_script(f"window.open('{link}', '_blank')")
            self.IrUltimaJanela()
            self.Print("Nova aba com aberta com sucesso")
        except Exception as e:
            self.Print(f"Não foi possível abrir uma nova aba com o link {link}: {e}", 3)


    def TirarPrintScreen(self, caminho:str="") -> Union[Image.Image, None]:
        """
        Tira uma captura de tela da aba ativa e retorna um objeto PIL.Image.Image. Caso seja passado
        o parametro caminho, ele salvará a imagem no caminho informado.
        """
                    
        try: 
            img = Image.open(BytesIO(self.dr.get_screenshot_as_png()))
            
            if(caminho):
                img.save(caminho)
                self.Print("Captura de tela feita e salva com sucesso")
            else:
                self.Print("Captura de tela feita com sucesso")
            
            return img
        except Exception as e:
            self.Print(f"Não foi possível tirar a screenshot da página: {e}", 3)
            return
        

    def VoltarPagina(self) -> None:
        "Volta para a ultima pagina da aba ativa"
        
        try: 
            self.dr.back()
            self.Print("Voltando a página")
        except Exception as e: self.Print(f"Não foi possível voltar a página: {e}", 3)

        
    def FecharDriver(self) -> None:
        "Finaliza a instância do chrome driver"
        
        try:
            self.dr.quit()
            self.Print("chrome driver fechado com sucesso")
        except Exception as e: self.Print(f"Não foi possível fechar chrome driver: {e}", 3)
    
            
    def VerificarAlerta(self) -> Tuple[str, bool]:
        """
        Verifica se há alguma caixa de dialogo na tela. Caso verdaderio, retorna uma tupla
        com seu conteudo e um booleano
        """
        
        try:
            return self.dr.switch_to.alert.text, True
        except:
            return "Sem nenhum alerta", False


    def FecharAlerta(self) -> bool:
        """
        Verifica se há alguma caixa de dialogo na tela. Caso verdaderio, fecha a caixa e
        retorna um booleano
        """
        
        try:
            self.dr.switch_to_alert().accept() 
            self.IrUltimaJanela()
            
            self.Print("Alerta fechado com sucesso")
            return True
        except: return False        
    
        
    def Print(self, msg:str, tipo:Literal[1, 2, 3, 4]=1) -> None:
        mainlog(f"{self.__class__.__name__};{msg}", tipo, arq=PATH_LOG+'log.log')


    def __del__(self): self.FecharDriver()