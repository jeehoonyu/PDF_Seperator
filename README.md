# PDF Seperator

A command-line tool that splits large textbook PDFs into per-chapter files using PDF bookmarks or manual YAML configs.

## Features

- Auto-generate chapter configs from PDF bookmarks/outlines
- Manual YAML configs for PDFs without bookmarks
- Dry-run mode to preview before splitting
- Selective chapter splitting (e.g., only chapters 3 and 5)
- Prepend common pages (notation, symbols) to every chapter

## Setup

```bash
python -m pip install pypdf pyyaml
```

## Usage

```bash
# 1. Place your textbook PDF in sources/

# 2. Auto-generate a config from PDF bookmarks:
python tools/split_pdf.py --generate-config sources/my-textbook.pdf > configs/my-textbook.yaml
#    Review the generated config — fix titles, adjust page ranges as needed.

# 3. Preview what will be created:
python tools/split_pdf.py configs/my-textbook.yaml --dry-run

# 4. Split:
python tools/split_pdf.py configs/my-textbook.yaml

# 5. Split only specific chapters:
python tools/split_pdf.py configs/my-textbook.yaml --chapters 3 5
```

If your PDF has no bookmarks, copy `configs/example-book.yaml` and fill in page ranges manually.

All page numbers use **PDF-internal numbering** (1 = first page of the file), not the printed page number. Use `prepend_pages` to attach notation or symbol pages to every chapter.

Output goes to the `output_dir` specified in your config, with filenames like `ch01-introduction.pdf`.

## Example

Say you have `sources/fluid-mechanics-9th.pdf` with 800 pages. Create `configs/fluid-mechanics.yaml`:

```yaml
source_pdf: sources/fluid-mechanics-9th.pdf
output_dir: chapters/fluid-mechanics-9th
prepend_pages: [3, 4]   # notation & symbols pages prepended to every chapter

chapters:
  - num: 1
    title: "Introduction"
    pages: [15, 42]

  - num: 2
    title: "Fluid Statics"
    pages: [43, 96]

  - num: 3
    title: "Bernoulli Equation"
    pages: [97, 150]
```

Then run:

```bash
# Preview first:
python tools/split_pdf.py configs/fluid-mechanics.yaml --dry-run

# Output:
#   [DRY RUN] ch01-introduction.pdf         — PDF pages 15–42 (+2 prepend), 30 pages total
#   [DRY RUN] ch02-fluid-statics.pdf        — PDF pages 43–96 (+2 prepend), 56 pages total
#   [DRY RUN] ch03-bernoulli-equation.pdf   — PDF pages 97–150 (+2 prepend), 56 pages total

# Split for real:
python tools/split_pdf.py configs/fluid-mechanics.yaml
```

Result:

```
chapters/fluid-mechanics-9th/
├── ch01-introduction.pdf        (30 pages)
├── ch02-fluid-statics.pdf       (56 pages)
├── ch03-bernoulli-equation.pdf  (56 pages)
```

## Repository Structure

```
PDF_Seperator/
├── tools/            # split_pdf.py — the main splitter script
├── configs/          # per-book chapter split configs (YAML)
├── library/          # extracted knowledge notes
├── templates/        # note templates
├── prompts/          # prompt templates for LLM extraction
├── references/       # bibliography metadata
```

## License

Personal project. Not licensed for redistribution.
