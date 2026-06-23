/* World Cup 2026 Predictor - frontend logic (vanilla JS) */
"use strict";

var EU_TZ = "Europe/Brussels";
var state = { matches: [], filter: "all" };

/* ---------- helpers ---------- */
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

/* ---------- live EU clock ---------- */
function tickClock() {
  var now = new Date();
  var time = new Intl.DateTimeFormat("en-GB", {
    timeZone: EU_TZ, hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false
  }).format(now);
  var date = new Intl.DateTimeFormat("en-GB", {
    timeZone: EU_TZ, weekday: "long", day: "2-digit", month: "long"
  }).format(now);
  document.getElementById("clock").textContent = time;
  document.getElementById("clock-date").textContent = date + " · Central European Time";
  updateCountdowns();
}

function updateCountdowns() {
  var nodes = document.querySelectorAll("[data-kickoff]");
  var now = Date.now();
  nodes.forEach(function (n) {
    var ko = new Date(n.getAttribute("data-kickoff")).getTime();
    var diff = ko - now;
    if (diff <= 0) { n.textContent = ""; return; }
    var s = Math.floor(diff / 1000);
    var d = Math.floor(s / 86400); s -= d * 86400;
    var h = Math.floor(s / 3600); s -= h * 3600;
    var m = Math.floor(s / 60); s -= m * 60;
    var out = "in ";
    if (d > 0) out += d + "d ";
    out += String(h).padStart(2, "0") + ":" + String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0");
    n.textContent = out;
  });
}

/* ---------- matches ---------- */
function teamCol(name, label, iso) {
  var url = flagUrl(iso);
  var img = url
    ? '<img class="flag" src="' + url + '" alt="" loading="lazy" onerror="this.style.visibility=\'hidden\'">'
    : '<div class="flag"></div>';
  return '<div class="team-col">' + img +
         '<div class="team-name">' + esc(label || name || "TBD") + '</div></div>';
}

function matchCard(m) {
  var mid = m.mid_col;
  var middle;
  if (m.status === "upcoming") {
    middle =
      '<div class="mid-col">' +
        '<div class="kick-day">' + esc(m.kickoff.day) + '</div>' +
        '<div class="vs">VS</div>' +
        '<div class="kick-time">' + esc(m.kickoff.time) + '</div>' +
        '<div class="countdown" data-kickoff="' + m.kickoff.iso_utc + '"></div>' +
      '</div>';
  } else {
    var sc = m.score ? (m.score.home + " - " + m.score.away) : "vs";
    middle =
      '<div class="mid-col">' +
        '<div class="kick-day">' + esc(m.kickoff.day) + '</div>' +
        '<div class="score">' + esc(sc) + '</div>' +
        (m.status === "live" ? '<div class="countdown">in play</div>' : '') +
      '</div>';
  }

  var card = el(
    '<div class="match-card">' +
      '<div class="match-top">' +
        '<span class="stage-pill">' + esc(m.stage) + '</span>' +
        '<span class="status ' + m.status + '">' + m.status + '</span>' +
      '</div>' +
      '<div class="versus">' +
        teamCol(m.home, m.home_label, m.home_iso) +
        middle +
        teamCol(m.away, m.away_label, m.away_iso) +
      '</div>' +
      '<div class="venue">📍 ' + esc(m.venue) + ' · ' + esc(m.kickoff.time) + ' CET</div>' +
      '<button class="analyze-btn" ' + (m.analyzable ? '' : 'disabled') + '>' +
        '🤖 Analyze with <span>AI</span></button>' +
    '</div>'
  );

  var btn = card.querySelector(".analyze-btn");
  if (m.analyzable) {
    btn.addEventListener("click", function () { openAnalysis(m); });
  } else {
    btn.textContent = "Teams to be decided";
  }
  return card;
}

function renderMatches() {
  var wrap = document.getElementById("matches");
  var list = state.matches.filter(function (m) {
    return state.filter === "all" ? true : m.status === state.filter;
  });
  wrap.innerHTML = "";
  if (!list.length) {
    wrap.appendChild(el('<div class="loading">No matches in this category.</div>'));
    return;
  }
  list.forEach(function (m) { wrap.appendChild(matchCard(m)); });
  updateCountdowns();
}

