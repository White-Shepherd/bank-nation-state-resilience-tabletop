from __future__ import annotations

from pathlib import Path

import streamlit as st

from . import SYNTHETIC_LABEL
from .presentation import PALETTE, build_executive_deck, executive_metrics, write_board_pdf


def render_executive_presentation(nodes, relationships, responsibilities, indicators, coverage):
    slides = build_executive_deck(nodes, relationships, responsibilities, indicators, coverage)
    metrics = executive_metrics(nodes, relationships, indicators, coverage)
    st.subheader("Executive resilience presentation")
    st.caption("Board-ready narrative derived from declared synthetic relationships. Counts are not probabilities or loss estimates.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Critical services", metrics["critical_service_count"])
    c2.metric("Tier 0 dependencies", metrics["tier0_count"])
    c3.metric("Declared relationships", metrics["relationship_count"])
    c4.metric("Warning indicators", metrics["warning_indicator_count"])

    slide_number = st.select_slider(
        "Presentation slide",
        options=list(range(1, len(slides) + 1)),
        format_func=lambda value: f"{value:02d} | {slides[value - 1].section}",
    )
    slide = slides[slide_number - 1]
    bullets = "".join(f"<li>{item}</li>" for item in slide.bullets)
    st.markdown(
        f"""
        <section aria-label="Slide {slide.number}: {slide.title}" style="background:{PALETTE['paper']};border-top:8px solid {PALETTE['teal']};padding:2.3rem 2.6rem;min-height:430px;border-radius:4px;box-shadow:0 8px 24px rgba(17,36,58,.10)">
          <p style="color:{PALETTE['blue']};font-weight:700;letter-spacing:.08em;margin:0 0 1rem">{slide.section.upper()} &nbsp; {slide.number:02d}</p>
          <h2 style="color:{PALETTE['ink']};font-size:2.45rem;line-height:1.12;max-width:1050px;margin:.2rem 0 1rem">{slide.title}</h2>
          <p style="color:{PALETTE['slate']};font-size:1.25rem;line-height:1.5;max-width:980px">{slide.subtitle}</p>
          <ul style="color:{PALETTE['ink']};font-size:1.08rem;line-height:1.7;max-width:980px">{bullets}</ul>
          <p style="color:{PALETTE['slate']};font-size:.75rem;margin-top:2rem">{SYNTHETIC_LABEL}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("Accessible text alternative and evidence references"):
        st.write(slide.title)
        st.write(slide.subtitle)
        for item in slide.bullets:
            st.write(f"- {item}")
        st.write("Supporting modeled identifiers:", ", ".join(slide.evidence_ids) or "Narrative synthesis")

    output_dir = Path("output")
    pptx = output_dir / "presentation" / "harbor-ridge-executive-resilience-briefing.pptx"
    pdf = output_dir / "pdf" / "harbor-ridge-executive-resilience-briefing.pdf"
    if not pdf.exists() and st.button("Generate board presentation PDF"):
        write_board_pdf(pdf, slides)
    downloads = st.columns(2)
    if pptx.exists():
        downloads[0].download_button("Download editable PowerPoint", pptx.read_bytes(), pptx.name, "application/vnd.openxmlformats-officedocument.presentationml.presentation")
    else:
        downloads[0].caption("Run the presentation asset generator to create the editable PowerPoint.")
    if pdf.exists():
        downloads[1].download_button("Download board presentation PDF", pdf.read_bytes(), pdf.name, "application/pdf")
