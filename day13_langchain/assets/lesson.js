(() => {
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const sleep = ms => new Promise(r => setTimeout(r, ms));
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ---------- 3D tilt + flip-in for cards ---------- */
function cardFx(sel) {
  const els = $$(sel);
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) return;
    e.target.classList.add('in');
    setTimeout(() => e.target.classList.add('ready'), 1400);
    io.unobserve(e.target);
  }), { threshold: .15 });
  els.forEach((el, i) => {
    el.style.setProperty('--i', i % 8);
    io.observe(el);
    el.addEventListener('pointermove', ev => {
      if (!el.classList.contains('ready')) return;
      const r = el.getBoundingClientRect();
      const x = (ev.clientX - r.left) / r.width - .5, y = (ev.clientY - r.top) / r.height - .5;
      el.style.transform = `rotateY(${x * 16}deg) rotateX(${-y * 16}deg) translateZ(10px)`;
    });
    el.addEventListener('pointerleave', () => { el.style.transform = ''; });
  });
}

/* ---------- index page ---------- */
const cat = $('#catalog');
if (cat) {
  const C = JSON.parse(cat.textContent);
  const groups = [];
  C.forEach(l => { let g = groups.find(g => g.name === l.group); if (!g) groups.push(g = { name: l.group, items: [] }); g.items.push(l); });
  const colors = ['#3b82f6', '#16a34a', '#f97316', '#8b5cf6', '#ec4899', '#0d9488'];
  $('#app').innerHTML = `
  <div class="wrap">
    <div class="ihero">
      <div class="cubebox"><div class="cube3d"><div class="f1">🦜</div><div class="f2">🧠</div><div class="f3">🔗</div><div class="f4">📚</div><div class="f5">🛠️</div><div class="f6">🤖</div></div></div>
      <div><h1>LangChain for Kids 🦜</h1><p>${C.length} animated 3D lessons. Every example from the course, explained like a story: <b>What, Why, When, Where</b> and <b>How</b>.</p></div>
    </div>
    <div class="how">
      <div><b>🎬 1. Watch</b>A 3D story plays. Little messages 📨 fly between the characters. Drag the world to spin it!</div>
      <div><b>👀 2. Follow the code</b>The yellow line in the code lights up at the same moment.</div>
      <div><b>🃏 3. Read the 4W+H</b>What is it? Why use it? When? Where? How?</div>
      <div><b>🧪 4. Try & quiz</b>Run the real example, then answer a quick quiz.</div>
    </div>
    ${groups.map((g, gi) => `<div class="group"><h2>${g.name}</h2><div class="lgrid">${g.items.map(l => `
      <a class="lcard" href="${l.file}" style="--lc:${colors[gi % colors.length]}">
        <div class="le">${l.emoji}</div><div class="ln2">LESSON ${l.num}</div><h3>${l.title}</h3><p>${l.tagline}</p></a>`).join('')}</div></div>`).join('')}
    <p style="color:var(--muted);margin:40px 0;text-align:center">Code for every lesson lives in <code>day13_langchain/langchain_examples</code>. Run one with <code>python main.py</code>.</p>
  </div>`;
  cardFx('.lcard');
  return;
}

