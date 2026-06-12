import urllib.request, json, re, os

TOKEN    = os.environ["PROFILE_TOKEN"]
USERNAME = "Janith2002"
HDRS     = {"Authorization": f"token {TOKEN}", "User-Agent": "profile-updater", "Accept": "application/vnd.github.v3+json"}

def api(url):
    req = urllib.request.Request(url, headers=HDRS)
    with urllib.request.urlopen(req) as r:
        return json.load(r)

repos  = api("https://api.github.com/user/repos?per_page=100&type=all&sort=updated")
total  = len(repos)
public = [r for r in repos if not r["private"] and not r["fork"]]
print(f"Total: {total} | Public: {len(public)}")

with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()

# Update badge count
content = re.sub(r"Total%20Repos-\d+-", f"Total%20Repos-{total}-", content)

# Build latest repos table (top 6 public, sorted by last updated)
rows = ""
for r in sorted(public, key=lambda x: x["updated_at"], reverse=True)[:6]:
    desc = (r["description"] or "No description").replace("|", "-")[:55]
    lang = r["language"] or "Code"
    rows += f"| [{r['name']}]({r['html_url']}) | {desc} | {lang} |\n"

block = f"""<!-- AUTO-REPOS:START -->
| Repository | Description | Language |
|:-----------|:-----------|:---------|
{rows.rstrip()}
<!-- AUTO-REPOS:END -->"""

if "<!-- AUTO-REPOS:START -->" in content:
    content = re.sub(r"<!-- AUTO-REPOS:START -->.*?<!-- AUTO-REPOS:END -->", block, content, flags=re.DOTALL)
else:
    # Insert before Connect section
    content = content.replace(
        '<img src="https://img.shields.io/badge/-Connect',
        block + '\n\n---\n\n<img src="https://img.shields.io/badge/-Connect'
    )

with open("README.md", "w", encoding="utf-8") as f:
    f.write(content)

print("README updated.")
