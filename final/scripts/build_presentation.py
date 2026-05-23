"""Generate IMT542_Final_Project.pptx — narrative deck (no rubric section labels)."""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

OUT = Path(__file__).resolve().parent.parent / "presentation" / "IMT542_Final_Project.pptx"
UW_PURPLE = RGBColor(0x4B, 0x2E, 0x83)

SLIDES = [
    (
        "LocalFind",
        "Helping Seattle residents discover and support independent neighborhood businesses.\n\n"
        "Sneha Reddy | IMT 542 | Spring 2026\n"
        "github.com/Sneha-8/IMT-542",
    ),
    (
        "Meet Alex",
        "Alex lives in Capitol Hill and wants coffee from a local shop with vegan options and Wi-Fi. "
        "They open Yelp, scroll past ads, check Instagram, and often give up.\n\n"
        "The information exists — it is scattered and locked in apps that were not built for this decision.",
    ),
    (
        "Why local discovery matters",
        "Local spending strengthens neighborhood economies.\n"
        "Small shops lack chain-level SEO and ad budgets.\n"
        "Civic tools and newsletters need machine-readable listings, not HTML tables.",
    ),
    (
        "Where information lives today",
        "Yelp and Google (proprietary, ad-driven)\n"
        "Chamber HTML directories (no stable IDs)\n"
        "Social posts and owner sites (unstructured)\n\n"
        "Problems: cannot combine open-now + tags + neighborhood in one query; "
        "no provenance; owner contact mixed with public data.",
    ),
    (
        "The journey we designed",
        "Sources -> normalize to one schema -> document database -> REST API -> LocalFind UI\n\n"
        "Same facts can power a website, map layer, newsletter, or assistant without re-scraping.",
    ),
    (
        "The LocalFind experience",
        "Search by keyword, neighborhood, and tags.\n"
        "See ratings, hours, open-now status, and popular items.\n"
        "Business detail with website, directions, and provenance footer.\n\n"
        "See live prototype: final/web/platform.html (open in browser during demo)",
    ),
    (
        "Portable structure — what changed",
        "Envelope: schema version, provenance, completeness on every response.\n"
        "Records: split addresses, E.164 phones, tags, hours, quality flags.\n"
        "Access: HTTPS search API instead of a static JSON file only developers can read.",
    ),
    (
        "Trust and privacy",
        "Provenance and license on every payload.\n"
        "Quality flags so consumers know what is missing.\n"
        "Public listings hide owner email/phone unless Bearer token authorizes access.",
    ),
    (
        "How we got here",
        "Started with Flask + JSON file.\n"
        "Added MongoDB and aggregation endpoints.\n"
        "Shipped schema v1.0, normalizer, tests, and this UI prototype.\n\n"
        "Production path: Yelp Fusion feeds the same normalizer.",
    ),
    (
        "Under the hood",
        "Flask API | MongoDB/Mongita | Python normalizer | pytest + JSON Schema\n\n"
        "Demo: six Seattle businesses. Live demo via ngrok during Q&A.",
    ),
    (
        "What comes next",
        "Live Yelp ingestion with caching.\n"
        "Public deployment of LocalFind.\n"
        "Partnerships with neighborhood associations.\n"
        "Feeds for maps and civic newsletters.",
    ),
    (
        "Thank you",
        "LocalFind — portable neighborhood business information.\n\n"
        "github.com/Sneha-8/IMT-542/tree/main/final\n"
        "Questions?",
    ),
]


def add_slide(prs, title: str, body: str):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    tb = slide.shapes.add_textbox(Inches(0.5), Inches(0.35), Inches(9), Inches(1.0))
    p = tb.text_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = UW_PURPLE
    bb = slide.shapes.add_textbox(Inches(0.5), Inches(1.4), Inches(9), Inches(5.3))
    tf = bb.text_frame
    tf.word_wrap = True
    for i, line in enumerate(body.split("\n")):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.text = line
        para.font.size = Pt(19)
        para.space_after = Pt(8)


def main():
    prs = Presentation()
    for t, b in SLIDES:
        add_slide(prs, t, b)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(OUT))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
