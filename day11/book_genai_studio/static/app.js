/* Book GenAI Studio – frontend (plain JavaScript, no build step). */
"use strict";

// ================================================================ small helpers
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const fmt = (n) => Number(n || 0).toLocaleString();
const money = (n) => "$" + Number(n || 0).toFixed(n && n < 0.01 ? 5 : 4);
const uid = () => Math.random().toString(36).slice(2, 10);
const debounce = (fn, ms = 350) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; };

const store = {
  get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* storage full or blocked */ } },
};

function md(text) {
  if (window.marked && window.DOMPurify) return DOMPurify.sanitize(marked.parse(text || ""));
  return esc(text).replace(/\n/g, "<br>");
}

function toast(message, { error = false, hint = "" } = {}) {
  const t = document.createElement("div");
  t.className = "toast" + (error ? " error" : "");
  t.innerHTML = `${esc(message)}${hint ? `<small>${esc(hint)}</small>` : ""}`;
  $("#toasts").append(t);
  setTimeout(() => t.remove(), error ? 7000 : 3000);
}

async function copyText(text) {
  try { await navigator.clipboard.writeText(text); }
  catch {
    const ta = Object.assign(document.createElement("textarea"), { value: text });
    document.body.append(ta); ta.select(); document.execCommand("copy"); ta.remove();
  }
  toast("Copied to clipboard ✓");
}

function download(name, text, type = "text/markdown") {
  const a = Object.assign(document.createElement("a"), { href: URL.createObjectURL(new Blob([text], { type })), download: name });
  a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}

// ================================================================ browser book storage (IndexedDB)
// The browser keeps a copy of every processed book. Free Vercel servers forget files,
// so when the server says "book_not_found" we quietly send this copy back.
const idb = (() => {
  let dbp;
  const open = () => dbp ??= new Promise((res, rej) => {
    const r = indexedDB.open("book-studio", 1);
    r.onupgradeneeded = () => r.result.createObjectStore("books", { keyPath: "id" });
    r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error);
  });
  const run = async (mode, fn) => {
    try {
      const db = await open();
      return await new Promise((res, rej) => {
        const tx = db.transaction("books", mode); const req = fn(tx.objectStore("books"));
        tx.oncomplete = () => res(req?.result); tx.onerror = () => rej(tx.error);
      });
    } catch { return undefined; }
  };
  return {
    put: (b) => run("readwrite", (s) => s.put(b)),
    get: (id) => run("readonly", (s) => s.get(id)),
    del: (id) => run("readwrite", (s) => s.delete(id)),
    all: () => run("readonly", (s) => s.getAll()),
  };
})();

// ================================================================ state
const state = {
  settings: store.get("settings", { apiKey: "", model: "" }),
  health: null,
  books: {},                       // id -> public book info
  activeBook: store.get("activeBook", ""),
  convos: store.get("convos", []),
  activeConvo: null,
  chatAbort: null,
  catalog: null,
  genType: "study_notes",
  notesCache: {},                  // `${bookId}:${chapter}:${mode}` -> notes
};

// ================================================================ API wrapper (errors + auto-restore)
class AppError extends Error {
  constructor(code, message, hint = "") { super(message); this.code = code; this.hint = hint; }
}

async function api(path, { method = "GET", body, form, stream = false, signal } = {}, retry = true) {
  const headers = {};
  if (state.settings.apiKey) headers["X-OpenAI-Key"] = state.settings.apiKey;
  let payload;
  if (form) payload = form;
  else if (body !== undefined) { headers["Content-Type"] = "application/json"; payload = JSON.stringify(body); }
  let res;
  try { res = await fetch(path, { method, headers, body: payload, signal }); }
  catch (e) {
    if (e.name === "AbortError") throw e;
    throw new AppError("network", "Can't reach the server.", "Check your connection, or that the server is running.");
  }
  if (!res.ok) {
    let data = {};
    try { data = await res.json(); } catch { /* not JSON */ }
    const err = data.error || {};
    if (Array.isArray(data.detail)) {   // FastAPI validation error
      const d = data.detail[0];
      err.code = "invalid_input"; err.message = `${(d.loc || []).slice(1).join(".")}: ${d.msg}`;
    }
    if (err.code === "book_not_found" && retry) {
      const bookId = body?.book_id || path.match(/\/api\/books\/([a-f0-9]+)/)?.[1] || body?.summarize?.book_id || body?.generate?.book_id;
      if (bookId && await restoreBook(bookId)) return api(path, { method, body, form, stream, signal }, false);
    }
    if (res.status === 413 && !err.code) { err.code = "too_large"; err.message = "That's too big for the server."; err.hint = "Vercel's free plan accepts up to ~4.5 MB per request."; }
    throw new AppError(err.code || `http_${res.status}`, err.message || `Server error (${res.status})`, err.hint || "");
  }
  return stream ? res : res.json();
}

async function restoreBook(id) {
  const copy = await idb.get(id);
  if (!copy) return false;
  try {
    await api("/api/books/restore", { method: "POST", body: copy }, false);
    toast("Re-sent the book to the server (it had restarted).");
    return true;
  } catch { return false; }
}

function showError(e) {
  if (e?.name === "AbortError") return;
  console.error(e);
  toast(e.message || "Something went wrong", { error: true, hint: e.hint });
}

// local usage log – survives server restarts (Vercel)
function recordUsage(feature, usage) {
  if (!usage || !usage.calls) return;
  const log = store.get("usageLog", []);
  log.push({ ts: Date.now(), feature, tokens: usage.total_tokens, cost: usage.cost_usd });
  store.set("usageLog", log.slice(-1000));
}

