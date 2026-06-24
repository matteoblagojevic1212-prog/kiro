/* World Cup 2026 Predictor - frontend (vanilla JS) */
"use strict";

var state = { matches: [], filter: "upcoming" };

function flagUrl(iso, size) {
  size = size || "w160";
  if (!iso || iso === "un") return "";
  return "https://flagcdn.com/" + size + "/" + iso + ".png";
}
function el(html) {
  var t = document.createElement("template");
  t.innerHTML = html.trim();
  return t.content.firstChild;
}
function esc(s) {
  return String(s).replace(/[&<>"]/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
  });
}
function starSvg() {
  return '<svg class="star" viewBox="0 0 24 24" aria-hidden="true">' +
    '<path d="M12 2l2.9 6.2 6.8.8-5 4.6 1.3 6.7L12 17.8 5.9 21l1.3-6.7-5-4.6 6.8-.8z"/></svg>';
}
function weatherIcon(cat) {
  var c = '<circle cx="12" cy="12" r="5" fill="#f6c945"/>';
  var sun = '<g stroke="#f6c945" stroke-width="2" stroke-linecap="round">' +
    '<line x1="12" y1="1" x2="12" y2="4"/><line x1="12" y1="20" x2="12" y2="23"/>' +
    '<line x1="1" y1="12" x2="4" y2="12"/><line x1="20" y1="12" x2="23" y2="12"/>' +
    '<line x1="4" y1="4" x2="6" y2="6"/><line x1="18" y1="18" x2="20" y2="20"/>' +
    '<line x1="20" y1="4" x2="18" y2="6"/><line x1="6" y1="18" x2="4" y2="20"/></g>';
  var cloud = '<path d="M7 18h9a4 4 0 0 0 .4-8 5.5 5.5 0 0 0-10.6 1.3A3.6 3.6 0 0 0 7 18z" fill="#cfd3e0"/>';
  var inner = {
    sunny: sun + c,
    partly: sun + '<path d="M7 19h9a3.6 3.6 0 0 0 .3-7.2 5 5 0 0 0-9.6 1.2A3.3 3.3 0 0 0 7 19z" fill="#cfd3e0"/>',
    cloudy: cloud,
    fog: cloud + '<g stroke="#9aa3b2" stroke-width="1.6" stroke-linecap="round"><line x1="5" y1="21" x2="15" y2="21"/><line x1="9" y1="23" x2="19" y2="23"/></g>',
    rain: cloud + '<g stroke="#5aa9ff" stroke-width="2" stroke-linecap="round"><line x1="8" y1="20" x2="7" y2="23"/><line x1="12" y1="20" x2="11" y2="23"/><line x1="16" y1="20" x2="15" y2="23"/></g>',
    snow: cloud + '<g fill="#dbe6ff"><circle cx="8" cy="21" r="1"/><circle cx="12" cy="22" r="1"/><circle cx="16" cy="21" r="1"/></g>',
    thunder: cloud + '<path d="M12 19l-3 4h2.2l-1 3 3.8-4.5H11.8L12 19z" fill="#f6c945"/>'
  };
  return '<svg class="wx-icon" viewBox="0 0 24 24" aria-hidden="true">' + (inner[cat] || cloud) + '</svg>';
}

