from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageFont


OUT_DIR = Path("upwork_client_gallery")
W, H = 1600, 1200


C = {
    "ink": "#17202a",
    "muted": "#566573",
    "white": "#ffffff",
    "line": "#d9e1e8",
    "teal": "#0f766e",
    "teal_dark": "#134e4a",
    "mint": "#ccfbf1",
    "blue": "#2563eb",
    "sky": "#dbeafe",
    "green": "#16a34a",
    "lime": "#dcfce7",
    "amber": "#f59e0b",
    "cream": "#fff7d6",
    "orange": "#f97316",
    "peach": "#ffedd5",
    "rose": "#fee2e2",
    "red": "#dc2626",
    "purple": "#7c3aed",
    "lav": "#ede9fe",
    "dark": "#111827",
    "soft": "#eef4f8",
    "paper": "#f8faf8",
}


def find_font(name: str, size: int):
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
    "hero": find_font("Arial Bold", 82),
    "title": find_font("Arial Bold", 62),
    "h2": find_font("Arial Bold", 42),
    "h3": find_font("Arial Bold", 32),
    "body": find_font("Arial", 28),
    "body_bold": find_font("Arial Bold", 28),
    "small": find_font("Arial", 22),
    "small_bold": find_font("Arial Bold", 22),
    "tiny": find_font("Arial", 18),
    "mono": find_font("Menlo", 22),
}


def hex_to_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    ar, ag, ab = hex_to_rgb(a)
    br, bg, bb = hex_to_rgb(b)
    return (
        int(ar + (br - ar) * t),
        int(ag + (bg - ag) * t),
        int(ab + (bb - ab) * t),
    )


def gradient(c1="#f8faf8", c2="#dbeafe"):
    img = Image.new("RGB", (W, H), c1)
    pix = img.load()
    for y in range(H):
        t = y / (H - 1)
        row = mix(c1, c2, t)
        for x in range(W):
            pix[x, y] = row
    return img


def size(draw, text, font):
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def wrap(draw, text, xy, font, fill, width, gap=8):
    x, y = xy
    lines = []
    for para in text.split("\n"):
        current = ""
        for word in para.split():
            test = f"{current} {word}".strip()
            if size(draw, test, font)[0] <= width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += size(draw, "Ag", font)[1] + gap
    return y


def card(draw, xy, fill=C["white"], outline=C["line"], radius=28, width=2):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def shadow_card(draw, xy, fill=C["white"], outline=C["line"], radius=28):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle((x1 + 10, y1 + 12, x2 + 10, y2 + 12), radius=radius, fill="#dbe3ea")
    card(draw, xy, fill=fill, outline=outline, radius=radius)


def pill(draw, xy, text, fill, ink=C["ink"], font=None):
    font = font or F["small_bold"]
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=(y2 - y1) // 2, fill=fill)
    tw, th = size(draw, text, font)
    draw.text((x1 + (x2 - x1 - tw) / 2, y1 + (y2 - y1 - th) / 2 - 2), text, font=font, fill=ink)


def header(draw, title, subtitle=None, dark=False):
    color = C["white"] if dark else C["ink"]
    muted = "#d5e8ef" if dark else C["muted"]
    draw.text((90, 72), title, font=F["title"], fill=color)
    if subtitle:
        wrap(draw, subtitle, (94, 150), F["body"], muted, 980, 8)


def footer(draw, text="Custom AI Agent Apps | Python | LangChain | LangGraph | Web UI"):
    draw.line((90, 1128, 1510, 1128), fill=C["line"], width=2)
    draw.text((90, 1150), text, font=F["small"], fill=C["muted"])


