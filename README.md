# 🏙️ Engage Bellingham: Civic Sentiment Analysis

This project analyzes public feedback from the City of Bellingham’s civic engagement platform, [Engage Bellingham](https://engagebellingham.org). It scrapes, processes, and visually presents community sentiment to highlight the most representative comments and common themes.

## 🌟 Features

* **Web Scraping:** Automatically collects guestbook comments, Q\&A submissions, and related documents from city forums.
* **Semantic Analysis:** Uses embeddings and clustering to rank and group public comments based on shared themes.
* **Interactive Dashboard:** A Streamlit-powered web app presenting top comments, thematic visualizations, and narrative summaries.

## 📂 Project Structure

```
.
├── .devcontainer/                                 # Dev container configurations
├── pages/
│   └── Top Comments.py                            # Main Streamlit frontend
├── .gitignore
├── Top Comments.py                                # Entry point for Streamlit app
├── comment_crawler.py                             # Extracts guestbook comments
├── questions_crawler.py                           # Extracts Q&A interactions
├── file_crawler.py                                # Crawls and downloads linked files (optional)
├── upload_files.ipynb                             # Notebook for data upload/manipulation
├── upload_files.py                                # Python script for data handling/upload
├── reverse_nn.ipynb                               # Performs embedding and semantic ranking
├── requirements.txt                               # Python dependencies
├── engage_bellingham_*.json                       # Various JSON files storing raw and processed data
├── engage_bellingham_final_narrative.md           # AI-generated community summary
├── raw_suggestions.json                           # Raw scraped suggestions
├── reverse_nn_all_suggestions.txt                 # Text output from embedding processes
└── README.md                                      # Project description (this file)
```

## 🚀 Quick Start

### 1. Setup Environment

Install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Scrape Data

Collect guestbook and Q\&A comments:

```bash
python comment_crawler.py
python questions_crawler.py
```

(Optional) Download files linked on the city site:

```bash
python file_crawler.py
```

### 3. Analyze and Rank Data

Use `reverse_nn.ipynb` to:

* Generate embeddings
* Cluster and rank comments by thematic similarity
* Output structured JSON files (`engage_bellingham_rnn_ranked.json`, etc.)

### 4. Launch Dashboard

Run the Streamlit application:

```bash
streamlit run "Top Comments.py"
```

## 📊 Dashboard Highlights

* **Representative Comments:** Clearly ranked comments reflecting widely shared sentiments.
* **Word and Phrase Clouds:** Visualize common words and bigrams across feedback.
* **Narrative Summary:** AI-generated overview of community sentiments.

## 🧠 How It Works

This project uses semantic embedding techniques and clustering (DBSCAN, reverse nearest neighbor ranking) to group and highlight common themes. This methodology ensures representative comments rise to the forefront, promoting balanced civic insight.