function loadMatches() {
  return fetch("/api/matches").then(function (r) { return r.json(); })
    .then(function (data) { state.matches = data.matches; renderMatches(); })
    .catch(function (e) {
      document.getElementById("matches").innerHTML =
        '<div class="loading">Could not load matches: ' + esc(e.message) + '</div>';
    });
}

/* ---------- groups ---------- */
function groupCard(letter, rows) {
  var body = rows.map(function (r) {
    var qual = r.pos <= 2 ? " class=\"qualify\"" : "";
    return '<tr' + qual + '>' +
      '<td class="pos">' + r.pos + '</td>' +
      '<td class="left"><div class="team-cell">' +
        '<img class="flag-sm" src="' + flagUrl(r.iso, "w40") + '" alt="" onerror="this.style.visibility=\'hidden\'">' +
        '<span>' + esc(r.team) + '</span></div></td>' +
      '<td>' + r.Pld + '</td><td>' + r.W + '</td><td>' + r.D + '</td><td>' + r.L + '</td>' +
      '<td>' + r.GF + '</td><td>' + r.GA + '</td><td>' + (r.GD > 0 ? "+" + r.GD : r.GD) + '</td>' +
      '<td class="pts">' + r.Pts + '</td></tr>';
  }).join("");

  return el(
    '<div class="group-card">' +
      '<h3>Group ' + letter + ' <small>· top 2 advance</small></h3>' +
      '<table class="standings"><thead><tr>' +
        '<th></th><th class="left">Team</th><th>P</th><th>W</th><th>D</th><th>L</th>' +
        '<th>GF</th><th>GA</th><th>GD</th><th>Pts</th>' +
      '</tr></thead><tbody>' + body + '</tbody></table>' +
    '</div>'
  );
}

function loadGroups() {
  return fetch("/api/groups").then(function (r) { return r.json(); })
    .then(function (data) {
      var wrap = document.getElementById("groups");
      wrap.innerHTML = "";
      Object.keys(data.groups).forEach(function (g) {
        wrap.appendChild(groupCard(g, data.groups[g]));
      });
    })
    .catch(function (e) {
      document.getElementById("groups").innerHTML =
        '<div class="loading">Could not load groups: ' + esc(e.message) + '</div>';
    });
}

/* ---------- AI analysis modal ---------- */
function bar(label, value) {
  return '<div class="bar-row"><div class="lbl"><span>' + esc(label) +
    '</span><b>' + value + '%</b></div><div class="bar"><span style="width:' +
    Math.max(2, value) + '%"></span></div></div>';
}

function playerRow(p, kind) {
  return '<li><img class="flag-sm" src="' + flagUrl(window._isoOf(p.team), "w40") +
    '" alt="" onerror="this.style.visibility=\'hidden\'">' +
    '<span>' + esc(p.player) + '</span>' +
    '<span class="pp">' + p.prob + '%</span></li>';
}

function openAnalysis(m) {
  window._isoOf = function (t) {
    return t === m.home ? m.home_iso : (t === m.away ? m.away_iso : "un");
  };
  var backdrop = document.getElementById("modal-backdrop");
  var body = document.getElementById("modal-body");
  body.innerHTML = '<div class="loading">🤖 Analyzing ' + esc(m.home_label) +
    ' vs ' + esc(m.away_label) + '…</div>';
  backdrop.classList.add("open");

  fetch("/api/analyze?id=" + encodeURIComponent(m.id))
    .then(function (r) { return r.json(); })
    .then(function (a) {
      if (a.error) { body.innerHTML = '<div class="loading">' + esc(a.error) + '</div>'; return; }
      renderAnalysis(body, m, a);
    })
    .catch(function (e) {
      body.innerHTML = '<div class="loading">Analysis failed: ' + esc(e.message) + '</div>';
    });
}

