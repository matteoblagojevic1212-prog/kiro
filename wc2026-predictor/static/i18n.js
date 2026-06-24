/* Simple i18n for the World Cup 2026 Predictor. Language is saved in
   localStorage ("wc_lang") so it persists like last time. Arabic uses RTL. */
"use strict";

var LANGS = [
  ["en", "English"], ["it", "Italiano"], ["fr", "Français"], ["es", "Español"],
  ["ru", "Русский"], ["ar", "العربية"], ["zh", "中文"], ["pt", "Português"],
  ["de", "Deutsch"], ["hr", "Srpskohrvatski"]
];
var RTL = { ar: true };

var T = {
  en: {
    subtitle: "Predictor & live tracker", matches: "Matches", groups: "Groups",
    upcoming: "Upcoming", live: "Live", finished: "Finished", search: "Search a team…",
    menu: "Menu", account: "Account", language: "Language",
    google: "Continue with Google", apple: "Continue with Apple",
    email: "Email", password: "Password", create: "Create account",
    signin: "Sign in", signout: "Sign out", signed: "Signed in as",
    analyse: "Analyse with AI", tbd: "Teams to be decided",
    ft: "FULL TIME", ht: "Half time", awaiting: "awaiting score",
    winner: "PREDICTED WINNER", confidence: "Confidence",
    High: "High", Medium: "Medium", Low: "Low",
    scores: "3 Most Probable Exact Scores", likely: "MOST LIKELY",
    result: "Match Result", goals: "Goals Markets", btts: "Both teams score",
    form: "recent form", scored: "Avg scored", conceded: "Avg conceded",
    scorers: "Likely Goalscorers", assists: "Likely Assists",
    venue: "Venue & weather", wxpending: "Weather forecast appears closer to kick-off.",
    norecent: "no recent data", draw: "Draw", win: "win", over: "Over", under: "Under"
  }
};


T.it = {
  subtitle: "Pronostici e diretta", matches: "Partite", groups: "Gironi",
  upcoming: "In arrivo", live: "Dal vivo", finished: "Concluse", search: "Cerca una squadra…",
  menu: "Menu", account: "Account", language: "Lingua",
  google: "Continua con Google", apple: "Continua con Apple",
  email: "Email", password: "Password", create: "Crea account",
  signin: "Accedi", signout: "Esci", signed: "Accesso come",
  analyse: "Analizza con IA", tbd: "Squadre da definire",
  ft: "FINALE", ht: "Intervallo", awaiting: "in attesa del risultato",
  winner: "VINCITORE PREVISTO", confidence: "Affidabilità",
  High: "Alta", Medium: "Media", Low: "Bassa",
  scores: "3 risultati esatti più probabili", likely: "PIÙ PROBABILE",
  result: "Esito partita", goals: "Mercato gol", btts: "Entrambe segnano",
  form: "forma recente", scored: "Media segnati", conceded: "Media subiti",
  scorers: "Probabili marcatori", assists: "Probabili assist",
  venue: "Stadio e meteo", wxpending: "Le previsioni meteo appariranno più vicino al calcio d'inizio.",
  norecent: "nessun dato recente", draw: "Pareggio", win: "vittoria", over: "Over", under: "Under"
};

T.fr = {
  subtitle: "Pronostics et direct", matches: "Matchs", groups: "Groupes",
  upcoming: "À venir", live: "En direct", finished: "Terminés", search: "Rechercher une équipe…",
  menu: "Menu", account: "Compte", language: "Langue",
  google: "Continuer avec Google", apple: "Continuer avec Apple",
  email: "E-mail", password: "Mot de passe", create: "Créer un compte",
  signin: "Se connecter", signout: "Se déconnecter", signed: "Connecté en tant que",
  analyse: "Analyser avec l'IA", tbd: "Équipes à déterminer",
  ft: "TERMINÉ", ht: "Mi-temps", awaiting: "résultat en attente",
  winner: "VAINQUEUR PRÉVU", confidence: "Confiance",
  High: "Élevée", Medium: "Moyenne", Low: "Faible",
  scores: "3 scores exacts les plus probables", likely: "LE PLUS PROBABLE",
  result: "Résultat du match", goals: "Marché des buts", btts: "Les deux marquent",
  form: "forme récente", scored: "Buts marqués (moy.)", conceded: "Buts encaissés (moy.)",
  scorers: "Buteurs probables", assists: "Passeurs probables",
  venue: "Stade et météo", wxpending: "La météo s'affichera plus près du coup d'envoi.",
  norecent: "pas de données récentes", draw: "Nul", win: "victoire", over: "Plus de", under: "Moins de"
};