function usageLine(u, extra = {}) {
  const bits = [];
  if (extra.mode) bits.push(extra.mode === "live" ? "🤖 Live AI" : "🧩 Demo");
  if (extra.version) bits.push(`prompt ${extra.version}`);
  if (u?.total_tokens) bits.push(`${fmt(u.prompt_tokens)} in + ${fmt(u.completion_tokens)} out tokens`);
  if (u?.cost_usd) bits.push(money(u.cost_usd));
  if (u?.calls > 1) bits.push(`${u.calls} calls`);
  if (u?.latency_ms) bits.push(`${(u.latency_ms / 1000).toFixed(1)}s`);
  return bits.map((b) => `<span>${esc(b)}</span>`).join("");
}

// ================================================================ feedback
function saveFeedback(fb) {
  const log = store.get("feedbackLog", []);
  log.push({ ...fb, ts: Date.now() });
  store.set("feedbackLog", log.slice(-2000));
  return api("/api/feedback", { method: "POST", body: fb }).catch(() => { /* kept locally anyway */ });
}

function outputCard({ title, output, result, feature, filename }) {
  const card = document.createElement("div");
  card.className = "out-card";
  card.innerHTML = `
    <div class="out-head"><b>${esc(title)}</b><div class="meta">${usageLine(result.usage, { mode: result.mode, version: result.prompt_version })}</div></div>
    <div class="out-body md">${md(output)}</div>
    <div class="out-foot">
      <button class="btn small" data-act="copy">📋 Copy</button>
      <button class="btn small ghost" data-act="dl">⬇ .md</button>
      <span class="muted">Rate:</span>
      <span class="stars">${[1, 2, 3, 4, 5].map((n) => `<button data-star="${n}" title="${n} star${n > 1 ? "s" : ""}">★</button>`).join("")}</span>
      <input class="fb-comment" placeholder="What could be better? (optional)">
      <button class="btn small" data-act="fb" disabled>Send</button>
    </div>`;
  let rating = 0;
  $$("[data-star]", card).forEach((b) => b.onclick = () => {
    rating = +b.dataset.star;
    $$("[data-star]", card).forEach((x) => x.classList.toggle("on", +x.dataset.star <= rating));
    $('[data-act="fb"]', card).disabled = false;
  });
  $('[data-act="copy"]', card).onclick = () => copyText(output);
  $('[data-act="dl"]', card).onclick = () => download(filename || "output.md", output);
  $('[data-act="fb"]', card).onclick = async (ev) => {
    await saveFeedback({ feature, prompt_version: result.prompt_version, rating, comment: $(".fb-comment", card).value,
      output_id: result.output_id, output_excerpt: output.slice(0, 500) });
    ev.target.textContent = "Thanks ✓"; ev.target.disabled = true;
  };
  return card;
}

// ================================================================ health + settings
async function loadHealth() {
  try {
    state.health = await api("/api/health");
    const h = state.health, badge = $("#modeBadge");
    const model = state.settings.model || h.model;
    badge.className = "badge " + h.mode;
    badge.textContent = h.mode === "live" ? `● Live AI · ${model}` : "● Demo mode";
    badge.title = h.mode === "live" ? `Using OpenAI (${h.server_key && !state.settings.apiKey ? "server key" : "your key"}). Tokenizer: ${h.tokenizer}`
      : "No API key: features run offline with simple algorithms. Add a key in Settings for real AI.";
    $("#maxMb").textContent = h.max_upload_mb;
    $("#modelSelect").innerHTML = h.models.map((m) => `<option ${m === model ? "selected" : ""}>${m}</option>`).join("");
  } catch (e) { showError(e); }
}

function setupSettings() {
  const dlg = $("#settings");
  $("#openSettings").onclick = () => { $("#apiKey").value = state.settings.apiKey; dlg.showModal(); };
  $("#toggleKey").onclick = () => { const i = $("#apiKey"); i.type = i.type === "password" ? "text" : "password"; $("#toggleKey").textContent = i.type === "password" ? "Show" : "Hide"; };
  $("#saveSettings").onclick = () => {
    const key = $("#apiKey").value.trim();
    if (key && !key.startsWith("sk-")) toast("That doesn't look like an OpenAI key (they start with sk-).", { error: true });
    state.settings = { apiKey: key, model: $("#modelSelect").value };
    store.set("settings", state.settings);
    loadHealth();
    toast("Settings saved");
  };
}
const model = () => state.settings.model || undefined;

// ================================================================ tabs
function setupTabs() {
  $$(".tab").forEach((t) => t.onclick = () => {
    $$(".tab").forEach((x) => x.classList.toggle("active", x === t));
    $$(".panel").forEach((p) => p.classList.toggle("active", p.id === "tab-" + t.dataset.tab));
    store.set("tab", t.dataset.tab);
    if (t.dataset.tab === "usage") loadUsage();
    if (t.dataset.tab === "lab") loadLab();
    if (t.dataset.tab === "ask") $("#chatInput").focus();
  });
  const saved = store.get("tab", "library");
  $(`.tab[data-tab="${saved}"]`)?.click();
}

// ================================================================ library
function bookFromPortable(p) {
  return { id: p.id, title: p.title, filename: p.filename, created: p.created, pages: p.pages, words: p.words, tokens: p.tokens,
    chapters: p.chapters.map((c, i) => ({ idx: c.idx ?? i, title: c.title, tokens: c.tokens, words: c.words })),
    chunks: p.chunks.length, semantic_search: false, localOnly: true };
}

