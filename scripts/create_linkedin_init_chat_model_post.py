from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT_DIR = Path("linkedin_posts")
W, H = 1600, 1600


C = {
    "bg": "#f7faf8",
    "ink": "#17202a",
    "muted": "#5b6670",
    "white": "#ffffff",
    "line": "#d7dee5",
    "teal": "#0f766e",
    "mint": "#ccfbf1",
    "blue": "#2563eb",
    "sky": "#dbeafe",
    "cream": "#fff7d6",
    "peach": "#ffedd5",
    "dark": "#111827",
    "soft": "#eef2f7",
}


def font(name: str, size: int):
    paths = [
        f"/System/Library/Fonts/Supplemental/{name}.ttf",
        f"/System/Library/Fonts/Supplemental/{name}.otf",
        f"/Library/Fonts/{name}.ttf",
        f"/Library/Fonts/{name}.otf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


F = {
    "hero": font("Arial Bold", 82),
    "title": font("Arial Bold", 58),
    "h2": font("Arial Bold", 42),
    "body": font("Arial", 30),
    "body_bold": font("Arial Bold", 30),
    "small": font("Arial", 24),
    "small_bold": font("Arial Bold", 24),
    "tiny": font("Arial", 20),
    "mono": font("Menlo", 24),
    "mono_small": font("Menlo", 18),
}


def size(draw, text, f):
    box = draw.textbbox((0, 0), text, font=f)
    return box[2] - box[0], box[3] - box[1]


def wrap(draw, text, xy, f, fill, width, gap=8):
    x, y = xy
    lines = []
    for para in text.split("\n"):
        if not para.strip():
            lines.append("")
            continue
        current = ""
        for word in para.split():
            test = f"{current} {word}".strip()
            if size(draw, test, f)[0] <= width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    for line in lines:
        draw.text((x, y), line, font=f, fill=fill)
        y += size(draw, "Ag", f)[1] + gap
    return y


def card(draw, xy, fill=C["white"], outline=C["line"], radius=28, width=2):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def shadow_card(draw, xy, fill=C["white"], outline=C["line"], radius=28):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle((x1 + 10, y1 + 12, x2 + 10, y2 + 12), radius=radius, fill="#dfe6ec")
    card(draw, xy, fill=fill, outline=outline, radius=radius)


def pill(draw, xy, text, fill, ink=C["ink"]):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=(y2 - y1) // 2, fill=fill)
    tw, th = size(draw, text, F["small_bold"])
    draw.text((x1 + (x2 - x1 - tw) / 2, y1 + (y2 - y1 - th) / 2 - 2), text, font=F["small_bold"], fill=ink)


def code_block(draw, xy, lines):
    x1, y1, x2, y2 = xy
    card(draw, xy, fill=C["dark"], outline=C["dark"], radius=24)
    y = y1 + 32
    for line in lines:
        color = "#e5e7eb"
        if line.strip().startswith("#"):
            color = "#93c5fd"
        if "init_chat_model" in line or "ChatGroq" in line:
            color = "#5eead4"
        draw.text((x1 + 34, y), line, font=F["mono_small"], fill=color)
        y += 34


def footer(draw):
    draw.line((95, 1512, 1505, 1512), fill=C["line"], width=2)
    draw.text((95, 1536), "LangChain learning notes | Specific class vs init_chat_model", font=F["small"], fill=C["muted"])


def image_01():
    img = Image.new("RGB", (W, H), C["bg"])
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, W, 18), fill=C["teal"])
    draw.text((95, 90), "LangChain init_chat_model", font=F["hero"], fill=C["ink"])
    wrap(draw, "Two ways to create chat models for AI agents.", (100, 195), F["body"], C["muted"], 1000)
    pill(draw, (100, 285, 350, 340), "Specific class", C["sky"], C["blue"])
    pill(draw, (375, 285, 650, 340), "Universal setup", C["mint"], C["teal"])

    shadow_card(draw, (95, 425, 760, 1160), fill=C["white"])
    draw.text((140, 470), "1. Specific Class", font=F["h2"], fill=C["ink"])
    wrap(draw, "Use the provider class directly when you already know the provider.", (142, 535), F["small"], C["muted"], 550)
    code_block(
        draw,
        (140, 645, 715, 920),
        [
            "from langchain_groq import ChatGroq",
            "",
            "llm = ChatGroq(",
            "    model=\"llama-3.3-70b-versatile\",",
            "    temperature=0",
            ")",
        ],
    )
    wrap(draw, "Best when you need provider-specific settings or a simple one-provider project.", (142, 965), F["small"], C["ink"], 550)

    shadow_card(draw, (840, 425, 1505, 1160), fill=C["white"])
    draw.text((885, 470), "2. Universal Initializer", font=F["h2"], fill=C["ink"])
    wrap(draw, "Use one LangChain function to initialize many providers.", (887, 535), F["small"], C["muted"], 550)
    code_block(
        draw,
        (885, 645, 1460, 920),
        [
            "from langchain.chat_models import init_chat_model",
            "",
            "llm = init_chat_model(",
            "    \"groq:llama-3.3-70b-versatile\",",
            "    temperature=0",
            ")",
        ],
    )
    wrap(draw, "Best when you want flexible code that can switch providers later.", (887, 965), F["small"], C["ink"], 550)

    card(draw, (220, 1265, 1380, 1405), fill=C["mint"], outline=C["teal"], radius=30)
    draw.text((275, 1305), "Simple idea:", font=F["body_bold"], fill=C["ink"])
    draw.text((465, 1305), "specific class = one provider, init_chat_model = flexible setup", font=F["body"], fill=C["ink"])
    footer(draw)
    return img


