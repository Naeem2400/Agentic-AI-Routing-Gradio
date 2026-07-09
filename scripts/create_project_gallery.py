from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFont


OUT_DIR = Path("project_gallery")
W, H = 1600, 1200


PALETTE = {
    "ink": "#17202a",
    "muted": "#52616b",
    "paper": "#f7f4ee",
    "white": "#ffffff",
    "teal": "#0f766e",
    "mint": "#ccfbf1",
    "blue": "#2563eb",
    "sky": "#dbeafe",
    "green": "#16a34a",
    "lime": "#dcfce7",
    "amber": "#f59e0b",
    "cream": "#fff7d6",
    "coral": "#f97316",
    "peach": "#ffedd5",
    "red": "#dc2626",
    "rose": "#fee2e2",
    "line": "#d7dce2",
    "dark": "#111827",
    "soft": "#eef2f7",
}


def find_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        f"/System/Library/Fonts/Supplemental/{name}.ttf",
        f"/System/Library/Fonts/Supplemental/{name}.otf",
        f"/Library/Fonts/{name}.ttf",
        f"/Library/Fonts/{name}.otf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default(size=size)


FONT = {
    "h1": find_font("Arial Bold", 78),
    "h2": find_font("Arial Bold", 56),
    "h3": find_font("Arial Bold", 36),
    "body": find_font("Arial", 28),
    "body_bold": find_font("Arial Bold", 28),
    "small": find_font("Arial", 22),
    "small_bold": find_font("Arial Bold", 22),
    "tiny": find_font("Arial", 18),
    "mono": find_font("Menlo", 24),
}


def text_size(draw: ImageDraw.ImageDraw, text: str, font) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def draw_wrapped(draw, text, xy, font, fill, width, line_gap=8):
    x, y = xy
    lines = []
    for para in text.split("\n"):
        if not para:
            lines.append("")
            continue
        current = ""
        for word in para.split():
            test = f"{current} {word}".strip()
            if text_size(draw, test, font)[0] <= width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += text_size(draw, "Ag", font)[1] + line_gap
    return y


def card(draw, xy, radius=28, fill="#ffffff", outline=None, width=2):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def pill(draw, xy, text, fill, ink=None, font=None):
    font = font or FONT["small_bold"]
    ink = ink or PALETTE["ink"]
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=(y2 - y1) // 2, fill=fill)
    tw, th = text_size(draw, text, font)
    draw.text((x1 + (x2 - x1 - tw) / 2, y1 + (y2 - y1 - th) / 2 - 2), text, font=font, fill=ink)


def arrow(draw, start, end, fill="#17202a", width=5):
    draw.line([start, end], fill=fill, width=width)
    ex, ey = end
    sx, sy = start
    if abs(ex - sx) > abs(ey - sy):
        direction = 1 if ex > sx else -1
        pts = [(ex, ey), (ex - direction * 18, ey - 10), (ex - direction * 18, ey + 10)]
    else:
        direction = 1 if ey > sy else -1
        pts = [(ex, ey), (ex - 10, ey - direction * 18), (ex + 10, ey - direction * 18)]
    draw.polygon(pts, fill=fill)


def base(title, subtitle=None):
    img = Image.new("RGB", (W, H), PALETTE["paper"])
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, W, 18), fill=PALETTE["teal"])
    draw.text((90, 72), title, font=FONT["h1"], fill=PALETTE["ink"])
    if subtitle:
        draw_wrapped(draw, subtitle, (94, 160), FONT["body"], PALETTE["muted"], 1000, 7)
    return img, draw


def footer(draw, label="Python | LangChain | LangGraph | Gradio"):
    draw.line((90, 1128, 1510, 1128), fill=PALETTE["line"], width=2)
    draw.text((90, 1150), label, font=FONT["small"], fill=PALETTE["muted"])
    draw.text((1170, 1150), "Portfolio Project Gallery", font=FONT["small_bold"], fill=PALETTE["teal"])