async function loadBooks() {
  const local = (await idb.all()) || [];
  state.books = {};
  local.forEach((p) => state.books[p.id] = bookFromPortable(p));
  try {
    (await api("/api/books")).forEach((b) => state.books[b.id] = { ...b, localOnly: false });
  } catch (e) { showError(e); }
  if (state.activeBook && !state.books[state.activeBook]) state.activeBook = "";
  renderBooks();
}

function renderBooks() {
  const list = Object.values(state.books).sort((a, b) => (b.created || 0) - (a.created || 0));
  $("#activeBook").innerHTML = `<option value="">No book (general)</option>` +
    list.map((b) => `<option value="${b.id}" ${b.id === state.activeBook ? "selected" : ""}>${esc(b.title)}</option>`).join("");
  $("#bookList").innerHTML = list.length ? list.map((b) => `
    <div class="book-item ${b.id === state.activeBook ? "active" : ""}" data-id="${b.id}">
      <div><b>${esc(b.title)}</b>
        <small>${fmt(b.words)} words · ${fmt(b.tokens)} tokens · ${b.chapters.length} chapters${b.pages ? ` · ${b.pages} pages` : ""}
        ${b.semantic_search ? " · 🧠 meaning search" : " · 🔎 keyword search"}${b.localOnly ? " · saved in browser" : ""}</small></div>
      <div class="acts"><button class="btn small" data-act="use">${b.id === state.activeBook ? "✓ Active" : "Use"}</button>
        <button class="btn small ghost" data-act="del" title="Delete">🗑</button></div>
    </div>`).join("") : `<p class="muted">No books yet. Upload one, or try the sample.</p>`;
  $$(".book-item").forEach((el) => {
    $('[data-act="use"]', el).onclick = () => setActiveBook(el.dataset.id);
    $('[data-act="del"]', el).onclick = () => deleteBook(el.dataset.id);
  });
  updateChapterSelects();
  renderBookDetail();
}

function setActiveBook(id) {
  state.activeBook = id;
  store.set("activeBook", id);
  renderBooks();
  renderSuggestions();
  updateSumMeter();
}

async function deleteBook(id) {
  if (!confirm(`Delete “${state.books[id]?.title}” from the server and this browser?`)) return;
  await api(`/api/books/${id}`, { method: "DELETE" }, false).catch(() => {});
  await idb.del(id);
  if (state.activeBook === id) setActiveBook("");
  loadBooks();
}

function renderBookDetail() {
  const b = state.books[state.activeBook], box = $("#bookDetail");
  if (!b) { box.classList.add("hidden"); return; }
  const prices = state.health?.prices?.[state.settings.model || state.health?.model] || [0.15, 0.6];
  const readCost = (b.tokens * prices[0]) / 1e6;
  box.classList.remove("hidden");
  box.innerHTML = `<h2>📘 ${esc(b.title)}</h2>
    <p class="muted">Reading the whole book once costs about <b>${money(readCost)}</b> in input tokens with ${esc(state.settings.model || state.health?.model || "")}.
    Click a chapter to preview it.</p>
    <div class="chapters">${b.chapters.map((c) => `<button class="chapter" data-idx="${c.idx}"><b>${esc(c.title)}</b><small>${fmt(c.words)} words · ${fmt(c.tokens)} tokens</small></button>`).join("")}</div>
    <div id="chapterPreview"></div>`;
  $$(".chapter", box).forEach((el) => el.onclick = async () => {
    try {
      const c = await api(`/api/books/${b.id}/chapters/${el.dataset.idx}`);
      $("#chapterPreview").innerHTML = `<div class="preview"><b>${esc(c.title)}</b>\n\n${esc(c.text)}${c.truncated ? "\n\n…(preview cut)" : ""}</div>`;
    } catch (e) { showError(e); }
  });
}

function updateChapterSelects() {
  const b = state.books[state.activeBook];
  const opts = b ? b.chapters.map((c) => `<option value="${c.idx}">${esc(c.title)} (${fmt(c.tokens)} tok)</option>`).join("") : "<option value=''>— pick a book first —</option>";
  ["#sumChapter", "#genChapter", "#cmpChapter"].forEach((s) => $(s).innerHTML = opts);
  $("#chatChapter").innerHTML = `<option value="">Whole book</option>` + (b ? b.chapters.map((c) => `<option value="${c.idx}">${esc(c.title)}</option>`).join("") : "");
}

async function uploadFile(file) {
  const max = state.health?.max_upload_mb || 25;
  const status = $("#uploadStatus");
  if (file.size > max * 1024 * 1024) {
    status.className = "status error";
    status.textContent = `“${file.name}” is ${(file.size / 1048576).toFixed(1)} MB; the limit here is ${max} MB. Try a .txt version or compress the PDF.`;
    return;
  }
  status.className = "status";
  status.textContent = `⏳ Reading “${file.name}”, finding chapters and building the search index…`;
  const form = new FormData();
  form.append("file", file);
  try {
    const r = await api("/api/books", { method: "POST", form });
    await idb.put(r.portable);
    status.textContent = `✅ “${r.book.title}” is ready: ${r.book.chapters.length} chapters, ${fmt(r.book.chunks)} passages.` +
      (r.usage?.cost_usd ? ` Indexing cost ${money(r.usage.cost_usd)}.` : "") + (r.warning ? ` ⚠ ${r.warning}` : "");
    recordUsage("embeddings", r.usage);
    await loadBooks();
    setActiveBook(r.book.id);
  } catch (e) {
    status.className = "status error";
    status.textContent = `❌ ${e.message} ${e.hint || ""}`;
  }
}

