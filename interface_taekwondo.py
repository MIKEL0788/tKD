import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
import pygame
import sys
import os
from PIL import Image, ImageTk
from typing import Dict, List, Optional, Tuple
from tkinter import Toplevel
from tour_de_passage import afficher_pyramide

from gamepad_manager import GamepadManager

class TaekwondoInterface:
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

    def __init__(self, root):
        self.root = root
        self.root.title("TK-WIN PRO - Système de gestion de compétition Taekwondo")
        self.root.geometry("1400x900")
        
        # Thème par défaut
        self.theme_mode = "dark"
        self.apply_theme()
        
        # Initialiser le gestionnaire de tournoi
        from tournament_manager import TournamentManager
        self.tournament_manager = TournamentManager(self)
        
        # Initialiser le gestionnaire d'affichage du tournoi
        from tournament_display import TournamentDisplay
        self.tournament_display = TournamentDisplay(self)
        
        # Mode de match (tournoi ou libre)
        self.match_mode = "libre"  # Par défaut, mode libre
        
        # Variables d'état du match
        self.is_running = False
        self.is_paused = False
        self.current_time = 180
        self.round_time = 120
        self.break_time = 30
        self.remaining_break_time = 0
        self.round_number = 1
        self.max_rounds = 2
        self.blue_score = 0
        self.red_score = 0
        self.match_configured = False
        self.timer_thread = None
        self.break_thread = None
        self.is_break_time = False
        self.round_winners = []
        self.final_winner = None

        # Variables de configuration
        self.blue_name = "nom joyeux rouge"
        self.red_name = "nom joyeux bleu"
        self.blue_club = "CLUB BLEU"
        self.red_club = "CLUB ROUGE"
        self.blue_country = "CI"
        self.red_country = "CI"
        self.blue_flag = "🇺🇸"
        self.red_flag = "🇨🇳"
        self.judges_count = 2
        self.match_number = "1"
        self.category = "MEN 12-15"

        self.blue_gam_jeom = 0
        self.red_gam_jeom = 0
        
        # Paramètres de victoire instantanée
        self.instant_win_gamjeom = 5
        self.instant_win_point_gap = 10
        self.sudden_death_points = 2  # Points nécessaires en round supplémentaire

        # Dictionnaire des drapeaux
        self.flag_dict = {
            "USA": "🇺🇸", "CHN": "🇨🇳", "KOR": "🇰🇷", "JPN": "🇯🇵",
            "FRA": "🇫🇷", "GER": "🇩🇪", "BRA": "🇧🇷", "RUS": "🇷🇺",
            "CI": "ci", "ESP": "🇪🇸", "ITA": "🇮🇹", "CAN": "🇨🇦",
            "ALG": "🇩🇿", "MAR": "🇲🇦", "TUN": "🇹🇳", "EGY": "🇪🇬",
            "SEN": "🇸🇳", "CIV": "🇨🇮", "NGR": "🇳🇬", "RSA": "🇿🇦"
        }

        # Gamepad integration
        self.gamepad_manager = GamepadManager(self)
        self.judge_entries = {}
        self.judge_agreement_timers = {}
        self.judge_pending_inputs = {}
        self.judge_last_input = {}
        self.judge_display = {}

        # Variables pour les modifications en attente
        self.pending_blue_score = 0
        self.pending_red_score = 0
        self.pending_blue_gam = 0
        self.pending_red_gam = 0

        # Configuration de la grille principale
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Créer les frames principaux
        self.create_main_frames()
        
        # Créer le menu principal
        self.create_main_menu()
        
        # Démarrer la surveillance périodique des manettes
        self.gamepad_manager.check_gamepads()
        
        # Gestion de la fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_main_menu(self):
        """Crée le menu principal de l'application"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Nouveau match", command=self.show_configuration_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.on_closing)
        
        # Menu Tournoi
        tournament_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tournoi", menu=tournament_menu)
        tournament_menu.add_command(label="Nouveau tournoi", command=self.create_new_tournament)
        tournament_menu.add_command(label="Charger tournoi", command=self.load_tournament)
        tournament_menu.add_command(label="Importer joueurs", command=self.import_players)
        tournament_menu.add_separator()
        tournament_menu.add_command(label="Générer matchs", command=self.generate_matches)
        tournament_menu.add_command(label="Prochain match", command=self.load_next_match)
        
        # Menu Outils  
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Outils", menu=tools_menu)
        tools_menu.add_command(label="Afficher la pyramide du tournoi", command=self.show_pyramid)
        
        # Menu Thème
        theme_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Thème", menu=theme_menu)
        theme_menu.add_command(label="Clair", command=lambda: self.set_theme("light"))
        theme_menu.add_command(label="Sombre", command=lambda: self.set_theme("dark"))
        
    def show_pyramid(self):
        """Affiche la pyramide du tournoi dans une nouvelle fenêtre"""
        # Vérifier si un tournoi est chargé dans le gestionnaire de tournoi
        if not hasattr(self, 'tournament_manager') or not self.tournament_manager.tournament:
            messagebox.showwarning("Aucun tournoi", "Veuillez d'abord créer ou charger un tournoi.")
            return
            
        # Préparer les données pour la pyramide
        tournament = self.tournament_manager.tournament
        
        # Fonction pour obtenir le nom d'un joueur en toute sécurité
        def get_player_name(player):
            if player is None:
                return 'Bye'
            if hasattr(player, 'name'):
                return player.name
            if hasattr(player, 'to_dict'):
                player_data = player.to_dict()
                return player_data.get('name', str(player))
            return str(player)
        
        # Préparer la liste des joueurs
        players_list = []
        for player in tournament.players.values():
            if hasattr(player, 'to_dict'):  # Si c'est un objet Player
                player_data = player.to_dict()
                players_list.append({
                    'name': player_data.get('name', str(player)),
                    'club': player_data.get('club', ''),
                    'country': player_data.get('country', '')
                })
            else:  # Si c'est une chaîne ou un autre type
                players_list.append({
                    'name': str(player),
                    'club': '',
                    'country': ''
                })
        
        # Préparer la liste des matchs
        matches_list = []
        for match in tournament.matches.values():
            blue_player = getattr(match, 'blue_player', None)
            red_player = getattr(match, 'red_player', None)
            
            matches_list.append({
                'round': getattr(match, 'round_number', 1),
                'player1': get_player_name(blue_player),
                'player2': get_player_name(red_player),
                'winner': getattr(match, 'winner', None),
                'category': getattr(match, 'category', '')
            })
        
        tournament_data = {
            'name': tournament.name,
            'players': players_list,
            'matches': matches_list
        }
            
        # Créer une nouvelle fenêtre pour la pyramide
        pyramid_window = Toplevel(self.root)
        pyramid_window.title(f"Pyramide du Tournoi - {tournament.name}")
        pyramid_window.geometry("1200x900")
        
        # Créer une instance de afficher_pyramide avec les données mises à jour
        try:
            from tour_de_passage import afficher_pyramide
            self.pyramid_viewer = afficher_pyramide(pyramid_window, tournament_data)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'afficher la pyramide: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def set_theme(self, theme_name):
        """Change le thème de l'interface"""
        self.theme_mode = theme_name
        self.apply_theme()
        if self.match_configured:
            self.setup_ui()
        
        # Initialisation des timers pour l'affichage des juges
        self.judge_timers = {}

    def reset_match_data(self):
        """Réinitialiser toutes les données du match"""
        self.is_running = False
        self.is_paused = False
        self.current_time = self.round_time
        self.remaining_break_time = 0
        self.round_number = 1
        self.blue_score = 0
        self.red_score = 0
        self.blue_gam_jeom = 0
        self.red_gam_jeom = 0
        self.match_configured = False
        self.timer_thread = None
        self.break_thread = None
        self.is_break_time = False
        self.round_winners = []
        self.final_winner = None
        self.judge_timers = {}
        
        # Réinitialiser les modifications en attente
        self.pending_blue_score = 0
        self.pending_red_score = 0
        self.pending_blue_gam = 0
        self.pending_red_gam = 0
        
        # Effacer le message de félicitations
        self.winner_frame.grid_remove()
        for widget in self.winner_frame.winfo_children():
            widget.destroy()

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

    def toggle_theme(self):
        """Basculer entre les thèmes clair et sombre"""
        self.theme_mode = "light" if self.theme_mode == "dark" else "dark"
        self.apply_theme()
        if self.match_configured:
            self.setup_ui()

    def create_main_frames(self):
        """Créer la structure principale responsive"""
        # Barre d'outils supérieure
        theme = self.THEMES[self.theme_mode]
        self.toolbar = tk.Frame(self.root, bg=theme["header_bg"], height=40)
        self.toolbar.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        self.toolbar.grid_propagate(False)
        
        # Conteneur principal (responsive)
        self.main_container = tk.Frame(self.root, bg=theme["bg"])
        self.main_container.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Zone pour le vainqueur final
        self.winner_frame = tk.Frame(self.root, bg=theme["winner_bg"], height=0)
        self.winner_frame.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
        self.winner_frame.grid_propagate(False)
        
        # Créer les éléments de la barre d'outils
        self.create_toolbar()

    def create_toolbar(self):
        """Créer la barre d'outils supérieure"""
        theme = self.THEMES[self.theme_mode]
        
        # Bouton Thème
        theme_btn = tk.Button(self.toolbar, text="🌙" if self.theme_mode == "dark" else "☀️", 
                             font=('Arial', 14), command=self.toggle_theme,
                             bg=theme["header_bg"], fg=theme["fg"], bd=0, 
                             activebackground='#555555')
        theme_btn.pack(side='left', padx=10, pady=5)
        
        # Bouton Paramètres
        settings_btn = tk.Button(self.toolbar, text="⚙️", font=('Arial', 14),
                               command=self.show_configuration_dialog,
                               bg=theme["header_bg"], fg=theme["fg"], bd=0, 
                               activebackground='#555555')
        settings_btn.pack(side='right', padx=10, pady=5)
        
        
        # Bouton Aide
        help_btn = tk.Button(self.toolbar, text="❓", font=('Arial', 14),
                           command=self.show_help,
                           bg=theme["header_bg"], fg=theme["fg"], bd=0, 
                           activebackground='#555555')
        help_btn.pack(side='right', padx=10, pady=5)

    def show_configuration_dialog(self):
        """Affiche la fenêtre de configuration modernisée"""
        if (self.is_running or self.is_paused) and not self.final_winner:
            if not self.confirm_action("Configurer un nouveau match ?", 
                                      "Le match actuel n'est pas terminé. Voulez-vous vraiment ouvrir la configuration ?"):
                return

        # Importer la classe MatchConfigDialog ici pour éviter l'erreur
        from match_config_dialog import MatchConfigDialog

        config_window = MatchConfigDialog(self.root, self)
        config_window.grab_set()
        config_window.transient(self.root)
        self.center_window(config_window)

    def center_window(self, window):
        """Centrer une fenêtre sur l'écran"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'+{x}+{y}')

    def confirm_action(self, title, message):
        """Afficher une boîte de confirmation pour les actions critiques"""
        return messagebox.askyesno(title, message)

    def setup_ui(self):
        """Créer l'interface principale"""
        if not self.match_configured:
            return
            
        # Effacer le conteneur principal
        for widget in self.main_container.winfo_children():
            widget.destroy()
            
        theme = self.THEMES[self.theme_mode]
        
        # Configurer la grille responsive
        self.main_container.grid_rowconfigure(0, weight=0)  # Header
        self.main_container.grid_rowconfigure(1, weight=0)  # Country bar
        self.main_container.grid_rowconfigure(2, weight=1)  # Fighters area
        self.main_container.grid_rowconfigure(3, weight=0)  # Round winners
        self.main_container.grid_rowconfigure(4, weight=0)  # Control panel
        self.main_container.grid_rowconfigure(5, weight=0)  # Control buttons
        
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(1, weight=0)  # Control panel
        
        # Créer les zones de l'interface
        self.create_header()
        self.create_info_bar()
        self.create_fighters_area()
        self.create_round_winners()
        self.create_control_panel()
        self.create_main_buttons()  # Boutons principaux en bas
        self.create_modification_controls()
        
        # Raccourcis clavier
        self.setup_keyboard_shortcuts()
        
        # Mise à jour de l'affichage
        self.update_display()
        self.update_button_states()

    def show_modification_controls(self):
        """Affiche les contrôles de modification (pendant la pause)"""
        self.modification_frame.grid()

    def hide_modification_controls(self):
        """Cache les contrôles de modification (quand on reprend)"""
        self.modification_frame.grid_remove()

    def create_header(self):
        """Zone 1 - Header avec toutes les informations"""
        theme = self.THEMES[self.theme_mode]
        header_frame = tk.Frame(self.main_container, bg=theme["header_bg"], height=100)
        header_frame.grid(row=0, column=0, columnspan=2, sticky='nsew', pady=2)
        header_frame.grid_propagate(False)
        
        # Configuration de la grille du header
        header_frame.columnconfigure(0, weight=1)  # Infos gauche
        header_frame.columnconfigure(1, weight=0)  # Centre
        header_frame.columnconfigure(2, weight=1)  # Droite
        
        # Section gauche - Informations générales
        left_frame = tk.Frame(header_frame, bg=theme["header_bg"])
        left_frame.grid(row=0, column=0, sticky='w')
        
        # Match info
        match_info = tk.Label(left_frame, 
                            text=f"Match {self.match_number} • {self.category}",
                            font=('Arial', 14, 'bold'), 
                            fg='white', bg=theme["header_bg"])
        match_info.pack(side='left', padx=10)
        
        # Section centrale - Chronomètre principal
        center_frame = tk.Frame(header_frame, bg=theme["header_bg"])
        center_frame.grid(row=0, column=1)
        
        # Round number
        self.round_label = tk.Label(center_frame, 
                                  text=f"ROUND {self.round_number}",
                                  font=('Arial', 16, 'bold'), 
                                  fg='white', bg=theme["header_bg"])
        self.round_label.pack(pady=(5, 0))
        
        # Temps principal en très grande taille
        self.time_display = tk.Label(center_frame, 
                                   text=self.format_time(self.current_time), 
                                   font=('Arial', 36, 'bold'), 
                                   fg=self.THEMES[self.theme_mode]["time_fg"], 
                                   bg=theme["header_bg"])
        self.time_display.pack(pady=(0, 5))
        
        # Section droite - Statut et connexions
        right_frame = tk.Frame(header_frame, bg=theme["header_bg"])
        right_frame.grid(row=0, column=2, sticky='e')
        
        # Gamepad status
        self.gamepad_status_label = tk.Label(right_frame, text="", 
                                           font=('Arial', 10), 
                                           fg='#FFD700', bg=theme["header_bg"])
        self.gamepad_status_label.pack(side='right', padx=10)
        
        # Status indicator
        self.status_label = tk.Label(right_frame, text="Ready", 
                                   font=('Arial', 12, 'bold'), 
                                   bg='green', fg='white', padx=10, pady=2)
        self.status_label.pack(side='right', padx=10)
        
        self.update_gamepad_status()

    def update_gamepad_status(self):
        """Mettre à jour le statut des manettes"""
        if self.gamepad_manager.gamepads:
            count = len(self.gamepad_manager.gamepads)
            self.gamepad_status_label.config(text=f" {count} 🧑‍⚖️ juge(s) détecté(s)")
        else:
            self.gamepad_status_label.config(text="🧑‍⚖️ Aucun juge détecté")

    def create_info_bar(self):
        """Zone 2 - Barre avec drapeaux, clubs et pays"""
        theme = self.THEMES[self.theme_mode]
        info_frame = tk.Frame(self.main_container, bg='#d0d0d0', height=70)
        info_frame.grid(row=1, column=0, columnspan=2, sticky='nsew', pady=2)
        info_frame.grid_propagate(False)
        
        # Conteneur principal
        info_container = tk.Frame(info_frame, bg='#d0d0d0')
        info_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Partie gauche - Club bleu
        left_section = tk.Frame(info_container, bg='#d0d0d0')
        left_section.pack(side='left', fill='y')
        
        # Drapeau
        flag_label = tk.Label(left_section, text=self.blue_flag, font=('Arial', 24), bg='#d0d0d0')
        flag_label.pack(pady=2)
        
        # Club et pays
        club_label = tk.Label(left_section, 
                            text=f"{self.blue_club} ({self.blue_country})", 
                            font=('Arial', 12, 'bold'), 
                            fg='white', bg='blue', padx=5, pady=2)
        club_label.pack()
        
        # Partie centrale - Informations du match
        center_section = tk.Frame(info_container, bg='#d0d0d0')
        center_section.pack(side='left', fill='both', expand=True, padx=10)
        
        # Nom des combattants
        names_frame = tk.Frame(center_section, bg='#d0d0d0')
        names_frame.pack(pady=5)
        
        blue_name_label = tk.Label(names_frame, text=self.blue_name, font=('Arial', 16, 'bold'), 
                                 fg='blue', bg='#d0d0d0')
        blue_name_label.pack(side='left', padx=20)
        
        vs_label = tk.Label(names_frame, text="VS", font=('Arial', 12, 'bold'), 
                          fg='black', bg='#d0d0d0')
        vs_label.pack(side='left', padx=20)
        
        red_name_label = tk.Label(names_frame, text=self.red_name, font=('Arial', 16, 'bold'), 
                                fg='red', bg='#d0d0d0')
        red_name_label.pack(side='left', padx=20)
        
        # Temps de repos
        break_frame = tk.Frame(center_section, bg='#d0d0d0')
        break_frame.pack(pady=5)  
        
        tk.Label(break_frame, text="Temps Repos:", font=('Arial', 10), 
                bg='#d0d0d0').pack(side='left')
        self.break_display = tk.Label(break_frame, text=self.format_time(self.remaining_break_time), 
                             font=('Arial', 14, 'bold'), 
                             fg='white', bg='black', padx=5, pady=2)
        self.break_display.pack(side='left', padx=5)
        
        # Partie droite - Club rouge
        right_section = tk.Frame(info_container, bg='#d0d0d0')
        right_section.pack(side='right', fill='y')
        
        # Drapeau
        flag_label = tk.Label(right_section, text=self.red_flag, font=('Arial', 24), bg='#d0d0d0')
        flag_label.pack(pady=2)
        
        # Club et pays
        club_label = tk.Label(right_section, 
                            text=f"{self.red_club} ({self.red_country})", 
                            font=('Arial', 12, 'bold'),  
                            fg='white', bg='red', padx=5, pady=2)
        club_label.pack()

    def create_fighters_area(self):
        """Zones 3 & 4 - Aires des combattants"""
        theme = self.THEMES[self.theme_mode]
        fighters_frame = tk.Frame(self.main_container, bg=theme["bg"])
        fighters_frame.grid(row=2, column=0, sticky='nsew', padx=2, pady=2)
        fighters_frame.grid_propagate(False)
        
        # Configuration de grille pour les combattants
        fighters_frame.grid_rowconfigure(0, weight=1)
        fighters_frame.grid_columnconfigure(0, weight=1)
        fighters_frame.grid_columnconfigure(1, weight=1)
        
        # Combattant BLEU (gauche)
        blue_frame = tk.Frame(fighters_frame, bg=theme["blue_bg"])
        blue_frame.grid(row=0, column=0, sticky='nsew', padx=2, pady=2)
        
        # Nom du combattant bleu
        self.blue_name_label = tk.Label(blue_frame, text=self.blue_name, font=('Arial', 14, 'bold'), 
                                      fg='white', bg=theme["blue_header"])
        self.blue_name_label.pack(fill='x')
        
        # Score du combattant bleu
        self.blue_score_label = tk.Label(blue_frame, text="0", 
                                        font=('Arial', 80, 'bold'), 
                                        fg='white', bg=theme["blue_bg"])
        self.blue_score_label.pack(fill='both', expand=True)
        
        # Affichage des juges pour le bleu
        blue_judges_frame = tk.Frame(blue_frame, bg=theme["blue_bg"])
        blue_judges_frame.pack(fill='x', pady=5)
        
        tk.Label(blue_judges_frame, text="Entrées Juges:", font=('Arial', 10, 'bold'),
                fg='white', bg=theme["blue_bg"]).pack(anchor='w', padx=10)
        
        judges_frame = tk.Frame(blue_judges_frame, bg=theme["blue_bg"])
        judges_frame.pack(fill='x', padx=10, pady=5)
        
        self.blue_judge_labels = []
        for i in range(self.judges_count):
            frame = tk.Frame(judges_frame, bg=theme["judge_bg"], bd=1, relief='solid')
            frame.pack(side='left', padx=5, pady=2)
            tk.Label(frame, text=f"J{i+1}", font=('Arial', 8), 
                    bg=theme["judge_bg"], fg=theme["judge_fg"]).pack(side='left', padx=2)
            label = tk.Label(frame, text="", font=('Arial', 10, 'bold'), 
                           bg=theme["judge_bg"], fg=theme["judge_fg"], width=8)
            label.pack(side='left', padx=2)
            self.blue_judge_labels.append(label)
        
        # Pénalités bleu
        blue_penalties_frame = tk.Frame(blue_frame, bg=theme["blue_bg"])
        blue_penalties_frame.pack(fill='x', pady=5)
        
        tk.Label(blue_penalties_frame, text="Gam-jeom:", font=('Arial', 12, 'bold'),
                fg='white', bg=theme["blue_bg"]).pack(side='left', padx=10)
        self.blue_gam_label = tk.Label(blue_penalties_frame, text="0", font=('Arial', 16, 'bold'),
                                      fg='red', bg=theme["blue_bg"])
        self.blue_gam_label.pack(side='left', padx=5)
        
        # Combattant ROUGE (droite)
        red_frame = tk.Frame(fighters_frame, bg=theme["red_bg"])
        red_frame.grid(row=0, column=1, sticky='nsew', padx=2, pady=2)
        
        # Nom du combattant rouge
        self.red_name_label = tk.Label(red_frame, text=self.red_name, font=('Arial', 14, 'bold'), 
                                     fg='white', bg=theme["red_header"])
        self.red_name_label.pack(fill='x')
        
        # Score du combattant rouge
        self.red_score_label = tk.Label(red_frame, text="0", 
                                       font=('Arial', 80, 'bold'), 
                                       fg='white', bg=theme["red_bg"])
        self.red_score_label.pack(fill='both', expand=True)
        
        # Affichage des juges pour le rouge
        red_judges_frame = tk.Frame(red_frame, bg=theme["red_bg"])
        red_judges_frame.pack(fill='x', pady=5)
        
        tk.Label(red_judges_frame, text="Entrées Juges:", font=('Arial', 10, 'bold'),
                fg='white', bg=theme["red_bg"]).pack(anchor='w', padx=10)
        
        judges_frame = tk.Frame(red_judges_frame, bg=theme["red_bg"])
        judges_frame.pack(fill='x', padx=10, pady=5)
        
        self.red_judge_labels = []
        for i in range(self.judges_count):
            frame = tk.Frame(judges_frame, bg=theme["judge_bg"], bd=1, relief='solid')
            frame.pack(side='left', padx=5, pady=2)
            tk.Label(frame, text=f"J{i+1}", font=('Arial', 8), 
                    bg=theme["judge_bg"], fg=theme["judge_fg"]).pack(side='left', padx=2)
            label = tk.Label(frame, text="", font=('Arial', 10, 'bold'), 
                           bg=theme["judge_bg"], fg=theme["judge_fg"], width=8)
            label.pack(side='left', padx=2)
            self.red_judge_labels.append(label)
        
        # Pénalités rouge
        red_penalties_frame = tk.Frame(red_frame, bg=theme["red_bg"])
        red_penalties_frame.pack(fill='x', pady=5)
        
        tk.Label(red_penalties_frame, text="Gam-jeom:", font=('Arial', 12, 'bold'),
                fg='white', bg=theme["red_bg"]).pack(side='left', padx=10)
        self.red_gam_label = tk.Label(red_penalties_frame, text="0", font=('Arial', 16, 'bold'),
                                     fg='yellow', bg=theme["red_bg"])
        self.red_gam_label.pack(side='left', padx=5)

    def create_round_winners(self):
        """Zone pour afficher les gagnants des rounds"""
        theme = self.THEMES[self.theme_mode]
        self.round_winners_frame = tk.Frame(self.main_container, bg=theme["round_bg"], height=30)
        self.round_winners_frame.grid(row=3, column=0, columnspan=2, sticky='nsew', pady=2)
        self.round_winners_frame.grid_propagate(False)
        
        tk.Label(self.round_winners_frame, text="🏆 Gagnants des Rounds", 
                font=('Arial', 14, 'bold'), fg='#4FC3F7', bg=theme["round_bg"]).pack(pady=10)
        
        self.winners_display_frame = tk.Frame(self.round_winners_frame, bg=theme["round_bg"])
        self.winners_display_frame.pack(fill='x', pady=10)
        
        self.update_round_winners_display()

    def update_round_winners_display(self):
        """Mettre à jour l'affichage des gagnants de rounds"""
        # Effacer l'affichage précédent
        for widget in self.winners_display_frame.winfo_children():
            widget.destroy()
        
        theme = self.THEMES[self.theme_mode]
        
        # Créer un cadre pour les étoiles des rounds
        rounds_frame = tk.Frame(self.winners_display_frame, bg=theme["round_bg"])
        rounds_frame.pack()
        
        # Pour chaque round (jusqu'au nombre maximum de rounds)
        for i in range(self.max_rounds):
            round_frame = tk.Frame(rounds_frame, bg=theme["round_bg"], width=50, height=50, relief='solid', bd=1)
            round_frame.grid(row=0, column=i, padx=5, pady=5)
            round_frame.grid_propagate(False)  # Pour garder la taille fixe
            
            # Numéro du round
            tk.Label(round_frame, text=f"{i+1}", 
                    font=('Arial', 10), fg=theme["fg"], bg=theme["round_bg"]).place(relx=0.5, rely=0.2, anchor='center')
            
            # Si ce round a un gagnant (i < len(self.round_winners))
            if i < len(self.round_winners):
                winner = self.round_winners[i]
                if winner == 'blue':
                    color = theme["blue_bg"]
                    text = "★"
                elif winner == 'red':
                    color = theme["red_bg"]
                    text = "★"
                else:  # draw
                    color = theme["round_bg"]
                    text = "="
                label = tk.Label(round_frame, text=text, font=('Arial', 24), bg=color, fg='white')
                label.place(relx=0.5, rely=0.6, anchor='center')

    def create_control_panel(self):
        """Zone 6 - Panneau de contrôle droit"""
        theme = self.THEMES[self.theme_mode]
        control_frame = tk.Frame(self.main_container, bg=theme["bg"])
        control_frame.grid(row=4, column=1, sticky='nsew', padx=5, pady=5)
        
        # Container principal pour les contrôles
        controls_container = tk.Frame(control_frame, bg=theme["bg"])
        controls_container.pack(fill='both', expand=True)
        
        # Boutons de contrôle rapide
        quick_buttons_frame = tk.Frame(controls_container, bg='#d0d0d0')
        quick_buttons_frame.pack(fill='x', pady=5)

    def create_main_buttons(self):
        """Créer les boutons principaux en bas de l'interface"""
        theme = self.THEMES[self.theme_mode]
        buttons_frame = tk.Frame(self.main_container, bg=theme["bg"])
        buttons_frame.grid(row=5, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)
        
        # Conteneur pour centrer les boutons
        container = tk.Frame(buttons_frame, bg=theme["bg"])
        container.pack(expand=True, fill='both')
        
        # Boutons principaux
        buttons = [
            {'text': "Start Round", 'command': self.start_round, 'bg': '#4CAF50', 'width': 120, 'height': 50},
            {'text': "Pause", 'command': self.pause_round, 'bg': '#FF9800', 'width': 120, 'height': 50},
            {'text': "End Round", 'command': self.end_round, 'bg': '#F44336', 'width': 120, 'height': 50},
            {'text': "Next Round", 'command': self.next_round, 'bg': '#2196F3', 'width': 120, 'height': 50},
            {'text': "Sauvegarder", 'command': self.save_match_result, 'bg': '#9C27B0', 'width': 120, 'height': 50}
        ]
        
        # Créer les boutons
        self.main_buttons = {}
        for i, btn_info in enumerate(buttons):
            btn = tk.Button(
                container, 
                text=btn_info['text'],
                command=btn_info['command'],
                bg=btn_info['bg'],
                fg='white',
                font=('Arial', 12, 'bold'),
                width=15,
                height=2,
                bd=0,
                relief='raised',
                activebackground=btn_info['bg']
            )
            btn.grid(row=0, column=i, padx=20, pady=10)
            
            # Stocker les boutons importants pour les mises à jour
            self.main_buttons[btn_info['text']] = btn
    
    def create_modification_controls(self):
        """Contrôles de modification (visibles seulement en pause)"""
        theme = self.THEMES[self.theme_mode]
        self.modification_frame = tk.Frame(self.main_container, bg=theme["bg"], relief='raised', bd=2)
        self.modification_frame.grid(row=4, column=0, sticky='nsew', padx=5, pady=5)
        
        # Titre
        tk.Label(self.modification_frame, text="CONTRÔLES DE MODIFICATION", 
                font=('Arial', 12, 'bold'), bg=theme["bg"], fg='red').pack(pady=5)
        
        # Conteneur avec barre de défilement
        container = tk.Frame(self.modification_frame, bg=theme["bg"])
        container.pack(fill='both', expand=True, padx=5, pady=5)
        
        canvas = tk.Canvas(container, bg=theme["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=theme["bg"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        scrollable_frame.pack(pady=5)
        
        # Boutons de score
        score_frame = tk.Frame(scrollable_frame, bg=theme["bg"])
        score_frame.pack(pady=5)
        
        # Score Bleu
        blue_score_frame = tk.Frame(score_frame, bg=theme["bg"])
        blue_score_frame.pack(side='left', padx=10)
        
        tk.Label(blue_score_frame, text="Score Bleu", font=('Arial', 10, 'bold'), 
                bg=theme["bg"], fg='blue').pack()
        
        # Affichage des modifications en attente
        self.blue_pending_label = tk.Label(blue_score_frame, text="Modification: +0", 
                                         font=('Arial', 9), bg=theme["bg"], fg='green')
        self.blue_pending_label.pack()
        
        blue_buttons = tk.Frame(blue_score_frame, bg=theme["bg"])
        blue_buttons.pack(pady=5)
        
        # Boutons positifs
        for points in [1, 2, 3, 4, 5]:
            tk.Button(blue_buttons, text=f"+{points}", 
                     command=lambda p=points: self.modify_score('blue', p),
                     bg='green', fg='white', padx=5).pack(side='left', padx=2)
        
        # Boutons négatifs
        for points in [-1, -2, -3, -4, -5]:
            tk.Button(blue_buttons, text=f"{points}", 
                     command=lambda p=points: self.modify_score('blue', p),
                     bg='red', fg='white', padx=5).pack(side='left', padx=2)
        
        # Score Rouge
        red_score_frame = tk.Frame(score_frame, bg=theme["bg"])
        red_score_frame.pack(side='right', padx=10)
        
        tk.Label(red_score_frame, text="Score Rouge", font=('Arial', 10, 'bold'), 
                bg=theme["bg"], fg='red').pack()
        
        # Affichage des modifications en attente
        self.red_pending_label = tk.Label(red_score_frame, text="Modification: +0", 
                                        font=('Arial', 9), bg=theme["bg"], fg='green')
        self.red_pending_label.pack()
        
        red_buttons = tk.Frame(red_score_frame, bg=theme["bg"])
        red_buttons.pack(pady=5)
        
        # Boutons positifs
        for points in [1, 2, 3, 4, 5]:
            tk.Button(red_buttons, text=f"+{points}", 
                     command=lambda p=points: self.modify_score('red', p),
                     bg='green', fg='white', padx=5).pack(side='left', padx=2)
        
        # Boutons négatifs
        for points in [-1, -2, -3, -4, -5]:
            tk.Button(red_buttons, text=f"{points}", 
                     command=lambda p=points: self.modify_score('red', p),
                     bg='red', fg='white', padx=5).pack(side='left', padx=2)
        
                
        # Gam-jeom Bleu
        blue_gam_frame = tk.Frame(scrollable_frame, bg=theme["bg"])
        blue_gam_frame.pack(side='left', padx=10, pady=5)
        
        tk.Label(blue_gam_frame, text="Gam-jeom Bleu", font=('Arial', 10, 'bold'), 
                bg=theme["bg"], fg='blue').pack()
        
        # Affichage des modifications en attente
        self.blue_gam_pending_label = tk.Label(blue_gam_frame, text="Modification: +0", 
                                             font=('Arial', 9), bg=theme["bg"], fg='green')
        self.blue_gam_pending_label.pack()
        
        blue_gam_buttons = tk.Frame(blue_gam_frame, bg=theme["bg"])
        blue_gam_buttons.pack(pady=5)
        
        tk.Button(blue_gam_buttons, text="+", command=lambda: self.modify_penalty('blue', 'gam_jeom', 1),
                 bg='green', fg='white', padx=5).pack(side='left', padx=2)
        tk.Button(blue_gam_buttons, text="-", command=lambda: self.modify_penalty('blue', 'gam_jeom', -1),
                 bg='red', fg='white', padx=5).pack(side='left', padx=2)
        
        # Gam-jeom Rouge
        red_gam_frame = tk.Frame(scrollable_frame, bg=theme["bg"])
        red_gam_frame.pack(side='right', padx=10, pady=5)
        
        tk.Label(red_gam_frame, text="Gam-jeom Rouge", font=('Arial', 10, 'bold'), 
                bg=theme["bg"], fg='red').pack()
        
        # Affichage des modifications en attente
        self.red_gam_pending_label = tk.Label(red_gam_frame, text="Modification: +0", 
                                            font=('Arial', 9), bg=theme["bg"], fg='green')
        self.red_gam_pending_label.pack()
        
        red_gam_buttons = tk.Frame(red_gam_frame, bg=theme["bg"])
        red_gam_buttons.pack(pady=5)
        
        tk.Button(red_gam_buttons, text="+", command=lambda: self.modify_penalty('red', 'gam_jeom', 1),
                 bg='green', fg='white', padx=5).pack(side='left', padx=2)
        tk.Button(red_gam_buttons, text="-", command=lambda: self.modify_penalty('red', 'gam_jeom', -1),
                 bg='red', fg='white', padx=5).pack(side='left', padx=2)
        
        # Paramètres de temps
        time_frame = tk.Frame(scrollable_frame, bg=theme["bg"])
        time_frame.pack(fill='x', pady=10)
        
        tk.Label(time_frame, text="Modifier Temps:", font=('Arial', 10, 'bold'), 
                bg=theme["bg"]).pack(side='left', padx=5)
        
        # Temps du round
        tk.Label(time_frame, text="Round (s):", bg=theme["bg"]).pack(side='left', padx=2)
        self.round_time_entry = tk.Entry(time_frame, width=5)
        self.round_time_entry.insert(0, str(self.round_time))
        self.round_time_entry.pack(side='left', padx=2)
        
        # Temps de repos
        tk.Label(time_frame, text="Repos (s):", bg=theme["bg"]).pack(side='left', padx=2)
        self.break_time_entry = tk.Entry(time_frame, width=5)
        self.break_time_entry.insert(0, str(self.break_time))
        self.break_time_entry.pack(side='left', padx=2)
        
        # Bouton d'application
        apply_frame = tk.Frame(scrollable_frame, bg=theme["bg"])
        apply_frame.pack(pady=10)
        
        tk.Button(apply_frame, text="Appliquer Modifications", 
                 font=('Arial', 10, 'bold'), bg='blue', fg='white',
                 command=self.apply_modifications).pack()
        
        # Bouton Annuler modifications
        tk.Button(apply_frame, text="Annuler Modifications", 
                 font=('Arial', 10, 'bold'), bg='red', fg='white',
                 command=self.cancel_modifications).pack(pady=5)
        
        # Cacher par défaut
        self.modification_frame.grid_remove()
        
    def update_pending_labels(self):
        """Mettre à jour les labels des modifications en attente"""
        self.blue_pending_label.config(text=f"Modification: {self.pending_blue_score:+d}")
        self.red_pending_label.config(text=f"Modification: {self.pending_red_score:+d}")
        self.blue_gam_pending_label.config(text=f"Modification: {self.pending_blue_gam:+d}")
        self.red_gam_pending_label.config(text=f"Modification: {self.pending_red_gam:+d}")

    def setup_keyboard_shortcuts(self):
        """Configurer les raccourcis clavier"""
        self.root.bind('<space>', lambda event: self.toggle_pause())
        
    def format_time(self, seconds):
        """Formater le temps en MM:SS"""
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"
    
    def start_round(self):
        """Démarrer le chronomètre du round"""
        if self.is_break_time:
            return
            
        if not self.is_running and not self.is_paused:
            self.is_running = True
            self.timer_thread = threading.Thread(target=self.run_timer, daemon=True)
            self.timer_thread.start()
            self.status_label.config(text="Running", bg='green')
            self.update_button_states()
        elif self.is_paused:
            self.is_paused = False
            self.is_running = True
            self.status_label.config(text="Running", bg='green')
            self.hide_modification_controls()  # Correction ici
            self.update_button_states()
    
    def run_timer(self):
        """Thread pour gérer le chronomètre"""
        while self.is_running and self.current_time > 0:
            if not self.is_paused:
                self.current_time -= 1
                self.time_display.config(text=self.format_time(self.current_time))
                # Changement de couleur pour les derniers instants
                if self.current_time <= 10:
                    self.time_display.config(fg='red')
                time.sleep(1)
        
        if self.current_time <= 0:
            self.end_round()
    
    def start_break(self):
        """Démarrer le temps de repos entre les rounds"""
        self.is_break_time = True
        self.remaining_break_time = self.break_time
        self.status_label.config(text="Break Time", bg='purple')
        self.update_button_states()
        
        self.break_thread = threading.Thread(target=self.run_break_timer, daemon=True)
        self.break_thread.start()
    
    def run_break_timer(self):
        """Thread pour gérer le temps de repos"""
        while self.remaining_break_time > 0 and self.is_break_time:
            self.remaining_break_time -= 1
            self.break_display.config(text=self.format_time(self.remaining_break_time))
            # Changement de couleur pour les derniers instants
            if self.remaining_break_time <= 10:
                self.break_display.config(fg='red')
            time.sleep(1)
        
        if self.remaining_break_time <= 0:
            self.next_round()
    
    def pause_round(self):
        """Mettre en pause le round"""
        if self.is_running and not self.is_paused:
            self.is_paused = True
            self.status_label.config(text="Paused", bg='orange')
            self.show_modification_controls()  # Correction ici
            self.update_button_states()
        
    def toggle_pause(self):
        """Basculer entre pause et reprise"""
        if self.is_running:
            if not self.is_paused:
                self.pause_round()
            else:
                self.start_round()
    
    def end_round(self):
        """Termine le round en cours"""
        if not self.is_running:
            return

        # Arrêter le chronomètre
        self.is_running = False
        self.is_paused = False

        # Déterminer le gagnant du round
        if self.blue_score > self.red_score:
            winner = 'blue'
        elif self.red_score > self.blue_score:
            winner = 'red'
        else:
            winner = 'draw'  # Égalité

        self.round_winners.append(winner)
        self.update_round_winners_display()

        # Vérifier si le match est terminé (tous les rounds joués)
        if len(self.round_winners) == self.max_rounds:
            # Déterminer le gagnant final
            blue_wins = self.round_winners.count('blue')
            red_wins = self.round_winners.count('red')
            if blue_wins > red_wins:
                self.final_winner = 'blue'
            elif red_wins > blue_wins:
                self.final_winner = 'red'
            else:
                # Égalité après tous les rounds - on ajoute un round supplémentaire
                self.max_rounds += 1
                self.start_break()
                return

            # Afficher le vainqueur final
            self.show_final_winner()
        else:
            # Démarrer le temps de repos avant le prochain round
            self.start_break()

        self.update_button_states()

    def next_round(self):
        """Passer au round suivant"""
        if self.round_number >= self.max_rounds:
            return
            
        self.is_break_time = False
        self.round_number += 1
        self.current_time = self.round_time
        theme = self.THEMES[self.theme_mode]
        self.time_display.config(text=self.format_time(self.current_time))
        self.break_display.config(text=self.format_time(self.break_time))
        self.round_label.config(text=f"ROUND {self.round_number}")
        self.status_label.config(text="Ready", bg='green')
        self.update_button_states()
        
        # Réinitialiser les scores pour le nouveau round
        self.blue_score = 0
        self.red_score = 0
        self.blue_score_label.config(text="0")
        self.red_score_label.config(text="0")
        
        # Réinitialiser les gam-jeom pour le nouveau round
        self.blue_gam_jeom = 0
        self.red_gam_jeom = 0
        self.blue_gam_label.config(text="0")
        self.red_gam_label.config(text="0")
        
        # Réinitialiser les affichages des juges
        for label in self.blue_judge_labels:
            label.config(text="")
        for label in self.red_judge_labels:
            label.config(text="")
        
        self.update_round_winners_display()
        self.update_button_states()
    
    def show_final_winner(self, winner=None):
        """Afficher le vainqueur final du match"""
        theme = self.THEMES[self.theme_mode]
        if not winner:
            # Déterminer le vainqueur si non fourni
            blue_wins = self.round_winners.count("blue")
            red_wins = self.round_winners.count("red")
            if blue_wins > red_wins:
                winner = "blue"
            elif red_wins > blue_wins:
                winner = "red"
            else:
                # Égalité, on ne devrait normalement pas arriver ici car on a ajouté un round supplémentaire
                winner = "draw"

        if winner == "draw":
            winner_name = "Match nul"
        else:
            winner_name = self.blue_name if winner == "blue" else self.red_name

        # Afficher le vainqueur final de manière spectaculaire
        self.winner_frame.config(height=80, bg=theme["winner_bg"])
        self.winner_frame.pack_propagate(False)

        # Effacer tout contenu précédent
        for widget in self.winner_frame.winfo_children():
            widget.destroy()

        # Message de félicitations
        congrats_label = tk.Label(self.winner_frame, 
                                text=f"FÉLICITATIONS À {winner_name.upper()} !",
                                font=('Arial', 20, 'bold'), bg=theme["winner_bg"], fg=theme["winner_fg"])
        congrats_label.pack(expand=True, fill='both')

        # Sous-titre
        champ_label = tk.Label(self.winner_frame, 
                             text="VAINQUEUR DU MATCH",
                             font=('Arial', 16, 'bold'), bg=theme["winner_bg"], fg=theme["winner_fg"])
        champ_label.pack(expand=True, fill='both')

        # Désactiver les boutons
        self.update_button_states()

        # S'assurer que le frame est visible
        self.winner_frame.grid()

        # Sauvegarder automatiquement le résultat du match
        self.final_winner = winner
        self.save_match_result()
    
    def add_score(self, fighter, points):
        """Ajouter des points à un combattant"""
        if fighter == 'blue':
            self.blue_score += points
            self.blue_score_label.config(text=str(self.blue_score))
        else:
            self.red_score += points
            self.red_score_label.config(text=str(self.red_score))
        
        # Vérifier les conditions de victoire instantanée pour le round
        self.check_instant_win_round()
    
    def check_instant_win_round(self):
        """Vérifier les conditions de victoire instantanée pour le round en cours"""
        if not self.is_running or self.is_paused:
            return
            
        # Victoire par gam-jeom
        if self.instant_win_gamjeom > 0:
            if self.blue_gam_jeom >= self.instant_win_gamjeom:
                # Victoire de l'adversaire (rouge) pour ce round
                self.end_round()
                return
            elif self.red_gam_jeom >= self.instant_win_gamjeom:
                # Victoire de l'adversaire (bleu) pour ce round
                self.end_round()
                return
        
        
        # Round supplémentaire - victoire par points
        if self.round_number > self.max_rounds:
            if self.blue_score >= self.sudden_death_points:
                self.end_round()
            elif self.red_score >= self.sudden_death_points:
                self.end_round()
    
    def modify_score(self, fighter, points):
        """Modifier le score pendant la pause"""
        if self.is_paused:
            if fighter == 'blue':
                self.pending_blue_score += points
            else:
                self.pending_red_score += points
            self.update_pending_labels()
    
    def modify_penalty(self, fighter, penalty_type, value):
        """Modifier les pénalités pendant la pause"""
        if self.is_paused:
            if fighter == 'blue':
                self.pending_blue_gam += value
                # Ajouter le point pour l'adversaire
                self.pending_red_score += value
            else:
                self.pending_red_gam += value
                # Ajouter le point pour l'adversaire
                self.pending_blue_score += value
            self.update_pending_labels()
    
    def apply_modifications(self):
        """Appliquer les modifications et reprendre le match"""
        # Mettre à jour les scores avec les modifications en attente
        self.blue_score += self.pending_blue_score
        self.red_score += self.pending_red_score
        self.blue_gam_jeom += self.pending_blue_gam
        self.red_gam_jeom += self.pending_red_gam
        
        # Mettre à jour l'affichage
        self.blue_score_label.config(text=str(self.blue_score))
        self.red_score_label.config(text=str(self.red_score))
        self.blue_gam_label.config(text=str(self.blue_gam_jeom))
        self.red_gam_label.config(text=str(self.red_gam_jeom))
        
        # Réinitialiser les modifications en attente
        self.pending_blue_score = 0
        self.pending_red_score = 0
        self.pending_blue_gam = 0
        self.pending_red_gam = 0
        self.update_pending_labels()
        
        # Mettre à jour les paramètres de temps
        try:
            self.round_time = int(self.round_time_entry.get())
            self.break_time = int(self.break_time_entry.get())
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs de temps valides")
        
        if self.is_paused:
            self.is_paused = False
            self.is_running = True
            self.status_label.config(text="Running", bg='green')
            self.hide_modification_controls()
            self.update_button_states()
    
    def cancel_modifications(self):
        """Annuler les modifications en attente"""
        self.pending_blue_score = 0
        self.pending_red_score = 0
        self.pending_blue_gam = 0
        self.pending_red_gam = 0
        self.update_pending_labels()
    
    def show_settings(self):
        """Afficher les paramètres"""
        self.show_configuration_dialog()
    
    def show_help(self):
        """Afficher l'aide"""
        help_text = """
        Raccourcis clavier:
        - Espace: Pause/Reprendre
        - S: Démarrer le round
        - E: Terminer le round
        - N: Round suivant
        
        Contrôles:
        - Utilisez les boutons colorés pour ajouter des points
        - En pause, utilisez les contrôles de modification
        """
        messagebox.showinfo("Aide", help_text)
    
    def update_display(self):
        """Mettre à jour tous les éléments de l'interface"""
        # Vérifier que les éléments d'interface existent avant de les mettre à jour
        if not hasattr(self, 'blue_score_label') or not self.match_configured:
            return
            
        self.blue_score_label.config(text=str(self.blue_score))
        self.red_score_label.config(text=str(self.red_score))
        self.blue_gam_label.config(text=str(self.blue_gam_jeom))
        self.red_gam_label.config(text=str(self.red_gam_jeom))
        self.time_display.config(text=self.format_time(self.current_time))
        self.round_label.config(text=f"ROUND {self.round_number}")
    

    def process_judge_input(self, judge_id, player, value):
        """Traiter les entrées des juges depuis les manettes"""
        # Conditions: rejeter si match non commencé ou en pause
        if not self.is_running or self.is_paused:
            return
            
        # Mettre à jour l'affichage du juge
        if player == 'blue':
            label = self.blue_judge_labels[judge_id]
        else:
            label = self.red_judge_labels[judge_id]
            
        if value == 'GAM-JEOM':
            text = "Gam-jeom"
        else:
            text = f"+{value}"
        label.config(text=text)
        
        # Planifier l'effacement après 2 secondes
        if (judge_id, player) in self.judge_timers:
            self.root.after_cancel(self.judge_timers[(judge_id, player)])
        self.judge_timers[(judge_id, player)] = self.root.after(2000, 
            lambda j=judge_id, p=player: self.clear_judge_display(j, p))
        
        # Si une seule manette est connectée, appliquer immédiatement
        if len(self.gamepad_manager.gamepads) == 1:
            self.apply_judge_input(player, value, judge_id)
            return
        
        # Sinon, utiliser le système d'accord entre juges
        current_time = time.time()
        key = (player, value)
        
        # Réinitialiser le timer si nouvelle entrée
        if key not in self.judge_last_input or current_time - self.judge_last_input[key] > 2:
            self.judge_pending_inputs[key] = set()
        
        # Enregistrer l'entrée du juge
        self.judge_pending_inputs[key].add(judge_id)
        self.judge_last_input[key] = current_time
        
        # Vérifier si on a au moins 2 juges d'accord
        if len(self.judge_pending_inputs[key]) >= 2:
            self.apply_judge_input(player, value, judge_id)
            # Réinitialiser les entrées pour cette action
            del self.judge_pending_inputs[key]
            del self.judge_last_input[key]
            
    def clear_judge_display(self, judge_id, player):
        """Effacer l'affichage d'un juge après 2 secondes"""
        if player == 'blue' and judge_id < len(self.blue_judge_labels):
            self.blue_judge_labels[judge_id].config(text="")
        elif player == 'red' and judge_id < len(self.red_judge_labels):
            self.red_judge_labels[judge_id].config(text="")
        
        # Supprimer le timer
        if (judge_id, player) in self.judge_timers:
            del self.judge_timers[(judge_id, player)]
    
    def apply_judge_input(self, player, value, judge_id=None):
        """Appliquer l'entrée d'un juge au score"""
        if value == 'GAM-JEOM':
            if player == 'blue':
                # Bleu reçoit un gam-jeom = +1 point pour rouge
                self.red_score += 1
                self.red_score_label.config(text=str(self.red_score))
                # Incrémenter le compteur de gam-jeom du bleu
                self.blue_gam_jeom += 1
                self.blue_gam_label.config(text=str(self.blue_gam_jeom))
            else:
                # Rouge reçoit un gam-jeom = +1 point pour bleu
                self.blue_score += 1
                self.blue_score_label.config(text=str(self.blue_score))
                # Incrémenter le compteur de gam-jeom du rouge
                self.red_gam_jeom += 1
                self.red_gam_label.config(text=str(self.red_gam_jeom))
        else:
            # Points normaux
            self.add_score(player, value)
        
        # Vérifier les conditions de victoire instantanée pour le round
        self.check_instant_win_round()
    
    def show_notification(self, message, level='info'):
        """Afficher une notification temporaire"""
        theme = self.THEMES[self.theme_mode]
        colors = {
            'info': '#2196F3',
            'success': '#4CAF50',
            'warning': '#FF9800',
            'error': '#F44336'
        }
        
        # Créer une fenêtre temporaire
        notification = tk.Toplevel(self.root)
        notification.wm_overrideredirect(True)
        notification.geometry("+100+100")
        notification.attributes("-alpha", 0.9)
        
        # Calculer la position
        x = self.root.winfo_rootx() + 50
        y = self.root.winfo_rooty() + 50
        notification.geometry(f"+{x}+{y}")
        
        # Créer le label
        label = tk.Label(notification, text=message, font=('Arial', 14, 'bold'), 
                        bg=colors.get(level, '#2196F3'), fg='white', padx=20, pady=10)
        label.pack()
        
        # Fermer après 2 secondes
        notification.after(2000, notification.destroy)
    
    def on_closing(self):
        """Gestionnaire de fermeture"""
        # Sauvegarder le tournoi en cours si nécessaire
        if hasattr(self, 'tournament_manager') and self.tournament_manager.tournament:
            if messagebox.askyesno("Sauvegarde", "Voulez-vous sauvegarder le tournoi en cours?"):
                self.tournament_manager.save_tournament()
        
        # Arrêter les threads de surveillance des manettes
        self.gamepad_manager.stop_monitoring = True
        for thread in self.gamepad_manager.monitoring_threads:
            if thread.is_alive():
                thread.join(timeout=1)

        self.root.quit()
        self.root.destroy()
    
    def create_new_tournament(self):
        """Crée un nouveau tournoi"""
        from tournament_manager import TournamentDialog
        dialog = TournamentDialog(self.root, self.tournament_manager)
        self.root.wait_window(dialog)
    
    def load_tournament(self):
        """Charge un tournoi existant"""
        try:
            # Charger le tournoi via le gestionnaire de tournoi
            tournament = self.tournament_manager.load_tournament()
            if not tournament:
                messagebox.showerror("Erreur", "Impossible de charger le tournoi. Le fichier est peut-être corrompu.")
                return
                
            # Mettre à jour les données du tournoi dans l'interface
            self.tournament_data = {
                'name': tournament.name,
                'category': getattr(tournament, 'category', ''),
                'players': [],
                'matches': []
            }
            
            # Fonction pour obtenir les informations d'un joueur de manière sécurisée
            def get_player_info(player):
                if player is None:
                    return None
                    
                if hasattr(player, 'to_dict'):
                    return player.to_dict()
                    
                # Si c'est déjà un dictionnaire
                if isinstance(player, dict):
                    return player
                    
                # Créer un dictionnaire basique avec les attributs disponibles
                return {
                    'id': getattr(player, 'id', str(id(player))),
                    'name': getattr(player, 'name', str(player)),
                    'club': getattr(player, 'club', ''),
                    'country': getattr(player, 'country', ''),
                    'category': getattr(player, 'category', '')
                }
            
            # Mettre à jour la liste des joueurs
            if hasattr(tournament, 'players') and tournament.players:
                for player_id, player in tournament.players.items():
                    player_info = get_player_info(player)
                    if player_info:
                        self.tournament_data['players'].append(player_info)
            
            # Mettre à jour la liste des matchs
            if hasattr(tournament, 'matches') and tournament.matches:
                for match_id, match in tournament.matches.items():
                    blue_player = getattr(match, 'blue_player', None)
                    red_player = getattr(match, 'red_player', None)
                    
                    match_info = {
                        'match_id': getattr(match, 'match_id', match_id),
                        'round_number': getattr(match, 'round_number', 1),
                        'match_number': getattr(match, 'match_number', 0),
                        'blue_player': get_player_info(blue_player),
                        'red_player': get_player_info(red_player),
                        'winner': getattr(match, 'winner', None),
                        'completed': getattr(match, 'completed', False),
                        'category': getattr(match, 'category', '')
                    }
                    self.tournament_data['matches'].append(match_info)
            
            # Afficher une notification de succès
            self.show_notification(f"Tournoi '{tournament.name}' chargé avec succès", "success")
            
            # Vérifier s'il y a des matchs non terminés
            has_unfinished_matches = any(
                not match.get('completed', False) 
                for match in self.tournament_data['matches']
            )
            
            # Si des matchs sont disponibles, charger le prochain match non terminé
            if has_unfinished_matches:
                self.load_next_match()
            else:
                # Si tous les matchs sont terminés, demander si l'utilisateur veut voir les résultats
                if messagebox.askyesno(
                    "Tournoi terminé", 
                    "Tous les matchs de ce tournoi sont terminés. Voulez-vous voir les résultats?"
                ):
                    self.show_tournament_display()
        
        except Exception as e:
            # En cas d'erreur, afficher un message d'erreur détaillé
            error_msg = f"Erreur lors du chargement du tournoi: {str(e)}"
            print(error_msg)  # Pour le débogage
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erreur", error_msg)
    
    def import_players(self):
        """Importe des joueurs depuis un fichier"""
        if not self.tournament_manager.tournament:
            messagebox.showerror("Erreur", "Veuillez d'abord créer ou charger un tournoi")
            return
        
        from import_manager import ImportDialog
        dialog = ImportDialog(self.root, self.handle_imported_players)
        self.root.wait_window(dialog)
    
    def handle_imported_players(self, players_data):
        """Traite les données des joueurs importés"""
        if not players_data:
            return
            
        count = 0
        for data in players_data:
            from tournament_manager import Player
            player = Player(
                id=data['id'],
                name=data['name'],
                club=data['club'],
                country=data['country'],
                category=data['category'],
                weight=data.get('weight', ''),
                age=data.get('age', '')
            )
            self.tournament_manager.tournament.add_player(player)
            count += 1
        self.show_notification(f"{count} joueurs importés avec succès", "success")
    
    def generate_matches(self):
        """Génère les matchs pour le tournoi"""
        if not self.tournament_manager.tournament:
            messagebox.showerror("Erreur", "Veuillez d'abord créer ou charger un tournoi")
            return
            
        # Récupérer toutes les catégories disponibles
        categories = list(self.tournament_manager.tournament.categories.keys())
        if not categories:
            messagebox.showerror("Erreur", "Aucune catégorie disponible")
            return
        
        # Créer une boîte de dialogue pour sélectionner les catégories
        dialog = tk.Toplevel(self.root)
        dialog.title("Générer des matchs par catégorie")
        dialog.geometry("500x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Sélectionnez les catégories pour générer des matchs:", 
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        # Frame principale avec scrollbar
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Créer un canvas avec scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Variables pour stocker les sélections
        category_vars = {}
        order_entries = {}
        
        # Créer un cadre pour l'ordre de passage
        order_frame = ttk.LabelFrame(scrollable_frame, text="Ordre de passage des catégories")
        order_frame.pack(fill="x", padx=5, pady=10)
        
        ttk.Label(order_frame, text="Définissez l'ordre de passage (1, 2, 3, etc.)", 
                 font=("Arial", 10)).pack(pady=5)
        
        # Créer des checkboxes pour chaque catégorie avec champ d'ordre
        for i, category in enumerate(categories):
            category_frame = ttk.Frame(scrollable_frame)
            category_frame.pack(fill="x", padx=5, pady=2)
            
            # Variable pour la checkbox
            var = tk.BooleanVar(value=True)  # Par défaut, toutes les catégories sont sélectionnées
            category_vars[category] = var
            
            # Checkbox pour la catégorie
            cb = ttk.Checkbutton(category_frame, text=category, variable=var)
            cb.pack(side=tk.LEFT, padx=5)
            
            # Champ pour l'ordre de passage
            ttk.Label(category_frame, text="Ordre:").pack(side=tk.LEFT, padx=5)
            order_var = ttk.Entry(category_frame, width=5)
            order_var.insert(0, str(i+1))  # Ordre par défaut
            order_var.pack(side=tk.LEFT, padx=5)
            order_entries[category] = order_var
            
            # Nombre de joueurs dans cette catégorie (en excluant les doublons)
            players_in_category = self.tournament_manager.tournament.categories.get(category, [])
            unique_players = []
            seen_names = set()
            for player_id in players_in_category:
                player = self.tournament_manager.tournament.players[player_id]
                if player.name not in seen_names:
                    unique_players.append(player)
                    seen_names.add(player.name)
            player_count = len(unique_players)
            ttk.Label(category_frame, text=f"({player_count} joueurs uniques)").pack(side=tk.LEFT, padx=5)
        
        # Boutons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        def on_generate():
            # Récupérer les catégories sélectionnées avec leur ordre
            selected_categories = []
            for category, var in category_vars.items():
                if var.get():
                    try:
                        order = int(order_entries[category].get())
                        selected_categories.append((category, order))
                    except ValueError:
                        messagebox.showerror("Erreur", f"Ordre invalide pour la catégorie {category}")
                        return
            
            if not selected_categories:
                messagebox.showerror("Erreur", "Veuillez sélectionner au moins une catégorie")
                return
            
            # Trier les catégories par ordre
            selected_categories.sort(key=lambda x: x[1])
            
            # Sauvegarder l'ordre des catégories dans le tournament manager
            category_order = {}
            for category, order in selected_categories:
                category_order[category] = order
            self.tournament_manager.set_category_order(category_order)
            
            # Générer les matchs pour chaque catégorie sélectionnée
            total_matches = 0
            results = []
            for category, order in selected_categories:
                # Utiliser generate_first_round au lieu de generate_next_round pour le premier tour
                matches = self.tournament_manager.tournament.generate_first_round(category)
                if matches:
                    total_matches += len(matches)
                    player_count = len(self.tournament_manager.tournament.categories.get(category, []))
                    results.append(f"{len(matches)} matchs générés pour {category} ({player_count} joueurs, ordre: {order})")
                else:
                    player_count = len(self.tournament_manager.tournament.categories.get(category, []))
                    results.append(f"Aucun match généré pour {category} ({player_count} joueurs)")
            
            if total_matches > 0:
                # Sauvegarder le tournoi après génération
                self.tournament_manager.save_tournament()
                # Afficher un résumé détaillé
                result_text = "\n".join(results)
                messagebox.showinfo("Génération réussie", 
                                   f"Total: {total_matches} matchs générés\n\n{result_text}")
                dialog.destroy()
            else:
                result_text = "\n".join(results)
                messagebox.showwarning("Attention", f"Aucun match généré\n\n{result_text}\n\nVérifiez qu'il y a au moins 2 joueurs différents par catégorie.")
        
        ttk.Button(btn_frame, text="Générer les matchs", command=on_generate).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Annuler", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def setup_match_interface(self):
        """Configure l'interface pour le match en cours"""
        # Initialiser l'interface de match si ce n'est pas déjà fait
        self.match_configured = True
        # Ajoutez ici toute autre initialisation nécessaire pour l'interface de match

    def load_next_match(self):
        """Charge le prochain match du tournoi"""
        if not hasattr(self, 'tournament_manager') or not self.tournament_manager.tournament:
            messagebox.showerror("Erreur", "Veuillez d'abord créer ou charger un tournoi")
            return
            
        # Récupérer le prochain match non terminé
        next_match = self.tournament_manager.get_next_match()
        if not next_match:
            messagebox.showinfo("Information", "Tous les matchs sont terminés ou aucun match n'est disponible")
            return
            
        # Stocker le match en cours
        self.current_match = next_match
        self.current_match_id = next_match.match_id
        
        # Fonction pour obtenir le nom d'un joueur en toute sécurité
        def get_player_name(player):
            if player is None:
                return 'Bye'
            if hasattr(player, 'name'):
                return player.name
            if hasattr(player, 'to_dict'):
                player_data = player.to_dict()
                return player_data.get('name', str(player))
            return str(player)
        
        # Mettre à jour les informations des joueurs
        blue_player = getattr(next_match, 'blue_player', None)
        red_player = getattr(next_match, 'red_player', None)
        
        # Mettre à jour l'interface avec les informations du match
        if hasattr(self, 'blue_name_label'):
            self.blue_name_label.config(text=get_player_name(blue_player))
            self.red_name_label.config(text=get_player_name(red_player))
            
            # Mettre à jour les drapeaux si les joueurs ont un pays
            if hasattr(self, 'flag_dict'):
                self.blue_flag = self.flag_dict.get(getattr(blue_player, 'country', ''), "🏳️")
                self.red_flag = self.flag_dict.get(getattr(red_player, 'country', ''), "🏳️")
                
                if hasattr(self, 'blue_flag_label'):
                    self.blue_flag_label.config(text=self.blue_flag)
                    self.red_flag_label.config(text=self.red_flag)
        
        # Mettre à jour les informations supplémentaires du match
        self.blue_name = get_player_name(blue_player)
        self.red_name = get_player_name(red_player)
        self.blue_club = getattr(blue_player, 'club', '')
        self.red_club = getattr(red_player, 'club', '')
        self.blue_country = getattr(blue_player, 'country', '')
        self.red_country = getattr(red_player, 'country', '')
        self.match_number = str(getattr(next_match, 'match_number', ''))
        self.category = getattr(next_match, 'category', '')
            
        # Réinitialiser les scores et le chronomètre
        self.blue_score = 0
        self.red_score = 0
        self.blue_gam_jeom = 0
        self.red_gam_jeom = 0
        self.current_time = 180  # 3 minutes en secondes
        self.round_number = 1
        self.round_winners = []
        self.final_winner = None
        self.is_running = False
        self.is_paused = False
        
        # Mettre à jour l'affichage
        self.update_display()
        
        # Si l'interface de match n'est pas encore configurée, l'afficher
        if not hasattr(self, 'match_configured') or not self.match_configured:
            self.setup_match_interface()
            
        # Afficher un message de confirmation
        messagebox.showinfo("Match chargé", f"Match {self.match_number} chargé: {self.blue_name} vs {self.red_name}")
        
        # Si la fenêtre de configuration du match n'est pas déjà affichée, l'afficher
        if not hasattr(self, 'match_config_dialog') or not hasattr(self.match_config_dialog, 'winfo_exists') or not self.match_config_dialog.winfo_exists():
            from match_config_dialog import MatchConfigDialog
            self.match_config_dialog = MatchConfigDialog(self.root, self)
            self.match_config_dialog.grab_set()
            
        # Afficher une notification
        self.show_notification(f"Match {self.match_number} chargé", "success")
    

    
    def show_tournament_display(self):
        """Affiche le tournoi avec le nouveau système d'affichage"""
        if not self.tournament_manager.tournament:
            messagebox.showerror("Erreur", "Veuillez d'abord créer ou charger un tournoi")
            return
            
        # Préparer les données du tournoi pour l'affichage
        tournament_data = {
            'name': self.tournament_manager.tournament.name,
            'category': self.tournament_manager.tournament.category,
            'players': [],
            'matches': []
        }
        
        # Convertir les joueurs
        for player in self.tournament_manager.tournament.players.values():
            tournament_data['players'].append({
                'id': player.id,
                'name': player.name,
                'club': player.club,
                'country': player.country,
                'category': player.category,
                'weight': player.weight,
                'age': player.age
            })
        
        # Convertir les matchs
        for match in self.tournament_manager.tournament.matches.values():
            tournament_data['matches'].append({
                'match_id': match.match_id,
                'round_number': match.round_number,
                'match_number': match.match_number,
                'category': match.category,
                'blue_player': {
                    'id': match.blue_player.id,
                    'name': match.blue_player.name,
                    'club': match.blue_player.club,
                    'country': match.blue_player.country,
                    'category': match.blue_player.category
                } if match.blue_player else None,
                'red_player': {
                    'id': match.red_player.id,
                    'name': match.red_player.name,
                    'club': match.red_player.club,
                    'country': match.red_player.country,
                    'category': match.red_player.category
                } if match.red_player else None,
                'winner': match.winner,
                'completed': match.completed
            })
        
        # Afficher le tournoi
        self.tournament_display.create_tournament_window(tournament_data)
    
    def save_match_result(self):
        """Sauvegarde le résultat du match en cours"""
        if not hasattr(self, 'current_match_id') or not self.current_match_id:
            return
            
        # Déterminer le vainqueur final
        if not self.final_winner and self.round_winners:
            blue_wins = self.round_winners.count("blue")
            red_wins = self.round_winners.count("red")
            if blue_wins > red_wins:
                self.final_winner = "blue"
            elif red_wins > blue_wins:
                self.final_winner = "red"
        
        if not self.final_winner:
            messagebox.showerror("Erreur", "Impossible de déterminer le vainqueur")
            return
            
        # Mettre à jour le résultat du match
        self.tournament_manager.update_match_result(
            match_id=self.current_match_id,
            blue_score=self.blue_score,
            red_score=self.red_score,
            blue_gam_jeom=self.blue_gam_jeom,
            red_gam_jeom=self.red_gam_jeom,
            winner=self.final_winner,
            round_winners=self.round_winners
        )
        
        # Sauvegarder le tournoi
        self.tournament_manager.save_tournament()
        
        # Calculer les statistiques du tournoi
        if self.tournament_manager.tournament:
            total_matches = len(self.tournament_manager.tournament.matches)
            completed_matches = sum(1 for m in self.tournament_manager.tournament.matches.values() if m.completed)
            remaining_matches = total_matches - completed_matches
            
            # Afficher les statistiques
            stats_message = f"Match {self.current_match_id} terminé\n"
            stats_message += f"Progression: {completed_matches}/{total_matches} matchs terminés\n"
            
            if remaining_matches > 0:
                stats_message += f"Il reste {remaining_matches} matchs à disputer"
                self.show_notification(stats_message, "success")
                # Afficher une notification moderne pour passer au match suivant
                self.show_next_match_notification()
            else:
                stats_message += "Tous les matchs sont terminés!"
                self.show_notification(stats_message, "success")
                # Afficher la finale du championnat
                self.show_championship_final()
        else:
            self.show_notification("Résultat du match sauvegardé", "success")
            # Afficher une notification moderne pour passer au match suivant
            self.show_next_match_notification()
    
    def show_next_match_notification(self):
        """Affiche une notification moderne en bas à droite pour passer au match suivant"""    
        # Créer une fenêtre de notification
        notification = tk.Toplevel(self.root)
        notification.title("")
        notification.geometry("350x150")
        notification.resizable(False, False)
        notification.overrideredirect(True)  # Supprimer la barre de titre
        
        # Positionner en bas à droite de l'écran
        screen_width = notification.winfo_screenwidth()
        screen_height = notification.winfo_screenheight()
        x = screen_width - 370
        y = screen_height - 200
        notification.geometry(f"350x150+{x}+{y}")
        
        # Style moderne avec dégradé bleu-rouge
        notification.configure(bg="#2c3e50")
        
        # Frame principal avec bordure arrondie simulée
        main_frame = tk.Frame(notification, bg="#2c3e50", padx=20, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre avec icône
        title_frame = tk.Frame(main_frame, bg="#2c3e50")
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(title_frame, text="🥋 Match Terminé!", 
                              font=("Arial", 14, "bold"), 
                              fg="#ecf0f1", bg="#2c3e50")
        title_label.pack()
        
        # Message
        message_label = tk.Label(main_frame, 
                                text="Voulez-vous passer au match suivant?",
                                font=("Arial", 11), 
                                fg="#bdc3c7", bg="#2c3e50",
                                wraplength=300)
        message_label.pack(pady=(0, 15))
        
        # Frame pour les boutons
        button_frame = tk.Frame(main_frame, bg="#2c3e50")
        button_frame.pack(fill=tk.X)
        
        # Bouton Oui (style bleu)
        yes_btn = tk.Button(button_frame, text="OUI",
                           font=("Arial", 10, "bold"),
                           bg="#3498db", fg="white", 
                           activebackground="#2980b9", activeforeground="white",
                           relief=tk.FLAT, padx=20, pady=8,
                           cursor="hand2",
                           command=lambda: self.on_next_match_yes(notification))
        yes_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Bouton Non (style rouge)
        no_btn = tk.Button(button_frame, text="NON",
                          font=("Arial", 10, "bold"),
                          bg="#e74c3c", fg="white", 
                          activebackground="#c0392b", activeforeground="white",
                          relief=tk.FLAT, padx=20, pady=8,
                          cursor="hand2",
                          command=lambda: notification.destroy())
        no_btn.pack(side=tk.LEFT)
        
        # Effet d'apparition
        notification.attributes("-alpha", 0.0)
        notification.lift()
        notification.focus_force()
        
        # Animation d'apparition
        def fade_in(alpha=0.0):
            alpha += 0.1
            notification.attributes("-alpha", alpha)
            if alpha < 1.0:
                notification.after(30, lambda: fade_in(alpha))
        
        fade_in()
        # Auto-fermeture après 10 secondes
        notification.after(10000, notification.destroy)
    
    def update_button_states(self):
        """Active/désactive les boutons principaux selon l'état du match"""
        if not hasattr(self, 'main_buttons'):
            return
            
        # Si le match a un vainqueur final (terminé), désactiver tous les boutons
        if self.final_winner is not None:
            for button in self.main_buttons.values():
                button.config(state="disabled")
            return

        # États: running, paused, break_time
        if self.is_running and not self.is_paused:
            # Match en cours: désactiver Start, activer Pause et End, désactiver Next
            self.main_buttons["Start Round"].config(state="disabled")
            self.main_buttons["Pause"].config(state="normal")
            self.main_buttons["End Round"].config(state="normal")
            self.main_buttons["Next Round"].config(state="disabled")
        elif self.is_paused:
            # Match en pause: activer Start (reprendre), désactiver Pause, activer End, désactiver Next
            self.main_buttons["Start Round"].config(state="normal")
            self.main_buttons["Pause"].config(state="disabled")
            self.main_buttons["End Round"].config(state="normal")
            self.main_buttons["Next Round"].config(state="disabled")
        elif self.is_break_time:
            # Temps de repos: désactiver Start, désactiver Pause, désactiver End, activer Next
            self.main_buttons["Start Round"].config(state="disabled")
            self.main_buttons["Pause"].config(state="disabled")
            self.main_buttons["End Round"].config(state="disabled")
            self.main_buttons["Next Round"].config(state="normal")
        else:
            # État prêt: activer Start, désactiver Pause, désactiver End, désactiver Next
            self.main_buttons["Start Round"].config(state="normal")
            self.main_buttons["Pause"].config(state="disabled")
            self.main_buttons["End Round"].config(state="disabled")
            self.main_buttons["Next Round"].config(state="disabled")

    def show_championship_final(self):
        """Affiche la finale du championnat de manière spectaculaire"""
        if not self.tournament_manager.tournament:
            return
            
        # Récupérer les vainqueurs de chaque catégorie
        winners = []
        categories = set()
        
        for match in self.tournament_manager.tournament.matches.values():
            if match.completed and match.winner:
                categories.add(match.category)
        
        # Pour chaque catégorie, trouver le vainqueur
        for category in categories:
            category_matches = [m for m in self.tournament_manager.tournament.matches.values() 
                              if m.category == category and m.completed and m.winner]
            
            if category_matches:
                # Prendre le dernier match de la catégorie (finale)
                final_match = max(category_matches, key=lambda m: m.round_number)
                winner_player = final_match.blue_player if final_match.winner == 'blue' else final_match.red_player
                winners.append({
                    'name': winner_player.name,
                    'club': winner_player.club,
                    'country': winner_player.country,
                    'category': category
                })
        
        if winners:
            # Afficher la finale du championnat
            self.tournament_display.show_championship_final(winners)
        else:
            messagebox.showinfo("Championnat", "Aucun vainqueur de catégorie trouvé pour la finale du championnat.")
    
    def on_next_match_yes(self, notification):
        """Gère le clic sur OUI pour passer au match suivant"""
        notification.destroy()
        
        # Réinitialiser l'interface
        self.blue_score = 0
        self.red_score = 0
        self.blue_gam_jeom = 0
        self.red_gam_jeom = 0
        self.round_number = 1
        self.round_winners = []
        self.final_winner = None
        
        # Afficher l'interface de configuration du match suivant
        self.show_configuration_dialog()
    pass
