import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.join(path.dirname(fileURLToPath(import.meta.url)), 'site');
const types = { '.html':'text/html; charset=utf-8', '.css':'text/css; charset=utf-8', '.js':'application/javascript; charset=utf-8', '.json':'application/json', '.png':'image/png', '.jpg':'image/jpeg', '.jpeg':'image/jpeg', '.webp':'image/webp', '.svg':'image/svg+xml', '.gif':'image/gif', '.ico':'image/x-icon', '.woff':'font/woff', '.woff2':'font/woff2', '.ttf':'font/ttf', '.eot':'application/vnd.ms-fontobject', '.pdf':'application/pdf' };

// The embed target is read by the visitor's browser, so CHAT_ORIGIN must be an
// address the browser can reach (not a Docker service name).
function embedConfig() {
  const chatOrigin = process.env.CHAT_ORIGIN || 'http://localhost:3100';
  const widgetId = Number(process.env.WIDGET_ID || 1);
  let origin;
  try { origin = new URL(chatOrigin); } catch { origin = null; }
  if (!origin || !['http:', 'https:'].includes(origin.protocol)) throw new Error(`CHAT_ORIGIN must be an http(s) URL, got ${JSON.stringify(chatOrigin)}`);
  if (!Number.isInteger(widgetId) || widgetId < 1) throw new Error(`WIDGET_ID must be a positive integer, got ${JSON.stringify(process.env.WIDGET_ID)}`);
  return { chatOrigin: origin.origin, widgetId };
}
let config;
try { config = embedConfig(); } catch (error) { console.error(error.message); process.exit(1); }
const configScript = 'window.ETPL_PREVIEW=' + JSON.stringify(config) + ';';

function send(req, res, status, headers, body) {
  res.writeHead(status, headers);
  res.end(req.method === 'HEAD' ? undefined : body);
}

http.createServer(async (req, res) => {
  if (!['GET','HEAD'].includes(req.method)) { send(req, res, 405, { 'Content-Type':'text/plain' }, 'Local preview: submissions disabled'); return; }
  let pathname;
  try { pathname = decodeURIComponent(new URL(req.url, 'http://preview.local').pathname); }
  catch { send(req, res, 400, { 'Content-Type':'text/plain' }, 'Bad request'); return; }
  if (pathname === '/preview-config.js') {
    send(req, res, 200, { 'Content-Type':'application/javascript; charset=utf-8', 'Cache-Control':'no-store' }, configScript); return;
  }
  let location = path.resolve(root, '.' + pathname);
  if (location !== root && !location.startsWith(root + path.sep)) { send(req, res, 403, {}, ''); return; }
  try {
    let stat = await fs.promises.stat(location);
    if (stat.isDirectory()) {
      // Relative links inside index.html resolve against the trailing slash.
      if (!pathname.endsWith('/')) { send(req, res, 301, { Location: encodeURI(pathname + '/') }, ''); return; }
      location = path.join(location, 'index.html');
      stat = await fs.promises.stat(location);
    }
    const etag = `W/"${stat.size.toString(16)}-${Math.floor(stat.mtimeMs).toString(16)}"`;
    const headers = { 'Content-Type':types[path.extname(location).toLowerCase()] || 'application/octet-stream', 'Cache-Control':'no-cache', ETag: etag };
    if (req.headers['if-none-match'] === etag) { send(req, res, 304, headers, ''); return; }
    res.writeHead(200, { ...headers, 'Content-Length': stat.size });
    if (req.method === 'HEAD') { res.end(); return; }
    fs.createReadStream(location).on('error', () => res.destroy()).pipe(res);
  } catch { send(req, res, 404, { 'Content-Type':'text/plain' }, 'This page or asset was unavailable in the captured public site.'); }
}).listen(Number(process.env.PORT || 3150), process.env.HOST || '127.0.0.1', () => {
  console.log(`ETPL website preview on http://${process.env.HOST || '127.0.0.1'}:${process.env.PORT || 3150}`);
  console.log(`Embedding chatbot widget ${config.widgetId} from ${config.chatOrigin} (set CHAT_ORIGIN / WIDGET_ID to change).`);
});