def robot(draw, cx, cy, scale=1.0, outfit="default", point=False):
    s = scale
    # legs / base
    draw.rounded_rectangle((cx - 86*s, cy + 178*s, cx + 86*s, cy + 230*s), radius=int(24*s), fill="#cbd5e1", outline="#64748b", width=max(1, int(3*s)))
    # body
    body = (cx - 105*s, cy + 15*s, cx + 105*s, cy + 190*s)
    draw.rounded_rectangle(body, radius=int(34*s), fill="#f1f5f9", outline="#64748b", width=max(1, int(4*s)))
    draw.rounded_rectangle((cx - 54*s, cy + 74*s, cx + 54*s, cy + 142*s), radius=int(20*s), fill="#0f172a")
    draw.ellipse((cx - 22*s, cy + 95*s, cx + 22*s, cy + 129*s), fill="#22d3ee")
    # neck and head
    draw.rounded_rectangle((cx - 32*s, cy - 24*s, cx + 32*s, cy + 24*s), radius=int(10*s), fill="#cbd5e1", outline="#64748b", width=max(1, int(2*s)))
    draw.rounded_rectangle((cx - 92*s, cy - 158*s, cx + 92*s, cy - 18*s), radius=int(42*s), fill="#f8fafc", outline="#64748b", width=max(1, int(4*s)))
    draw.rounded_rectangle((cx - 55*s, cy - 113*s, cx + 55*s, cy - 64*s), radius=int(20*s), fill="#111827")
    draw.ellipse((cx - 37*s, cy - 98*s, cx - 17*s, cy - 78*s), fill="#38bdf8")
    draw.ellipse((cx + 17*s, cy - 98*s, cx + 37*s, cy - 78*s), fill="#38bdf8")
    draw.arc((cx - 28*s, cy - 86*s, cx + 28*s, cy - 47*s), start=20, end=160, fill="#93c5fd", width=max(1, int(3*s)))
    # ears
    draw.ellipse((cx - 112*s, cy - 95*s, cx - 88*s, cy - 65*s), fill="#94a3b8")
    draw.ellipse((cx + 88*s, cy - 95*s, cx + 112*s, cy - 65*s), fill="#94a3b8")
    # arms
    left_arm = [(cx - 104*s, cy + 52*s), (cx - 202*s, cy + 115*s), (cx - 184*s, cy + 145*s), (cx - 83*s, cy + 93*s)]
    right_arm = [(cx + 104*s, cy + 52*s), (cx + 202*s, cy + 115*s), (cx + 184*s, cy + 145*s), (cx + 83*s, cy + 93*s)]
    if point:
        right_arm = [(cx + 102*s, cy + 48*s), (cx + 226*s, cy - 32*s), (cx + 242*s, cy - 5*s), (cx + 120*s, cy + 78*s)]
    draw.polygon(left_arm, fill="#e2e8f0", outline="#64748b")
    draw.polygon(right_arm, fill="#e2e8f0", outline="#64748b")
    draw.ellipse((cx - 220*s, cy + 110*s, cx - 172*s, cy + 158*s), fill="#f8fafc", outline="#64748b", width=max(1, int(3*s)))
    if point:
        draw.ellipse((cx + 226*s, cy - 48*s, cx + 274*s, cy + 0*s), fill="#f8fafc", outline="#64748b", width=max(1, int(3*s)))
        draw.line((cx + 255*s, cy - 35*s, cx + 305*s, cy - 72*s), fill="#64748b", width=max(1, int(4*s)))
    else:
        draw.ellipse((cx + 172*s, cy + 110*s, cx + 220*s, cy + 158*s), fill="#f8fafc", outline="#64748b", width=max(1, int(3*s)))
    # outfit overlays
    if outfit == "chef":
        draw.ellipse((cx - 100*s, cy - 226*s, cx - 18*s, cy - 142*s), fill=C["white"], outline="#cbd5e1", width=max(1, int(3*s)))
        draw.ellipse((cx - 35*s, cy - 245*s, cx + 55*s, cy - 150*s), fill=C["white"], outline="#cbd5e1", width=max(1, int(3*s)))
        draw.ellipse((cx + 25*s, cy - 220*s, cx + 105*s, cy - 140*s), fill=C["white"], outline="#cbd5e1", width=max(1, int(3*s)))
        draw.rounded_rectangle((cx - 100*s, cy - 172*s, cx + 100*s, cy - 130*s), radius=int(18*s), fill=C["white"], outline="#cbd5e1", width=max(1, int(3*s)))
        draw.rounded_rectangle((cx - 82*s, cy + 25*s, cx + 82*s, cy + 185*s), radius=int(20*s), fill=C["white"], outline="#cbd5e1", width=max(1, int(3*s)))
        draw.text((cx - 34*s, cy + 65*s), "MENU", font=F["tiny"], fill=C["orange"])
    elif outfit == "doctor":
        draw.polygon([(cx - 105*s, cy + 35*s), (cx - 14*s, cy + 190*s), (cx - 88*s, cy + 190*s)], fill=C["white"], outline="#cbd5e1")
        draw.polygon([(cx + 105*s, cy + 35*s), (cx + 14*s, cy + 190*s), (cx + 88*s, cy + 190*s)], fill=C["white"], outline="#cbd5e1")
        draw.rounded_rectangle((cx - 18*s, cy + 35*s, cx + 18*s, cy + 190*s), radius=int(10*s), fill=C["sky"])
        draw.ellipse((cx - 62*s, cy + 68*s, cx + 62*s, cy + 150*s), outline=C["teal"], width=max(1, int(5*s)))
        draw.rounded_rectangle((cx + 48*s, cy + 35*s, cx + 90*s, cy + 70*s), radius=int(6*s), fill=C["rose"])
        draw.text((cx + 58*s, cy + 39*s), "+", font=F["small_bold"], fill=C["red"])
    elif outfit == "support":
        draw.arc((cx - 120*s, cy - 138*s, cx + 120*s, cy + 22*s), start=190, end=350, fill=C["dark"], width=max(1, int(8*s)))
        draw.rounded_rectangle((cx - 122*s, cy - 58*s, cx - 88*s, cy + 4*s), radius=int(10*s), fill=C["dark"])
        draw.rounded_rectangle((cx + 88*s, cy - 58*s, cx + 122*s, cy + 4*s), radius=int(10*s), fill=C["dark"])
        draw.line((cx + 90*s, cy - 5*s, cx + 138*s, cy + 32*s), fill=C["dark"], width=max(1, int(5*s)))
        draw.ellipse((cx + 132*s, cy + 24*s, cx + 152*s, cy + 44*s), fill=C["teal"])
    elif outfit == "business":
        draw.polygon([(cx - 90*s, cy + 25*s), (cx, cy + 110*s), (cx + 90*s, cy + 25*s), (cx + 105*s, cy + 190*s), (cx - 105*s, cy + 190*s)], fill="#1f2937")
        draw.polygon([(cx - 38*s, cy + 28*s), (cx, cy + 105*s), (cx + 38*s, cy + 28*s)], fill=C["white"])
        draw.polygon([(cx - 12*s, cy + 54*s), (cx + 12*s, cy + 54*s), (cx + 24*s, cy + 145*s), (cx, cy + 174*s), (cx - 24*s, cy + 145*s)], fill=C["teal"])