/* ----- live clock math (drives the Google-style minute + score) ----- */
function liveInfo(koMs, now, opts) {
  opts = opts || {};
  var el = (now - koMs) / 60000; // minutes since kickoff
  if (el < 0) return { phase: "pre" };
  if (el <= 45) { var a = Math.max(1, Math.ceil(el)); return { phase: "1h", min: a, label: a + "'" }; }
  if (el <= 47) return { phase: "1h", min: 45, label: "45+" + Math.ceil(el - 45) + "'" };
  if (el <= 62) return { phase: "ht", min: 45, label: "Half time" };
  if (el <= 107) { var m = Math.min(90, 45 + Math.ceil(el - 62)); return { phase: "2h", min: m, label: m + "'" }; }
  if (el <= 110) return { phase: "2h", min: 90, label: "90+" + Math.ceil(el - 107) + "'" };
  // After 90+stoppage: knockouts level go to extra time, then penalties
  if (opts.knockout && opts.level && opts.hasScore) {
    if (el <= 125) { var e = Math.min(120, 90 + Math.ceil(el - 110)); return { phase: "et", min: e, label: e + "' ET" }; }
    return { phase: "pens", min: 120, label: "Penalties" };
  }
  return { phase: "ft", min: 120, label: "FT" };
}
function scoreFromEvents(events, matchMinute) {
  var h = 0, a = 0;
  (events || []).forEach(function (e) {
    if (e.minute <= matchMinute) { if (e.team === "home") h++; else a++; }
  });
  return { home: h, away: a };
}


/* ----- per-second updates: countdowns + live minute/score ----- */
function tick() {
  var now = Date.now();
  document.querySelectorAll("[data-kickoff]").forEach(function (n) {
    var ko = new Date(n.getAttribute("data-kickoff")).getTime();
    var diff = ko - now;
    if (diff <= 0) { n.textContent = ""; return; }
    var s = Math.floor(diff / 1000);
    var d = Math.floor(s / 86400); s -= d * 86400;
    var h = Math.floor(s / 3600); s -= h * 3600;
    var mi = Math.floor(s / 60); s -= mi * 60;
    var out;
    if (d > 0) out = "in " + d + "d " + h + "h";
    else if (h > 0) out = "in " + h + "h " + mi + "m";
    else out = "in " + mi + "m " + String(s).padStart(2, "0") + "s";
    n.textContent = out;
  });
  state.matches.forEach(function (m) {
    if (m.status !== "live") return;
    var koMs = new Date(m.kickoff.iso_utc).getTime();
    var hasScore = !!(m.events && m.events.length) || !!m.live_real;
    var curScore = null;
    if (m.live_real && m.score) curScore = m.score;
    var minEl = document.getElementById("min-" + m.id);
    var scEl = document.getElementById("sc-" + m.id);
    // figure out the score first (needed for extra-time logic)
    var info = liveInfo(koMs, Date.now(), { knockout: !m.group });
    var sc = curScore || (m.events && m.events.length ? scoreFromEvents(m.events, info.min) : null);
    info = liveInfo(koMs, Date.now(), {
      knockout: !m.group, hasScore: hasScore,
      level: sc ? (sc.home === sc.away) : false
    });
    if (minEl) {
      var label;
      if ((m.live_detail && /half|ht\b/i.test(m.live_detail)) || info.phase === "ht") label = t("ht");
      else if (m.live_clock) label = m.live_clock;
      else label = info.label || "LIVE";
      minEl.textContent = label;
      minEl.className = "minute" + (/half/i.test(label) || info.phase === "ht" ? " ht" : "");
    }
    if (scEl && sc) scEl.textContent = sc.home + " - " + sc.away;
  });
}

/* ----- match card ----- */
function teamCol(name, label, iso) {
  var url = flagUrl(iso);
  var img = url
    ? '<img class="flag" src="' + url + '" alt="" loading="lazy" onerror="this.style.visibility=\'hidden\'">'
    : '<div class="flag"></div>';
  return '<div class="team-col">' + img +
    '<div class="team-name">' + esc(label || name || "TBD") + '</div></div>';
}

