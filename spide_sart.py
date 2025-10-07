import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
import pygame
import sys
import os
from PIL import Image, ImageTk
from typing import Dict, List, Optional, Tuple

from gamepad_manager import GamepadManager


class demarrage_rapide_interface :
    THEMES = {
        "dark": {
            "bg": "#2C2C3A",
            "fg": "white",
            "header_bg": "#1A1A2A",
            "blue_bg": "#1565C0",
            "blue_header": "#0D47A1",
            "red_bg": "#C62828",
            "red_header": "#B71C1C",
            "winner_bg": "#FFD700",
            "winner_fg": "#1A1A2A",
            "round_bg": "#1A1A2A",
            "button_bg": "#4CAF50",
            "button_fg": "white",
            "time_fg": "#FFD700",
            "judge_bg": "#3A3A4A",
            "judge_fg": "#FFFFFF",
            "disabled": "#aaaaaa",
            "config_bg": "#1E1E2E",
            "config_header": "#42A5F5",
            "config_label": "#B0BEC5",
            "config_entry": "#37474F",
            "config_button": "#1976D2"
        },
        "light": {
            "bg": "#e8e8e8",
            "fg": "black",
            "header_bg": "#333333",
            "blue_bg": "#2196F3",
            "blue_header": "#0D47A1",
            "red_bg": "#F44336",
            "red_header": "#B71C1C",
            "winner_bg": "gold",
            "winner_fg": "black",
            "round_bg": "#f0f0f0",
            "button_bg": "#4CAF50",
            "button_fg": "white",
            "time_fg": "black",
            "judge_bg": "#D0D0D0",
            "judge_fg": "#000000",
            "disabled": "#cccccc",
            "config_bg": "#F5F5F5",
            "config_header": "#1E88E5",
            "config_label": "#455A64",
            "config_entry": "#FFFFFF",
            "config_button": "#2196F3"
        }
    }



    def create_main_frames(self):
            """Créer la structure principale responsive"""
            # Barre d'outils supérieure
            theme = self.THEMES[self.theme_mode]
            self.toolbar = tk.Frame(self.root, bg=theme["header_bg"], height=40)
            self.toolbar.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
            self.toolbar.grid_propagate(False)

    def apply_theme(self):
        """Appliquer le thème actuel à l'interface"""
        theme = self.THEMES[self.theme_mode]
        self.root.configure(bg=theme["bg"])
        if hasattr(self, "toolbar"):
            self.toolbar.configure(bg=theme["header_bg"])
        if hasattr(self, "main_container"):
            self.main_container.configure(bg=theme["bg"])
        if hasattr(self, "winner_frame"):
            self.winner_frame.configure(bg=theme["winner_bg"])




    def en_tete(self):
        """Crée l'en-tête de l'interface un titre"""
        theme = self.THEMES[self.theme_mode]
        
        
        # Titre
        title_label = tk.Label(self.toolbar, text="BIENVENU SUR TAEKWONDO EVEIL", font=('Arial', 35, 'bold'),
                               bg=theme["header_bg"], fg=theme["fg"])
        title_label.pack(side='left', padx=20, pady=10)

    def create_main_container(self):
        """Créer le conteneur principal pour les éléments de l'interface"""
        theme = self.THEMES[self.theme_mode]
        self.main_container = tk.Frame(self.root, bg=theme["bg"])
        self.main_container.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
    

    # cette fonction permet de creer les liens vers les element pour vite demarrer une session
    #il seront creer sur cree comme des liens un peut comme dans du html (juste du texte en bleu qui ouvre une fenetre)
    def link_raccourcis(self):
        """cree liens vers les element de l'interface( nouveau tournoir, nouveau match, charger un tournoi)"""
        theme = self.THEMES[self.theme_mode]
        self.raccourcis_frame = tk.Frame(self.main_container, bg=theme["bg"])
        self.raccourcis_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        self.raccourcis_frame.grid_columnconfigure(0, weight=1)

        # Titre des raccourcis
        title_label = tk.Label(self.raccourcis_frame, text="Raccourcis", font=('Arial', 20, 'bold'),
                               bg=theme["bg"], fg=theme["fg"])
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Bouton pour créer un nouveau tournoi
        new_tournament_button = tk.Button(self.raccourcis_frame, text="Nouveau Tournoi", font=('Arial', 14),
                                          bg=theme["button_bg"], fg=theme["button_fg"],
                                          command=self.create_new_tournament)
        new_tournament_button.grid(row=1, column=0, padx=10, pady=5, sticky='ew')

        # Bouton pour créer un nouveau match
        new_match_button = tk.Button(self.raccourcis_frame, text="Nouveau Match", font=('Arial', 14),
                                     bg=theme["button_bg"], fg=theme["button_fg"],
                                     command=self.create_new_match)
        new_match_button.grid(row=1, column=1, padx=10, pady=5, sticky='ew')

        # Bouton pour charger un tournoi
        load_tournament_button = tk.Button(self.raccourcis_frame, text="Charger Tournoi", font=('Arial', 14),
                                           bg=theme["button_bg"], fg=theme["button_fg"],
                                           command=self.load_tournament)
        load_tournament_button.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky='ew')