T.es = {
  subtitle: "Pronósticos y en vivo", matches: "Partidos", groups: "Grupos",
  upcoming: "Próximos", live: "En vivo", finished: "Finalizados", search: "Buscar un equipo…",
  menu: "Menú", account: "Cuenta", language: "Idioma",
  google: "Continuar con Google", apple: "Continuar con Apple",
  email: "Correo", password: "Contraseña", create: "Crear cuenta",
  signin: "Iniciar sesión", signout: "Cerrar sesión", signed: "Sesión iniciada como",
  analyse: "Analizar con IA", tbd: "Equipos por definir",
  ft: "FINAL", ht: "Descanso", awaiting: "esperando resultado",
  winner: "GANADOR PREVISTO", confidence: "Confianza",
  High: "Alta", Medium: "Media", Low: "Baja",
  scores: "3 marcadores exactos más probables", likely: "MÁS PROBABLE",
  result: "Resultado", goals: "Mercado de goles", btts: "Ambos marcan",
  form: "forma reciente", scored: "Goles a favor (prom.)", conceded: "Goles en contra (prom.)",
  scorers: "Goleadores probables", assists: "Asistencias probables",
  venue: "Estadio y clima", wxpending: "El pronóstico aparecerá más cerca del inicio.",
  norecent: "sin datos recientes", draw: "Empate", win: "victoria", over: "Más de", under: "Menos de"
};


T.ru = {
  subtitle: "Прогнозы и трансляция", matches: "Матчи", groups: "Группы",
  upcoming: "Предстоящие", live: "В прямом эфире", finished: "Завершённые", search: "Поиск команды…",
  menu: "Меню", account: "Аккаунт", language: "Язык",
  google: "Войти через Google", apple: "Войти через Apple",
  email: "Эл. почта", password: "Пароль", create: "Создать аккаунт",
  signin: "Войти", signout: "Выйти", signed: "Вы вошли как",
  analyse: "Анализ с ИИ", tbd: "Команды будут определены",
  ft: "ЗАВЕРШЁН", ht: "Перерыв", awaiting: "ожидание результата",
  winner: "ПРОГНОЗ ПОБЕДИТЕЛЯ", confidence: "Уверенность",
  High: "Высокая", Medium: "Средняя", Low: "Низкая",
  scores: "3 самых вероятных счёта", likely: "НАИБОЛЕЕ ВЕРОЯТНО",
  result: "Исход матча", goals: "Рынок голов", btts: "Обе забьют",
  form: "форма", scored: "Забито (сред.)", conceded: "Пропущено (сред.)",
  scorers: "Вероятные бомбардиры", assists: "Вероятные передачи",
  venue: "Стадион и погода", wxpending: "Прогноз погоды появится ближе к началу.",
  norecent: "нет данных", draw: "Ничья", win: "победа", over: "Больше", under: "Меньше"
};

T.ar = {
  subtitle: "التوقعات والبث المباشر", matches: "المباريات", groups: "المجموعات",
  upcoming: "القادمة", live: "مباشر", finished: "المنتهية", search: "ابحث عن فريق…",
  menu: "القائمة", account: "الحساب", language: "اللغة",
  google: "المتابعة عبر Google", apple: "المتابعة عبر Apple",
  email: "البريد الإلكتروني", password: "كلمة المرور", create: "إنشاء حساب",
  signin: "تسجيل الدخول", signout: "تسجيل الخروج", signed: "تم الدخول باسم",
  analyse: "تحليل بالذكاء الاصطناعي", tbd: "الفرق لم تتحدد بعد",
  ft: "انتهت", ht: "الاستراحة", awaiting: "بانتظار النتيجة",
  winner: "الفائز المتوقع", confidence: "الثقة",
  High: "عالية", Medium: "متوسطة", Low: "منخفضة",
  scores: "أكثر 3 نتائج احتمالاً", likely: "الأكثر احتمالاً",
  result: "نتيجة المباراة", goals: "سوق الأهداف", btts: "كلا الفريقين يسجل",
  form: "الأداء الأخير", scored: "متوسط التسجيل", conceded: "متوسط استقبال الأهداف",
  scorers: "الهدافون المحتملون", assists: "صناع الأهداف المحتملون",
  venue: "الملعب والطقس", wxpending: "تظهر توقعات الطقس قرب موعد المباراة.",
  norecent: "لا توجد بيانات", draw: "تعادل", win: "فوز", over: "أكثر من", under: "أقل من"
};