/* ---------- lesson page ---------- */
const lessonData = $('#lesson');
if (!lessonData) return; // the static index pages have no lesson data
const L = JSON.parse(lessonData.textContent);
const W5 = [
  ['what', '🤔', 'WHAT is it?', '#3b82f6'], ['why', '💡', 'WHY use it?', '#eab308'], ['when', '⏰', 'WHEN do I use it?', '#16a34a'],
  ['where', '📍', 'WHERE does it go?', '#ec4899'], ['how', '🛠️', 'HOW does it work?', '#8b5cf6']
];
const navA = (l, cls, label) => l ? `<a class="${cls}" href="${l.file}"><small>${label}</small><div><b>${l.emoji} ${l.title}</b></div></a>` : '<span></span>';
$('#app').innerHTML = `
<div class="wrap">
  <nav class="top"><a class="pill" href="${L.home}">🏠 All lessons</a><span class="sp"></span>
    ${L.prev ? `<a class="pill" href="${L.prev.file}">◀ ${L.prev.num}</a>` : ''}
    ${L.next ? `<a class="pill" href="${L.next.file}">${L.next.num} ▶</a>` : ''}</nav>
  <header class="hero"><div class="hero-emoji">${L.emoji}</div>
    <div><div class="num">Lesson ${L.num} of ${L.total}</div><h1>${L.title}</h1><p class="tagline">${L.tagline}</p></div></header>

  <div class="stage-grid">
    <div>
      <div class="viewport" id="vp"><div class="world" id="world"><div class="floor"></div></div><div class="hint">🖱️ drag to spin the world</div></div>
      <div class="narr"><div class="mascot">🤖</div><div class="bubble"><div class="stepno" id="stepno"></div><p class="say" id="say"></p></div></div>
      <div class="controls">
        <button class="btn" id="bRestart" title="Start again">⏮ Restart</button>
        <button class="btn" id="bPrev" title="Back (←)">◀ Back</button>
        <button class="btn main" id="bPlay" title="Play / pause (space)">⏸ Pause</button>
        <button class="btn" id="bNext" title="Next (→)">Next ▶</button>
        <div class="dots" id="dots"></div>
      </div>
    </div>
    <div class="code-card">
      <div class="code-head"><div class="lights"><i style="background:#ff5f57"></i><i style="background:#febc2e"></i><i style="background:#28c840"></i></div><span id="tabs"></span></div>
      <div class="code-body" id="codeBody"></div>
      <div class="code-note">📂 langchain_examples/${L.run.folder}</div>
    </div>
  </div>

  <section class="block"><div class="analogy"><div class="big">${L.analogy.emoji}</div><div><h3>Imagine this… ${L.analogy.title}</h3><p>${L.analogy.text}</p></div></div></section>

  <section class="block"><h2>🧭 The 4W + H</h2><div class="cards">
    ${W5.map(([k, e, t, c]) => `<div class="wcard" style="--wc:${c}"><div class="we">${e}</div><h3>${t}</h3><p>${L.w[k]}</p></div>`).join('')}
  </div></section>

  <section class="block"><div class="remember">🧠 <b>Remember:</b> ${L.remember}</div></section>

  <section class="block"><h2>🧪 Try it yourself</h2><div class="tryit">
    <div class="term"><span class="c"># 1. open the examples folder and switch on the virtual env</span><br>
      <span class="p">&gt;</span> cd D:\\getwork\\day13_langchain\\langchain_examples<br><span class="p">&gt;</span> .venv\\Scripts\\activate<br><br>
      <span class="c"># 2. go into this lesson's folder</span><br><span class="p">&gt;</span> cd ${esc(L.run.folder)}<br><br>
      <span class="c"># 3. run it (add your key to .env first)</span><br><span class="p">&gt;</span> ${esc(L.run.py)}</div>
    <div class="visits"><b>👉 What you should see</b>${L.run.visits.map(v => `<div class="visit"><div class="u">${esc(v[0])}</div><div class="o">→ ${esc(v[1])}</div></div>`).join('')}</div>
  </div></section>

  <section class="block"><h2>🎯 Quick quiz</h2><div class="quiz">
    ${L.quiz.map((q, qi) => `<div class="q" data-a="${q.a}"><h3>${qi + 1}. ${q.q}</h3><div class="opts">${q.o.map((o, i) => `<button class="opt" data-i="${i}">${o}</button>`).join('')}</div><div class="why">${q.why}</div></div>`).join('')}
  </div></section>

  <nav class="navfoot">${navA(L.prev, 'pv', '◀ Previous lesson')}${navA(L.next, 'nx', 'Next lesson ▶')}</nav>
</div>`;
document.title = `${L.num}. ${L.title} · LangChain for Kids`;
cardFx('.wcard');

