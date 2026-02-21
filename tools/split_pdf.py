"""Split a textbook PDF into per-chapter files using a YAML config."""

import argparse
import re
import sys
from pathlib import Path

import yaml
from pypdf import PdfReader, PdfWriter


def load_config(config_path):
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_config(cfg):
    for key in ("source_pdf", "output_dir", "chapters"):
        if key not in cfg:
            sys.exit(f"ERROR: config missing required key: '{key}'")

    for ch in cfg["chapters"]:
        missing = [k for k in ("num", "title", "pages") if k not in ch]
        if missing:
            sys.exit(f"ERROR: chapter entry missing {missing}: {ch}")
        if len(ch["pages"]) != 2:
            sys.exit(f"ERROR: chapter {ch['num']}: 'pages' must be [first, last]")
        if ch["pages"][0] > ch["pages"][1]:
            sys.exit(f"ERROR: chapter {ch['num']}: start page ({ch['pages'][0]}) > end page ({ch['pages'][1]})")


def slugify(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def chapter_filename(num, title):
    return f"ch{num:02d}-{slugify(title)}.pdf"


def generate_config(pdf_path):
    """Read PDF bookmarks/outline and generate a YAML config."""
    reader = PdfReader(str(pdf_path))
    total_pages = len(reader.pages)
    outline = reader.outline

    if not outline:
        sys.exit(
            f"ERROR: no bookmarks found in {pdf_path.name}.\n"
            "This PDF has no table of contents embedded. "
            "You'll need to create the config manually from configs/example-book.yaml."
        )

    # Flatten nested outline — extract top-level chapter entries
    entries = []
    for item in outline:
        # Skip nested lists (sub-sections) — we only want top-level
        if isinstance(item, list):
            continue
        try:
            page_num = reader.get_destination_page_number(item) + 1  # 0-indexed -> 1-indexed
            entries.append({"title": item.title.strip(), "start_page": page_num})
        except Exception:
            continue

    if not entries:
        sys.exit(f"ERROR: could not extract any chapter entries from {pdf_path.name}")

    # Compute end pages: each chapter ends where the next one starts
    chapters = []
    for i, entry in enumerate(entries):
        end_page = entries[i + 1]["start_page"] - 1 if i + 1 < len(entries) else total_pages
        chapters.append({
            "num": i + 1,
            "title": entry["title"],
            "pages": [entry["start_page"], end_page],
        })

    config = {
        "source_pdf": f"sources/{pdf_path.name}",
        "output_dir": f"chapters/{slugify(pdf_path.stem)}",
        "prepend_pages": [],
        "chapters": chapters,
    }

    # Dump with nice formatting
    output = yaml.dump(config, default_flow_style=False, sort_keys=False, allow_unicode=True)
    # Fix pages lists to flow style: [1, 20] instead of multi-line
    output = re.sub(
        r"pages:\n\s+- (\d+)\n\s+- (\d+)",
        r"pages: [\1, \2]",
        output,
    )
    return output


def split_book(config, project_root, dry_run=False, only_chapters=None):
    source_path = project_root / config["source_pdf"]
    output_dir = project_root / config["output_dir"]

    if not source_path.exists():
        sys.exit(f"ERROR: source PDF not found: {source_path}")

    reader = PdfReader(str(source_path))
    total_pages = len(reader.pages)
    prepend = config.get("prepend_pages", [])

    book_title = config.get("title", source_path.stem)
    print(f"Book:   {book_title}")
    print(f"Source: {source_path.name}  ({total_pages} pages)")
    print(f"Output: {output_dir}")
    if prepend:
        print(f"Prepend pages: {prepend}")
    print()

    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    written = []
    for ch in config["chapters"]:
        if only_chapters and ch["num"] not in only_chapters:
            continue

        first, last = ch["pages"]
        chapter_pages = list(range(first, last + 1))
        all_pages = prepend + chapter_pages

        # Bounds check
        bad = [p for p in all_pages if p < 1 or p > total_pages]
        if bad:
            print(f"  WARNING ch{ch['num']:02d}: pages {bad} out of range (PDF has {total_pages} pages) — skipping")
            continue

        fname = chapter_filename(ch["num"], ch["title"])

        if dry_run:
            prepend_note = f" (+{len(prepend)} prepend)" if prepend else ""
            print(f"  [DRY RUN] {fname}  — PDF pages {first}–{last}{prepend_note}, {len(all_pages)} pages total")
        else:
            writer = PdfWriter()
            for pnum in all_pages:
                writer.add_page(reader.pages[pnum - 1])
            fpath = output_dir / fname
            with open(fpath, "wb") as f:
                writer.write(f)
            print(f"  wrote {fname}  ({len(all_pages)} pages)")
            written.append(str(fpath))

    print(f"\nDone. {len(written)} files written." if not dry_run else "\nDry run complete.")
    return written


def main():
    parser = argparse.ArgumentParser(
        description="Split a textbook PDF into chapter files using a YAML config."
    )
    parser.add_argument("config", help="Path to the book's YAML config file (or PDF when using --generate-config)")
    parser.add_argument("--generate-config", action="store_true",
                        help="Read PDF bookmarks and print a YAML config to stdout")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview what would be written without creating files")
    parser.add_argument("--chapters", nargs="+", type=int, metavar="N",
                        help="Only split these chapter numbers (e.g. --chapters 3 5)")
    parser.add_argument("--output-dir", metavar="PATH",
                        help="Override the output directory from the config")
    args = parser.parse_args()

    input_path = Path(args.config).resolve()
    if not input_path.exists():
        sys.exit(f"ERROR: file not found: {input_path}")

    # Generate config mode: read PDF bookmarks, print YAML, done
    if args.generate_config:
        print(generate_config(input_path))
        return

    # Resolve project root from script location (tools/ -> project root)
    project_root = Path(__file__).resolve().parent.parent

    config = load_config(input_path)
    validate_config(config)

    if args.output_dir:
        config["output_dir"] = args.output_dir

    split_book(config, project_root, dry_run=args.dry_run, only_chapters=args.chapters)


if __name__ == "__main__":
    main()