def mini_browser(draw, xy, title, lines, accent=PALETTE["teal"]):
    x, y, w, h = xy
    card(draw, (x, y, x + w, y + h), radius=24, fill=PALETTE["white"], outline=PALETTE["line"])
    draw.rounded_rectangle((x, y, x + w, y + 72), radius=24, fill="#edf2f7")
    draw.rectangle((x, y + 46, x + w, y + 72), fill="#edf2f7")
    for i, c in enumerate(["#ef4444", "#f59e0b", "#22c55e"]):
        draw.ellipse((x + 26 + i * 34, y + 26, x + 44 + i * 34, y + 44), fill=c)
    draw.text((x + 150, y + 24), title, font=FONT["small_bold"], fill=PALETTE["ink"])
    yy = y + 105
    for kind, text in lines:
        if kind == "user":
            bubble = (x + 42, yy, x + w - 250, yy + 72)
            fill = PALETTE["soft"]
            color = PALETTE["ink"]
        elif kind == "agent":
            bubble = (x + 230, yy, x + w - 42, yy + 84)
            fill = PALETTE["mint"]
            color = PALETTE["ink"]
        else:
            bubble = (x + 42, yy, x + w - 42, yy + 58)
            fill = PALETTE["sky"]
            color = PALETTE["blue"]
        draw.rounded_rectangle(bubble, radius=18, fill=fill)
        draw_wrapped(draw, text, (bubble[0] + 22, bubble[1] + 18), FONT["small"], color, bubble[2] - bubble[0] - 44, 4)
        yy = bubble[3] + 22
    draw.rounded_rectangle((x + 42, y + h - 80, x + w - 42, y + h - 28), radius=15, outline=PALETTE["line"], width=2)
    draw.text((x + 62, y + h - 65), "Ask the agent...", font=FONT["tiny"], fill=PALETTE["muted"])
    draw.rounded_rectangle((x + w - 160, y + h - 76, x + w - 52, y + h - 32), radius=14, fill=accent)
    draw.text((x + w - 130, y + h - 66), "Send", font=FONT["tiny"], fill=PALETTE["white"])


