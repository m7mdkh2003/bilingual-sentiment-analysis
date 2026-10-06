"""Dependency-free local web interface for the trained model."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from app import predict_sentiment


HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Bilingual Sentiment Analysis</title>
  <style>
    :root { color-scheme: light; --ink:#102a43; --muted:#627d98; --blue:#0b7285; --sand:#f8f9fa; }
    * { box-sizing:border-box; }
    body { margin:0; min-height:100vh; font-family:Arial,"Noto Sans Arabic",sans-serif; background:linear-gradient(135deg,#e3fafc,#fff4e6); color:var(--ink); display:grid; place-items:center; padding:24px; }
    main { width:min(780px,100%); background:white; border:1px solid #d9e2ec; border-radius:22px; padding:34px; box-shadow:0 18px 50px rgba(16,42,67,.12); }
    .badge { display:inline-block; background:#c5f6fa; color:#0b7285; border-radius:999px; padding:7px 12px; font-weight:700; font-size:13px; }
    h1 { margin:16px 0 6px; font-size:clamp(28px,5vw,46px); line-height:1.05; }
    .ar { direction:rtl; text-align:right; }
    .sub { color:var(--muted); margin:0 0 24px; }
    textarea { width:100%; min-height:150px; resize:vertical; border:1px solid #bcccdc; border-radius:14px; padding:16px; font:inherit; font-size:17px; line-height:1.6; }
    textarea:focus { outline:3px solid #99e9f2; border-color:#0b7285; }
    .actions { display:flex; flex-wrap:wrap; gap:10px; margin-top:14px; }
    button { border:0; border-radius:12px; padding:12px 18px; font:inherit; font-weight:700; cursor:pointer; }
    #analyze { background:var(--blue); color:white; }
    .example { background:#edf2f7; color:#334e68; }
    #result { display:none; margin-top:24px; padding:20px; border-radius:15px; background:var(--sand); border-left:6px solid var(--blue); }
    #label { font-size:28px; font-weight:800; margin-bottom:8px; }
    .meter { height:11px; border-radius:999px; background:#d9e2ec; overflow:hidden; margin:12px 0; }
    .meter span { display:block; height:100%; background:linear-gradient(90deg,#12b886,#0b7285); }
    small { color:var(--muted); line-height:1.5; display:block; }
  </style>
</head>
<body>
<main>
  <span class="badge">MACHINE LEARNING PORTFOLIO PROJECT</span>
  <h1>Bilingual Sentiment Analysis</h1>
  <p class="sub">Arabic-English sentiment classification with confidence-aware output</p>
  <h2 class="ar">نظام ثنائي اللغة لتحليل مشاعر مراجعات العملاء</h2>
  <textarea id="text" placeholder="Write a review in Arabic or English... / اكتب مراجعة بالعربية أو الإنجليزية"></textarea>
  <div class="actions">
    <button id="analyze">Analyze / تحليل</button>
    <button class="example" data-text="This product is excellent and easy to use.">English example</button>
    <button class="example" data-text="الخدمة ممتازة وسريعة وأنا سعيد جداً">مثال عربي</button>
  </div>
  <section id="result" aria-live="polite">
    <div id="label"></div>
    <div id="confidence"></div>
    <div class="meter"><span id="bar"></span></div>
    <small id="language"></small>
    <small id="note"></small>
  </section>
</main>
<script>
const text = document.querySelector('#text');
const result = document.querySelector('#result');
document.querySelectorAll('.example').forEach(b => b.onclick = () => text.value = b.dataset.text);
document.querySelector('#analyze').onclick = async () => {
  const value = text.value.trim();
  if (!value) return;
  const response = await fetch('/api/predict', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({text:value})});
  const data = await response.json();
  if (!response.ok) { alert(data.error || 'Error'); return; }
  document.querySelector('#label').textContent = `${data.label_en} — ${data.label_ar}`;
  document.querySelector('#confidence').textContent = `Confidence / الثقة: ${(data.confidence*100).toFixed(1)}%`;
  document.querySelector('#bar').style.width = `${Math.round(data.confidence*100)}%`;
  document.querySelector('#language').textContent = `Detected language / اللغة: ${data.detected_language.toUpperCase()}`;
  document.querySelector('#note').textContent = `${data.note_en} ${data.note_ar}`;
  result.style.display = 'block';
};
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path != "/":
            self._send(404, b"Not found", "text/plain; charset=utf-8")
            return
        self._send(200, HTML.encode("utf-8"), "text/html; charset=utf-8")

    def do_POST(self):
        if self.path != "/api/predict":
            self._send(404, b"Not found", "text/plain; charset=utf-8")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            result = predict_sentiment(str(payload.get("text", "")))
            body = json.dumps(result, ensure_ascii=False).encode("utf-8")
            self._send(200, body, "application/json; charset=utf-8")
        except Exception as exc:
            body = json.dumps({"error": str(exc)}, ensure_ascii=False).encode("utf-8")
            self._send(400, body, "application/json; charset=utf-8")

    def log_message(self, format, *args):
        return


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Open http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop / اضغط Ctrl+C للإيقاف")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

