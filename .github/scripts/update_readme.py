import urllib.request, json, re, os, base64

TOKEN    = os.environ["PROFILE_TOKEN"]
USERNAME = "Janith2002"
HDRS     = {"Authorization": f"token {TOKEN}", "User-Agent": "profile-updater",
            "Accept": "application/vnd.github.v3+json"}

def api(url):
    req = urllib.request.Request(url, headers=HDRS)
    with urllib.request.urlopen(req) as r:
        return json.load(r)

def get_file(repo, path, branch="main"):
    url = f"https://api.github.com/repos/{USERNAME}/{repo}/contents/{path}?ref={branch}"
    req = urllib.request.Request(url, headers=HDRS)
    try:
        with urllib.request.urlopen(req) as r:
            return base64.b64decode(json.load(r)["content"]).decode(errors="replace")
    except:
        return ""

def replace_marker(content, marker, new_content):
    pattern = rf"<!-- {marker}:START -->.*?<!-- {marker}:END -->"
    replacement = f"<!-- {marker}:START -->\n{new_content}\n<!-- {marker}:END -->"
    return re.sub(pattern, replacement, content, flags=re.DOTALL)

# ── Mappings ──────────────────────────────────────────────────────────────────

LANG_ICONS = {
    "PHP":"php","C#":"cs","Python":"py","TypeScript":"ts","JavaScript":"js",
    "HTML":"html","CSS":"css","Rust":"rust","Go":"go","Java":"java",
    "Kotlin":"kotlin","Swift":"swift","Ruby":"ruby","Dart":"dart","Lua":"lua",
    "Shell":None,"Dockerfile":"docker","SCSS":"sass","Vue":"vuejs","Svelte":"svelte"
}

FRAMEWORK_ICONS = {
    "nextjs":["next"],"react":["react","react-dom"],"tailwind":["tailwindcss"],
    "bootstrap":["bootstrap"],"express":["express"],"vuejs":["vue"],
    "flask":["flask"],"fastapi":["fastapi"],"django":["django"],
    "opencv":["opencv-python","opencv-python-headless","cv2"],
    "dotnet":["Microsoft.AspNetCore","aspnetcore"],
    "laravel":["laravel/framework"],"symfony":["symfony/framework"],
    "pytorch":["torch"],"tensorflow":["tensorflow","tf"],
    "nuxtjs":["nuxt"],"astro":["astro"],"svelte":["svelte"],
}

DB_ICONS = {
    "mysql":["mysql","mysqli","pymysql","mysql-connector-python","mysql2"],
    "sqlite":["sqlite3","aiosqlite"],
    "firebase":["firebase","firebase-admin","pyrebase"],
    "mssql":["Microsoft.Data.SqlClient","System.Data.SqlClient","pyodbc","mssql"],
    "postgres":["psycopg2","pg","postgres","asyncpg"],
    "mongodb":["mongoose","mongodb","pymongo"],
    "redis":["redis","ioredis","aioredis"],
    "planetscale":["planetscale"],
    "supabase":["supabase","@supabase/supabase-js"],
    "cassandra":["cassandra-driver"],
}

TOOL_ICONS = {
    "docker":["docker","docker-compose","Dockerfile"],
    "kubernetes":["kubernetes","k8s"],
    "githubactions":[".github/workflows"],
    "postman":["postman"],
    "jest":["jest","@jest/core"],
    "vitest":["vitest"],
    "webpack":["webpack"],
    "vite":["vite"],
    "babel":["@babel/core","babel-core"],
    "eslint":["eslint"],
    "prettier":["prettier"],
    "graphql":["graphql","apollo","@apollo"],
    "nginx":["nginx"],
}

DEPLOY_ICONS = {
    "netlify":["netlify","@netlify"],
    "vercel":["vercel","@vercel"],
    "firebase":["firebase"],
    "render":["render.yaml","render"],
    "heroku":["Procfile","heroku"],
    "aws":["aws-sdk","boto3","@aws-sdk"],
    "azure":["azure","@azure"],
    "gcp":["google-cloud","@google-cloud"],
    "cloudflare":["cloudflare","wrangler"],
    "railway":["railway"],
}

API_BADGES = {
    "telegram":   ("telegram",  "skillicon"),
    "Groq_AI":    ("F55036",    "groq"),
    "YouTube_API":("FF0000",    "youtube"),
    "Pexels_API": ("05A081",    "pexels"),
    "WhatsApp_API":("25D366",   "whatsapp"),
    "OpenAI":     ("412991",    "openai"),
    "Stripe":     ("635BFF",    "stripe"),
    "Twilio":     ("F22F46",    "twilio"),
}

