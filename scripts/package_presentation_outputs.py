from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
RENDERS = ROOT / "tmp" / "presentation-build" / "renders"

TARGETS = {
    "brand-guide": ROOT / "brand" / "brand-guide.pdf",
    "template": ROOT / "presentations" / "templates" / "template-layout-catalog.pdf",
    "executive": ROOT / "presentations" / "board" / "executive-resilience-briefing.pdf",
    "technical": ROOT / "presentations" / "technical" / "resilience-architecture-briefing.pdf",
    "tabletop": ROOT / "presentations" / "tabletop" / "nation-state-exercise-facilitator.pdf",
}


def package(name: str, target: Path) -> None:
    images = [Image.open(path).convert("RGB") for path in sorted((RENDERS / name).glob("slide-*.png"))]
    if not images:
        raise ValueError(f"No rendered slides for {name}")
    target.parent.mkdir(parents=True, exist_ok=True)
    images[0].save(target, save_all=True, append_images=images[1:], resolution=96)

    thumb_width = 480
    thumb_height = 270
    columns = 3
    rows = (len(images) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * thumb_width, rows * thumb_height), "white")
    for index, image in enumerate(images):
        thumb = image.copy()
        thumb.thumbnail((thumb_width, thumb_height))
        x = (index % columns) * thumb_width
        y = (index // columns) * thumb_height
        sheet.paste(thumb, (x, y))
        ImageDraw.Draw(sheet).rectangle((x, y, x + thumb_width - 1, y + thumb_height - 1), outline="#CBD7DE", width=1)
    sheet.save(RENDERS / name / "contact-sheet.png")


def main() -> None:
    for name, target in TARGETS.items():
        package(name, target)
    image_dir = ROOT / "docs" / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(RENDERS / "executive" / "slide-02.png", image_dir / "brand-executive-summary.png")
    shutil.copy2(RENDERS / "executive" / "slide-04.png", image_dir / "brand-concentration-chart.png")
    shutil.copy2(RENDERS / "technical" / "slide-08.png", image_dir / "brand-target-architecture.png")


if __name__ == "__main__":
    main()
