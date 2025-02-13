from flask import Flask, render_template, request, jsonify
from Config.Engine import configClient, configServer
from threading import Thread
from Browser import getDriver, click
from requests import post
import cv2 as cv
import base64
import time
import os

# se identificar rc-imageselect-payload abre mais a imagem
app     = Flask(__name__)

class TempSave:
    BaseBox = 400
    Driver  = None
    propH   = None
    propX   = None

# Criar pasta para armazenar imagens, se não existir
IMAGE_FOLDER = "static"
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

@app.route("/receiveCoordinateServer", methods=["POST"])
def receiveCoordinateServer():
    try:
        print(f"[INFO].{int(int(time.time()))}...RECEBENDO COORDENADAS")
        receive     = request.get_json()
        Width       = int(receive['Width'])
        Height      = int(receive['Height'])
        # Localiza o reCAPTCHA na página
        x_click = Width
        y_click = Height
        print(f"[INFO].{int(int(time.time()))}...EFETUNDO CLICK EM {x_click} X {y_click}")
        click(x_click, y_click)
        return {"Status": True}, 200
    except Exception as e:
        print(f"[ERROR]...{e}")
        return {"Status": False}, 400  # Retorna um erro 400 em caso de falha
    
# var select = document.querySelector('#rc-imageselect');
# select.offsetHeight 
app.route("/", methods=["GET"])
def EnviarImage():
    TempSave.Driver = getDriver()
    while True:
        if TempSave.Driver:
            try:
                # print(f"[INFO].{int(int(time.time()))}...ENVIANDO IMAGEM")
                IMAGE_FOLDER = os.path.join("static", "reCAPTCHA.png")
                try: os.remove(IMAGE_FOLDER)
                except: pass
                TempSave.Driver.save_screenshot(IMAGE_FOLDER)
                
                # Lê a imagem com OpenCV
                image = cv.imread(IMAGE_FOLDER)
                if image is None: return "Erro: Falha ao carregar a imagem com OpenCV", 500

                # Obtém dimensões
                h, w = image.shape[:2]

                # Define posição padrão caso os valores não existam
                x, y, width, height = 100, 100, 200, 200

                # Localiza o reCAPTCHA na página
                reCAPTCHA = TempSave.Driver.execute_script("""
                    return document.querySelector("[title='reCAPTCHA']");
                """)
                if reCAPTCHA:
                    width, height = reCAPTCHA.get_dom_attribute('width'), reCAPTCHA.get_dom_attribute('height')
                    x, y = reCAPTCHA.get_attribute('offsetLeft'), reCAPTCHA.get_attribute('offsetTop')
                    xw, yw = TempSave.Driver.execute_script("return window.innerWidth"), TempSave.Driver.execute_script("return window.innerHeight")
                    if width and height and x and y:
                        x = int(eval(x))
                        y = int(eval(y))
                        height = int(eval(height))
                        width = int(eval(width))

                # Ajusta para proporção correta
                propH = (h/yw)
                propW = (w/xw)
                y_ = int(y * propH)
                x_ = int(x * propW)
                height = int(height * propH)
                width = int(width * propW)

                # Recorta a imagem e verifica se há erro
                if y + height > h or x + width > w: return {"Status": False, "MSG": "Erro: Recorte fora dos limites da imagem"}, 500
                cropped_image = image[y_-TempSave.BaseBox:y_+height, x_-TempSave.BaseBox:x_+width]
                if cropped_image is None or cropped_image.size == 0: return {"Status": False, "MSG": "Erro: O recorte da imagem está vazio"}, 500

                # Salva a imagem recortada como cut.jpeg na pasta static
                try: os.remove(IMAGE_FOLDER)
                except: pass
                cv.imwrite(IMAGE_FOLDER, cropped_image)

                with open(IMAGE_FOLDER, "rb") as img:
                    url = f'http://{configClient["IP"]}:{configClient["PORT"]}/receiveIMG'
                    response    = post(
                        url,
                        json    = {
                            "reCAPTCHA":    base64.b64encode(img.read()).decode('utf-8'),
                            "offsetLeft":   x_-TempSave.BaseBox,
                            "offsetTop":    y_-TempSave.BaseBox
                        },
                        verify=False
                    )
            except Exception as e:
                print(f"[ERROR-EnviarImage].{int(int(time.time()))}...{e}")
                if TempSave.Driver:
                    TempSave.Driver.refresh()
                time.sleep(10)
        else:
            time.sleep(1)
            
if __name__ == '__main__':
    Process = Thread(target=EnviarImage, daemon=True)
    Process.start()
    app.run(host=configServer["IP"], port=configServer["PORT"], debug=True)