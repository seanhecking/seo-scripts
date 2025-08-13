import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load your CSV file (adjust the path as needed)
##### REPLACE CSV FILE #####
file_path = 'my-csv-file.csv'
df = pd.read_csv(file_path)

# Rename columns for clarity
df.columns = ['staging_url', 'public_url']

# Drop rows with missing values
df_clean = df.dropna(subset=['staging_url', 'public_url'])

# Function to extract keywords from a URL
def extract_keywords(url):
    tokens = re.split(r'[/:._\-?=&]+', url)
    return ' '.join([t.lower() for t in tokens if len(t) > 2 and not t.isdigit()])

# Apply keyword extraction
df_clean['staging_keywords'] = df_clean['staging_url'].apply(extract_keywords)
df_clean['public_keywords'] = df_clean['public_url'].apply(extract_keywords)

# Vectorize and compute similarity
vectorizer = TfidfVectorizer().fit(df_clean['staging_keywords'].tolist() + df_clean['public_keywords'].tolist())
staging_vectors = vectorizer.transform(df_clean['staging_keywords'])
public_vectors = vectorizer.transform(df_clean['public_keywords'])

similarity_matrix = cosine_similarity(staging_vectors, public_vectors)
best_matches = similarity_matrix.argmax(axis=1)

# Create results DataFrame
matched_df = pd.DataFrame({
    'staging_url': df_clean['staging_url'].values,
    'matched_public_url': df_clean['public_url'].iloc[best_matches].values,
    'similarity_score': similarity_matrix.max(axis=1)
})

# Save results to CSV
matched_df.to_csv('matched_urls_with_similarity.csv', index=False)
print("✅ Matched file saved as: matched_urls_with_similarity.csv")