def node(draw, center, text, fill, outline=None, w=250, h=92):
    x, y = center
    box = (x - w // 2, y - h // 2, x + w // 2, y + h // 2)
    card(draw, box, radius=20, fill=fill, outline=outline or PALETTE["line"], width=3)
    tw, th = text_size(draw, text, FONT["body_bold"])
    draw.text((x - tw / 2, y - th / 2 - 2), text, font=FONT["body_bold"], fill=PALETTE["ink"])


def image_01_cover():
    img, draw = base(
        "Custom AI Agent Apps",
        "Beginner-friendly AI agents with tools, workflows, and web UI for real business tasks.",
    )
    pill(draw, (94, 245, 360, 295), "Groq / OpenAI", PALETTE["mint"], PALETTE["teal"])
    pill(draw, (385, 245, 640, 295), "LangGraph Flow", PALETTE["sky"], PALETTE["blue"])
    pill(draw, (665, 245, 900, 295), "Gradio Web UI", PALETTE["cream"], PALETTE["ink"])
    mini_browser(
        draw,
        (835, 285, 610, 660),
        "AI Agent Web App",
        [
            ("user", "Can you check my order and calculate my bill?"),
            ("agent", "Sure. I used order status and bill tools. Your total is Rs 1260."),
            ("tool", "Tools used: check_order_status + calculate_bill"),
        ],
    )
    items = [
        ("Tool calling", "Search, weather, menu, bill, date/time"),
        ("Agent workflows", "Clear routing with LangGraph nodes"),
        ("Browser app", "Simple Gradio interface for clients"),
        ("Documentation", "Notebook and source code included"),
    ]
    y = 365
    for title, body in items:
        card(draw, (95, y, 705, y + 118), radius=22, fill=PALETTE["white"], outline=PALETTE["line"])
        draw.ellipse((125, y + 34, 173, y + 82), fill=PALETTE["mint"])
        draw.text((195, y + 26), title, font=FONT["body_bold"], fill=PALETTE["ink"])
        draw.text((195, y + 64), body, font=FONT["small"], fill=PALETTE["muted"])
        y += 142
    footer(draw)
    return img


def image_02_first_agent():
    img, draw = base(
        "First Agent Demo",
        "A simple LangGraph agent without an LLM. It teaches the basic idea: state moves through nodes.",
    )
    mini_browser(
        draw,
        (90, 300, 650, 610),
        "first_notebook.ipynb",
        [
            ("user", "Run the graph with empty messages"),
            ("agent", "Hello From Pakistan"),
            ("tool", "START -> greet -> END"),
        ],
        accent=PALETTE["green"],
    )
    node(draw, (980, 420), "START", PALETTE["sky"], PALETTE["blue"])
    node(draw, (980, 590), "greet", PALETTE["mint"], PALETTE["teal"])
    node(draw, (980, 760), "END", PALETTE["cream"], PALETTE["amber"])
    arrow(draw, (980, 470), (980, 535), PALETTE["ink"])
    arrow(draw, (980, 645), (980, 705), PALETTE["ink"])
    card(draw, (1160, 360, 1460, 840), radius=24, fill=PALETTE["white"], outline=PALETTE["line"])
    draw.text((1195, 398), "Client value", font=FONT["h3"], fill=PALETTE["ink"])
    draw_wrapped(
        draw,
        "Great for education, prototypes, and explaining how agent state and graph flow work before adding paid APIs.",
        (1198, 462),
        FONT["body"],
        PALETTE["muted"],
        225,
        9,
    )
    footer(draw)
    return img


def image_03_restaurant_agent():
    img, draw = base(
        "Restaurant Agent Example",
        "A daily-life workflow that turns a customer order into clear agent steps.",
    )
    steps = [
        ("Take order", PALETTE["sky"]),
        ("Send to kitchen", PALETTE["mint"]),
        ("Cook food", PALETTE["cream"]),
        ("Serve customer", PALETTE["peach"]),
    ]
    xs = [245, 575, 905, 1235]
    for i, ((label, fill), x) in enumerate(zip(steps, xs)):
        node(draw, (x, 505), label, fill, w=260, h=110)
        if i < len(xs) - 1:
            arrow(draw, (x + 145, 505), (xs[i + 1] - 145, 505), PALETTE["ink"])
    card(draw, (130, 700, 720, 930), radius=26, fill=PALETTE["white"], outline=PALETTE["line"])
    draw.text((170, 738), "State", font=FONT["h3"], fill=PALETTE["ink"])
    draw_wrapped(draw, "The order paper carries the data: item, quantity, status, and final reply.", (170, 800), FONT["body"], PALETTE["muted"], 500)
    card(draw, (790, 700, 1380, 930), radius=26, fill=PALETTE["white"], outline=PALETTE["line"])
    draw.text((830, 738), "Graph flow", font=FONT["h3"], fill=PALETTE["ink"])
    draw_wrapped(draw, "The path tells the agent what happens first, next, and last.", (830, 800), FONT["body"], PALETTE["muted"], 500)
    footer(draw, "Restaurant bot | Agent state | Workflow demo")
    return img


def image_04_llm_gradio():
    img, draw = base(
        "LLM Chatbot With Gradio",
        "A browser-based AI assistant powered by Groq or OpenAI style chat models.",
    )
    mini_browser(
        draw,
        (105, 290, 760, 665),
        "llm_gradio_agent.ipynb",
        [
            ("user", "I want biryani. Can you help?"),
            ("agent", "Yes. I can answer, explain, and guide the user in a friendly way."),
            ("tool", "LLM response through Gradio UI"),
        ],
        accent=PALETTE["blue"],
    )
    card(draw, (950, 325, 1400, 860), radius=30, fill=PALETTE["white"], outline=PALETTE["line"])
    draw.text((990, 370), "What it includes", font=FONT["h3"], fill=PALETTE["ink"])
    features = ["Chat UI", "Groq/OpenAI setup", "Prompt design", "Easy notebook docs", "Runnable demo"]
    y = 450
    for item in features:
        draw.rounded_rectangle((995, y, 1037, y + 42), radius=12, fill=PALETTE["mint"])
        draw.text((1058, y + 4), item, font=FONT["body"], fill=PALETTE["ink"])
        y += 72
    footer(draw, "LLM chatbot | Gradio UI | Python notebook")
    return img


def image_05_routing_agent():
    img, draw = base(
        "Routing Agent Workflow",
        "The agent chooses the right path: refund, cook food, ask a question, call a tool, or end chat.",
    )
    node(draw, (220, 520), "User", PALETTE["soft"], w=190)
    node(draw, (510, 520), "Router", PALETTE["sky"], PALETTE["blue"], w=220)
    routes = [
        ("refund", 875, 330, PALETTE["rose"]),
        ("cook_food", 875, 455, PALETTE["cream"]),
        ("ask_question", 875, 580, PALETTE["mint"]),
        ("call_tool", 875, 705, PALETTE["sky"]),
        ("end_chat", 875, 830, PALETTE["peach"]),
    ]
    arrow(draw, (315, 520), (395, 520), PALETTE["ink"])
    for label, x, y, fill in routes:
        arrow(draw, (620, 520), (745, y), PALETTE["ink"], width=4)
        node(draw, (x, y), label, fill, w=270, h=86)
    card(draw, (1130, 350, 1460, 830), radius=26, fill=PALETTE["white"], outline=PALETTE["line"])
    draw.text((1170, 390), "Why it matters", font=FONT["h3"], fill=PALETTE["ink"])
    draw_wrapped(
        draw,
        "Real agents need decisions. Routing keeps the logic clean, testable, and easier to extend.",
        (1172, 460),
        FONT["body"],
        PALETTE["muted"],
        250,
        9,
    )
    footer(draw, "LangGraph routing | Decision paths | Tool calling")
    return img


def image_06_general_tools():
    img, draw = base(
        "General Tool Agent",
        "An assistant that can use live tools when the model does not know current information.",
    )
    cards = [
        ("Web Search", "latest news and current info", PALETTE["sky"]),
        ("Weather", "live city weather", PALETTE["mint"]),
        ("Date and Time", "current day and clock", PALETTE["cream"]),
        ("LLM Answer", "simple final response", PALETTE["peach"]),
    ]
    positions = [(120, 310), (820, 310), (120, 645), (820, 645)]
    for (title, body, fill), (x, y) in zip(cards, positions):
        card(draw, (x, y, x + 600, y + 235), radius=28, fill=PALETTE["white"], outline=PALETTE["line"])
        draw.rounded_rectangle((x + 28, y + 30, x + 122, y + 124), radius=22, fill=fill)
        draw.text((x + 155, y + 38), title, font=FONT["h3"], fill=PALETTE["ink"])
        draw_wrapped(draw, body, (x + 158, y + 98), FONT["body"], PALETTE["muted"], 370)
        pill(draw, (x + 158, y + 168, x + 360, y + 212), "custom tool", PALETTE["soft"], PALETTE["teal"], FONT["tiny"])
    footer(draw, "Search | Weather | Date/time | Tool-aware agent")
    return img


def image_07_custom_tools_phone():
    img, draw = base(
        "Custom Tools + Live UI",
        "A phone-style dashboard shows live clock and weather from the same tool functions.",
    )
    card(draw, (145, 270, 610, 1010), radius=48, fill=PALETTE["dark"])
    draw.rounded_rectangle((205, 320, 550, 370), radius=24, fill="#1f2937")
    draw.text((230, 333), "Agent Phone", font=FONT["small_bold"], fill=PALETTE["white"])
    card(draw, (205, 420, 550, 575), radius=28, fill=PALETTE["white"])
    draw.text((235, 452), "Current Date And Time", font=FONT["small_bold"], fill=PALETTE["muted"])
    draw_wrapped(draw, "Tuesday, July 07, 2026\n09:59 AM", (235, 492), FONT["body_bold"], PALETTE["ink"], 275)
    card(draw, (205, 625, 550, 815), radius=28, fill=PALETTE["sky"])
    draw.text((235, 657), "Weather In Karachi", font=FONT["small_bold"], fill=PALETTE["blue"])
    draw_wrapped(draw, "Temperature, humidity, and wind from live weather tool.", (235, 700), FONT["body"], PALETTE["ink"], 270)
    draw.text((230, 900), "Auto refresh every 10 sec", font=FONT["small"], fill="#d1d5db")
    tool_cards = [
        ("check_menu", "Menu and price"),
        ("check_order_status", "Track an order"),
        ("calculate_bill", "Exact total"),
        ("get_weather", "Live weather"),
        ("web_search", "Latest info"),
        ("get_current_datetime", "Current clock"),
    ]
    x, y = 735, 320
    for i, (title, body) in enumerate(tool_cards):
        yy = y + (i % 3) * 190
        xx = x + (i // 3) * 360
        card(draw, (xx, yy, xx + 320, yy + 145), radius=24, fill=PALETTE["white"], outline=PALETTE["line"])
        draw.text((xx + 28, yy + 28), title, font=FONT["body_bold"], fill=PALETTE["ink"])
        draw.text((xx + 28, yy + 78), body, font=FONT["small"], fill=PALETTE["muted"])
    footer(draw, "Custom tools | Phone-style UI | Live dashboard")
    return img


def image_08_benefits():
    img, draw = base(
        "What Clients Receive",
        "Clear deliverables for small business AI agent prototypes and learning demos.",
    )
    benefits = [
        ("Working agent app", "Runs in browser with Gradio"),
        ("Source code", "Clean Python and notebook files"),
        ("Custom tools", "Business logic, search, weather, billing"),
        ("Testing", "Example questions and expected outputs"),
        ("Documentation", "Simple setup and usage notes"),
        ("API guidance", "Groq/OpenAI key setup explained"),
    ]
    for i, (title, body) in enumerate(benefits):
        x = 110 + (i % 3) * 485
        y = 315 + (i // 3) * 245
        card(draw, (x, y, x + 430, y + 185), radius=26, fill=PALETTE["white"], outline=PALETTE["line"])
        draw.ellipse((x + 30, y + 38, x + 82, y + 90), fill=[PALETTE["mint"], PALETTE["sky"], PALETTE["cream"]][i % 3])
        draw.text((x + 105, y + 34), title, font=FONT["body_bold"], fill=PALETTE["ink"])
        draw_wrapped(draw, body, (x + 105, y + 78), FONT["small"], PALETTE["muted"], 275)
    card(draw, (240, 865, 1360, 990), radius=30, fill=PALETTE["mint"], outline=PALETTE["teal"])
    draw.text((300, 900), "Best for:", font=FONT["h3"], fill=PALETTE["ink"])
    draw.text((505, 909), "customer support demos, restaurant bots, tool agents, and AI prototypes", font=FONT["body"], fill=PALETTE["ink"])
    footer(draw, "Deliverables | Benefits | Client-ready project")
    return img


def save_all():
    OUT_DIR.mkdir(exist_ok=True)
    images = [
        ("01_cover_custom_ai_agent_apps.png", image_01_cover()),
        ("02_first_agent_demo.png", image_02_first_agent()),
        ("03_restaurant_agent_workflow.png", image_03_restaurant_agent()),
        ("04_llm_gradio_chatbot_ui.png", image_04_llm_gradio()),
        ("05_routing_agent_workflow.png", image_05_routing_agent()),
        ("06_general_tool_agent.png", image_06_general_tools()),
        ("07_custom_tools_phone_weather_ui.png", image_07_custom_tools_phone()),
        ("08_client_benefits_deliverables.png", image_08_benefits()),
    ]
    for name, img in images:
        path = OUT_DIR / name
        img.save(path, optimize=True)
        print(path)


if __name__ == "__main__":
    save_all()
