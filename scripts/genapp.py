import tkinter as tk
from tkinter import ttk, filedialog
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Генерація текстури ---
def generate_texture(event=None):
    size = 1920

    noise_large = np.random.rand(size, size)
    noise_medium = np.random.rand(size, size)
    noise_small = np.random.rand(size, size)

    sigma_large = sigma_large_var.get()
    sigma_medium = sigma_medium_var.get()
    sigma_small = sigma_small_var.get()

    weight_large = weight_large_var.get()
    weight_medium = weight_medium_var.get()
    weight_small = weight_small_var.get()

    r_mult = red_multiplier_var.get()
    g_mult = green_multiplier_var.get()
    b_mult = blue_multiplier_var.get()

    blurred_large = gaussian_filter(noise_large, sigma=sigma_large)
    blurred_medium = gaussian_filter(noise_medium, sigma=sigma_medium)
    blurred_small = gaussian_filter(noise_small, sigma=sigma_small)

    blurred_large = (blurred_large - blurred_large.min()) / (blurred_large.max() - blurred_large.min())
    blurred_medium = (blurred_medium - blurred_medium.min()) / (blurred_medium.max() - blurred_medium.min())
    blurred_small = (blurred_small - blurred_small.min()) / (blurred_small.max() - blurred_small.min())

    mix = weight_large * blurred_large + weight_medium * blurred_medium + weight_small * blurred_small

    global image
    image = np.zeros((size, size, 3))
    image[:, :, 0] = r_mult * mix
    image[:, :, 1] = g_mult * mix
    image[:, :, 2] = b_mult * mix

    image = np.clip(image, 0, 1)

    ax.clear()
    ax.imshow(image)
    ax.axis('off')
    canvas.draw()

# --- Збереження зображення ---
def save_image():
    file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG files", "*.png")])
    if file_path:
        plt.imsave(file_path, image)

# --- Побудова інтерфейсу ---
root = tk.Tk()
root.title("Генератор текстур")
root.geometry("1000x600")
root.columnconfigure(1, weight=1)
root.rowconfigure(0, weight=1)

# Параметри
sigma_large_var = tk.DoubleVar(value=30)
sigma_medium_var = tk.DoubleVar(value=50)
sigma_small_var = tk.DoubleVar(value=70)

weight_large_var = tk.DoubleVar(value=0.5)
weight_medium_var = tk.DoubleVar(value=0.3)
weight_small_var = tk.DoubleVar(value=0.2)

red_multiplier_var = tk.DoubleVar(value=0.3)
green_multiplier_var = tk.DoubleVar(value=0.7)
blue_multiplier_var = tk.DoubleVar(value=0.2)

# Контейнер для контролів
control_frame = ttk.Frame(root, padding=10)
control_frame.grid(row=0, column=0, sticky="ns")

# Слайдери з підписами
params = [
    ("Sigma Large", sigma_large_var, 1, 100),
    ("Sigma Medium", sigma_medium_var, 1, 100),
    ("Sigma Small", sigma_small_var, 1, 100),
    ("Weight Large", weight_large_var, 0, 1),
    ("Weight Medium", weight_medium_var, 0, 1),
    ("Weight Small", weight_small_var, 0, 1),
    ("Red Multiplier", red_multiplier_var, 0, 1),
    ("Green Multiplier", green_multiplier_var, 0, 1),
    ("Blue Multiplier", blue_multiplier_var, 0, 1),
]

value_labels = []

for idx, (label, var, minval, maxval) in enumerate(params):
    ttk.Label(control_frame, text=label).grid(row=idx, column=0, sticky="w")
    scale = ttk.Scale(control_frame, from_=minval, to=maxval, variable=var,
                      orient="horizontal", command=generate_texture)
    scale.grid(row=idx, column=1, sticky="ew", padx=5)

    value_label = ttk.Label(control_frame, text=f"{var.get():.2f}")
    value_label.grid(row=idx, column=2, sticky="e")
    value_labels.append((var, value_label))

# Оновлення числових значень кожні 100 мс
def update_values():
    for var, label in value_labels:
        label.config(text=f"{var.get():.2f}")
    root.after(100, update_values)

update_values()

# Кнопка збереження
save_button = ttk.Button(control_frame, text="Зберегти зображення", command=save_image)
save_button.grid(row=len(params), column=0, columnspan=3, pady=10)

# Полотно для малювання
figure_frame = ttk.Frame(root)
figure_frame.grid(row=0, column=1, sticky="nsew")
figure_frame.rowconfigure(0, weight=1)
figure_frame.columnconfigure(0, weight=1)

fig, ax = plt.subplots(figsize=(6, 6))
canvas = FigureCanvasTkAgg(fig, master=figure_frame)
canvas_widget = canvas.get_tk_widget()
canvas_widget.grid(row=0, column=0, sticky="nsew")

generate_texture()
root.mainloop()
