#!/usr/bin/env python3
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Kevin White
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Create the media files used by gwizard_data_base.ged and gwizard_mergefrom.ged.

Usage::

    python make_gwizard_testdata_images.py [IMAGES_DIR]

IMAGES_DIR defaults to C:\\gramps_dev\\gramps_gwizard_mediafix_plugin\\images.
Two folders are written inside it:

* ``FamilyTree``: the media base path to set in Gramps. Holds the files the
  GEDCOMs reference by relative path, one file that no media record uses,
  and one deliberately corrupt file.
* ``Downloads``: files referenced by absolute path from outside the media
  base path.

Two referenced files are deliberately *not* created, so they show up as
missing: ``FamilyTree\\Duncan_MacDonald_school_photo_1925.jpg`` and
``C:\\Users\\GWizardTester\\Pictures\\obrien_grave_1931.jpg``.

Requires Pillow (``pip install pillow``).
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from __future__ import annotations
import os
import random
import sys

# -------------------------------------------------------------------------
#
# Pillow
#
# -------------------------------------------------------------------------
from PIL import Image, ImageDraw, ImageFilter, ImageFont

DEFAULT_DIR = r"C:\gramps_dev\gramps_gwizard_mediafix_plugin\images"

PAPER = (238, 228, 203)
INK = (52, 40, 30)
FADED = (120, 104, 84)
SEPIA_DARK = (74, 56, 38)

_FONT_CANDIDATES = {
    "serif": ("DejaVuSerif.ttf", "georgia.ttf", "times.ttf", "Times New Roman.ttf"),
    "serif-bold": ("DejaVuSerif-Bold.ttf", "georgiab.ttf", "timesbd.ttf"),
    "script": ("DejaVuSerif-Italic.ttf", "georgiai.ttf", "timesi.ttf"),
    "mono": ("DejaVuSansMono.ttf", "consola.ttf", "cour.ttf"),
}


def font(kind: str, size: int) -> ImageFont.ImageFont:
    """Return a TrueType font of the given kind, or Pillow's default."""
    for name in _FONT_CANDIDATES[kind]:
        for folder in ("", "/usr/share/fonts/truetype/dejavu", r"C:\Windows\Fonts"):
            try:
                return ImageFont.truetype(os.path.join(folder, name), size)
            except OSError:
                continue
    return ImageFont.load_default(size=size)


