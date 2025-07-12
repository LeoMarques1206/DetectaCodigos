# 🖥️ DetectaCódigos

![Made with Python](https://img.shields.io/badge/Made%20with-Python-3776AB?logo=python&logoColor=white)
![UI com ttkbootstrap](https://img.shields.io/badge/UI-ttkbootstrap-blueviolet)
![Platform](https://img.shields.io/badge/Platform-Windows-blue)

Um aplicativo em Python para detectar e copiar automaticamente **códigos promocionais** e **gift cards** diretamente da tela, ideal para vídeos com brindes e transmissões ao vivo.

---

## 📸 Funcionalidades

- 🖱️ Seleção de área da tela com interface gráfica
- 🔍 Detecção de códigos via **OCR + Regex personalizada**
- 🎨 Interface com **tema claro/escuro**
- 📋 Códigos detectados são copiados automaticamente
- ☕ Botão de apoio integrado com **Buy Me a Coffee**

---

## 📦 Requisitos

- Python **3.10+**
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)

> ⚠️ Certifique-se de instalar o Tesseract e, se necessário, configurar o caminho no código:

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
