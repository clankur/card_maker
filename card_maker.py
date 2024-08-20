import csv
from PIL import Image, ImageDraw, ImageFont
import textwrap
import os

COLORS = {
    "background": "#0d1b2a",
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

# Page dimensions setting set for standard US letter page
# with printer of 300 dpi
PAGE_WIDTH, PAGE_HEIGHT = 2550, 3300

CARD_WIDTH = PAGE_WIDTH // 3
CARD_HEIGHT = PAGE_HEIGHT // 3


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


def draw_rounded_rectangle(draw, xy, corner_radius, fill=None, outline=None):
    upper_left_point = xy[0]
    bottom_right_point = xy[1]

    draw.rectangle(
        [
            (upper_left_point[0], upper_left_point[1] + corner_radius),
            (bottom_right_point[0], bottom_right_point[1] - corner_radius),
        ],
        fill=fill,
        outline=outline,
    )
    draw.rectangle(
        [
            (upper_left_point[0] + corner_radius, upper_left_point[1]),
            (bottom_right_point[0] - corner_radius, bottom_right_point[1]),
        ],
        fill=fill,
        outline=outline,
    )
    draw.pieslice(
        [
            upper_left_point,
            (
                upper_left_point[0] + corner_radius * 2,
                upper_left_point[1] + corner_radius * 2,
            ),
        ],
        180,
        270,
        fill=fill,
        outline=outline,
    )
    draw.pieslice(
        [
            (
                bottom_right_point[0] - corner_radius * 2,
                bottom_right_point[1] - corner_radius * 2,
            ),
            bottom_right_point,
        ],
        0,
        90,
        fill=fill,
        outline=outline,
    )
    draw.pieslice(
        [
            (upper_left_point[0], bottom_right_point[1] - corner_radius * 2),
            (upper_left_point[0] + corner_radius * 2, bottom_right_point[1]),
        ],
        90,
        180,
        fill=fill,
        outline=outline,
    )
    draw.pieslice(
        [
            (bottom_right_point[0] - corner_radius * 2, upper_left_point[1]),
            (bottom_right_point[0], upper_left_point[1] + corner_radius * 2),
        ],
        270,
        360,
        fill=fill,
        outline=outline,
    )


def create_card(title, cost, type, ability, atk, image_path):
    card = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), color=COLORS["background"])
    draw = ImageDraw.Draw(card)

    fonts = {
        "title": get_font(int(CARD_HEIGHT * 0.06)),  # 6% of card height
        "type": get_font(int(CARD_HEIGHT * 0.045)),  # 4.5% of card height
        "cost": get_font(int(CARD_HEIGHT * 0.07)),  # 7% of card height
        "ability": get_font(int(CARD_HEIGHT * 0.04)),  # 4% of card height
        "stat": get_font(int(CARD_HEIGHT * 0.07)),  # 7% of card height
    }

    border_width = max(
        1, int(CARD_WIDTH * 0.007)
    )  # 0.7% of card width, minimum 1 pixel
    draw.rectangle(
        [0, 0, CARD_WIDTH - 1, CARD_HEIGHT - 1],
        outline=COLORS["border"],
        width=border_width,
    )

    title_area_height = int(CARD_HEIGHT * 0.125)  # 12.5% of card height
    draw.line(
        [
            (border_width, title_area_height),
            (CARD_WIDTH - border_width, title_area_height),
        ],
        fill=COLORS["border"],
        width=border_width,
    )

    draw.text(
        (
            (CARD_WIDTH - draw.textlength(title, font=fonts["title"])) / 2,
            int(CARD_HEIGHT * 0.025),
        ),
        title,
        font=fonts["title"],
        fill=COLORS["title"],
    )

    cost_x = (
        CARD_WIDTH
        - draw.textlength(str(cost), font=fonts["cost"])
        - int(CARD_WIDTH * 0.033)
    )
    cost_y = (title_area_height - fonts["cost"].size) // 2
    draw.text(
        (cost_x, cost_y),
        str(cost),
        font=fonts["cost"],
        fill=COLORS["cost"],
    )

    image_height = int(CARD_HEIGHT * 0.5)  # 50% of card height
    image_y = title_area_height + int(CARD_HEIGHT * 0.0125)
    if os.path.exists(image_path):
        char_image = Image.open(image_path)
        char_image.thumbnail((int(CARD_WIDTH * 0.67), image_height))
        image_pos = (
            (CARD_WIDTH - char_image.width) // 2,
            image_y + (image_height - char_image.height) // 2,
        )
        card.paste(
            char_image, image_pos, char_image if char_image.mode == "RGBA" else None
        )
    else:
        draw.text(
            (CARD_WIDTH // 3, CARD_HEIGHT // 2.5),
            "Image not found",
            font=fonts["ability"],
            fill=COLORS["ability"],
        )

    type_width = draw.textlength(type, font=fonts["type"]) + int(CARD_WIDTH * 0.067)
    type_height = int(CARD_HEIGHT * 0.075)
    type_x = (CARD_WIDTH - type_width) // 2
    type_y = image_y + image_height - type_height // 2

    draw_rounded_rectangle(
        draw,
        [(type_x, type_y), (type_x + type_width, type_y + type_height)],
        corner_radius=int(CARD_HEIGHT * 0.025),
        fill=COLORS["type_background"],
    )

    draw.text(
        (type_x + int(CARD_WIDTH * 0.033), type_y + int(CARD_HEIGHT * 0.0125)),
        type,
        font=fonts["type"],
        fill=COLORS["type"],
    )

    ability_font = fonts["ability"]
    ability_x = int(CARD_WIDTH * 0.05)  # 5% padding from the left
    ability_y = image_y + image_height + type_height // 2 + int(CARD_HEIGHT * 0.025)
    ability_width = int(CARD_WIDTH * 0.9)  # 90% of card width
    ability_height = int(CARD_HEIGHT * 0.25)  # 25% of card height for ability text

    # Calculate the average character width
    avg_char_width = ability_font.getbbox("x")[2] - ability_font.getbbox("x")[0]

    # Wrap the ability text
    wrapped_ability = textwrap.fill(
        ability, width=int(ability_width / avg_char_width * 1.5)
    )

    # Draw the wrapped ability text
    draw.multiline_text(
        (ability_x, ability_y),
        wrapped_ability,
        font=ability_font,
        fill=COLORS["ability"],
        align="center",
        spacing=int(CARD_HEIGHT * 0.01),  # Add some line spacing
    )

    atk_text = f"ATK: {atk}"
    x, y = int(CARD_WIDTH * 0.033), CARD_HEIGHT - int(CARD_HEIGHT * 0.0875)
    for offset in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
        draw.text(
            (x + offset[0], y + offset[1]),
            atk_text,
            font=fonts["stat"],
            fill=COLORS["stat_border"],
        )
    draw.text((x, y), atk_text, font=fonts["stat"], fill=COLORS["stat_fill"])

    return card


def create_grid(cards):
    grid = Image.new("RGB", (PAGE_WIDTH, PAGE_HEIGHT), color=COLORS["grid_background"])
    for i, card in enumerate(cards):
        grid.paste(card, ((i % 3) * CARD_WIDTH, (i // 3) * CARD_HEIGHT))
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
        f"Created {len(grids)} grid(s) of cards with dimensions {PAGE_WIDTH}x{PAGE_HEIGHT} pixels."
    )
