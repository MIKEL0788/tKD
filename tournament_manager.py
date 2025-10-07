import os
import csv
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import random
from typing import List, Dict, Any, Optional, Tuple

class Player:
    """Classe représentant un joueur/combattant dans le tournoi"""
    def __init__(self, id: str, name: str, club: str, country: str, category: str, weight: str = "", age: str = ""):
        self.id = id
        self.name = name
        self.club = club
        self.country = country
        self.category = category
        self.weight = weight
        self.age = age
        self.wins = 0
        self.losses = 0
        self.points_scored = 0
        self.points_received = 0
        self.eliminated = False

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le joueur en dictionnaire pour la sérialisation"""
        return {
            "id": self.id,
            "name": self.name,
            "club": self.club,
            "country": self.country,
            "category": self.category,
            "weight": self.weight,
            "age": self.age,
            "wins": self.wins,
            "losses": self.losses,
            "points_scored": self.points_scored,
            "points_received": self.points_received,
            "eliminated": self.eliminated
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """Crée un joueur à partir d'un dictionnaire"""
        player = cls(
            id=data["id"],
            name=data["name"],
            club=data["club"],
            country=data["country"],
            category=data["category"],
            weight=data.get("weight", ""),
            age=data.get("age", "")
        )
        player.wins = data.get("wins", 0)
        player.losses = data.get("losses", 0)
        player.points_scored = data.get("points_scored", 0)
        player.points_received = data.get("points_received", 0)
        player.eliminated = data.get("eliminated", False)
        return player

class Match:
    """Classe représentant un match entre deux joueurs"""
    def __init__(self, match_id: str, blue_player: Player, red_player: Player, 
                 round_number: int, match_number: int, category: str):
        self.match_id = match_id
        self.blue_player = blue_player
        self.red_player = red_player
        self.round_number = round_number
        self.match_number = match_number
        self.category = category
        self.winner = None  # Sera défini après le match ("blue" ou "red")
        self.blue_score = 0
        self.red_score = 0
        self.blue_gam_jeom = 0
        self.red_gam_jeom = 0
        self.completed = False
        self.round_winners = []  # Liste des gagnants par round ("blue" ou "red")

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le match en dictionnaire pour la sérialisation"""
        return {
            "match_id": self.match_id,
            "blue_player": self.blue_player.to_dict() if self.blue_player else None,
            "red_player": self.red_player.to_dict() if self.red_player else None,
            "round_number": self.round_number,
            "match_number": self.match_number,
            "category": self.category,
            "winner": self.winner,
            "blue_score": self.blue_score,
            "red_score": self.red_score,
            "blue_gam_jeom": self.blue_gam_jeom,
            "red_gam_jeom": self.red_gam_jeom,
            "completed": self.completed,
            "round_winners": self.round_winners
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Match':
        """Crée un match à partir d'un dictionnaire"""
        blue_player = Player.from_dict(data["blue_player"]) if data.get("blue_player") else None
        red_player = Player.from_dict(data["red_player"]) if data.get("red_player") else None
        
        match = cls(
            match_id=data["match_id"],
            blue_player=blue_player,
            red_player=red_player,
            round_number=data["round_number"],
            match_number=data["match_number"],
            category=data["category"]
        )
        match.winner = data.get("winner")
        match.blue_score = data.get("blue_score", 0)
        match.red_score = data.get("red_score", 0)
        match.blue_gam_jeom = data.get("blue_gam_jeom", 0)
        match.red_gam_jeom = data.get("red_gam_jeom", 0)
        match.completed = data.get("completed", False)
        match.round_winners = data.get("round_winners", [])
        return match

