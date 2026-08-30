"""
Combine dashboard/index.html and report/index.html into one tabbed artifact.
Each original page is embedded verbatim as an iframe srcdoc, so neither page's
CSS or JS needs to be touched or re-scoped -- full isolation, zero collision risk.
Run this LAST, after 05_build_dashboard.py and 07_build_report.py.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DASHBOARD_HTML = os.path.join(ROOT, "dashboard", "index.html")
REPORT_HTML = os.path.join(ROOT, "report", "index.html")
OUT_DIR = os.path.join(ROOT, "combined")
OUT_PATH = os.path.join(OUT_DIR, "index.html")


SHELL = r"""<!doctype html>
<html lang="en">
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
    <button class="tab-btn active" data-tab="report">Intelligence Report</button>
    <button class="tab-btn" data-tab="dashboard">Transfer Database</button>
  </nav>
  <main class="frames">
    <iframe class="tab-frame" id="frame-dashboard" title="Transfer Database"></iframe>
    <iframe class="tab-frame active" id="frame-report" title="Intelligence Report"></iframe>
  </main>

<script>
const DASHBOARD_HTML = __DASHBOARD_JSON__;
const REPORT_HTML = __REPORT_JSON__;

const frames = { dashboard: document.getElementById('frame-dashboard'), report: document.getElementById('frame-report') };
let loaded = { dashboard: false, report: false };

function loadTab(name){
  if (loaded[name]) return;
  frames[name].srcdoc = name === 'dashboard' ? DASHBOARD_HTML : REPORT_HTML;
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


def main():
    with open(DASHBOARD_HTML, encoding="utf-8") as f:
        dashboard_html = f.read()
    with open(REPORT_HTML, encoding="utf-8") as f:
        report_html = f.read()

    import base64
    audax_crest = os.path.join(ROOT, "data", "raw", "crests", "6363.png")
    with open(audax_crest, "rb") as f:
        audax_uri = "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")

    def safe_json(html):
        # Prevent the embedded HTML's own "</script>" from prematurely closing
        # the outer <script> tag -- the HTML tokenizer matches this literally,
        # regardless of JS string-quoting context.
        return json.dumps(html).replace("</script", "<\\/script").replace("</SCRIPT", "<\\/SCRIPT")

    shell = SHELL.replace("__AUDAX_LOGO__", audax_uri)
    shell = shell.replace("__DASHBOARD_JSON__", safe_json(dashboard_html))
    shell = shell.replace("__REPORT_JSON__", safe_json(report_html))

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(shell)
    print(f"Combined artifact written -> {OUT_PATH} ({os.path.getsize(OUT_PATH)/1024/1024:.2f} MB)")


if __name__ == "__main__":
    main()
