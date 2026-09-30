"""
Combine the Audax report and one transfer dashboard per country into a single
tabbed artifact. Each original page is embedded verbatim as an iframe srcdoc, so
no page's CSS or JS needs to be touched or re-scoped -- full isolation, zero
collision risk.
Run this LAST, after 07_build_report.py and 05_build_dashboard.py --league X for
every country (chile, uruguay, paraguay, peru).
"""
import argparse
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_HTML = os.path.join(ROOT, "report", "index.html")
OUT_DIR = os.path.join(ROOT, "combined")


SHELL = r"""<!doctype html>
<html lang="__LANG__">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Audax Transfer Intelligence</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    color-scheme: light;
    --surface-1: #fcfcfb;
    --ink: #0b0b0b;
    --ink-2: #52514e;
    --muted: #898781;
    --border: rgba(11,11,11,0.10);
    --accent: #0353cc;
    --accent-ink: #ffffff;
    --plane: #f9f9f7;
    --font-display: "Barlow Condensed", system-ui, sans-serif;
    --font-body: "IBM Plex Sans", system-ui, sans-serif;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      color-scheme: dark;
      --surface-1: #1a1a19;
      --ink: #ffffff;
      --ink-2: #c3c2b7;
      --muted: #898781;
      --border: rgba(255,255,255,0.10);
      --accent: #4d86e8;
      --plane: #0d0d0d;
    }
  }
  :root[data-theme="dark"] {
    color-scheme: dark;
    --surface-1: #1a1a19;
    --ink: #ffffff;
    --ink-2: #c3c2b7;
    --muted: #898781;
    --border: rgba(255,255,255,0.10);
    --accent: #4d86e8;
    --plane: #0d0d0d;
  }

  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; height: 100%; background: var(--plane); }
  body { font-family: var(--font-body); display: flex; flex-direction: column; }

  nav.tabbar {
    display: flex; align-items: center; gap: 4px;
    padding: 10px 20px; background: var(--surface-1); border-bottom: 3px solid var(--accent);
    flex: none;
  }
  .tabbar-brand {
    width: 30px; height: 30px; border-radius: 7px; margin-right: 10px;
    display: flex; align-items: center; justify-content: center; flex: none;
    overflow: hidden; background: var(--plane); border: 1px solid var(--border);
  }
  .tabbar-brand img { width: 100%; height: 100%; object-fit: contain; }
  .tabbar-title {
    font-family: var(--font-display); font-weight: 800; text-transform: uppercase;
    font-size: 15px; letter-spacing: 0.02em; color: var(--ink); margin-right: 18px; white-space: nowrap;
  }
  button.tab-btn {
    font-family: var(--font-body); font-weight: 600; font-size: 13.5px;
    color: var(--ink-2); background: transparent; border: 1px solid transparent;
    border-radius: 7px; padding: 7px 14px; cursor: pointer;
  }
  button.tab-btn:hover { background: var(--border); }
  button.tab-btn.active { background: var(--accent); color: var(--accent-ink); }

  main.frames { position: relative; flex: 1; min-height: 0; }
  iframe.tab-frame {
    position: absolute; inset: 0; width: 100%; height: 100%; border: 0;
    display: none; background: var(--surface-1);
  }
  iframe.tab-frame.active { display: block; }

  @media (max-width: 640px) {
    .tabbar-title { display: none; }
  }
</style>
</head>
<body>
  <nav class="tabbar">
    <div class="tabbar-brand"><img src="__AUDAX_LOGO__" alt=""></div>
    <div class="tabbar-title">Audax Transfer Intelligence</div>
    <button class="tab-btn active" data-tab="report">__REPORT_LABEL__</button>
    __COUNTRY_BUTTONS__
  </nav>
  <main class="frames">
    __COUNTRY_FRAMES__
    <iframe class="tab-frame active" id="frame-report" title="__REPORT_LABEL__"></iframe>
  </main>

<script>
const PAGES = __PAGES_JSON__;

const frames = Object.fromEntries(Object.keys(PAGES).map(k => [k, document.getElementById('frame-' + k)]));
const loaded = Object.fromEntries(Object.keys(PAGES).map(k => [k, false]));

function loadTab(name){
  if (loaded[name]) return;
  frames[name].srcdoc = PAGES[name];
  loaded[name] = true;
}
loadTab('report');

document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const tab = btn.getAttribute('data-tab');
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b === btn));
    document.querySelectorAll('.tab-frame').forEach(f => f.classList.remove('active'));
    frames[tab].classList.add('active');
    loadTab(tab);
  });
});
</script>
</body>
</html>
"""


def args_lang(es):
    return "es" if es else "en"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", default="en", choices=["en", "es"])
    es = parser.parse_args().lang == "es"
    suffix = "_es" if es else ""
    tabs = [("chile", "Chile"), ("uruguay", "Uruguay"), ("paraguay", "Paraguay"), ("peru", "Perú" if es else "Peru")]
    report_label = "Informe de Inteligencia Audax" if es else "Audax Intelligence Report"

    pages = {}
    with open(os.path.join(ROOT, "report", f"index{suffix}.html"), encoding="utf-8") as f:
        pages["report"] = f.read()
    for key, _ in tabs:
        with open(os.path.join(ROOT, "dashboard", key, f"index{suffix}.html"), encoding="utf-8") as f:
            pages[key] = f.read()

    import base64
    audax_crest = os.path.join(ROOT, "data", "raw", "crests", "6363.png")
    with open(audax_crest, "rb") as f:
        audax_uri = "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")

    def safe_json_obj(obj):
        # Prevent the embedded HTML's own "</script>" from prematurely closing
        # the outer <script> tag -- the HTML tokenizer matches this literally,
        # regardless of JS string-quoting context.
        return json.dumps(obj).replace("</script", "<\\/script").replace("</SCRIPT", "<\\/SCRIPT")

    buttons = "\n    ".join(f'<button class="tab-btn" data-tab="{k}">{label}</button>' for k, label in tabs)
    country_frames = "\n    ".join(
        f'<iframe class="tab-frame" id="frame-{k}" title="{label}"></iframe>' for k, label in tabs)
    shell = SHELL.replace("__AUDAX_LOGO__", audax_uri)
    shell = shell.replace("__LANG__", args_lang(es)).replace("__REPORT_LABEL__", report_label)
    shell = shell.replace("__COUNTRY_BUTTONS__", buttons)
    shell = shell.replace("__COUNTRY_FRAMES__", country_frames)
    shell = shell.replace("__PAGES_JSON__", safe_json_obj(pages))

    out_path = os.path.join(OUT_DIR, f"index{suffix}.html")
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(shell)
    print(f"Combined artifact written -> {out_path} ({os.path.getsize(out_path)/1024/1024:.2f} MB)")


if __name__ == "__main__":
    main()
