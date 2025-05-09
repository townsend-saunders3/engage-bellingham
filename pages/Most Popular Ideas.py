import streamlit as st
import json
import pandas as pd
import os

st.title("💬 Common Ideas from the Community")

st.markdown("""
This page shows groups of **similar ideas** shared by people in our community.
We used AI to read all the suggestions and group the ones that talk about the same thing.
Each group is like a collection of ideas that sound alike.
""")

# --- Load clustered suggestions ---
data_path = os.path.join("engage_bellingham_suggestion_clusters.json")
with open(data_path, "r") as f:
    clusters = json.load(f)

cluster_ids = sorted(clusters.keys(), key=lambda cid: len(clusters[cid]), reverse=True)

# --- Sidebar filter ---
st.sidebar.title("Show Groups With At Least...")
min_size = st.sidebar.slider("How many similar ideas should be in each group?", 1, 10, 2)
filtered_clusters = [cid for cid in cluster_ids if len(clusters[cid]) >= min_size]

# --- Display clusters ---
st.markdown(f"### 👥 Showing {len(filtered_clusters)} groups with at least {min_size} similar ideas")

for cid in filtered_clusters:
    first_idea = clusters[cid][0]['suggestion']
    with st.expander(f"{first_idea} ({len(clusters[cid])} similar ideas)"):
        for item in clusters[cid]:
            st.markdown(f"- {item['suggestion']}")

# --- Footer ---
st.markdown("---")
st.caption("Grouped using AI to find ideas that are alike.")