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

def replace_inline(content, marker, new_html):
    """For tech stack markers that are INLINE inside <td> cells."""
    pattern = rf"<!-- {marker}:START -->.*?<!-- {marker}:END -->"
    replacement = f"<!-- {marker}:START -->{new_html}<!-- {marker}:END -->"
    return re.sub(pattern, replacement, content, flags=re.DOTALL)

def replace_block(content, marker, new_rows):
    """For project markers that WRAP full div+table blocks."""
    LIVE = "![Live](https://img.shields.io/badge/Live-00C851?style=flat-square)"
    if not new_rows:
        return content
    pattern = rf"<!-- {marker}:START -->.*?<!-- {marker}:END -->"
    # Find existing rows inside the marker
    match = re.search(pattern, content, flags=re.DOTALL)
    if not match:
        return content
    existing = match.group(0)
    # Extract existing table rows (lines starting with |)
    existing_rows = [l for l in existing.split('\n') if l.strip().startswith('|') and '---' not in l and 'Project' not in l]
    all_rows = existing_rows + new_rows
    rows_str = '\n'.join(all_rows)
    new_block = f"""<!-- {marker}:START -->
<div align="center">

| Project | Description | Stack | Status |
|:--------|:-----------|:------|:------:|
{rows_str}

</div>
<!-- {marker}:END -->"""
    return re.sub(pattern, new_block, content, flags=re.DOTALL)

# ── Mappings ──────────────────────────────────────────────────────────────────
LANG_ICONS = {
    "PHP":"php","C#":"cs","Python":"py","TypeScript":"ts","JavaScript":"js",
    "HTML":"html","CSS":"css","Rust":"rust","Go":"go","Java":"java",
    "Kotlin":"kotlin","Swift":"swift","Ruby":"ruby","Dart":"dart",
    "Shell":None,"Dockerfile":"docker","Vue":"vuejs","Svelte":"svelte"
}
FRAMEWORK_ICONS = {
    "nextjs":["next"],"react":["react","react-dom"],"tailwind":["tailwindcss"],
    "bootstrap":["bootstrap"],"express":["express"],"vuejs":["vue"],
    "flask":["flask"],"fastapi":["fastapi"],"django":["django"],
    "opencv":["opencv-python","cv2"],"dotnet":["Microsoft.AspNetCore"],
    "laravel":["laravel/framework"],"pytorch":["torch"],"tensorflow":["tensorflow"],
    "nuxtjs":["nuxt"],"astro":["astro"],
}
DB_ICONS = {
    "mysql":["mysql","mysqli","pymysql","mysql2"],"sqlite":["sqlite3"],
    "firebase":["firebase","firebase-admin"],"mssql":["Microsoft.Data.SqlClient","pyodbc"],
    "postgres":["psycopg2","pg","postgres"],"mongodb":["mongoose","pymongo"],
    "redis":["redis","ioredis"],"supabase":["supabase","@supabase/supabase-js"],
}
TOOL_ICONS = {
    "git":[],"github":[],"githubactions":[".github/workflows"],
    "docker":["docker","Dockerfile"],"vscode":[],"figma":[],"xd":[],
    "jest":["jest"],"vitest":["vitest"],"vite":["vite"],"nginx":["nginx"],
}
DEPLOY_ICONS = {
    "netlify":["netlify"],"vercel":["vercel"],"firebase":["firebase"],
    "render":["render.yaml"],"heroku":["Procfile"],
    "aws":["aws-sdk","boto3"],"azure":["azure","@azure"],
    "cloudflare":["cloudflare","wrangler"],
}
ORDERED_FW  = ["nextjs","dotnet","bootstrap","tailwind","flask","fastapi","django","opencv","react","vuejs","pytorch","tensorflow","laravel","astro","svelte"]
ORDERED_DB  = ["mysql","sqlite","firebase","mssql","postgres","mongodb","redis","supabase"]
ORDERED_TOOL= ["git","github","githubactions","docker","vscode","figma","xd","jest","vitest","vite","nginx"]
ORDERED_DEP = ["netlify","vercel","firebase","render","heroku","aws","azure","cloudflare"]

EXISTING = [
    "AI-Powered-Smart-School-Attendance-System","isdn_sales_system","Unimanage",
    "qrave-restaurant","Shopora-POS-project-plan","CVora","Xera-Studio","HJ_Stores_IMS_Pro",
    "AniVerse","smartspendamerica","sherov-edits-bot","Sherov-Flux","Janith2002",
    "privacy-policy","n8n-docker-caddy","my-portfolio","Python-FTP-Client",
    "worldmonitor","janith-portfolio","sherov"
]

def classify(repo, langs):
    n = repo["name"].lower(); d = (repo["description"] or "").lower()
    auto_kw = ["bot","automation","scraper","pipeline","youtube","scheduler","workflow","n8n","discord"]
    ai_kw   = ["ai","ml","vision","opencv","face","recognition","predict","neural"]
    if any(k in n or k in d for k in auto_kw): return "auto"
    if any(k in n or k in d for k in ai_kw):   return "ai"
    return "web"

# ── Main ──────────────────────────────────────────────────────────────────────
print("Fetching repos...")
repos  = api(f"https://api.github.com/user/repos?per_page=100&type=all&sort=updated")
total  = len(repos)
public = [r for r in repos if not r["private"] and not r["fork"]]

