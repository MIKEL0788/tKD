import tkinter as tk
from tkinter import ttk
from ui_manager import TaekwondoInterface
from license_manager import ModernLicenseManager
from activation_window import SecureActivationWindow
from spash_screen import ModernSplashScreen
import sys
import time

def launch_main_app():
    """Lance l'application principale avec une interface moderne"""
    root = tk.Tk()
    root.title("Gestionnaire Taekwondo Pro")
    root.geometry("1200x800")
    root.configure(bg='#f5f5f5')
    
    # Centrer la fenêtre principale
    center_window(root, 1200, 800)
    
    # Créer l'interface principale
    app = TaekwondoInterface(root)
    
    # Définir le mode tournoi par défaut au démarrage
    app.match_mode = "tournoi"
    
    # Afficher la fenêtre de configuration avec priorité au tournoi
    root.after(500, lambda: app.show_configuration_dialog())
    
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

def center_window(window, width, height):
    """Centre une fenêtre sur l'écran"""
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight() 
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

def show_splash_and_check_license():
    """Affiche le splash screen et vérifie la licence"""
    # Vérifier la licence en arrière-plan
    manager = ModernLicenseManager()
    
    # Créer la fenêtre principale cachée pour le splash
    root = tk.Tk()
    root.withdraw()  # Cacher la fenêtre principale
    
    # Créer et afficher le splash screen
    splash = ModernSplashScreen(root)
    splash_window = splash.show()

    
    # s'assurer que la fenettre splash se ferme automatiquement
    root.after(5000,splash.close_splash)
    
    # Attendre que le splash se ferme
    root.wait_window(splash_window)
    
    # Fermer la fenêtre racine temporaire
    root.destroy()
    
    return manager

if __name__ == "__main__":
    try:
        # Afficher le splash screen et vérifier la licence
        manager = show_splash_and_check_license()
        
        # Lancer l'application ou l'activation selon l'état de la licence
        if manager.is_valid():
            print("Licence valide - Lancement de l'application principale")
            launch_main_app()
        else:
            print("Licence non valide - Affichage de la fenêtre d'activation")
            # Créer la fenêtre d'activation
            activation_root = tk.Tk()
            app = SecureActivationWindow(activation_root, manager)
            activation_root.mainloop()
    
    except Exception as e:
        # En cas d'erreur, afficher un message et quitter proprement
        root = tk.Tk()
        root.withdraw()
        tk.messagebox.showerror(
            "Erreur de démarrage",
            f"Une erreur s'est produite lors du démarrage de l'application:\n\n{str(e)}"
        )
        root.destroy()
        sys.exit(1)