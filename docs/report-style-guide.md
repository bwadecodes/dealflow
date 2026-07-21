# Report Style Guide

Every prose deliverable produced by a dealflow skill — assessments, memos,
summaries, question lists, and review reports — must be ready for investment
committee (IC) review: written so that a senior investment professional with no
prior exposure to the deal, the data room, or the analysis behind the report can
follow every sentence on first reading.

These rules apply to Markdown and HTML report bodies. They are supplemented,
and where the two conflict overridden, by the firm's writing preferences in
`~/.claude/dealflow/firm-style.yaml`.

## Language

1. **Use plain phrases rather than coined labels.** Do not invent analyst
   jargon. Write "establish which entities are included in the deal," not
   "define the entity perimeter." Write "revenue swings sharply year to year,"
   not "revenue sawtooths." Terms established in industry usage (EBITDA, QoE,
   LOI, IC) are acceptable; terms a professional reader might not immediately
   understand are not.
2. **Define every abbreviation at first use.** If a report shortens entity or
   product names, provide a one-line list of definitions at the beginning of
   the report. The reader should never have to infer the meaning of an
   undefined term.
3. **Avoid idiomatic, promotional, or overconfident language.** Replace
   colloquial phrasing with the substantive point: not "retention is the whole
   ballgame," but "none of the identified synergies can be delivered without
   retaining key personnel."
4. **Maintain one consistent voice.** Findings are stated in analytical
   prose, supported by evidence, using the perspective set in the firm's
   profile (`voice.perspective` in `firm-style.yaml`; first-person plural
   when no profile exists). Do not mix in drafting instructions addressed
   to the author ("request it," "do not cite this"); action items belong in
   the recommendations or open-items sections, where imperative phrasing is
   the convention.

## Structure and formatting

5. **Prefer bulleted lists to dense paragraphs.** A paragraph in which several
   sentences carry bolded lead-ins should be reformatted as a bulleted list,
   with the bolded phrase leading each item. Limit each paragraph to one idea
   and generally no more than four sentences.
6. **Make each section self-contained.** A reader should be able to understand
   any section without having read the others. Restate the subject rather than
   relying on cross-references such as "concern 2 above."
7. **Reserve tables for enumerable facts.** Comparisons, inventories, and
   metrics belong in tables; anything requiring judgment or explanation belongs
   in complete sentences. Table cells must not contain fragments that omit the
   context required for interpretation.
8. **Attribute every quantitative claim.** Each figure carries its source —
   document, tab, page, or row — in parentheses or a footnote. Do not present
   numbers without attribution.

## Language patterns to remove

9. **Filler intensifiers.** Delete words such as "genuinely," "truly,"
   "crucially," "importantly," and "notably," or replace them with the specific
   evidence that supports the emphasis.
10. **Formulaic phrases.** Remove "it is important to note," "in conclusion,"
    "overall," introductory sentences that add no information, and parallel
    constructions repeated across sections.
11. **Decorative typography.** Do not use emoji other than the established flag
    indicators (🟢🟡🔴). Do not use arrow chains in place of complete
    sentences; arrows are acceptable only within a labeled data series, such as
    a year-over-year revenue progression. Bold no more than one phrase per
    bullet.
12. **Repetitive qualification.** State the report's confidence level once, in
    the executive summary. Individual findings state what the evidence shows;
    where a conclusion rests on professional judgment rather than calculation,
    label it as such explicitly instead of qualifying every sentence with
    "may," "could," or "appears."

## Final review before saving

Before saving any report, re-read the executive summary and one additional
section against these rules. Rewrite any sentence that cannot be understood
without knowledge of the process that produced the report.
