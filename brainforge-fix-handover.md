# BrainForge fix handover

Base file: the offline `brainforge.html` on `cursor/brainforge-app-58c5`. Claude’s copy was the same length as that file and was not used as the base. The brief wins wherever it disagrees with an earlier chat instruction.

## Where the brief overruled an earlier instruction

- Word hints are no longer Pete’s shared Tier 2 groups (massive, monolithic, immense, and the rest, including “utilize”). Section 2 replaces them with one list per word. “hard”, “clear” and “poor” are not flagged.
- Pasting into a writing box no longer clears the box, and the message is no longer “No cheating!…”. The typed text stays, and the message is “Pasting is switched off here. Type it in your own words and it will stick in your memory.”
- The fixed activity paragraph is gone. The report builds three sentences from the piece. The old evidence JSON, including `bureaucraticStatement`, is gone. The download follows the Wattlewood evidence file spec and is a separate button.
- “utilize” is now “utilise”, as the brief’s spelling sweep requires.

Kept, because the brief did not change them: one offline file, no remote URL, Years 3–6 ages 8–12, subject English, paste still works in the research box and the three fact boxes, Saved only after the stored text matches, no “Save evidence again” button, and the date box still shows “Write the date”.

## What changed

1. Grammar. Removed the mid-sentence capital rule. Removed `may`, `march`, and the `act` territory rule. Abbreviations (`e.g.`, `i.e.`, `etc.`, `approx.`, `Mr.`, `Mrs.`, `Ms.`, `Dr.`, `St.`, `no.`) are not sentence ends, and `i.e.` is not the word I. A paragraph that ends with a quote or bracket after the stop is complete. The ending badge waits until the field loses focus. Badge wording matches the brief, and each badge sits under the line it refers to. The example names the word that was found.
2. Vocabulary. One suggestion list per word, at most three badges, and no badge for a proper-noun phrase or a capital that is not the first word of a sentence. Child-facing text says “everyday word”, not “Tier 1”.
3. Paste. The field is not cleared. Drag-and-drop and `insertFromDrop` are cancelled. Fact boxes max out at 80 characters. Older saved facts longer than 80 are not thrown away on load.
4. Pieces. Each student has `pieces` and `activePieceId`. An old save becomes one piece with the same text. My writing, Start a new piece, Remove this piece, and Show the research again are in the page. A second student with the same first name is refused. If the last piece is removed, an empty piece is added so the student still has somewhere to write.
5. Report. Create evidence report stays disabled until there are three facts, a main title, and a paragraph, and the hint says what is missing. The statement is built from the work. Facts are listed above the work sample. The checklist starts unticked every time it opens. The ruler line says “headings”. The print button says “Print report”.
6. Evidence file. Export evidence file builds a `wattlewood-evidence` 1.0 file, checks it, then downloads `Name_brainforge_from_to_date.wwevidence.json`. The object URL is released after a short delay. `entryId` is `brainforge:` plus the piece id and does not change between exports. `appVersion` is `1.1` because section 6 requires that field, even though section 0 says not to put versions in the exported file.
7. Layout warnings. Two honest messages for a subheader above the title and for more than one main title. The margin warning is gone. The red margin line is still drawn.
8. Look. The hidden theme icon is actually hidden. Dark mode field borders and the subheader button use a light brass edge. The tab icon is the Wattlewood PNG data URI. The SVG icon was not copied, because its data URI contains `http://www.w3.org/2000/svg` and this file must not contain a remote URL. Font stacks start with Fraunces and Source Sans 3 and keep the old fallbacks. No font file is loaded. Headings and labels use the brief’s plain names.



## Acceptance tests

All 46 browser checks passed, including every grammar, vocabulary, paste, piece, report, and export case in section 9. No network request was made. A search of the file found none of: Official, bureaucratic, Tier 1, cheating, utilize, fulfill, analyzed, organize.

QA command, with no `--allow-online`:

`python3 /cursor/stores/bc-f55c7061-2e96-40c1-b876-17650ca4faf5/docs/standards/qa_module.py /workspace/brainforge.html`

Exit code: 0. Passed: 10. Failed: 0. The checker’s “verbatim activity statement” line did not run, because that paragraph is no longer in the file. The other checks passed.

## Unsure

- Removing the last piece replaces it with a blank piece. The brief does not say what an empty list should look like.
- The month “March” is no longer flagged, because `march` had to come off the proper-noun list.