def paper(width: int, height: int, seed: int, tint: tuple = PAPER) -> Image.Image:
    """Return an aged-paper background with speckles and a darker edge."""
    rng = random.Random(seed)
    img = Image.new("RGB", (width, height), tint)
    draw = ImageDraw.Draw(img)
    for _ in range(width * height // 300):
        x, y = rng.randrange(width), rng.randrange(height)
        shade = rng.randint(-28, 8)
        draw.point((x, y), fill=tuple(max(0, c + shade) for c in tint))
    edge = Image.new("L", (width, height), 0)
    ImageDraw.Draw(edge).rectangle(
        (18, 18, width - 18, height - 18), fill=255
    )
    edge = edge.filter(ImageFilter.GaussianBlur(22))
    dark = Image.new("RGB", (width, height), tuple(int(c * 0.78) for c in tint))
    return Image.composite(img, dark, edge)


def centred(draw: ImageDraw.ImageDraw, y: int, text: str, fnt, width: int, fill=INK):
    """Draw text centred horizontally at height y."""
    box = draw.textbbox((0, 0), text, font=fnt)
    draw.text(((width - (box[2] - box[0])) / 2, y), text, font=fnt, fill=fill)


def certificate(path: str, heading: str, sub: str, fields: list[tuple[str, str]],
                seed: int, size=(1100, 800)) -> None:
    """A bordered civil-registration style certificate."""
    w, h = size
    img = paper(w, h, seed)
    d = ImageDraw.Draw(img)
    d.rectangle((40, 40, w - 40, h - 40), outline=INK, width=4)
    d.rectangle((52, 52, w - 52, h - 52), outline=FADED, width=1)
    size = 44
    while size > 18:
        heading_font = font("serif-bold", size)
        box = d.textbbox((0, 0), heading, font=heading_font)
        if box[2] - box[0] <= w - 160:
            break
        size -= 2
    centred(d, 80, heading, heading_font, w)
    centred(d, 140, sub, font("serif", 24), w, FADED)
    y = 220
    for label, value in fields:
        d.text((110, y), label, font=font("serif", 24), fill=FADED)
        d.text((420, y - 4), value, font=font("script", 30), fill=INK)
        d.line((420, y + 34, w - 110, y + 34), fill=FADED, width=1)
        y += 66
    d.ellipse((w - 250, h - 210, w - 110, h - 70), outline=(140, 30, 30), width=4)
    centred_x = w - 180
    d.text((centred_x - 38, h - 152), "SEAL", font=font("serif-bold", 26),
           fill=(140, 30, 30))
    save(img, path)


def census(path: str, year: str, place: str, rows: list[list[str]], seed: int) -> None:
    """A ruled census population schedule."""
    w, h = 1400, 900
    img = paper(w, h, seed, (232, 226, 210))
    d = ImageDraw.Draw(img)
    centred(d, 30, "%s UNITED STATES FEDERAL CENSUS - POPULATION" % year,
            font("serif-bold", 34), w)
    centred(d, 80, place, font("serif", 24), w, FADED)
    cols = [60, 140, 520, 760, 860, 980, 1340]
    heads = ["Line", "Name", "Relation", "Sex", "Age", "Birthplace"]
    top = 140
    for i, x in enumerate(cols):
        d.line((x, top, x, h - 60), fill=FADED, width=2)
    for r in range(16):
        y = top + r * 44
        d.line((60, y, 1340, y), fill=FADED, width=1)
    for i, head in enumerate(heads):
        d.text((cols[i] + 8, top + 8), head, font=font("serif-bold", 22), fill=INK)
    fill_rows = [[str(41 + i)] + row for i, row in enumerate(rows)]
    for r, row in enumerate(fill_rows, start=1):
        y = top + r * 44 + 6
        for i, cell in enumerate(row):
            d.text((cols[i] + 10, y), cell, font=font("script", 24), fill=SEPIA_DARK)
    save(img, path)


def newspaper(path: str, masthead: str, date: str, heading: str,
              body: list[str], seed: int) -> None:
    """A newspaper clipping with an obituary."""
    w, h = 900, 1100
    img = paper(w, h, seed, (226, 222, 208))
    d = ImageDraw.Draw(img)
    centred(d, 30, masthead, font("serif-bold", 48), w)
    d.line((40, 100, w - 40, 100), fill=INK, width=3)
    centred(d, 110, date, font("serif", 20), w, FADED)
    centred(d, 170, heading, font("serif-bold", 34), w)
    y = 240
    for line in body:
        d.text((70, y), line, font=font("serif", 24), fill=INK)
        y += 36
    rng = random.Random(seed)
    for x0 in (70, 470):
        yy = max(y + 40, 700)
        while yy < h - 60:
            d.line((x0, yy, x0 + rng.randint(260, 360), yy), fill=FADED, width=3)
            yy += 22
    save(img, path)


def grave(path: str, lines: list[str], seed: int) -> None:
    """A photo of a grave marker in grass."""
    w, h = 900, 1100
    rng = random.Random(seed)
    img = Image.new("RGB", (w, h), (120, 150, 170))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 700, w, h), fill=(70, 105, 55))
    for _ in range(4000):
        x, y = rng.randrange(w), rng.randrange(700, h)
        d.line((x, y, x + rng.randint(-3, 3), y - rng.randint(4, 14)),
               fill=(50 + rng.randint(0, 40), 90 + rng.randint(0, 50), 40))
    d.rounded_rectangle((220, 230, 680, 860), radius=60, fill=(150, 148, 140))
    d.pieslice((220, 120, 680, 460), 180, 360, fill=(150, 148, 140))
    y = 300
    for i, line in enumerate(lines):
        centred(d, y, line, font("serif-bold" if i == 0 else "serif", 40 if i == 0 else 30),
                w, (60, 58, 54))
        y += 70 if i == 0 else 52
    img = img.filter(ImageFilter.GaussianBlur(0.8))
    save(img, path)


def portrait(path: str, caption: str, seed: int, people: int = 1) -> None:
    """A sepia studio portrait (or group photo) with a caption."""
    w, h = 800, 1000 if people == 1 else 700
    if people > 1:
        w = 1200
    rng = random.Random(seed)
    img = Image.new("RGB", (w, h), (196, 172, 136))
    d = ImageDraw.Draw(img)
    for y in range(h):
        shade = int(30 * y / h)
        d.line((0, y, w, y), fill=(196 - shade, 172 - shade, 136 - shade))
    spacing = w / (people + 1)
    for p in range(people):
        cx = int(spacing * (p + 1)) + rng.randint(-20, 20)
        top = 220 if people == 1 else 200 + rng.randint(-30, 30)
        r = 110 if people == 1 else 70
        d.ellipse((cx - r, top, cx + r, top + int(r * 2.5)), fill=SEPIA_DARK)
        d.rounded_rectangle((cx - r * 2, top + int(r * 2.2), cx + r * 2, h - 80),
                            radius=r, fill=(88, 66, 46))
    d.rectangle((0, h - 70, w, h), fill=(232, 222, 200))
    centred(d, h - 56, caption, font("script", 30), w, SEPIA_DARK)
    img = img.filter(ImageFilter.GaussianBlur(1.2))
    save(img, path)


