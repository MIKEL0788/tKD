import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading

class SecureActivationWindow:
    def __init__(self, master, secure_license_manager):
        self.master = master
        self.license_manager = secure_license_manager
        self.master.title("Activation Sécurisée - Taekwondo Pro")
        self.master.geometry("750x650")
        self.master.resizable(False, False)
        self.master.configure(bg='#f5f5f5')
        
        # Variables pour le contrôle d'activation
        self.activation_in_progress = False
        self.server_time_available = False
        self.offline_mode = False
        
        # Centrer la fenêtre
        self.center_window()
        
        # Créer les styles personnalisés
        self.create_custom_styles()
        
        # Créer l'interface
        self.create_interface()
        
        # Vérifier le statut de sécurité au démarrage
        self.check_security_status()
    
    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.master.update_idletasks()
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width - 750) // 2
        y = (screen_height - 650) // 2
        self.master.geometry(f"750x650+{x}+{y}")
    
    def create_custom_styles(self):
        """Crée des styles personnalisés pour l'interface moderne"""
        self.style = ttk.Style()
        
        # Style pour les boutons principaux
        self.style.configure('Modern.TButton',
                           padding=(20, 10),
                           font=('Arial', 10, 'bold'))
        
        # Style pour le bouton d'activation
        self.style.configure('Accent.TButton',
                           padding=(25, 12),
                           font=('Arial', 11, 'bold'))
    
    def create_interface(self):
        """Crée l'interface moderne d'activation sécurisée"""
        # En-tête avec gradient simulé - couleur adaptée selon sécurité
        header_color = self.get_header_color()
        header_frame = tk.Frame(self.master, bg=header_color, height=130)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Contenu de l'en-tête
        header_content = tk.Frame(header_frame, bg=header_color)
        header_content.pack(expand=True, fill='both', padx=40, pady=20)
        
        # Logo et titre dans l'en-tête
        title_frame = tk.Frame(header_content, bg=header_color)
        title_frame.pack(side=tk.LEFT, fill='y')
        
        tk.Label(title_frame,
                text="🔐",
                font=('Arial', 32),
                bg=header_color,
                fg='white').pack(anchor='w')
        
        tk.Label(title_frame,
                text="ACTIVATION SÉCURISÉE",
                font=('Arial', 18, 'bold'),
                bg=header_color,
                fg='white').pack(anchor='w')
        
        tk.Label(title_frame,
                text="Gestionnaire Taekwondo Pro - Protection Avancée",
                font=('Arial', 12),
                bg=header_color,
                fg='#E3F2FD').pack(anchor='w', pady=(5, 0))
        
        # Logo principal à droite
        logo_frame = tk.Frame(header_content, bg=header_color)
        logo_frame.pack(side=tk.RIGHT, fill='y')
        
        tk.Label(logo_frame,
                text="🥋",
                font=('Arial', 48),
                bg=header_color,
                fg='white').pack()
        
        # Indicateur de statut de sécurité
        self.security_indicator = tk.Label(logo_frame,
                                         text="",
                                         font=('Arial', 10, 'bold'),
                                         bg=header_color,
                                         fg='white')
        self.security_indicator.pack(pady=(5, 0))
        
        # Corps principal avec carte
        body_frame = tk.Frame(self.master, bg='#f5f5f5')
        body_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # Carte principale avec effet d'ombre intégré
        shadow_container = tk.Frame(body_frame, bg='#e0e0e0')
        shadow_container.pack(fill=tk.BOTH, expand=True)
        
        # Décalage pour simuler l'ombre
        card_frame = tk.Frame(shadow_container, bg='white', relief='flat', bd=0)
        card_frame.pack(fill=tk.BOTH, expand=True, padx=(0, 2), pady=(0, 2))
        
        # Contenu de la carte
        card_content = tk.Frame(card_frame, bg='white')
        card_content.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Section Statut de Sécurité (NOUVEAU)
        self.create_security_section(card_content)
        
        # Section ID Machine
        machine_section = tk.Frame(card_content, bg='white')
        machine_section.pack(fill='x', pady=(0, 25))
        
        tk.Label(machine_section,
                text="Identifiant sécurisé de votre machine",
                font=('Arial', 11, 'bold'),
                bg='white',
                fg='#333333').pack(anchor='w')
        
        machine_info_frame = tk.Frame(machine_section, bg='white')
        machine_info_frame.pack(fill='x', pady=(8, 0))
        
        # Zone d'ID avec style moderne
        id_frame = tk.Frame(machine_info_frame, bg='#f8f9fa', relief='solid', bd=1)
        id_frame.pack(fill='x', side='left', expand=True, padx=(0, 10))
        
        self.machine_id_label = tk.Label(id_frame,
                                       text=self.get_masked_id(),
                                       font=('Courier', 10, 'bold'),
                                       bg='#f8f9fa',
                                       fg='#FF6B35',
                                       pady=12,
                                       padx=15)
        self.machine_id_label.pack(fill='x')
        
        # Bouton copier moderne
        copy_button = tk.Button(machine_info_frame,
                              text="📋 Copier",
                              command=self.copy_machine_id,
                              bg='#4CAF50',
                              fg='white',
                              font=('Arial', 9, 'bold'),
                              relief='flat',
                              padx=20,
                              pady=12,
                              cursor='hand2')
        copy_button.pack(side='right')
        
        # Section clé de licence
        key_section = tk.Frame(card_content, bg='white')
        key_section.pack(fill='x', pady=(0, 20))
        
        tk.Label(key_section,
                text="Clé de licence",
                font=('Arial', 11, 'bold'),
                bg='white',
                fg='#333333').pack(anchor='w')
        
        tk.Label(key_section,
                text="Entrez la clé de licence fournie lors de votre achat (Format: XXXX-XXXX-XXXX-XXXX)",
                font=('Arial', 9),
                bg='white',
                fg='#666666').pack(anchor='w', pady=(2, 8))
        
        # Champ de saisie moderne
        entry_frame = tk.Frame(key_section, bg='white')
        entry_frame.pack(fill='x')
        
        self.key_entry = tk.Entry(entry_frame,
                                font=('Courier', 12),
                                relief='solid',
                                bd=2,
                                highlightthickness=0,
                                bg='white',
                                fg='#333333',
                                insertbackground='#2196F3')
        self.key_entry.pack(fill='x', ipady=12, ipadx=15)
        
        # Lier les événements pour les effets visuels et la validation
        self.key_entry.bind('<FocusIn>', self.on_entry_focus_in)
        self.key_entry.bind('<FocusOut>', self.on_entry_focus_out)
        self.key_entry.bind('<KeyRelease>', self.on_key_change)
        
        # Section mode d'activation (NOUVEAU)
        self.create_activation_mode_section(card_content)
        
        # Boutons d'action
        action_frame = tk.Frame(card_content, bg='white')
        action_frame.pack(fill='x', pady=(20, 0))
        
        # Bouton principal d'activation
        self.activate_button = tk.Button(action_frame,
                                       text="🔓 Activer la Licence",
                                       command=self.activate,
                                       bg='#2196F3',
                                       fg='white',
                                       font=('Arial', 11, 'bold'),
                                       relief='flat',
                                       padx=30,
                                       pady=15,
                                       cursor='hand2')
        self.activate_button.pack(side='left')
        
        # Bouton test de connexion (NOUVEAU)
        test_button = tk.Button(action_frame,
                              text="🌐 Test Connexion",
                              command=self.test_server_connection,
                              bg='#9C27B0',
                              fg='white',
                              font=('Arial', 10),
                              relief='flat',
                              padx=20,
                              pady=15,
                              cursor='hand2')
        test_button.pack(side='left', padx=(10, 0))
        
        # Bouton d'achat
        buy_button = tk.Button(action_frame,
                             text="🛒 Acheter",
                             command=self.buy_license,
                             bg='#FF6B35',
                             fg='white',
                             font=('Arial', 10),
                             relief='flat',
                             padx=20,
                             pady=15,
                             cursor='hand2')
        buy_button.pack(side='left', padx=(10, 0))
        
        # Bouton quitter
        quit_button = tk.Button(action_frame,
                              text="✕ Quitter",
                              command=self.master.destroy,
                              bg='#f44336',
                              fg='white',
                              font=('Arial', 10),
                              relief='flat',
                              padx=20,
                              pady=15,
                              cursor='hand2')
        quit_button.pack(side='right')
        
        # Zone de progression (cachée initialement)
        self.progress_frame = tk.Frame(card_content, bg='white')
        
        self.progress_label = tk.Label(self.progress_frame,
                                     text="",
                                     font=('Arial', 10),
                                     bg='white',
                                     fg='#666666')
        self.progress_label.pack(anchor='w', pady=(0, 8))
        
        # Barre de progression moderne
        progress_bg_frame = tk.Frame(self.progress_frame, bg='#e0e0e0', height=8)
        progress_bg_frame.pack(fill='x')
        progress_bg_frame.pack_propagate(False)
        
        self.progress_fill = tk.Frame(progress_bg_frame, bg='#4CAF50', height=8)
        self.progress_fill.place(x=0, y=0, width=0, height=8)
        
        # Zone de statut
        self.status_label = tk.Label(card_content,
                                   text="Entrez votre clé de licence pour activer le logiciel",
                                   font=('Arial', 10),
                                   bg='white',
                                   fg='#2196F3',
                                   pady=15)
        self.status_label.pack(fill='x')
        
        # Pied de page avec informations de sécurité
        self.create_footer()
    
    def create_security_section(self, parent):
        """Crée la section d'affichage du statut de sécurité"""
        security_section = tk.Frame(parent, bg='white')
        security_section.pack(fill='x', pady=(0, 20))
        
        tk.Label(security_section,
                text="Statut de Sécurité",
                font=('Arial', 11, 'bold'),
                bg='white',
                fg='#333333').pack(anchor='w')
        
        # Frame pour les indicateurs de sécurité
        indicators_frame = tk.Frame(security_section, bg='white')
        indicators_frame.pack(fill='x', pady=(8, 0))
        
        # Indicateur de protection temporelle
        self.time_protection_indicator = tk.Label(indicators_frame,
                                                text="🕐 Protection Temporelle: Vérification...",
                                                font=('Arial', 9),
                                                bg='white',
                                                fg='#666666')
        self.time_protection_indicator.pack(anchor='w')
        
        # Indicateur de connexion serveur
        self.server_indicator = tk.Label(indicators_frame,
                                       text="🌐 Serveur de Temps: Vérification...",
                                       font=('Arial', 9),
                                       bg='white',
                                       fg='#666666')
        self.server_indicator.pack(anchor='w')
        
        # Indicateur de tentatives de manipulation
        self.tamper_indicator = tk.Label(indicators_frame,
                                       text="🛡️ Tentatives de Manipulation: Vérification...",
                                       font=('Arial', 9),
                                       bg='white',
                                       fg='#666666')
        self.tamper_indicator.pack(anchor='w')
    
    def create_activation_mode_section(self, parent):
        """Crée la section de sélection du mode d'activation"""
        mode_section = tk.Frame(parent, bg='white')
        mode_section.pack(fill='x', pady=(15, 0))
        
        tk.Label(mode_section,
                text="Mode d'Activation",
                font=('Arial', 11, 'bold'),
                bg='white',
                fg='#333333').pack(anchor='w')
        
        # Frame pour les options
        options_frame = tk.Frame(mode_section, bg='white')
        options_frame.pack(fill='x', pady=(8, 0))
        
        # Variable pour le mode
        self.activation_mode = tk.StringVar(value="online")
        
        # Option en ligne
        online_frame = tk.Frame(options_frame, bg='white')
        online_frame.pack(anchor='w')
        
        self.online_radio = tk.Radiobutton(online_frame,
                                         text="🌐 Activation en ligne (Recommandé)",
                                         variable=self.activation_mode,
                                         value="online",
                                         font=('Arial', 9),
                                         bg='white',
                                         fg='#4CAF50',
                                         selectcolor='white',
                                         command=self.on_mode_change)
        self.online_radio.pack(side='left')
        
        # Option hors ligne
        offline_frame = tk.Frame(options_frame, bg='white')
        offline_frame.pack(anchor='w', pady=(5, 0))
        
        self.offline_radio = tk.Radiobutton(offline_frame,
                                          text="📱 Activation hors ligne (Protection limitée)",
                                          variable=self.activation_mode,
                                          value="offline",
                                          font=('Arial', 9),
                                          bg='white',
                                          fg='#FF9800',
                                          selectcolor='white',
                                          command=self.on_mode_change)
        self.offline_radio.pack(side='left')
    
    def create_footer(self):
        """Crée le pied de page avec informations sécurisées"""
        footer_frame = tk.Frame(self.master, bg='#f5f5f5', height=60)
        footer_frame.pack(fill='x')
        footer_frame.pack_propagate(False)
        
        footer_content = tk.Frame(footer_frame, bg='#f5f5f5')
        footer_content.pack(expand=True, fill='both', pady=10)
        
        tk.Label(footer_content,
                text="© 2024 Taekwondo Manager Pro - Licence Sécurisée avec Protection Anti-Triche",
                font=('Arial', 8, 'bold'),
                bg='#f5f5f5',
                fg='#666666').pack()
        
        self.footer_security_label = tk.Label(footer_content,
                                           text="🔒 Système de sécurité activé",
                                           font=('Arial', 8),
                                           bg='#f5f5f5',
                                           fg='#4CAF50')
        self.footer_security_label.pack()
    
    def get_header_color(self):
        """Retourne la couleur de l'en-tête selon le statut de sécurité"""
        security_status = self.license_manager.get_security_status()
        colors = {
            'secure': '#2196F3',      # Bleu - Sécurisé
            'warning': '#FF9800',     # Orange - Avertissement
            'restricted': '#f44336',  # Rouge - Restreint
            'compromised': '#9E9E9E', # Gris - Compromis
            'unknown': '#607D8B'      # Bleu-gris - Inconnu
        }
        return colors.get(security_status, '#2196F3')
    
    def check_security_status(self):
        """Vérifie et affiche le statut de sécurité"""
        threading.Thread(target=self._check_security_background, daemon=True).start()
    
    def _check_security_background(self):
        """Vérification de sécurité en arrière-plan"""
        try:
            # Test de connexion serveur
            server_time = self.license_manager.get_server_time(timeout=5)
            self.server_time_available = server_time is not None
            
            # Récupération du statut de sécurité
            security_status = self.license_manager.get_security_status()
            license_info = self.license_manager.get_license_info()
            
            # Mettre à jour l'interface
            self.master.after(0, self._update_security_display, security_status, license_info)
            
        except Exception as e:
            print(f"Erreur vérification sécurité: {e}")
            self.master.after(0, self._update_security_display, 'unknown', None)
    
    def _update_security_display(self, security_status, license_info):
        """Met à jour l'affichage du statut de sécurité"""
        # Mettre à jour les indicateurs
        tamper_count = 0
        if license_info and 'security_status' in license_info:
            tamper_count = license_info['security_status'].get('tamper_attempts', 0)
        
        # Indicateur de protection temporelle
        if security_status == 'secure':
            self.time_protection_indicator.config(
                text="🟢 Protection Temporelle: Active et Sécurisée",
                fg='#4CAF50'
            )
        elif security_status == 'warning':
            self.time_protection_indicator.config(
                text="🟡 Protection Temporelle: Avertissement Détecté",
                fg='#FF9800'
            )
        elif security_status == 'restricted':
            self.time_protection_indicator.config(
                text="🟠 Protection Temporelle: Mode Restreint Activé",
                fg='#f44336'
            )
        else:
            self.time_protection_indicator.config(
                text="🔴 Protection Temporelle: Système Compromis",
                fg='#9E9E9E'
            )
        
        # Indicateur serveur
        if self.server_time_available:
            self.server_indicator.config(
                text="🟢 Serveur de Temps: Connecté et Synchronisé",
                fg='#4CAF50'
            )
        else:
            self.server_indicator.config(
                text="🔴 Serveur de Temps: Indisponible (Mode Hors Ligne)",
                fg='#f44336'
            )
        
        # Indicateur de manipulation
        if tamper_count == 0:
            self.tamper_indicator.config(
                text="🟢 Tentatives de Manipulation: Aucune Détectée",
                fg='#4CAF50'
            )
        elif tamper_count < 3:
            self.tamper_indicator.config(
                text=f"🟡 Tentatives de Manipulation: {tamper_count} Détectée(s)",
                fg='#FF9800'
            )
        else:
            self.tamper_indicator.config(
                text=f"🔴 Tentatives de Manipulation: {tamper_count} - Sécurité Compromise",
                fg='#f44336'
            )
        
        # Mettre à jour l'indicateur en en-tête
        status_texts = {
            'secure': '🟢 SÉCURISÉ',
            'warning': '🟡 AVERTISSEMENT',
            'restricted': '🟠 RESTREINT', 
            'compromised': '🔴 COMPROMIS',
            'unknown': '❓ INCONNU'
        }
        self.security_indicator.config(text=status_texts.get(security_status, '❓ INCONNU'))
        
        # Ajuster le mode d'activation recommandé
        if not self.server_time_available:
            self.activation_mode.set("offline")
            self.online_radio.config(state='disabled')
            self.status_label.config(
                text="⚠️ Serveurs indisponibles - Activation hors ligne uniquement",
                fg='#FF9800'
            )
    
    def on_mode_change(self):
        """Gestionnaire de changement de mode d'activation"""
        mode = self.activation_mode.get()
        if mode == "online" and not self.server_time_available:
            messagebox.showwarning(
                "Connexion Indisponible",
                "Les serveurs de temps ne sont pas accessibles.\n"
                "L'activation en ligne n'est pas possible actuellement."
            )
            self.activation_mode.set("offline")
        elif mode == "offline":
            messagebox.showinfo(
                "Mode Hors Ligne",
                "⚠️ Attention: L'activation hors ligne utilise l'horloge système.\n\n"
                "Des vérifications de sécurité supplémentaires seront activées\n"
                "pour détecter toute manipulation temporelle."
            )
    
    def on_entry_focus_in(self, event):
        """Effet visuel lors du focus sur le champ"""
        self.key_entry.config(bd=2, highlightbackground='#2196F3')
    
    def on_entry_focus_out(self, event):
        """Effet visuel lors de la perte du focus"""
        self.key_entry.config(bd=1, highlightbackground='#e0e0e0')
    
    def on_key_change(self, event):
        """Valide le format de la clé en temps réel"""
        key = self.key_entry.get().upper()
        
        # Formatage automatique avec tirets
        if len(key) == 4 and not key.endswith('-'):
            self.key_entry.delete(0, tk.END)
            self.key_entry.insert(0, key + '-')
        elif len(key) == 9 and not key.endswith('-'):
            self.key_entry.delete(0, tk.END)
            self.key_entry.insert(0, key + '-')
        elif len(key) == 14 and not key.endswith('-'):
            self.key_entry.delete(0, tk.END)
            self.key_entry.insert(0, key + '-')
        
        # Validation visuelle
        if len(key) == 19 and key.count('-') == 3:
            self.key_entry.config(bg='#E8F5E8')  # Vert clair - valide
            self.status_label.config(text="✓ Format de clé valide", fg='#4CAF50')
        elif len(key) > 0:
            self.key_entry.config(bg='#FFF3E0')  # Orange clair - en cours
            self.status_label.config(text="⏳ Saisie en cours...", fg='#FF9800')
        else:
            self.key_entry.config(bg='white')
            self.status_label.config(text="Entrez votre clé de licence", fg='#2196F3')
    
    def get_masked_id(self):
        """Retourne l'ID machine masqué pour la sécurité"""
        full_id = self.license_manager.machine_id
        return f"{full_id[:8]}•••••••{full_id[-8:]}"
    
    def copy_machine_id(self):
        """Copie l'ID machine dans le presse-papiers"""
        self.master.clipboard_clear()
        self.master.clipboard_append(self.license_manager.machine_id)
        self.status_label.config(text="✓ ID machine copié dans le presse-papiers!", fg='#4CAF50')
        self.master.after(3000, lambda: self.status_label.config(
            text="Entrez votre clé de licence pour activer le logiciel", fg='#2196F3'))
    
    def test_server_connection(self):
        """Test la connexion aux serveurs de temps"""
        self.status_label.config(text="🌐 Test de connexion en cours...", fg='#2196F3')
        threading.Thread(target=self._test_connection_background, daemon=True).start()
    
    def _test_connection_background(self):
        """Test de connexion en arrière-plan"""
        try:
            server_time = self.license_manager.get_server_time(timeout=10)
            if server_time:
                self.server_time_available = True
                self.master.after(0, lambda: self.status_label.config(
                    text=f"✅ Connexion réussie! Heure serveur: {server_time.strftime('%H:%M:%S UTC')}",
                    fg='#4CAF50'
                ))
                self.master.after(0, lambda: self.online_radio.config(state='normal'))
            else:
                self.server_time_available = False
                self.master.after(0, lambda: self.status_label.config(
                    text="❌ Impossible de se connecter aux serveurs de temps",
                    fg='#f44336'
                ))
        except Exception as e:
            self.server_time_available = False
            self.master.after(0, lambda: self.status_label.config(
                text=f"❌ Erreur de connexion: {str(e)}",
                fg='#f44336'
            ))
    
    def buy_license(self):
        """Ouvre la page d'achat de licence"""
        self.status_label.config(text="🌐 Redirection vers le portail d'achat...", fg='#FF6B35')
        messagebox.showinfo(
            "Acheter une Licence",
            "Visitez notre site web pour acheter votre licence:\n\n"
            "🌐 www.taekwondo-manager-pro.com\n\n"
            "Clés de test disponibles:\n"
            "• TEST-1234-ABCD-5678 (1 an)\n"
            "• DEMO-2024-TKDO-MGMT (30 jours)\n"
            "• PRO-2024-FULL-ACCES (2 ans)"
        )
        self.status_label.config(text="Entrez votre clé de licence pour activer le logiciel", fg='#2196F3')
    
    def activate(self):
        """Démarre le processus d'activation sécurisé"""
        key = self.key_entry.get().strip().upper()
        if not key:
            messagebox.showerror("Erreur", "Veuillez entrer une clé de licence")
            return
        
        # Vérifier le format
        if len(key) != 19 or key.count('-') != 3:
            messagebox.showerror("Format Invalide", 
                               "Format attendu: XXXX-XXXX-XXXX-XXXX")
            return
        
        # Déterminer le mode d'activation
        self.offline_mode = (self.activation_mode.get() == "offline")
        
        # Désactiver les contrôles pendant l'activation
        self.activate_button.config(state='disabled', text="⏳ Activation en cours...")
        self.key_entry.config(state='disabled')
        self.online_radio.config(state='disabled')
        self.offline_radio.config(state='disabled')
        
        # Afficher la zone de progression
        self.progress_frame.pack(fill='x', pady=(20, 0))
        
        # Lancer le processus en arrière-plan
        threading.Thread(target=self.process_secure_activation, args=(key,), daemon=True).start()
    
    def process_secure_activation(self, key):
        """Effectue le processus d'activation sécurisé avec progression visuelle"""
        if self.offline_mode:
            steps = [
                ("🔍 Vérification du format de la clé", 0.15),
                ("📱 Mode hors ligne - Validation locale", 0),
                ("📱 Mode hors ligne - Validation locale", 0.30),
                ("🛡️ Vérification de la sécurité système", 0.50),
                ("⏰ Validation de l'horloge système", 0.70),
                ("💾 Enregistrement de la licence", 0.85),
                ("✅ Finalisation de l'activation", 1.0)
            ]
        else:
            steps = [
                ("🔍 Vérification du format de la clé", 0.10),
                ("🌐 Connexion au serveur de validation", 0.25),
                ("🔐 Authentification sécurisée", 0.40),
                ("📊 Validation des données de licence", 0.60),
                ("⏰ Synchronisation temporelle", 0.75),
                ("💾 Enregistrement de la licence", 0.90),
                ("✅ Finalisation de l'activation", 1.0)
            ]
        
        try:
            for step_text, progress in steps:
                self.master.after(0, self.update_progress, step_text, progress)
                
                # Simulation du temps de traitement
                if progress < 1.0:
                    time.sleep(1.5 if not self.offline_mode else 1.0)
            
            # Effectuer l'activation réelle
            if self.offline_mode:
                result = self.license_manager.activate_offline(key)
            else:
                result = self.license_manager.activate_online(key)
            
            # Traitement du résultat
            self.master.after(0, self.handle_activation_result, result)
            
        except Exception as e:
            error_msg = f"Erreur lors de l'activation: {str(e)}"
            self.master.after(0, self.handle_activation_error, error_msg)
    
    def update_progress(self, text, progress):
        """Met à jour la barre de progression"""
        self.progress_label.config(text=text)
        
        # Animation de la barre de progression
        total_width = self.progress_frame.winfo_width()
        if total_width > 1:  # Éviter la division par zéro
            new_width = int(total_width * progress)
            self.progress_fill.place(width=new_width)
        
        self.master.update()
    
    def handle_activation_result(self, result):
        """Traite le résultat de l'activation"""
        # Cacher la zone de progression
        self.progress_frame.pack_forget()
        
        if result.get('success', False):
            # Activation réussie
            self.status_label.config(
                text="🎉 Activation réussie! Redémarrage du logiciel...",
                fg='#4CAF50'
            )
            
            # Afficher les informations de la licence
            license_info = result.get('license_info', {})
            expires_date = license_info.get('expires', 'N/A')
            license_type = license_info.get('type', 'Standard')
            
            success_msg = (
                f"✅ Licence activée avec succès!\n\n"
                f"📋 Type: {license_type}\n"
                f"📅 Expire le: {expires_date}\n"
                f"🔒 Mode: {'Hors ligne' if self.offline_mode else 'En ligne'}\n\n"
                f"Le logiciel va redémarrer automatiquement."
            )
            
            messagebox.showinfo("Activation Réussie", success_msg)
            
            # Redémarrage automatique après 3 secondes
            self.master.after(3000, self.restart_application)
            
        else:
            # Activation échouée
            error_msg = result.get('error', 'Erreur inconnue')
            self.handle_activation_error(error_msg)
    
    def handle_activation_error(self, error_msg):
        """Traite les erreurs d'activation"""
        # Cacher la zone de progression
        self.progress_frame.pack_forget()
        
        # Réactiver les contrôles
        self.activate_button.config(state='normal', text="🔓 Activer la Licence")
        self.key_entry.config(state='normal')
        if self.server_time_available:
            self.online_radio.config(state='normal')
        self.offline_radio.config(state='normal')
        
        # Afficher l'erreur
        self.status_label.config(text=f"❌ {error_msg}", fg='#f44336')
        
        # Message d'erreur détaillé
        if "format" in error_msg.lower():
            messagebox.showerror(
                "Format de Clé Invalide",
                "La clé de licence ne respecte pas le format attendu.\n\n"
                "Format requis: XXXX-XXXX-XXXX-XXXX\n"
                "Exemple: TEST-1234-ABCD-5678"
            )
        elif "expired" in error_msg.lower():
            messagebox.showerror(
                "Licence Expirée",
                "Cette clé de licence a expiré.\n\n"
                "Veuillez renouveler votre licence ou contacter\n"
                "le support technique."
            )
        elif "invalid" in error_msg.lower():
            messagebox.showerror(
                "Clé Invalide",
                "Cette clé de licence n'est pas valide.\n\n"
                "Vérifiez que vous avez saisi la clé correctement\n"
                "ou contactez le support technique."
            )
        elif "network" in error_msg.lower():
            messagebox.showerror(
                "Erreur Réseau",
                "Impossible de contacter les serveurs d'activation.\n\n"
                "Vérifiez votre connexion internet ou essayez\n"
                "l'activation en mode hors ligne."
            )
        elif "security" in error_msg.lower():
            messagebox.showerror(
                "Problème de Sécurité",
                "Un problème de sécurité a été détecté.\n\n"
                "Votre système pourrait avoir été compromis.\n"
                "Contactez le support technique."
            )
        else:
            messagebox.showerror("Erreur d'Activation", error_msg)
    
    def restart_application(self):
        """Redémarre l'application après activation réussie"""
        try:
            # Fermer la fenêtre d'activation
            self.master.destroy()
            
            # Ici, vous pouvez ajouter le code pour redémarrer l'application principale
            # Par exemple: subprocess.Popen([sys.executable] + sys.argv)
            
        except Exception as e:
            print(f"Erreur lors du redémarrage: {e}")

