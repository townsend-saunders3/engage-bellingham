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
    for a in soup.select("a[href*='/']"):
        href = a.get("href")
        if href and href.startswith("/") and not any(ex in href for ex in ["register", "login", "faq", "about"]):
            full_url = urljoin(BASE_URL, href.split('?')[0])
            project_links.add(full_url)
    return list(project_links)

def extract_guestbook_comments(tool_url, project_title):
    comments = []
    resp = requests.get(tool_url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, 'html.parser')
    for wrapper in soup.select("div.comment-wrapper"):
        comment_div = wrapper.select_one("div.comment p.content")
        author_span = wrapper.select_one(".comment-info .author span")
        timestamp_span = wrapper.select_one(".comment-info .timestamp")

        if comment_div:
            comments.append({
                "type": "comment",
                "content": comment_div.get_text(strip=True),
                "author": author_span.get_text(strip=True) if author_span else None,
                "date": timestamp_span.get_text(strip=True) if timestamp_span else None,
                "project_title": project_title,
                "tool_url": tool_url
            })
    return comments

def get_project_title(project_html):
    soup = BeautifulSoup(project_html, 'html.parser')
    h1 = soup.find("h1")
    return h1.get_text(strip=True) if h1 else "Untitled"

def main():
    all_comments = []
    projects = get_project_links()
    print(f"Found {len(projects)} project links")

    for project_url in projects:
        try:
            project_resp = requests.get(project_url, headers=HEADERS)
            project_html = project_resp.text
            project_title = get_project_title(project_html)
            print(f"Processing project: {project_title}")

            # Extract tool tabs
            soup = BeautifulSoup(project_html, 'html.parser')
            for tab in soup.select("#tool_tab a[href]"):
                tool_href = tab.get("href")
                if "guest_book" in tool_href:
                    full_tool_url = urljoin(BASE_URL, tool_href)
                    comments = extract_guestbook_comments(full_tool_url, project_title)
                    all_comments.extend(comments)
                    print(f"  Found {len(comments)} guestbook comments")
                time.sleep(1)
        except Exception as e:
            print(f"Error processing {project_url}: {e}")
            continue

    with open("bellingham_community_comments.json", "w") as f:
        json.dump(all_comments, f, indent=2)
    print(f"Saved {len(all_comments)} comments to bellingham_community_comments.json")

if __name__ == "__main__":
    main()