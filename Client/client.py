from flask import Flask, render_template, request, jsonify
from Config.Engine import configClient, configServer
from requests import post
import base64
import time
import os

app = Flask(__name__)

class TempSave:
    offsetLeft  = None
    offsetTop   = None

# Criar pasta para armazenar imagens, se não existir
IMAGE_FOLDER = "static"
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/reCAPTCHA")
def imagem():
    return render_template("reCAPTCHA.html")

@app.route("/receiveIMG", methods=["POST"])
def receiveIMG():
    try:
        print("[INFO-receiveIMG].{time.time()}...IMAGEM RECEBIDA")
        result              = request.get_json()
        photo               = result['reCAPTCHA']
        TempSave.offsetLeft = result['offsetLeft']
        TempSave.offsetTop  = result['offsetTop']
        photo_data = base64.b64decode(photo)
        with open("static/reCAPTCHA.png", "wb") as file:
            file.write(photo_data)
            return {"Status": True}, 200
    except Exception as e:
        print(f"[ERROR-receiveIMG]...{e}")
        return {"Status": False}, 400
    
@app.route("/receiveCoordinateClient", methods=["POST"])
def recCoodinate():
    try:
        if TempSave.offsetLeft and TempSave.offsetTop:
            print(f"[INFO-recCoodinate].{time.time()}...ENVIANDO COORDENADAS")
            receive     = request.get_json()
            json        = {
                'Width':  receive['Width'] + TempSave.offsetLeft,
                'Height': receive['Height'] + TempSave.offsetTop
            }
            response    = post(
                f'http://{configServer["IP"]}:{configServer["PORT"]}/receiveCoordinateServer',
                json    = json,
                verify  = False
            )
            print(f"[INFO-recCoodinate].{time.time()}...STATUS {response.status_code}")
            return {"Status": True}, response.status_code
        else:
            print(f"[INFO-recCoodinate].{time.time()}...STATUS: offsetLeft ans offsetTop Not Defined")
            return {"Status": False}, 400
    except Exception as e:
        print(f"[ERROR-recCoodinate].{time.time()}...{e}")
        return {"Status": False}, 400

if __name__ == '__main__':
    app.run(host=configClient["IP"], port=configClient["PORT"], debug=True)