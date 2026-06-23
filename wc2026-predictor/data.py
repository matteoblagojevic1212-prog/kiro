# -*- coding: utf-8 -*-
"""
World Cup 2026 data: 48 teams, 12 groups, flags (ISO-2 codes for flag images),
Elo strength ratings (an approximation distilled from international men's results
1872-2024), and per-team scoring profiles used by the AI analysis engine.

Everything here is editable. If FIFA's official draw / squads change, just update
the values below and the whole app (schedule, standings, predictions) follows.
"""

# ---------------------------------------------------------------------------
# TEAMS
# ---------------------------------------------------------------------------
# key fields:
#   name  : display name
#   iso   : ISO 3166-1 alpha-2 code -> used to load a rounded flag image
#   elo   : strength rating (higher = stronger). Drives expected goals.
#   players: key squad members with relative goal/assist weights.
#            goal/assist weights are RELATIVE shares (normalised by the engine).
# ---------------------------------------------------------------------------

TEAMS = {
    # ---- Hosts (CONCACAF) ----
    "USA":        {"iso": "us", "elo": 1800, "players": [("Christian Pulisic", 5, 4), ("Folarin Balogun", 4, 1), ("Weston McKennie", 2, 3), ("Giovanni Reyna", 2, 3), ("Tim Weah", 2, 2)]},
    "Mexico":     {"iso": "mx", "elo": 1810, "players": [("Santiago Gimenez", 5, 1), ("Raul Jimenez", 4, 2), ("Hirving Lozano", 3, 3), ("Edson Alvarez", 1, 2), ("Alexis Vega", 2, 3)]},
    "Canada":     {"iso": "ca", "elo": 1760, "players": [("Jonathan David", 5, 2), ("Alphonso Davies", 3, 4), ("Cyle Larin", 3, 1), ("Tajon Buchanan", 2, 3), ("Stephen Eustaquio", 1, 3)]},

    # ---- UEFA ----
    "France":     {"iso": "fr", "elo": 2070, "players": [("Kylian Mbappe", 6, 3), ("Ousmane Dembele", 3, 4), ("Antoine Griezmann", 3, 4), ("Marcus Thuram", 3, 1), ("Aurelien Tchouameni", 1, 2)]},
    "Spain":      {"iso": "es", "elo": 2070, "players": [("Lamine Yamal", 4, 5), ("Nico Williams", 4, 4), ("Alvaro Morata", 4, 1), ("Dani Olmo", 3, 3), ("Pedri", 2, 3)]},
    "England":    {"iso": "gb-eng", "elo": 2010, "players": [("Harry Kane", 6, 2), ("Bukayo Saka", 3, 4), ("Phil Foden", 3, 3), ("Jude Bellingham", 3, 3), ("Cole Palmer", 3, 4)]},
    "Portugal":   {"iso": "pt", "elo": 1985, "players": [("Cristiano Ronaldo", 5, 1), ("Bruno Fernandes", 3, 5), ("Rafael Leao", 4, 3), ("Bernardo Silva", 2, 4), ("Goncalo Ramos", 3, 1)]},
    "Netherlands":{"iso": "nl", "elo": 1975, "players": [("Memphis Depay", 4, 3), ("Cody Gakpo", 4, 3), ("Xavi Simons", 3, 4), ("Donyell Malen", 3, 2), ("Frenkie de Jong", 1, 3)]},
    "Germany":    {"iso": "de", "elo": 1945, "players": [("Kai Havertz", 4, 2), ("Jamal Musiala", 4, 4), ("Florian Wirtz", 3, 4), ("Niclas Fullkrug", 4, 1), ("Leroy Sane", 2, 3)]},
    "Belgium":    {"iso": "be", "elo": 1925, "players": [("Romelu Lukaku", 5, 1), ("Kevin De Bruyne", 2, 6), ("Jeremy Doku", 3, 3), ("Leandro Trossard", 3, 2), ("Youri Tielemans", 1, 2)]},
    "Italy":      {"iso": "it", "elo": 1900, "players": [("Mateo Retegui", 4, 1), ("Federico Chiesa", 3, 3), ("Gianluca Scamacca", 3, 1), ("Nicolo Barella", 2, 3), ("Federico Dimarco", 1, 3)]},
    "Croatia":    {"iso": "hr", "elo": 1880, "players": [("Andrej Kramaric", 4, 2), ("Bruno Petkovic", 3, 1), ("Luka Modric", 2, 4), ("Mateo Kovacic", 1, 3), ("Ivan Perisic", 3, 3)]},
    "Switzerland":{"iso": "ch", "elo": 1860, "players": [("Breel Embolo", 4, 2), ("Dan Ndoye", 3, 2), ("Ruben Vargas", 3, 3), ("Granit Xhaka", 1, 3), ("Xherdan Shaqiri", 2, 3)]},
    "Denmark":    {"iso": "dk", "elo": 1840, "players": [("Rasmus Hojlund", 4, 1), ("Christian Eriksen", 2, 5), ("Jonas Wind", 3, 1), ("Mikkel Damsgaard", 2, 3), ("Andreas Skov Olsen", 3, 3)]},
    "Austria":    {"iso": "at", "elo": 1790, "players": [("Marko Arnautovic", 3, 2), ("Michael Gregoritsch", 3, 1), ("Christoph Baumgartner", 3, 3), ("Marcel Sabitzer", 2, 3), ("Patrick Wimmer", 2, 2)]},
    "Turkey":     {"iso": "tr", "elo": 1790, "players": [("Arda Guler", 3, 4), ("Kenan Yildiz", 3, 3), ("Hakan Calhanoglu", 2, 4), ("Baris Alper Yilmaz", 3, 2), ("Kerem Akturkoglu", 3, 3)]},
    "Norway":     {"iso": "no", "elo": 1810, "players": [("Erling Haaland", 7, 1), ("Martin Odegaard", 2, 5), ("Alexander Sorloth", 4, 1), ("Antonio Nusa", 2, 3), ("Oscar Bobb", 2, 3)]},
    "Serbia":     {"iso": "rs", "elo": 1810, "players": [("Aleksandar Mitrovic", 5, 1), ("Dusan Vlahovic", 4, 1), ("Dusan Tadic", 2, 4), ("Sergej Milinkovic-Savic", 2, 3), ("Filip Kostic", 1, 3)]},
    "Poland":     {"iso": "pl", "elo": 1770, "players": [("Robert Lewandowski", 6, 2), ("Piotr Zielinski", 2, 4), ("Karol Swiderski", 3, 1), ("Sebastian Szymanski", 2, 3), ("Nicola Zalewski", 1, 3)]},
    "Ukraine":    {"iso": "ua", "elo": 1770, "players": [("Artem Dovbyk", 4, 1), ("Mykhailo Mudryk", 3, 3), ("Viktor Tsygankov", 3, 3), ("Heorhiy Sudakov", 2, 3), ("Oleksandr Zinchenko", 1, 3)]},

    # ---- CONMEBOL ----
    "Argentina":  {"iso": "ar", "elo": 2143, "players": [("Lionel Messi", 5, 5), ("Lautaro Martinez", 5, 1), ("Julian Alvarez", 4, 3), ("Angel Di Maria", 2, 4), ("Enzo Fernandez", 2, 3)]},
    "Brazil":     {"iso": "br", "elo": 1995, "players": [("Vinicius Junior", 5, 4), ("Rodrygo", 4, 3), ("Raphinha", 4, 4), ("Endrick", 3, 1), ("Bruno Guimaraes", 1, 2)]},
    "Uruguay":    {"iso": "uy", "elo": 1900, "players": [("Darwin Nunez", 5, 2), ("Federico Valverde", 3, 4), ("Facundo Pellistri", 2, 3), ("Nicolas De La Cruz", 2, 3), ("Maxi Araujo", 2, 2)]},
    "Colombia":   {"iso": "co", "elo": 1900, "players": [("Luis Diaz", 5, 3), ("James Rodriguez", 2, 6), ("Jhon Duran", 3, 1), ("Rafael Santos Borre", 3, 1), ("Jhon Arias", 2, 3)]},
    "Ecuador":    {"iso": "ec", "elo": 1790, "players": [("Enner Valencia", 4, 2), ("Kevin Rodriguez", 3, 1), ("Kendry Paez", 2, 3), ("Moises Caicedo", 1, 2), ("Pervis Estupinan", 1, 3)]},
    "Paraguay":   {"iso": "py", "elo": 1700, "players": [("Antonio Sanabria", 4, 1), ("Julio Enciso", 3, 3), ("Miguel Almiron", 3, 3), ("Diego Gomez", 2, 2), ("Omar Alderete", 1, 1)]},

    # ---- CAF ----
    "Morocco":    {"iso": "ma", "elo": 1860, "players": [("Youssef En-Nesyri", 4, 1), ("Brahim Diaz", 3, 3), ("Hakim Ziyech", 2, 4), ("Achraf Hakimi", 2, 4), ("Sofyan Amrabat", 1, 2)]},
    "Senegal":    {"iso": "sn", "elo": 1820, "players": [("Sadio Mane", 4, 3), ("Nicolas Jackson", 4, 2), ("Iliman Ndiaye", 3, 3), ("Ismaila Sarr", 3, 3), ("Pape Matar Sarr", 1, 2)]},
    "Nigeria":    {"iso": "ng", "elo": 1780, "players": [("Victor Osimhen", 6, 1), ("Ademola Lookman", 4, 3), ("Samuel Chukwueze", 2, 3), ("Alex Iwobi", 2, 3), ("Victor Boniface", 3, 1)]},
    "Egypt":      {"iso": "eg", "elo": 1760, "players": [("Mohamed Salah", 6, 4), ("Omar Marmoush", 4, 2), ("Mostafa Mohamed", 3, 1), ("Trezeguet", 2, 3), ("Mohamed Elneny", 1, 2)]},
    "Algeria":    {"iso": "dz", "elo": 1760, "players": [("Riyad Mahrez", 3, 4), ("Mohamed Amoura", 4, 2), ("Islam Slimani", 3, 1), ("Said Benrahma", 2, 3), ("Ismael Bennacer", 1, 3)]},
    "Tunisia":    {"iso": "tn", "elo": 1710, "players": [("Youssef Msakni", 3, 3), ("Wahbi Khazri", 3, 2), ("Naim Sliti", 2, 3), ("Mohamed Drager", 1, 2), ("Hannibal Mejbri", 2, 3)]},
    "Ivory Coast":{"iso": "ci", "elo": 1750, "players": [("Sebastien Haller", 4, 1), ("Nicolas Pepe", 3, 3), ("Simon Adingra", 3, 3), ("Franck Kessie", 2, 2), ("Jeremie Boga", 2, 3)]},
    "Ghana":      {"iso": "gh", "elo": 1720, "players": [("Mohammed Kudus", 4, 3), ("Inaki Williams", 4, 2), ("Jordan Ayew", 3, 3), ("Antoine Semenyo", 3, 2), ("Thomas Partey", 1, 2)]},
    "Cameroon":   {"iso": "cm", "elo": 1720, "players": [("Vincent Aboubakar", 4, 2), ("Bryan Mbeumo", 3, 3), ("Karl Toko Ekambi", 3, 2), ("Andre-Frank Zambo Anguissa", 2, 3), ("Georges-Kevin Nkoudou", 2, 2)]},

    # ---- AFC ----
    "Japan":      {"iso": "jp", "elo": 1840, "players": [("Kaoru Mitoma", 4, 4), ("Takefusa Kubo", 3, 4), ("Ayase Ueda", 4, 1), ("Daizen Maeda", 3, 2), ("Wataru Endo", 1, 2)]},
    "South Korea":{"iso": "kr", "elo": 1790, "players": [("Son Heung-min", 5, 4), ("Lee Kang-in", 3, 4), ("Hwang Hee-chan", 3, 2), ("Cho Gue-sung", 3, 1), ("Hwang In-beom", 1, 3)]},
    "Iran":       {"iso": "ir", "elo": 1820, "players": [("Mehdi Taremi", 5, 3), ("Sardar Azmoun", 4, 2), ("Alireza Jahanbakhsh", 2, 3), ("Saman Ghoddos", 2, 2), ("Mehdi Ghayedi", 2, 2)]},
    "Australia":  {"iso": "au", "elo": 1730, "players": [("Mitchell Duke", 3, 1), ("Martin Boyle", 3, 3), ("Jackson Irvine", 2, 2), ("Riley McGree", 2, 3), ("Craig Goodwin", 2, 3)]},
    "Saudi Arabia":{"iso": "sa", "elo": 1670, "players": [("Salem Al-Dawsari", 4, 3), ("Firas Al-Buraikan", 4, 1), ("Saleh Al-Shehri", 3, 1), ("Mohamed Kanno", 1, 2), ("Abdullah Al-Hamdan", 2, 2)]},
    "Qatar":      {"iso": "qa", "elo": 1680, "players": [("Almoez Ali", 4, 2), ("Akram Afif", 3, 4), ("Hassan Al-Haydos", 2, 3), ("Mohammed Muntari", 2, 1), ("Ahmed Alaaeldin", 2, 2)]},
    "Uzbekistan": {"iso": "uz", "elo": 1660, "players": [("Eldor Shomurodov", 4, 2), ("Igor Sergeev", 3, 1), ("Abbosbek Fayzullaev", 2, 3), ("Jaloliddin Masharipov", 2, 3), ("Otabek Shukurov", 1, 2)]},
    "Jordan":     {"iso": "jo", "elo": 1620, "players": [("Musa Al-Taamari", 3, 3), ("Yazan Al-Naimat", 3, 2), ("Ali Olwan", 3, 1), ("Noor Al-Rawabdeh", 1, 2), ("Mahmoud Al-Mardi", 1, 2)]},

    # ---- CONCACAF ----
    "Costa Rica": {"iso": "cr", "elo": 1680, "players": [("Manfred Ugalde", 4, 2), ("Joel Campbell", 3, 3), ("Alonso Martinez", 3, 1), ("Brandon Aguilera", 2, 3), ("Josimar Alcocer", 2, 2)]},
    "Panama":     {"iso": "pa", "elo": 1680, "players": [("Cecilio Waterman", 3, 1), ("Jose Fajardo", 3, 1), ("Adalberto Carrasquilla", 2, 3), ("Ismael Diaz", 3, 3), ("Eric Davis", 1, 3)]},
    "Jamaica":    {"iso": "jm", "elo": 1650, "players": [("Michail Antonio", 3, 2), ("Leon Bailey", 4, 3), ("Demarai Gray", 3, 3), ("Bobby De Cordova-Reid", 2, 3), ("Shamar Nicholson", 3, 1)]},

    # ---- OFC ----
    "New Zealand":{"iso": "nz", "elo": 1610, "players": [("Chris Wood", 5, 1), ("Ben Old", 2, 3), ("Marko Stamenic", 2, 2), ("Kosta Barbarouses", 2, 2), ("Elijah Just", 2, 2)]},

    # ---- Extra / playoff ----
    "Peru":       {"iso": "pe", "elo": 1720, "players": [("Gianluca Lapadula", 4, 1), ("Andre Carrillo", 2, 3), ("Edison Flores", 2, 3), ("Sergio Pena", 1, 3), ("Bryan Reyna", 2, 2)]},
}

