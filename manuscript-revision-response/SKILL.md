---
name: manuscript-revision-response
description: Run a journal revision round end to end in Word — turn the decision letter and reviewer reports into a numbered revision plan, triage each comment (revise, clarify, respectfully disagree, out of scope), work the items one at a time with before-and-after text, keep the manuscript, supplementary material and tracked and clean copies in step, and build the point-by-point response-to-reviewers letter (.docx) with page and line locations. Use whenever the user has received reviewer comments, a major or minor revision decision, or a resubmission request, or asks to answer reviewers or write a rebuttal or response letter, even for a single comment.
---

# Manuscript revision and response letter

A revision has two deliverables that must agree: the revised manuscript and the response
letter that quotes it. The letter is finished last, from the finished manuscript, but it
is built item by item as the work lands so nothing is forgotten.

## Standing rules

1. **The author's text is edited for grammar and clarity only**, with every change shown
   (Original | Revised | Reason). New prose follows the bodrud-doza-scholarly-voice skill.
2. **Propose before changing the manuscript.** Quote the current passage, propose the
   replacement, and wait for approval. Apply approved changes with Track Changes on (the
   docx skill's tracked-change workflow, or give the author the text to paste).
3. **Verify every number against its source** (model output, data file, the analysis
   script), not against another place in the manuscript.
4. **Every change lands in every copy**: manuscript, supplementary material, tracked and
   clean versions, and any anonymised copy.
5. **One item at a time**: finish, record in the plan, then start the next.
6. **No invented citations.** A reference added in response to a reviewer is checked
   (DOI resolves to the cited work) before it goes into the manuscript or letter.

## Workflow

1. **Collect** the decision letter and reports, the submitted manuscript (.docx), the
   supplementary material, the journal's instructions for revisions (response format,
   tracked changes or highlighting, line numbering), and the deadline.
2. **Build the plan**: `python scripts/parse_comments.py reviews.txt --out plan.json`.
   Check the split against the original; add editor requests that sit in the letter body.
   With the author, give each item a category (revise / clarify / disagree with evidence /
   out of scope with reason) and effort, and link items that raise the same issue so they
   get one consistent answer. Show the plan before starting work.
3. **Decide on requested analyses early.** New calibration runs, extra stations or
   scenarios take the longest; agree which are done, partly done, or declined with a reason.
4. **Work the items** in an order that avoids rework (structure and analyses first, wording
   last). For each: quote current text → propose change → apply on approval → write the
   response and changes into `plan.json` → mark status `done`.
5. **Write responses** following [references/responding.md](references/responding.md):
   answer in the first sentence, say what changed and where, quote the revised text,
   disagree with evidence and courtesy.
6. **Fix locations last.** When the manuscript is final, update page and line numbers in
   the plan from the final tracked version, then build the letter:
   `python scripts/build_response_letter.py plan.json --out response_letter.docx`.
   It marks unanswered items `[RESPONSE PENDING]` in red and exits with an error until
   every item has a response.
7. **Close out**: re-read the manuscript as a whole (consistency of terms, numbers,
   figure and table numbering, references cited and listed), write the cover letter to the
   editor summarising the main changes, and list anything the author must still confirm.

For a strategic assessment of a hard round (whether to push back, how reviewers might
read a response), the academic-paper skill's revision-coach and rebuttal-audit modes can
complement this workflow.