function setupLibrary() {
  const zone = $("#dropZone"), input = $("#fileInput");
  input.onchange = () => input.files[0] && uploadFile(input.files[0]);
  ["dragenter", "dragover"].forEach((ev) => zone.addEventListener(ev, (e) => { e.preventDefault(); zone.classList.add("over"); }));
  ["dragleave", "drop"].forEach((ev) => zone.addEventListener(ev, (e) => { e.preventDefault(); zone.classList.remove("over"); }));
  zone.addEventListener("drop", (e) => e.dataTransfer.files[0] && uploadFile(e.dataTransfer.files[0]));
  $("#loadSample").onclick = async () => {
    const blob = await (await fetch("/api/sample")).blob();
    uploadFile(new File([blob], "the_lighthouse_apprentice.txt", { type: "text/plain" }));
  };
  $("#activeBook").onchange = (e) => setActiveBook(e.target.value);
}

// ================================================================ summarize
function needBook() {
  if (!state.activeBook) { toast("Pick or upload a book first (Library tab).", { error: true }); return true; }
  return false;
}

const updateSumMeter = debounce(async () => {
  const scope = $("#sumScope").value, meter = $("#sumMeter"), b = state.books[state.activeBook];
  const m = state.settings.model || state.health?.model || "gpt-4o-mini";
  const price = state.health?.prices?.[m] || [0.15, 0.6];
  const est = (tin, tout) => money((tin * price[0] + tout * price[1]) / 1e6);
  if (scope === "text") {
    const text = $("#sumText").value;
    if (!text.trim()) { meter.textContent = "Paste text to see its token count."; return; }
    try {
      const r = await api("/api/tokens", { method: "POST", body: { text, model: m, expected_output_tokens: 500 } });
      meter.className = "token-meter" + (r.fits_in_one_call ? "" : " warn");
      meter.innerHTML = `<b>${fmt(r.tokens)}</b> tokens · ${fmt(r.words)} words · est. ${money(r.estimated_cost_usd)}` +
        (r.fits_in_one_call ? "" : " · long text: will be split and combined (map-reduce)");
    } catch { meter.textContent = "—"; }
  } else if (!b) { meter.textContent = "Pick a book first."; }
  else if (scope === "chapter") {
    const c = b.chapters[+$("#sumChapter").value] || b.chapters[0];
    meter.className = "token-meter";
    meter.innerHTML = `<b>${fmt(c.tokens)}</b> tokens in this chapter · est. ${est(c.tokens, 600)}`;
  } else {
    meter.className = "token-meter";
    meter.innerHTML = `<b>${fmt(b.tokens)}</b> tokens · ${b.chapters.length} chapters → ${b.chapters.length + 1} AI calls · est. ${est(b.tokens * 1.05, b.chapters.length * 300 + 800)}`;
  }
}, 300);

async function runSummarize() {
  const scope = $("#sumScope").value, btn = $("#runSummarize");
  const base = { length: $("#sumLength").value, style: $("#sumStyle").value, prompt_version: $("#sumVersion").value, model: model() };
  if (scope !== "text" && needBook()) return;
  btn.disabled = true;
  const prog = $("#sumProgress");
  try {
    let result, title;
    const b = state.books[state.activeBook];
    if (scope === "text") {
      result = await api("/api/summarize", { method: "POST", body: { ...base, scope: "text", text: $("#sumText").value } });
      title = "Summary of your text";
    } else if (scope === "chapter") {
      const idx = +$("#sumChapter").value;
      result = await api("/api/summarize", { method: "POST", body: { ...base, scope: "chapter", book_id: b.id, chapter: idx } });
      title = `${b.chapters[idx].title} — summary`;
    } else {
      // Whole book: one request per chapter (keeps each request short — important on Vercel), then combine.
      prog.classList.remove("hidden");
      const mode = state.health?.mode, notes = new Array(b.chapters.length), totals = { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0, cost_usd: 0, calls: 0, latency_ms: 0 };
      const t0 = Date.now();
      let done = 0, next = 0;
      const setP = (txt) => { prog.style.setProperty("--p", `${Math.round((done / (b.chapters.length + 1)) * 100)}%`); $("span", prog).textContent = txt; };
      setP(`Reading chapter 1 of ${b.chapters.length}…`);
      const worker = async () => {
        while (next < b.chapters.length) {
          const i = next++, key = `${b.id}:${i}:${mode}`;
          if (!state.notesCache[key]) {
            const r = await api("/api/summarize", { method: "POST", body: { ...base, scope: "notes", book_id: b.id, chapter: i } });
            state.notesCache[key] = r.output;
            for (const k in totals) totals[k] += r.usage?.[k] || 0;
          }
          notes[i] = { title: b.chapters[i].title, notes: state.notesCache[key] };
          done++; setP(`Read ${done} of ${b.chapters.length} chapters…`);
        }
      };
      await Promise.all([worker(), worker(), worker()]);  // 3 at a time
      setP("Writing the final summary…");
      result = await api("/api/summarize", { method: "POST", body: { ...base, scope: "combine", book_id: b.id, notes } });
      for (const k in totals) result.usage[k] = (result.usage[k] || 0) + totals[k];
      result.usage.latency_ms = Date.now() - t0;
      done++; setP("Done");
      title = `${b.title} — whole-book summary`;
    }
    recordUsage("summarize", result.usage);
    const out = $("#sumOutput");
    if ($(".empty", out)) out.innerHTML = "";
    out.prepend(outputCard({ title, output: result.output, result, feature: "summarize", filename: "summary.md" }));
  } catch (e) { showError(e); }
  finally { btn.disabled = false; setTimeout(() => prog.classList.add("hidden"), 800); }
}