function midCol(m) {
  if (m.status === "upcoming") {
    return '<div class="mid-col">' +
      '<div class="kick-day">' + esc(m.kickoff.day) + '</div>' +
      '<div class="vs">VS</div>' +
      '<div class="kick-time">' + esc(m.kickoff.time) + '</div>' +
      '<div class="countdown" data-kickoff="' + m.kickoff.iso_utc + '"></div></div>';
  }
  if (m.status === "live") {
    var liveScore = (m.score) ? (m.score.home + " - " + m.score.away)
                              : (m.events && m.events.length ? "0 - 0" : "–");
    return '<div class="mid-col">' +
      '<div class="score" id="sc-' + m.id + '">' + liveScore + '</div>' +
      '<div class="minute" id="min-' + m.id + '">…</div></div>';
  }
  if (m.awaiting) {
    return '<div class="mid-col">' +
      '<div class="kick-day">' + esc(m.kickoff.day) + '</div>' +
      '<div class="vs">VS</div>' +
      '<div class="ft-badge">' + t("awaiting") + '</div></div>';
  }
  var sc = m.score ? (m.score.home + " - " + m.score.away) : "–";
  return '<div class="mid-col">' +
    '<div class="kick-day">' + esc(m.kickoff.day) + '</div>' +
    '<div class="score">' + esc(sc) + '</div>' +
    '<div class="ft-badge">' + t("ft") + '</div></div>';
}


function matchCard(m) {
  var statusText = t(m.status);
  var card = el(
    '<div class="match-card">' +
      '<div class="match-top">' +
        '<span class="stage-pill">' + esc(m.stage) + '</span>' +
        '<span class="status ' + m.status + '">' + statusText + '</span>' +
      '</div>' +
      '<div class="versus">' +
        teamCol(m.home, m.home_label, m.home_iso) +
        midCol(m) +
        teamCol(m.away, m.away_label, m.away_iso) +
      '</div>' +
      '<div class="venue">' + esc(m.venue) + ' · ' + esc(m.kickoff.time) + ' CET</div>' +
      '<button class="analyze-btn" ' + (m.analyzable ? '' : 'disabled') + '>' +
        starSvg() + '<span>' + t("analyse") + '</span></button>' +
    '</div>'
  );
  var btn = card.querySelector(".analyze-btn");
  if (m.analyzable) btn.addEventListener("click", function () { openAnalysis(m); });
  else btn.querySelector("span").textContent = t("tbd");
  return card;
}

function renderMatches() {
  var wrap = document.getElementById("matches");
  var list;
  if (state.search) {
    list = state.matches.filter(function (m) {
      return ((m.home_label + " " + m.away_label).toLowerCase()).indexOf(state.search) !== -1;
    });
  } else {
    list = state.matches.filter(function (m) { return m.status === state.filter; });
  }
  wrap.innerHTML = "";
  if (!list.length) {
    var msg = state.search ? 'No games found for "' + esc(state.search) + '".' : "No " + state.filter + " matches right now.";
    wrap.appendChild(el('<div class="loading">' + msg + '</div>'));
    return;
  }
  list.forEach(function (m) { wrap.appendChild(matchCard(m)); });
  tick();
}

function loadMatches() {
  return fetch("/api/matches").then(function (r) { return r.json(); })
    .then(function (data) { state.matches = data.matches; renderMatches(); })
    .catch(function (e) {
      document.getElementById("matches").innerHTML =
        '<div class="loading">Could not load matches: ' + esc(e.message) + '</div>';
    });
}


/* ----- groups ----- */
function groupCard(letter, rows) {
  var body = rows.map(function (r) {
    var qual = r.pos <= 2 ? ' class="qualify"' : "";
    return '<tr' + qual + '><td class="pos">' + r.pos + '</td>' +
      '<td class="left"><div class="team-cell">' +
        '<img class="flag-sm" src="' + flagUrl(r.iso, "w40") + '" alt="" onerror="this.style.visibility=\'hidden\'">' +
        '<span>' + esc(r.team) + '</span></div></td>' +
      '<td>' + r.Pld + '</td><td>' + r.W + '</td><td>' + r.D + '</td><td>' + r.L + '</td>' +
      '<td>' + r.GF + '</td><td>' + r.GA + '</td><td>' + (r.GD > 0 ? "+" + r.GD : r.GD) + '</td>' +
      '<td class="pts">' + r.Pts + '</td></tr>';
  }).join("");
  return el('<div class="group-card"><h3>Group ' + letter + ' <small>· top 2 advance</small></h3>' +
    '<table class="standings"><thead><tr><th></th><th class="left">Team</th>' +
    '<th>P</th><th>W</th><th>D</th><th>L</th><th>GF</th><th>GA</th><th>GD</th><th>Pts</th>' +
    '</tr></thead><tbody>' + body + '</tbody></table></div>');
}
function loadGroups() {
  return fetch("/api/groups").then(function (r) { return r.json(); }).then(function (data) {
    var wrap = document.getElementById("groups"); wrap.innerHTML = "";
    Object.keys(data.groups).forEach(function (g) { wrap.appendChild(groupCard(g, data.groups[g])); });
  }).catch(function (e) {
    document.getElementById("groups").innerHTML = '<div class="loading">Could not load groups: ' + esc(e.message) + '</div>';
  });
}

