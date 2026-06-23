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

/* ----- live clock math (drives the Google-style minute + score) ----- */
function liveInfo(koMs, now) {
  var el = (now - koMs) / 60000; // minutes since kickoff
  if (el < 0) return { phase: "pre" };
  if (el <= 45) return { phase: "1h", min: Math.max(1, Math.ceil(el)), label: Math.max(1, Math.ceil(el)) + "'" };
  if (el <= 60) return { phase: "ht", min: 45, label: "HT" };
  if (el <= 105) { var m = Math.min(90, 45 + Math.ceil(el - 60)); return { phase: "2h", min: m, label: m + "'" }; }
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
    n.textContent = "in " + (d > 0 ? d + "d " : "") +
      String(h).padStart(2, "0") + ":" + String(mi).padStart(2, "0") + ":" + String(s).padStart(2, "0");
  });
  state.matches.forEach(function (m) {
    if (m.status !== "live") return;
    var koMs = new Date(m.kickoff.iso_utc).getTime();
    var info = liveInfo(koMs, now);
    var minEl = document.getElementById("min-" + m.id);
    var scEl = document.getElementById("sc-" + m.id);
    if (minEl) {
      var label = (m.live_minute != null) ? (m.live_minute + "'") : (info.label || "LIVE");
      minEl.textContent = label;
      minEl.className = "minute" + (info.phase === "ht" ? " ht" : "");
    }
    if (scEl) {
      if (m.live_real && m.score) {
        scEl.textContent = m.score.home + " - " + m.score.away; // real feed
      } else if (m.events && m.events.length && info.min !== undefined) {
        var sc = scoreFromEvents(m.events, info.min);
        scEl.textContent = sc.home + " - " + sc.away;
      }
    }
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
      '<div class="ft-badge">awaiting score</div></div>';
  }
  var sc = m.score ? (m.score.home + " - " + m.score.away) : "–";
  return '<div class="mid-col">' +
    '<div class="kick-day">' + esc(m.kickoff.day) + '</div>' +
    '<div class="score">' + esc(sc) + '</div>' +
    '<div class="ft-badge">FULL TIME</div></div>';
}


function matchCard(m) {
  var statusText = m.status === "live" ? "LIVE" : m.status.toUpperCase();
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
        starSvg() + '<span>Analyse with AI</span></button>' +
    '</div>'
  );
  var btn = card.querySelector(".analyze-btn");
  if (m.analyzable) btn.addEventListener("click", function () { openAnalysis(m); });
  else btn.querySelector("span").textContent = "Teams to be decided";
  return card;
}

function renderMatches() {
  var wrap = document.getElementById("matches");
  var list = state.matches.filter(function (m) { return m.status === state.filter; });
  wrap.innerHTML = "";
  if (!list.length) {
    wrap.appendChild(el('<div class="loading">No ' + state.filter + ' matches right now.</div>'));
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
      '</div><div class="pr">' + s.prob + '%</div>' + (best ? '<div class="tagline">MOST LIKELY</div>' : '') + '</div>';
  }).join("");
  var scorers = a.scorers.map(playerRow).join("");
  var assists = a.assisters.map(playerRow).join("");

  var fh = a.form ? a.form.home : null, fa = a.form ? a.form.away : null;
  function badges(f) {
    if (!f || !f.last5 || !f.last5.length) return '<span class="note">no recent data</span>';
    return f.last5.map(function (x) {
      return '<span class="frm ' + x.res + '" title="vs ' + esc(x.opp) + ' ' + x.gf + '-' + x.ga + '">' + x.res + '</span>';
    }).join("");
  }
  function formPanel(label, f) {
    if (!f) return "";
    return '<div class="panel"><h4>' + esc(label) + ' · recent form</h4>' +
      '<div class="form-badges">' + badges(f) + '</div>' +
      '<div class="kv"><span>Avg scored</span><b>' + f.gf + '</b></div>' +
      '<div class="kv"><span>Avg conceded</span><b>' + f.ga + '</b></div></div>';
  }
  var formHtml = '<div class="grid-2" style="margin-top:14px">' +
    formPanel(m.home_label, fh) + formPanel(m.away_label, fa) + '</div>';

  body.innerHTML =
    '<div class="analysis-head">' + teamCol(m.home, m.home_label, m.home_iso) +
      '<div class="vs">VS</div>' + teamCol(m.away, m.away_label, m.away_iso) + '</div>' +
    '<div class="predict-banner"><div class="predict-label">MOST LIKELY SCORE</div>' +
      '<div class="predict-score">' + pred.home + ' – ' + pred.away + '</div>' +
      '<div class="predict-call">Goals lean: ' + pred.goals_call + ' (' + pred.goals_prob + '%)</div></div>' +
    '<div class="headline">' + esc(a.headline) +
      '<br><small>Expected goals (xG): ' + esc(m.home_label) + ' ' + a.xg.home + ' — ' + a.xg.away +
      ' ' + esc(m.away_label) + '</small></div>' +
    '<div class="panel" style="margin-bottom:14px"><h4>3 Most Probable Exact Scores</h4>' +
      '<div class="scoreline-list">' + scorelines + '</div>' +
      '<p class="note">Each exact score is just one outcome, so they don\'t add up to 100%. ' +
      'A low score can be "most likely" even when Over 2.5 is the more likely goals market — ' +
      'because Over 2.5 adds up many higher scores together.</p></div>' +
    '<div class="grid-2"><div class="panel"><h4>Match Result</h4>' +
      bar(m.home_label + " win", res.home_win) + bar("Draw", res.draw) + bar(m.away_label + " win", res.away_win) +
      '</div><div class="panel"><h4>Goals Markets</h4>' +
      bar("Over 1.5", g.over_1_5) + bar("Over 2.5", g.over_2_5) + bar("Over 3.5", g.over_3_5) +
      bar("Both teams score", a.btts.yes) + '</div></div>' +
    formHtml +
    '<div class="grid-2" style="margin-top:14px"><div class="panel"><h4>Likely Goalscorers</h4>' +
      '<ul class="plist">' + scorers + '</ul></div><div class="panel"><h4>Likely Assists</h4>' +
      '<ul class="plist">' + assists + '</ul></div></div>';
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
      renderMatches();
    });
  });
}
function setupModal() {
  var b = document.getElementById("modal-backdrop");
  document.getElementById("modal-close").addEventListener("click", function () { b.classList.remove("open"); });
  b.addEventListener("click", function (e) { if (e.target === b) b.classList.remove("open"); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") b.classList.remove("open"); });
}
function loadInfo() {
  fetch("/api/info").then(function (r) { return r.json(); }).then(function (d) {
    var el = document.getElementById("data-source");
    if (el && d.matches_analyzed > 0)
      el.innerHTML = "Ratings built from <b>" + d.matches_analyzed.toLocaleString() +
        "</b> real international matches (" + esc(d.data_source) + ").";
  }).catch(function () {});
}
function init() {
  setupTabs(); setupModal();
  loadMatches(); loadGroups(); loadInfo();
  setInterval(tick, 1000);
  setInterval(function () { loadMatches(); loadGroups(); }, 20000);
}
document.addEventListener("DOMContentLoaded", init);
