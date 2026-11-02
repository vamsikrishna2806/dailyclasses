"""All prompts live here, with versions, so we can A/B test and improve them.

How prompt iteration works in this app:
  1. Each output is made with one prompt version (v1 or v2), chosen at random when "auto".
  2. Users rate the output 1-5 stars.
  3. The Prompt Lab tab shows the average rating per version.
  4. Keep the winner, write a new v3 that fixes the complaints, repeat.
"""
import random

LENGTHS = {"short": 120, "medium": 300, "detailed": 700}

STYLES = {
    "bullets": "a bulleted list of key points (one idea per bullet)",
    "paragraph": "flowing paragraphs",
    "tldr": "a single TL;DR line followed by 3 bullets",
    "eli5": "very simple words a 10-year-old understands",
    "academic": "a formal academic abstract",
    "chapter_notes": "study notes with headings: Key events, Key ideas, People, Quotes worth remembering",
}

# ------------------------------------------------------------------ summarize
SUMMARIZE = {
    "v1": {
        "label": "Baseline",
        "system": "You are a helpful assistant that summarizes text.",
        "user": "Summarize the following text in about {words} words as {style}.\n\n{text}",
    },
    "v2": {
        "label": "Grounded editor",
        "system": (
            "You are an expert book editor. You write faithful summaries: you never add facts that are not "
            "in the text, you keep important names, numbers and causes, and you explain why things matter. "
            "Use Markdown."
        ),
        "user": (
            "Write a summary of the text below.\n"
            "- Length: about {words} words\n- Format: {style}\n"
            "- Start with a bold one-sentence overview.\n"
            "- If the text is a part of a larger work, say what it sets up next.\n\n"
            "TEXT:\n\"\"\"\n{text}\n\"\"\""
        ),
    },
}

# Map step for long texts: turn each piece into dense notes, then combine.
NOTES_PROMPT = (
    "Make dense, factual notes of this section of “{title}” ({part}). Keep names, events in order, "
    "key arguments, numbers and memorable quotes (short). 120-250 words. No intro sentence.\n\n\"\"\"\n{text}\n\"\"\""
)
COMBINE_PROMPT = (
    "Below are notes for each part of “{title}”, in order. Using only these notes, write the summary.\n"
    "- Length: about {words} words\n- Format: {style}\n- Start with a bold one-sentence overview.\n\n{text}"
)

# ------------------------------------------------------------------ Q&A
QA = {
    "v1": {
        "label": "Baseline",
        "system": "Answer the user's question using the context below.\n\nCONTEXT:\n{context}",
    },
    "v2": {
        "label": "Cited & honest",
        "system": (
            "You are a reading assistant for the book “{title}”. Answer ONLY from the numbered sources below.\n"
            "Rules:\n"
            "1. Cite every claim with its source tag, like [S2]. Put tags right after the sentence.\n"
            "2. If the sources don't contain the answer, say: “I couldn't find that in the book.” and suggest "
            "what the reader could ask instead. Never guess.\n"
            "3. Quote at most one short phrase when it helps.\n"
            "4. Keep answers under 200 words unless the user asks for more. Use Markdown.\n\n"
            "SOURCES:\n{context}"
        ),
    },
}
GENERAL_CHAT_SYSTEM = (
    "You are a friendly, precise assistant. Use Markdown. If you are not sure about a fact, say so."
)
CONDENSE_PROMPT = (
    "Rewrite the user's last message as one standalone search question about the book, using the chat "
    "history to fill in names and pronouns. Reply with the question only.\n\nHISTORY:\n{history}\n\n"
    "LAST MESSAGE: {question}"
)

# ------------------------------------------------------------------ content generator
CONTENT_TYPES = {
    "quiz": "a 10-question multiple-choice quiz (4 options each, mark the answer and give a one-line "
            "explanation after each question)",
    "flashcards": "15 flashcards as a Markdown table with columns Front | Back",
    "study_notes": "structured study notes with headings, key terms in bold, and a 5-point recap",
    "blog_post": "an engaging blog post with a catchy title, intro hook, 3-5 sections with headings, and a conclusion",
    "social_thread": "a 7-post social media thread; number each post, max 270 characters each, first post is a hook",
    "newsletter": "an email newsletter with a subject line, a preview line, and a short body with one call to action",
    "discussion_questions": "10 open-ended discussion questions for a book club, from easy to deep",
    "characters": "profiles of the main characters or key figures: role, traits, motivation, how they change",
    "timeline": "a timeline of key events in order as a Markdown table: # | Event | Why it matters",
    "lesson_plan": "a 45-minute lesson plan: objectives, warm-up, activities with timings, assessment, homework",
    "custom": "exactly what the user's extra instructions ask for",
}

GENERATE = {
    "v1": {
        "label": "Baseline",
        "system": "You are a helpful content writer.",
        "user": "Create {spec} about the material below. Tone: {tone}. Audience: {audience}. {extra}\n\n{material}",
    },
    "v2": {
        "label": "Expert creator",
        "system": (
            "You are a senior content designer who turns books into learning and marketing material. "
            "Everything you write must be accurate to the source material; do not invent plot points, "
            "quotes or statistics. Use clean Markdown with no preamble like “Sure, here is…”."
        ),
        "user": (
            "TASK: Create {spec}.\nTONE: {tone}\nAUDIENCE: {audience}\nEXTRA INSTRUCTIONS: {extra}\n\n"
            "SOURCE MATERIAL (from “{title}”):\n\"\"\"\n{material}\n\"\"\"\n\n"
            "Before finishing, check each item against the source material and fix anything not supported."
        ),
    },
}

FEATURES = {"summarize": SUMMARIZE, "qa": QA, "generate": GENERATE}


def pick_version(feature: str, requested: str | None) -> str:
    versions = FEATURES[feature]
    if requested in versions:
        return requested
    return random.choice(list(versions))  # "auto" = A/B test


def catalog() -> dict:
    return {
        "features": {f: {v: p["label"] for v, p in versions.items()} for f, versions in FEATURES.items()},
        "content_types": list(CONTENT_TYPES),
        "styles": list(STYLES),
        "lengths": LENGTHS,
        "prompts": FEATURES,
    }
