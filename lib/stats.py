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
