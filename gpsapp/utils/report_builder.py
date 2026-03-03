import os
import uuid

import matplotlib
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

matplotlib.use("Agg")


def rotate_image_90(input_path):
    img = Image.open(input_path)
    rotated = img.rotate(90, expand=True)
    rotated.save(input_path)


def plot_event(data_input, title, output_file, is_match):
    if data_input.empty:
        return

    df_sorted = data_input.sort_values(by="Total Distance (m)", ascending=False).copy()

    numeric_cols = [
        "Total Distance (m)",
        "Run Distance > 15 km/h (m)",
        "Sprint Distance > 20 km/h (m)",
        "Hi-Sprint Distance > 25 km/h (m)",
        "Max Speed (km/h)",
        "# Hi-Sprints",
    ]

    avg_values = df_sorted[numeric_cols].mean()
    avg_row = pd.DataFrame([avg_values])
    avg_row["Speler"] = "TEAM GEMIDDELDE"
    avg_row = avg_row[df_sorted.columns]

    rows_to_concat = [df_sorted, avg_row]

    if is_match:
        sum_values = df_sorted[numeric_cols].sum()
        norm_values = sum_values / 10
        norm_row = pd.DataFrame([norm_values])
        norm_row["Speler"] = "TEAM GEMIDDELDE (90 min)"
        norm_row = norm_row[df_sorted.columns]
        rows_to_concat.append(norm_row)

    data = pd.concat(rows_to_concat, ignore_index=True)

    players = data["Speler"].tolist()[::-1]
    total = data["Total Distance (m)"].tolist()[::-1]
    run = data["Run Distance > 15 km/h (m)"].tolist()[::-1]
    sprint = data["Sprint Distance > 20 km/h (m)"].tolist()[::-1]
    hisprint = data["Hi-Sprint Distance > 25 km/h (m)"].tolist()[::-1]
    max_speeds = data["Max Speed (km/h)"].tolist()[::-1]
    nr_hisprints = data["# Hi-Sprints"].tolist()[::-1]

    y = np.arange(len(players))

    fig, ax = plt.subplots(figsize=(12, 8))

    ax.barh(y, total, color="skyblue", alpha=0.8, label="Total Distance")
    ax.barh(y, run, color="darkblue", alpha=0.9, label="Run > 15 km/h")
    ax.barh(y, sprint, color="orange", alpha=0.9, label="Sprint > 20 km/h")
    ax.barh(y, hisprint, color="red", alpha=1.0, label="Hi-Sprint > 25 km/h")

    for i in range(len(players)):
        txt_total = ax.text(
            total[i] + 100,
            y[i],
            f"{total[i]:.0f}",
            va="center",
            fontsize=9,
            fontweight="bold",
            color="black",
        )
        txt_total.set_path_effects(
            [path_effects.Stroke(linewidth=2, foreground="white"), path_effects.Normal()]
        )

        txt_run = ax.text(
            run[i] + 50,
            y[i] - 0.25,
            f"{run[i]:.0f}",
            va="center",
            fontsize=8,
            fontweight="bold",
            color="white",
        )

        txt_sprint = ax.text(
            sprint[i] + 50,
            y[i] + 0.05,
            f"{sprint[i]:.0f}",
            va="center",
            fontsize=8,
            fontweight="bold",
            color="white",
        )

        txt_hisprint = ax.text(
            hisprint[i] + 50,
            y[i] + 0.30,
            f"{hisprint[i]:.0f}",
            va="center",
            fontsize=8,
            fontweight="bold",
            color="white",
        )

        for txt in [txt_run, txt_sprint, txt_hisprint]:
            txt.set_path_effects(
                [path_effects.Stroke(linewidth=2, foreground="black"), path_effects.Normal()]
            )

    ax.text(
        1.02,
        1.01,
        "Max\nSpeed",
        transform=ax.transAxes,
        fontsize=10,
        fontweight="bold",
        va="bottom",
        ha="center",
        color="black",
    )
    ax.text(
        1.12,
        1.01,
        "# Hi\nSprints",
        transform=ax.transAxes,
        fontsize=10,
        fontweight="bold",
        va="bottom",
        ha="center",
        color="black",
    )

    for i in range(len(players)):
        ax.text(
            1.02,
            y[i],
            f"{max_speeds[i]:.1f}",
            transform=ax.get_yaxis_transform(),
            fontsize=9,
            va="center",
            ha="center",
        )
        ax.text(
            1.12,
            y[i],
            f"{nr_hisprints[i]:.0f}",
            transform=ax.get_yaxis_transform(),
            fontsize=9,
            va="center",
            ha="center",
        )

    ax.set_yticks(y)
    ax.set_yticklabels(players)

    ytick_labels = ax.get_yticklabels()
    for label in ytick_labels:
        if "GEMIDDELDE" in label.get_text():
            label.set_fontweight("bold")

    ax.set_xlabel("Afstand (m)")
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(axis="x", linestyle="--", alpha=0.5)

    plt.subplots_adjust(right=0.85)
    plt.savefig(output_file, dpi=600, bbox_inches="tight")
    plt.close(fig)