/* ----- analysis modal ----- */
function bar(label, value) {
  return '<div class="bar-row"><div class="lbl"><span>' + esc(label) + '</span><b>' + value +
    '%</b></div><div class="bar"><span style="width:' + Math.max(2, value) + '%"></span></div></div>';
}
function playerRow(p) {
  return '<li><img class="flag-sm" src="' + flagUrl(window._isoOf(p.team), "w40") +
    '" alt="" onerror="this.style.visibility=\'hidden\'"><span>' + esc(p.player) +
    '</span><span class="pp">' + p.prob + '%</span></li>';
}
function openAnalysis(m) {
  window._isoOf = function (t) { return t === m.home ? m.home_iso : (t === m.away ? m.away_iso : "un"); };
  var backdrop = document.getElementById("modal-backdrop");
  var body = document.getElementById("modal-body");
  body.innerHTML = '<div class="loading">Analysing ' + esc(m.home_label) + ' vs ' + esc(m.away_label) + '…</div>';
  backdrop.classList.add("open");
  document.body.classList.add("modal-open");
  fetch("/api/analyze?id=" + encodeURIComponent(m.id)).then(function (r) { return r.json(); })
    .then(function (a) {
      if (a.error) { body.innerHTML = '<div class="loading">' + esc(a.error) + '</div>'; return; }
      renderAnalysis(body, m, a);
    }).catch(function (e) { body.innerHTML = '<div class="loading">Analysis failed: ' + esc(e.message) + '</div>'; });
}


