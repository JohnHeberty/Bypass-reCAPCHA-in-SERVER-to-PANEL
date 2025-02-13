from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from pathlib import Path
import psutil
import time
import os

Driver = None  # Variável global para armazenar o WebDriver

def getDriver():
    global Driver
    if Driver is None:
        print(f"[INFO].{time.time()}...ABRINDO NAVEGADOR")
        try:
            finalizar_processo("undetected_chromedriver.exe")
            
            # Configuração do ChromeOptions
            chrome_options = Options()
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Evita ser detectado como bot
            chrome_options.add_argument("--no-sandbox")  # Recomendado para evitar problemas de permissão
            chrome_options.add_argument("--disable-dev-shm-usage")  # Evita erros em sistemas com pouca memória
            chrome_options.add_argument("--disable-infobars")  # Remove avisos de automação
            chrome_options.add_argument("--remote-debugging-port=9222")  # Debugging remoto

            # Inicializa o WebDriver do Chrome
            Driver = uc.Chrome(options=chrome_options, headless=False, use_subprocess=False)
            Driver.set_page_load_timeout(60)
            Driver.set_script_timeout(120)

            # Acessar o site
            Driver.get("https://www.alelofrota.com.br/login")
            
            # Espera até que o botão de aceitar cookies esteja presente e clicável
            try:
                wait = WebDriverWait(Driver, 10)
                cacheAccept = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
                cacheAccept.click()
                print(f"[INFO].{time.time()}...ACEITE DE COOKIES CONCLUÍDO")
            except Exception:
                print(f"[WARNING]...BOTÃO DE COOKIES NÃO ENCONTRADO OU JÁ ACEITO")
            print(f"[INFO].{time.time()}...BROWSER ABERTO COM SUCESSO")
            return Driver
        except Exception as e:
            print(f"[ERROR].{time.time()}...ERRO NA ABERTURA DO NAVEGADOR: {e}")
            return None
    else:
        print(f"[INFO].{time.time()}...USANDO DRIVER EXISTENTE")
        return Driver

def click(x, y):
    try:
        # 🔹 Verifica se o Selenium Driver está inicializado
        if not Driver:
            print("[ERROR]... O WEBDRIVER NÃO ESTÁ INICIALIZADO.")
            return
        
        # 🔹 Obtém o tamanho da janela do navegador
        window_size = Driver.get_window_size()
        max_x = window_size["width"]
        max_y = window_size["height"]

        # 🔹 Verifica se as coordenadas estão dentro dos limites da tela
        print(f"[INFO]... CLIQUE vs SIZE WINDOS! X={x}, Y={y} (Limites: {max_x}x{max_y})")
        if x < 0 or y < 0 or x >= max_x or y >= max_y:
            return

        # 🔹 Move para a posição e realiza o clique
        action = ActionBuilder(Driver)
        action.pointer_action.move_to_location(x, y)
        action.pointer_action.click()
        action.perform()

        print(f"[INFO]... CLIQUE REALIZADO EM X={x}, Y={y}")

    except Exception as e:
        print(f"[ERROR]... ERRO AO TENTAR CLICAR: {e}")

def finalizar_processo(nome_processo):
    """ Finaliza qualquer processo pelo nome, incluindo seus processos filhos. """
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        try:
            if nome_processo.lower() in proc.info['name'].lower():
                pid = proc.info['pid']
                processo = psutil.Process(pid)
                # 🔹 Finaliza processos filhos primeiro
                for child in processo.children(recursive=True):  # Encontra e finaliza filhos
                    print(f"[INFO]...Finalizando processo filho: {child.name()} (PID: {child.pid})")
                    child.terminate()
                # 🔹 Agora finaliza o processo principal
                print(f"[INFO]...Finalizando processo: {proc.info['name']} (PID: {pid})")
                processo.terminate()

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        
def excluir_undetected_chromedriver():
    try:
        # Obtém o diretório do usuário independentemente do sistema operacional
        user_dir = Path.home()
        caminho_arquivo = os.path.join(user_dir,"AppData","Roaming","undetected_chromedriver","undetected_chromedriver.exe")

        # Finaliza o processo antes de excluir o arquivo
        finalizar_processo("undetected_chromedriver.exe")
        
        # Verifica se o arquivo existe antes de tentar excluir
        if os.path.exists(caminho_arquivo):
            os.remove(caminho_arquivo)
            print(f"[INFO]...ARQUIVO EXCLUÍDO: {caminho_arquivo}")
        else:
            print(f"[WARNING]...ARQUIVO NÃO ENCONTRADO: {caminho_arquivo}")

    except Exception as e:
        print(f"[ERROR]...ERRO AO EXCLUIR O ARQUIVO: {e}")

# def alelofrota():
#     try:

#         # Lê a imagem com OpenCV
#         image = cv.imread(screenshot_path)
#         if image is None:
#             return "Erro: Falha ao carregar a imagem com OpenCV", 500

#         # Obtém dimensões
#         h, w = image.shape[:2]

#         # Define posição padrão caso os valores não existam
#         x, y, width, height = 100, 100, 200, 200

#         # Localiza o reCAPTCHA na página
#         reCAPTCHA = driver.execute_script("""
#             return document.querySelector("[title='reCAPTCHA']");
#         """)

#         if reCAPTCHA:
#             width, height = reCAPTCHA.get_dom_attribute('width'), reCAPTCHA.get_dom_attribute('height')
#             x, y = reCAPTCHA.get_attribute('offsetLeft'), reCAPTCHA.get_attribute('offsetTop')
#             xw, yw = driver.execute_script("return window.innerWidth"), driver.execute_script("return window.innerHeight")

#             if width and height and x and y:
#                 x = int(eval(x))
#                 y = int(eval(y))
#                 height = int(eval(height))
#                 width = int(eval(width))

#         # Ajusta para proporção correta
#         y = int(y * (h/yw))
#         x = int(x * (w/xw))
#         height = int(height * (h/yw))
#         width = int(width * (w/xw))

#         # Recorta a imagem e verifica se há erro
#         if y + height > h or x + width > w:
#             return "Erro: Recorte fora dos limites da imagem", 500

#         cropped_image = image[y:y+height, x:x+width]

#         if cropped_image is None or cropped_image.size == 0:
#             return "Erro: O recorte da imagem está vazio", 500

#         # Salva a imagem recortada como cut.jpeg na pasta static
#         cropped_path = os.path.join(IMAGE_FOLDER, "static/reCAPTCHA.png")
#         cv.imwrite(cropped_path, cropped_image)
#         try:
#             os.remove("website.jpeg")
#         except:
#             pass

#         return "Imagem recortada salva com sucesso!"

#     except Exception as e:
#         return f"Erro ao processar a imagem: {e}", 500

# @app.route('/reCAPTCHA')
# def index():
#     return render_template_string('''
#         <!DOCTYPE html>
#         <html lang="pt">
#             <head>
#                 <meta charset="UTF-8">
#                 <meta name="viewport" content="width=device-width, initial-scale=1.0">
#                 <title>Exibir reCAPTCHA</title>
#             </head>
#             <body>
#                 <h1>Imagem do reCAPTCHA</h1>
#                 <img src="{{ url_for('static', filename='reCAPTCHA.png') }}" alt="Imagem do reCAPTCHA" width="300">
#             </body>
#         </html>
#     ''')
