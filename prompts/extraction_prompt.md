# Extraction Prompt

Use this prompt when feeding source material (textbook pages, paper sections, lecture notes) to Claude or GPT for knowledge extraction.

---

## How to Use

1. Copy the prompt below.
2. Paste it into a new Claude or GPT conversation.
3. Attach or paste the source material after the prompt.
4. Review the output and save to `library/` with an appropriate filename.

---

## The Prompt

```
You are a research-grade knowledge extractor building an engineering/science reference library.

I will provide source material from a textbook or technical document. Your job:

1. IDENTIFY every distinct concept, equation, theorem, method, or important definition in this material.

2. For EACH concept found, produce a complete note using the template below.

3. Follow these rules strictly:
   - Every equation must include variable definitions with SI units
   - Every equation must pass a dimensional consistency check
   - State physical intuition (WHY, not just WHAT)
   - List ALL assumptions and what breaks when each is violated
   - The "Validity and Limitations" section is mandatory and must be substantive
   - Include source page/section references for every claim
   - If you are uncertain about anything, mark it with "⚠️ UNCERTAIN:" and explain
   - If constructing an example not from the source, label it "[Constructed example]"
   - Use $...$ for inline LaTeX, $$...$$ for display LaTeX (GitHub-compatible)
   - Set status to "draft" and confidence to your honest assessment (high/medium/low)

4. If a concept requires prerequisite knowledge, note it in the prerequisites field using [[kebab-case-filename]] links.

5. Output each note as a separate markdown block, clearly separated, ready to save as individual .md files. Suggest a filename for each.

SOURCE MATERIAL:
[Paste or attach your content here]

METADATA:
- Book: [Title, Author, Edition]
- Chapter/Section: [e.g., Chapter 3, Section 3.4]
- Pages: [e.g., 112-125]
```

---

## Variant: Single-Topic Deep Dive

Use this when you want one detailed note on a specific topic rather than scanning for all concepts:

```
You are a research-grade knowledge extractor building an engineering/science reference library.

I need a comprehensive reference note on: [TOPIC NAME]

Source material is attached. Produce a single, thorough note using the template below.

Pay special attention to:
- Physical intuition (WHY does this take this form?)
- All assumptions and their consequences when violated
- At least one worked example with full reasoning
- Common mistakes practitioners make
- Limiting behavior and dimensional checks
- When this method/equation FAILS and what to use instead

Source: [Book, Edition, Chapter, Pages]

[Paste or attach your content here]
```

---

## Variant: Cross-Reference Check

Use this after generating several notes, to verify consistency across them:

```
I have generated the following library notes. Please check for:

1. Notation conflicts (same symbol used for different things across notes)
2. Broken prerequisite chains (Note A references Note B, but B doesn't exist yet)
3. Contradictory assumptions between related notes
4. Missing "Related Topics" links that should exist
5. Any claim that appears in multiple notes with different details

List all issues found. For each, suggest a fix.

[Paste your notes here]
```
