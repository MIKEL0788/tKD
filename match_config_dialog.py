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
from interface_taekwondo import TaekwondoInterface



class MatchConfigDialog(tk.Toplevel):
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app
        self.title("🥊 Configuration du Match - TK-WIN PRO")
        self.configure(bg=self.main_app.THEMES[self.main_app.theme_mode]["config_bg"])
        self.geometry("780x830")
        self.resizable(False, False)
        
        # Style global
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        
        # Configurer les styles selon le thème
        theme = self.main_app.THEMES[self.main_app.theme_mode]
        
        # Configurer les styles
        self.style.configure("TLabel", 
                           background=theme["config_bg"], 
                           foreground=theme["config_label"], 
                           font=("Segoe UI", 10))
        
        self.style.configure("TEntry", 
                           padding=4, 
                           fieldbackground=theme["config_entry"])
        
        self.style.configure("Blue.TEntry", 
                           fieldbackground="#1976D2", 
                           foreground="white")
        
        self.style.configure("Red.TEntry", 
                           fieldbackground="#D32F2F", 
                           foreground="white")
        
        self.style.configure("TButton", 
                           padding=6, 
                           font=("Segoe UI", 10, "bold"))
        
        self.style.configure("Blue.TButton", 
                           background=theme["config_button"], 
                           foreground="white")
        
        self.style.map("Blue.TButton", 
                    background=[("active", "#1565C0")])
        
        self.style.configure("Red.TButton", 
                           background="#D32F2F", 
                           foreground="white")
        
        self.style.map("Red.TButton", 
                    background=[("active", "#B71C1C")])
        
        self.style.configure("TLabelframe", 
                           background=theme["config_bg"], 
                           foreground=theme["config_header"], 
                           font=("Segoe UI", 10, "bold"))
        
        self.style.configure("TLabelframe.Label", 
                           background=theme["config_bg"], 
                           foreground=theme["config_header"])
        
        self.create_widgets()
        self.load_current_config()

    def create_widgets(self):
        theme = self.main_app.THEMES[self.main_app.theme_mode]
        
        # Cadre principal avec barre de défilement
        main_canvas = tk.Canvas(self, bg=theme["config_bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        scrollbar.pack(side="right", fill="y")
        
        # ==== Titre ====
        title_frame = tk.Frame(scrollable_frame, bg=theme["config_bg"])
        title_frame.pack(pady=10, fill="x")
        tk.Label(title_frame, text="⚙ Configuration du Match", 
                font=("Segoe UI", 14, "bold"), 
                fg=theme["config_header"], 
                bg=theme["config_bg"]).pack()
        
        # ==== Section Mode de Match ====
        mode_frame = ttk.LabelFrame(scrollable_frame, text="Mode de Match")
        mode_frame.pack(fill='x', pady=10, padx=5)
        
        # Variable pour stocker le choix du mode
        self.match_mode_var = tk.StringVar(value=self.main_app.match_mode)
        
        # Créer les boutons radio pour choisir le mode
        mode_container = tk.Frame(mode_frame, bg=theme["config_bg"])
        mode_container.pack(fill='x', pady=5)
        
        # Mode tournoi
        tournament_radio = ttk.Radiobutton(
            mode_container, 
            text="Tournoi ", 
            variable=self.match_mode_var, 
            value="tournoi",
            command=self.on_match_mode_change
        )
        tournament_radio.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        # Mode libre
        free_radio = ttk.Radiobutton(
            mode_container, 
            text="Match Libre (manuelles)", 
            variable=self.match_mode_var, 
            value="libre",
            command=self.on_match_mode_change
        )
        free_radio.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Boutons d'action pour le mode tournoi
        self.tournament_actions_frame = ttk.Frame(mode_frame)
        self.tournament_actions_frame.pack(fill='x', pady=5)
        
        ttk.Button(
            self.tournament_actions_frame, 
            text="Créer un nouveau tournoi", 
            command=self.main_app.create_new_tournament
        ).grid(row=0, column=0, padx=5, pady=5)
        
        ttk.Button(
            self.tournament_actions_frame, 
            text="Charger un tournoi existant", 
            command=self.main_app.load_tournament
        ).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(
            self.tournament_actions_frame, 
            text="Importer des joueurs", 
            command=self.main_app.import_players
        ).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Button(
            self.tournament_actions_frame, 
            text="Afficher le Tournoi", 
            command=self.main_app.show_tournament_display
        ).grid(row=0, column=3, padx=5, pady=5)
        
        # Masquer les actions de tournoi si on est en mode libre
        if self.main_app.match_mode == "libre":
            self.tournament_actions_frame.pack_forget()
        
        # ==== Section Informations Générales ====
        general_frame = ttk.LabelFrame(scrollable_frame, text="Informations Générales")
        general_frame.pack(fill='x', pady=10, padx=5)
        
        # Liste des champs
        self.general_entries = {}
        fields = [
            ("Numéro de Match:", "match_number", "Red.TEntry"),
            ("Catégorie:", "category", "Blue.TEntry"),
            ("Temps du Round (s):", "round_time", "Red.TEntry"),
            ("Temps de Repos (s):", "break_time", "Blue.TEntry"),
            ("Nombre de Rounds:", "max_rounds", "Red.TEntry"),
            ("Nombre de Juges:", "judges_count", "Blue.TEntry")
        ]
        
        # Créer les champs
        for i, (label, attr, style_name) in enumerate(fields):
            row_frame = tk.Frame(general_frame, bg=theme["config_bg"])
            row_frame.pack(fill='x', pady=5)
            
            ttk.Label(row_frame, text=label).pack(side='left', padx=5)
            entry = ttk.Entry(row_frame, width=25, style=style_name)
            entry.pack(side='right', padx=5, fill='x', expand=True)
            self.general_entries[attr] = entry
        
        # ==== Section Règles du Match ====
        rules_frame = ttk.LabelFrame(scrollable_frame, text="Règles du Match")
        rules_frame.pack(fill='x', pady=10, padx=5)
        
        # Liste des champs
        self.rules_entries = {}
        rules_fields = [
            ("Victoire par gam-jeom:", "instant_win_gamjeom", "Red.TEntry"),
            ("Points round supplémentaire:", "sudden_death_points", "Blue.TEntry")
        ]
        
        # Créer les champs
        for i, (label, attr, style_name) in enumerate(rules_fields):
            row_frame = tk.Frame(rules_frame, bg=theme["config_bg"])
            row_frame.pack(fill='x', pady=5)
            
            ttk.Label(row_frame, text=label).pack(side='left', padx=5)
            entry = ttk.Entry(row_frame, width=25, style=style_name)
            entry.pack(side='right', padx=5, fill='x', expand=True)
            self.rules_entries[attr] = entry
        
        # ==== Section Combattants ====
        fighters_frame = ttk.Frame(scrollable_frame)
        fighters_frame.pack(fill='x', pady=10, padx=5)
        
        # Combattant Bleu
        fighter_blue = ttk.LabelFrame(fighters_frame, text="Combattant Bleu")
        fighter_blue.pack(side='left', fill='both', expand=True, padx=5)
        
        self.blue_entries = {}
        blue_fields = [
            ("Nom:", "blue_name", "Blue.TEntry"),
            ("Club:", "blue_club", "Blue.TEntry"),
            ("Pays:", "blue_country", "Blue.TEntry")
        ]
        
        for i, (label, attr, style_name) in enumerate(blue_fields):
            row_frame = tk.Frame(fighter_blue, bg=theme["config_bg"])
            row_frame.pack(fill='x', pady=5)
            
            ttk.Label(row_frame, text=label).pack(side='left', padx=5)
            entry = ttk.Entry(row_frame, width=20, style=style_name)
            entry.pack(side='right', padx=5, fill='x', expand=True)
            self.blue_entries[attr] = entry
        
        # Combattant Rouge
        fighter_red = ttk.LabelFrame(fighters_frame, text="Combattant Rouge")
        fighter_red.pack(side='right', fill='both', expand=True, padx=5)
        
        self.red_entries = {}
        red_fields = [
            ("Nom:", "red_name", "Red.TEntry"),
            ("Club:", "red_club", "Red.TEntry"),
            ("Pays:", "red_country", "Red.TEntry")
        ]
        
        for i, (label, attr, style_name) in enumerate(red_fields):
            row_frame = tk.Frame(fighter_red, bg=theme["config_bg"])
            row_frame.pack(fill='x', pady=5)
            
            ttk.Label(row_frame, text=label).pack(side='left', padx=5)
            entry = ttk.Entry(row_frame, width=20, style=style_name)
            entry.pack(side='right', padx=5, fill='x', expand=True)
            self.red_entries[attr] = entry
        
        # Boutons
        btn_frame = tk.Frame(scrollable_frame, bg=theme["config_bg"])
        btn_frame.pack(pady=20, fill='x')
        
        validate_btn = ttk.Button(
            btn_frame, 
            text="Valider", 
            style="Blue.TButton", 
            command=self.save_config
        )
        validate_btn.pack(side="left", padx=10)
        
        cancel_btn = ttk.Button(
            btn_frame, 
            text="Annuler", 
            style="Red.TButton", 
            command=self.destroy
        )
        cancel_btn.pack(side="left", padx=10)
        
        # Désactiver les champs en mode tournoi
        self.on_match_mode_change()
        
        # Configurer les événements de scroll
        self.bind("<MouseWheel>", lambda e: main_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        self.bind("<Button-4>", lambda e: main_canvas.yview_scroll(-1, "units"))
        self.bind("<Button-5>", lambda e: main_canvas.yview_scroll(1, "units"))
        
        # Focus sur le premier champ
        self.after(100, lambda: next(iter(self.general_entries.values())).focus_set())

    def load_current_config(self):
        """Charge la configuration actuelle dans les champs"""
        # Informations générales
        for attr, entry in self.general_entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, str(getattr(self.main_app, attr)))
        
        # Règles
        for attr, entry in self.rules_entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, str(getattr(self.main_app, attr)))
        
        # Combattants
        for attr, entry in self.blue_entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, str(getattr(self.main_app, attr)))
        
        for attr, entry in self.red_entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, str(getattr(self.main_app, attr)))
    
    def on_match_mode_change(self):
        """Gérer le changement de mode de match"""
        mode = self.match_mode_var.get()
        
        # Afficher ou masquer les actions de tournoi
        if mode == "tournoi":
            self.tournament_actions_frame.pack(fill='x', pady=5)
            # Désactiver les champs des combattants
            for entry in self.blue_entries.values():
                entry.configure(state="disabled")
            for entry in self.red_entries.values():
                entry.configure(state="disabled")
        else:
            self.tournament_actions_frame.pack_forget()
            # Activer les champs des combattants
            for entry in self.blue_entries.values():
                entry.configure(state="normal")
            for entry in self.red_entries.values():
                entry.configure(state="normal")
    
    def save_config(self):
        """Sauvegarder la configuration du match"""
        try:
            # Récupérer et valider les valeurs des informations générales
            for attr, entry in self.general_entries.items():
                value = entry.get().strip()
                # Convertir les valeurs numériques
                if attr in ["round_time", "break_time", "max_rounds", "judges_count"]:
                    value = int(value)
                setattr(self.main_app, attr, value)
            
            # Récupérer et valider les valeurs des règles
            for attr, entry in self.rules_entries.items():
                value = entry.get().strip()
                setattr(self.main_app, attr, int(value))
            
            # En mode libre, récupérer les informations des combattants
            if self.match_mode_var.get() == "libre":
                for attr, entry in self.blue_entries.items():
                    setattr(self.main_app, attr, entry.get().strip())
                
                for attr, entry in self.red_entries.items():
                    setattr(self.main_app, attr, entry.get().strip())
                
                # Validation des informations des combattants
                if not self.main_app.blue_name or not self.main_app.red_name:
                    raise ValueError("Les noms des combattants sont obligatoires")
            
            # Validation des valeurs
            if self.main_app.round_time <= 0 or self.main_app.break_time <= 0 or self.main_app.max_rounds <= 0 or self.main_app.judges_count <= 0:
                raise ValueError("Toutes les valeurs doivent être positives")
            
            if self.main_app.judges_count > 10:
                raise ValueError("Maximum 10 juges autorisés")
            
            # Mettre à jour les drapeaux
            self.main_app.blue_flag = self.main_app.flag_dict.get(self.main_app.blue_country, "🏳️")
            self.main_app.red_flag = self.main_app.flag_dict.get(self.main_app.red_country, "🏳️")
            
            # Réinitialiser les données du match
            self.main_app.reset_match_data()
            self.main_app.match_configured = True
            
            self.destroy()
            self.main_app.setup_ui()
            self.main_app.gamepad_manager.setup_judges(self.main_app.judges_count)
            
        except ValueError as e:
            messagebox.showerror("Erreur de configuration", str(e))
        except Exception as e:
            messagebox.showerror("Erreur", f"Configuration échouée: {str(e)}")