print("Fetching languages...")
all_langs = {}
for repo in public:
    try:
        for lang, b in api(f"https://api.github.com/repos/{USERNAME}/{repo['name']}/languages").items():
            all_langs[lang] = all_langs.get(lang, 0) + b
    except: pass

lang_icons = []
for lang, _ in sorted(all_langs.items(), key=lambda x: -x[1]):
    icon = LANG_ICONS.get(lang)
    if icon and icon not in lang_icons:
        lang_icons.append(icon)

print("Detecting frameworks...")
found_fw   = set(["nextjs","dotnet","bootstrap","tailwind","flask","fastapi","opencv"])
found_db   = set(["mysql","sqlite","firebase","mssql"])
found_tool = set(["git","github","githubactions","docker","vscode","figma","xd"])
found_dep  = set(["netlify","vercel","firebase","render"])
found_apis = set(["telegram","Groq_AI","YouTube_API","Pexels_API","WhatsApp_API"])

for repo in public:
    rname = repo["name"]
    text  = (get_file(rname,"package.json") + get_file(rname,"requirements.txt")).lower()
    try:
        tree = api(f"https://api.github.com/repos/{USERNAME}/{rname}/git/trees/main?recursive=1")
        for item in tree.get("tree",[]):
            if item["path"].endswith(".csproj"):
                text += get_file(rname, item["path"]).lower()
                break
    except: pass
    for icon, kws in FRAMEWORK_ICONS.items():
        if any(k.lower() in text for k in kws): found_fw.add(icon)
    for icon, kws in DB_ICONS.items():
        if any(k.lower() in text for k in kws): found_db.add(icon)
    for icon, kws in TOOL_ICONS.items():
        if any(k.lower() in text for k in kws) or icon in ["git","github","vscode","figma","xd"]: found_tool.add(icon)
    for icon, kws in DEPLOY_ICONS.items():
        if any(k.lower() in text for k in kws): found_dep.add(icon)
    if "openai" in text:  found_apis.add("OpenAI")
    if "stripe"  in text: found_apis.add("Stripe")

def skillicons(icons, ordered=None):
    if ordered:
        icons = [i for i in ordered if i in icons] + [i for i in icons if i not in ordered]
    return f'<img src="https://skillicons.dev/icons?i={",".join(icons)}&theme=dark"/>'

lang_html = skillicons(lang_icons)
fw_html   = skillicons(found_fw, ORDERED_FW)
db_html   = skillicons(found_db, ORDERED_DB)
tool_html = skillicons([t for t in ORDERED_TOOL if t in found_tool])
tool_html += '&nbsp;<img src="https://img.shields.io/badge/FFmpeg-007808?style=for-the-badge&logo=ffmpeg&logoColor=white"/>&nbsp;<img src="https://img.shields.io/badge/n8n-EA4B71?style=for-the-badge&logo=n8n&logoColor=white"/>'
dep_html  = skillicons([d for d in ORDERED_DEP if d in found_dep])
dep_html += '&nbsp;<img src="https://img.shields.io/badge/Caddy-00ADD8?style=for-the-badge&logo=caddy&logoColor=white"/>'

api_parts = ['<img src="https://skillicons.dev/icons?i=telegram&theme=dark"/>']
API_BADGES = {
    "Groq_AI":("F55036","groq"),"YouTube_API":("FF0000","youtube"),
    "Pexels_API":("05A081","pexels"),"WhatsApp_API":("25D366","whatsapp"),
    "OpenAI":("412991","openai"),"Stripe":("635BFF","stripe"),
}
for key, (color, logo) in API_BADGES.items():
    if key in found_apis:
        api_parts.append(f'&nbsp;<img src="https://img.shields.io/badge/{key}-{color}?style=for-the-badge&logo={logo}&logoColor=white"/>')
api_html = "".join(api_parts)

LIVE = "![Live](https://img.shields.io/badge/Live-00C851?style=flat-square)"
new_ai, new_web, new_auto = [], [], []
for repo in public:
    if repo["name"] in EXISTING: continue
    try: langs = api(f"https://api.github.com/repos/{USERNAME}/{repo['name']}/languages")
    except: langs = {}
    desc = (repo["description"] or "No description").replace("|","-")[:55]
    lang = repo.get("language") or "Code"
    row  = f"| [{repo['name']}]({repo['html_url']}) | {desc} | {lang} | {LIVE} |"
    cat  = classify(repo, langs)
    if cat=="ai": new_ai.append(row)
    elif cat=="auto": new_auto.append(row)
    else: new_web.append(row)

with open("README.md","r",encoding="utf-8") as f:
    content = f.read()

content = re.sub(r"Total%20Repos-\d+-", f"Total%20Repos-{total}-", content)
content = replace_inline(content, "LANGS",      lang_html)
content = replace_inline(content, "FRAMEWORKS", fw_html)
content = replace_inline(content, "DATABASES",  db_html)
content = replace_inline(content, "TOOLS",      tool_html)
content = replace_inline(content, "DEPLOY",     dep_html)
content = replace_inline(content, "APIS",       api_html)
content = replace_block(content, "PROJECTS-AI",   new_ai)
content = replace_block(content, "PROJECTS-WEB",  new_web)
content = replace_block(content, "PROJECTS-AUTO", new_auto)

with open("README.md","w",encoding="utf-8") as f:
    f.write(content)

print(f"Done! Total:{total} | New AI:{len(new_ai)} | New Web:{len(new_web)} | New Auto:{len(new_auto)}")