class Tournament:
    """Classe représentant un tournoi complet"""
    def __init__(self, name: str, date: str, location: str):
        self.name = name
        self.date = date
        self.location = location
        self.players: Dict[str, Player] = {}  # id -> Player
        self.matches: Dict[str, Match] = {}  # match_id -> Match
        self.categories: Dict[str, List[str]] = {}  # category -> list of player_ids
        self.rounds: Dict[int, List[str]] = {}  # round_number -> list of match_ids
        self.current_round = 1
        self.tournament_id = f"{name.replace(' ', '_')}_{date.replace('/', '_')}"

    def add_player(self, player: Player) -> None:
        """Ajoute un joueur au tournoi"""
        self.players[player.id] = player
        
        # Ajouter à la catégorie appropriée
        if player.category not in self.categories:
            self.categories[player.category] = []
        self.categories[player.category].append(player.id)

    def import_players_from_csv(self, file_path: str) -> int:
        """Importe les joueurs depuis un fichier CSV"""
        count = 0
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Vérifier les champs obligatoires
                    required_fields = ['id', 'name', 'club', 'country', 'category']
                    if not all(field in row for field in required_fields):
                        continue
                    
                    player = Player(
                        id=row['id'],
                        name=row['name'],
                        club=row['club'],
                        country=row['country'],
                        category=row['category'],
                        weight=row.get('weight', ''),
                        age=row.get('age', '')
                    )
                    self.add_player(player)
                    count += 1
            return count
        except Exception as e:
            print(f"Erreur lors de l'importation des joueurs: {e}")
            return 0

    def generate_first_round(self, category: str) -> List[Match]:
        """Génère les matchs du premier tour pour une catégorie donnée"""
        if category not in self.categories or not self.categories[category]:
            return []
        
        # Récupérer les joueurs de cette catégorie
        player_ids = self.categories[category]
        players = [self.players[pid] for pid in player_ids if not self.players[pid].eliminated]
        
        # Supprimer les doublons (même joueur avec des IDs différents)
        unique_players = []
        seen_names = set()
        seen_ids = set()
        
        for player in players:
            # Vérifier à la fois le nom ET l'ID pour éviter les doublons
            if player.name not in seen_names and player.id not in seen_ids:
                unique_players.append(player)
                seen_names.add(player.name)
                seen_ids.add(player.id)
            else:
                print(f"Joueur dupliqué ignoré: {player.name} (ID: {player.id})")
        
        players = unique_players
        
        # Vérifier qu'il y a au moins 2 joueurs différents
        if len(players) < 2:
            print(f"Pas assez de joueurs uniques dans la catégorie {category} pour créer des matchs (seulement {len(players)} joueur(s))")
            return []
        
        # Mélanger les joueurs pour des matchs aléatoires
        random.shuffle(players)
        
        # Si nombre impair, ajouter un bye
        if len(players) % 2 != 0:
            bye_player = players.pop()
            bye_player.wins += 1
            print(f"Joueur {bye_player.name} passe automatiquement au tour suivant (bye)")
        
        matches = []
        match_number = 1
        
        # Créer les matchs
        for i in range(0, len(players), 2):
            if i + 1 < len(players):
                blue_player = players[i]
                red_player = players[i + 1]
                
                # Double vérification que les deux joueurs sont différents
                if (blue_player.id == red_player.id or 
                    blue_player.name == red_player.name or
                    blue_player.name.lower().strip() == red_player.name.lower().strip()):
                    print(f"ERREUR: Tentative de match entre le même joueur ({blue_player.name} vs {red_player.name})")
                    continue
                
                match_id = f"{category}_R1_M{match_number}"
                match = Match(
                    match_id=match_id,
                    blue_player=blue_player,
                    red_player=red_player,
                    round_number=1,
                    match_number=match_number,
                    category=category
                )
                
                self.matches[match_id] = match
                matches.append(match)
                match_number += 1
                print(f"Match créé: {blue_player.name} vs {red_player.name}")
        
        # Enregistrer les matchs pour ce tour
        if 1 not in self.rounds:
            self.rounds[1] = []
        
        self.rounds[1].extend([match.match_id for match in matches])
        return matches

    def generate_next_round(self, category: str) -> List[Match]:
        """Génère les matchs du tour suivant en fonction des gagnants du tour précédent"""
        current_round = self.current_round
        next_round = current_round + 1
        
        # Récupérer les matchs du tour actuel pour cette catégorie
        current_matches = []
        if current_round in self.rounds:
            for match_id in self.rounds[current_round]:
                match = self.matches[match_id]
                if match.category == category:
                    current_matches.append(match)
        
        # Vérifier que tous les matchs sont terminés
        if not all(match.completed for match in current_matches):
            return []
        
        # Récupérer les gagnants
        winners = []
        for match in current_matches:
            if match.winner == "blue":
                winners.append(match.blue_player)
                # Mettre à jour les statistiques
                match.blue_player.wins += 1
                match.red_player.losses += 1
                match.red_player.eliminated = True
            elif match.winner == "red":
                winners.append(match.red_player)
                # Mettre à jour les statistiques
                match.red_player.wins += 1
                match.blue_player.losses += 1
                match.blue_player.eliminated = True
        
        # Si nombre impair, ajouter un bye
        if len(winners) % 2 != 0:
            # Le dernier joueur passe automatiquement au tour suivant
            bye_player = winners.pop()
            bye_player.wins += 1
        
        matches = []
        match_number = 1
        
        # Créer les matchs du tour suivant
        for i in range(0, len(winners), 2):
            if i + 1 < len(winners):
                blue_player = winners[i]
                red_player = winners[i + 1]
                
                match_id = f"{category}_R{next_round}_M{match_number}"
                match = Match(
                    match_id=match_id,
                    blue_player=blue_player,
                    red_player=red_player,
                    round_number=next_round,
                    match_number=match_number,
                    category=category
                )
                
                self.matches[match_id] = match
                matches.append(match)
                match_number += 1
        
        # Enregistrer les matchs pour ce tour
        if next_round not in self.rounds:
            self.rounds[next_round] = []
        
        self.rounds[next_round].extend([match.match_id for match in matches])
        return matches

    def get_next_match(self, category: Optional[str] = None) -> Optional[Match]:
        """Récupère le prochain match non terminé"""
        for round_num in sorted(self.rounds.keys()):
            for match_id in self.rounds[round_num]:
                match = self.matches[match_id]
                if not match.completed and (category is None or match.category == category):
                    return match
        return None
        
    def get_matches_by_category(self) -> Dict[str, List[Match]]:
        """Retourne les matchs organisés par catégorie"""
        matches_by_category = {}
        
        for match_id, match in self.matches.items():
            if not match.completed:
                if match.category not in matches_by_category:
                    matches_by_category[match.category] = []
                matches_by_category[match.category].append(match)
        
        # Trier les matchs par numéro de tour et numéro de match
        for category in matches_by_category:
            matches_by_category[category].sort(key=lambda m: (m.round_number, m.match_number))
            
        return matches_by_category

    def update_match_result(self, match_id: str, blue_score: int, red_score: int, 
                           blue_gam_jeom: int, red_gam_jeom: int, winner: str, 
                           round_winners: List[str]) -> None:
        """Met à jour les résultats d'un match"""
        if match_id not in self.matches:
            return
        
        match = self.matches[match_id]
        match.blue_score = blue_score
        match.red_score = red_score
        match.blue_gam_jeom = blue_gam_jeom
        match.red_gam_jeom = red_gam_jeom
        match.winner = winner
        match.round_winners = round_winners
        match.completed = True
        
        # Mettre à jour les statistiques des joueurs
        if match.blue_player:
            match.blue_player.points_scored += blue_score
            match.blue_player.points_received += red_score
        
        if match.red_player:
            match.red_player.points_scored += red_score
            match.red_player.points_received += blue_score

    def save_to_file(self, file_path: str) -> bool:
        """Sauvegarde le tournoi dans un fichier JSON"""
        try:
            data = {
                "name": self.name,
                "date": self.date,
                "location": self.location,
                "tournament_id": self.tournament_id,
                "current_round": self.current_round,
                "players": {pid: player.to_dict() for pid, player in self.players.items()},
                "matches": {mid: match.to_dict() for mid, match in self.matches.items()},
                "categories": self.categories,
                "rounds": self.rounds
            }
            
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du tournoi: {e}")
            return False

    @classmethod
    def load_from_file(cls, file_path: str) -> Optional['Tournament']:
        """Charge un tournoi depuis un fichier JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            tournament = cls(data["name"], data["date"], data["location"])
            tournament.tournament_id = data["tournament_id"]
            tournament.current_round = data["current_round"]
            
            # Charger les joueurs
            for pid, player_data in data["players"].items():
                tournament.players[pid] = Player.from_dict(player_data)
            
            # Charger les matchs
            for mid, match_data in data["matches"].items():
                tournament.matches[mid] = Match.from_dict(match_data)
            
            # Charger les catégories et les tours
            tournament.categories = data["categories"]
            tournament.rounds = {int(k): v for k, v in data["rounds"].items()}
            
            return tournament
        except Exception as e:
            print(f"Erreur lors du chargement du tournoi: {e}")
            return None

class TournamentManager:
    """Gestionnaire de tournoi avec interface utilisateur"""
    def __init__(self, parent):
        self.parent = parent
        self.tournament = None
        self.data_dir = os.path.join(os.path.expanduser("~"), "TaekwondoManagerPro", "tournaments")
        os.makedirs(self.data_dir, exist_ok=True)
        # Ordre de passage des catégories (catégorie -> ordre)
        self.category_order = {}
    
    def create_new_tournament(self, name: str, date: str, location: str) -> Tournament:
        """Crée un nouveau tournoi"""
        self.tournament = Tournament(name, date, location)
        return self.tournament
    
    def import_players(self) -> int:
        """Ouvre une boîte de dialogue pour importer des joueurs depuis un CSV"""
        if not self.tournament:
            messagebox.showerror("Erreur", "Veuillez d'abord créer un tournoi")
            return 0
        
        file_path = filedialog.askopenfilename(
            title="Importer des joueurs",
            filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")]
        )
        
        if not file_path:
            return 0
        
        count = self.tournament.import_players_from_csv(file_path)
        if count > 0:
            messagebox.showinfo("Importation réussie", f"{count} joueurs ont été importés avec succès")
        else:
            messagebox.showerror("Erreur", "Aucun joueur n'a pu être importé")
        
        return count
    
    def save_tournament(self) -> bool:
        """Sauvegarde le tournoi actuel"""
        if not self.tournament:
            messagebox.showerror("Erreur", "Aucun tournoi à sauvegarder")
            return False
        
        file_path = os.path.join(self.data_dir, f"{self.tournament.tournament_id}.json")
        success = self.tournament.save_to_file(file_path)
        
        if success:
            messagebox.showinfo("Sauvegarde", "Tournoi sauvegardé avec succès")
        else:
            messagebox.showerror("Erreur", "Erreur lors de la sauvegarde du tournoi")
        
        return success
    
    def load_tournament(self) -> Optional[Tournament]:
        """Charge un tournoi existant"""
        file_path = filedialog.askopenfilename(
            title="Charger un tournoi",
            initialdir=self.data_dir,
            filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
        )
        
        if not file_path:
            return None
        
        tournament = Tournament.load_from_file(file_path)
        if tournament:
            self.tournament = tournament
            messagebox.showinfo("Chargement", "Tournoi chargé avec succès")
        else:
            messagebox.showerror("Erreur", "Erreur lors du chargement du tournoi")
        
        return tournament
    
    def get_next_match(self, category: Optional[str] = None) -> Optional[Match]:
        """Récupère le prochain match non terminé"""
        if not self.tournament:
            return None
        
        return self.tournament.get_next_match(category)
        
    def set_category_order(self, category_order: Dict[str, int]):
        """Définit l'ordre de passage des catégories"""
        self.category_order = category_order
        print(f"Ordre des catégories défini: {category_order}")
        # Sauvegarder immédiatement l'ordre
        if self.tournament:
            self.save_tournament()
    
    def get_matches_by_category(self) -> Dict[str, List[Match]]:
        """Récupère les matchs organisés par catégorie"""
        if not self.tournament:
            return {}
        
        # Récupérer les matchs par catégorie
        matches_by_category = self.tournament.get_matches_by_category()
        
        # Si un ordre de catégories est défini, trier le dictionnaire selon cet ordre
        if self.category_order:
            # Créer un nouveau dictionnaire trié
            sorted_matches = {}
            
            # Trier les catégories selon l'ordre défini
            sorted_categories = sorted(
                matches_by_category.keys(),
                key=lambda cat: self.category_order.get(cat, float('inf'))
            )
            
            # Reconstruire le dictionnaire dans l'ordre
            for category in sorted_categories:
                sorted_matches[category] = matches_by_category[category]
                
            return sorted_matches
        
        return matches_by_category
    
    def update_match_result(self, match_id: str, blue_score: int, red_score: int, 
                           blue_gam_jeom: int, red_gam_jeom: int, winner: str, 
                           round_winners: List[str]) -> None:
        """Met à jour les résultats d'un match"""
        if not self.tournament:
            return
        
        self.tournament.update_match_result(
            match_id, blue_score, red_score, blue_gam_jeom, red_gam_jeom, winner, round_winners
        )
    
    def generate_next_round(self, category: str) -> List[Match]:
        """Génère les matchs du tour suivant pour une catégorie"""
        if not self.tournament:
            return []
        
        if self.tournament.current_round == 1:
            matches = self.tournament.generate_first_round(category)
        else:
            matches = self.tournament.generate_next_round(category)
        
        if matches:
            self.tournament.current_round += 1
        
        return matches

