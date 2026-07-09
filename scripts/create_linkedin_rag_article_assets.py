from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont


OUT_DIR = Path("linkedin_posts")
OUT_DIR.mkdir(exist_ok=True)


def font(size: int, bold: bool = False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def rounded_rect(draw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def line_text(draw, text, xy, fill, fnt, max_width, line_gap=8):
    x, y = xy
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        if draw.textlength(test, font=fnt) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    for line in lines:
        draw.text((x, y), line, fill=fill, font=fnt)
        y += fnt.size + line_gap
    return y


def draw_icon_doc(draw, x, y, color):
    rounded_rect(draw, (x, y, x + 86, y + 104), 14, fill=(255, 255, 255, 24), outline=color, width=3)
    draw.line((x + 18, y + 34, x + 66, y + 34), fill=color, width=4)
    draw.line((x + 18, y + 55, x + 66, y + 55), fill=color, width=4)
    draw.line((x + 18, y + 76, x + 50, y + 76), fill=color, width=4)


def draw_icon_search(draw, x, y, color):
    draw.ellipse((x, y, x + 70, y + 70), outline=color, width=6)
    draw.line((x + 55, y + 55, x + 94, y + 94), fill=color, width=7)


def draw_icon_answer(draw, x, y, color):
    rounded_rect(draw, (x, y, x + 108, y + 82), 22, fill=(255, 255, 255, 25), outline=color, width=3)
    draw.polygon([(x + 25, y + 82), (x + 43, y + 82), (x + 28, y + 102)], fill=(255, 255, 255, 25), outline=color)
    draw.line((x + 24, y + 30, x + 84, y + 30), fill=color, width=4)
    draw.line((x + 24, y + 50, x + 70, y + 50), fill=color, width=4)


def create_cover():
    width, height = 1600, 900
    img = Image.new("RGB", (width, height), "#071017")
    draw = ImageDraw.Draw(img)

    # Editorial dark gradient.
    for yy in range(height):
        shade = int(18 + yy * 0.018)
        draw.line((0, yy, width, yy), fill=(7, 16 + shade // 4, 23 + shade // 3))
    for rr in range(620, 0, -18):
        alpha = rr / 620
        color = (
            int(26 * alpha),
            int(148 * alpha),
            int(132 * alpha),
        )
        draw.ellipse((980 - rr, -190 - rr, 980 + rr, -190 + rr), outline=color, width=2)
    for rr in range(520, 0, -18):
        alpha = rr / 520
        color = (
            int(122 * alpha),
            int(76 * alpha),
            int(236 * alpha),
        )
        draw.ellipse((1450 - rr, 780 - rr, 1450 + rr, 780 + rr), outline=color, width=2)

    teal = (63, 224, 208)
    blue = (96, 165, 250)
    violet = (167, 139, 250)
    white = (242, 247, 250)
    muted = (163, 177, 189)
    panel = (14, 25, 35)
    border = (41, 63, 76)

    # Header tag.
    rounded_rect(draw, (92, 70, 410, 120), 25, fill=(23, 45, 55), outline=(58, 91, 105), width=2)
    draw.text((122, 83), "RAG PROJECT NOTES", fill=teal, font=font(24, True))

    draw.text((92, 165), "RAG Chatbots", fill=white, font=font(76, True))
    draw.text((92, 252), "from files to", fill=white, font=font(52, True))
    draw.text((92, 312), "trusted answers", fill=white, font=font(52, True))
    line_text(
        draw,
        "I built a free-model RAG workflow using an Agentic AI article and my GitHub repo as the knowledge base.",
        (96, 392),
        muted,
        font(28),
        560,
        line_gap=10,
    )

    # Flow panel.
    rounded_rect(draw, (760, 120, 1508, 762), 36, fill=panel, outline=border, width=2)
    draw.text((812, 165), "How the system thinks", fill=white, font=font(34, True))
    draw.text((812, 209), "Not general guessing. Document-grounded answers.", fill=muted, font=font(24))

    cards = [
        ("1", "Load", "PDF article + GitHub repo", teal, draw_icon_doc),
        ("2", "Chunk", "Break long files into sections", blue, draw_icon_doc),
        ("3", "Embed", "Convert text into searchable meaning", violet, draw_icon_search),
        ("4", "Retrieve", "Find the most relevant chunks", teal, draw_icon_search),
        ("5", "Answer", "Use only retrieved context", blue, draw_icon_answer),
        ("6", "Cite", "Show where the answer came from", violet, draw_icon_doc),
    ]

    x0, y0 = 812, 280
    card_w, card_h = 315, 128
    gap_x, gap_y = 32, 28
    for idx, (num, title, desc, accent, icon_fn) in enumerate(cards):
        col = idx % 2
        row = idx // 2
        x = x0 + col * (card_w + gap_x)
        y = y0 + row * (card_h + gap_y)
        rounded_rect(draw, (x, y, x + card_w, y + card_h), 24, fill=(10, 38, 48), outline=(55, 91, 102), width=2)
        draw.ellipse((x + 22, y + 24, x + 66, y + 68), fill=accent)
        draw.text((x + 37, y + 31), num, fill="#071017", font=font(23, True), anchor="mm")
        draw.text((x + 84, y + 28), title, fill=white, font=font(28, True))
        line_text(draw, desc, (x + 84, y + 65), muted, font(20), 190, line_gap=4)

    # Bottom statement.
    rounded_rect(draw, (92, 690, 686, 784), 28, fill=(8, 46, 52), outline=(58, 119, 126), width=2)
    draw.text((125, 716), "Core rule:", fill=teal, font=font(28, True))
    draw.text((264, 716), "Answer only from provided files.", fill=white, font=font(25, True))
    draw.text((125, 752), "If the answer is not in the files, say it is not found.", fill=muted, font=font(22))

    draw.text((96, 842), "Python • LangChain • Groq free tier • Gradio • RAG", fill=(122, 148, 164), font=font(22, True))
    img.save(OUT_DIR / "rag_chatbot_linkedin_cover.png", quality=95)


ARTICLE = """# What I Learned While Building a RAG Chatbot With a Free Model

This week I worked on a practical RAG chatbot project.

RAG stands for Retrieval-Augmented Generation. In simple words, it means the AI does not answer from memory first. It searches the documents first, finds the most relevant parts, and then writes an answer using only that context.

That one idea changes the whole behavior of a chatbot.

A normal chatbot may sound confident even when it is guessing. A RAG chatbot should be more controlled. If the answer is inside the knowledge base, it answers with sources. If the answer is not there, it should say it could not find it.

For practice, I used two knowledge sources:

1. A recent Agentic AI article from arXiv
2. My own GitHub repo with notebooks and project files

The full flow was:

- Load the documents
- Extract text
- Split long text into smaller chunks
- Create embeddings so chunks become searchable
- Retrieve the most relevant chunks for a question
- Send only those chunks to the model
- Ask the model to answer strictly from that context
- Show the sources used

The most important concept for me was chunking.

At first, I thought the model simply reads the full PDF or full repo. But real RAG does not work like that. Large documents are split into focused sections, because the model only needs the most relevant parts to answer a specific question.

Another important concept was embeddings.

An embedding is a numeric representation of text. It helps the system compare a user question with document chunks and find what is most similar. In a production system, I would use a stronger embedding model and a vector database like Chroma, Pinecone, Weaviate, or FAISS.

For learning, I kept the setup free and simple:

- Local retrieval logic
- Free-tier Groq model for answering
- Gradio UI for testing
- Source-based answers

This is the same idea clients ask for when they want a chatbot that answers from Google Drive, PDFs, company policies, help docs, or internal knowledge bases.

My key takeaway:

RAG is not just a chatbot feature. It is a trust system.

It helps the chatbot stay grounded, cite sources, and avoid making up answers when the information is not available.

Next step: connect this same RAG pipeline to Google Drive and build a full document-based assistant.

#RAG #AIAgents #LangChain #Python #GenerativeAI #Gradio #LearningInPublic
"""


def create_article_file():
    (OUT_DIR / "rag_chatbot_linkedin_article.md").write_text(ARTICLE, encoding="utf-8")


if __name__ == "__main__":
    create_cover()
    create_article_file()
    print(f"Created {OUT_DIR / 'rag_chatbot_linkedin_cover.png'}")
    print(f"Created {OUT_DIR / 'rag_chatbot_linkedin_article.md'}")
