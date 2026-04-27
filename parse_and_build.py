#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parser and website builder for תנ"ך לחיים
Reads the WhatsApp chat export and generates a full static website.
"""

import re
import json
import os

def normalize_for_match(s):
    """Normalize a title/filename for fuzzy matching."""
    s = re.sub(r'["\'\-–—?!,.():\[\]״״]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def load_custom_images(folder):
    """Load images from 'another picturs' and its sub-folders, keyed by normalized filename."""
    img_dirs = [
        ('another picturs', os.path.join(folder, 'another picturs')),
        ('another picturs/more picturs', os.path.join(folder, 'another picturs', 'more picturs')),
    ]
    mapping = {}
    for rel_path, img_dir in img_dirs:
        if not os.path.exists(img_dir):
            continue
        for fname in os.listdir(img_dir):
            if fname.lower().endswith(('.png', '.jpg', '.jpeg')):
                name = os.path.splitext(fname)[0]
                key = normalize_for_match(name)
                mapping[key] = rel_path + '/' + fname
    return mapping

def find_image_for_post(title, image_map):
    """Find best matching image for a post title."""
    if not title:
        return None
    norm_title = normalize_for_match(title)
    # Exact match
    if norm_title in image_map:
        return image_map[norm_title]
    # Partial match: image name is contained in title or vice versa
    for key, path in image_map.items():
        if key in norm_title or norm_title in key:
            return path
        # Word overlap match: at least 2 words AND ≥50% of shorter title
        title_words = set(norm_title.split())
        key_words = set(key.split())
        common = title_words & key_words
        shorter = min(len(title_words), len(key_words))
        if shorter > 0 and len(common) >= 2 and len(common) / shorter >= 0.5:
            return path
    return None

CHAT_FILE = "‏צ'אט WhatsApp עם אתר תנך לחיים.txt"
OUTPUT_FILE = "index.html"

SERIES_ORDER = ['קהלת', 'שמואל א', 'שמואל ב', 'מגילת אסתר', 'שמות', 'פסוקי גאולה']
SERIES_COLORS = {
    'קהלת': '#5B7FA6',
    'שמואל א': '#6B8E5E',
    'שמואל ב': '#8B6B5E',
    'מגילת אסתר': '#A67B5B',
    'שמות': '#7B6EA6',
    'פסוקי גאולה': '#A65B5B',
    'אחר': '#888888',
}

SERIES_ICONS = {
    'קהלת': '📖',
    'שמואל א': '🏹',
    'שמואל ב': '👑',
    'מגילת אסתר': '🌸',
    'שמות': '🔥',
    'פסוקי גאולה': '🕊️',
    'אחר': '📜',
}

# Atmospheric gradient palettes per series (multiple variants for variety)
SERIES_GRADIENTS = {
    'קהלת': [
        'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
        'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)',
        'linear-gradient(160deg, #2d3561 0%, #c05c7e 50%, #f3826f 100%)',
        'linear-gradient(135deg, #4776e6 0%, #8e54e9 100%)',
        'linear-gradient(160deg, #373b44 0%, #4286f4 100%)',
    ],
    'שמואל א': [
        'linear-gradient(135deg, #134e5e 0%, #71b280 100%)',
        'linear-gradient(160deg, #093028 0%, #237a57 100%)',
        'linear-gradient(135deg, #1a6b3a 0%, #5aaa6f 50%, #a8d8a8 100%)',
        'linear-gradient(160deg, #2c5364 0%, #203a43 50%, #0f2027 100%)',
        'linear-gradient(135deg, #1d4350 0%, #a43931 100%)',
    ],
    'שמואל ב': [
        'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
        'linear-gradient(160deg, #2d1b69 0%, #11998e 100%)',
        'linear-gradient(135deg, #360033 0%, #0b8793 100%)',
        'linear-gradient(160deg, #2c3e50 0%, #4ca1af 100%)',
        'linear-gradient(135deg, #373b44 0%, #4286f4 100%)',
    ],
    'מגילת אסתר': [
        'linear-gradient(135deg, #c94b4b 0%, #4b134f 100%)',
        'linear-gradient(160deg, #b24592 0%, #f15f79 100%)',
        'linear-gradient(135deg, #8e0e00 0%, #1f1c18 100%)',
        'linear-gradient(160deg, #c6426e 0%, #642b73 100%)',
        'linear-gradient(135deg, #f7971e 0%, #ffd200 50%, #c94b4b 100%)',
    ],
    'שמות': [
        'linear-gradient(135deg, #f46b45 0%, #eea849 100%)',
        'linear-gradient(160deg, #c94b4b 0%, #eea849 100%)',
        'linear-gradient(135deg, #f7971e 0%, #ffd200 100%)',
        'linear-gradient(160deg, #b45309 0%, #f59e0b 50%, #fcd34d 100%)',
        'linear-gradient(135deg, #7b4f12 0%, #e07b00 50%, #f7971e 100%)',
    ],
    'פסוקי גאולה': [
        'linear-gradient(135deg, #56ccf2 0%, #2f80ed 100%)',
        'linear-gradient(160deg, #005c97 0%, #363795 100%)',
        'linear-gradient(135deg, #1cb5e0 0%, #000046 100%)',
        'linear-gradient(160deg, #0f2027 0%, #203a43 50%, #2c5364 100%)',
        'linear-gradient(135deg, #00b4db 0%, #0083b0 100%)',
    ],
    'אחר': [
        'linear-gradient(135deg, #888 0%, #555 100%)',
    ],
}

# SVG overlay patterns per series for texture
SERIES_PATTERNS = {
    'קהלת': '<circle cx="20" cy="20" r="1.5" fill="rgba(255,255,255,0.15)"/><circle cx="60" cy="10" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="35" r="2" fill="rgba(255,255,255,0.12)"/><circle cx="40" cy="50" r="1" fill="rgba(255,255,255,0.1)"/>',
    'שמואל א': '<path d="M0 40 Q25 20 50 40 Q75 60 100 40" stroke="rgba(255,255,255,0.1)" fill="none" stroke-width="2"/><path d="M0 60 Q25 40 50 60 Q75 80 100 60" stroke="rgba(255,255,255,0.07)" fill="none" stroke-width="2"/>',
    'שמואל ב': '<polygon points="50,5 61,35 95,35 68,57 79,91 50,70 21,91 32,57 5,35 39,35" fill="rgba(255,215,0,0.08)"/>',
    'מגילת אסתר': '<circle cx="50" cy="30" r="20" stroke="rgba(255,215,0,0.15)" fill="none" stroke-width="1"/><circle cx="50" cy="30" r="28" stroke="rgba(255,215,0,0.08)" fill="none" stroke-width="1"/>',
    'שמות': '<path d="M10 60 L50 10 L90 60" stroke="rgba(255,200,0,0.2)" fill="rgba(255,150,0,0.05)" stroke-width="2"/>',
    'פסוקי גאולה': '<path d="M20 50 Q50 10 80 50" stroke="rgba(255,255,255,0.12)" fill="none" stroke-width="3"/><circle cx="50" cy="20" r="8" fill="rgba(255,255,200,0.15)"/>',
    'אחר': '',
}


def determine_series(verse_ref):
    if not verse_ref:
        return 'אחר'
    if 'קהלת' in verse_ref:
        return 'קהלת'
    if 'שמואל א' in verse_ref:
        return 'שמואל א'
    if 'שמואל ב' in verse_ref:
        return 'שמואל ב'
    if 'אסתר' in verse_ref:
        return 'מגילת אסתר'
    if 'שמות' in verse_ref:
        return 'שמות'
    if 'ירמיהו' in verse_ref or 'ישעיהו' in verse_ref:
        return 'פסוקי גאולה'
    return 'אחר'


def clean_bold(text):
    """Remove WhatsApp *bold* markers."""
    return re.sub(r'\*([^*]+)\*', r'\1', text)


def bold_to_html(text):
    """Convert WhatsApp *bold* to <strong>."""
    return re.sub(r'\*([^*]+)\*', r'<strong>\1</strong>', text)


def text_to_html(text):
    """Convert plain text with *bold* markers to HTML paragraphs."""
    lines = text.strip().split('\n')
    result = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        line_html = bold_to_html(line)
        result.append(f'<p>{line_html}</p>')
    return '\n'.join(result)


def parse_post(post_text, image_file):
    """Parse a single post text into structured data."""
    lines = [l for l in post_text.strip().split('\n')]

    title = ''
    author = ''
    verse_text = ''
    verse_ref = ''
    commentary_lines = []
    life_point_lines = []
    section = 'header'

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            i += 1
            continue

        # Stop at separator or CTA
        if re.match(r'^={3,}$', stripped) or 'הצטרפו לקבוצה' in stripped or stripped.startswith('https://'):
            break

        # Author line
        if stripped == 'הרב יואב אוריאל':
            author = 'הרב יואב אוריאל'
            i += 1
            continue

        # Special header line (series title like "הפסוק היומי - פסוקי גאולה")
        if 'הפסוק היומי' in stripped and not title:
            title = clean_bold(stripped)
            i += 1
            continue

        # Verse line: contains a parenthetical reference with Hebrew book name
        if section in ('header', 'title_done', 'post_body'):
            # Check if this line looks like a verse (has a reference in parentheses)
            # Allow optional period/dot after the closing parenthesis
            ref_match = re.search(r'\(([^)]+(?:א|ב|ג|ד|ה|ו|ז|ח|ט|י|כ|ל|מ|נ|ס|ע|פ|צ|ק|ר|ש|ת)[^)]*)\)[.\s]*$', stripped)
            has_quote = ('"' in stripped or '\u201c' in stripped or '\u201d' in stripped or
                         stripped.startswith('*"') or '״' in stripped)
            if ref_match and has_quote and not verse_ref:
                verse_ref = ref_match.group(1).strip()
                verse_text = stripped[:ref_match.start()].strip()
                # Clean quote marks and bold markers
                for ch in ['*', '"', '\u201c', '\u201d', '״', '"', '"']:
                    verse_text = verse_text.strip(ch)
                verse_text = verse_text.strip()
                section = 'post_body'
                i += 1
                continue

        # Commentary section
        if '📜' in stripped:
            section = 'commentary'
            rest = stripped.replace('📜', '').strip()
            if rest:
                commentary_lines.append(rest)
            i += 1
            continue

        # Life point section
        if '🌿' in stripped:
            section = 'life_point'
            rest = stripped.replace('🌿', '').strip()
            if rest.startswith('נקודת חיים'):
                rest = rest[len('נקודת חיים'):].lstrip(':').strip()
            if rest:
                life_point_lines.append(rest)
            i += 1
            continue

        # Accumulate by section
        if section == 'commentary':
            commentary_lines.append(stripped)
        elif section == 'life_point':
            life_point_lines.append(stripped)
        elif section == 'header' and not title:
            title = clean_bold(stripped)
            section = 'title_done'
        elif section == 'title_done':
            # Could be more header text before verse
            pass

        i += 1

    commentary = '\n'.join(commentary_lines)
    life_point = '\n'.join(life_point_lines)
    series = determine_series(verse_ref)

    return {
        'title': title,
        'author': author,
        'verse_text': verse_text,
        'verse_ref': verse_ref,
        'commentary': commentary,
        'life_point': life_point,
        'series': series,
        'image': image_file,
    }


def parse_chat(filepath):
    """Parse the WhatsApp chat file and return list of posts."""
    with open(filepath, encoding='utf-8') as f:
        content = f.read()

    # Split by timestamp lines
    timestamp_pattern = re.compile(r'\d{1,2}\.\d{1,2}\.\d{4}, \d{2}:\d{2} - ')
    boundaries = [m.start() for m in timestamp_pattern.finditer(content)]
    boundaries.append(len(content))

    posts = []

    for i in range(len(boundaries) - 1):
        start = boundaries[i]
        end = boundaries[i + 1]
        msg_text = content[start:end].strip()

        # Extract timestamp and body
        ts_match = re.match(r'(\d{1,2}\.\d{1,2}\.\d{4}, \d{2}:\d{2}) - ', msg_text)
        if not ts_match:
            continue
        timestamp = ts_match.group(1)
        body = msg_text[ts_match.end():]

        # Only process Daniel elbaz messages
        if 'Daniel elbaz:' not in body:
            continue

        body = body.split('Daniel elbaz:', 1)[1].strip()

        # Check if it's an image message (with or without BOM character)
        img_match = re.match(r'\u200f?(IMG-[\w-]+\.(?:jpg|png))\s*\(קובץ מצורף\)\n?', body)

        if img_match:
            image_file = img_match.group(1)
            post_text = body[img_match.end():]
        else:
            # Text-only message (first post)
            image_file = None
            post_text = body

        # Remove CTA
        cta_idx = post_text.find('הצטרפו לקבוצה')
        if cta_idx > 0:
            post_text = post_text[:cta_idx].strip()

        # Remove trailing URLs
        post_text = re.sub(r'https?://\S+\s*$', '', post_text, flags=re.MULTILINE).strip()

        # Skip if too short to be a real post
        if len(post_text.strip()) < 30:
            continue

        post = parse_post(post_text, image_file)

        # Only include posts that have meaningful content
        if post['verse_ref'] or (post['title'] and post['commentary']):
            posts.append(post)

    return posts


def json_escape(s):
    """Escape for JSON embedding in HTML."""
    return json.dumps(s, ensure_ascii=False)


def build_html(posts):
    """Generate the complete HTML website."""

    # Group posts by series
    by_series = {}
    for post in posts:
        s = post['series']
        if s not in by_series:
            by_series[s] = []
        by_series[s].append(post)

    # Count per series for navigation
    series_counts = {s: len(p) for s, p in by_series.items()}

    # Build series tabs HTML
    tabs_html = '<button class="tab-btn active" data-series="all" onclick="filterSeries(\'all\')">הכל <span class="count">' + str(len(posts)) + '</span></button>\n'
    for s in SERIES_ORDER:
        if s in by_series:
            count = series_counts[s]
            color = SERIES_COLORS.get(s, '#888')
            icon = SERIES_ICONS.get(s, '📜')
            tabs_html += f'<button class="tab-btn" data-series="{s}" style="--series-color:{color}" onclick="filterSeries(\'{s}\')">{s} <span class="count">{count}</span></button>\n'

    # Build cards HTML
    cards_html = ''
    for i, post in enumerate(posts):
        series = post['series']
        color = SERIES_COLORS.get(series, '#888')
        icon = SERIES_ICONS.get(series, '📜')

        title = post['title'] or post['verse_ref'] or 'פסוק יומי'
        verse_preview = post['verse_text'][:80] + '...' if len(post['verse_text']) > 80 else post['verse_text']

        # Image
        img_html = ''
        if post['image']:
            img_html = f'<div class="card-image"><img src="{post["image"]}" alt="{title}" loading="lazy" onerror="this.parentElement.style.display=\'none\'"></div>'

        author_html = f'<span class="card-author">{post["author"]}</span>' if post['author'] else ''

        cards_html += f'''
        <div class="post-card" data-series="{series}" onclick="openPost({i})">
            {img_html}
            <div class="card-body">
                <div class="card-series" style="background:{color}">{series}</div>
                <h3 class="card-title">{title}</h3>
                {author_html}
                <div class="card-verse">"{verse_preview}"</div>
                <div class="card-ref">{post["verse_ref"]}</div>
            </div>
        </div>
        '''

    # Build posts JSON for modal
    posts_json = json.dumps(posts, ensure_ascii=False)

    html = f'''<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>תנ"ך לחיים</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Frank+Ruhl+Libre:wght@300;400;500;700;900&family=Heebo:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

:root {{
  --gold: #C9A84C;
  --gold-light: #E8D5A3;
  --dark: #1C2B1E;
  --text: #2C2C2C;
  --text-light: #6B6B6B;
  --bg: #FAFAF7;
  --bg-card: #FFFFFF;
  --border: #E8E4DC;
  --shadow: 0 2px 16px rgba(0,0,0,0.08);
  --shadow-hover: 0 8px 32px rgba(0,0,0,0.15);
  --radius: 12px;
}}

html {{ scroll-behavior: smooth; }}

body {{
  font-family: 'Heebo', sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.7;
  direction: rtl;
}}

/* ── HEADER ── */
.site-header {{
  background:
    radial-gradient(ellipse 64% 60% at 50% 22%, rgba(212,162,68,0.50) 0%, transparent 68%),
    radial-gradient(ellipse 38% 50% at 24% 65%, rgba(180,126,50,0.36) 0%, transparent 62%),
    radial-gradient(ellipse 52% 46% at 92% 8%,  rgba(36,88,76,0.58)   0%, transparent 64%),
    radial-gradient(ellipse 42% 44% at 5%  12%, rgba(50,70,94,0.38)   0%, transparent 58%),
    radial-gradient(ellipse 38% 52% at 82% 74%, rgba(46,96,60,0.30)   0%, transparent 55%),
    radial-gradient(ellipse 55% 38% at 62% 90%, rgba(140,100,40,0.28) 0%, transparent 58%),
    radial-gradient(ellipse 74% 44% at 50% 115%, rgba(6,14,8,0.75)   0%, transparent 65%),
    linear-gradient(170deg, #0C1810 0%, #162616 28%, #1F3219 52%, #18280E 76%, #0A1408 100%);
  color: white;
  text-align: center;
  padding: 60px 20px 50px;
  position: relative;
  overflow: hidden;
}}

/* Paper grain texture */
.site-header::before {{
  content: '';
  position: absolute;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='220'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.80' numOctaves='4' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='220' height='220' filter='url(%23n)'/%3E%3C/svg%3E");
  background-size: 180px 180px;
  opacity: 0.045;
  mix-blend-mode: screen;
  pointer-events: none;
  z-index: 0;
}}

/* Bottom paint bleed — colour pooling at the edge */
.site-header::after {{
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: linear-gradient(to bottom, transparent, rgba(5,12,6,0.50));
  pointer-events: none;
  z-index: 0;
}}

/* Keep all text above pseudo-elements */
.site-header > * {{
  position: relative;
  z-index: 1;
}}

.site-title {{
  font-family: 'Frank Ruhl Libre', serif;
  font-size: clamp(36px, 6vw, 64px);
  font-weight: 900;
  color: white;
  margin-bottom: 8px;
  text-shadow: 0 2px 28px rgba(0,0,0,0.45), 0 0 60px rgba(0,0,0,0.25);
}}

.site-subtitle {{
  font-size: 18px;
  color: var(--gold-light);
  font-weight: 300;
  letter-spacing: 0.5px;
}}

.site-meta {{
  margin-top: 20px;
  display: flex;
  gap: 24px;
  justify-content: center;
  flex-wrap: wrap;
}}

.meta-badge {{
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  color: rgba(255,255,255,0.85);
}}

/* ── SEARCH ── */
.search-bar {{
  max-width: 600px;
  margin: -24px auto 0;
  padding: 0 20px;
  position: relative;
  z-index: 10;
}}

.search-input {{
  width: 100%;
  padding: 16px 24px;
  border: 2px solid var(--border);
  border-radius: 50px;
  font-size: 16px;
  font-family: 'Heebo', sans-serif;
  background: white;
  box-shadow: var(--shadow);
  outline: none;
  direction: rtl;
  transition: border-color 0.2s, box-shadow 0.2s;
}}

.search-input:focus {{
  border-color: var(--gold);
  box-shadow: 0 4px 24px rgba(201,168,76,0.2);
}}

/* ── MAIN LAYOUT ── */
.main-content {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}}

/* ── SERIES TABS ── */
.series-nav {{
  margin: 32px 0;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}}

.tab-btn {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  border: 2px solid var(--border);
  border-radius: 50px;
  background: white;
  font-family: 'Heebo', sans-serif;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text);
}}

.tab-btn:hover {{
  border-color: var(--series-color, var(--gold));
  color: var(--series-color, var(--gold));
  background: rgba(201,168,76,0.05);
}}

.tab-btn.active {{
  background: var(--series-color, var(--dark));
  border-color: var(--series-color, var(--dark));
  color: white;
}}

.tab-btn[data-series="all"].active {{
  background: var(--dark);
  border-color: var(--dark);
}}

.tab-btn .count {{
  background: rgba(255,255,255,0.25);
  padding: 1px 7px;
  border-radius: 10px;
  font-size: 12px;
}}

.tab-btn:not(.active) .count {{
  background: var(--bg);
  color: var(--text-light);
}}

/* ── CARDS GRID ── */
.results-count {{
  color: var(--text-light);
  font-size: 14px;
  margin-bottom: 20px;
}}

.cards-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}}

.post-card {{
  background: var(--bg-card);
  border-radius: var(--radius);
  border: 1px solid var(--border);
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
}}

.post-card:hover {{
  transform: translateY(-4px);
  box-shadow: var(--shadow-hover);
}}

.post-card.hidden {{
  display: none;
}}

.card-image {{
  width: 100%;
  height: 180px;
  overflow: hidden;
  background: #f0ece4;
}}

.card-image img {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}}

.post-card:hover .card-image img {{
  transform: scale(1.03);
}}

.card-body {{
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}}

.card-series {{
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  font-weight: 600;
  color: white;
  padding: 3px 10px;
  border-radius: 12px;
  align-self: flex-start;
  letter-spacing: 0.3px;
}}

.card-title {{
  font-family: 'Frank Ruhl Libre', serif;
  font-size: 18px;
  font-weight: 700;
  color: var(--dark);
  line-height: 1.4;
}}

.card-author {{
  font-size: 13px;
  color: var(--text-light);
  font-style: italic;
}}

.card-verse {{
  font-size: 14px;
  color: var(--text);
  font-style: italic;
  line-height: 1.6;
  border-right: 3px solid var(--gold);
  padding-right: 12px;
  color: #555;
}}

.card-ref {{
  font-size: 13px;
  color: var(--gold);
  font-weight: 600;
  margin-top: auto;
}}

/* ── MODAL ── */
.modal-overlay {{
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  z-index: 1000;
  display: none;
  align-items: center;
  justify-content: center;
  padding: 20px;
  backdrop-filter: blur(4px);
}}

.modal-overlay.open {{
  display: flex;
}}

.modal {{
  background: white;
  border-radius: 16px;
  max-width: 720px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  animation: modal-in 0.3s ease;
}}

@keyframes modal-in {{
  from {{ opacity: 0; transform: translateY(20px) scale(0.97); }}
  to {{ opacity: 1; transform: translateY(0) scale(1); }}
}}

.modal-close {{
  position: sticky;
  top: 0;
  display: flex;
  justify-content: flex-end;
  padding: 16px 20px 0;
  background: white;
  z-index: 5;
}}

.btn-close {{
  width: 36px;
  height: 36px;
  border: none;
  background: #f0f0f0;
  border-radius: 50%;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}}

.btn-close:hover {{ background: #e0e0e0; }}

.modal-image {{
  width: 100%;
  max-height: 280px;
  object-fit: cover;
  display: block;
}}

.modal-body {{
  padding: 32px 40px 40px;
}}

.modal-series-badge {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: white;
  padding: 4px 14px;
  border-radius: 12px;
  margin-bottom: 16px;
}}

.modal-title {{
  font-family: 'Frank Ruhl Libre', serif;
  font-size: clamp(22px, 4vw, 32px);
  font-weight: 900;
  color: var(--dark);
  line-height: 1.3;
  margin-bottom: 8px;
}}

.modal-author {{
  font-size: 15px;
  color: var(--text-light);
  font-style: italic;
  margin-bottom: 24px;
}}

.modal-verse-block {{
  background: linear-gradient(135deg, #FFFBF0, #FFF8E7);
  border-right: 4px solid var(--gold);
  padding: 20px 24px;
  border-radius: 8px;
  margin-bottom: 28px;
}}

.modal-verse-text {{
  font-family: 'Frank Ruhl Libre', serif;
  font-size: 18px;
  color: var(--dark);
  line-height: 1.8;
  font-style: italic;
  margin-bottom: 8px;
}}

.modal-verse-ref {{
  font-size: 14px;
  color: var(--gold);
  font-weight: 700;
}}

.modal-section {{
  margin-bottom: 24px;
}}

.modal-section-title {{
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text-light);
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}}

.modal-section-title::after {{
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}}

.modal-text {{
  font-size: 16px;
  line-height: 1.9;
  color: var(--text);
}}

.modal-text p {{
  margin-bottom: 10px;
}}

.modal-text strong {{
  color: var(--dark);
  font-weight: 700;
}}

.modal-life-point {{
  background: #F0F7F0;
  border-radius: 10px;
  padding: 20px 24px;
}}

.modal-life-point .modal-section-title {{
  color: #3A7A3A;
}}

.modal-life-point .modal-text {{
  color: #2C4A2C;
}}

.modal-nav {{
  display: flex;
  justify-content: space-between;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--border);
}}

.btn-nav {{
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: 2px solid var(--border);
  border-radius: 8px;
  background: white;
  font-family: 'Heebo', sans-serif;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text);
}}

.btn-nav:hover {{
  border-color: var(--dark);
  background: var(--dark);
  color: white;
}}

.btn-nav:disabled {{
  opacity: 0.3;
  cursor: default;
}}

.btn-nav:disabled:hover {{
  border-color: var(--border);
  background: white;
  color: var(--text);
}}

/* ── NO RESULTS ── */
.no-results {{
  text-align: center;
  padding: 60px 20px;
  color: var(--text-light);
  display: none;
}}

.no-results.show {{ display: block; }}

/* ── FOOTER ── */
.site-footer {{
  text-align: center;
  padding: 40px 20px;
  color: var(--text-light);
  font-size: 14px;
  border-top: 1px solid var(--border);
  margin-top: 60px;
}}

/* ── RESPONSIVE ── */
@media (max-width: 600px) {{
  .cards-grid {{ grid-template-columns: 1fr; }}
  .modal-body {{ padding: 24px 20px 32px; }}
  .series-nav {{ gap: 6px; }}
  .tab-btn {{ padding: 6px 12px; font-size: 13px; }}
}}

/* ── SCROLLBAR ── */
.modal::-webkit-scrollbar {{ width: 6px; }}
.modal::-webkit-scrollbar-track {{ background: #f0f0f0; }}
.modal::-webkit-scrollbar-thumb {{ background: #ccc; border-radius: 3px; }}
</style>
</head>
<body>

<header class="site-header">
  <h1 class="site-title">תנ"ך לחיים</h1>
  <p class="site-subtitle">פסוקים יומיים עם מסר לחיים • הרב יואב אוריאל</p>
  <div class="site-meta">
    <span class="meta-badge">📚 {len(posts)} פסוקים</span>
    <span class="meta-badge">📖 {len([s for s in SERIES_ORDER if s in by_series])} ספרים</span>
  </div>
</header>

<div class="search-bar">
  <input type="text" class="search-input" placeholder="חיפוש לפי כותרת, פסוק או נושא..." oninput="searchPosts(this.value)" aria-label="חיפוש">
</div>

<main class="main-content">

  <nav class="series-nav" aria-label="סינון לפי ספר">
    {tabs_html}
  </nav>

  <div class="results-count" id="results-count">{len(posts)} פסוקים</div>

  <div class="cards-grid" id="cards-grid">
    {cards_html}
  </div>

  <div class="no-results" id="no-results">
    <p style="font-size:48px">🔍</p>
    <p style="font-size:18px;margin-top:12px">לא נמצאו תוצאות</p>
  </div>

</main>

<footer class="site-footer">
  <p>תנ"ך לחיים • הרב יואב אוריאל</p>
  <p style="margin-top:6px;font-size:13px">כל הזכויות שמורות לעמותת &#39;בני ציון&#39;</p>
  <p style="margin-top:8px;font-size:12px;color:#999;max-width:560px;margin-right:auto;margin-left:auto;line-height:1.6">התוכן באתר מוקדש לעילוי נשמת מעין פלסר ז״ל במסגרת מיזם &#39;תנ״ך למשפחה&#39; של ארגון בני-ציון</p>
</footer>

<!-- MODAL -->
<div class="modal-overlay" id="modal-overlay" onclick="handleOverlayClick(event)">
  <div class="modal" id="modal">
    <div class="modal-close">
      <button class="btn-close" onclick="closePost()" aria-label="סגור">✕</button>
    </div>
    <img class="modal-image" id="modal-image" src="" alt="" style="display:none">
    <div class="modal-body">
      <div id="modal-series-badge" class="modal-series-badge"></div>
      <h2 class="modal-title" id="modal-title"></h2>
      <p class="modal-author" id="modal-author"></p>

      <div class="modal-verse-block">
        <div class="modal-verse-text" id="modal-verse-text"></div>
        <div class="modal-verse-ref" id="modal-verse-ref"></div>
      </div>

      <div class="modal-section" id="commentary-section">
        <div class="modal-section-title">📜 פרשנות</div>
        <div class="modal-text" id="modal-commentary"></div>
      </div>

      <div class="modal-section modal-life-point" id="lifepoint-section">
        <div class="modal-section-title">🌿 נקודת חיים</div>
        <div class="modal-text" id="modal-lifepoint"></div>
      </div>

      <div class="modal-nav">
        <button class="btn-nav" id="btn-prev" onclick="navigatePost(-1)">→ הקודם</button>
        <button class="btn-nav" id="btn-next" onclick="navigatePost(1)">הבא ←</button>
      </div>
    </div>
  </div>
</div>

<script>
const POSTS = {posts_json};

const SERIES_COLORS = {json.dumps(SERIES_COLORS, ensure_ascii=False)};
const SERIES_ICONS = {json.dumps(SERIES_ICONS, ensure_ascii=False)};

let currentPostIndex = -1;
let currentSeries = 'all';
let currentSearch = '';
let visibleIndices = POSTS.map((_, i) => i);

function getVisibleIndices() {{
  return POSTS.map((p, i) => {{
    const matchSeries = currentSeries === 'all' || p.series === currentSeries;
    const q = currentSearch.toLowerCase();
    const matchSearch = !q ||
      (p.title && p.title.includes(q)) ||
      (p.verse_text && p.verse_text.includes(q)) ||
      (p.verse_ref && p.verse_ref.includes(q)) ||
      (p.commentary && p.commentary.includes(q)) ||
      (p.life_point && p.life_point.includes(q));
    return matchSeries && matchSearch ? i : -1;
  }}).filter(i => i !== -1);
}}

function filterSeries(series) {{
  currentSeries = series;
  document.querySelectorAll('.tab-btn').forEach(btn => {{
    btn.classList.toggle('active', btn.dataset.series === series);
  }});
  updateDisplay();
}}

function searchPosts(query) {{
  currentSearch = query;
  updateDisplay();
}}

function updateDisplay() {{
  visibleIndices = getVisibleIndices();
  const cards = document.querySelectorAll('.post-card');
  cards.forEach((card, i) => {{
    card.classList.toggle('hidden', !visibleIndices.includes(i));
  }});
  const count = visibleIndices.length;
  document.getElementById('results-count').textContent = count + ' פסוקים';
  document.getElementById('no-results').classList.toggle('show', count === 0);
}}

function openPost(index) {{
  currentPostIndex = index;
  const post = POSTS[index];

  // Image
  const img = document.getElementById('modal-image');
  if (post.image) {{
    img.src = post.image;
    img.alt = post.title || '';
    img.style.display = 'block';
    img.onerror = () => img.style.display = 'none';
  }} else {{
    img.style.display = 'none';
  }}

  // Series badge
  const color = SERIES_COLORS[post.series] || '#888';
  const icon = SERIES_ICONS[post.series] || '📜';
  const badge = document.getElementById('modal-series-badge');
  badge.style.background = color;
  badge.textContent = icon + ' ' + post.series;

  // Title & author
  document.getElementById('modal-title').textContent = post.title || 'פסוק יומי';
  const authorEl = document.getElementById('modal-author');
  authorEl.textContent = post.author || '';
  authorEl.style.display = post.author ? 'block' : 'none';

  // Verse
  document.getElementById('modal-verse-text').textContent = post.verse_text ? '"' + post.verse_text + '"' : '';
  document.getElementById('modal-verse-ref').textContent = post.verse_ref || '';

  // Commentary
  const commSection = document.getElementById('commentary-section');
  const commEl = document.getElementById('modal-commentary');
  if (post.commentary && post.commentary.trim()) {{
    commEl.innerHTML = toHtml(post.commentary);
    commSection.style.display = 'block';
  }} else {{
    commSection.style.display = 'none';
  }}

  // Life point
  const lpSection = document.getElementById('lifepoint-section');
  const lpEl = document.getElementById('modal-lifepoint');
  if (post.life_point && post.life_point.trim()) {{
    lpEl.innerHTML = toHtml(post.life_point);
    lpSection.style.display = 'block';
  }} else {{
    lpSection.style.display = 'none';
  }}

  // Navigation buttons
  document.getElementById('btn-prev').disabled = index <= 0;
  document.getElementById('btn-next').disabled = index >= POSTS.length - 1;

  // Show modal
  document.getElementById('modal-overlay').classList.add('open');
  document.getElementById('modal').scrollTop = 0;
  document.body.style.overflow = 'hidden';
}}

function closePost() {{
  document.getElementById('modal-overlay').classList.remove('open');
  document.body.style.overflow = '';
}}

function handleOverlayClick(e) {{
  if (e.target === document.getElementById('modal-overlay')) {{
    closePost();
  }}
}}

function navigatePost(dir) {{
  const newIndex = currentPostIndex + dir;
  if (newIndex >= 0 && newIndex < POSTS.length) {{
    openPost(newIndex);
  }}
}}

function toHtml(text) {{
  if (!text) return '';
  return text.split('\\n').map(line => {{
    if (!line.trim()) return '';
    // Bold: *text*
    const html = line.replace(/\\*([^*]+)\\*/g, '<strong>$1</strong>');
    return '<p>' + html + '</p>';
  }}).filter(Boolean).join('\\n');
}}

// Keyboard navigation
document.addEventListener('keydown', e => {{
  if (!document.getElementById('modal-overlay').classList.contains('open')) return;
  if (e.key === 'Escape') closePost();
  if (e.key === 'ArrowRight') navigatePost(-1);
  if (e.key === 'ArrowLeft') navigatePost(1);
}});
</script>
</body>
</html>'''

    return html


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Find the chat file (Hebrew filename may cause issues, search by pattern)
    chat_path = None
    for fname in os.listdir(script_dir):
        if fname.endswith('.txt') and 'WhatsApp' in fname:
            chat_path = os.path.join(script_dir, fname)
            break

    if not chat_path:
        chat_path = os.path.join(script_dir, CHAT_FILE)

    output_path = os.path.join(script_dir, OUTPUT_FILE)

    print(f"Reading: {chat_path}")
    posts = parse_chat(chat_path)
    print(f"Parsed {len(posts)} posts")

    # Fix titles: first 2 posts in פסוקי גאולה series get the full title
    geula_fixed = 0
    for post in posts:
        if post['series'] == 'פסוקי גאולה' and geula_fixed < 2:
            post['title'] = 'הפסוק היומי - פסוקי גאולה לקראת יום העצמאות'
            geula_fixed += 1

    # Load custom images and match to posts
    image_map = load_custom_images(script_dir)
    print(f"Found {len(image_map)} custom images")
    matched = 0
    for post in posts:
        custom_img = find_image_for_post(post['title'], image_map)
        if custom_img:
            post['image'] = custom_img
            matched += 1
    print(f"Matched {matched} posts to custom images")
    unmatched_imgs = set(image_map.keys()) - {normalize_for_match(p['title']) for p in posts if p.get('image') and 'another picturs' in p['image']}
    for u in unmatched_imgs:
        print(f"  Unmatched image: {u}")

    # ── פסוקים ידניים (נוספו מחוץ לווטסאפ) ──────────────────────────
    MANUAL_POSTS = [
        {
            'title': 'הפסוק היומי - פסוקי גאולה לכבוד יום העצמאות',
            'author': 'הרב יואב אוריאל',
            'verse_text': 'עוֹד תִּטְּעִי כְרָמִים בְּהָרֵי שֹׁמְרוֹן נָטְעוּ נֹטְעִים וְחִלֵּלוּ. כִּי יֶשׁ יוֹם קָרְאוּ נֹצְרִים בְּהַר אֶפְרָיִם קוּמוּ וְנַעֲלֶה צִיּוֹן אֶל ה\' אֱלֹהֵינוּ',
            'verse_ref': 'ירמיהו לא, ד-ה',
            'commentary': 'נבואת הגאולה אינה מסתפקת בחזון רוחני מופשט, אלא יורדת אל הקרקע, אל החקלאות ואל עבודת האדמה. החורבן גרם לארץ להיות שוממה, ובשיבה אליה הרי השומרון יתמלאו בכרמים. העמל הפיזי של בניין הארץ והפרחת השממה הוא השלב הראשון שמוביל בסופו של דבר לקריאה הרוחנית העליונה \'קומו ונעלה ציון\'. הקודש והחול אינם מנותקים; הם משלימים זה את זה בתהליך ארוך וטבעי של תקומה.',
            'life_point': 'לפעמים העשייה היומיומית והשוחקת נראית לנו רחוקה מעולם של קדושה ורוח. הפסוק מלמד אותנו שכל נטיעה, כל בנייה וכל מאמץ שלנו הם חלק מתהליך גאולה ענק. נשתדל היום להתבונן בעשייה הפשוטה והחומרית שלנו כחלק מבניין האומה, ולחבר את עבודת הכפיים לחזון רוחני גדול. קומו ונעלה ציון!',
            'series': 'פסוקי גאולה',
            'image': 'another picturs/עוד תטעי כרמים.png',
        },
        {
            'title': 'הפסוק היומי - פסוקי גאולה לכבוד יום העצמאות',
            'author': 'הרב יואב אוריאל',
            'verse_text': 'כִּי אַעֲלֶה אֲרֻכָה לָךְ וּמִמַּכּוֹתַיִךְ אֶרְפָּאֵךְ נְאֻם ה\' כִּי נִדָּחָה קָרְאוּ לָךְ צִיּוֹן הִיא דֹּרֵשׁ אֵין לָהּ. כֹּה אָמַר ה\' הִנְנִי שָׁב שְׁבוּת אָהֳלֵי יַעֲקוֹב וּמִשְׁכְּנֹתָיו אֲרַחֵם וְנִבְנְתָה עִיר עַל תִּלָּהּ',
            'verse_ref': 'ירמיהו ל, יז-יח',
            'commentary': 'אומות העולם הביטו על ישראל בגלות וחשבו שהסיפור שלנו נגמר. קראו לנו "נידחה" וסברו שאין מי שחפץ ודורש בציון. לפעמים הכי קשה לעמוד מול כל העולם שכבר התיאש מאיתנו ומבזה אותנו. אבל הגאולה אינה רק חזרה למה שהיה, אלא תשובה ניצחת לכל המייאשים. פתאום עם ישראל הופך להיות מחדש למושא ההערצה של העולם כולו.',
            'life_point': 'לא פעם קולות מבחוץ או מחשבות מבפנים מנסים לשדר לנו ייאוש ולטעון שמצבנו חסר תקנה. הפסוק הזה הוא מרשם אלוהי של תקווה אמיתית. נזכור היום שגם פצעים לאומיים ופרטיים עמוקים ביותר יכולים להירפא. אל לנו להקשיב לקולות המחלישים, אלא לאחוז בחוזקה בהבטחת הרפואה והבניין.',
            'series': 'פסוקי גאולה',
            'image': 'another picturs/כי אעלה ארוכה לך.png',
        },
        {
            'title': 'הפסוק היומי - פסוקי גאולה לקראת יום העצמאות',
            'author': 'הרב יואב אוריאל',
            'verse_text': 'לְמַעַן צִיּוֹן לֹא אֶחֱשֶׁה וּלְמַעַן יְרוּשָׁלַ‍ִם לֹא אֶשְׁקוֹט עַד יֵצֵא כַנֹּגַהּ צִדְקָהּ וִישׁוּעָתָהּ כְּלַפִּיד יִבְעָר. וְרָאוּ גוֹיִם צִדְקֵךְ וְכָל מְלָכִים כְּבוֹדֵךְ',
            'verse_ref': 'ישעיהו סב, א-ב',
            'commentary': 'הקב"ה כביכול מצהיר שאינו יכול "לשקוט" ולהחריש עד שעם ישראל יגיע לגאולתו השלמה והמלאה. התוצאה היא תהליך הגאולה אינו פסיבי ונסתר. איננו נגאלים כגנבים בחושך. אלא אנו חותרים לתהליך בראש מורם בוער, נוכח ואקטיבי. הצדק והישועה של ירושלים חייבים להאיר בעוצמה גלויה כלפיד, כדי שכל העולם כולו יכיר בתפארתה של האומה.',
            'life_point': 'אם בורא עולם "לא מחריש" ולא שוקט למען בניינה של ירושלים, גם אנחנו לא יכולים לעמוד מנגד ולצפות מהצד. נשתדל היום לחיות מתוך אותה אכפתיות ובעירה פנימית, ולא להשלים עם הבינוניות בשום תחום. כל מעשה של הוספת אור בישראל הוא חלק מאותו לפיד ישועה שמאיר את העולם כולו.',
            'series': 'פסוקי גאולה',
            'image': 'another picturs/למען ציון לא אחשה.png',
        },
        {
            'title': 'הפסוק היומי - פסוקי גאולה',
            'author': 'הרב יואב אוריאל',
            'verse_text': 'כִּי זֹאת הַבְּרִית אֲשֶׁר אֶכְרֹת אֶת בֵּית יִשְׂרָאֵל אַחֲרֵי הַיָּמִים הָהֵם נְאֻם ה\' נָתַתִּי אֶת תּוֹרָתִי בְּקִרְבָּם וְעַל לִבָּם אֶכְתֲּבֶנָּה וְהָיִיתִי לָהֶם לֵאלֹהִים וְהֵמָּה יִהְיוּ לִי לְעָם',
            'verse_ref': 'ירמיהו לא, לב',
            'commentary': 'הנביא מבטיח ברית חדשה שתיכרת עם ישראל. מדובר בשינוי עמוק של החיבור שלנו אליה. בגלות נחוותה התורה לעיתים כדבר חיצוני שכופה את עצמו עלינו. לעומת זאת, לעתיד לבוא היא תהיה טבועה במהותנו. הגאולה השלמה מתבטאת בכך שרצון ה\' הופך להיות הרצון הפנימי והטבעי של העם, עד שהתורה חקוקה על ליבם ללא צורך בתזכורת חיצונית.',
            'life_point': 'במבט ראשון, קיום מצוות עשוי להיראות כחובה טכנית שעלינו לבצע. אך הנביא מגלה לנו שבגאולה אנו צועדים לקראת חיבור אורגני ופנימי. כדאי לשים לב היום למצווה או הנהגה טובה שאנו עושים, ולנסות לקיים אותה מתוך חיבור של הלב ורצון פנימי, ולא רק מתוך הרגל. נתרגל לתת לתורה מקום טבעי וזורם בחיים שלנו.',
            'series': 'פסוקי גאולה',
            'image': 'another picturs/כי זאת הברית.png',
        },
        {
            'title': 'הפסוק היומי - פסוקי גאולה',
            'author': 'הרב יואב אוריאל',
            'verse_text': 'וַתֹּאמֶר צִיּוֹן עֲזָבַנִי ה\' וַאדֹנָי שְׁכֵחָנִי. הֲתִשְׁכַּח אִשָּׁה עוּלָהּ מֵרַחֵם בֶּן בִּטְנָהּ גַּם אֵלֶּה תִשְׁכַּחְנָה וְאָנֹכִי לֹא אֶשְׁכָּחֵךְ. הֵן עַל כַּפַּיִם חַקֹּתִיךְ חוֹמֹתַיִךְ נֶגְדִּי תָּמִיד',
            'verse_ref': 'ישעיהו מט, יד-טז',
            'commentary': 'ברגעי משבר ארוכים עלולה לעלות התחושה הקשה מכל: תחושת הנטישה והשכחה. ציון זועקת שה\' עזב אותה. אך תשובת הקב"ה מוחצת כל ספק: הקשר בין ה\' לישראל עמוק וטבעי יותר מקשר של אם לתינוקה. האהבה האלוהית חקוקה בעצם המציאות, ולכן גם כשאנו מרגישים נשכחים, אנו תמיד מונחים על כפיים ומוגנים.',
            'life_point': 'ישנם רגעים בחיים הלאומיים והפרטיים שבהם נראה שנותרנו לבד במערכה החשוכה. הנביא מזכיר לנו שמדובר באשליה ובהסתר זמני בלבד. ברגעים הכי קודרים שנופלים עלינו, נזכור: הקשר שלנו עם בורא עולם הוא נצחי ובלתי ניתן לניתוק.',
            'series': 'פסוקי גאולה',
            'image': 'another picturs/הן על כפים חקותיך.png',
        },
    ]
    posts.extend(MANUAL_POSTS)
    print(f"Added {len(MANUAL_POSTS)} manual posts — total: {len(posts)}")

    # Show series breakdown
    from collections import Counter
    series_count = Counter(p['series'] for p in posts)
    for series, count in sorted(series_count.items()):
        print(f"  {series}: {count}")

    html = build_html(posts)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\nWebsite saved: {output_path}")
    print(f"Total size: {len(html):,} bytes")


if __name__ == '__main__':
    main()
