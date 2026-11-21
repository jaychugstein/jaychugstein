# Puts the games on the profile page in order of popularity (most downloaded first).
# Runs once a day on GitHub (see .github/workflows/popular.yml). To add a new game:
# put it at the TOP of games.json (newest first) and add its title screen as images/<repo>.png.
import json, os, urllib.request

USER = "jaychugstein"
here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)
games = json.load(open(os.path.join(root, "games.json")))

def downloads(repo):
    # For each release, count its most-downloaded file (FX games come as 2-3 files, so adding
    # them all up would count one person 3 times). Then add up all the releases.
    req = urllib.request.Request(f"https://api.github.com/repos/{USER}/{repo}/releases?per_page=100",
                                 headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN")
    if token: req.add_header("Authorization", f"Bearer {token}")
    try:
        rel = json.load(urllib.request.urlopen(req, timeout=30))
    except Exception as e:
        raise SystemExit(f"{repo}: couldn't read downloads ({e}), so the page is left as it was")
    return sum(max([a["download_count"] for a in r.get("assets", [])] or [0]) for r in rel)

for i, g in enumerate(games):
    g["downloads"], g["newest"] = downloads(g["repo"]), i
    print(f'{g["downloads"]:6}  {g["name"]}')
games.sort(key=lambda g: (-g["downloads"], g["newest"]))   # most popular first; ties stay newest first

tiles = "\n".join(f'<a href="https://{USER}.github.io/{g["repo"]}/"><img src="images/{g["repo"]}.png" alt="{g["name"]}" width="32%"></a>'
                  for g in games)
readme = f'''<p align="center">
  <img src="images/header.gif" alt="Jay Chugstein: Arduboy games" width="512">
</p>

<p align="center">
  <b>Handheld games for the Arduboy, by Jay Chugstein.</b><br>
  Tap a game to play it right in your browser. Most popular first.
</p>

<p align="center">
{tiles}
</p>
'''
open(os.path.join(root, "README.md"), "w").write(readme)
