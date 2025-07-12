import pyautogui
import pytesseract
import pyperclip
import time
import re
from PIL import Image
import winsound
import os
import psutil

# Prioridade máxima no Windows para desempenho
p = psutil.Process(os.getpid())
p.nice(psutil.HIGH_PRIORITY_CLASS)

# Caminho para o Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

region = (286, 870, 1045, 140)
ultima_leitura = ""

# Atualiza a região da tela a ser capturada
def set_region(nova_regiao):
    global region
    region = nova_regiao
    print(f"📐 Região definida: {region}")

# Pré-processamento simples: binarização para melhorar OCR
def melhorar_nitidez(imagem: Image.Image) -> Image.Image:
    imagem = imagem.convert('L')  # Escala de cinza
    imagem = imagem.point(lambda p: 0 if p < 145 else 255, mode='1')  # Binarização
    return imagem

# Loop principal
def run_ocr_ui(regex_usuario, update_callback, stop_check, get_audio_status):
    global ultima_leitura

    try:
        padrao_codigo = re.compile(regex_usuario)
    except re.error:
        print("❌ Regex inválida:", regex_usuario)
        return

    print(f"🚀 OCR iniciado com regex: {regex_usuario}")
    print(f"📷 Região monitorada: {region}")

    while not stop_check():
        img = pyautogui.screenshot(region=region)
        imagem_processada = melhorar_nitidez(img)

        custom_config = r'--oem 1 --psm 6'
        texto = pytesseract.image_to_string(imagem_processada, lang='eng', config=custom_config).strip()

        match = padrao_codigo.search(texto)
        if match:
            codigo = match.group()
            pyperclip.copy(codigo)

            if get_audio_status():
                winsound.Beep(1000, 300)

            print(f"⚡ Código detectado: {codigo} (copiado!)")
            with open("codigos_detectados.txt", "a", encoding="utf-8") as f:
                f.write(codigo + "\n")

            update_callback(codigo)

        time.sleep(0.01)