def app_window(draw, xy, title, rows, accent=C["teal"]):
    x1, y1, x2, y2 = xy
    shadow_card(draw, xy, fill=C["white"], radius=28)
    draw.rounded_rectangle((x1, y1, x2, y1 + 74), radius=28, fill="#edf2f7")
    draw.rectangle((x1, y1 + 48, x2, y1 + 74), fill="#edf2f7")
    for i, col in enumerate(["#ef4444", "#f59e0b", "#22c55e"]):
        draw.ellipse((x1 + 28 + i * 34, y1 + 28, x1 + 46 + i * 34, y1 + 46), fill=col)
    draw.text((x1 + 155, y1 + 24), title, font=F["small_bold"], fill=C["ink"])
    y = y1 + 112
    for label, value, fill in rows:
        card(draw, (x1 + 42, y, x2 - 42, y + 72), fill=fill, outline=None, radius=18)
        draw.text((x1 + 65, y + 18), label, font=F["small_bold"], fill=C["ink"])
        draw.text((x2 - 230, y + 21), value, font=F["small"], fill=accent)
        y += 92


def service_list(draw, x, y, items, color=C["teal"]):
    for item in items:
        draw.rounded_rectangle((x, y + 4, x + 42, y + 46), radius=12, fill=C["mint"])
        draw.text((x + 12, y + 8), "OK", font=F["tiny"], fill=color)
        draw.text((x + 60, y + 8), item, font=F["body"], fill=C["ink"])
        y += 64