function renderAnalysis(body, m, a) {
  var res = a.result, g = a.goals;

  var scorelines = a.top_scorelines.map(function (s, i) {
    var isBest = (s.home === a.best_fit_scoreline.home && s.away === a.best_fit_scoreline.away);
    return '<div class="scoreline' + (isBest ? ' best' : '') + '">' +
      '<div class="sc">' + s.home + '-' + s.away + '</div>' +
      '<div class="pr">' + s.prob + '%</div>' +
      (isBest ? '<div class="tagline">AI BEST FIT</div>' : '') +
      '</div>';
  }).join("");

  var scorers = a.scorers.map(function (p) { return playerRow(p, "g"); }).join("");
  var assists = a.assisters.map(function (p) { return playerRow(p, "a"); }).join("");

  body.innerHTML =
    '<div class="analysis-head">' +
      teamCol(m.home, m.home_label, m.home_iso) +
      '<div class="vs">VS</div>' +
      teamCol(m.away, m.away_label, m.away_iso) +
    '</div>' +
    '<div class="headline"><span class="ai-tag">AI PREDICTION:</span> ' + esc(a.headline) +
      '<br><small>Expected goals (xG): ' + esc(m.home_label) + ' ' + a.xg.home +
      ' — ' + a.xg.away + ' ' + esc(m.away_label) + ' · total ' + a.xg.total + '</small></div>' +

    '<div class="panel" style="margin-bottom:14px">' +
      '<h4>3 Most Probable Scorelines</h4>' +
      '<div class="scoreline-list">' + scorelines + '</div>' +
    '</div>' +

    '<div class="grid-2">' +
      '<div class="panel">' +
        '<h4>Match Result (1X2)</h4>' +
        bar(m.home_label + " win", res.home_win) +
        bar("Draw", res.draw) +
        bar(m.away_label + " win", res.away_win) +
      '</div>' +
      '<div class="panel">' +
        '<h4>Goals Markets</h4>' +
        bar("Over 1.5", g.over_1_5) +
        bar("Over 2.5", g.over_2_5) +
        bar("Over 3.5", g.over_3_5) +
        bar("Both teams to score", a.btts.yes) +
      '</div>' +
    '</div>' +

    '<div class="grid-2" style="margin-top:14px">' +
      '<div class="panel"><h4>⚽ Likely Goalscorers</h4><ul class="plist">' + scorers + '</ul></div>' +
      '<div class="panel"><h4>🅰 Likely Assists</h4><ul class="plist">' + assists + '</ul></div>' +
    '</div>' +

    '<div class="grid-2" style="margin-top:14px">' +
      '<div class="panel"><h4>Double Chance</h4>' +
        '<div class="kv"><span>' + esc(m.home_label) + ' or Draw</span><b>' + a.double_chance.home_or_draw + '%</b></div>' +
        '<div class="kv"><span>' + esc(m.away_label) + ' or Draw</span><b>' + a.double_chance.away_or_draw + '%</b></div>' +
        '<div class="kv"><span>Either team (no draw)</span><b>' + a.double_chance.home_or_away + '%</b></div>' +
      '</div>' +
      '<div class="panel"><h4>Clean Sheet</h4>' +
        '<div class="kv"><span>' + esc(m.home_label) + ' keeps clean sheet</span><b>' + a.clean_sheet.home + '%</b></div>' +
        '<div class="kv"><span>' + esc(m.away_label) + ' keeps clean sheet</span><b>' + a.clean_sheet.away + '%</b></div>' +
        '<div class="kv"><span>Under 2.5 goals</span><b>' + g.under_2_5 + '%</b></div>' +
      '</div>' +
    '</div>';
}

/* ---------- tabs / filters / wiring ---------- */
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
      renderMatches();
    });
  });
}

function setupModal() {
  var backdrop = document.getElementById("modal-backdrop");
  document.getElementById("modal-close").addEventListener("click", function () {
    backdrop.classList.remove("open");
  });
  backdrop.addEventListener("click", function (e) {
    if (e.target === backdrop) backdrop.classList.remove("open");
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") backdrop.classList.remove("open");
  });
}

function init() {
  setupTabs();
  setupModal();
  tickClock();
  setInterval(tickClock, 1000);
  loadMatches();
  loadGroups();
  loadInfo();
  // refresh data periodically so status / standings update in real time
  setInterval(function () { loadMatches(); loadGroups(); }, 30000);
}

function loadInfo() {
  fetch("/api/info").then(function (r) { return r.json(); }).then(function (d) {
    var el = document.getElementById("data-source");
    if (!el) return;
    if (d.matches_analyzed > 0) {
      el.innerHTML = "📊 Strength ratings built from <b>" +
        d.matches_analyzed.toLocaleString() + "</b> real international matches (" +
        esc(d.data_source) + "). Run <code>fetch_results.py</code> for the full 1872–2024 set.";
    } else {
      el.textContent = "Using baseline strength ratings.";
    }
  }).catch(function () {});
}

document.addEventListener("DOMContentLoaded", init);