def _summary_from_df(df_part):
    summary = df_part.groupby("name").agg(
        {
            "totaldistance": "sum",
            "rundistance": "sum",
            "sprintdistance": "sum",
            "hisprintdistance": "sum",
            "maxspeed": "max",
            "numberofhisprints": "sum",
        }
    ).reset_index()

    summary = summary.rename(
        columns={
            "name": "Speler",
            "totaldistance": "Total Distance (m)",
            "rundistance": "Run Distance > 15 km/h (m)",
            "sprintdistance": "Sprint Distance > 20 km/h (m)",
            "hisprintdistance": "Hi-Sprint Distance > 25 km/h (m)",
            "maxspeed": "Max Speed (km/h)",
            "numberofhisprints": "# Hi-Sprints",
        }
    )
    return summary.sort_values(by="Speler").reset_index(drop=True)


def _safe_name(value):
    return "".join([c if c.isalnum() else "_" for c in value]).strip("_")


def _mm_to_px(mm, dpi):
    return int((mm / 25.4) * dpi)


def _image_to_a4_page(image_path, margin_mm=12, dpi=300):
    a4_w_px = _mm_to_px(210, dpi)
    a4_h_px = _mm_to_px(297, dpi)
    margin_px = _mm_to_px(margin_mm, dpi)

    content_w = a4_w_px - (2 * margin_px)
    content_h = a4_h_px - (2 * margin_px)

    img = Image.open(image_path).convert("RGB")
    img.thumbnail((content_w, content_h), Image.Resampling.LANCZOS)

    page = Image.new("RGB", (a4_w_px, a4_h_px), "white")
    x = (a4_w_px - img.width) // 2
    y = (a4_h_px - img.height) // 2
    page.paste(img, (x, y))
    return page


def images_to_pdf(image_paths, pdf_path):
    pages = []
    for path in image_paths:
        if os.path.exists(path):
            pages.append(_image_to_a4_page(path))

    if not pages:
        raise ValueError("Geen grafieken gevonden om PDF te maken.")

    first, rest = pages[0], pages[1:]
    first.save(pdf_path, save_all=True, append_images=rest)


def build_graph_only_pdf(csv_path, output_base):
    df = pd.read_csv(csv_path)
    if "exercise" not in df.columns:
        raise ValueError("CSV mist verplichte kolom: exercise")

    exercise_norm = df["exercise"].astype(str).str.strip()
    is_match = exercise_norm.str.contains("first half|second half", case=False, na=False).any()

    df_total = df[exercise_norm.str.upper() == "TOTAL EVENT"]

    summary_total = df_total[
        [
            "name",
            "totaldistance",
            "rundistance",
            "sprintdistance",
            "hisprintdistance",
            "maxspeed",
            "numberofhisprints",
        ]
    ].copy()
    summary_total = summary_total.rename(
        columns={
            "name": "Speler",
            "totaldistance": "Total Distance (m)",
            "rundistance": "Run Distance > 15 km/h (m)",
            "sprintdistance": "Sprint Distance > 20 km/h (m)",
            "hisprintdistance": "Hi-Sprint Distance > 25 km/h (m)",
            "maxspeed": "Max Speed (km/h)",
            "numberofhisprints": "# Hi-Sprints",
        }
    )
    summary_total = summary_total.sort_values(by="Speler").reset_index(drop=True)
    if summary_total.empty:
        raise ValueError("Geen TOTAL EVENT data gevonden in CSV.")

    summary_halves = None

    if is_match:
        df_halves = df[
            df["exercise"].str.contains("first half|second half|third half", case=False, na=False)
        ]
        if not df_halves.empty:
            summary_halves = _summary_from_df(df_halves)

    run_id = uuid.uuid4().hex
    output_dir = os.path.join(output_base, "generated", run_id)
    os.makedirs(output_dir, exist_ok=True)

    event_name = df_total["event"].iloc[0] if not df_total.empty else "GPS Event Samenvatting"

    plot_total_path = os.path.join(output_dir, "plot_total_event.png")
    plot_event(summary_total, f"{event_name} - TOTAL SESSION", plot_total_path, is_match)
    if not os.path.exists(plot_total_path):
        raise ValueError("Kon geen grafiek maken voor TOTAL EVENT.")
    rotate_image_90(plot_total_path)

    selected_plot_paths = [plot_total_path]

    if is_match and summary_halves is not None and not summary_halves.empty:
        plot_halves_path = os.path.join(output_dir, "plot_halves_summary.png")
        plot_event(
            summary_halves,
            f"{event_name} - 1e + 2e helft Samenvatting",
            plot_halves_path,
            is_match,
        )
        if os.path.exists(plot_halves_path):
            rotate_image_90(plot_halves_path)
            selected_plot_paths.append(plot_halves_path)

    safe_event_name = _safe_name(event_name) or "gps_event"
    pdf_filename = f"{safe_event_name}_graphs.pdf"
    pdf_path = os.path.join(output_dir, pdf_filename)
    images_to_pdf(selected_plot_paths, pdf_path)

    return {
        "event_name": event_name,
        "is_match": bool(is_match),
        "pdf_path": pdf_path,
        "pdf_filename": pdf_filename,
        "plots": selected_plot_paths,
    }
