# Interview Tasks

This repository collects small technical exercises produced for an interview process.

## Context

The hiring company is a large multinational technology group focused on the energy
sector. Its work spans power generation, grid technology and transmission,
industrial energy systems, and services that support the shift toward
lower-carbon energy. In that setting, internal assistants that answer engineering
and operations questions must ground every answer in trusted source documents,
which is what the task below checks.

## `citation-grounding-check.py` — a simple RAG grounding check

A minimal groundedness reviewer for a retrieval-augmented QA assistant. Given a
spreadsheet with source documents and a transcript of question / answer / citation
rows, it decides whether each answer is actually supported by the document it
cites.

### How it works

1. **Load sources.** The `Sources` sheet is parsed into a dictionary of documents
   keyed by `DOC-*` identifiers.
2. **Read the transcript.** Columns (`Question`, `PlantAssist Answer`, `Citation`,
   `Your Verdict`, `Why?`) are located by header name.
3. **Check the citation.** If a row has no `DOC-\d+` citation, or cites a document
   that is not in the knowledge base, it is marked `BLOCK`.
4. **Score groundedness.** The answer is split into sentences with NLTK. Each
   sentence is embedded with a sentence-transformer model (`BAAI/bge-base-en-v1.5`)
   and compared to the cited document by cosine similarity.
5. **Assign a verdict:**
   - `TRUST` — mean similarity ≥ `0.82` and no sentence below `0.70`.
   - `FIX` — mean similarity ≥ `0.70`.
   - `BLOCK` — otherwise (unsupported or contradictory claims).
6. **Write results.** Verdict and reason (with the similarity score) are written
   back and saved to `QA_Assessment_Reviewed.xlsx`.

### Requirements

```
pip install sentence-transformers scikit-learn openpyxl nltk
```

### Usage

Place `QA_Assessment.xlsx` (with `Sources` and `Transcript` sheets) next to the
script and run:

```
python citation-grounding-check.py
```

### Notes and limitations

- Embedding similarity is a proxy for entailment; it can miss negation and
  contradiction. A natural-language-inference model would be a stronger check.
- Thresholds (`TRUST_THRESHOLD`, `FIX_THRESHOLD`) are hand-tuned and should be
  calibrated against a labelled sample.
- The whole cited document is embedded as one chunk; long documents would benefit
  from passage-level retrieval before scoring.