def save(img: Image.Image, path: str) -> None:
    """Save as PNG or JPEG depending on the extension."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if path.lower().endswith(".png"):
        img.save(path, "PNG", optimize=True)
    else:
        img.save(path, "JPEG", quality=82)
    print("wrote", path)


def main(images_dir: str) -> None:
    tree = os.path.join(images_dir, "FamilyTree")
    downloads = os.path.join(images_dir, "Downloads")

    # ---- base tree: files that follow the Media Fix naming template ----
    certificate(
        os.path.join(tree, "I00001_MacDonald_Angus-Birth_certificate_of_Angus_MacDonald-1890.png"),
        "EXTRACT OF AN ENTRY IN A REGISTER OF BIRTHS",
        "Parish of Inverness, County of Inverness, Scotland",
        [("Name", "Angus MacDonald"), ("When born", "1890, March Twelfth"),
         ("Where born", "Church Street, Inverness"), ("Father", "Donald MacDonald, crofter"),
         ("Mother", "Catherine MacDonald, m.s. Fraser"), ("Registered", "Entry No. 112")],
        seed=1,
    )
    census(
        os.path.join(tree, "I00001_MacDonald_Angus-census_Angus_MacDonald_household-1920.jpg"),
        "1920", "Boston, Suffolk County, Massachusetts - Sheet 7A",
        [["MacDonald, Angus", "Head", "M", "29", "Scotland"],
         ["MacDonald, Mary", "Wife", "F", "27", "Scotland"],
         ["MacDonald, Duncan", "Son", "M", "5", "Massachusetts"],
         ["MacDonald, Margaret", "Daughter", "F", "3", "Massachusetts"],
         ["MacDonald, Ewan", "Son", "M", "1", "Massachusetts"]],
        seed=2,
    )
    portrait(
        os.path.join(tree, "I00006_von_Holt_Clara-Portrait_of_Clara_von_Holt-1880.jpg"),
        "Clara von Holt, Bremen, 1880", seed=3,
    )
    certificate(
        os.path.join(tree, "F00001_MacDonald-Marriage_record_of_Angus_MacDonald_and_Mary_MacLean-1912.png"),
        "EXTRACT OF AN ENTRY IN A REGISTER OF MARRIAGES",
        "District of Inverness, Scotland - 1912",
        [("When married", "1912, June Fifteenth"), ("Bridegroom", "Angus MacDonald, 22"),
         ("Bride", "Mary MacLean, 20"), ("Where", "Free North Church, Inverness"),
         ("Witnesses", "Ewan Fraser, Isabella Ross"), ("Registered", "Entry No. 33")],
        seed=4,
    )
    census(
        os.path.join(tree, "I00007_Schmidt_Johann-census_Johann_Schmidt_household_sheet_12B-1900.jpg"),
        "1900", "Cincinnati, Hamilton County, Ohio - Ward 11, Sheet 12B",
        [["Schmidt, Johann", "Head", "M", "50", "Germany"],
         ["Schmidt, Anna", "Wife", "F", "47", "Germany"],
         ["Schmidt, Heinrich", "Son", "M", "20", "Ohio"],
         ["Schmidt, John", "Son", "M", "22", "Ohio"]],
        seed=19,
    )
    certificate(
        os.path.join(tree, "S00010-Death_certificate_of_Johann_Schmidt-1910.png"),
        "CERTIFICATE OF DEATH",
        "State of Ohio - Bureau of Vital Statistics",
        [("Full name", "Johann Schmidt"), ("Date of death", "April 3, 1910"),
         ("Place", "Cincinnati, Hamilton Co."), ("Birthplace", "Bamberg, Bavaria"),
         ("Age", "60 years"), ("File No.", "4521")],
        seed=5,
    )
    grave(
        os.path.join(tree, "I00011_O_Brien_Patrick-Grave_marker_of_Patrick_O_Brien-1931.jpg"),
        ["PATRICK O'BRIEN", "BORN CORK 1870", "DIED 1931", "REQUIESCAT IN PACE"], seed=6,
    )

    # ---- base tree: files with problems for Media Fix ----
    grave(os.path.join(tree, "Johann Schmidt grave.JPG"),
          ["JOHANN SCHMIDT", "1850 - 1910", "RUHE IN FRIEDEN"], seed=7)
    portrait(os.path.join(tree, "family_reunion_1950.jpg"),
             "Turner family reunion, Leeds, 1950", seed=8, people=5)
    portrait(os.path.join(tree, "unknown_woman_1900.jpg"), "Unknown, about 1900", seed=9)
    newspaper(
        os.path.join(tree, "obit_obrien_1931.jpg"), "THE BOSTON EVENING TRANSCRIPT",
        "Monday, February 16, 1931", "PATRICK O'BRIEN",
        ["Patrick O'Brien, a native of Cork, died", "Saturday at his home in South Boston,",
         "on his sixty-first birthday. He came to", "this country as a young man and worked",
         "for many years on the waterfront.", "Funeral Wednesday, Gate of Heaven."],
        seed=10,
    )
    portrait(os.path.join(tree, "mary_maclean_portrait.jpg"), "Mary MacLean", seed=11)
    newspaper(
        os.path.join(tree, "obit_maclean_1970.jpg"), "THE BOSTON GLOBE",
        "Thursday, March 12, 1970", "MARY (MacLEAN) MacDONALD",
        ["Mary MacDonald, 77, born in Portree on", "the Isle of Skye, died Monday. Widow of",
         "Angus MacDonald. Survived by her sons", "Duncan and Ewan and daughter Margaret.",
         "Services at St. Margaret's Church."],
        seed=17,
    )
    certificate(
        os.path.join(tree, "Duvault_Thomas_baptism_1868.jpg"), "CERTIFICATE OF BAPTISM",
        "Trinity Lutheran Church, Lancaster, Pennsylvania",
        [("Child", "Thomas Duvault"), ("Born", "1868"), ("Father", "Thomas Duvault"),
         ("Register", "Baptisms 1868, p. 44")],
        seed=18, size=(1100, 620),
    )
    certificate(
        os.path.join(tree, "orphan_scan_0007.png"), "CERTIFICATE OF BAPTISM",
        "St. Andrew's Church", [("Name", "(illegible)"), ("Date", "18__")], seed=12,
        size=(900, 520),
    )
    # Deliberately corrupt: a JPEG header followed by junk.
    os.makedirs(tree, exist_ok=True)
    with open(os.path.join(tree, "broken_scan.jpg"), "wb") as handle:
        handle.write(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00" + bytes(range(256)) * 8)
    print("wrote", os.path.join(tree, "broken_scan.jpg"), "(corrupt on purpose)")

    # ---- merge-from file: files that follow the naming template ----
    certificate(
        os.path.join(tree, "I00001_McDonald_Angus-Birth_certificate_of_Angus_McDonald-1890.png"),
        "EXTRACT OF AN ENTRY IN A REGISTER OF BIRTHS",
        "Parish of Inverness, County of Inverness, Scotland",
        [("Name", "Angus McDonald"), ("When born", "1890, March Twelfth"),
         ("Where born", "Inverness"), ("Registered", "Entry No. 112")],
        seed=13, size=(1100, 620),
    )
    portrait(os.path.join(tree, "I00011_Turner_Bill-Portrait_of_Bill_Turner-1925.jpg"),
             "Bill Turner, Leeds, 1925", seed=14)

    # ---- outside the media base path (absolute paths) ----
    certificate(
        os.path.join(downloads, "scan0042.jpg"), "CERTIFICATE OF NATURALIZATION",
        "Circuit Court of Milwaukee County, Wisconsin",
        [("Name", "Friedrich von Steuben"), ("Former nationality", "Prussia"),
         ("Date", "October 2, 1878"), ("Certificate No.", "1187")],
        seed=15, size=(1100, 640),
    )
    certificate(
        os.path.join(downloads, "Ohio death cert Johann Schmid.jpg"),
        "CERTIFICATE OF DEATH", "State of Ohio - Bureau of Vital Statistics",
        [("Full name", "Johann Schmid"), ("Date of death", "April 3, 1910"),
         ("Place", "Cincinnati"), ("File No.", "4521")],
        seed=16, size=(1100, 600),
    )


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DIR)
