import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import os
from PIL import Image, ImageTk

class TournamentDisplay:
    """Gestionnaire d'affichage du tournoi avec graphiques et couleurs de tenues"""
    
    def __init__(self, parent):
        self.parent = parent
        self.tournament_data = {}
        self.current_round = 1
        self.max_rounds = 0
        self.logo_path = "logo_eveil.png"
        self.setup_colors()
        
    def setup_colors(self):
        """Configuration des couleurs pour les tenues"""
        self.tenue_colors = {
            'blue': {
                'primary': '#1565C0',
                'secondary': '#0D47A1',
                'text': 'white'
            },
            'red': {
                'primary': '#C62828',
                'secondary': '#B71C1C',
                'text': 'white'
            },
            'ui': {
                'background': '#2C2C3A',
                'text': '#ECF0F1',
                'line': '#566573',
                'highlight': '#F1C40F',
                'match_bg': '#3C3C4A',
                'match_highlight': '#4C4C5A'
            }
        }
        
    def create_tournament_window(self, tournament_data: Dict[str, Any]):
        """Crée la fenêtre principale d'affichage du tournoi"""
        self.tournament_data = tournament_data
        self.max_rounds = self.calculate_max_rounds(len(tournament_data.get('players', [])))
        
        # Créer la fenêtre
        self.tournament_window = tk.Toplevel(self.parent)
        self.tournament_window.title("🏆 Tournoi Taekwondo - Affichage des Matchs")
        self.tournament_window.geometry("1400x900")
        self.tournament_window.configure(bg=self.tenue_colors['ui']['background'])
        
        # Centrer la fenêtre
        self.center_window(self.tournament_window)
        
        # Ajouter l'icône du logo
        self.set_window_icon()
        
        # Créer l'interface
        self.create_tournament_interface()
        
        # Générer le graphique initial
        self.generate_tournament_bracket()
        
    def set_window_icon(self):
        """Définit l'icône de la fenêtre avec le logo"""
        try:
            if os.path.exists(self.logo_path):
                # Convertir l'image PNG en format compatible avec tkinter
                from PIL import Image, ImageTk
                img = Image.open(self.logo_path)
                # Redimensionner si nécessaire
                img = img.resize((32, 32), Image.Resampling.LANCZOS)
                icon = ImageTk.PhotoImage(img)
                self.tournament_window.iconphoto(True, icon)
        except Exception as e:
            print(f"Erreur lors du chargement de l'icône: {e}")
    
    def center_window(self, window):
        """Centre une fenêtre sur l'écran"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'+{x}+{y}')
    
    def create_tournament_interface(self):
        """Crée l'interface principale du tournoi"""
        # Frame principal
        main_frame = ttk.Frame(self.tournament_window)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # En-tête avec logo
        self.create_header(main_frame)
        
        # Frame pour les contrôles
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill='x', pady=(20, 10))
        
        # Boutons de contrôle
        self.create_control_buttons(controls_frame)
        
        # Frame pour le graphique
        self.graph_frame = ttk.Frame(main_frame)
        self.graph_frame.pack(fill='both', expand=True, pady=10)
        
        # Informations du match actuel
        self.create_current_match_info(main_frame)
    
    def create_header(self, parent):
        """Crée l'en-tête avec le logo et le titre"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Logo
        try:
            if os.path.exists(self.logo_path):
                logo_img = Image.open(self.logo_path)
                logo_img = logo_img.resize((60, 60), Image.Resampling.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)
                
                logo_label = ttk.Label(header_frame, image=logo_photo)
                logo_label.image = logo_photo
                logo_label.pack(side='left', padx=(0, 15))
        except Exception as e:
            print(f"Erreur lors du chargement du logo: {e}")
        
        # Titre
        title_label = ttk.Label(
            header_frame, 
            text="🏆 TOURNOI TAEKWONDO", 
            font=('Arial', 24, 'bold'),
            foreground=self.tenue_colors['ui']['text']
        )
        title_label.pack(side='left')
        
        # Informations du tournoi
        info_frame = ttk.Frame(header_frame)
        info_frame.pack(side='right')
        
        tournament_name = self.tournament_data.get('name', 'Tournoi')
        category = self.tournament_data.get('category', 'Toutes catégories')
        
        ttk.Label(info_frame, text=f"Tournoi: {tournament_name}", font=('Arial', 12)).pack(anchor='e')
        ttk.Label(info_frame, text=f"Catégorie: {category}", font=('Arial', 12)).pack(anchor='e')
    
    def create_control_buttons(self, parent):
        """Crée les boutons de contrôle"""
        # Frame pour les boutons
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill='x')
        
        # Bouton précédent
        self.prev_btn = ttk.Button(
            buttons_frame,
            text="◀ Match Précédent",
            command=self.previous_match,
            style='Accent.TButton'
        )
        self.prev_btn.pack(side='left', padx=(0, 10))
        
        # Bouton suivant
        self.next_btn = ttk.Button(
            buttons_frame,
            text="Match Suivant ▶",
            command=self.next_match,
            style='Accent.TButton'
        )
        self.next_btn.pack(side='left', padx=(0, 10))
        
        # Bouton imprimer
        self.print_btn = ttk.Button(
            buttons_frame,
            text="🖨️ Imprimer le Graphique",
            command=self.print_tournament_bracket
        )
        self.print_btn.pack(side='left', padx=(0, 10))
        
        # Bouton fermer
        self.close_btn = ttk.Button(
            buttons_frame,
            text="❌ Fermer",
            command=self.tournament_window.destroy
        )
        self.close_btn.pack(side='right')
        
        # Informations du round actuel
        self.round_info_label = ttk.Label(
            buttons_frame,
            text=f"Round {self.current_round} / {self.max_rounds}",
            font=('Arial', 12, 'bold'),
            foreground=self.tenue_colors['ui']['text']
        )
        self.round_info_label.pack(side='right', padx=(0, 20))
    
    def create_current_match_info(self, parent):
        """Crée l'affichage des informations du match actuel"""
        match_frame = ttk.LabelFrame(parent, text="🥊 Match Actuel", padding=15)
        match_frame.pack(fill='x', pady=(20, 0))
        
        # Frame pour les combattants
        fighters_frame = ttk.Frame(match_frame)
        fighters_frame.pack(fill='x')
        
        # Combattant bleu
        self.blue_frame = ttk.Frame(fighters_frame)
        self.blue_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        self.blue_name_label = ttk.Label(
            self.blue_frame,
            text="Combattant Bleu",
            font=('Arial', 14, 'bold'),
            foreground='white',
            background=self.tenue_colors['blue']['primary'],
            padding=(10, 5)
        )
        self.blue_name_label.pack(fill='x')
        
        self.blue_info_label = ttk.Label(
            self.blue_frame,
            text="Club - Pays",
            font=('Arial', 10),
            foreground=self.tenue_colors['blue']['primary']
        )
        self.blue_info_label.pack()
        
        # VS
        vs_label = ttk.Label(
            fighters_frame,
            text="VS",
            font=('Arial', 20, 'bold'),
            foreground=self.tenue_colors['ui']['text']
        )
        vs_label.pack(side='left', padx=20)
        
        # Combattant rouge
        self.red_frame = ttk.Frame(fighters_frame)
        self.red_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        self.red_name_label = ttk.Label(
            self.red_frame,
            text="Combattant Rouge",
            font=('Arial', 14, 'bold'),
            foreground='white',
            background=self.tenue_colors['red']['primary'],
            padding=(10, 5)
        )
        self.red_name_label.pack(fill='x')
        
        self.red_info_label = ttk.Label(
            self.red_frame,
            text="Club - Pays",
            font=('Arial', 10),
            foreground=self.tenue_colors['red']['primary']
        )
        self.red_info_label.pack()
    
    def calculate_max_rounds(self, player_count: int) -> int:
        """Calcule le nombre maximum de rounds basé sur le nombre de joueurs"""
        if player_count <= 1:
            return 1
        return (player_count - 1).bit_length()
    
    def generate_tournament_bracket(self):
        """Génère le graphique du tournoi en forme de pyramide moderne"""
        # Nettoyer le frame du graphique
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        
        # Créer la figure matplotlib avec un design moderne
        fig, ax = plt.subplots(figsize=(14, 10))
        ui_colors = self.tenue_colors['ui']
        fig.patch.set_facecolor(ui_colors['background'])
        ax.set_facecolor(ui_colors['background'])
        
        # Obtenir les données du tournoi
        matches = self.tournament_data.get('matches', [])
        players = self.tournament_data.get('players', [])
        self.current_round = self.tournament_data.get('current_round', 1)
        
        if not matches:
            self.create_empty_bracket(ax, players)
        else:
            self.create_match_bracket(ax, matches, players, self.current_round)
        
        # Configuration de l'apparence
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        ax.set_title('Pyramide du Tournoi', color=ui_colors['text'], fontsize=16, pad=20)
        
        # Créer le canvas avec une apparence moderne
        canvas = FigureCanvasTkAgg(fig, self.graph_frame)
        canvas.draw()
        
        # Ajouter le canvas à l'interface
        canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Mettre à jour les informations du match actuel
        self.update_current_match_info()
    
    def create_match_bracket(self, ax, matches, players, current_round):
        """Crée la structure pyramidale des matchs avec un design moderne"""
        # Organiser les matchs par round
        rounds = {}
        for match in matches:
            round_num = match.get('round', 1)
            if round_num not in rounds:
                rounds[round_num] = []
            rounds[round_num].append(match)
        
        # Déterminer le nombre total de rounds
        total_rounds = max(rounds.keys()) if rounds else 0
        
        # Utiliser les couleurs de l'interface utilisateur
        ui_colors = self.tenue_colors['ui']
        
        # Paramètres de la pyramide
        base_y = 8.5
        round_height = 1.5
        match_width = 1.2
        
        # Dessiner la pyramide de tournoi
        for round_num in range(1, total_rounds + 1):
            round_matches = rounds.get(round_num, [])
            y_pos = base_y - (round_num - 1) * round_height
            
            # Calculer la position horizontale pour centrer les matchs
            num_matches = len(round_matches)
            total_width = num_matches * match_width
            start_x = (10 - total_width) / 2
            
            for i, match in enumerate(round_matches):
                x_pos = start_x + i * match_width + match_width / 2
                
                # Déterminer si c'est le round actuel
                is_current = round_num == current_round
                
                # Dessiner les connexions avec les rounds précédents
                if round_num > 1:
                    parent_x1 = start_x + (i * 2) * (match_width / 2) + (match_width / 4)
                    parent_x2 = start_x + (i * 2 + 1) * (match_width / 2) + (match_width / 4)
                    parent_y = base_y - (round_num - 2) * round_height
                    
                    # Lignes de connexion
                    ax.plot([parent_x1, x_pos], [parent_y, y_pos], 
                            color=ui_colors['line'], linewidth=1, alpha=0.7)
                    ax.plot([parent_x2, x_pos], [parent_y, y_pos], 
                            color=ui_colors['line'], linewidth=1, alpha=0.7)
                
                # Dessiner le match
                self.draw_match(ax, match, x_pos, y_pos, is_current)
        
        # Ajouter le trophée pour le gagnant final
        if total_rounds > 0:
            winner = self.determine_winner(matches, players)
            if winner:
                ax.text(5, 0.5, f"🏆 {winner}", ha='center', va='center', 
                       fontsize=14, color=ui_colors['highlight'], 
                       bbox=dict(facecolor=ui_colors['background'], alpha=0.8, 
                               edgecolor=ui_colors['highlight'], boxstyle='round,pad=0.5'))
    
    def draw_match(self, ax, match, x, y, is_current=False):
        """Dessine un match individuel avec style moderne"""
        ui_colors = self.tenue_colors['ui']
        
        # Couleurs de fond pour le match
        bg_color = ui_colors['match_highlight'] if is_current else ui_colors['match_bg']
        border_color = ui_colors['highlight'] if is_current else ui_colors['line']
        
        # Rectangle de fond pour le match
        rect = plt.Rectangle((x-0.6, y-0.25), 1.2, 0.5, fill=True, 
                            facecolor=bg_color,
                            edgecolor=border_color,
                            alpha=0.9 if is_current else 0.8,
                            linewidth=2 if is_current else 1,
                            zorder=5 if is_current else 4,
                            boxstyle='round,pad=0.1')
        ax.add_patch(rect)
        
        # Récupérer les informations des joueurs
        player1 = match.get('player1', {}) if isinstance(match.get('player1'), dict) else {'name': str(match.get('player1', 'Joueur 1'))}
        player2 = match.get('player2', {}) if isinstance(match.get('player2'), dict) else {'name': str(match.get('player2', 'Joueur 2'))}
        
        # Couleurs des joueurs
        blue_colors = self.tenue_colors['blue']
        red_colors = self.tenue_colors['red']
        
        # Déterminer le gagnant
        winner = match.get('winner')
        p1_style = 'bold' if winner == 'blue' else 'normal'
        p2_style = 'bold' if winner == 'red' else 'normal'
        
        # Afficher les noms des joueurs avec leurs couleurs
        ax.text(x, y + 0.1, player1.get('name', 'Joueur 1'), 
               ha='center', va='center',
               color=blue_colors['text'], 
               fontsize=9, 
               weight=p1_style,
               bbox=dict(facecolor=blue_colors['primary'], 
                        alpha=0.8, 
                        edgecolor=blue_colors['secondary'],
                        boxstyle='round,pad=0.1'))
        
        ax.text(x, y - 0.1, player2.get('name', 'Joueur 2'), 
               ha='center', va='center',
               color=red_colors['text'], 
               fontsize=9, 
               weight=p2_style,
               bbox=dict(facecolor=red_colors['primary'], 
                        alpha=0.8, 
                        edgecolor=red_colors['secondary'],
                        boxstyle='round,pad=0.1'))
        
        # Afficher le score si disponible
        if 'score' in match:
            score_text = match['score']
            if isinstance(score_text, (list, tuple)) and len(score_text) >= 2:
                score_text = f"{score_text[0]} - {score_text[1]}"
            ax.text(x, y, str(score_text), 
                   ha='center', va='center',
                   color=ui_colors['text'], 
                   fontsize=10, 
                   weight='bold',
                   bbox=dict(facecolor=ui_colors['background'], 
                            alpha=0.9, 
                            edgecolor=ui_colors['highlight'],
                            boxstyle='round,pad=0.1'))
    
    def create_empty_bracket(self, ax, players):
        """Crée un bracket vide avec les joueurs"""
        ui_colors = self.tenue_colors['ui']
        
        # Afficher un message
        ax.text(5, 7, "Le tournoi n'a pas encore commencé", 
               ha='center', va='center', 
               fontsize=16, 
               color=ui_colors['highlight'],
               bbox=dict(facecolor=ui_colors['background'], 
                        alpha=0.9, 
                        edgecolor=ui_colors['highlight'],
                        boxstyle='round,pad=0.5'))
        
        # Afficher la liste des participants
        if players:
            # Organiser les joueurs en deux colonnes
            half = (len(players) + 1) // 2
            col1 = players[:half]
            col2 = players[half:]
            
            # Afficher le titre des participants
            ax.text(3, 5.5, "Participants:", 
                   ha='left', va='center', 
                   fontsize=14, 
                   color=ui_colors['highlight'],
                   weight='bold')
            
            # Afficher la première colonne de participants
            for i, player in enumerate(col1, 1):
                player_name = player.get('name', str(player)) if isinstance(player, dict) else str(player)
                ax.text(3, 5 - i*0.4, f"• {player_name}", 
                       ha='left', va='center', 
                       fontsize=11, 
                       color=ui_colors['text'])
            
            # Afficher la deuxième colonne de participants si nécessaire
            if col2:
                for i, player in enumerate(col2, 1):
                    player_name = player.get('name', str(player)) if isinstance(player, dict) else str(player)
                    ax.text(6, 5 - i*0.4, f"• {player_name}", 
                           ha='left', va='center', 
                           fontsize=11, 
                           color=ui_colors['text'])
    
    def determine_winner(self, matches, players):
        """Détermine le gagnant final du tournoi"""
        if not matches:
            return None
            
        # Trouver le dernier round
        last_round = max(match.get('round', 0) for match in matches)
        last_matches = [m for m in matches if m.get('round') == last_round]
        
        # Vérifier s'il y a un gagnant dans le dernier match
        for match in last_matches:
            winner = match.get('winner')
            if winner:
                # Si le gagnant est une référence à un joueur
                if isinstance(winner, dict):
                    return winner.get('name', 'Vainqueur inconnu')
                # Si le gagnant est identifié par une couleur
                elif winner in ['blue', 'red']:
                    player_data = match.get(f'{winner}_player', {})
                    if isinstance(player_data, dict):
                        return player_data.get('name', f'Joueur {winner.capitalize()}')
                    return str(player_data)
                # Si le gagnant est directement le nom
                else:
                    return str(winner)
        
        return None
    
    def update_current_match_info(self):
        """Met à jour les informations du match actuel"""
        if not hasattr(self, 'blue_info_label') or not hasattr(self, 'red_info_label'):
            return
            
        matches = self.tournament_data.get('matches', [])
        current_matches = [m for m in matches if m.get('round') == self.current_round]
        
        if not current_matches:
            self.blue_info_label.config(text="Aucun match en cours")
            self.red_info_label.config(text="")
            return
        
        # Prendre le premier match du round actuel
        current_match = current_matches[0]
        
        # Mettre à jour les informations des joueurs
        blue_player = current_match.get('blue_player', {})
        red_player = current_match.get('red_player', {})
        
        blue_name = blue_player.get('name', 'Joueur Bleu') if isinstance(blue_player, dict) else str(blue_player)
        red_name = red_player.get('name', 'Joueur Rouge') if isinstance(red_player, dict) else str(red_player)
        
        blue_club = f"\n{blue_player.get('club', '')}" if isinstance(blue_player, dict) and 'club' in blue_player else ""
        red_club = f"\n{red_player.get('club', '')}" if isinstance(red_player, dict) and 'club' in red_player else ""
        
        # Mettre à jour les labels
        self.blue_info_label.config(
            text=f"🔵 {blue_name}{blue_club}",
            foreground=self.tenue_colors['blue']['primary']
        )
        
        self.red_info_label.config(
            text=f"🔴 {red_name}{red_club}",
            foreground=self.tenue_colors['red']['primary']
        )
        
        # Mettre à jour le score si disponible
        if 'score' in current_match:
            score = current_match['score']
            if isinstance(score, (list, tuple)) and len(score) >= 2:
                score_text = f"{score[0]} - {score[1]}"
        if winner:
            # Si le gagnant est une référence à un joueur
            if isinstance(winner, dict):
                return winner.get('name', 'Vainqueur inconnu')
            # Si le gagnant est identifié par une couleur
            elif winner in ['blue', 'red']:
                player_data = match.get(f'{winner}_player', {})
                if isinstance(player_data, dict):
                    return player_data.get('name', f'Joueur {winner.capitalize()}')
                return str(player_data)
            # Si le gagnant est directement le nom
        for i in range(0, len(players), 2):
            if i + 1 < len(players):
                player_pairs.append((players[i], players[i+1]))
            else:
                player_pairs.append((players[i], None))
        
        # Position de départ
        y_start = 8
        y_spacing = 1.5
        
        for i, (player1, player2) in enumerate(player_pairs):
            y_pos = y_start - (i * y_spacing)
            
            # Combattant bleu (gauche)
            if player1:
                self.draw_player_box(ax, 2, y_pos, player1, 'blue', 'left')
            
            # Combattant rouge (droite)
            if player2:
                self.draw_player_box(ax, 6, y_pos, player2, 'red', 'right')
            
            # Ligne de connexion
            if player1 and player2:
                ax.plot([3.5, 4.5], [y_pos, y_pos], 'white', linewidth=2)
    
    def create_match_bracket(self, ax, matches: List[Dict[str, Any]], players: List[Dict[str, Any]]):
        """Crée le bracket avec les matchs existants"""
        # Organiser les matchs par round
        rounds = {}
        for match in matches:
            round_num = match.get('round_number', 1)
            if round_num not in rounds:
                rounds[round_num] = []
            rounds[round_num].append(match)
        
        # Dessiner chaque round
        max_round = max(rounds.keys()) if rounds else 1
        x_spacing = 8 / max_round
        
        for round_num in range(1, max_round + 1):
            x_pos = 1 + (round_num - 1) * x_spacing
            round_matches = rounds.get(round_num, [])
            
            if round_matches:
                y_spacing = 8 / len(round_matches)
                
                for i, match in enumerate(round_matches):
                    y_pos = 8 - (i * y_spacing)
                    
                    # Dessiner les joueurs
                    blue_player = match.get('blue_player')
                    red_player = match.get('red_player')
                    
                    if blue_player:
                        self.draw_player_box(ax, x_pos - 1, y_pos, blue_player, 'blue', 'left')
                    
                    if red_player:
                        self.draw_player_box(ax, x_pos + 1, y_pos, red_player, 'red', 'right')
                    
                    # Ligne de connexion
                    if blue_player and red_player:
                        ax.plot([x_pos - 0.5, x_pos + 0.5], [y_pos, y_pos], 'white', linewidth=2)
                    
                    # Indiquer le vainqueur si le match est terminé
                    winner = match.get('winner')
                    if winner:
                        winner_pos = x_pos - 1 if winner == 'blue' else x_pos + 1
                        ax.scatter(winner_pos, y_pos, color='gold', s=100, zorder=5)
    
    def draw_player_box(self, ax, x: float, y: float, player: Dict[str, Any], color: str, side: str):
        """Dessine une boîte pour un joueur"""
        # Couleurs
        colors = self.tenue_colors[color]
        
        # Créer la boîte
        box = FancyBboxPatch(
            (x - 0.8, y - 0.3),
            1.6, 0.6,
            boxstyle="round,pad=0.1",
            facecolor=colors['primary'],
            edgecolor=colors['secondary'],
            linewidth=2
        )
        ax.add_patch(box)
        
        # Nom du joueur
        name = player.get('name', 'Joueur')
        ax.text(x, y + 0.1, name, ha='center', va='center', 
                fontsize=8, fontweight='bold', color=colors['text'])
        
        # Club
        club = player.get('club', '')
        if club:
            ax.text(x, y - 0.1, club, ha='center', va='center', 
                    fontsize=6, color=colors['text'])
    
    def update_current_match_info(self):
        """Met à jour les informations du match actuel"""
        matches = self.tournament_data.get('matches', [])
        current_matches = [m for m in matches if m.get('round_number') == self.current_round]
        
        if current_matches:
            # Prendre le premier match du round actuel
            current_match = current_matches[0]
            
            blue_player = current_match.get('blue_player', {})
            red_player = current_match.get('red_player', {})
            
            # Mettre à jour les labels
            self.blue_name_label.config(text=blue_player.get('name', 'Combattant Bleu'))
            self.blue_info_label.config(text=f"{blue_player.get('club', '')} - {blue_player.get('country', '')}")
            
            self.red_name_label.config(text=red_player.get('name', 'Combattant Rouge'))
            self.red_info_label.config(text=f"{red_player.get('club', '')} - {red_player.get('country', '')}")
        else:
            # Pas de match en cours
            self.blue_name_label.config(text="En attente...")
            self.blue_info_label.config(text="")
            self.red_name_label.config(text="En attente...")
            self.red_info_label.config(text="")
    
    def next_match(self):
        """Passe au match suivant"""
        if self.current_round < self.max_rounds:
            self.current_round += 1
            self.round_info_label.config(text=f"Round {self.current_round} / {self.max_rounds}")
            self.generate_tournament_bracket()
    
    def previous_match(self):
        """Passe au match précédent"""
        if self.current_round > 1:
            self.current_round -= 1
            self.round_info_label.config(text=f"Round {self.current_round} / {self.max_rounds}")
            self.generate_tournament_bracket()
    
    def print_tournament_bracket(self):
        """Imprime le graphique du tournoi"""
        try:
            # Sauvegarder le graphique
            filename = f"tournoi_bracket_{self.tournament_data.get('name', 'tournoi')}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='#2C2C3A')
            
            messagebox.showinfo(
                "Impression",
                f"Le graphique du tournoi a été sauvegardé sous le nom:\n{filename}"
            )
        except Exception as e:
            messagebox.showerror(
                "Erreur d'impression",
                f"Erreur lors de l'impression:\n{str(e)}"
            )
    
    def show_championship_final(self, winners: List[Dict[str, Any]]):
        """Affiche la finale du championnat de manière spectaculaire"""
        # Créer une nouvelle fenêtre pour la finale
        final_window = tk.Toplevel(self.parent)
        final_window.title("🏆 FINALE DU CHAMPIONNAT")
        final_window.geometry("1200x800")
        final_window.configure(bg='#1A1A2A')
        
        # Centrer la fenêtre
        self.center_window(final_window)
        
        # Ajouter l'icône
        self.set_window_icon()
        
        # Créer l'interface de la finale
        self.create_championship_interface(final_window, winners)
    
    def create_championship_interface(self, parent, winners: List[Dict[str, Any]]):
        """Crée l'interface pour la finale du championnat"""
        # Titre principal
        title_label = ttk.Label(
            parent,
            text="🏆 FINALE DU CHAMPIONNAT 🏆",
            font=('Arial', 32, 'bold'),
            foreground='#FFD700',
            background='#1A1A2A'
        )
        title_label.pack(pady=50)
        
        # Sous-titre
        subtitle_label = ttk.Label(
            parent,
            text="Affrontement des Vainqueurs de Catégories",
            font=('Arial', 18),
            foreground='white',
            background='#1A1A2A'
        )
        subtitle_label.pack(pady=20)
        
        # Frame pour les combattants
        fighters_frame = ttk.Frame(parent)
        fighters_frame.pack(pady=50)
        
        # Afficher les combattants
        for i, winner in enumerate(winners):
            self.create_champion_fighter_display(fighters_frame, winner, i)
        
        # Bouton pour commencer la finale
        start_btn = ttk.Button(
            parent,
            text="🥊 COMMENCER LA FINALE",
            command=lambda: self.start_championship_final(winners),
            style='Accent.TButton'
        )
        start_btn.pack(pady=30)
    
    def create_champion_fighter_display(self, parent, winner: Dict[str, Any], index: int):
        """Crée l'affichage d'un combattant champion"""
        frame = ttk.Frame(parent)
        frame.pack(side='left', padx=20)
        
        # Couleur selon l'index
        color = 'blue' if index == 0 else 'red'
        colors = self.tenue_colors[color]
        
        # Nom du champion
        name_label = ttk.Label(
            frame,
            text=winner.get('name', 'Champion'),
            font=('Arial', 20, 'bold'),
            foreground=colors['text'],
            background=colors['primary'],
            padding=(20, 10)
        )
        name_label.pack()
        
        # Informations
        info_text = f"Catégorie: {winner.get('category', '')}\n"
        info_text += f"Club: {winner.get('club', '')}\n"
        info_text += f"Pays: {winner.get('country', '')}"
        
        info_label = ttk.Label(
            frame,
            text=info_text,
            font=('Arial', 12),
            foreground=colors['primary']
        )
        info_label.pack(pady=10)
    
    def start_championship_final(self, winners: List[Dict[str, Any]]):
        """Démarre la finale du championnat"""
        # Ici, vous pouvez intégrer avec le système de match existant
        messagebox.showinfo(
            "Finale du Championnat",
            "La finale du championnat va commencer !\nLes combattants vont s'affronter pour déterminer le grand champion."
        ) 