function renderAnalysis(body, m, a) {
  var res = a.result, g = a.goals, pred = a.prediction;
  var scorelines = a.top_scorelines.map(function (s) {
    var best = (s.home === pred.home && s.away === pred.away);
    return '<div class="scoreline' + (best ? ' best' : '') + '"><div class="sc">' + s.home + '-' + s.away +
      '</div><div class="pr">' + s.prob + '%</div>' + (best ? '<div class="tagline">' + t("likely") + '</div>' : '') + '</div>';
  }).join("");
  var scorers = a.scorers.map(playerRow).join("");
  var assists = a.assisters.map(playerRow).join("");
  function gl(line, over, under) {
    return (over >= under) ? bar(t("over") + " " + line, over) : bar(t("under") + " " + line, under);
  }
  var fh = a.form ? a.form.home : null, fa = a.form ? a.form.away : null;
  function badges(f) {
    if (!f || !f.last5 || !f.last5.length) return '<span class="note">' + t("norecent") + '</span>';
    return f.last5.map(function (x) {
      return '<span class="frm ' + x.res + '" title="vs ' + esc(x.opp) + ' ' + x.gf + '-' + x.ga + '">' + x.res + '</span>';
    }).join("");
  }
  function formPanel(label, f) {
    if (!f) return "";
    return '<div class="panel"><h4>' + esc(label) + ' · ' + t("form") + '</h4>' +
      '<div class="form-badges">' + badges(f) + '</div>' +
      '<div class="kv"><span>' + t("scored") + '</span><b>' + f.gf + '</b></div>' +
      '<div class="kv"><span>' + t("conceded") + '</span><b>' + f.ga + '</b></div></div>';
  }
  var formHtml = '<div class="grid-2" style="margin-top:14px">' +
    formPanel(m.home_label, fh) + formPanel(m.away_label, fa) + '</div>';

  var venueHtml = "";
  if (a.venue) {
    var w = a.weather, vi = a.venue_info || {};
    var wline = w
      ? (weatherIcon(w.cat) + ' <span>' + esc(w.desc) + " · " + Math.round(w.temp_max) + "° / " + Math.round(w.temp_min) + "°C</span>")
      : t("wxpending");
    venueHtml = '<div class="panel venue-panel" style="margin-top:14px"><h4>' + t("venue") + '</h4>' +
      '<div class="venue-stadium">' + esc(vi.stadium || a.venue) + '</div>' +
      '<div class="wx-line">' + wline + '</div></div>';
  }

  var winnerTxt = (a.winner === "Draw") ? t("draw") : (a.winner || t("draw"));
  var cl = a.confidence_label || "Medium";

  body.innerHTML =
    '<div class="analysis-head">' + teamCol(m.home, m.home_label, m.home_iso) +
      '<div class="vs">VS</div>' + teamCol(m.away, m.away_label, m.away_iso) + '</div>' +
    '<div class="predict-banner"><div class="predict-label">' + t("winner") + '</div>' +
      '<div class="predict-winner">' + esc(winnerTxt) + '</div>' +
      '<div class="predict-conf conf-' + cl.toLowerCase() + '">' + t("confidence") + ': ' + t(cl) + '</div></div>' +
    '<div class="panel" style="margin-bottom:14px"><h4>' + t("scores") + '</h4>' +
      '<div class="scoreline-list">' + scorelines + '</div></div>' +
    '<div class="grid-2"><div class="panel"><h4>' + t("result") + '</h4>' +
      bar(m.home_label + " " + t("win"), res.home_win) + bar(t("draw"), res.draw) + bar(m.away_label + " " + t("win"), res.away_win) +
      '</div><div class="panel"><h4>' + t("goals") + '</h4>' +
      gl("1.5", g.over_1_5, g.under_1_5) + gl("2.5", g.over_2_5, g.under_2_5) +
      bar(t("btts"), a.btts.yes) + '</div></div>' +
    formHtml +
    '<div class="grid-2" style="margin-top:14px"><div class="panel"><h4>' + t("scorers") + '</h4>' +
      '<ul class="plist">' + scorers + '</ul></div><div class="panel"><h4>' + t("assists") + '</h4>' +
      '<ul class="plist">' + assists + '</ul></div></div>' +
    venueHtml;
}

/* ----- wiring ----- */
function setupTabs() {
  document.querySelectorAll(".tab").forEach(function (t) {
    t.addEventListener("click", function () {
      document.querySelectorAll(".tab").forEach(function (x) { x.classList.remove("active"); });
      t.classList.add("active");
      var tab = t.getAttribute("data-tab");
      document.getElementById("view-matches").classList.toggle("active", tab === "matches");
      document.getElementById("view-groups").classList.toggle("active", tab === "groups");
      document.getElementById("filter-wrap").style.display = tab === "matches" ? "flex" : "none";
    });
  });
  document.querySelectorAll(".chip").forEach(function (c) {
    c.addEventListener("click", function () {
      document.querySelectorAll(".chip").forEach(function (x) { x.classList.remove("active"); });
      c.classList.add("active");
      state.filter = c.getAttribute("data-filter");
      var s = document.getElementById("search");
      if (s) s.value = "";
      state.search = "";
      renderMatches();
    });
  });
}

function setupSearch() {
  var s = document.getElementById("search");
  if (!s) return;
  s.addEventListener("input", function () {
    state.search = s.value.trim().toLowerCase();
    // searching applies to matches; make sure that view is showing
    if (state.search) {
      document.querySelectorAll(".tab").forEach(function (x) { x.classList.remove("active"); });
      var mt = document.querySelector('.tab[data-tab="matches"]');
      if (mt) mt.classList.add("active");
      document.getElementById("view-matches").classList.add("active");
      document.getElementById("view-groups").classList.remove("active");
    }
    renderMatches();
  });
}

