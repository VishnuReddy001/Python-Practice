import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

print("Program Started...")

# Read Excel
df = pd.read_excel("may_month_tickets.xlsx")

print(f"Total Tickets: {len(df)}")

# Create comparison text
df["comparison_text"] = (
    df["Application Name"].fillna("").astype(str) + " " +
    df["Module Name"].fillna("").astype(str) + " " +
    df["Sub Module"].fillna("").astype(str) + " " +
    df["Ticket Discription"].fillna("").astype(str)
)

# Generate TF-IDF vectors
vectorizer = TfidfVectorizer(stop_words="english")
vectors = vectorizer.fit_transform(df["comparison_text"])

print("TF-IDF vectors generated successfully")
print("Shape:", vectors.shape)

# Generate similarity matrix
print("Calculating similarity matrix...")
similarity_matrix = cosine_similarity(vectors)

print("Finding similar tickets...")

results = []

for i in range(len(df)):
    for j in range(i + 1, len(df)):

        similarity = similarity_matrix[i][j]

        # Similarity threshold
        if similarity >= 0.50:

            results.append({
                "Ticket1": df.iloc[i]["Ticket Number"],
                "Ticket2": df.iloc[j]["Ticket Number"],
                "Similarity": round(float(similarity), 2)*100,
                "Description1": str(df.iloc[i]["Ticket Discription"]),
                "Description2": str(df.iloc[j]["Ticket Discription"])
            })

# Create output dataframe
result_df = pd.DataFrame(results)

# Save to Excel
result_df.to_excel("Similar_Tickets1.xlsx", index=False)

print(f"Similar pairs found: {len(result_df)}")
print("Output saved as Similar_Tickets1.xlsx")