/* quiz */
$$('.q').forEach(q => q.addEventListener('click', e => {
  const b = e.target.closest('.opt'); if (!b || q.classList.contains('answered')) return;
  const right = +b.dataset.i === +q.dataset.a;
  b.classList.add(right ? 'right' : 'wrong');
  if (!right) { setTimeout(() => b.classList.remove('wrong'), 450); return; }
  q.classList.add('answered');
  const r = b.getBoundingClientRect();
  for (let i = 0; i < 14; i++) {
    const s = document.createElement('span'); s.className = 'burst'; s.textContent = ['🎉', '⭐', '✨', '🎈'][i % 4];
    s.style.left = (r.left + r.width / 2) + 'px'; s.style.top = (r.top + r.height / 2) + 'px';
    const a = Math.random() * Math.PI * 2, d = 60 + Math.random() * 90;
    s.style.setProperty('--dx', Math.cos(a) * d + 'px'); s.style.setProperty('--dy', Math.sin(a) * d + 'px'); s.style.setProperty('--rot', (Math.random() * 360) + 'deg');
    document.body.appendChild(s); setTimeout(() => s.remove(), 1000);
  }
}));

/* ---------- code panel ---------- */
function hlPy(line) {
  const re = /(#.*$)|("""[^]*?"""|[rf]?"(?:[^"\\]|\\.)*"|[rf]?'(?:[^'\\]|\\.)*')|(@[\w.]+)|\b(from|import|def|async|await|return|class|if|not|in|is|else|elif|try|except|finally|with|as|for|while|yield|raise|None|True|False|lambda|and|or|del|pass)\b|\b(\d+(?:\.\d+)?)\b|\b(int|str|float|bool|dict|list|print|len|max)\b/g;
  let out = '', last = 0, m;
  while ((m = re.exec(line))) {
    out += esc(line.slice(last, m.index));
    const cls = m[1] ? 'c' : m[2] ? 's' : m[3] ? 'd' : m[4] ? 'k' : m[5] ? 'n' : 'b';
    out += `<span class="tk-${cls}">${esc(m[0])}</span>`; last = re.lastIndex;
  }
  return out + esc(line.slice(last));
}
const files = L.files.map(f => ({ ...f, lines: f.code.replace(/\n$/, '').split('\n') }));
let curFile = 0;
function showFile(i) {
  curFile = i;
  $('#tabs').innerHTML = files.map((f, j) => `<button class="tab ${j === i ? 'on' : ''}" data-f="${j}">${esc(f.name)}</button>`).join('');
  const py = files[i].name.endsWith('.py');
  $('#codeBody').innerHTML = files[i].lines.map((l, n) => `<div class="ln" data-n="${n}"><span class="no">${n + 1}</span><span>${(py ? hlPy(l) : esc(l)) || ' '}</span></div>`).join('');
}
$('#tabs').addEventListener('click', e => { const t = e.target.closest('.tab'); if (t) showFile(+t.dataset.f); });
showFile(0);
function highlight(finds) {
  if (!finds) { $$('.ln.hl').forEach(l => l.classList.remove('hl')); return; }
  finds = [].concat(finds);
  const fi = files.findIndex(f => f.lines.some(l => l.includes(finds[0])));
  if (fi < 0) return;
  if (fi !== curFile) showFile(fi);
  $$('.ln.hl').forEach(l => l.classList.remove('hl'));
  let first = null;
  files[fi].lines.forEach((l, n) => {
    if (finds.some(f => l.includes(f))) { const el = $(`.ln[data-n="${n}"]`); el.classList.add('hl'); if (!first) first = el; }
  });
  if (first) { const body = $('#codeBody'); body.scrollTo({ top: Math.max(0, first.offsetTop - body.clientHeight / 3), behavior: 'smooth' }); }
}

/* ---------- 3D world ---------- */
const vp = $('#vp'), world = $('#world');
const actors = {};
L.actors.forEach((a, i) => {
  const el = document.createElement('div');
  el.className = 'actor' + (a.hidden ? ' off' : '');
  el.style.setProperty('--c', a.color);
  el.style.transform = `translate3d(${a.x}px,0,${a.z}px)`;
  el.innerHTML = `<div class="pop"><div class="ringwrap"><div class="ring"></div></div>
    <div class="box">${['front', 'back', 'right', 'left', 'top'].map(f => `<div class="face ${f}">${f === 'front' || f === 'back' ? esc(a.name) : ''}</div>`).join('')}</div>
    <div class="char"><span style="animation-delay:${-i * .37}s">${a.emoji}</span></div><div class="fx"></div></div>`;
  world.appendChild(el);
  actors[a.id] = { ...a, el };
});
let rx = -38, ry = 0, userRy = 0, userRx = -38, drag = null, k = 1;
function fit() { k = Math.min(1.05, vp.clientWidth / 1060); }
addEventListener('resize', fit); fit();
vp.addEventListener('pointerdown', e => { drag = { x: e.clientX, y: e.clientY, ry: userRy, rx: userRx }; vp.setPointerCapture(e.pointerId); });
vp.addEventListener('pointermove', e => {
  if (!drag) return;
  userRy = Math.max(-60, Math.min(60, drag.ry + (e.clientX - drag.x) * .3));
  userRx = Math.max(-55, Math.min(-6, drag.rx - (e.clientY - drag.y) * .2));
});
vp.addEventListener('pointerup', () => drag = null);
vp.addEventListener('pointercancel', () => drag = null);
(function loop(t) {
  const sway = reduce || drag ? 0 : Math.sin(t / 2600) * 7;
  ry += (userRy + sway - ry) * .08; rx += (userRx - rx) * .08;
  world.style.setProperty('--ry', ry.toFixed(2) + 'deg');
  world.style.setProperty('--rx', rx.toFixed(2) + 'deg');
  world.style.setProperty('--k', k);
  requestAnimationFrame(loop);
})(0);

const METHOD_COLORS = { GET: '#3b82f6', POST: '#16a34a', PUT: '#f97316', PATCH: '#8b5cf6', DELETE: '#ef4444', WS: '#0d9488' };
function packetColor(label, from) {
  const m = String(label).match(/^([A-Z]+)\b/);
  if (m && METHOD_COLORS[m[1]]) return METHOD_COLORS[m[1]];
  if (/^[\[{"]/.test(label) || /^\d{3}\b/.test(label)) return '#d97706';
  return actors[from] ? actors[from].color : '#3b82f6';
}
function fly(from, to, label, color, token) {
  const A = actors[from], B = actors[to];
  if (!A || !B) return Promise.resolve();
  const p = document.createElement('div'); p.className = 'packet';
  p.innerHTML = `<div class="pk bb"><span style="--pc:${color || packetColor(label, from)}">${esc(label)}</span></div>`;
  world.appendChild(p);
  const dist = Math.hypot(B.x - A.x, B.z - A.z), dur = Math.max(900, Math.min(1700, dist * 2.4)) / (reduce ? 1.5 : 1);
  const h = 70 + dist * .18;
  return new Promise(res => {
    const t0 = performance.now();
    (function step(now) {
      if (token !== runToken) { p.remove(); return res(); }
      let t = Math.min(1, (now - t0) / dur); const e = t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
      const x = A.x + (B.x - A.x) * e, z = A.z + (B.z - A.z) * e, y = -110 - Math.sin(Math.PI * e) * h;
      p.style.transform = `translate3d(${x}px,${y}px,${z}px)`;
      if (t < 1) requestAnimationFrame(step); else { setTimeout(() => p.remove(), 120); res(); }
    })(t0);
  });
}
function setVis(id, on) { const a = actors[id]; if (a) a.el.classList.toggle('off', !on); }
function clearFx() {
  Object.values(actors).forEach(a => { a.el.classList.remove('glow', 'shake'); $('.fx', a.el).innerHTML = ''; });
  $$('.packet', world).forEach(p => p.remove());
}
function badge(id, text) {
  const a = actors[id]; if (!a) return;
  const cls = /^(✅|👍|🎉)/.test(text) ? 'ok' : /^(❌|🚫|⛔)/.test(text) ? 'err' : '';
  $('.fx', a.el).innerHTML = `<div class="badge ${cls}">${esc(text)}</div>`;
}

/* ---------- story player ---------- */
const steps = L.steps;
let cur = 0, playing = !reduce, runToken = 0;
$('#dots').innerHTML = steps.map((_, i) => `<button class="dot" data-i="${i}" aria-label="Step ${i + 1}"></button>`).join('');
async function doAct(a, tk) {
  if (a.code !== undefined) highlight(a.code);
  if (a.show) { [].concat(a.show).forEach(id => setVis(id, true)); await sleep(450); }
  if (a.hide) { [].concat(a.hide).forEach(id => setVis(id, false)); await sleep(450); }
  if (a.glow) [].concat(a.glow).forEach(id => actors[id] && actors[id].el.classList.add('glow'));
  if (a.unglow) [].concat(a.unglow).forEach(id => actors[id] && actors[id].el.classList.remove('glow'));
  if (a.send) { const [f, t] = a.send.split('>'); await fly(f.trim(), t.trim(), a.label || '', a.color, tk); }
  if (a.multi) await Promise.all(a.multi.map(m => { const [f, t] = m[0].split('>'); return fly(f.trim(), t.trim(), m[1], m[2], tk); }));
  if (a.badge) { badge(a.badge[0], a.badge[1]); await sleep(550); }
  if (a.shake) { [].concat(a.shake).forEach(id => actors[id] && actors[id].el.classList.add('shake')); await sleep(900); }
  if (a.wait) await sleep(a.wait);
}
async function go(i) {
  i = Math.max(0, Math.min(steps.length - 1, i));
  const tk = ++runToken; cur = i;
  clearFx(); highlight(null);
  L.actors.forEach(a => setVis(a.id, !a.hidden));
  for (let j = 0; j < i; j++) for (const a of steps[j].do || []) { if (a.show) [].concat(a.show).forEach(id => setVis(id, true)); if (a.hide) [].concat(a.hide).forEach(id => setVis(id, false)); }
  $('#stepno').textContent = `Step ${i + 1} of ${steps.length}`;
  const say = $('#say'); say.classList.remove('enter'); void say.offsetWidth; say.innerHTML = steps[i].say; say.classList.add('enter');
  $$('.dot').forEach((d, j) => { d.classList.toggle('on', j === i); d.classList.toggle('done', j < i); });
  await sleep(350);
  for (const a of steps[i].do || []) { if (tk !== runToken) return; await doAct(a, tk); }
  if (tk !== runToken) return;
  const read = Math.max(2600, steps[i].say.replace(/<[^>]+>/g, '').length * 55);
  await sleep(read);
  if (tk !== runToken || !playing) return;
  if (i < steps.length - 1) go(i + 1); else { playing = false; syncPlay(); }
}
function syncPlay() { $('#bPlay').textContent = playing ? '⏸ Pause' : (cur >= steps.length - 1 ? '🔁 Replay' : '▶ Play'); }
$('#bPlay').onclick = () => {
  if (playing) { playing = false; syncPlay(); return; }
  playing = true; syncPlay(); go(cur >= steps.length - 1 ? 0 : cur + 1);
};
$('#bNext').onclick = () => { playing = false; syncPlay(); go(cur + 1); };
$('#bPrev').onclick = () => { playing = false; syncPlay(); go(cur - 1); };
$('#bRestart').onclick = () => { playing = true; syncPlay(); go(0); };
$('#dots').onclick = e => { const d = e.target.closest('.dot'); if (d) { playing = false; syncPlay(); go(+d.dataset.i); } };
addEventListener('keydown', e => {
  if (e.target.closest('button,input,textarea')) return;
  if (e.key === 'ArrowRight') $('#bNext').click(); else if (e.key === 'ArrowLeft') $('#bPrev').click();
  else if (e.key === ' ') { e.preventDefault(); $('#bPlay').click(); }
});
syncPlay();
go(0);
})();