function setupHeaderScroll() {
  var bar = document.querySelector(".topbar");
  if (!bar) return;
  var last = 0;
  window.addEventListener("scroll", function () {
    var y = window.scrollY || document.documentElement.scrollTop;
    if (y > last && y > 90) bar.classList.add("hidden");
    else bar.classList.remove("hidden");
    last = y;
  }, { passive: true });
}
function setupModal() {
  var b = document.getElementById("modal-backdrop");
  function close() { b.classList.remove("open"); document.body.classList.remove("modal-open"); }
  document.getElementById("modal-close").addEventListener("click", close);
  b.addEventListener("click", function (e) { if (e.target === b) close(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });
}
/* ----- menu: account (local) + language ----- */
function getUser() { try { return JSON.parse(localStorage.getItem("wc_user")); } catch (e) { return null; } }
function setUser(u) {
  if (u) localStorage.setItem("wc_user", JSON.stringify(u));
  else localStorage.removeItem("wc_user");
  renderAccount();
}
function renderAccount() {
  var el = document.getElementById("account-area");
  if (!el) return;
  var u = getUser();
  if (u) {
    el.innerHTML = '<div class="acct-signed">' + t("signed") + ' <b>' + esc(u.email || u.name) + '</b></div>' +
      '<button class="btn-line" id="signout-btn">' + t("signout") + '</button>';
    document.getElementById("signout-btn").onclick = function () { setUser(null); };
  } else {
    el.innerHTML =
      '<button class="btn-provider google" data-prov="Google">' + t("google") + '</button>' +
      '<button class="btn-provider apple" data-prov="Apple">' + t("apple") + '</button>' +
      '<div class="acct-or"></div>' +
      '<input class="acct-inp" id="acct-email" type="email" placeholder="' + t("email") + '" autocomplete="off">' +
      '<input class="acct-inp" id="acct-pass" type="password" placeholder="' + t("password") + '" autocomplete="off">' +
      '<button class="btn-line gold" id="acct-create">' + t("create") + '</button>';
    el.querySelectorAll(".btn-provider").forEach(function (b) {
      b.onclick = function () { setUser({ name: b.getAttribute("data-prov") + " user", via: b.getAttribute("data-prov") }); };
    });
    document.getElementById("acct-create").onclick = function () {
      var em = document.getElementById("acct-email").value.trim();
      if (em) setUser({ email: em });
    };
  }
}
function renderLangs() {
  var el = document.getElementById("lang-list");
  if (!el) return;
  el.innerHTML = LANGS.map(function (l) {
    return '<button class="lang-item' + (l[0] === getLang() ? " active" : "") + '" data-lang="' + l[0] + '">' + l[1] + '</button>';
  }).join("");
  el.querySelectorAll(".lang-item").forEach(function (b) {
    b.onclick = function () { setLang(b.getAttribute("data-lang")); renderLangs(); };
  });
}
function setupMenu() {
  var btn = document.getElementById("menu-btn"), dr = document.getElementById("drawer"), ov = document.getElementById("drawer-overlay");
  function open() { dr.classList.add("open"); ov.classList.add("open"); document.body.classList.add("modal-open"); }
  function close() { dr.classList.remove("open"); ov.classList.remove("open"); document.body.classList.remove("modal-open"); }
  btn.onclick = open; ov.onclick = close;
  document.getElementById("drawer-close").onclick = close;
  renderAccount(); renderLangs();
}

window._onLangChange = function () { renderAccount(); renderLangs(); renderMatches(); };

function init() {
  setupTabs(); setupModal(); setupSearch(); setupHeaderScroll(); setupMenu();
  applyLang();
  loadMatches(); loadGroups();
  setInterval(tick, 1000);
  setInterval(function () { loadMatches(); loadGroups(); }, 20000);
}
document.addEventListener("DOMContentLoaded", init);
