"""
Groundedness Review for PlantAssist QA Assessment

Requirements:
pip install sentence-transformers scikit-learn openpyxl nltk

"""

import re
import nltk
import numpy as np

from openpyxl import load_workbook
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download("punkt")

# ----------------------------------------------------
# Configuration
# ----------------------------------------------------

WORKBOOK = "QA_Assessment.xlsx"

MODEL_NAME = "BAAI/bge-base-en-v1.5"

TRUST_THRESHOLD = 0.82
FIX_THRESHOLD = 0.70

# ----------------------------------------------------
# Load embedding model
# ----------------------------------------------------

print("Loading embedding model...")

model = SentenceTransformer(MODEL_NAME)

# ----------------------------------------------------
# Load workbook
# ----------------------------------------------------

wb = load_workbook(WORKBOOK)

sources_ws = wb["Sources"]
transcript_ws = wb["Transcript"]

# ----------------------------------------------------
# Read source documents
# ----------------------------------------------------

documents = {}

current_doc = None
buffer = []

for row in sources_ws.iter_rows(values_only=True):

    value = row[0]

    if isinstance(value, str) and value.startswith("DOC-"):

        if current_doc is not None:
            documents[current_doc] = "\n".join(buffer)

        current_doc = value.strip()
        buffer = []

    else:

        if value:
            buffer.append(str(value))

if current_doc:
    documents[current_doc] = "\n".join(buffer)

print(f"Loaded {len(documents)} documents")

# ----------------------------------------------------
# Find transcript columns automatically
# ----------------------------------------------------

headers = [cell.value for cell in transcript_ws[1]]

question_col = headers.index("Question") + 1
answer_col = headers.index("PlantAssist Answer") + 1
citation_col = headers.index("Citation") + 1
verdict_col = headers.index("Your Verdict") + 1
reason_col = headers.index("Why?") + 1

# ----------------------------------------------------
# Groundedness Function
# ----------------------------------------------------


def groundedness(answer, context):

    context_embedding = model.encode(
        [context],
        normalize_embeddings=True
    )

    unsupported = []
    scores = []

    sentences = sent_tokenize(answer)

    for sentence in sentences:

        emb = model.encode(
            [sentence],
            normalize_embeddings=True
        )

        similarity = cosine_similarity(
            emb,
            context_embedding
        )[0][0]

        scores.append(similarity)

        if similarity < FIX_THRESHOLD:
            unsupported.append(sentence)

    average = float(np.mean(scores))

    if average >= TRUST_THRESHOLD and len(unsupported) == 0:

        verdict = "TRUST"

    elif average >= FIX_THRESHOLD:

        verdict = "FIX"

    else:

        verdict = "BLOCK"

    if verdict == "TRUST":

        reason = "All claims are supported by the cited document."

    elif verdict == "FIX":

        reason = "Some claims appear weakly supported by the cited document."

    else:

        reason = "Answer contains unsupported or contradictory claims."

    return verdict, reason, average


# ----------------------------------------------------
# Review Transcript
# ----------------------------------------------------

for row in range(2, transcript_ws.max_row + 1):

    answer = transcript_ws.cell(row, answer_col).value
    citation = transcript_ws.cell(row, citation_col).value

    if answer is None or citation is None:
        continue

    citation_match = re.search(r"DOC-\d+", str(citation))

    if citation_match is None:

        transcript_ws.cell(row, verdict_col).value = "BLOCK"
        transcript_ws.cell(row, reason_col).value = "No valid citation found."
        continue

    doc = citation_match.group()

    if doc not in documents:

        transcript_ws.cell(row, verdict_col).value = "BLOCK"
        transcript_ws.cell(row, reason_col).value = (
            f"{doc} does not exist in the knowledge base."
        )
        continue

    verdict, reason, score = groundedness(
        answer,
        documents[doc]
    )

    transcript_ws.cell(row, verdict_col).value = verdict

    transcript_ws.cell(
        row,
        reason_col
    ).value = f"{reason} (similarity={score:.2f})"

# ----------------------------------------------------
# Save
# ----------------------------------------------------

OUTPUT = "QA_Assessment_Reviewed.xlsx"

wb.save(OUTPUT)

print(f"Saved to {OUTPUT}")