import os
import uuid
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from PIL import Image

# helper: draai 90° en schaal binnen A4 hoogte
def rotate_and_resize_for_a4(path, max_height_cm=24.0):
    img = Image.open(path)
    rotated = img.rotate(90, expand=True)
    # schaal: we willen max hoogte ~ 24 cm -> convert to pixels: but easier: resize by ratio of inches
    # We'll compute based on DPI (300) target
    dpi = 300
    max_h_px = int((max_height_cm / 2.54) * dpi)
    w, h = rotated.size
    if h > max_h_px:
        ratio = max_h_px / h
        new_w = int(w * ratio)
        new_h = int(h * ratio)
        rotated = rotated.resize((new_w, new_h), Image.LANCZOS)
    rotated.save(path, dpi=(dpi, dpi))

def apply_plot_style():
    plt.rcParams.update({
        "axes.edgecolor": "#111111",
        "axes.labelcolor": "#111111",
        "xtick.color": "#111111",
        "ytick.color": "#111111",
        "font.size": 10,
    })

def make_plot(data, title, outpath):
    apply_plot_style()
    if data.empty:
        # create empty placeholder
        plt.figure(figsize=(6,4))
        plt.text(0.5, 0.5, "Geen data", ha='center', va='center')
        plt.axis('off')
        plt.savefig(outpath, dpi=200)
        plt.close()
        rotate_and_resize_for_a4(outpath)
        return

    data = data.sort_values(by="Total Distance (m)", ascending=False).reset_index(drop=True)
    players = data["Speler"].tolist()[::-1]
    total = data["Total Distance (m)"].tolist()[::-1]
    sprint = data["Sprint Distance > 20 km/h (m)"].tolist()[::-1]
    hisprint = data["Hi-Sprint Distance > 25 km/h (m)"].tolist()[::-1]

    y = np.arange(len(players))
    plt.figure(figsize=(8, max(4, len(players)*0.4)))  # verticale ruimte afhankelijk van aantal spelers

    # kleuren: rood/zwart/grey (kleurenblindvriendelijk combinatie)
    plt.barh(y, total, color="#B30000", alpha=0.9, label="Total")
    plt.barh(y, sprint, color="#4D4D4D", alpha=0.95, label="Sprint >20")
    plt.barh(y, hisprint, color="#111111", alpha=0.95, label="Hi-Sprint >25")

    for i in range(len(players)):
        for value, offset, fontsize in ((total[i], 0, 10), (sprint[i], -0.2, 9), (hisprint[i], +0.2, 9)):
            txt = plt.text(value + max(100, value*0.03), y[i] + offset, f"{value:.0f}",
                           va='center', fontsize=fontsize, fontweight='bold', color='white')
            txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

    plt.yticks(y, players)
    plt.xlabel("Afstand (m)")
    plt.title(title)
    plt.legend()
    plt.grid(axis='x', linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.savefig(outpath, dpi=300)
    plt.close()

    rotate_and_resize_for_a4(outpath)

def process_gps_file(csv_path, output_base):
    df = pd.read_csv(csv_path)

    # unify exercise text to avoid case-sensitivity
    df['exercise_clean'] = df['exercise'].astype(str).str.strip()

    # === Total event table (exact match or contains 'total event', case-insensitive) ===
    df_total = df[df['exercise_clean'].str.contains('total event', case=False, na=False)]

    summary_total = pd.DataFrame()
    if not df_total.empty:
        summary_total = df_total[["name", "totaldistance", "sprintdistance", "hisprintdistance"]].copy()
        summary_total = summary_total.rename(columns={
            "name": "Speler",
            "totaldistance": "Total Distance (m)",
            "sprintdistance": "Sprint Distance > 20 km/h (m)",
            "hisprintdistance": "Hi-Sprint Distance > 25 km/h (m)"
        })
    else:
        # empty frame with columns for template consistency
        summary_total = pd.DataFrame(columns=["Speler", "Total Distance (m)", "Sprint Distance > 20 km/h (m)", "Hi-Sprint Distance > 25 km/h (m)"])

    # === Halves combined ===
    df_halves = df[df['exercise_clean'].str.contains('first half|second half|third half', case=False, na=False)]
    if not df_halves.empty:
        summary_halves = df_halves.groupby('name', dropna=False).agg({
            'totaldistance': 'sum',
            'sprintdistance': 'sum',
            'hisprintdistance': 'sum'
        }).reset_index()
        summary_halves = summary_halves.rename(columns={
            'name': 'Speler',
            'totaldistance': 'Total Distance (m)',
            'sprintdistance': 'Sprint Distance > 20 km/h (m)',
            'hisprintdistance': 'Hi-Sprint Distance > 25 km/h (m)'
        })
    else:
        summary_halves = pd.DataFrame(columns=["Speler", "Total Distance (m)", "Sprint Distance > 20 km/h (m)", "Hi-Sprint Distance > 25 km/h (m)"])

    # === Separate per half (if present) ===
    halves = ['first half', 'second half', 'third half']
    per_half_tables = {}
    for half in halves:
        subset = df[df['exercise_clean'].str.contains(half, case=False, na=False)]
        if not subset.empty:
            s = subset.groupby('name', dropna=False).agg({
                'totaldistance': 'sum',
                'sprintdistance': 'sum',
                'hisprintdistance': 'sum'
            }).reset_index().rename(columns={
                'name': 'Speler',
                'totaldistance': 'Total Distance (m)',
                'sprintdistance': 'Sprint Distance > 20 km/h (m)',
                'hisprintdistance': 'Hi-Sprint Distance > 25 km/h (m)'
            })
            per_half_tables[half.title()] = s

    # make output folders
    uid = uuid.uuid4().hex
    plots_dir = os.path.join(output_base, 'plots', uid)
    os.makedirs(plots_dir, exist_ok=True)
    reports_dir = os.path.join(output_base, 'reports')
    os.makedirs(reports_dir, exist_ok=True)

    # create plots
    plot_total_path = os.path.join(plots_dir, 'plot_total.png')
    make_plot(summary_total, 'Total Event - Afstanden', plot_total_path)

    plot_halves_path = os.path.join(plots_dir, 'plot_halves.png')
    make_plot(summary_halves, 'Halves (1e+2e+3e) - Afstanden', plot_halves_path)

    plot_half_urls = {}
    for half_name, table in per_half_tables.items():
        fname = f"plot_{half_name.replace(' ', '_').lower()}.png"
        p = os.path.join(plots_dir, fname)
        make_plot(table, f"{half_name} - Afstanden", p)
        plot_half_urls[half_name] = os.path.join('plots', uid, fname)

    # relative URLs for templates (MEDIA_URL + path)
    plot_total_rel = os.path.join('plots', uid, 'plot_total.png')
    plot_halves_rel = os.path.join('plots', uid, 'plot_halves.png')

    # event name best effort
    event_name = df_total['event'].iloc[0] if not df_total.empty and 'event' in df_total.columns else 'GPS Event Samenvatting'

    return {
        'event_name': event_name,
        'summary_total': summary_total.to_dict(orient='records'),
        'summary_halves': summary_halves.to_dict(orient='records'),
        'plot_total_url': os.path.join('/media', plot_total_rel).replace('\\','/'),
        'plot_halves_url': os.path.join('/media', plot_halves_rel).replace('\\','/'),
        'plot_half_urls': {k: os.path.join('/media', v).replace('\\','/') for k, v in plot_half_urls.items()},
        'plots_dir': plots_dir,
        'report_dir': reports_dir
    }
