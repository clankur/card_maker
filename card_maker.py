import csv
import os
from PIL import Image, ImageDraw, ImageFont, ImageColor
import textwrap
from functools import lru_cache

COLORS = {
    "background": (*ImageColor.getrgb("#0d1b2a"), 128),
    "border": "#778da9",
    "title": "white",
    "type": "#e0e1dd",
    "type_background": "#415a77",
    "cost": "#e0e1dd",
    "ability": "white",
    "stat_fill": "#778da9",
    "stat_border": "black",
    "grid_background": "white",
}

PAGE_SIZE = (2550, 3300)  # US letter page at 300 dpi
CARD_SIZE = (PAGE_SIZE[0] // 3, PAGE_SIZE[1] // 3)


@lru_cache(maxsize=None)
def get_font(size):
    font_paths = [
        "/Library/Fonts/Luminari.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def resize_and_crop(image, target_size):
    aspect_ratio_target = target_size[0] / target_size[1]
    aspect_ratio_image = image.width / image.height
    if aspect_ratio_image > aspect_ratio_target:
        new_width = int(image.height * aspect_ratio_target)
        image = image.crop(
            (
                (image.width - new_width) // 2,
                0,
                (image.width + new_width) // 2,
                image.height,
            )
        )
    else:
        new_height = int(image.width / aspect_ratio_target)
        image = image.crop(
            (
                0,
                (image.height - new_height) // 2,
                image.width,
                (image.height + new_height) // 2,
            )
        )
    return image.resize(target_size, Image.LANCZOS)


def create_card(title, cost, type, ability, atk, image_path):
    card = Image.new("RGBA", CARD_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)

    bg_image = (
        Image.open(image_path).convert("RGBA")
        if os.path.exists(image_path)
        else Image.new("RGBA", CARD_SIZE, COLORS["background"][:3] + (255,))
    )
    bg_image = resize_and_crop(bg_image, CARD_SIZE)

    overlay = Image.new("RGBA", CARD_SIZE, COLORS["background"])
    card = Image.alpha_composite(bg_image, overlay)
    draw = ImageDraw.Draw(card)

    border_width = max(1, int(CARD_SIZE[0] * 0.007))
    title_area_height = int(CARD_SIZE[1] * 0.125)

    draw.rounded_rectangle(
        [0, 0, CARD_SIZE[0], CARD_SIZE[1]],
        radius=int(CARD_SIZE[1] * 0.025),
        outline=COLORS["border"],
        width=border_width,
    )
    draw.line(
        [(0, title_area_height), (CARD_SIZE[0], title_area_height)],
        fill=COLORS["border"],
        width=border_width,
    )

    draw.text(
        (CARD_SIZE[0] // 2, title_area_height // 2),
        title,
        font=get_font(int(CARD_SIZE[1] * 0.06)),
        fill=COLORS["title"],
        anchor="mm",
    )
    draw.text(
        (CARD_SIZE[0] * 0.95, title_area_height // 2),
        str(cost),
        font=get_font(int(CARD_SIZE[1] * 0.07)),
        fill=COLORS["cost"],
        anchor="rm",
    )
    draw.text(
        (CARD_SIZE[0] // 2, title_area_height + int(CARD_SIZE[1] * 0.5)),
        type,
        font=get_font(int(CARD_SIZE[1] * 0.045)),
        fill=COLORS["type"],
        anchor="mm",
    )

    ability_font = get_font(int(CARD_SIZE[1] * 0.04))
    wrapped_ability = textwrap.fill(
        ability,
        width=int(
            CARD_SIZE[0]
            * 0.9
            / (ability_font.getbbox("x")[2] - ability_font.getbbox("x")[0])
            * 1.5
        ),
    )
    draw.multiline_text(
        (CARD_SIZE[0] // 2, title_area_height + int(CARD_SIZE[1] * 0.56)),
        wrapped_ability,
        font=ability_font,
        fill=COLORS["ability"],
        align="center",
        anchor="ma",
        spacing=int(CARD_SIZE[1] * 0.01),
    )

    atk_font = get_font(int(CARD_SIZE[1] * 0.06))
    draw.text(
        (int(CARD_SIZE[0] * 0.05), CARD_SIZE[1] - int(CARD_SIZE[1] * 0.08)),
        str(atk),
        font=atk_font,
        fill=COLORS["stat_fill"],
        stroke_width=2,
        stroke_fill=COLORS["stat_border"],
    )

    return card


def create_grid(cards):
    grid = Image.new("RGB", PAGE_SIZE, color=COLORS["grid_background"])
    for i, card in enumerate(cards):
        grid.paste(card, ((i % 3) * CARD_SIZE[0], (i // 3) * CARD_SIZE[1]))
    return grid


def process_csv(csv_file):
    with open(csv_file, "r") as file:
        reader = csv.DictReader(file)
        cards = [
            create_card(
                **{
                    k: row[k]
                    for k in ["title", "cost", "type", "ability", "atk", "image_path"]
                }
            )
            for row in reader
        ]
    return [create_grid(cards[i : i + 9]) for i in range(0, len(cards), 9)]


if __name__ == "__main__":
    csv_file = "cards.csv"
    grids = process_csv(csv_file)
    for i, grid in enumerate(grids):
        grid.save(f"card_grid_{i+1}.png")
    print(
        f"Created {len(grids)} grid(s) of cards with dimensions {PAGE_SIZE[0]}x{PAGE_SIZE[1]} pixels."
    )