def image_02():
    img = Image.new("RGB", (W, H), "#eff6ff")
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, W, 18), fill=C["blue"])
    draw.text((95, 90), "When should you use which?", font=F["hero"], fill=C["ink"])
    wrap(draw, "Both are correct. Choose based on your project style.", (100, 195), F["body"], C["muted"], 1000)

    blocks = [
        (
            "Use Specific Class",
            C["sky"],
            [
                "You know the provider",
                "You want direct provider features",
                "Your app uses one model family",
                "Beginner-friendly imports",
            ],
        ),
        (
            "Use init_chat_model",
            C["mint"],
            [
                "You may switch models later",
                "Provider comes from config",
                "You want one common pattern",
                "Good for reusable agent code",
            ],
        ),
    ]

    for i, (title, fill, bullets) in enumerate(blocks):
        x = 110 + i * 740
        shadow_card(draw, (x, 360, x + 640, 1010), fill=C["white"])
        draw.rounded_rectangle((x + 42, 410, x + 598, 495), radius=24, fill=fill)
        tw, th = size(draw, title, F["h2"])
        draw.text((x + 320 - tw / 2, 432), title, font=F["h2"], fill=C["ink"])
        y = 585
        for bullet in bullets:
            draw.rounded_rectangle((x + 60, y + 4, x + 105, y + 49), radius=12, fill=C["mint"] if i == 0 else C["sky"])
            draw.text((x + 72, y + 10), "OK", font=F["tiny"], fill=C["teal"] if i == 0 else C["blue"])
            draw.text((x + 130, y + 8), bullet, font=F["body"], fill=C["ink"])
            y += 82

    card(draw, (170, 1120, 1430, 1335), fill=C["white"], radius=30)
    draw.text((230, 1160), "My rule:", font=F["h2"], fill=C["teal"])
    wrap(
        draw,
        "Start with the specific class while learning. Use init_chat_model when your agent should support multiple providers like Groq, Gemini, Mistral, Anthropic, xAI, or OpenAI.",
        (230, 1225),
        F["body"],
        C["muted"],
        1140,
        8,
    )
    footer(draw)
    return img


def main():
    OUT_DIR.mkdir(exist_ok=True)
    files = [
        ("01_init_chat_model_comparison.png", image_01()),
        ("02_init_chat_model_when_to_use.png", image_02()),
    ]
    for name, img in files:
        path = OUT_DIR / name
        img.save(path, optimize=True)
        print(path)


if __name__ == "__main__":
    main()
