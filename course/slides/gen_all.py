#!/usr/bin/env python3
"""Batch-generate the 28 slide background images via draw.py (gpt-image-2).

- Writes each page's prompt to prompts/pNN.md (the deliverable prompt files)
- Calls draw.py sequentially, skipping pages that already have a PNG (resumable)
"""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
PROMPTS_DIR = HERE / "prompts"
OUT_DIR = HERE / "generated"
DRAW = Path.home() / ".claude" / "skills" / "draw" / "draw.py"

STYLE = (
    "Dark navy #171C28 presentation slide background, flat vector illustration "
    "style, thin-line monochrome icons in desaturated gray-blue, single amber "
    "#FFB454 focal element with everything else muted, generous negative space, "
    "clean grid layout, minimal, 16:9 widescreen, no Chinese text, "
    "minimal small English labels only. "
)

PROMPTS = {
    "p01": "Hero illustration for an AI coding agent course cover: a large glowing amber loop orbiting a small robot chip in the right third of frame, subtle circuit traces in the background, left two-thirds mostly empty dark space reserved for title text.",
    "p02": "Simple linear diagram: small person icon at left, single arrow to a cloud containing a neural chip icon at center-right, a return arrow below it, depicting one request-response API exchange, amber highlight on the cloud only, top third empty for heading.",
    "p03": "Nearly empty pause slide: one large thin-outline amber question mark slightly right of center with faint concentric circles radiating from it, everything else vast empty dark space.",
    "p04": "Metaphor illustration: minimalist side view of a car drawn in thin gray-blue lines, with a glowing amber brain chip seated as the driver in the cockpit, bottom third left empty for caption text.",
    "p05": "Radial hub diagram: central amber hexagon connected by even spokes to five orbiting thin-line icons - wrench, open book, eye, lightning bolt, shield - top area empty for heading.",
    "p06": "Split comparison: left half a tangled messy flowchart of many small dull-gray boxes with crossing arrows and a subtle X mark over it; right half one clean simple amber circular loop; thin vertical divider, top strip empty for heading.",
    "p07": "Nearly empty pause slide: large thin-outline code brackets and a blinking cursor symbol centered in amber, faint dot grid, vast dark negative space.",
    "p08": "Bold transition slide: single thick amber circular arrow loop at center with a small terminal prompt symbol inside it, large clean geometric sans-serif English words 'ONE LOOP' beneath, dramatic and minimal.",
    "p09": "Technical flow diagram: rounded rectangle labeled 'messages' at left, arrow to a brain chip labeled 'LLM' at center, then a diamond labeled 'stop_reason?' branching into a downward exit arrow and an amber return path passing through a gear labeled 'tools' looping back to messages; amber only on the return loop, small English labels.",
    "p10": "Dark code editor window mockup centered: window chrome with three dots, left gutter showing line numbers 1 to 30, the code area intentionally blank for text overlay, three horizontal amber highlight bars at different line positions.",
    "p11": "Dark terminal window mockup with three-dot title bar, mostly empty screen with a single amber prompt chevron at the top-left inside the window, subtle scanline texture, margin space around the window.",
    "p12": "Ascending stepped path: 12 small circular nodes arranged in three clustered groups of 3, 4 and 5 along a rising line from bottom-left to top-right, faint dashed rounded rectangles around each group with small English labels 'CORE', 'CONTEXT', 'MULTI-AGENT', an amber loop icon at the path start staying highlighted.",
    "p13": "Two-panel illustration: left panel a power strip with several sockets and one amber plug being inserted; right panel a clipboard checklist with three checkboxes where the top one is checked in amber; top strip empty for heading.",
    "p14": "Nearly empty pause slide: thin-outline gauge meter centered with an amber needle pointing near the full end and faint overflow droplets spilling, vast dark negative space around it.",
    "p15": "Row of three mini diagrams evenly spaced: first a main node forking off a smaller clean branch node, second a bookshelf with one amber book sliding out, third a wide rectangle being compressed into a narrow one by inward arrows; space below each left empty for labels.",
    "p16": "Background of three tall rounded-rectangle card outlines side by side, each topped with a thin-line icon - a branching fork, an open book, inward compress arrows - card bodies intentionally empty for overlay text, the middle card edged in amber.",
    "p17": "Kanban board: three columns of small sticky-note cards linked by thin left-to-right dependency arrows, one card in amber marked in progress; in the lower right a small gear with a clock face suggesting background work; top strip empty.",
    "p18": "Nearly empty pause slide: one large thin-outline robot icon centered with an amber outline, three fainter smaller robot silhouettes fading in behind it, vast dark space.",
    "p19": "Delegation diagram: one larger lead robot at left in amber connected by dashed lines to three smaller worker robots at right, each worker enclosed in its own faint rounded bubble, a small mailbox icon on each dashed line.",
    "p20": "Two-part illustration: upper half two robots exchanging structured envelope packets across a radio-wave line with a small rulebook icon between them; lower half a robot pulling an amber ticket card off a wall board full of tickets; thin-line style.",
    "p21": "Three parallel vertical lanes separated by thin walls, a small robot working at its own desk with a folder in each lane, and at the bottom a git branch symbol merging the three lanes into one amber trunk line, top strip empty for heading.",
    "p22": "Layered stack architecture: a wide amber foundation slab labeled 'LOOP' at the bottom, twelve thin translucent layers stacked above it in three grouped color bands with tiny icons on some layers, left column left empty for text.",
    "p23": "Dark terminal window mockup split into three panes, each pane with a colored prompt chevron and faint activity lines, one pane highlighted in amber, the window centered with margin space around it.",
    "p24": "Horizontal timeline of twelve small mechanism icons in muted gray across the upper middle, and beneath them one continuous unbroken amber loop line running the full width, emphasizing the unchanged constant, top area empty.",
    "p25": "Minimalist vehicle chassis side view with an open engine bay, four interchangeable engine chip modules floating above ready to slot in - one amber, three gray - and a small config file icon with sliders in a corner, bottom strip empty for caption.",
    "p26": "Winding road from bottom-left to top-right with three amber milestone flags at waypoints, a small video play icon, a document icon and a terminal icon beside different waypoints, a faint dotted shortcut path cutting across, right third empty.",
    "p27": "Balanced closing illustration: a glowing amber brain on the left and a thin-line vehicle wireframe on the right joined by a plus sign at center, symmetric composition, lower third empty for a closing statement.",
    "p28": "Minimal closing slide: a small thin-line shield with a copyright symbol at lower center, a faint amber loop watermark in one corner, almost entirely empty dark space for legal text overlay.",
}


def main():
    PROMPTS_DIR.mkdir(exist_ok=True)
    OUT_DIR.mkdir(exist_ok=True)
    failed = []
    for name, body in PROMPTS.items():
        prompt = STYLE + body
        (PROMPTS_DIR / f"{name}.md").write_text(
            f"# {name} 生圖提示詞\n\n```\n{prompt}\n```\n", encoding="utf-8"
        )
        if list(OUT_DIR.glob(f"{name}_*.png")):
            print(f"[skip] {name} already generated")
            continue
        print(f"[gen ] {name} ...", flush=True)
        r = subprocess.run(
            [sys.executable, str(DRAW), prompt,
             "--size", "1536x1024", "--quality", "low",
             "--name", name, "--outdir", str(OUT_DIR)],
            capture_output=True, text=True)
        if r.returncode != 0 or not list(OUT_DIR.glob(f"{name}_*.png")):
            print(f"[FAIL] {name}: {r.stderr.strip()[-300:]}")
            failed.append(name)
    print(f"\nDone. {28 - len(failed)}/28 ok. Failed: {failed or 'none'}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
