import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# ─────────────────────────────────────────
# Settings
# ─────────────────────────────────────────

EXCEL_FILE           = "may_month_tickets.xlsx"
OUTPUT_FILE          = "Similar_Tickets.xlsx"
SIMILARITY_THRESHOLD = 0.50

COL_TICKET_NUMBER = "Ticket Number"
COL_APP_NAME      = "Application Name"
COL_MODULE        = "Module Name"
COL_SUBMODULE     = "Sub Module"
COL_DESCRIPTION   = "Ticket Discription"

# ─────────────────────────────────────────
# IT Support keyword groups
# Tickets sharing same GROUP get boosted
# ─────────────────────────────────────────

KEYWORD_GROUPS = {
    "login"      : r"login|log.?in|sign.?in|password|credential|authenticate|otp|2fa",
    "timeout"    : r"timeout|time.?out|slow|hang|loading|not respond|freeze|stuck",
    "payment"    : r"payment|checkout|purchase|transaction|billing|invoice|refund",
    "error"      : r"error|exception|crash|fail|failure|500|404|not working|broken",
    "access"     : r"access|permission|role|rights|privilege|unauthorized|forbidden",
    "missing"    : r"missing|not found|not display|disappear|blank|empty|not show",
    "report"     : r"report|dashboard|export|download|excel|pdf|chart|graph",
    "data"       : r"data|record|entry|field|form|save|submit|update|delete",
    "email"      : r"email|mail|notification|alert|sms|message|inbox",
    "server"     : r"database|db|connection|server|api|network|service|down",
}

# ─────────────────────────────────────────
# Step 1: Read Excel
# ─────────────────────────────────────────

print("\n========================================")
print("   Recurring Ticket Finder (Free/Smart)")
print("========================================\n")

print(f"Reading: {EXCEL_FILE}")
df = pd.read_excel(EXCEL_FILE)
print(f"Total tickets: {len(df)}\n")

# ─────────────────────────────────────────
# Step 2: Clean + enrich text
# ─────────────────────────────────────────

def clean(text):
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def enrich(row):
    base = clean(
        str(row[COL_APP_NAME])   + " " +
        str(row[COL_MODULE])     + " " +
        str(row[COL_SUBMODULE])  + " " +
        str(row[COL_DESCRIPTION])
    )
    # Boost keywords by repeating them — gives more weight in TF-IDF
    boosts = []
    for group_name, pattern in KEYWORD_GROUPS.items():
        if re.search(pattern, base):
            boosts.append(f"{group_name} {group_name} {group_name}")
    return base + " " + " ".join(boosts)

print("Enriching ticket text with keyword groups...")
df["enriched"] = df.apply(enrich, axis=1)

# ─────────────────────────────────────────
# Step 3: TF-IDF vectors with bigrams
# ─────────────────────────────────────────

print("Building TF-IDF vectors (with 2-word phrases)...")
vectorizer = TfidfVectorizer(
    stop_words  = "english",
    ngram_range = (1, 2),     # captures "login error", "payment failed" etc.
    min_df      = 1,
    max_features= 8000,
    sublinear_tf= True        # reduces impact of very frequent words
)
vectors = vectorizer.fit_transform(df["enriched"])
print(f"Vector shape: {vectors.shape}\n")

# ─────────────────────────────────────────
# Step 4: Find similar pairs
# ─────────────────────────────────────────

print("Calculating similarities...")
sim_matrix = cosine_similarity(vectors)

results    = []
seen_pairs = set()

for i in range(len(df)):
    # Only look at top matches for each ticket (faster than full matrix scan)
    scores = sim_matrix[i]
    top_indices = np.argsort(scores)[::-1]  # sort descending

    for j in top_indices:
        if j <= i:
            continue   # skip self and already-seen pairs

        score = scores[j]
        if score < SIMILARITY_THRESHOLD:
            break      # since sorted, no point checking further

        pair_key = (i, j)
        if pair_key in seen_pairs:
            continue
        seen_pairs.add(pair_key)

        results.append({
            "Ticket 1 Number"     : df.iloc[i][COL_TICKET_NUMBER],
            "Ticket 2 Number"     : df.iloc[j][COL_TICKET_NUMBER],
            "Similarity Score"    : round(float(score), 2),
            "Similarity %"        : f"{round(float(score) * 100)}%",
            "Ticket 1 App"        : df.iloc[i][COL_APP_NAME],
            "Ticket 2 App"        : df.iloc[j][COL_APP_NAME],
            "Ticket 1 Description": str(df.iloc[i][COL_DESCRIPTION]),
            "Ticket 2 Description": str(df.iloc[j][COL_DESCRIPTION]),
        })

# ─────────────────────────────────────────
# Step 5: Save output
# ─────────────────────────────────────────

result_df = pd.DataFrame(results)
if not result_df.empty:
    result_df = result_df.sort_values("Similarity Score", ascending=False)

result_df.to_excel(OUTPUT_FILE, index=False)

print("\n========================================")
print(f"  Similar pairs found : {len(result_df)}")
print(f"  Threshold used      : {SIMILARITY_THRESHOLD} ({int(SIMILARITY_THRESHOLD*100)}%+)")
print(f"  Output saved to     : {OUTPUT_FILE}")
print("========================================\n")