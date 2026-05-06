---
name: latex-table-to-word
description: Convert Excel/CSV tables into Word (.docx) tables while turning inline LaTeX formulas like `$V = \sum Q_i \times P_i$` into real Word formula objects (OMML), not images. Also rebuild existing Word documents whose formulas were broken into many short lines/fragments, then convert formula-like segments into equation objects. Use when the user has spreadsheet-like tabular data with mixed Chinese/English text and LaTeX math, wants a Word table output, or wants an existing .docx cleaned up so formulas become proper editable objects.
---

# Latex Table To Word

Convert CSV/Excel-like tables to `.docx` with mixed plain text + LaTeX formulas preserved as Word equation objects, and repair existing `.docx` files where formulas were split into many short paragraphs.

## Workflows

### 1) CSV or Excel-like table → Word table with formula objects

1. Identify the source file path.
   - Prefer `.csv` for direct conversion.
   - If the user says “Excel” but provides CSV-like content, treat it as CSV unless a real `.xlsx` is present.
2. Run `scripts/csv_latex_to_word.py`.
3. Save the output `.docx` where the user asked.
4. Tell the user the exact output path.

Command:

```powershell
python .\skills\latex-table-to-word\scripts\csv_latex_to_word.py --input <csv-path> --output <docx-path>
```

Example:

```powershell
python .\skills\latex-table-to-word\scripts\csv_latex_to_word.py --input "J:\Desktop\table-1775988874328.csv" --output "J:\Desktop\table-1775988874328_latex公式对象版.docx"
```

### 2) Existing Word document with broken formula fragments → rebuilt Word document

Use this when the input is already a `.docx`, but the formula content is broken into many short lines/paragraphs such as `V`, `wr`, `P`, `i`, blank lines, etc.

1. Run `scripts/docx_mixed_formula_rebuild.py`.
2. Let it regroup fragmented paragraphs into logical lines.
3. Let it convert detected formula-like fragments to Word equation objects.
4. Save as a new `.docx` rather than overwriting the original.

Command:

```powershell
python .\skills\latex-table-to-word\scripts\docx_mixed_formula_rebuild.py --input <input-docx> --output <output-docx>
```

Example:

```powershell
python .\skills\latex-table-to-word\scripts\docx_mixed_formula_rebuild.py --input "J:\Desktop\TEST.docx" --output "J:\Desktop\TEST_重做公式对象版.docx"
```

## What the scripts do

### `csv_latex_to_word.py`

- Reads CSV with encoding fallback: `utf-8-sig`, `utf-8`, `gb18030`, `gbk`
- Splits mixed cell content into plain text segments and `$...$` LaTeX segments
- Converts LaTeX to MathML, then MathML to OMML using `assets/MML2OMML.XSL`
- Writes a Word table with:
  - plain text kept as normal text
  - formulas inserted as real Word equation objects

### `docx_mixed_formula_rebuild.py`

- Reads an existing `.docx`
- Merges fragmented formula paragraphs into logical lines
- Normalizes broken patterns like `V` + `wr` → `V_wr`, `P` + `i` → `P_i`
- Keeps Chinese text as normal text
- Converts formula-like segments into OMML equation objects
- Writes a rebuilt `.docx`

## Notes

- Prefer the OMML route over COM `OMaths.BuildUp()` guessing when the user wants LaTeX handled correctly.
- For CSV/table conversion, formulas should ideally be wrapped in `$...$`.
- For broken `.docx` repair, save to a new file first.
- If WPS display is questioned, inspect whether the generated `.docx` contains OMML nodes before assuming conversion failed.

## Files in this skill

- `scripts/csv_latex_to_word.py` — CSV/table converter
- `scripts/docx_mixed_formula_rebuild.py` — existing DOCX repair + formula-object rebuild
- `assets/MML2OMML.XSL` — MathML to OMML transform used by both scripts