function setupSummarize() {
  const sync = () => {
    const s = $("#sumScope").value;
    $("#sumChapterWrap").classList.toggle("hidden", s !== "chapter");
    $("#sumTextWrap").classList.toggle("hidden", s !== "text");
    updateSumMeter();
  };
  $("#sumScope").onchange = sync;
  $("#sumChapter").onchange = updateSumMeter;
  $("#sumText").oninput = updateSumMeter;
  $("#runSummarize").onclick = runSummarize;
  sync();
}

// ================================================================ chat (multi-turn, streaming, sources)
const saveConvos = () => store.set("convos", state.convos.slice(0, 50));

function newConvo() {
  const c = { id: uid(), title: "New chat", bookId: state.activeBook, messages: [], updated: Date.now() };
  state.convos.unshift(c);
  state.activeConvo = c.id;
  saveConvos(); renderConvos(); renderMessages();
}
const currentConvo = () => state.convos.find((c) => c.id === state.activeConvo);

function renderConvos() {
  $("#convos").innerHTML = state.convos.map((c) => `<div class="convo ${c.id === state.activeConvo ? "active" : ""}" data-id="${c.id}">
    <span title="${esc(c.title)}">${esc(c.title)}</span><button title="Delete chat">✕</button></div>`).join("");
  $$(".convo").forEach((el) => {
    el.onclick = () => { state.activeConvo = el.dataset.id; renderConvos(); renderMessages(); };
    $("button", el).onclick = (e) => {
      e.stopPropagation();
      state.convos = state.convos.filter((c) => c.id !== el.dataset.id);
      if (state.activeConvo === el.dataset.id) state.activeConvo = state.convos[0]?.id;
      saveConvos(); if (!state.activeConvo) newConvo(); else { renderConvos(); renderMessages(); }
    };
  });
}

function messageEl(m, i) {
  const el = document.createElement("div");
  el.className = `msg ${m.role}${m.error ? " error" : ""}`;
  if (m.role === "user") { el.textContent = m.content; return el; }
  el.innerHTML = `<div class="md body">${md(m.content)}</div>
    ${m.sources?.length ? `<div class="sources">${m.sources.map((s, j) => `<button class="src" data-j="${j}" title="Show passage">${s.tag} · ${esc(s.label)}</button>`).join("")}</div><div class="src-slot"></div>` : ""}
    <div class="msg-tools">
      <button data-act="copy">📋 Copy</button>
      <button data-act="up" class="${m.rating === 5 ? "on" : ""}">👍</button>
      <button data-act="down" class="${m.rating === 1 ? "on" : ""}">👎</button>
      ${i === currentConvo().messages.length - 1 ? `<button data-act="regen">↻ Regenerate</button>` : ""}
      <span>${usageLine(m.usage, { mode: m.mode, version: m.prompt_version })}</span>
    </div>`;
  $$(".src", el).forEach((b) => b.onclick = () => {
    const s = m.sources[+b.dataset.j], slot = $(".src-slot", el);
    slot.innerHTML = slot.dataset.open === b.dataset.j ? "" : `<div class="src-text"><b>${esc(s.tag)} · ${esc(s.label)}</b>\n${esc(s.text)}</div>`;
    slot.dataset.open = slot.dataset.open === b.dataset.j ? "" : b.dataset.j;
  });
  $('[data-act="copy"]', el).onclick = () => copyText(m.content);
  const rate = (r) => { m.rating = r; saveConvos(); renderMessages();
    saveFeedback({ feature: "qa", prompt_version: m.prompt_version, rating: r, output_id: m.output_id, output_excerpt: m.content.slice(0, 500), comment: "" }); };
  $('[data-act="up"]', el).onclick = () => rate(5);
  $('[data-act="down"]', el).onclick = () => rate(1);
  const regen = $('[data-act="regen"]', el);
  if (regen) regen.onclick = () => { currentConvo().messages.pop(); sendChat(null); };
  return el;
}

function renderMessages() {
  const c = currentConvo(), box = $("#messages");
  $("#chatTitle").textContent = c.title;
  const b = state.books[c.bookId];
  $("#chatScopeLabel").textContent = b ? ` — about “${b.title}”` : " — general chat";
  box.innerHTML = "";
  if (!c.messages.length) {
    box.innerHTML = `<div class="welcome"><div style="font-size:2rem">💬</div><p>${state.activeBook ? `Ask anything about <b>${esc(state.books[state.activeBook]?.title)}</b>. Answers cite the passages they come from — click a tag to read it.` : "No book selected: this is a general chat. Pick a book at the top to chat with it."}</p></div>`;
  }
  c.messages.forEach((m, i) => box.append(messageEl(m, i)));
  box.scrollTop = box.scrollHeight;
  renderSuggestions();
}