# Category rules for auto-classifying new repos
def classify_repo(repo, languages):
    name = repo["name"].lower()
    desc = (repo["description"] or "").lower()
    topics = repo.get("topics", [])
    langs  = [l.lower() for l in languages.keys()]

    ai_keywords   = ["ai","ml","vision","opencv","face","recognition","model","neural","predict","bot","telegram","automation"]
    auto_keywords = ["bot","automation","scraper","pipeline","youtube","scheduler","cron","workflow","n8n","discord"]

    if any(k in name or k in desc for k in auto_keywords) or "telegram" in langs or "bot" in topics:
        return "automation"
    if any(k in name or k in desc for k in ai_keywords) or "opencv" in langs:
        return "ai"
    return "web"

# ── Fetch repos ───────────────────────────────────────────────────────────────
print("Fetching repos...")
repos  = api(f"https://api.github.com/user/repos?per_page=100&type=all&sort=updated")
total  = len(repos)
public = [r for r in repos if not r["private"] and not r["fork"]]
print(f"Total: {total} | Public non-fork: {len(public)}")

# ── Aggregate languages ───────────────────────────────────────────────────────
print("Fetching languages...")
all_langs = {}
for repo in public:
    try:
        langs = api(f"https://api.github.com/repos/{USERNAME}/{repo['name']}/languages")
        for lang, bytes_ in langs.items():
            all_langs[lang] = all_langs.get(lang, 0) + bytes_
    except:
        pass

lang_icons = []
for lang, _ in sorted(all_langs.items(), key=lambda x: -x[1]):
    icon = LANG_ICONS.get(lang)
    if icon and icon not in lang_icons:
        lang_icons.append(icon)

print(f"Languages detected: {lang_icons}")

# ── Detect frameworks, DBs, tools from repo files ────────────────────────────
print("Detecting tech stack...")
found_frameworks = set(["nextjs","dotnet","bootstrap","tailwind","flask","fastapi","opencv"])
found_dbs        = set(["mysql","sqlite","firebase","mssql"])
found_tools      = set(["git","github","githubactions","docker","vscode","figma","xd"])
found_deploy     = set(["netlify","vercel","firebase","render"])
found_apis       = set(["telegram","Groq_AI","YouTube_API","Pexels_API","WhatsApp_API"])

for repo in public:
    rname = repo["name"]
    pkg   = get_file(rname, "package.json")
    req   = get_file(rname, "requirements.txt")
    csproj_content = ""
    # Try to find .csproj
    try:
        tree_url = f"https://api.github.com/repos/{USERNAME}/{rname}/git/trees/main?recursive=1"
        tree_req = urllib.request.Request(tree_url, headers=HDRS)
        with urllib.request.urlopen(tree_req) as r:
            tree = json.load(r)
            for item in tree.get("tree", []):
                if item["path"].endswith(".csproj"):
                    csproj_content = get_file(rname, item["path"])
                    break
    except:
        pass

    combined = (pkg + req + csproj_content).lower()

    for icon, keywords in FRAMEWORK_ICONS.items():
        if any(kw.lower() in combined for kw in keywords):
            found_frameworks.add(icon)

    for icon, keywords in DB_ICONS.items():
        if any(kw.lower() in combined for kw in keywords):
            found_dbs.add(icon)

    for icon, keywords in TOOL_ICONS.items():
        if any(kw.lower() in combined for kw in keywords):
            found_tools.add(icon)

    for icon, keywords in DEPLOY_ICONS.items():
        if any(kw.lower() in combined for kw in keywords):
            found_deploy.add(icon)

    # API detection
    all_text = combined
    if "openai" in all_text:     found_apis.add("OpenAI")
    if "stripe" in all_text:     found_apis.add("Stripe")
    if "twilio" in all_text:     found_apis.add("Twilio")

print(f"Frameworks: {found_frameworks}")
print(f"Databases:  {found_dbs}")
print(f"Tools:      {found_tools}")
print(f"Deploy:     {found_deploy}")
print(f"APIs:       {found_apis}")

# ── Build skillicon / badge HTML ──────────────────────────────────────────────
ORDERED_FW   = ["nextjs","dotnet","bootstrap","tailwind","flask","fastapi","django","opencv","react","vuejs","astro","svelte","laravel","pytorch","tensorflow"]
ORDERED_DB   = ["mysql","sqlite","firebase","mssql","postgres","mongodb","redis","supabase","planetscale"]
ORDERED_TOOL = ["git","github","githubactions","docker","vscode","figma","xd","jest","vitest","webpack","vite","nginx","postman"]
ORDERED_DEP  = ["netlify","vercel","firebase","render","heroku","aws","azure","gcp","cloudflare","railway"]

def skillicons_img(icons, ordered=None):
    if ordered:
        icons = [i for i in ordered if i in icons] + [i for i in icons if i not in ordered]
    return f'<img src="https://skillicons.dev/icons?i={",".join(icons)}&theme=dark"/>'

