import os
import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple, Set

class ImportManager:
    """Gestionnaire d'importation de données pour le système de tournoi"""
    def __init__(self):
        self.supported_formats = ['.csv', '.xlsx', '.xls']
        self.required_fields = ['id', 'name', 'club', 'country', 'category']
        self.optional_fields = ['weight', 'age', 'gender', 'belt']
    
    def validate_file_format(self, file_path: str) -> bool:
        """Vérifie si le format du fichier est supporté"""
        _, ext = os.path.splitext(file_path)
        return ext.lower() in self.supported_formats
    
    def read_file(self, file_path: str) -> Optional[List[Dict[str, Any]]]:
        """Lit le fichier et retourne les données sous forme de liste de dictionnaires"""
        if not self.validate_file_format(file_path):
            return None
        
        try:
            _, ext = os.path.splitext(file_path)
            
            if ext.lower() == '.csv':
                return self._read_csv(file_path)
            elif ext.lower() in ['.xlsx', '.xls']:
                return self._read_excel(file_path)
            
            return None
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier: {e}")
            return None
    
    def _read_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """Lit un fichier CSV et retourne les données, peu importe le séparateur (virgule, point-virgule, tabulation)"""
        import csv
        data = []
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                # Lire un échantillon pour détecter le séparateur
                sample = file.read(4096)
                file.seek(0)
                # Détection automatique du séparateur
                sniffer = csv.Sniffer()
                try:
                    dialect = sniffer.sniff(sample, delimiters=[',', ';', '\t'])
                except csv.Error:
                    # Si la détection échoue, on tente tabulation puis virgule
                    if '\t' in sample:
                        dialect = csv.get_dialect('excel-tab')
                    else:
                        dialect = csv.get_dialect('excel')
                reader = csv.DictReader(file, dialect=dialect)
                for row in reader:
                    # Normaliser les clés pour matcher les champs requis
                    normalized_row = {k.strip().lower(): v for k, v in row.items()}
                    # Vérifier que les champs requis sont présents
                    if all(field in normalized_row for field in self.required_fields):
                        # Remettre les clés d'origine attendues
                        item = {}
                        for field in self.required_fields + self.optional_fields:
                            item[field] = normalized_row.get(field, "")
                        data.append(item)
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as file:
                sample = file.read(4096)
                file.seek(0)
                sniffer = csv.Sniffer()
                try:
                    dialect = sniffer.sniff(sample, delimiters=[',', ';', '\t'])
                except csv.Error:
                    if '\t' in sample:
                        dialect = csv.get_dialect('excel-tab')
                    else:
                        dialect = csv.get_dialect('excel')
                reader = csv.DictReader(file, dialect=dialect)
                for row in reader:
                    normalized_row = {k.strip().lower(): v for k, v in row.items()}
                    if all(field in normalized_row for field in self.required_fields):
                        item = {}
                        for field in self.required_fields + self.optional_fields:
                            item[field] = normalized_row.get(field, "")
                        data.append(item)
        return data
        
    def _read_excel(self, file_path: str) -> List[Dict[str, Any]]:
        """Lit un fichier Excel et retourne les données avec structure bien organisée"""
        try:
            # Lire toutes les feuilles ou seulement la première
            df = pd.read_excel(file_path, sheet_name=0)
            
            # Normaliser les noms de colonnes : minuscules et suppression espaces
            df.columns = [col.strip().lower() for col in df.columns]
            
            # Vérifier les colonnes requises (en minuscules)
            required_lower = [f.lower() for f in self.required_fields]
            if not all(field in df.columns for field in required_lower):
                missing = set(required_lower) - set(df.columns)
                print(f"Colonnes manquantes: {', '.join(missing)}")
                return []
            
            # Gérer les colonnes optionnelles
            for opt in self.optional_fields:
                opt_lower = opt.lower()
                if opt_lower not in df.columns:
                    df[opt_lower] = ""  # Ajouter colonne vide si manquante
            
            # Convertir et formater les données avec structure bien organisée
            data = []
            for _, row in df.iterrows():
                # Créer un dictionnaire avec toutes les colonnes bien structurées
                item = {}
                
                # Colonnes requises
                for field in self.required_fields:
                    field_lower = field.lower()
                    if field_lower in df.columns:
                        value = row[field_lower]
                        if pd.notna(value):
                            item[field] = str(value).strip()
                        else:
                            item[field] = ""
                    else:
                        item[field] = ""
                
                # Colonnes optionnelles
                for opt in self.optional_fields:
                    opt_lower = opt.lower()
                    if opt_lower in df.columns:
                        value = row[opt_lower]
                        if pd.notna(value):
                            item[opt] = str(value).strip()
                        else:
                            item[opt] = ""
                    else:
                        item[opt] = ""
                
                # Nettoyer et valider les données
                if self._validate_player_data(item):
                    data.append(item)
            
            return data
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier Excel: {e}")
            return []
    
    def _validate_player_data(self, player_data: Dict[str, Any]) -> bool:
        """Valide les données d'un joueur"""
        # Vérifier que les champs requis ne sont pas vides
        for field in self.required_fields:
            if not player_data.get(field, "").strip():
                print(f"Champ requis manquant ou vide: {field}")
                return False
        
        # Valider le format de l'ID
        player_id = player_data.get('id', '').strip()
        if not player_id or len(player_id) < 2:
            print(f"ID invalide: {player_id}")
            return False
        
        # Valider le nom
        name = player_data.get('name', '').strip()
        if not name or len(name) < 2:
            print(f"Nom invalide: {name}")
            return False
        
        # Valider la catégorie
        category = player_data.get('category', '').strip()
        if not category:
            print(f"Catégorie manquante pour {name}")
            return False
        
        return True
    
    def validate_data(self, data: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Valide les données importées"""
        valid_data = []
        errors = []
        seen_ids = set()
        
        for i, row in enumerate(data, start=1):
            # Vérification des champs obligatoires
            missing = [field for field in self.required_fields if field not in row or not row[field]]
            if missing:
                errors.append(f"Ligne {i}: Champs obligatoires manquants ({', '.join(missing)})")
                continue
            
            # Vérification de l'unicité des IDs
            player_id = row['id']
            if player_id in seen_ids:
                errors.append(f"Ligne {i}: ID dupliqué '{player_id}'")
                continue
            seen_ids.add(player_id)
            
            # Validation du poids
            if 'weight' in row:
                try:
                    row['weight'] = float(row['weight'])
                except (ValueError, TypeError):
                    errors.append(f"Ligne {i}: Format de poids invalide '{row['weight']}'")
                    continue
            
            valid_data.append(row)
        
        return valid_data, errors

class ImportDialog(tk.Toplevel):
    """Boîte de dialogue pour importer des données"""
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.parent = parent
        self.callback = callback
        self.import_manager = ImportManager()
        self.imported_data = []
        self.all_columns = []  # Stocke toutes les colonnes détectées
        
        self.title("Importation de joueurs")
        self.geometry("800x600")
        self.resizable(True, True)
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
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="Importation de joueurs", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        file_frame = ttk.LabelFrame(main_frame, text="Sélection du fichier", padding="10")
        file_frame.pack(fill=tk.X, pady=10)
        
        file_frame_inner = ttk.Frame(file_frame)
        file_frame_inner.pack(fill=tk.X)
        
        self.file_path_var = tk.StringVar()
        ttk.Label(file_frame_inner, text="Fichier:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(file_frame_inner, textvariable=self.file_path_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(file_frame_inner, text="Parcourir...", command=self.browse_file).pack(side=tk.LEFT)
        
        formats_text = "Formats supportés: CSV, Excel (.xlsx, .xls)"
        ttk.Label(file_frame, text=formats_text, font=("Arial", 9, "italic")).pack(anchor=tk.W, pady=(5, 0))
        
        required_text = "Champs obligatoires: id, name, club, country, category"
        ttk.Label(file_frame, text=required_text, font=("Arial", 9, "italic")).pack(anchor=tk.W)
        
        ttk.Button(file_frame, text="Importer", command=self.import_file).pack(anchor=tk.E, pady=(10, 0))
        
        preview_frame = ttk.LabelFrame(main_frame, text="Aperçu des données", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        table_frame = ttk.Frame(preview_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configuration des scrollbars
        y_scrollbar = ttk.Scrollbar(table_frame)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Configuration du Treeview
        self.tree = ttk.Treeview(
            table_frame,
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set,
            show="headings"  # Afficher uniquement les en-têtes
        )
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        y_scrollbar.config(command=self.tree.yview)
        x_scrollbar.config(command=self.tree.xview)
        
        # Boutons de confirmation
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Confirmer", command=self.confirm_import).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Annuler", command=self.destroy).pack(side=tk.RIGHT, padx=5)
    
    def browse_file(self):
        """Ouvre une boîte de dialogue pour sélectionner un fichier"""
        file_types = [
            ("Fichiers supportés", "*.csv;*.xlsx;*.xls"),
            ("Fichiers CSV", "*.csv"),
            ("Fichiers Excel", "*.xlsx;*.xls"),
            ("Tous les fichiers", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier",
            filetypes=file_types
        )
        
        if file_path:
            self.file_path_var.set(file_path)
    
    def import_file(self):
        """Importe les données du fichier sélectionné"""
        file_path = self.file_path_var.get()
        
        if not file_path:
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier")
            return
        
        if not self.import_manager.validate_file_format(file_path):
            messagebox.showerror("Erreur", "Format de fichier non supporté")
            return
        
        data = self.import_manager.read_file(file_path)
        
        if not data:
            messagebox.showerror("Erreur", "Impossible de lire le fichier ou aucune donnée valide")
            return
        
        valid_data, errors = self.import_manager.validate_data(data)
        
        if errors:
            error_msg = "\n".join(errors[:10])
            if len(errors) > 10:
                error_msg += f"\n... et {len(errors) - 10} autres erreurs"
            messagebox.showwarning("Avertissement", f"Des erreurs ont été détectées:\n{error_msg}")
        
        if not valid_data:
            messagebox.showerror("Erreur", "Aucune donnée valide à importer")
            return
        
        self.imported_data = valid_data
        self.update_preview()
    
    def update_preview(self):
        """Met à jour l'aperçu des données"""
        # Réinitialiser le Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.tree["columns"] = []
        
        # Déterminer toutes les colonnes disponibles
        if self.imported_data:
            all_columns = set()
            for row in self.imported_data:
                all_columns.update(row.keys())
            self.all_columns = sorted(all_columns)
            
            # Configurer les colonnes du Treeview
            self.tree["columns"] = self.all_columns
            
            # Configurer les en-têtes
            for col in self.all_columns:
                self.tree.heading(col, text=col.capitalize())
                self.tree.column(col, width=100, anchor=tk.W)
            
            # Ajouter les données
            for row in self.imported_data:
                values = [row.get(col, "") for col in self.all_columns]
                self.tree.insert("", tk.END, values=values)
    
    def confirm_import(self):
        """Confirme l'importation des données"""
        if not self.imported_data:
            messagebox.showerror("Erreur", "Aucune donnée à importer")
            return
        
        self.callback(self.imported_data)
        self.destroy()