function renderSuggestions() {
  const c = currentConvo(), b = state.books[state.activeBook];
  const qs = b ? ["Who are the main characters?", "What is the main conflict?", "Summarize the first chapter in 3 bullets", "What are the key themes?", "How does it end?"]
    : ["Explain tokens in simple words", "Write a haiku about books"];
  $("#suggestions").innerHTML = c && !c.messages.length ? qs.map((q) => `<button class="chip">${esc(q)}</button>`).join("") : "";
  $$("#suggestions .chip").forEach((ch) => ch.onclick = () => { $("#chatInput").value = ch.textContent; sendChat(); });
}

async function sendChat(e) {
  e?.preventDefault?.();
  const input = $("#chatInput"), c = currentConvo();
  const text = input.value.trim();
  if (e !== null) {           // null = regenerate (reuse last user message)
    if (!text) return;
    if (c.bookId !== state.activeBook && c.messages.length) { newConvo(); return sendChatWith(text); }
    c.bookId = state.activeBook;
    input.value = ""; updateChatTokens();
    c.messages.push({ role: "user", content: text });
    if (c.title === "New chat") c.title = text.slice(0, 40);
  }
  return streamAnswer(c);
}
function sendChatWith(text) { $("#chatInput").value = text; return sendChat(); }

async function streamAnswer(c) {
  const msg = { role: "assistant", content: "", sources: [], usage: null };
  c.messages.push(msg); c.updated = Date.now();
  renderConvos(); renderMessages();
  const bodyEl = () => $("#messages").lastElementChild;
  bodyEl().classList.add("typing");
  $("#sendBtn").classList.add("hidden"); $("#stopBtn").classList.remove("hidden");
  state.chatAbort = new AbortController();
  const chapterVal = $("#chatChapter").value;
  try {
    const res = await api("/api/chat", { method: "POST", stream: true, signal: state.chatAbort.signal, body: {
      book_id: c.bookId || null, chapter: chapterVal === "" ? null : +chapterVal, model: model(),
      prompt_version: "auto", messages: c.messages.slice(0, -1).filter((m) => !m.error).map(({ role, content }) => ({ role, content })) } });
    const reader = res.body.getReader(), dec = new TextDecoder();
    let buf = "", lastPaint = 0;
    const paint = (force) => {
      if (!force && Date.now() - lastPaint < 50) return;
      lastPaint = Date.now();
      const el = bodyEl(); $(".body", el).innerHTML = md(msg.content);
      const box = $("#messages"); box.scrollTop = box.scrollHeight;
    };
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });
      let cut;
      while ((cut = buf.indexOf("\n\n")) >= 0) {
        const raw = buf.slice(0, cut); buf = buf.slice(cut + 2);
        const ev = raw.match(/^event: (.*)$/m)?.[1], data = JSON.parse(raw.match(/^data: (.*)$/m)?.[1] || "{}");
        if (ev === "meta") { Object.assign(msg, { sources: data.sources, prompt_version: data.prompt_version, output_id: data.output_id }); }
        else if (ev === "delta") { msg.content += data.t; paint(); }
        else if (ev === "done") { msg.usage = data.usage; msg.mode = data.mode; recordUsage("qa", data.usage); }
        else if (ev === "error") { throw new AppError(data.code, data.message, data.hint); }
      }
    }
  } catch (e) {
    if (e.name === "AbortError") msg.content += "\n\n_(stopped)_";
    else { msg.error = true; msg.content = (msg.content ? msg.content + "\n\n" : "") + `⚠️ **${e.message}** ${e.hint || ""}`; showError(e); }
  } finally {
    state.chatAbort = null;
    $("#sendBtn").classList.remove("hidden"); $("#stopBtn").classList.add("hidden");
    saveConvos(); renderMessages();
  }
}

const updateChatTokens = debounce(async () => {
  const t = $("#chatInput").value;
  if (!t) { $("#chatTokens").textContent = "0 tokens"; return; }
  try { const r = await api("/api/tokens", { method: "POST", body: { text: t, model: model() } }); $("#chatTokens").textContent = `${fmt(r.tokens)} tokens`; } catch { /* ignore */ }
}, 250);

function setupChat() {
  $("#chatForm").onsubmit = sendChat;
  $("#chatInput").addEventListener("keydown", (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendChat(e); } });
  $("#chatInput").oninput = updateChatTokens;
  $("#stopBtn").onclick = () => state.chatAbort?.abort();
  $("#newChat").onclick = newConvo;
  state.activeConvo = state.convos[0]?.id;
  if (!state.activeConvo) newConvo(); else { renderConvos(); renderMessages(); }
}

// ================================================================ create
const TYPES = [
  ["study_notes", "📒", "Study notes"], ["quiz", "❓", "Quiz"], ["flashcards", "🃏", "Flashcards"],
  ["blog_post", "📰", "Blog post"], ["social_thread", "🧵", "Social thread"], ["newsletter", "✉️", "Newsletter"],
  ["discussion_questions", "🗣️", "Book club Qs"], ["characters", "🎭", "Characters"], ["timeline", "🕰️", "Timeline"],
  ["lesson_plan", "🎓", "Lesson plan"], ["custom", "🛠️", "Custom"],
];

