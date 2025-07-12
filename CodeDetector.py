import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import threading
import pyautogui
import cv2
import numpy as np
import webbrowser
from PIL import Image, ImageTk
import sys
import os

region = (286, 870, 1045, 140)
audio_ativo = True

class OCRApp:
    def __init__(self, root):
        self.root = root
        self.tema_atual = "cosmo"
        self.style = ttk.Style(self.tema_atual)

        self.root.title("Detector de Código")
        

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS  
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        icone_path = os.path.join(base_path, "icone.ico")
        self.root.iconbitmap(icone_path)

        self.root.geometry("850x700")

        # Frame lateral (direito)
        sidebar = ttk.Frame(self.root, padding=10)
        sidebar.pack(side="right", fill="y")

        self.toggle_theme_button = ttk.Button(
            sidebar, text="🌙 Modo Escuro", command=self.trocar_tema, bootstyle=SECONDARY
        )
        self.toggle_theme_button.pack(pady=10, fill="x")

        self.audio_button = ttk.Button(
            sidebar, text="🔊", command=self.toggle_audio, bootstyle=SUCCESS
        )
        self.audio_button.pack(pady=5, fill="x")

        # Frame principal (esquerdo)
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(side="left", fill="both", expand=True)

        ttk.Label(main_frame, text="Detector de Código Resgatável", font=("Arial", 18, "bold")).pack(pady=15)
        ttk.Label(main_frame, text="Formato do código:").pack()

        self.regex_options = {
            "XXX-XXXXX-XXXXX-XXXXX (3-5-5-5)": r"\b[A-Z0-9]{3}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}\b",
            "XXXX-XXXX (4-4)": r"\b[A-Z0-9]{4}-[A-Z0-9]{4}\b",
            "XXXXXXXXX (9)": r"\b[A-Z0-9]{9}\b",
            "XXXX-XXXX-XXXX (4-4-4)": r"\b\d{4}-\d{4}-\d{4}\b",
            "XX-XXXXX-XXXXX-XXXXX (2-5-5-5)": r"\b[A-Za-z0-9]{2}-[A-Za-z0-9]{5}-[A-Za-z0-9]{5}-[A-Za-z0-9]{5}\b",
            "XXXXX-XXXXX-XXXXX (5-5-5)" : r"\b[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}\b",
            "Personalizado regex - avançado": ""
        }

        self.selected_format = ttk.StringVar(value=list(self.regex_options.keys())[0])
        self.dropdown = ttk.OptionMenu(main_frame, self.selected_format, self.selected_format.get(), *self.regex_options.keys(), command=self.on_format_change)
        self.dropdown.pack()

        self.regex_entry = ttk.Entry(main_frame, width=60)
        self.regex_entry.insert(0, self.regex_options[self.selected_format.get()])
        self.regex_entry.pack(pady=5)

        ttk.Button(main_frame, text="🖱️ Selecionar área da tela", command=self.selecionar_area, bootstyle=PRIMARY).pack(pady=5)

        self.status_label = ttk.Label(main_frame, text="Aguardando início...", foreground="blue")
        self.status_label.pack(pady=10)

        self.start_button = ttk.Button(main_frame, text="Iniciar Captura", command=self.start_ocr, bootstyle=SUCCESS)
        self.start_button.pack(pady=5)

        self.stop_button = ttk.Button(main_frame, text="Parar", command=self.stop_ocr, state="disabled", bootstyle=DANGER)
        self.stop_button.pack(pady=5)

        self.last_code_label = ttk.Label(main_frame, text="Último código: ---")
        self.last_code_label.pack(pady=15)

        self.instrucoes_label = ttk.Label(
            main_frame,
            text=(
                "Esse software é ideal para extrair e converter rapidamente códigos resgatáveis (promocionais e cartão presente) em formato de vídeo para texto.\n"
                "Certifique-se que a resolução da imagem está adequada para a detecção. Nem sempre o código será extraído 100% correto.\n\n"
                "ℹ️ Como usar:\n1. Escolha ou edite o formato do código desejado.\n"
                "2. Selecione a área da tela com o botão acima - pressione ENTER ou ESC para confirmar.\n"
                "3. Clique em 'Iniciar Captura'.\n"
                "4. O código será detectado, copiado e salvo automaticamente.\n"
                "5. Clique em 'Parar' para interromper."
            ),
            justify="left",
            wraplength=700
        )
        self.instrucoes_label.pack(pady=(10, 0))

        self.apoio_label = ttk.Label(
            main_frame,
            text="☕ Gostou do projeto? Me apoie!",
            font=("Arial", 9),
            justify="center"
        )
        self.apoio_label.pack(side="bottom", pady=(0, 2))

        try:
            bmc_path = os.path.join(base_path, "bmc.png")
            imagem_original = Image.open(bmc_path)
            imagem_redimensionada = imagem_original.resize((160, 45))
            self.bmc_image = ImageTk.PhotoImage(imagem_redimensionada)

            self.bmc_button = ttk.Button(
                main_frame,
                image=self.bmc_image,
                command=lambda: webbrowser.open("https://buymeacoffee.com/leomarques"),
                bootstyle=LINK
            )
            self.bmc_button.pack(side="bottom", pady=10)
        except Exception as e:
            print("❌ Erro ao carregar imagem do Buy Me a Coffee:", e)

        self.running = False
        self.thread = None

    def on_format_change(self, selection):
        self.regex_entry.delete(0, 'end')
        if self.regex_options[selection] != "":
            self.regex_entry.insert(0, self.regex_options[selection])

    def trocar_tema(self):
        if self.tema_atual == "cosmo":
            self.tema_atual = "darkly"
            self.toggle_theme_button.config(text="☀️ Modo Claro")
        else:
            self.tema_atual = "cosmo"
            self.toggle_theme_button.config(text="🌙 Modo Escuro")
        self.style.theme_use(self.tema_atual)

    def toggle_audio(self):
        global audio_ativo
        audio_ativo = not audio_ativo
        if audio_ativo:
            self.audio_button.config(text="🔊", bootstyle=SUCCESS)
        else:
            self.audio_button.config(text="🔇", bootstyle=DANGER)

    def selecionar_area(self):
        global region
        self.status_label.config(text="Abra a área do código. Aguarde...", foreground="black")
        self.root.update()
        try:
            screenshot = pyautogui.screenshot()
            screen_np = np.array(screenshot)
            screen_cv = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
            win_name = "🗱️ Selecione a área e pressione ENTER ou ESC"
            cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
            cv2.setWindowProperty(win_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.setWindowProperty(win_name, cv2.WND_PROP_TOPMOST, 1)
            roi = cv2.selectROI(win_name, screen_cv, showCrosshair=True)
            cv2.destroyAllWindows()
            x, y, w, h = roi
            if w > 0 and h > 0:
                region = (int(x), int(y), int(w), int(h))
                self.status_label.config(text=f"Área selecionada: {region}", foreground="blue")
            else:
                self.status_label.config(text="Nenhuma área selecionada.", foreground="red")
        except Exception as e:
            self.status_label.config(text="Erro ao selecionar área.", foreground="red")
            print("❌ Erro ao selecionar área:", e)

    def start_ocr(self):
        regex = self.regex_entry.get().strip()
        if not regex:
            messagebox.showerror("Erro", "Você precisa inserir uma regex válida.")
            return
        self.running = True
        self.status_label.config(text="Rodando...", foreground="green")
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.thread = threading.Thread(
            target=self.run_detector, args=(regex,)
        )
        self.thread.start()

    def stop_ocr(self):
        self.running = False
        self.status_label.config(text="Parado", foreground="red")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

    def run_detector(self, regex_usuario):
        import detector
        detector.set_region(region)
        detector.run_ocr_ui(
            regex_usuario,
            update_callback=self.update_code,
            stop_check=lambda: not self.running,
            get_audio_status=lambda: audio_ativo
        )

    def update_code(self, codigo):
        self.last_code_label.config(text=f"Último código: {codigo}")
        self.status_label.config(text="Código detectado!", foreground="orange")

if __name__ == "__main__":
    root = ttk.Window(themename="cosmo")
    app = OCRApp(root)
    root.mainloop()