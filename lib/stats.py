import numpy as np
import matplotlib.pyplot as plt
from random import randint, shuffle
from PIL import Image
from PIL.ImageOps import invert


def create_stats() -> None:
    stats: list = ['Constitution', 'Intelligence',
                   'Force', 'Conscience', 'Agilité', 'Social']
    total_stats: int = 30
    number_stats: int = len(stats)

    values: list = []
    while sum(values) != total_stats:
        values = [randint(2, 8) for _ in range(number_stats)]

    # il faut copier la première valeur à la dernière place
    values.append(values[0])

    plt.figure(figsize=(4, 4), dpi=100)
    ax = plt.subplot(polar=True)

    theta = np.linspace(0, 2 * np.pi, len(values))

    lines, labels = plt.thetagrids(range(0, 360, int(360/len(stats))), (stats))

    ax.plot(theta, values, color='#658e26')
    ax.fill(theta, values, alpha=0.1, color='#658e26')
    ax.set_rlabel_position(0)

    angles = np.linspace(0, 2*np.pi, len(ax.get_xticklabels())+1)
    angles[np.cos(angles) < 0] = angles[np.cos(angles) < 0] + np.pi
    angles = np.rad2deg(angles)
    labels = []
    for label, angle in zip(ax.get_xticklabels(), angles):
        x, y = label.get_position()
        lab = ax.text(x, y, label.get_text(), transform=label.get_transform(),
                      ha=label.get_ha(), va=label.get_va())
        if angle > 90:
            lab.set_rotation(angle+90)
        else:
            lab.set_rotation(angle-90)
        labels.append(lab)
    ax.set_xticklabels([])

    ax.set_ylim([0, 8])
    path: str = "img/radial_stats.png"
    plt.savefig(path, transparent=True, bbox_inches='tight')

    image = Image.open(path)
    if image.mode == 'RGBA':
        r, g, b, a = image.split()
        rgb_image = Image.merge('RGB', (r, g, b))
        inverted_image = invert(rgb_image)
        r2, g2, b2 = inverted_image.split()
        final_transparent_image = Image.merge('RGBA', (r2, g2, b2, a))
        final_transparent_image.save(path)

    else:
        inverted_image = invert(image)
        inverted_image.save(path)

    return path


def display_stats(stats: list, current_values: list, maximum_values: list, critical_values: list) -> str:
    color_critical: str = "#12b6b7"
    color_maximum: str = "#4d12b7"
    color_current: str = "#576e07"
    current_values.append(current_values[0])
    maximum_values.append(maximum_values[0])
    critical_values.append(critical_values[0])

    plt.figure(figsize=(4, 4), dpi=100)
    ax = plt.subplot(polar=True)

    theta = np.linspace(0, 2 * np.pi, len(current_values))

    lines, labels = plt.thetagrids(range(0, 360, int(360/len(stats))), (stats))

    ax.plot(theta, current_values, color=color_current)
    ax.plot(theta, maximum_values, color=color_maximum)
    ax.plot(theta, critical_values, color=color_critical)
    ax.fill(theta, critical_values, alpha=0.1, color=color_critical)
    ax.set_rlabel_position(0)

    angles = np.linspace(0, 2*np.pi, len(ax.get_xticklabels())+1)
    angles[np.cos(angles) < 0] = angles[np.cos(angles) < 0] + np.pi
    angles = np.rad2deg(angles)
    labels = []
    for label, angle in zip(ax.get_xticklabels(), angles):
        x, y = label.get_position()
        lab = ax.text(x, y, label.get_text(), transform=label.get_transform(),
                      ha=label.get_ha(), va=label.get_va())
        if angle > 90:
            lab.set_rotation(angle+90)
        else:
            lab.set_rotation(angle-90)
        labels.append(lab)
    ax.set_xticklabels([])

    ax.set_ylim([0, 24])
    ax.set_yticklabels([])
    path: str = "img/player_stats.png"
    plt.savefig(path, transparent=True, bbox_inches='tight')

    image = Image.open(path)
    if image.mode == 'RGBA':
        r, g, b, a = image.split()
        rgb_image = Image.merge('RGB', (r, g, b))
        inverted_image = invert(rgb_image)
        r2, g2, b2 = inverted_image.split()
        final_transparent_image = Image.merge('RGBA', (r2, g2, b2, a))
        final_transparent_image.save(path)

    else:
        inverted_image = invert(image)
        inverted_image.save(path)

    return path


def count_crit_values(current_values: list, critical_values: list) -> tuple:
    """Etant donné un tableau de valeurs, donne les comptes des valeurs sous le seuil et égales à zéro

    Args:
        current_values (list): liste de valeurs actuelles
        critical_values (list): bornes auxquelles comparer

    Returns:
        tuple: (|valeurs sous seuil critique|, |valeurs à 0|)
    """
    return sum([1 for i, current in enumerate(current_values) if current < critical_values[i]]), sum([1 for current in current_values if current == 0])