async function runGenerate() {
  const src = $("#genSource").value, btn = $("#runGenerate");
  if (["book", "chapter", "topic"].includes(src) && needBook()) return;
  const body = { content_type: state.genType, tone: $("#genTone").value, audience: $("#genAudience").value,
    extra: $("#genExtra").value, prompt_version: $("#genVersion").value, model: model() };
  if (src !== "free" && src !== "text") body.book_id = state.activeBook;
  if (src === "chapter") body.chapter = +$("#genChapter").value;
  if (src === "topic" || src === "free") body.topic = $("#genTopic").value;
  if (src === "text") body.text = $("#genText").value;
  btn.disabled = true; btn.textContent = "Creating…";
  try {
    const r = await api("/api/generate", { method: "POST", body });
    recordUsage("generate", r.usage);
    const label = TYPES.find((t) => t[0] === state.genType)[2];
    const out = $("#genOutput");
    if ($(".empty", out)) out.innerHTML = "";
    out.prepend(outputCard({ title: label, output: r.output, result: r, feature: "generate", filename: `${state.genType}.md` }));
  } catch (e) { showError(e); }
  finally { btn.disabled = false; btn.textContent = "Create"; }
}

function setupCreate() {
  $("#typeGrid").innerHTML = TYPES.map(([k, icon, label]) => `<button class="type-btn ${k === state.genType ? "active" : ""}" data-k="${k}"><span>${icon}</span>${label}</button>`).join("");
  $$(".type-btn").forEach((b) => b.onclick = () => { state.genType = b.dataset.k; $$(".type-btn").forEach((x) => x.classList.toggle("active", x === b)); });
  const sync = () => {
    const s = $("#genSource").value;
    $("#genChapterWrap").classList.toggle("hidden", s !== "chapter");
    $("#genTopicWrap").classList.toggle("hidden", !["topic", "free"].includes(s));
    $("#genTextWrap").classList.toggle("hidden", s !== "text");
  };
  $("#genSource").onchange = sync; sync();
  $("#runGenerate").onclick = runGenerate;
}

// ================================================================ prompt lab
async function loadLab() {
  try {
    const [fb, cat] = await Promise.all([api("/api/feedback"), state.catalog || api("/api/prompts")]);
    state.catalog = cat;
    const rows = fb.by_version;
    const local = store.get("feedbackLog", []);
    const best = {};
    rows.forEach((r) => { if (!best[r.feature] || r.avg_rating > best[r.feature].avg_rating) best[r.feature] = r; });
    $("#ratingTable").innerHTML = rows.length ? `<div class="table-wrap"><table class="data"><tr><th>Feature</th><th>Prompt</th><th>Ratings</th><th>Average</th><th>% happy (4–5★)</th><th></th></tr>
      ${rows.map((r) => `<tr><td>${r.feature}</td><td>${r.prompt_version || "—"} ${esc(cat.features[r.feature]?.[r.prompt_version] || "")}</td><td>${r.n}</td>
      <td>${"★".repeat(Math.round(r.avg_rating))} ${r.avg_rating.toFixed(2)}</td><td>${Math.round((r.positive / r.n) * 100)}%</td>
      <td>${best[r.feature] === r && rows.filter((x) => x.feature === r.feature).length > 1 ? '<span class="winner">🏆 leading</span>' : ""}</td></tr>`).join("")}</table></div>
      <p class="muted">Tip: wait for 20+ ratings per version before deciding. This browser also keeps ${local.length} rating(s) locally.</p>`
      : `<p class="muted">No ratings on the server yet${local.length ? ` (this browser has ${local.length} saved locally — export them below)` : ""}. Rate some outputs with ★ or 👍/👎.</p>`;
    $("#promptViewer").innerHTML = Object.entries(cat.prompts).map(([f, versions]) =>
      `<h3>${f}</h3>` + Object.entries(versions).map(([v, p]) => `<b>${v} – ${esc(p.label)}</b>
      <div class="prompt-box">SYSTEM: ${esc(p.system)}${p.user ? `\n\nUSER: ${esc(p.user)}` : ""}</div>`).join("")).join("");
  } catch (e) { showError(e); }
}

async function runCompare() {
  const src = $("#cmpSource").value, btn = $("#runCompare");
  const s = { length: "short", style: $("#cmpStyle").value, model: model() };
  if (src === "chapter") { if (needBook()) return; Object.assign(s, { book_id: state.activeBook, scope: "chapter", chapter: +$("#cmpChapter").value }); }
  else Object.assign(s, { scope: "text", text: $("#cmpText").value });
  btn.disabled = true; btn.textContent = "Running both prompts…";
  try {
    const r = await api("/api/compare", { method: "POST", body: { feature: "summarize", summarize: s } });
    if (r.v1.mode === "demo") toast("Demo mode gives identical outputs. Add an API key for a real comparison.", { error: true });
    const order = Math.random() < 0.5 ? ["v1", "v2"] : ["v2", "v1"];
    const box = $("#cmpOutput");
    box.innerHTML = order.map((v, i) => `<div class="out-card"><div class="out-head"><b>Option ${"AB"[i]}</b><div class="meta reveal" data-v="${v}"></div></div>
      <div class="out-body md">${md(r[v].output)}</div><div class="out-foot"><button class="btn primary small" data-pick="${i}">👈 ${"AB"[i]} is better</button></div></div>`).join("") +
      `<div style="grid-column:1/-1;text-align:center"><button class="btn small ghost" data-pick="tie">They're equal</button></div>`;
    recordUsage("summarize", r.v1.usage); recordUsage("summarize", r.v2.usage);
    $$("[data-pick]", box).forEach((b) => b.onclick = async () => {
      const pick = b.dataset.pick;
      await Promise.all(order.map((v, i) => saveFeedback({ feature: "summarize", prompt_version: v, rating: pick === "tie" ? 3 : (+pick === i ? 5 : 2),
        comment: "blind compare", output_id: r[v].output_id, output_excerpt: r[v].output.slice(0, 300) })));
      $$(".reveal", box).forEach((m) => m.textContent = `was prompt ${m.dataset.v} (${state.catalog?.features.summarize[m.dataset.v] || ""})`);
      $$("[data-pick]", box).forEach((x) => x.disabled = true);
      toast("Vote saved – versions revealed"); loadLab();
    });
  } catch (e) { showError(e); }
  finally { btn.disabled = false; btn.textContent = "Run blind compare"; }
}

