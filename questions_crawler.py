import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin

BASE_URL = "https://engagebellingham.org"
PROJECTS_PAGE = f"{BASE_URL}/projects"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_project_links():
    resp = requests.get(PROJECTS_PAGE, headers=HEADERS)
    soup = BeautifulSoup(resp.text, 'html.parser')
    project_links = set()
    for a in soup.select("a[href^='/']"):
        href = a.get("href")
        if href and not any(ex in href for ex in ["/login", "/register", "/faq", "/about", "#", "mailto:", "tel:"]):
            full_url = urljoin(BASE_URL, href.split('?')[0])
            project_links.add(full_url)
    return sorted(project_links)

def extract_guestbook_comments(tool_url, project_title):
    comments = []
    try:
        resp = requests.get(tool_url, headers=HEADERS)
        soup = BeautifulSoup(resp.text, "html.parser")
        for wrapper in soup.select("div.comment-wrapper"):
            content_tag = wrapper.select_one("div.comment > p.content")
            author_tag = wrapper.select_one("span.author > span")
            timestamp_tag = wrapper.select_one("span.timestamp")
            if content_tag and author_tag:
                comments.append({
                    "type": "comment",
                    "project_title": project_title,
                    "author": author_tag.text.strip(),
                    "timestamp": timestamp_tag.text.strip() if timestamp_tag else None,
                    "content": content_tag.text.strip(),
                    "source_url": tool_url
                })
    except Exception as e:
        print(f"[ERROR] Failed to extract guestbook from {tool_url}: {e}")
    return comments

def extract_qanda_questions(tool_url, project_title):
    questions = []
    try:
        resp = requests.get(tool_url, headers=HEADERS)
        soup = BeautifulSoup(resp.text, "html.parser")

        for li in soup.select("li.shared-content-block"):
            question_tag = li.select_one("div.question h3.q")
            author_tag = li.select_one("div.meta span.author")
            timestamp_tag = li.select_one("div.meta span.timestamp")

            if question_tag and author_tag:
                author = author_tag.text.replace("asked", "").strip()
                questions.append({
                    "type": "question",
                    "project_title": project_title,
                    "author": author,
                    "timestamp": timestamp_tag.text.strip() if timestamp_tag else None,
                    "content": question_tag.text.strip(),
                    "source_url": tool_url
                })
    except Exception as e:
        print(f"[ERROR] Failed to parse HTML Q&A for {tool_url}: {e}")

    return questions

def main():
    all_comments = []
    all_questions = []

    project_links = get_project_links()
    print(f"Found {len(project_links)} projects.")

    for idx, project_url in enumerate(project_links, 1):
        print(f"({idx}/{len(project_links)}) Processing project: {project_url}")
        try:
            resp = requests.get(project_url, headers=HEADERS)
            soup = BeautifulSoup(resp.text, "html.parser")
            project_title_tag = soup.select_one("h1")
            project_title = project_title_tag.text.strip() if project_title_tag else "Unknown"

            for a in soup.select("#tool_tab a"):
                href = a.get("href")
                if not href:
                    continue
                full_url = urljoin(BASE_URL, href)
                if 'guest_book' in href:
                    print(f"  → Extracting guestbook from {full_url}")
                    all_comments.extend(extract_guestbook_comments(full_url, project_title))
                elif 'qanda' in href:
                    print(f"  → Extracting Q&A from {full_url}")
                    all_questions.extend(extract_qanda_questions(full_url, project_title))
            time.sleep(0.5)  # Avoid hammering the site
        except Exception as e:
            print(f"[ERROR] Failed to process project page: {project_url} — {e}")

    # Save results
    with open("engage_bellingham_guestbook_comments2.json", "w") as f:
        json.dump(all_comments, f, indent=2)
    print(f"\n✅ Saved {len(all_comments)} comments.")

    with open("engage_bellingham_questions2.json", "w") as f:
        json.dump(all_questions, f, indent=2)
    print(f"✅ Saved {len(all_questions)} questions.")

if __name__ == "__main__":
    main()