T.zh = {
  subtitle: "预测与实时比分", matches: "比赛", groups: "小组",
  upcoming: "即将开始", live: "进行中", finished: "已结束", search: "搜索球队…",
  menu: "菜单", account: "账户", language: "语言",
  google: "使用 Google 继续", apple: "使用 Apple 继续",
  email: "邮箱", password: "密码", create: "创建账户",
  signin: "登录", signout: "退出", signed: "已登录：",
  analyse: "AI 分析", tbd: "球队待定",
  ft: "全场结束", ht: "中场", awaiting: "等待比分",
  winner: "预测胜者", confidence: "可信度",
  High: "高", Medium: "中", Low: "低",
  scores: "最可能的3个比分", likely: "最可能",
  result: "比赛结果", goals: "进球盘口", btts: "双方均进球",
  form: "近期状态", scored: "场均进球", conceded: "场均失球",
  scorers: "可能的射手", assists: "可能的助攻",
  venue: "球场与天气", wxpending: "临近开球时显示天气预报。",
  norecent: "暂无数据", draw: "平局", win: "胜", over: "大于", under: "小于"
};


T.pt = {
  subtitle: "Prognósticos e ao vivo", matches: "Jogos", groups: "Grupos",
  upcoming: "Próximos", live: "Ao vivo", finished: "Terminados", search: "Pesquisar uma equipa…",
  menu: "Menu", account: "Conta", language: "Idioma",
  google: "Continuar com Google", apple: "Continuar com Apple",
  email: "E-mail", password: "Palavra-passe", create: "Criar conta",
  signin: "Entrar", signout: "Sair", signed: "Sessão iniciada como",
  analyse: "Analisar com IA", tbd: "Equipas a definir",
  ft: "FIM DE JOGO", ht: "Intervalo", awaiting: "a aguardar resultado",
  winner: "VENCEDOR PREVISTO", confidence: "Confiança",
  High: "Alta", Medium: "Média", Low: "Baixa",
  scores: "3 resultados exatos mais prováveis", likely: "MAIS PROVÁVEL",
  result: "Resultado", goals: "Mercado de golos", btts: "Ambas marcam",
  form: "forma recente", scored: "Média marcados", conceded: "Média sofridos",
  scorers: "Prováveis marcadores", assists: "Prováveis assistências",
  venue: "Estádio e clima", wxpending: "A previsão aparece mais perto do início.",
  norecent: "sem dados recentes", draw: "Empate", win: "vitória", over: "Mais de", under: "Menos de"
};

T.de = {
  subtitle: "Prognosen & Liveticker", matches: "Spiele", groups: "Gruppen",
  upcoming: "Anstehend", live: "Live", finished: "Beendet", search: "Team suchen…",
  menu: "Menü", account: "Konto", language: "Sprache",
  google: "Weiter mit Google", apple: "Weiter mit Apple",
  email: "E-Mail", password: "Passwort", create: "Konto erstellen",
  signin: "Anmelden", signout: "Abmelden", signed: "Angemeldet als",
  analyse: "Mit KI analysieren", tbd: "Teams noch offen",
  ft: "ABPFIFF", ht: "Halbzeit", awaiting: "Ergebnis ausstehend",
  winner: "VORHERGESAGTER SIEGER", confidence: "Sicherheit",
  High: "Hoch", Medium: "Mittel", Low: "Niedrig",
  scores: "3 wahrscheinlichste Ergebnisse", likely: "AM WAHRSCHEINLICHSTEN",
  result: "Spielausgang", goals: "Tormarkt", btts: "Beide treffen",
  form: "aktuelle Form", scored: "Tore (Schnitt)", conceded: "Gegentore (Schnitt)",
  scorers: "Wahrscheinliche Torschützen", assists: "Wahrscheinliche Vorlagen",
  venue: "Stadion & Wetter", wxpending: "Wetter erscheint näher am Anstoß.",
  norecent: "keine Daten", draw: "Unentschieden", win: "Sieg", over: "Über", under: "Unter"
};

