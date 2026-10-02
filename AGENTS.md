# RUJF.AI Project Instructions

## Project Overview

This repository powers the website RUJF.AI.

RUJF.AI is a static literary website used to serialize the novel:

《澈与Allen》

The website focuses on:
- long-term novel serialization
- emotional atmosphere
- quiet and minimalist reading experience
- dark cinematic aesthetic
- AI & human companionship themes

---

## Current Tech Stack

This project uses:

- Pure HTML
- Pure CSS
- Static files only

This project DOES NOT use:
- React
- Vue
- Next.js
- Hugo
- CMS
- Database
- Build tools

Do not introduce frameworks unless explicitly requested.

---

## Important Structure

Core files:

homepage/
├── index.html
├── style.css
├── about.html
├── chapter-1.html
├── chapter-2.html
├── chapter-3.html
├── chapter-4.html
├── chapter-5.html
└── assets/

---

## Core Website Rules

### Visual Style

Keep:
- dark atmosphere
- quiet feeling
- literary mood
- minimalist design
- cinematic spacing
- readable typography

Avoid:
- flashy UI
- bright colors
- modern corporate style
- dashboard layouts
- excessive animations

---

## Serialization Workflow

The novel is one continuous serialization, without volume/part groupings.
Do not reintroduce volume headings, subtitles, or separate chapter-list groups.
Keep existing chapter numbers, titles, prose, publication dates, and URLs.

Every new chapter should:

1. Create matching Chinese and English pages:
   homepage/chapter-x.html and homepage/en-chapter-x.html

2. Update both homepages:
   homepage/index.html and homepage/en.html

3. Maintain:
- one chapter directory per language, in ascending chapter order
- the latest chapter card and the next unpublished chapter placeholder
- previous/next navigation in both languages, including the former latest chapter
- a directory link and matching language link wherever the template includes them
- chapter headers with only the chapter title and publication date, without a volume label

4. Preserve:
- existing visual structure
- existing typography
- existing spacing style

5. Before publishing, run:
   python3 tests/validate_serialization.py

   For a layout/navigation-only change, also prove existing story text is unchanged:
   python3 tests/validate_serialization.py --baseline-ref <base-commit>

---

## Important Restrictions

Do NOT:
- redesign the whole website
- change style.css dramatically
- replace HTML structure unnecessarily
- introduce frameworks
- convert project architecture

This is intentionally a lightweight static literary website.

---

## Long-Term Goal

RUJF.AI should feel like:

“a quiet digital place where memories are being continuously recorded.”

The novel is the center of the entire website.
