import tkinter as tk
from tkinter import ttk, filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

try:
    import cupy as cp
    use_gpu = True
    print("Using GPU acceleration with CuPy.")
except ImportError:
    import numpy as cp
    use_gpu = False
    print("Using CPU with NumPy. CuPy not found.")

from noise import pnoise2  

size = 700  # Розмір текстури
image = None  # Зображення для експорту

def generate_fractal_noise(width, height, scale, octaves, persistence=0.5, lacunarity=2.0, seed=0):
    noise = np.zeros((height, width), dtype=np.float32)
    for y in range(height):
        for x in range(width):
            noise[y, x] = pnoise2(
                x / scale,
                y / scale,
                octaves=octaves,
                persistence=persistence,
                lacunarity=lacunarity,
                repeatx=width,
                repeaty=height,
                base=seed
            )
    return (noise + 0.5)  # Переводимо в діапазон 0..1

def generate_texture(event=None):
    global image

    def normalize(x):
        return (x - cp.min(x)) / (cp.max(x) - cp.min(x) + 1e-8)

    # Отримуємо параметри з інтерфейсу
    octaves = int(octaves_var.get())
    scale = float(perlin_scale_var.get())
    seed = int(seed_var.get())

    r_mult = float(red_multiplier_var.get())
    g_mult = float(green_multiplier_var.get())
    b_mult = float(blue_multiplier_var.get())

    # Генеруємо фрактальний шум для кожного каналу з різними seed
    def make_cloud(seed_offset):
        data = generate_fractal_noise(
            width=size,
            height=size,
            scale=scale,
            octaves=octaves,
            persistence=0.5,
            lacunarity=2.0,
            seed=seed + seed_offset
        )
        return cp.array(data)

    r_layer = make_cloud(1) * r_mult
    g_layer = make_cloud(2) * g_mult
    b_layer = make_cloud(3) * b_mult

    # Об'єднуємо канали
    image = cp.stack([r_layer, g_layer, b_layer], axis=-1)
    image = cp.clip(image, 0, 1)

    image_np = cp.asnumpy(image)

    ax.clear()
    ax.imshow(image_np)
    ax.axis('off')
    canvas.draw()

    update_labels()

def update_labels():
    for var, label in label_vars:
        label.config(text=f"{var.get():.2f}")

def save_image():
    if image is not None:
        path = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG Files", "*.png")],
                                             initialfile="texture.png")
        if path:
            plt.imsave(path, cp.asnumpy(image))
            print(f"Image saved to {path}")

# --- Інтерфейс ---
root = tk.Tk()
root.title("Генератор фрактальних текстур")
root.geometry("1000x600")
root.columnconfigure(1, weight=1)
root.rowconfigure(0, weight=1)

# Змінні параметрів
octaves_var = tk.IntVar(value=4)
perlin_scale_var = tk.DoubleVar(value=100)
seed_var = tk.IntVar(value=0)

red_multiplier_var = tk.DoubleVar(value=0.5)
green_multiplier_var = tk.DoubleVar(value=0.5)
blue_multiplier_var = tk.DoubleVar(value=0.5)

params = [
    ("Octaves", octaves_var, 1, 8),
    ("Perlin Scale", perlin_scale_var, 10, 300),
    ("Seed", seed_var, 0, 1000),
    ("Red Multiplier", red_multiplier_var, 0, 1),
    ("Green Multiplier", green_multiplier_var, 0, 1),
    ("Blue Multiplier", blue_multiplier_var, 0, 1),
]

controls_frame = ttk.Frame(root, padding=10)
controls_frame.grid(row=0, column=0, sticky="ns")

label_vars = []
for idx, (label_text, var, minval, maxval) in enumerate(params):
    ttk.Label(controls_frame, text=label_text).grid(row=idx, column=0, sticky="w")
    ttk.Scale(controls_frame, from_=minval, to=maxval, variable=var, orient="horizontal",
              command=generate_texture).grid(row=idx, column=1, sticky="ew", padx=5)
    value_label = ttk.Label(controls_frame, text=f"{var.get():.2f}", width=6)
    value_label.grid(row=idx, column=2)
    label_vars.append((var, value_label))

save_button = ttk.Button(controls_frame, text="Зберегти зображення", command=save_image)
save_button.grid(row=len(params), column=0, columnspan=3, pady=10)

# Площа для малювання
fig, ax = plt.subplots(figsize=(6, 6))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.grid(row=0, column=1, sticky="nsew")

generate_texture()
root.mainloop()
