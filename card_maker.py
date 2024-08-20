import csv
from PIL import Image, ImageDraw, ImageFont
import textwrap
import os

# Global color palette
COLORS = {
    "background": "#0d1b2a",
    "border": "#778da9",
    "title": "white",
    "type": "#e0e1dd",
    "cost": "#e0e1dd",
    "ability": "white",
    "stat_fill": "#778da9",
    "stat_border": "black",
    "grid_background": "white",
}


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


def create_card(title, cost, type, ability, atk, image_path):
    card_width, card_height = 300, 400

    card = Image.new("RGB", (card_width, card_height), color=COLORS["background"])
    draw = ImageDraw.Draw(card)

    fonts = {
        "title": get_font(24),
        "type": get_font(18),
        "cost": get_font(36),
        "ability": get_font(16),
        "stat": get_font(28),
    }

    # Draw borders
    border_width = 2
    draw.rectangle(
        [0, 0, card_width - 1, card_height - 1],
        outline=COLORS["border"],
        width=border_width,
    )
    draw.line(
        [(border_width, 65), (card_width - border_width, 65)],
        fill=COLORS["border"],
        width=border_width,
    )

    # Draw text elements
    draw.text(
        ((card_width - draw.textlength(title, font=fonts["title"])) / 2, 10),
        title,
        font=fonts["title"],
        fill=COLORS["title"],
    )
    draw.text(
        ((card_width - draw.textlength(type, font=fonts["type"])) / 2, 40),
        type,
        font=fonts["type"],
        fill=COLORS["type"],
    )
    draw.text(
        (card_width - draw.textlength(str(cost), font=fonts["cost"]) - 10, 5),
        str(cost),
        font=fonts["cost"],
        fill=COLORS["cost"],
    )

    # Draw image
    if os.path.exists(image_path):
        char_image = Image.open(image_path)
        char_image.thumbnail((200, 200))
        image_pos = (
            (card_width - char_image.width) // 2,
            70 + (200 - char_image.height) // 2,
        )
        card.paste(
            char_image, image_pos, char_image if char_image.mode == "RGBA" else None
        )
    else:
        draw.text(
            (100, 150), "Image not found", font=fonts["ability"], fill=COLORS["ability"]
        )

    # Draw ability
    lines = textwrap.wrap(ability, width=35)
    y_text = 280
    for line in lines:
        line_width = draw.textlength(line, font=fonts["ability"])
        draw.text(
            ((card_width - line_width) / 2, y_text),
            line,
            font=fonts["ability"],
            fill=COLORS["ability"],
        )
        y_text += 20

    # Draw attack with border and fill
    atk_text = f"ATK: {atk}"
    x, y = 10, card_height - 35
    # Draw the text with a border
    for offset in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
        draw.text(
            (x + offset[0], y + offset[1]),
            atk_text,
            font=fonts["stat"],
            fill=COLORS["stat_border"],
        )
    # Draw the main text
    draw.text((x, y), atk_text, font=fonts["stat"], fill=COLORS["stat_fill"])

    return card


def create_grid(cards):
    grid = Image.new("RGB", (900, 1200), color=COLORS["grid_background"])
    for i, card in enumerate(cards):
        grid.paste(card, ((i % 3) * 300, (i // 3) * 400))
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

    print(f"Created {len(grids)} grid(s) of cards.")
