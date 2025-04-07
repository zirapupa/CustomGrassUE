import tkinter as tk
from tkinter import ttk, colorchooser
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.colors import LinearSegmentedColormap
from noise import pnoise2
import random

# --- GUI SETUP ---
root = tk.Tk()
root.title("Перлін Текстура: Шарова генерація")
root.geometry("1100x700")

texture_size = 512
layers = []
color_stops = []

fig, ax = plt.subplots(figsize=(6, 6))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.grid(row=0, column=1, rowspan=10, padx=10, pady=10)

# --- FUNCTIONS ---
def generate_color_palette():
    main_color = "#4CAF50"
    accent_color = "#FFC107"
    mid_colors = ["#8BC34A", "#CDDC39", "#FFEB3B"]
    all_colors = [main_color] + mid_colors + [accent_color]
    stops = [(i / (len(all_colors) - 1), col) for i, col in enumerate(all_colors)]
    return stops

def update_color_list_ui():
    for widget in color_list_frame.winfo_children():
        widget.destroy()

    for i, (pos, color) in enumerate(color_stops):
        row = tk.Frame(color_list_frame)
        row.pack(fill="x", pady=2)

        lbl = tk.Label(row, text=f"{pos:.2f}", width=5)
        lbl.pack(side="left")

        btn = tk.Button(row, bg=color, width=4, command=lambda idx=i: choose_new_color(idx))
        btn.pack(side="left", padx=2)

        del_btn = tk.Button(row, text="🗑", command=lambda idx=i: delete_color(idx))
        del_btn.pack(side="right")

def choose_new_color(index):
    new_color = colorchooser.askcolor(title="Оберіть новий колір")[1]
    if new_color and 0 <= index < len(color_stops):
        color_stops[index] = (color_stops[index][0], new_color)
        update_color_list_ui()
        generate_texture()

def delete_color(index):
    if 0 <= index < len(color_stops):
        del color_stops[index]
        update_color_list_ui()
        generate_texture()

def add_new_color():
    new_color = colorchooser.askcolor(title="Оберіть колір для додавання")[1]
    if new_color:
        last_pos = color_stops[-1][0] if color_stops else 0.0
        new_pos = min(last_pos + 0.1, 1.0)
        color_stops.append((new_pos, new_color))
        update_color_list_ui()
        generate_texture()

def generate_texture():
    global layers
    result = np.zeros((texture_size, texture_size))

    for layer in layers:
        scale = layer['scale'].get()
        octaves = int(layer['octaves'].get())
        persistence = layer['persistence'].get()
        lacunarity = layer['lacunarity'].get()
        weight = layer['weight'].get()
        seed = layer['seed'].get()

        noise = np.zeros((texture_size, texture_size))
        for y in range(texture_size):
            for x in range(texture_size):
                nx = x / texture_size * scale
                ny = y / texture_size * scale
                noise[y][x] = pnoise2(nx, ny, octaves=octaves,
                                      persistence=persistence,
                                      lacunarity=lacunarity,
                                      repeatx=texture_size, repeaty=texture_size,
                                      base=seed)

        noise = (noise - noise.min()) / (noise.max() - noise.min() + 1e-8)
        result += noise * weight

    result = (result - result.min()) / (result.max() - result.min() + 1e-8)

    if not color_stops:
        color_stops.extend(generate_color_palette())

    stops = sorted(color_stops, key=lambda c: c[0])
    if stops[0][0] > 0.0:
        stops.insert(0, (0.0, stops[0][1]))
    if stops[-1][0] < 1.0:
        stops.append((1.0, stops[-1][1]))

    cmap = LinearSegmentedColormap.from_list("custom", [color for _, color in stops])

    ax.clear()
    ax.imshow(result, cmap=cmap)
    ax.axis('off')
    canvas.draw()

def add_layer():
    frame = ttk.LabelFrame(scrollable_frame, text=f"Шар {len(layers)+1}")
    frame.pack(fill="x", padx=5, pady=5)

    layer = {
        'scale': tk.DoubleVar(value=4.0),
        'octaves': tk.IntVar(value=4),
        'persistence': tk.DoubleVar(value=0.5),
        'lacunarity': tk.DoubleVar(value=2.0),
        'weight': tk.DoubleVar(value=1.0),
        'seed': tk.IntVar(value=random.randint(0, 10000)),
    }

    def create_scale(label, var, frm, to, step):
        ttk.Label(frame, text=label).pack(anchor='w')
        scale = tk.Scale(frame, variable=var, from_=frm, to=to, resolution=step, orient='horizontal', command=lambda e: generate_texture())
        scale.pack(fill="x")

    create_scale("Scale", layer['scale'], 1, 20, 0.1)
    create_scale("Octaves", layer['octaves'], 1, 10, 1)
    create_scale("Persistence", layer['persistence'], 0.1, 1.0, 0.05)
    create_scale("Lacunarity", layer['lacunarity'], 1.0, 4.0, 0.1)
    create_scale("Weight", layer['weight'], 0.0, 1.0, 0.05)

    seed_entry = ttk.Entry(frame, textvariable=layer['seed'])
    seed_entry.pack()
    seed_entry.bind("<Return>", lambda e: generate_texture())

    def remove_layer():
        layers.remove(layer)
        frame.destroy()
        generate_texture()

    ttk.Button(frame, text="Видалити шар", command=remove_layer).pack(pady=5)

    layers.append(layer)
    generate_texture()

def save_texture():
    from tkinter import filedialog
    path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[["PNG Files", "*.png"]])
    if path:
        ax.set_position([0, 0, 1, 1])
        ax.set_xlim([0, texture_size])
        ax.set_ylim([texture_size, 0])
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        fig.savefig(path, dpi=300, transparent=True, bbox_inches='tight', pad_inches=0)

# --- UI ---
scroll_canvas = tk.Canvas(root, width=350)
scroll_canvas.grid(row=0, column=0, sticky='ns')
scrollbar = ttk.Scrollbar(root, orient="vertical", command=scroll_canvas.yview)
scrollbar.grid(row=0, column=0, sticky='nse', padx=(330, 0))
scrollable_frame = ttk.Frame(scroll_canvas)
scrollable_frame.bind("<Configure>", lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all")))
scroll_canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
scroll_canvas.configure(yscrollcommand=scrollbar.set)

add_btn = ttk.Button(scrollable_frame, text="+ Додати шум", command=add_layer)
add_btn.pack(pady=10)

color_frame = ttk.LabelFrame(scrollable_frame, text="Кольори")
color_frame.pack(fill="x", padx=5, pady=10)

color_list_frame = ttk.Frame(color_frame)
color_list_frame.pack(fill="x")

add_color_btn = ttk.Button(color_frame, text="+ Додати колір", command=add_new_color)
add_color_btn.pack(pady=5)

save_btn = ttk.Button(scrollable_frame, text="📂 Зберегти текстуру", command=save_texture)
save_btn.pack(pady=10)

# --- START ---
color_stops.extend(generate_color_palette())
update_color_list_ui()
add_layer()
root.mainloop()