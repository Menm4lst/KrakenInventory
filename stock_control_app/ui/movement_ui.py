import tkinter as tk
from tkinter import ttk

class MovementUI:
	def __init__(self, parent, read_only=False):
		self.frame = ttk.Frame(parent)
		label = ttk.Label(self.frame, text="Movimientos (implementación básica)")
		label.pack(padx=10, pady=10)