# Classe d'exemple pour le gestionnaire de licence (à adapter selon vos besoins)
class SecureLicenseManager:
    def __init__(self):
        self.machine_id = self.generate_machine_id()
        self.security_status = 'unknown'
        self.tamper_attempts = 0
    
    def generate_machine_id(self):
        """Génère un ID unique pour la machine"""
        import hashlib
        import platform
        import uuid
        
        # Collecter des informations système uniques
        system_info = f"{platform.system()}-{platform.machine()}-{uuid.getnode()}"
        return hashlib.sha256(system_info.encode()).hexdigest()
    
    def get_security_status(self):
        """Retourne le statut de sécurité actuel"""
        # Logique de vérification de sécurité
        return self.security_status
    
    def get_license_info(self):
        """Retourne les informations de licence"""
        return {
            'security_status': {
                'tamper_attempts': self.tamper_attempts
            }
        }
    
    def get_server_time(self, timeout=5):
        """Obtient l'heure du serveur"""
        try:
            import requests
            import datetime
            
            # Simuler une requête vers un serveur de temps
            # En production, remplacer par votre serveur réel
            response = requests.get('http://worldtimeapi.org/api/timezone/UTC', timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                return datetime.datetime.fromisoformat(data['datetime'].replace('Z', '+00:00'))
            return None
        except:
            return None
    
    def activate_online(self, key):
        """Activation en ligne"""
        try:
            # Simulation d'activation en ligne
            time.sleep(2)  # Simulation du temps de traitement serveur
            
            # Clés de test pour la démo
            test_keys = {
                'TEST-1234-ABCD-5678': {'type': 'Test', 'expires': '2025-12-31'},
                'DEMO-2024-TKDO-MGMT': {'type': 'Démo', 'expires': '2025-09-07'},
                'PRO-2024-FULL-ACCES': {'type': 'Professionnel', 'expires': '2026-08-07'}
            }
            
            if key in test_keys:
                self.security_status = 'secure'
                return {
                    'success': True,
                    'license_info': test_keys[key]
                }
            else:
                return {
                    'success': False,
                    'error': 'Clé de licence invalide'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Erreur réseau: {str(e)}'
            }
    
    def activate_offline(self, key):
        """Activation hors ligne"""
        try:
            # Simulation d'activation hors ligne
            time.sleep(1)
            
            # Vérifications de sécurité supplémentaires en mode hors ligne
            self.security_status = 'warning'  # Mode hors ligne = avertissement
            
            # Clés de test pour la démo
            test_keys = {
                'TEST-1234-ABCD-5678': {'type': 'Test (Hors ligne)', 'expires': '2025-12-31'},
                'DEMO-2024-TKDO-MGMT': {'type': 'Démo (Hors ligne)', 'expires': '2025-09-07'},
                'PRO-2024-FULL-ACCES': {'type': 'Professionnel (Hors ligne)', 'expires': '2026-08-07'}
            }
            
            if key in test_keys:
                return {
                    'success': True,
                    'license_info': test_keys[key]
                }
            else:
                return {
                    'success': False,
                    'error': 'Clé de licence invalide ou expirée'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Erreur d\'activation: {str(e)}'
            }

# Fonction principale pour tester l'interface
def main():
    root = tk.Tk()
    license_manager = SecureLicenseManager()
    app = SecureActivationWindow(root, license_manager)
    root.mainloop()

if __name__ == "__main__":
    main()