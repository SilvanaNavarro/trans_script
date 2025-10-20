import pyautogui
import time
import os
import keyboard
import threading
from pynput import mouse
from pynput.mouse import Listener as MouseListener

class CodeTyper:
    def __init__(self, file_path):
        self.file_path = file_path
        self.progress_file = "typing_progress.txt"
        self.is_running = False
        self.stop_requested = False
        self.mouse_listener = None
        
    def load_code(self):
        """Carga el código desde el archivo de texto"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {self.file_path}")
            return None
    
    def save_progress(self, position):
        """Guarda la posición actual en el archivo de progreso"""
        with open(self.progress_file, 'w') as file:
            file.write(str(position))
    
    def load_progress(self):
        """Carga la posición guardada desde el archivo de progreso"""
        try:
            with open(self.progress_file, 'r') as file:
                return int(file.read().strip())
        except FileNotFoundError:
            return 0
        except ValueError:
            return 0
    
    def clear_progress(self):
        """Elimina el archivo de progreso"""
        try:
            os.remove(self.progress_file)
        except FileNotFoundError:
            pass

    def on_click(self, x, y, button, pressed):
        """Callback que se ejecuta cuando se detecta un clic del mouse"""
        if pressed and self.is_running:
            self.stop_requested = True
            button_name = "Izquierdo" if button == mouse.Button.left else "Derecho"
    
    def start_mouse_monitor(self):
        """Inicia el monitor de clics del mouse"""
        self.mouse_listener = MouseListener(on_click=self.on_click)
        self.mouse_listener.start()
    
    def stop_mouse_monitor(self):
        """Detiene el monitor de clics del mouse"""
        if self.mouse_listener:
            self.mouse_listener.stop()
    
    def monitor_keyboard(self):
        """Monitorea el teclado para detener la ejecución"""
        keyboard.wait()  # Espera hasta que se presione cualquier tecla
        if self.is_running:
            self.stop_requested = True
    
    def type_code(self, delay=0.5, line_delay=0.8):
        """Escribe el código carácter por carácter"""
        code = self.load_code()
        if code is None:
            return
        
        # Cargar progreso anterior
        start_position = self.load_progress()
        
        if start_position > 0:
            code = code[start_position:]
        
        self.is_running = True
        self.stop_requested = False
        
        # Iniciar hilos para monitorear teclado y mouse
        keyboard_thread = threading.Thread(target=self.monitor_keyboard)
        keyboard_thread.daemon = True
        keyboard_thread.start()

        time.sleep(5)
        
        # Iniciar monitor de mouse
        self.start_mouse_monitor()
        
        total_chars = len(code)
        current_position = start_position
        
        try:
            for i, char in enumerate(code):
                if self.stop_requested:
                    break
                
                # Escribir el carácter actual
                pyautogui.write(char)
                
                current_position = start_position + i + 1
                
                # Guardar progreso periódicamente
                if i % 10 == 0:  # Guardar cada 10 caracteres
                    self.save_progress(current_position)
                
                # Delay entre caracteres
                time.sleep(delay)
                
                # Delay adicional después de saltos de línea
                if char == '\n':
                    time.sleep(line_delay)
                
                # Mostrar progreso
                if i % 50 == 0:
                    total_length = start_position + total_chars
                    if total_length > 0:
                        progress = (current_position / total_length) * 100
            
            # Si completó sin interrupciones, limpiar progreso
            if not self.stop_requested:
                self.clear_progress()
            else:
                # Guardar la posición actual antes de salir
                self.save_progress(current_position)
                
        except KeyboardInterrupt:
            # Guardar progreso si se interrumpe con Ctrl+C
            self.save_progress(current_position)
        
        finally:
            # Asegurarse de detener el monitor del mouse
            self.stop_mouse_monitor()
            self.is_running = False

def main():
    # Configuración
    file_path = "codigo.txt"  # Cambia esto por la ruta de tu archivo
    
    # Crear instancia del tecleador
    typer = CodeTyper(file_path)
       
    try:
        # Configurar delays (puedes ajustar estos valores)
        char_delay = 0.5  # Delay entre caracteres en segundos
        line_delay = 0.5   # Delay adicional después de saltos de línea
        
        typer.type_code(char_delay, line_delay)
        
    except Exception as e:
        print(f"Error durante la ejecución: {e}")

if __name__ == "__main__":
    main()