def image_cover():
    img = gradient("#effdfb", "#dbeafe")
    draw = ImageDraw.Draw(img)
    draw.ellipse((-300, 80, 850, 1240), outline="#8bd8df", width=8)
    robot(draw, 350, 620, 1.55, outfit="default", point=True)
    header(draw, "AI Agent Apps", "Custom assistants for business workflows, support, orders, research, billing, and automation.")
    draw.text((865, 300), "I build", font=F["h2"], fill=C["muted"])
    draw.text((865, 358), "custom AI agents", font=F["hero"], fill=C["teal_dark"])
    draw.text((865, 458), "that use tools", font=F["hero"], fill=C["ink"])
    pill(draw, (870, 590, 1120, 646), "Web App UI", C["white"], C["teal"])
    pill(draw, (1145, 590, 1410, 646), "Custom Tools", C["cream"], C["ink"])
    pill(draw, (870, 670, 1120, 726), "Automation", C["mint"], C["teal"])
    pill(draw, (1145, 670, 1410, 726), "Source Code", C["sky"], C["blue"])
    card(draw, (870, 820, 1430, 960), fill=C["white"], radius=26)
    wrap(draw, "For startups, clinics, restaurants, service businesses, creators, and small teams.", (910, 858), F["body"], C["muted"], 480)
    footer(draw, "AI agent development | Client-ready apps | Custom business tools")
    return img


