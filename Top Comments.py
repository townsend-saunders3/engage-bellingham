import streamlit as st
import json
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
from collections import Counter
import re
import matplotlib.pyplot as plt

# --- Load Ranked Data ---
with open("engage_bellingham_rnn_ranked.json", "r") as f:
    data = json.load(f)

with open("engage_bellingham_narrative_tree.json", "r") as f:
    tree = json.load(f)

with open("engage_bellingham_final_narrative.md", "r") as f:
    final_narrative = f.read()

# --- Prepare DataFrame ---
df = pd.DataFrame(data)
df["type"] = df["meta"].apply(lambda x: x.get("type", ""))
df["author"] = df["meta"].apply(lambda x: x.get("author", ""))
df["project"] = df["meta"].apply(lambda x: x.get("project_title", ""))

# --- Sidebar Filters ---
st.sidebar.title("Filter the Comments")
type_filter = st.sidebar.multiselect("What kind of message is it?", df["type"].unique(), default=df["type"].unique())
all_projects = sorted(df["project"].dropna().unique())
select_all_projects = st.sidebar.checkbox("Show All Projects", value=True)

if select_all_projects:
    project_filter = st.sidebar.multiselect("Pick a Project", all_projects, default=all_projects)
else:
    project_filter = st.sidebar.multiselect("Pick a Project", all_projects)

filtered_df = df[df["type"].isin(type_filter) & df["project"].isin(project_filter)]

# --- Normalize score using theoretical max ---
N = len(df)
max_possible_score = (N - 1) ** 2
min_possible_score = (N - 1) * 1
score_range = max_possible_score - min_possible_score
df["clipped_score"] = df["score"].clip(lower=min_possible_score, upper=max_possible_score)
df["normalized_score"] = ((df["clipped_score"] - min_possible_score) / score_range * 100).round().astype(int)

# --- Title and Description ---
st.title("🗣️ What is Bellingham Saying?")

st.markdown("""
This dashboard uses AI to identify **shared public sentiment** across all feedback submitted to Engage Bellingham.

Instead of surfacing the loudest or most recent voices, we highlight the most **representative ideas** — the comments that best reflect what many others also said.

### 💡 What the score means:
- A score of **100%** means lots of people shared this same thought.
- Lower scores mean the idea was more unique.

You can also explore a short story that explains what the whole community said overall.
""")

# --- Word Cloud ---
st.markdown("### ☁️ Most Common Words")
top_text = " ".join(df.sort_values("normalized_score", ascending=False).head(50)["text"])
custom_stopwords = set(STOPWORDS)
custom_stopwords.update(["city", "need", "bellingham", "project", "like", "think", "please", "make", "would", "use", "area", "people", "one", "will", "going"])
wordcloud = WordCloud(width=800, height=300, background_color='white', stopwords=custom_stopwords).generate(top_text)
plt.figure(figsize=(10, 4))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
st.pyplot(plt)

# --- Bigram Cloud ---
st.markdown("### 🔗 Common Two-Word Phrases")
words = [re.sub(r"[^\w\s]", "", w.lower()) for w in top_text.split() if len(w) > 2]
words = [w for w in words if w not in custom_stopwords]
bigrams = zip(words, words[1:])
bigram_phrases = [" ".join(pair) for pair in bigrams]
bigram_counts = Counter(bigram_phrases)
bigram_cloud = WordCloud(width=800, height=300, background_color='white').generate_from_frequencies(bigram_counts)
plt.figure(figsize=(10, 4))
plt.imshow(bigram_cloud, interpolation='bilinear')
plt.axis("off")
st.pyplot(plt)

# --- Leaderboard ---
st.markdown("### 🏅 Ideas Lots of People Shared")
ranked_df = df.loc[filtered_df.index].sort_values("normalized_score", ascending=False).reset_index(drop=True)

for idx, row in ranked_df.iterrows():
    with st.expander(f"#{idx + 1} — {row['type'].capitalize()} by {row['author']} (Score: {row['normalized_score']}%)"):
        st.markdown(f"**Project:** {row['project']}")
        st.markdown(f"**What they said:**\n\n{row['text']}")
        st.markdown(f"**See more:** [Original comment]({row['meta']['source_url']})")

# --- Narrative Explorer ---
st.markdown("---")
st.markdown(final_narrative)

# --- Footer ---
st.markdown("---")
st.caption("Made with AI to help everyone understand what our community is saying.")