function setupLab() {
  $("#refreshLab").onclick = loadLab;
  $("#runCompare").onclick = runCompare;
  $("#cmpSource").onchange = () => {
    const t = $("#cmpSource").value === "text";
    $("#cmpText").classList.toggle("hidden", !t); $("#cmpChapterWrap").classList.toggle("hidden", t);
  };
  $("#exportFeedback").onclick = () => {
    const log = store.get("feedbackLog", []);
    if (!log.length) return toast("No feedback saved in this browser yet.");
    const cols = ["ts", "feature", "prompt_version", "rating", "comment", "output_id", "output_excerpt"];
    const q = (v) => `"${String(v ?? "").replace(/"/g, '""').replace(/\n/g, " ")}"`;
    download("feedback.csv", [cols.join(","), ...log.map((r) => cols.map((c) => q(c === "ts" ? new Date(r.ts).toISOString() : r[c])).join(","))].join("\n"), "text/csv");
  };
  const fill = () => $$(".version-select").forEach((s) => s.innerHTML =
    `<option value="auto">Auto (A/B test v1 vs v2)</option><option value="v1">v1 – Baseline</option><option value="v2">v2 – Improved</option>`);
  fill();
}

// ================================================================ usage
function bars(rows, label, value, fmtv) {
  const max = Math.max(...rows.map((r) => r[value] || 0), 1);
  return rows.length ? `<div class="bars">${rows.map((r) => `<div class="bar-row"><span>${esc(r[label])}</span>
    <div class="bar-track"><div class="bar-fill" style="width:${((r[value] || 0) / max) * 100}%"></div></div><span class="num">${fmtv(r)}</span></div>`).join("")}</div>`
    : `<p class="muted">No calls yet.</p>`;
}

async function loadUsage() {
  try {
    const u = await api("/api/usage"), t = u.totals;
    const local = store.get("usageLog", []);
    const lc = local.reduce((a, r) => ({ tokens: a.tokens + (r.tokens || 0), cost: a.cost + (r.cost || 0) }), { tokens: 0, cost: 0 });
    const tiles = [
      ["AI calls", fmt(t.calls)], ["Tokens", fmt(t.prompt_tokens + t.completion_tokens)], ["Cost", money(t.cost)],
      ["Avg response", `${(t.avg_latency_ms / 1000).toFixed(1)}s`], ["Errors", fmt(t.errors)],
      ["Today", money(u.cost_today) + (u.daily_budget ? ` / $${u.daily_budget}` : "")],
      ["This browser (all time)", `${fmt(lc.tokens)} tok · ${money(lc.cost)}`],
    ];
    $("#usageTiles").innerHTML = tiles.map(([k, v]) => `<div class="tile"><small>${k}</small><b>${v}</b></div>`).join("");
    $("#usageFeatures").innerHTML = bars(u.by_feature, "feature", "tokens", (r) => `${fmt(r.tokens)} · ${money(r.cost)}`);
    $("#usageDays").innerHTML = bars(u.by_day, "day", "tokens", (r) => `${fmt(r.tokens)} tok`);
    $("#usageRecent").innerHTML = u.recent.length ? `<table class="data"><tr><th>Time</th><th>Feature</th><th>Model</th><th>In</th><th>Out</th><th>Cost</th><th>Time</th><th>Status</th></tr>
      ${u.recent.map((r) => `<tr><td>${new Date(r.ts * 1000).toLocaleTimeString()}</td><td>${r.feature}</td><td>${r.model}</td><td>${fmt(r.prompt_tokens)}</td>
      <td>${fmt(r.completion_tokens)}</td><td>${money(r.cost)}</td><td>${r.latency_ms} ms</td><td>${r.ok ? "✅" : "❌ " + esc(r.error)}</td></tr>`).join("")}</table>`
      : `<p class="muted">No AI calls yet. In Demo mode nothing is sent to OpenAI, so nothing is logged here.</p>`;
  } catch (e) { showError(e); }
}

function setupUsage() {
  $("#refreshUsage").onclick = loadUsage;
  $("#clearUsage").onclick = async () => { if (confirm("Clear the server's usage log?")) { await api("/api/usage", { method: "DELETE" }); loadUsage(); } };
  $("#calcText").oninput = debounce(async () => {
    const text = $("#calcText").value;
    try {
      const r = await api("/api/tokens", { method: "POST", body: { text, model: model(), expected_output_tokens: 0 } });
      $("#calcOut").innerHTML = `<b>${fmt(r.tokens)}</b> tokens · ${fmt(r.words)} words · ${fmt(r.chars)} characters · input cost ≈ ${money(r.estimated_cost_usd)} on ${r.model} (${r.tokenizer})`;
    } catch (e) { showError(e); }
  });
}

// ================================================================ start
document.addEventListener("DOMContentLoaded", async () => {
  setupSettings(); setupTabs(); setupLibrary(); setupSummarize(); setupChat(); setupCreate(); setupLab(); setupUsage();
  await loadHealth();
  await loadBooks();
  renderMessages();
});