def badge(label, color, logo):
    return f'<img src="https://img.shields.io/badge/{label}-{color}?style=for-the-badge&logo={logo}&logoColor=white"/>'

lang_html      = skillicons_img(lang_icons)
framework_html = skillicons_img(found_frameworks, ORDERED_FW)
db_html        = skillicons_img(found_dbs, ORDERED_DB)

tool_skillicons = [t for t in ORDERED_TOOL if t in found_tools]
tool_html = skillicons_img(tool_skillicons)
if "docker" in found_tools or "docker" not in tool_skillicons:
    pass  # already included
tool_html += '\n&nbsp;<img src="https://img.shields.io/badge/FFmpeg-007808?style=for-the-badge&logo=ffmpeg&logoColor=white"/>'
tool_html += '\n&nbsp;<img src="https://img.shields.io/badge/n8n-EA4B71?style=for-the-badge&logo=n8n&logoColor=white"/>'

deploy_skillicons = [d for d in ORDERED_DEP if d in found_deploy]
deploy_html = skillicons_img(deploy_skillicons)
deploy_html += '\n&nbsp;<img src="https://img.shields.io/badge/Caddy-00ADD8?style=for-the-badge&logo=caddy&logoColor=white"/>'

api_parts = []
for api_key in found_apis:
    info = API_BADGES.get(api_key)
    if not info: continue
    color, logo = info
    if color == "skillicon":
        api_parts.append(f'<img src="https://skillicons.dev/icons?i={logo}&theme=dark"/>')
    else:
        label = api_key.replace("_", "_")
        api_parts.append(f'<img src="https://img.shields.io/badge/{label}-{color}?style=for-the-badge&logo={logo}&logoColor=white"/>')
api_html = "\n&nbsp;".join(api_parts)

# ── Existing project names (to avoid duplicates) ─────────────────────────────
EXISTING_PROJECTS = [
    "AI-Powered-Smart-School-Attendance-System","isdn_sales_system","Unimanage",
    "qrave-restaurant","Shopora-POS-project-plan","CVora","Xera-Studio",
    "HJ_Stores_IMS_Pro","AniVerse","smartspendamerica","sherov-edits-bot",
    "Sherov-Flux","Janith2002","privacy-policy","n8n-docker-caddy","my-portfolio",
    "Python-FTP-Client","worldmonitor","janith-portfolio","sherov"
]

live_badge = "![Live](https://img.shields.io/badge/Live-00C851?style=flat-square)"

new_ai_rows, new_web_rows, new_auto_rows = [], [], []

for repo in public:
    if repo["name"] in EXISTING_PROJECTS:
        continue
    try:
        langs = api(f"https://api.github.com/repos/{USERNAME}/{repo['name']}/languages")
    except:
        langs = {}

    desc  = (repo["description"] or "No description").replace("|", "-")[:60]
    lang  = repo.get("language") or "Code"
    url   = repo["html_url"]
    name  = repo["name"]
    row   = f"| [{name}]({url}) | {desc} | {lang} | {live_badge} |"
    cat   = classify_repo(repo, langs)
    if cat == "ai":     new_ai_rows.append(row)
    elif cat == "auto": new_auto_rows.append(row)
    else:               new_web_rows.append(row)

# ── Read and update README ────────────────────────────────────────────────────
with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()

# Update total repos badge
content = re.sub(r"Total%20Repos-\d+-", f"Total%20Repos-{total}-", content)

# Update tech stack sections
content = replace_marker(content, "LANGS",      lang_html)
content = replace_marker(content, "FRAMEWORKS", framework_html)
content = replace_marker(content, "DATABASES",  db_html)
content = replace_marker(content, "TOOLS",      tool_html)
content = replace_marker(content, "DEPLOY",     deploy_html)
content = replace_marker(content, "APIS",       api_html)

# Append new projects if any
def append_to_marker(content, marker, new_rows):
    if not new_rows: return content
    pattern = rf"(<!-- {marker}:START -->)(.*?)(<!-- {marker}:END -->)"
    def replacer(m):
        return m.group(1) + m.group(2).rstrip() + "\n" + "\n".join(new_rows) + "\n" + m.group(3)
    return re.sub(pattern, replacer, content, flags=re.DOTALL)

content = append_to_marker(content, "PROJECTS-AI",   new_ai_rows)
content = append_to_marker(content, "PROJECTS-WEB",  new_web_rows)
content = append_to_marker(content, "PROJECTS-AUTO", new_auto_rows)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(content)

print("README fully updated!")
print(f"New AI projects:         {len(new_ai_rows)}")
print(f"New Web projects:        {len(new_web_rows)}")
print(f"New Automation projects: {len(new_auto_rows)}")