class TournamentDialog(tk.Toplevel):
    """Boîte de dialogue pour créer ou charger un tournoi"""
    def __init__(self, parent, tournament_manager):
        super().__init__(parent)
        self.parent = parent
        self.tournament_manager = tournament_manager
        self.title("Gestion de tournoi")
        self.geometry("600x400")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        self.center_window()
    
    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Crée les widgets de la boîte de dialogue"""
        # Frame principal
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        title_label = ttk.Label(main_frame, text="Gestion de tournoi", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Boutons pour créer ou charger un tournoi
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        create_btn = ttk.Button(btn_frame, text="Créer un nouveau tournoi", command=self.show_create_tournament)
        create_btn.pack(fill=tk.X, pady=5)
        
        load_btn = ttk.Button(btn_frame, text="Charger un tournoi existant", command=self.load_tournament)
        load_btn.pack(fill=tk.X, pady=5)
        
        # Séparateur
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        
        # Frame pour la création de tournoi
        self.create_frame = ttk.LabelFrame(main_frame, text="Créer un nouveau tournoi", padding="10")
        
        # Champs pour la création de tournoi
        ttk.Label(self.create_frame, text="Nom du tournoi:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(self.create_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self.create_frame, text="Date (JJ/MM/AAAA):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.date_var = tk.StringVar()
        ttk.Entry(self.create_frame, textvariable=self.date_var, width=30).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self.create_frame, text="Lieu:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.location_var = tk.StringVar()
        ttk.Entry(self.create_frame, textvariable=self.location_var, width=30).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        btn_frame2 = ttk.Frame(self.create_frame)
        btn_frame2.grid(row=3, column=0, columnspan=2, pady=10)
        
        create_tournament_btn = ttk.Button(btn_frame2, text="Créer", command=self.create_tournament)
        create_tournament_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(btn_frame2, text="Annuler", command=lambda: self.create_frame.pack_forget())
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def show_create_tournament(self):
        """Affiche le formulaire de création de tournoi"""
        self.create_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    def create_tournament(self):
        """Crée un nouveau tournoi"""
        name = self.name_var.get().strip()
        date = self.date_var.get().strip()
        location = self.location_var.get().strip()
        
        if not name or not date or not location:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
            return
        
        tournament = self.tournament_manager.create_new_tournament(name, date, location)
        if tournament:
            messagebox.showinfo("Succès", "Tournoi créé avec succès")
            self.show_import_players()
        else:
            messagebox.showerror("Erreur", "Erreur lors de la création du tournoi")
    
    def load_tournament(self):
        """Charge un tournoi existant"""
        tournament = self.tournament_manager.load_tournament()
        if tournament:
            self.destroy()
    
    def show_import_players(self):
        """Affiche la boîte de dialogue pour importer des joueurs"""
        self.create_frame.pack_forget()
        
        import_frame = ttk.LabelFrame(self, text="Importer des joueurs", padding="10")
        import_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        ttk.Label(import_frame, text="Voulez-vous importer des joueurs maintenant ?").pack(pady=10)
        
        btn_frame = ttk.Frame(import_frame)
        btn_frame.pack(pady=10)
        
        import_btn = ttk.Button(btn_frame, text="Importer des joueurs", 
                               command=lambda: self.import_players_and_close(import_frame))
        import_btn.pack(side=tk.LEFT, padx=5)
        
        skip_btn = ttk.Button(btn_frame, text="Passer cette étape", command=self.destroy)
        skip_btn.pack(side=tk.LEFT, padx=5)
    
    def import_players_and_close(self, frame):
        """Importe des joueurs et ferme la boîte de dialogue"""
        count = self.tournament_manager.import_players()
        if count > 0:
            self.destroy()
        else:
            frame.pack_forget()
            self.show_import_players()