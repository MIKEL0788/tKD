import tkinter as tk
import time

class ModernSplashScreen:
    def __init__(self, root):
        self.root = root
        self.splash = tk.Toplevel(root)
        self.splash.title("")
        
        # Configuration de base
        self.splash.configure(bg='#1a1a1a')
        self.splash.resizable(False, False)
        
        # Taille fixe du splash
        self.width = 600
        self.height = 350
        
        # IMPORTANT: Centrer AVANT d'appliquer overrideredirect
        self.center_window_properly()
        
        # Maintenant on peut supprimer la barre de titre
        self.splash.overrideredirect(True)
        
        # Variables d'animation
        self.progress_value = 0
        self.dot_count = 0
        
        # Création interface
        self.create_interface()
        
        # Lancement animation
        self.splash.after(100, self.animate_progress)

    def center_window_properly(self):
        """Centre la fenêtre CORRECTEMENT en plusieurs étapes"""
        # Étape 1: Créer la géométrie de base
        self.splash.geometry(f"{self.width}x{self.height}")
        
        # Étape 2: Forcer la mise à jour pour obtenir les vraies dimensions
        self.splash.update_idletasks()
        self.splash.update()
        
        # Étape 3: Calculer le centre de l'écran
        screen_width = self.splash.winfo_screenwidth()
        screen_height = self.splash.winfo_screenheight()
        
        # Position centrée
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        
        # Étape 4: Appliquer la position centrée
        self.splash.geometry(f"{self.width}x{self.height}+{x}+{y}")
        
        # Étape 5: Une dernière mise à jour pour être sûr
        self.splash.update_idletasks()

    def create_interface(self):
        # Container principal qui s'étend sur toute la fenêtre
        main_container = tk.Frame(self.splash, bg='#1a1a1a')
        main_container.pack(fill='both', expand=True)
        
        # Configuration de la grille pour centrage parfait
        main_container.grid_rowconfigure(0, weight=1)    # Espace supérieur
        main_container.grid_rowconfigure(1, weight=0)    # Contenu principal
        main_container.grid_rowconfigure(2, weight=1)    # Espace inférieur
        main_container.grid_columnconfigure(0, weight=1) # Centrage horizontal
        
        # Frame de contenu principal centré
        content_frame = tk.Frame(main_container, bg='#1a1a1a')
        content_frame.grid(row=1, column=0, padx=40, pady=20)
        
        # Container horizontal pour logo + informations
        info_container = tk.Frame(content_frame, bg='#1a1a1a')
        info_container.pack()
        
        # Section logo (gauche)
        logo_frame = tk.Frame(info_container, bg='#1a1a1a')
        logo_frame.pack(side='left', padx=(0, 40))
        
        # Création d'une image de logo par défaut si le fichier n'existe pas
        try:
            self.logo_image = tk.PhotoImage(file="logo_eveil.png")
        except:
            # Créer une image de remplacement si logo.png n'existe pas
            self.logo_image = tk.PhotoImage(width=100, height=100)
            # Dessiner un simple rectangle vert comme placeholder
            self.logo_image.put("#4CAF50", to=(10, 10, 90, 90))
        
        self.logo_label = tk.Label(
            logo_frame,
            image=self.logo_image,
            bg='#1a1a1a'
        )
        self.logo_label.pack()
        
        # Section informations (droite)
        info_frame = tk.Frame(info_container, bg='#1a1a1a')
        info_frame.pack(side='right', anchor='n')
        
        # Titre principal
        title_label = tk.Label(
            info_frame,
            text="Bienvenue dans TKD EVEIL",
            font=("Helvetica", 20, "bold"),
            bg='#1a1a1a',
            fg='#4CAF50'
        )
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Sous-titre
        subtitle_label = tk.Label(
            info_frame,
            text="Logiciel Professionnel de Gestion\nde Compétitions Taekwondo",
            font=("Helvetica", 12),
            bg='#1a1a1a',
            fg='#CCCCCC',
            justify='left'
        )
        subtitle_label.pack(anchor='w', pady=(0, 30))
        
        # Container pour la progression
        progress_container = tk.Frame(info_frame, bg='#1a1a1a')
        progress_container.pack(fill='x', pady=(0, 15))
        
        # Barre de progression avec dimensions fixes
        progress_bg_frame = tk.Frame(progress_container, bg='#1a1a1a', width=300, height=8)
        progress_bg_frame.pack(anchor='w')
        progress_bg_frame.pack_propagate(False)
        
        # Arrière-plan de la barre
        self.progress_bg = tk.Frame(progress_bg_frame, bg='#333333', height=6)
        self.progress_bg.place(x=0, y=1, width=300, height=6)
        
        # Barre de progression active
        self.progress_bar = tk.Frame(self.progress_bg, bg='#4CAF50', height=6)
        self.progress_bar.place(x=0, y=0, width=0, height=6)
        
        # Texte de chargement
        self.loading_label = tk.Label(
            info_frame,
            text="Chargement",
            font=("Arial", 10),
            bg='#1a1a1a',
            fg='#999999'
        )
        self.loading_label.pack(anchor='w')
        
        # Pied de page
        footer_label = tk.Label(
            main_container,
            text="© 2025 TK-WIN | Tous droits réservés",
            font=("Arial", 8),
            bg='#1a1a1a',
            fg='#666666'
        )
        footer_label.grid(row=2, column=0, sticky='s', pady=(0, 15))

    def animate_progress(self):
        if self.progress_value <= 100:
            # Mise à jour de la barre de progression
            progress_width = int((self.progress_value / 100) * 300)
            self.progress_bar.place(width=progress_width)
            
            # Animation du texte de chargement
            self.dot_count = (self.dot_count + 1) % 4
            dots = "." * self.dot_count
            loading_text = f"Chargement{dots}"
            self.loading_label.config(text=loading_text)
            
            # Progression
            self.progress_value += 1.8
            self.splash.after(45, self.animate_progress)
        else:
            # Progression terminée
            self.loading_label.config(text="Terminé !")
            self.splash.after(800, self.close_splash)

    def close_splash(self):
        try:
            self.splash.destroy()
        except tk.TclError:
            pass  # Fenêtre déjà fermée

    def show(self):
        # S'assurer que la fenêtre est visible et au premier plan
        self.splash.deiconify()
        self.splash.lift()
        self.splash.attributes('-topmost', True)
        
        # Permettre le clic pour fermer
        self.splash.bind("<Button-1>", lambda e: self.close_splash())
        
        return self.splash


# Test de la classe
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Masquer la fenêtre principale
    
    # Créer et afficher le splash screen
    splash = ModernSplashScreen(root)
    splash.show()
    
    # Démarrer la boucle principale
    root.mainloop()