# Interview Tasks

Small, self-contained technical exercises produced for an interview process.

## Context

The hiring company is a large multinational technology group focused on the
energy sector. Its work spans power generation, grid technology and transmission,
industrial energy systems, and services that support the shift toward
lower-carbon energy. The tasks here reflect problems that come up in that
setting — in particular, making internal AI assistants reliable enough to use for
engineering and operations questions.

## Layout

Each task lives in its own folder with its own README, dependencies, and data.

| Folder | What it does |
| --- | --- |
| [`RAG-citation-grounding-check/`](RAG-citation-grounding-check/) | Groundedness reviewer for a retrieval-augmented QA assistant: checks whether each answer is actually supported by the document it cites and assigns a TRUST / FIX / BLOCK verdict. |

## Adding a task

1. Create a new top-level folder with a short, descriptive name.
2. Add a `README.md` inside it covering purpose, how it works, requirements, and
   how to run it.
3. Keep dependencies local to the folder (or note them in that README).
4. Add a row to the table above.
