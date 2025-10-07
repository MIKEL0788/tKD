import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
import pygame
import sys
import os
from PIL import Image, ImageTk
from typing import Dict, List, Optional, Tuple


class GamepadManager:
    def __init__(self, main_app):
        self.app = main_app
        self.judges = {}
        self.active = False
        self.gamepads = []
        self.monitoring_threads = []
        self.stop_monitoring = False
        self.last_detected_count = 0
        try:
            pygame.init()
            pygame.joystick.init()
            self.detect_gamepads()
        except Exception as e:
            print(f"Erreur d'initialisation pygame: {e}")
            self.gamepads = []

    def detect_gamepads(self, show_notification=True):
        previous_count = len(self.gamepads)
        self.gamepads = []
        try:
            count = pygame.joystick.get_count()
            for i in range(count):
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                self.gamepads.append(joystick)
            
            if show_notification and count != previous_count:
                if count > 0:
                    msg = f"{count} manette(s) détectée(s)"
                    print(msg)
                    if hasattr(self.app, 'root'):
                        self.app.root.after(0, lambda: self.show_gamepad_notification(msg, 'success'))
                else:
                    msg = "Aucun juge connecté"
                    print(msg)
                    if hasattr(self.app, 'root'):
                        self.app.root.after(0, lambda: self.show_gamepad_notification(msg, 'warning'))
        except Exception as e:
            print(f"Erreur détection manettes: {e}")
        return len(self.gamepads)

    def show_gamepad_notification(self, message, level='info'):
        try:
            if hasattr(self.app, 'show_notification'):
                self.app.show_notification(message, level)
            else:
                print(f"Notification: {message}")
        except Exception as e:
            print(f"Erreur notification: {e}")

    def setup_judges(self, count):
        self.stop_monitoring = True
        time.sleep(0.1)
        self.judges = {}
        self.monitoring_threads = []
        self.stop_monitoring = False
        
        # Si une seule manette est connectée, on l'assigne à tous les juges
        if len(self.gamepads) == 1:
            for i in range(count):
                self.judges[i] = {'active': True, 'gamepad_id': 0}
                thread = threading.Thread(target=self.monitor_judge_input, args=(i,), daemon=True)
                self.monitoring_threads.append(thread)
                thread.start()
        else:
            for i in range(count):
                self.judges[i] = {
                    'active': True,
                    'gamepad_id': i % len(self.gamepads) if self.gamepads else None
                }
                if self.gamepads:
                    thread = threading.Thread(
                        target=self.monitor_judge_input,
                        args=(i,),
                        daemon=True
                    )
                    self.monitoring_threads.append(thread)
                    thread.start()

    def monitor_judge_input(self, judge_id):
        if not self.gamepads or judge_id >= len(self.gamepads):
            return
        gamepad_index = judge_id % len(self.gamepads)
        joystick = self.gamepads[gamepad_index]
        last_btn_state = [False] * joystick.get_numbuttons()
        last_hat_state = (0, 0)
        while not self.stop_monitoring:
            try:
                pygame.event.pump()
                if joystick.get_numhats() > 0:
                    hat = joystick.get_hat(0)
                    if hat != last_hat_state:
                        self.process_hat_input(judge_id, hat)
                    last_hat_state = hat
                for btn in range(joystick.get_numbuttons()):
                    state = joystick.get_button(btn)
                    if state and not last_btn_state[btn]:
                        self.process_button_input(judge_id, btn)
                    last_btn_state[btn] = state
            except Exception as e:
                print(f"Erreur monitoring manette {judge_id}: {e}")
                break
            time.sleep(0.03)

    def process_hat_input(self, judge_id, hat):
        if hat[1] == 1:
            self.send_judge_input(judge_id, 'blue', 1, "D-Pad Haut")
        elif hat[0] == 1:
            self.send_judge_input(judge_id, 'blue', 2, "D-Pad Droite")
        elif hat[1] == -1:
            self.send_judge_input(judge_id, 'blue', 3, "D-Pad Bas")
        elif hat[0] == -1:
            self.send_judge_input(judge_id, 'blue', 4, "D-Pad Gauche")

    def process_button_input(self, judge_id, btn):
        button_mapping = {
            0: ('red', 1, 'Triangle'),
            1: ('red', 2, 'Rond'),
            2: ('red', 3, 'Croix'),
            3: ('red', 4, 'Carré'),
            5: ('red', 5, 'R1'),
            7: ('red', 'GAM-JEOM', 'R2'),
            4: ('blue', 5, 'L1'),
            6: ('blue', 'GAM-JEOM', 'L2'),                                      
        }
        if btn in button_mapping:
            player, value, button_name = button_mapping[btn]
            self.send_judge_input(judge_id, player, value, button_name)

    def send_judge_input(self, judge_id, player, value, button_name):
        try:
            if hasattr(self.app, 'process_judge_input'):
                self.app.root.after(0, lambda: self.app.process_judge_input(judge_id, player, value))
        except Exception as e:
            print(f"Erreur envoi entrée juge: {e}")

    def check_gamepads(self):
        """Vérifie périodiquement les nouvelles manettes"""
        current_count = len(self.gamepads)
        new_count = self.detect_gamepads(show_notification=False)
        
        if new_count != current_count:
            # Afficher notification seulement si changement
            if new_count > 0:
                msg = f"{new_count} manette(s) détectée(s)"
                self.show_gamepad_notification(msg, 'success')
            else:
                msg = "Aucun juge détecté"
                self.show_gamepad_notification(msg, 'warning')
            
            # Reconfigurer les juges si nécessaire
            if hasattr(self.app, 'judges_count'):
                self.setup_judges(self.app.judges_count)
        
        # Vérifier à nouveau après 3 secondes
        if hasattr(self.app, 'root'):
            self.app.root.after(3000, self.check_gamepads)