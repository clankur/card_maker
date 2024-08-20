import csv
from PIL import Image, ImageDraw, ImageFont, ImageColor
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


COLORS["background"] = (
    *ImageColor.getrgb(COLORS["background"]),
    128,
)  # 128 for 50% opacity


def create_card(title, cost, type, ability, atk, image_path):
    # Create a transparent base for the card
    card = Image.new("RGBA", (CARD_WIDTH, CARD_HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)

    # Load and resize the background image
    if os.path.exists(image_path):
        bg_image = Image.open(image_path).convert("RGBA")
        bg_image = resize_and_crop(bg_image, (CARD_WIDTH, CARD_HEIGHT))
    else:
        bg_image = Image.new(
            "RGBA", (CARD_WIDTH, CARD_HEIGHT), COLORS["background"][:3] + (255,)
        )
        draw_placeholder = ImageDraw.Draw(bg_image)
        draw_placeholder.text(
            (CARD_WIDTH // 2, CARD_HEIGHT // 2),
            "Image not found",
            font=get_font(int(CARD_HEIGHT * 0.05)),
            fill="white",
            anchor="mm",
        )

    # Create a semi-transparent overlay
    overlay = Image.new("RGBA", (CARD_WIDTH, CARD_HEIGHT), COLORS["background"])

    # Composite the background image and overlay
    card = Image.alpha_composite(bg_image, overlay)
    draw = ImageDraw.Draw(card)

    # Calculate border and title area dimensions
    border_width = max(1, int(CARD_WIDTH * 0.007))
    title_area_height = int(CARD_HEIGHT * 0.125)
    corner_radius = int(CARD_HEIGHT * 0.025)

    # Draw the title area separator
    draw.line(
        [(0, title_area_height), (CARD_WIDTH, title_area_height)],
        fill=COLORS["border"],
        width=border_width,
    )

    # Draw rounded corners
    draw_rounded_corners(
        draw, CARD_WIDTH, CARD_HEIGHT, corner_radius, COLORS["border"], border_width
    )

    # Draw title
    title_font = get_font(int(CARD_HEIGHT * 0.06))
    draw.text(
        (CARD_WIDTH // 2, title_area_height // 2),
        title,
        font=title_font,
        fill=COLORS["title"],
        anchor="mm",
    )

    # Draw cost
    cost_font = get_font(int(CARD_HEIGHT * 0.07))
    cost_x = CARD_WIDTH - int(CARD_WIDTH * 0.05)
    cost_y = title_area_height // 2
    draw.text(
        (cost_x, cost_y), str(cost), font=cost_font, fill=COLORS["cost"], anchor="rm"
    )

    # Draw type
    type_font = get_font(int(CARD_HEIGHT * 0.045))
    type_y = title_area_height + int(CARD_HEIGHT * 0.5)
    draw.text(
        (CARD_WIDTH // 2, type_y),
        type,
        font=type_font,
        fill=COLORS["type"],
        anchor="mm",
    )

    # Draw ability
    ability_font = get_font(int(CARD_HEIGHT * 0.04))
    ability_x = int(CARD_WIDTH * 0.05)
    ability_y = type_y + int(CARD_HEIGHT * 0.06)
    ability_width = int(CARD_WIDTH * 0.9)

    avg_char_width = ability_font.getbbox("x")[2] - ability_font.getbbox("x")[0]
    wrapped_ability = textwrap.fill(
        ability, width=int(ability_width / avg_char_width * 1.5)
    )

    draw.multiline_text(
        (CARD_WIDTH // 2, ability_y),
        wrapped_ability,
        font=ability_font,
        fill=COLORS["ability"],
        align="center",
        anchor="ma",
        spacing=int(CARD_HEIGHT * 0.01),
    )

    # Draw attack
    atk_font = get_font(int(CARD_HEIGHT * 0.06))
    atk_x = int(CARD_WIDTH * 0.05)
    atk_y = CARD_HEIGHT - int(CARD_HEIGHT * 0.08)
    atk_text = f"{atk}"

    # Draw ATK text with outline
    outline_color = COLORS["stat_border"]
    for offset in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
        draw.text(
            (atk_x + offset[0], atk_y + offset[1]),
            atk_text,
            font=atk_font,
            fill=outline_color,
        )
    draw.text((atk_x, atk_y), atk_text, font=atk_font, fill=COLORS["stat_fill"])

    return card


def resize_and_crop(image, target_size):
    # Calculate the aspect ratios
    aspect_ratio_target = target_size[0] / target_size[1]
    aspect_ratio_image = image.width / image.height

    if aspect_ratio_image > aspect_ratio_target:
        # Image is wider, crop the sides
        new_width = int(image.height * aspect_ratio_target)
        left = (image.width - new_width) // 2
        image = image.crop((left, 0, left + new_width, image.height))
    else:
        # Image is taller, crop the top and bottom
        new_height = int(image.width / aspect_ratio_target)
        top = (image.height - new_height) // 2
        image = image.crop((0, top, image.width, top + new_height))

    # Resize the cropped image to the target size
    return image.resize(target_size, Image.LANCZOS)


def draw_rounded_corners(draw, width, height, radius, fill, border_width):
    draw.arc([0, 0, radius * 2, radius * 2], 180, 270, fill=fill, width=border_width)
    draw.arc(
        [width - radius * 2, 0, width, radius * 2],
        270,
        0,
        fill=fill,
        width=border_width,
    )
    draw.arc(
        [0, height - radius * 2, radius * 2, height],
        90,
        180,
        fill=fill,
        width=border_width,
    )
    draw.arc(
        [width - radius * 2, height - radius * 2, width, height],
        0,
        90,
        fill=fill,
        width=border_width,
    )

    draw.line([(radius, 0), (width - radius, 0)], fill=fill, width=border_width)
    draw.line(
        [(width, radius), (width, height - radius)], fill=fill, width=border_width
    )
    draw.line(
        [(radius, height), (width - radius, height)], fill=fill, width=border_width
    )
    draw.line([(0, radius), (0, height - radius)], fill=fill, width=border_width)


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
