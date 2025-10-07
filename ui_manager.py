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
from match_config_dialog import MatchConfigDialog


if __name__ == "__main__":
    root = tk.Tk()
    app = TaekwondoInterface(root)
    root.mainloop()