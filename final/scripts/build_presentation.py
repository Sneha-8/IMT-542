"""Generate IMT542_Final_Project.pptx — matches presentation/index.html (v4)."""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

OUT = Path(__file__).resolve().parent.parent / "presentation" / "IMT542_Final_Project.pptx"
UW_PURPLE = RGBColor(0x4B, 0x2E, 0x83)

SLIDES = [
    ("LocalFind", "One place to discover small businesses in your neighborhood.\nSneha Reddy | IMT 542 | github.com/Sneha-8/IMT-542"),
    (
        "Information story — who and why",
        "Story: Community members find small businesses around them (cafes, salons, shops).\n\n"
        "Who benefits:\n"
        "  Residents — discover shops they did not know existed nearby\n"
        "  Owners — more discoverability in one combined feed\n\n"
        "Why it matters:\n"
        "  Local shops are hard to see next to big chains\n"
        "  Supporting nearby business keeps money in the community\n"
        "  One search beats checking Yelp, Google, and social separately",
    ),
    (
        "Current problems",
        "Most people do not know how many small businesses exist near them.\n"
        "There is no single way to answer what local shops are nearby.\n"
        "Information is split across Yelp, Google, Instagram, chamber sites, owner pages.\n"
        "Each source uses different fields, ads, and rules — every search starts over.\n\n"
        "The data exists. It is not combined in a form people can use.",
    ),
    (
        "FAIR assessment — Yelp + OpenStreetMap",
        "                Yelp Fusion          OpenStreetMap\n"
        "Findable         Partial              Partial\n"
        "Accessible       Partial (API key)    Partial (throttle)\n"
        "Interoperable    Low                  Partial (tags)\n"
        "Reusable         Low (display-only)   High (ODbL)\n\n"
        "Yelp: ratings, photos, hours. OSM: open map data. Neither alone fits our story.",
    ),
    (
        "Our solution — SBP v1.0 + LocalFind",
        "Pipeline: Yelp + OSM -> normalizer -> cache -> API -> LocalFind UI\n\n"
        "Design for FAIR gaps:\n"
        "  Findable — stable id, schema_version\n"
        "  Accessible — REST + web (ZIP, category, near me)\n"
        "  Interoperable — one JSON shape for both sources\n"
        "  Reusable — provenance + quality_flags on every response\n\n"
        "Example: merged record with name, zip_code, hours, rating, yelp_url, osm_url",
    ),
    (
        "Quality, performance, security",
        "Quality: JSON Schema; completeness_score; 12 pytest tests\n"
        "Performance: cached search ~20-100 ms; live refresh ~15-40 s\n"
        "Security: public API hides phone/email; Bearer unlocks contact; keys in .env only\n"
        "Tradeoffs: cache speed vs freshness; more metadata vs larger payloads",
    ),
    (
        "Demo — LocalFind",
        "Search by category, ZIP, or near me.\n"
        "Open a listing for hours, ratings, directions.\n"
        "http://127.0.0.1:8777/web/platform.html",
    ),
    (
        "Thank you",
        "LocalFind — discover local small businesses; more visibility for owners.\n"
        "github.com/Sneha-8/IMT-542/tree/main/final\nQuestions?",
    ),
]


def add_slide(prs, title: str, body: str):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    tb = slide.shapes.add_textbox(Inches(0.45), Inches(0.3), Inches(9.1), Inches(0.95))
    p = tb.text_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = UW_PURPLE
    bb = slide.shapes.add_textbox(Inches(0.45), Inches(1.25), Inches(9.1), Inches(5.5))
    tf = bb.text_frame
    tf.word_wrap = True
    for i, line in enumerate(body.split("\n")):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.text = line
        para.font.size = Pt(17)
        para.space_after = Pt(6)


def main():
    prs = Presentation()
    for t, b in SLIDES:
        add_slide(prs, t, b)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(OUT))
    print(f"Wrote {OUT} ({len(SLIDES)} slides)")


if __name__ == "__main__":
    main()
