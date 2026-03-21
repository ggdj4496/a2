import speech_recognition as sr
import pyttsx3
import threading
import time
import os

class VoiceAssistant:
    def __init__(self, wake_word="guillecoder"):
        self.wake_word = wake_word.lower()
        self.recognizer = sr.Recognizer()
        self.is_listening = False
        self.is_speaking = False
        self.running = False
        
        try:
            self.engine = pyttsx3.init()
            # Configurar la voz del tecnico experto (masculina, clara)
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if "spanish" in voice.name.lower() or "ES" in voice.id:
                    self.engine.setProperty('voice', voice.id)
                    break
            self.engine.setProperty('rate', 170) 
            self.engine.setProperty('volume', 0.9)
        except Exception as e:
            print(f"[GUILLECODER-VOZ-ERROR] Error al inicializar TTS: {e}")
            self.engine = None

    def speak(self, text):
        if not self.engine:
            print(f"[GUILLECODER-VOZ-OFFLINE] {text}")
            return
            
        print(f"[GUILLECODER-VOZ] Respondiendo: {text}")
        self.is_speaking = True
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"[GUILLECODER-VOZ-ERROR] Fallo al hablar: {e}")
        finally:
            self.is_speaking = False

    def listen_for_wake_word(self, callback):
        self.running = True
        print(f"[GUILLECODER-VOZ] Modo Live Activado. Escuchando: '{self.wake_word}'...")
        
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                while self.running:
                    if self.is_speaking:
                        time.sleep(0.5)
                        continue
                    
                    try:
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
                        text = self.recognizer.recognize_google(audio, language="es-ES").lower()
                        
                        if self.wake_word in text:
                            print(f"[GUILLECODER-VOZ] Palabra clave detectada.")
                            self.speak("Dime, ¿que código programamos hoy?")
                            self._capture_command(source, callback)
                            
                    except sr.WaitTimeoutError:
                        pass
                    except sr.UnknownValueError:
                        pass
                    except Exception as e:
                        print(f"[GUILLECODER-VOZ-ERROR] Error en reconocimiento: {e}")
                        time.sleep(2)
        except Exception as e:
            print(f"[GUILLECODER-VOZ-ERROR] No se pudo acceder al microfono: {e}")

    def _capture_command(self, source, callback):
        print("[GUILLECODER-VOZ] Escuchando comando...")
        try:
            audio = self.recognizer.listen(source, timeout=7, phrase_time_limit=10)
            command = self.recognizer.recognize_google(audio, language="es-ES")
            print(f"[GUILLECODER-VOZ] Comando recibido: {command}")
            if callback:
                callback(command)
        except Exception as e:
            print(f"[GUILLECODER-VOZ-ERROR] No he podido entender el comando: {e}")
            self.speak("Repite, por favor, no te he captado bien.")

    def start_live_mode(self, callback):
        self.voice_thread = threading.Thread(target=self.listen_for_wake_word, args=(callback,), daemon=True)
        self.voice_thread.start()

    def stop(self):
        self.running = False

if __name__ == "__main__":
    # Prueba basica de voz
    def mock_callback(cmd):
        print(f"EJECUTANDO: {cmd}")
        
    va = VoiceAssistant()
    va.speak("Virgilio iniciado y listo para el modo manos libres.")
    va.start_live_mode(mock_callback)
    while True: time.sleep(1)
