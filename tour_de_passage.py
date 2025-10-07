import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.patches import Rectangle, FancyBboxPatch
import math

class afficher_pyramide:
    def __init__(self, parent_frame, tournament_data):
        self.parent_frame = parent_frame
        self.tournament_data = tournament_data
        self.current_round = 1
        self.current_match_idx = 0
        self.setup_ui()
        
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Cadre principal
        self.main_frame = ttk.Frame(self.parent_frame)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Cadre pour les contrôles (boutons)
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill='x', pady=(0, 10))
        
        # Boutons de navigation
        self.prev_btn = ttk.Button(self.control_frame, text="← Match Précédent", 
                                  command=self.previous_match)
        self.prev_btn.pack(side='left', padx=(0, 10))
        
        self.next_btn = ttk.Button(self.control_frame, text="Match Suivant →", 
                                  command=self.next_match)
        self.next_btn.pack(side='left')
        
        # Bouton d'impression
        self.print_btn = ttk.Button(self.control_frame, text="🖨️ Imprimer le Graphique", 
                                   command=self.print_bracket)
        self.print_btn.pack(side='right')
        
        # Cadre pour les informations du match en cours
        self.info_frame = ttk.LabelFrame(self.main_frame, text="Informations du Match")
        self.info_frame.pack(fill='x', pady=(0, 10))
        
        self.match_info = ttk.Label(self.info_frame, text="Sélectionnez un match pour voir les détails")
        self.match_info.pack(padx=10, pady=10)
        
        # Cadre pour le graphique pyramidal
        self.graph_frame = ttk.Frame(self.main_frame)
        self.graph_frame.pack(fill='both', expand=True)
        
        # Générer le bracket initial
        self.generate_bracket()
        
        # Mettre à jour l'état des boutons
        self.update_buttons_state()
    
    def generate_bracket(self):
        """Génère le graphique pyramidal du tournoi"""
        # Nettoyer le frame du graphique
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        
        # Créer la figure matplotlib avec un design moderne
        fig, ax = plt.subplots(figsize=(14, 10))
        fig.patch.set_facecolor('#2C2C3A')
        ax.set_facecolor('#2C2C3A')
        
        # Obtenir les données du tournoi
        matches = self.tournament_data.get('matches', [])
        players = self.tournament_data.get('players', [])
        
        if not matches:
            self.create_empty_bracket(ax, players)
        else:
            self.create_pyramid_bracket(ax, matches, players)
        
        # Configuration de l'apparence
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        ax.set_title('Pyramide du Tournoi - Coupe d\'Afrique', color='white', fontsize=16, pad=20)
        
        # Créer le canvas avec une apparence moderne
        self.canvas = FigureCanvasTkAgg(fig, self.graph_frame)
        self.canvas.draw()
        
        # Ajouter une toolbar de navigation
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.graph_frame)
        self.toolbar.update()
        self.toolbar.pack(side='bottom', fill='x')
        
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Mettre à jour les informations du match actuel
        self.update_match_info()
    
    def create_pyramid_bracket(self, ax, matches, players):
        """Crée la structure pyramidale des matchs avec un design moderne"""
        # Organiser les matchs par round
        rounds = {}
        for match in matches:
            round_num = match['round']
            if round_num not in rounds:
                rounds[round_num] = []
            rounds[round_num].append(match)
        
        # Déterminer le nombre total de rounds
        total_rounds = max(rounds.keys()) if rounds else 0
        
        # Couleurs modernes
        colors = {
            'blue': '#3498db',
            'red': '#e74c3c',
            'background': '#2C2C3A',
            'text': '#ECF0F1',
            'line': '#566573',
            'highlight': '#F1C40F',
            'player1': '#E74C3C',  # Rouge
            'player2': '#3498DB',  # Bleu
            'winner': '#2ECC71',   # Vert pour le gagnant
            'future_match': '#7F8C8D'  # Gris pour les matchs futurs
        }
        
        # Paramètres de la pyramide
        base_y = 8.5
        round_height = 1.2
        match_width = 1.5
        
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
                
                # Déterminer si c'est le match actuel
                is_current = (round_num == self.current_round and 
                             i == self.current_match_idx)
                
                # Dessiner les connexions avec les rounds précédents
                if round_num > 1:
                    # Calculer les positions des matchs parents
                    parent_match_idx = i // 2
                    parent_round_matches = rounds.get(round_num - 1, [])
                    
                    if parent_match_idx < len(parent_round_matches):
                        parent_x = start_x + parent_match_idx * match_width + match_width / 2
                        parent_y = base_y - (round_num - 2) * round_height
                        
                        # Ligne de connexion
                        ax.plot([parent_x, x_pos], [parent_y, y_pos], 
                               color=colors['line'], linewidth=2, alpha=0.7, zorder=1)
                
                # Dessiner le match
                self.draw_match(ax, match, x_pos, y_pos, colors, is_current)
        
        # Ajouter le trophée pour le gagnant final
        if total_rounds > 0:
            winner = self.determine_winner(matches, players)
            if winner:
                ax.text(5, 0.5, f"🏆 {winner}", ha='center', va='center', 
                       fontsize=14, color=colors['highlight'], 
                       bbox=dict(facecolor=colors['background'], alpha=0.8, 
                                edgecolor=colors['highlight'], boxstyle='round,pad=0.5'))
    
    def draw_match(self, ax, match, x, y, colors, is_current=False):
        """Dessine un match individuel avec style moderne"""
        # Déterminer les couleurs des joueurs
        player1_color = colors['player1']
        player2_color = colors['player2']
        
        # Déterminer le style basé sur le gagnant
        winner = match.get('winner')
        p1_style = 'bold' if winner == 'player1' else 'normal'
        p2_style = 'bold' if winner == 'player2' else 'normal'
        
        # Couleur de fond différente pour le match actuel
        if is_current:
            bg_color = '#34495E'
            border_color = colors['highlight']
            border_width = 3
        elif winner:
            bg_color = '#2C3E50'
            border_color = colors['line']
            border_width = 1
        else:
            bg_color = colors['background']
            border_color = colors['line']
            border_width = 1
        
        # Rectangle de fond pour le match
        rect = FancyBboxPatch((x-0.6, y-0.25), 1.2, 0.5, 
                             boxstyle="round,pad=0.1",
                             facecolor=bg_color, edgecolor=border_color,
                             linewidth=border_width, alpha=0.9, zorder=2)
        ax.add_patch(rect)
        
        # Afficher les noms des joueurs avec leurs couleurs
        ax.text(x, y + 0.1, match['player1'], ha='center', va='center',
               color=player1_color, fontsize=10, weight=p1_style, family='sans-serif')
        ax.text(x, y - 0.1, match['player2'], ha='center', va='center',
               color=player2_color, fontsize=10, weight=p2_style, family='sans-serif')
        
        # Afficher le score si disponible
        if 'score' in match and match['score']:
            ax.text(x, y, match['score'], ha='center', va='center',
                   color=colors['text'], fontsize=9, weight='bold', family='sans-serif')
        
        # Afficher le round et le numéro du match
        round_text = f"Round {match['round']}"
        ax.text(x, y + 0.3, round_text, ha='center', va='center',
               color=colors['text'], fontsize=8, alpha=0.7, family='sans-serif')
    
    def create_empty_bracket(self, ax, players):
        """Crée un bracket vide avec les joueurs"""
        # Afficher un message
        ax.text(5, 5, "Le tournoi n'a pas encore commencé", 
               ha='center', va='center', fontsize=14, color='white', family='sans-serif')
        
        # Afficher la liste des participants
        if players:
            participants_text = "Participants:\n" + "\n".join(players)
            ax.text(5, 3, participants_text, 
                   ha='center', va='center', fontsize=11, color='white', family='sans-serif')
    
    def determine_winner(self, matches, players):
        """Détermine le gagnant final du tournoi"""
        # Trouver le match final
        max_round = max(match['round'] for match in matches)
        final_matches = [m for m in matches if m['round'] == max_round]
        
        if final_matches and 'winner' in final_matches[0]:
            winner_id = final_matches[0]['winner']
            # Trouver le nom du gagnant basé sur son ID
            for player in players:
                if player.get('id') == winner_id:
                    return player.get('name', 'Gagnant')
        return None
    
    def update_match_info(self):
        """Met à jour les informations du match actuel"""
        matches = self.tournament_data.get('matches', [])
        current_matches = [m for m in matches if m['round'] == self.current_round]
        
        if current_matches and self.current_match_idx < len(current_matches):
            match = current_matches[self.current_match_idx]
            
            # Déterminer l'état du match
            if match.get('winner'):
                status = "Terminé"
                result = f"Vainqueur: {match['winner']}"
            else:
                status = "À venir"
                result = "En attente"
            
            # Mettre à jour le texte d'information
            info_text = f"Round {self.current_round} - Match {self.current_match_idx + 1}\n"
            info_text += f"{match['player1']} (Rouge) vs {match['player2']} (Bleu)\n"
            info_text += f"Statut: {status}\n"
            info_text += result
            
            self.match_info.config(text=info_text)
        else:
            self.match_info.config(text="Aucun match sélectionné")
    
    def next_match(self):
        """Passe au match suivant"""
        matches = self.tournament_data.get('matches', [])
        current_round_matches = [m for m in matches if m['round'] == self.current_round]
        
        if self.current_match_idx < len(current_round_matches) - 1:
            self.current_match_idx += 1
        else:
            # Passer au round suivant s'il existe
            next_round = self.current_round + 1
            next_round_matches = [m for m in matches if m['round'] == next_round]
            
            if next_round_matches:
                self.current_round = next_round
                self.current_match_idx = 0
            else:
                # Revenir au début si on est à la fin
                self.current_round = 1
                self.current_match_idx = 0
        
        self.generate_bracket()
        self.update_buttons_state()
    
    def previous_match(self):
        """Revient au match précédent"""
        if self.current_match_idx > 0:
            self.current_match_idx -= 1
        else:
            # Revenir au round précédent s'il existe
            prev_round = self.current_round - 1
            if prev_round > 0:
                matches = self.tournament_data.get('matches', [])
                prev_round_matches = [m for m in matches if m['round'] == prev_round]
                
                if prev_round_matches:
                    self.current_round = prev_round
                    self.current_match_idx = len(prev_round_matches) - 1
        
        self.generate_bracket()
        self.update_buttons_state()
    
    def update_buttons_state(self):
        """Met à jour l'état des boutons de navigation"""
        matches = self.tournament_data.get('matches', [])
        
        # Vérifier s'il y a un match précédent
        has_previous = not (self.current_round == 1 and self.current_match_idx == 0)
        
        # Vérifier s'il y a un match suivant
        current_round_matches = [m for m in matches if m['round'] == self.current_round]
        has_next = not (self.current_round == max(m['round'] for m in matches) and 
                       self.current_match_idx == len(current_round_matches) - 1)
        
        self.prev_btn.config(state='normal' if has_previous else 'disabled')
        self.next_btn.config(state='normal' if has_next else 'disabled')
    
    def print_bracket(self):
        """Imprime le graphique du tournoi"""
        # Enregistrer la figure dans un fichier
        try:
            plt.figure(self.canvas.figure.number)
            plt.savefig("pyramide_tournoi.png", dpi=300, bbox_inches='tight', 
                       facecolor='#2C2C3A', edgecolor='none')
            messagebox.showinfo("Impression", "Graphique exporté sous 'pyramide_tournoi.png'")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'exporter le graphique: {str(e)}")
    
    def update_tournament_data(self, new_data):
        """Met à jour les données du tournoi et rafraîchit l'affichage"""
        self.tournament_data = new_data
        self.generate_bracket()
        self.update_buttons_state()