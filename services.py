import os
import json
import requests
import logging
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PLATFORM_CONFIGS = {
    "instagram": {"max_chars": 2200, "style": "visual storytelling, emojis, line breaks"},
    "facebook":  {"max_chars": 500,  "style": "conversational, community-focused"},
    "tiktok":    {"max_chars": 150,  "style": "punchy, trendy, Gen-Z hooks"},
    "whatsapp":  {"max_chars": 400,  "style": "personal, direct, informal"},
    "email":     {"max_chars": 800,  "style": "professional warm newsletter with subject line"},
}

TONES = {
    "adventurous": "exciting, bold, adrenaline-fueled",
    "romantic":    "intimate, poetic, dreamy — for couples",
    "professional":"trustworthy, polished, safety-focused",
    "family":      "warm, fun, inclusive, all ages",
}

def _call(prompt: str) -> dict:
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.8,
    )
    return json.loads(r.choices[0].message.content)


def process_kayak_content(
    user_input: str,
    context: str = "",
    tone: str = "adventurous",
    language: str = "auto",
    platforms: list = None,
) -> dict:
    if not platforms:
        platforms = ["instagram", "whatsapp"]

    tone_desc = TONES.get(tone, TONES["adventurous"])
    plat_lines = "\n".join(
        f'  "{p}": max {PLATFORM_CONFIGS[p]["max_chars"]} chars — {PLATFORM_CONFIGS[p]["style"]}'
        for p in platforms if p in PLATFORM_CONFIGS
    )
    lang_rule = "Match the language of user_input." if language == "auto" else f"Write EVERYTHING in {language}."

    prompt = f"""
You are a world-class marketing expert for "Berlin Kayak Tours".

INPUT: {user_input}
CONTEXT: {context or "none"}
TONE: {tone_desc}
LANGUAGE: {lang_rule}

If too vague → return: {{"status":"need_more_info","questions":["q1","q2"]}}

Otherwise return:
{{
  "status": "complete",
  "tour_title": "<catchy name>",
  "platforms": {{
{chr(10).join(f'    "{p}": "<full ready-to-post text>"' for p in platforms if p in PLATFORM_CONFIGS)}
  }},
  "hashtags": ["10 hashtags WITHOUT #"],
  "image_prompt": "<vivid cinematic English Flux image prompt>",
  "email_subject": "<subject line or empty>"
}}

Limits: {plat_lines}
Return ONLY valid JSON.
"""
    return _call(prompt)


def generate_bulk_content(user_input: str, tone: str = "adventurous", language: str = "auto") -> dict:
    tone_desc = TONES.get(tone, TONES["adventurous"])
    lang_rule = "Match user_input language." if language == "auto" else f"Write in {language}."
    prompt = f"""
You are a social media manager for "Berlin Kayak Tours".
CONCEPT: {user_input} | TONE: {tone_desc} | LANGUAGE: {lang_rule}

Create a 7-day Instagram calendar with UNIQUE daily hooks:
Day1=Teaser, Day2=Social proof, Day3=BTS, Day4=FAQ, Day5=User story, Day6=Limited offer, Day7=Grand CTA

Return ONLY:
{{
  "calendar": [
    {{"day":1,"theme":"Teaser","caption":"<full post with emojis>","hashtags":["5 tags no #"],"image_prompt":"<vivid English prompt>"}}
  ]
}}
Exactly 7 items. ONLY valid JSON.
"""
    return _call(prompt)


def generate_marketing_image(image_prompt: str) -> str:
    logger.info(f"Image gen: {image_prompt[:50]}...")
    try:
        url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(image_prompt)}?width=1024&height=1024&model=flux&nologo=true&enhance=true"
        r = requests.get(url, timeout=45)
        if r.status_code == 200:
            with open("latest_promo.png", "wb") as f:
                f.write(r.content)
            return "latest_promo.png"
        return "image_error"
    except requests.exceptions.Timeout:
        return "timeout"
    except Exception as e:
        logger.exception(e)
        return "connection_failed"