T.hr = {
  subtitle: "Prognoze i prijenos uživo", matches: "Utakmice", groups: "Skupine",
  upcoming: "Nadolazeće", live: "Uživo", finished: "Završene", search: "Pretraži reprezentaciju…",
  menu: "Izbornik", account: "Račun", language: "Jezik",
  google: "Nastavi s Google", apple: "Nastavi s Apple",
  email: "E-pošta", password: "Lozinka", create: "Otvori račun",
  signin: "Prijava", signout: "Odjava", signed: "Prijavljeni kao",
  analyse: "Analiziraj s AI", tbd: "Ekipe se određuju",
  ft: "KRAJ", ht: "Poluvrijeme", awaiting: "čeka se rezultat",
  winner: "PREDVIĐENI POBJEDNIK", confidence: "Pouzdanost",
  High: "Visoka", Medium: "Srednja", Low: "Niska",
  scores: "3 najvjerojatnija rezultata", likely: "NAJVJEROJATNIJE",
  result: "Ishod utakmice", goals: "Tržište golova", btts: "Oba tima zabijaju",
  form: "nedavna forma", scored: "Prosjek zabijenih", conceded: "Prosjek primljenih",
  scorers: "Mogući strijelci", assists: "Moguće asistencije",
  venue: "Stadion i vrijeme", wxpending: "Prognoza se prikazuje bliže početku.",
  norecent: "nema podataka", draw: "Neriješeno", win: "pobjeda", over: "Više od", under: "Manje od"
};


var _lang = localStorage.getItem("wc_lang") || "en";

function t(key) {
  return (T[_lang] && T[_lang][key]) || T.en[key] || key;
}
function getLang() { return _lang; }
function setLang(code) {
  if (!T[code]) return;
  _lang = code;
  localStorage.setItem("wc_lang", code);
  applyLang();
}
function applyLang() {
  document.documentElement.lang = _lang;
  document.documentElement.dir = RTL[_lang] ? "rtl" : "ltr";
  document.querySelectorAll("[data-i18n]").forEach(function (el) {
    el.textContent = t(el.getAttribute("data-i18n"));
  });
  document.querySelectorAll("[data-i18n-ph]").forEach(function (el) {
    el.setAttribute("placeholder", t(el.getAttribute("data-i18n-ph")));
  });
  // let the rest of the app re-render translated dynamic content
  if (window._onLangChange) window._onLangChange();
}


// History section labels (added across all languages)
T.en.history = "Analysis history"; T.en.nohist = "No analyses yet";
T.it.history = "Cronologia analisi"; T.it.nohist = "Nessuna analisi";
T.fr.history = "Historique des analyses"; T.fr.nohist = "Aucune analyse";
T.es.history = "Historial de análisis"; T.es.nohist = "Sin análisis";
T.ru.history = "История анализов"; T.ru.nohist = "Пока нет анализов";
T.ar.history = "سجل التحليلات"; T.ar.nohist = "لا توجد تحليلات بعد";
T.zh.history = "分析记录"; T.zh.nohist = "暂无分析";
T.pt.history = "Histórico de análises"; T.pt.nohist = "Sem análises";
T.de.history = "Analyseverlauf"; T.de.nohist = "Noch keine Analysen";
T.hr.history = "Povijest analiza"; T.hr.nohist = "Još nema analiza";


// "Files" section labels
T.en.files = "Files"; T.en.openfolder = "Open install folder";
T.it.files = "File"; T.it.openfolder = "Apri cartella di installazione";
T.fr.files = "Fichiers"; T.fr.openfolder = "Ouvrir le dossier d'installation";
T.es.files = "Archivos"; T.es.openfolder = "Abrir carpeta de instalación";
T.ru.files = "Файлы"; T.ru.openfolder = "Открыть папку установки";
T.ar.files = "الملفات"; T.ar.openfolder = "فتح مجلد التثبيت";
T.zh.files = "文件"; T.zh.openfolder = "打开安装文件夹";
T.pt.files = "Ficheiros"; T.pt.openfolder = "Abrir pasta de instalação";
T.de.files = "Dateien"; T.de.openfolder = "Installationsordner öffnen";
T.hr.files = "Datoteke"; T.hr.openfolder = "Otvori instalacijsku mapu";
