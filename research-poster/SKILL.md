---
name: research-poster
description: Plan, write and build conference research posters (IAGLR, SWCS, AGU, CWRA, ASA-CSSA-SSSA, CGU, symposia and lab days) as an editable PowerPoint file plus PDF, from a manuscript, thesis chapter or results, including turning a paper into a poster, choosing sections and the one-sentence takeaway, sizing type and figures for A0 or 48 x 36 in, and checking layout, image resolution and claims before printing. Use whenever the user mentions a poster, poster session, poster board or e-poster, or asks to revise or critique one, even if they only want the text or the section plan.
---

# Research posters

A poster is read in under a minute from two metres away, then in detail by the few
people who stop. It works when one takeaway is visible from a distance, three to five
sections carry the argument, and every number matches the manuscript. Write the content
first; layout comes after the text is agreed.

## Workflow

1. **Collect inputs**: the manuscript or results (the authority for every fact), figures
   in their highest-resolution or vector form, logos, and the venue's requirements (size,
   orientation, poster ID, template, printing deadline). Ask for the size if it is not
   given; do not assume it.
2. **Write the takeaway and plan** before any layout: the one-sentence conclusion, then
   three to five sections with their message, figure and approximate length. Use
   [references/poster-guide.md](references/poster-guide.md). Show the plan and draft text
   to the user and wait for agreement; text is the expensive part to redo.
3. **Draft the text** in the author's voice (the bodrud-doza-scholarly-voice skill for new
   prose; grammar and clarity only when editing the author's own text). Real sentences, not
   keyword fragments. State what is measured, modelled, scenario-based or future work, and
   keep each claim inside its evidence.
4. **Build the PowerPoint** with `scripts/build_poster.py spec.json --out poster.pptx --render`
   (copy `assets/example_spec.json`). It sets the slide size, a column grid, header and
   conclusion bands and scaled type, and reports estimated column fill, overflow and
   low-resolution images. For a venue template, open the template with python-pptx and
   place content in its frames instead of building from scratch.
5. **Look at the render** (PNG preview, then the PDF at 100 % in several places): reading
   order, balance between columns, clipped or overflowing text, legibility of figure
   labels at print size. Rebalance by moving or trimming whole sections and rebuild. The
   first layout is never the final one.
6. **Final checks** with the checklist in the guide; list anything unresolved for the user
   (missing logos, figures below 150 dpi at print size, claims to confirm, venue rules not yet known).

## Defaults

- Sizes: A0 portrait 33.11 x 46.81 in; A0 landscape 46.81 x 33.11 in; 48 x 36 in and
  36 x 48 in for North American venues. PowerPoint slides cannot exceed 56 in: build larger
  posters at half scale and print at 200 %.
- Type at A0: title about 96 pt, section headings about 54 pt, body 32 pt (never under
  24 pt), captions 26 pt, conclusion headline about 64 pt; the script scales these for
  other sizes. One sans-serif family; left-aligned body text.
- Figures from the research-figures-maps skill, redrawn at poster scale (larger fonts,
  thicker lines) rather than pasted from the paper at journal size.
- Deliverables: `poster.pptx` (editable), `poster.pdf` exported from PowerPoint for
  printing, a PNG preview, and the list of open items.

## Python conventions

Python first: python-pptx for building, LibreOffice or PowerPoint for PDF export, PyMuPDF
for previews. Keep the spec JSON beside the PowerPoint file so the poster can be rebuilt
after edits.