def image_services():
    img = gradient("#f8faf8", "#eef2ff")
    draw = ImageDraw.Draw(img)
    header(draw, "AI Agent Services", "Client-facing solutions, not only a tutorial or one Gradio demo.")
    services = [
        ("Customer Support", "FAQ, returns, service replies", C["mint"]),
        ("Order Assistant", "status, menu, invoice, tracking", C["sky"]),
        ("Lead Agent", "collect details and qualify leads", C["cream"]),
        ("Document Q&A", "summaries and answers from docs", C["lav"]),
        ("Research Agent", "web search and latest info", C["lime"]),
        ("Booking Flow", "appointments and reminders", C["peach"]),
        ("Billing Tool", "exact totals and estimates", C["rose"]),
        ("Dashboard UI", "simple panels and reports", C["soft"]),
    ]
    for i, (title, body, fill) in enumerate(services):
        x = 90 + (i % 4) * 370
        y = 280 + (i // 4) * 260
        shadow_card(draw, (x, y, x + 320, y + 180), fill=C["white"], radius=26)
        draw.rounded_rectangle((x + 30, y + 34, x + 92, y + 96), radius=18, fill=fill)
        draw.text((x + 120, y + 36), title, font=F["body_bold"], fill=C["ink"])
        wrap(draw, body, (x + 120, y + 78), F["small"], C["muted"], 170, 4)
    card(draw, (260, 900, 1340, 1005), fill=C["mint"], outline=C["teal"], radius=28)
    draw.text((325, 934), "Build an agent around your real business process.", font=F["h3"], fill=C["ink"])
    footer(draw, "Support | Leads | Orders | Documents | Research | Business automation")
    return img


def image_doctor():
    img = gradient("#eff6ff", "#f8faf8")
    draw = ImageDraw.Draw(img)
    header(draw, "Clinic Assistant Agent", "A helpful AI assistant for appointments, patient intake, clinic FAQs, and admin tasks.")
    robot(draw, 350, 660, 1.38, outfit="doctor")
    app_window(
        draw,
        (760, 250, 1445, 805),
        "Clinic Agent UI",
        [
            ("Appointment", "Book / reschedule", C["sky"]),
            ("Patient Intake", "Collect details", C["mint"]),
            ("Clinic FAQs", "Hours and services", C["cream"]),
            ("Admin Summary", "Prepare notes", C["soft"]),
        ],
        accent=C["blue"],
    )
    card(draw, (760, 865, 1445, 990), fill=C["white"], radius=28)
    wrap(draw, "Designed for admin support and information flow. Not a medical diagnosis tool.", (800, 902), F["body"], C["muted"], 590)
    footer(draw, "Healthcare admin support | Appointments | Intake | FAQs")
    return img


def image_restaurant():
    img = gradient("#fff7ed", "#ecfeff")
    draw = ImageDraw.Draw(img)
    header(draw, "Restaurant Agent", "A friendly food-order assistant for menus, order status, bills, and customer replies.")
    robot(draw, 370, 675, 1.38, outfit="chef")
    app_window(
        draw,
        (760, 245, 1445, 800),
        "Restaurant Agent UI",
        [
            ("Menu Checker", "Prices and items", C["cream"]),
            ("Order Status", "Cooking / delivery", C["sky"]),
            ("Bill Calculator", "Exact total", C["mint"]),
            ("Customer Reply", "Clear answer", C["peach"]),
        ],
        accent=C["orange"],
    )
    card(draw, (760, 865, 1445, 990), fill=C["white"], radius=28)
    wrap(draw, "Example: biryani orders, delivery updates, refund routing, and daily menu questions.", (800, 902), F["body"], C["muted"], 590)
    footer(draw, "Restaurant support | Menu | Orders | Billing | Customer replies")
    return img


def image_support():
    img = gradient("#f8faf8", "#dbeafe")
    draw = ImageDraw.Draw(img)
    header(draw, "Customer Support Agent", "Answer common questions, guide users, and reduce repeated manual replies.")
    robot(draw, 350, 670, 1.36, outfit="support")
    # chat cards
    shadow_card(draw, (750, 245, 1450, 880), fill=C["white"], radius=28)
    draw.text((800, 292), "Support Inbox", font=F["h2"], fill=C["ink"])
    bubbles = [
        ("Customer", "Where is my order?", C["soft"], 800, 385, 1220),
        ("Agent", "I checked the order tool. It is out for delivery.", C["mint"], 920, 500, 1395),
        ("Customer", "Can you send the total?", C["soft"], 800, 620, 1210),
        ("Agent", "Sure. The bill calculator shows Rs 1260.", C["sky"], 920, 735, 1395),
    ]
    for role, text, fill, x1, y1, x2 in bubbles:
        card(draw, (x1, y1, x2, y1 + 82), fill=fill, outline=None, radius=22)
        draw.text((x1 + 24, y1 + 16), role, font=F["tiny"], fill=C["muted"])
        draw.text((x1 + 24, y1 + 43), text, font=F["small"], fill=C["ink"])
    footer(draw, "Customer service | Tool replies | Faster support workflow")
    return img


def image_business():
    img = gradient("#eef2ff", "#f8faf8")
    draw = ImageDraw.Draw(img)
    header(draw, "Business Workflow Agent", "Automate small repeated tasks with a clear AI workflow and app dashboard.")
    robot(draw, 355, 675, 1.38, outfit="business")
    shadow_card(draw, (760, 240, 1445, 880), fill=C["white"], radius=28)
    draw.text((815, 290), "Workflow Dashboard", font=F["h2"], fill=C["ink"])
    metrics = [("Leads", "24", C["sky"]), ("Tasks", "18", C["mint"]), ("Reports", "7", C["cream"])]
    for i, (label, value, fill) in enumerate(metrics):
        x = 815 + i * 200
        card(draw, (x, 360, x + 165, 475), fill=fill, outline=None, radius=22)
        draw.text((x + 28, 388), label, font=F["small_bold"], fill=C["muted"])
        draw.text((x + 52, 425), value, font=F["h2"], fill=C["ink"])
    rows = ["Qualify new lead", "Summarize document", "Draft customer reply", "Prepare daily report"]
    y = 555
    for row in rows:
        draw.rounded_rectangle((820, y, 880, y + 50), radius=14, fill=C["mint"])
        draw.text((838, y + 10), "OK", font=F["tiny"], fill=C["teal"])
        draw.text((905, y + 10), row, font=F["body"], fill=C["ink"])
        y += 72
    footer(draw, "Lead flow | Reports | Task automation | Business dashboard")
    return img


def image_app_options():
    img = gradient("#f8faf8", "#ecfeff")
    draw = ImageDraw.Draw(img)
    header(draw, "App UI Options", "Your agent is not limited to one interface. I can prepare the right demo surface.")
    ui_cards = [
        ("Web Chat App", "simple browser chatbot", C["mint"]),
        ("Admin Dashboard", "tool results and reports", C["sky"]),
        ("Mobile Style UI", "phone-like assistant screen", C["cream"]),
        ("API Backend", "connect agent to an app", C["lav"]),
    ]
    for i, (title, body, fill) in enumerate(ui_cards):
        x = 100 + (i % 2) * 720
        y = 285 + (i // 2) * 300
        shadow_card(draw, (x, y, x + 600, y + 220), fill=C["white"], radius=28)
        draw.rounded_rectangle((x + 35, y + 40, x + 130, y + 135), radius=22, fill=fill)
        draw.text((x + 165, y + 46), title, font=F["h3"], fill=C["ink"])
        wrap(draw, body, (x + 165, y + 96), F["body"], C["muted"], 360, 8)
        pill(draw, (x + 165, y + 154, x + 360, y + 202), "client demo", C["soft"], C["teal"], F["tiny"])
    footer(draw, "Gradio | Streamlit-style dashboards | Web apps | API-ready prototypes")
    return img


def image_integrations():
    img = gradient("#f8faf8", "#fff7ed")
    draw = ImageDraw.Draw(img)
    header(draw, "Custom Tools & Integrations", "Connect your agent to useful business data and actions.")
    center = (800, 555)
    card(draw, (center[0] - 150, center[1] - 85, center[0] + 150, center[1] + 85), fill=C["mint"], outline=C["teal"], radius=30, width=4)
    draw.text((center[0] - 95, center[1] - 23), "AI Agent", font=F["h2"], fill=C["ink"])
    nodes = [
        ("Website", 295, 320, C["sky"]),
        ("Documents", 610, 260, C["lav"]),
        ("Spreadsheet", 1000, 260, C["lime"]),
        ("Database", 1300, 320, C["soft"]),
        ("Email", 330, 790, C["peach"]),
        ("Calendar", 645, 870, C["cream"]),
        ("Payment", 1000, 870, C["rose"]),
        ("API", 1300, 790, C["mint"]),
    ]
    for label, x, y, fill in nodes:
        draw.line((center[0], center[1], x, y), fill=C["line"], width=4)
        card(draw, (x - 120, y - 45, x + 120, y + 45), fill=fill, outline=C["line"], radius=22)
        tw, th = size(draw, label, F["body_bold"])
        draw.text((x - tw / 2, y - th / 2 - 2), label, font=F["body_bold"], fill=C["ink"])
    footer(draw, "Tools | APIs | Documents | Spreadsheets | Email | Calendar | Database")
    return img


def image_stack():
    img = gradient("#eff6ff", "#f8faf8")
    draw = ImageDraw.Draw(img)
    header(draw, "Modern AI Agent Stack", "Flexible model and framework choices based on project needs.")
    blocks = [
        ("LLM Models", ["Groq", "OpenAI", "Gemini", "DeepSeek"], C["sky"]),
        ("Agent Logic", ["LangChain", "LangGraph", "Routing", "Memory"], C["mint"]),
        ("Custom Tools", ["Search", "Weather", "Calculator", "Business Data"], C["cream"]),
        ("User Interface", ["Gradio", "Dashboard", "Web App", "API"], C["peach"]),
    ]
    for i, (title, items, fill) in enumerate(blocks):
        x = 120 + i * 365
        shadow_card(draw, (x, 305, x + 310, 825), fill=C["white"], radius=28)
        draw.rounded_rectangle((x + 35, 350, x + 275, 430), radius=24, fill=fill)
        tw, th = size(draw, title, F["body_bold"])
        draw.text((x + 155 - tw / 2, 376), title, font=F["body_bold"], fill=C["ink"])
        y = 505
        for item in items:
            draw.rounded_rectangle((x + 40, y + 2, x + 74, y + 36), radius=10, fill=C["mint"])
            draw.text((x + 88, y + 2), item, font=F["small"], fill=C["muted"])
            y += 62
    card(draw, (270, 905, 1330, 1015), fill=C["white"], radius=28)
    wrap(draw, "I choose the simple, cost-friendly setup for your use case and explain how to run it.", (320, 940), F["body"], C["muted"], 960)
    footer(draw, "LLM models | Agent workflows | Custom tools | Web UI")
    return img


def image_deliverables():
    img = gradient("#f8faf8", "#eef2ff")
    draw = ImageDraw.Draw(img)
    header(draw, "What You Receive", "A complete prototype package that a client can test and understand.")
    robot(draw, 310, 670, 1.25, outfit="default", point=True)
    items = [
        ("Working AI agent app", "ready to test in browser"),
        ("Custom tool functions", "business logic and actions"),
        ("Source code", "clean Python files/notebooks"),
        ("Setup guide", "easy run instructions"),
        ("Testing examples", "sample questions and outputs"),
        ("Documentation", "what the agent does"),
    ]
    for i, (title, body) in enumerate(items):
        x = 700 + (i % 2) * 390
        y = 275 + (i // 2) * 190
        shadow_card(draw, (x, y, x + 340, y + 135), fill=C["white"], radius=24)
        draw.ellipse((x + 26, y + 36, x + 74, y + 84), fill=[C["mint"], C["sky"], C["cream"]][i % 3])
        draw.text((x + 95, y + 30), title, font=F["small_bold"], fill=C["ink"])
        wrap(draw, body, (x + 95, y + 64), F["tiny"], C["muted"], 200, 3)
    footer(draw, "Working app | Source code | Documentation | Testing | Handoff")
    return img


def save_all():
    OUT_DIR.mkdir(exist_ok=True)
    images = [
        ("01_ai_agent_apps_cover.png", image_cover()),
        ("02_ai_agent_services.png", image_services()),
        ("03_clinic_doctor_agent.png", image_doctor()),
        ("04_restaurant_chef_agent.png", image_restaurant()),
        ("05_customer_support_agent.png", image_support()),
        ("06_business_workflow_agent.png", image_business()),
        ("07_app_ui_options.png", image_app_options()),
        ("08_tools_integrations.png", image_integrations()),
        ("09_modern_ai_agent_stack.png", image_stack()),
        ("10_deliverables_benefits.png", image_deliverables()),
    ]
    for name, img in images:
        path = OUT_DIR / name
        img.save(path, optimize=True)
        print(path)


if __name__ == "__main__":
    save_all()