# ---------------------------------------------------------------------------
# GROUPS  (12 groups A-L, 4 teams each = 48)
# ---------------------------------------------------------------------------
GROUPS = {
    "A": ["Mexico", "Croatia", "Ivory Coast", "New Zealand"],
    "B": ["Canada", "Belgium", "Morocco", "Uzbekistan"],
    "C": ["USA", "Netherlands", "Japan", "Ghana"],
    "D": ["Argentina", "Norway", "Tunisia", "Jordan"],
    "E": ["France", "Senegal", "Australia", "Costa Rica"],
    "F": ["Spain", "Uruguay", "Egypt", "Panama"],
    "G": ["England", "Colombia", "South Korea", "Jamaica"],
    "H": ["Portugal", "Serbia", "Nigeria", "Peru"],
    "I": ["Brazil", "Switzerland", "Iran", "Ukraine"],
    "J": ["Germany", "Ecuador", "Algeria", "Saudi Arabia"],
    "K": ["Italy", "Denmark", "Cameroon", "Qatar"],
    "L": ["Turkey", "Poland", "Austria", "Paraguay"],
}

# Host cities used as venues for flavour (kickoff scheduling uses these).
VENUES = [
    "MetLife Stadium, New York/NJ", "SoFi Stadium, Los Angeles",
    "AT&T Stadium, Dallas", "Mercedes-Benz Stadium, Atlanta",
    "Arrowhead Stadium, Kansas City", "NRG Stadium, Houston",
    "Lincoln Financial Field, Philadelphia", "Lumen Field, Seattle",
    "Levi's Stadium, San Francisco Bay", "Hard Rock Stadium, Miami",
    "Gillette Stadium, Boston", "L=Estadio Azteca, Mexico City",
    "Estadio Akron, Guadalajara", "Estadio BBVA, Monterrey",
    "BMO Field, Toronto", "BC Place, Vancouver",
]


def team(name):
    """Safe accessor for a team record."""
    return TEAMS.get(name, {"iso": "un", "elo": 1500, "players": []})


def group_of(name):
    for g, members in GROUPS.items():
        if name in members:
            return g
    return None
