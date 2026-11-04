"""Exos « Lire la consigne » : un long énoncé en anglais, puis des questions de compréhension.

Chaque exo : id, title, focus (ce qu'on entraîne), text (énoncé HTML en anglais, au format du test),
questions (q, o = options, a = index de la bonne réponse, why = explication), keys (mots-pièges à retenir).
"""

READ = [
    {"id": "rd01", "title": "Columns written top to bottom", "focus": "Lire une grille écrite en colonnes verticales",
     "text": """<p>The warehouse scanners are old and print their reports in a strange way. Each report is a text file in which the codes of the scanned parcels are written <b>vertically</b>: the first code is the first column of characters, read from top to bottom, the second code is the next column, and so on. All lines of a file have the same length, and codes shorter than the others are completed at the bottom with the character <code>.</code>, which is not part of the code. Columns are separated by one column of spaces.</p>
<p>For example, the file</p><pre>A C X
B D .
1 2 .</pre><p>contains the three codes <code>AB1</code>, <code>CD2</code> and <code>X</code>.</p>
<p>Your task is to return, for each file, the number of codes and the longest code (the first one in reading order if several have the same length).</p>""",
     "questions": [
         {"q": "Dans l'exemple, combien de colonnes de caractères contient chaque ligne ?", "o": ["3", "5", "6", "9"], "a": 1,
          "why": "3 colonnes de codes + 2 colonnes d'espaces entre elles = 5 caractères par ligne (« A C X »). Le séparateur est une colonne entière d'espaces."},
         {"q": "Quel est le 2e caractère du code n°3 dans l'exemple ?", "o": ["« . »", "Il n'y en a pas : le code est X", "« 2 »", "« D »"], "a": 1,
          "why": "Le « . » complète les codes courts et ne fait pas partie du code. Le code n°3 est seulement « X »."},
         {"q": "Comment obtenir le code n°k d'un fichier (en partant de 0) ?", "o": ["Lire la ligne k", "Prendre le caractère d'indice 2k de chaque ligne, de haut en bas, puis retirer les « . »", "Découper chaque ligne sur les espaces et prendre le k-ième mot", "Prendre le caractère d'indice k de chaque ligne"], "a": 1,
          "why": "Les colonnes de codes sont aux indices 0, 2, 4… à cause des colonnes d'espaces. Découper sur les espaces ne marche pas : on obtient des lignes, pas des colonnes."},
         {"q": "Deux codes ont la même longueur maximale. Lequel retourner ?", "o": ["Le plus petit en ordre alphabétique", "Le dernier", "Le premier dans l'ordre de lecture, donc la colonne la plus à gauche", "N'importe lequel"], "a": 2,
          "why": "« the first one in reading order » : ici l'ordre de lecture des codes, c'est de gauche à droite."}],
     "keys": ["vertically = une colonne de caractères par valeur", "completed with = remplissage à retirer", "separated by one column of spaces = indices 0, 2, 4…", "first one in reading order = départage par position"]},

    {"id": "rd02", "title": "The most recent known value", "focus": "« Most recent », « on or before », valeur reportée",
     "text": """<p>Prices of our products change from time to time, and each change is a row of <code>prices_df</code> with the columns <code>sku</code>, <code>valid_from</code> (date) and <code>price</code>. A price stays valid until the next change of the same product. <code>orders_df</code> has the columns <code>order_id</code>, <code>sku</code>, <code>ordered_on</code> (date) and <code>qty</code>.</p>
<p>An order is charged at the price valid on the day it was placed, that is the price of the most recent change on or before <code>ordered_on</code>. Orders placed before the first known price of their product cannot be charged: they are reported with a <code>null</code> amount and still appear in the output.</p>
<p>Your task is to return every order with its columns and <code>amount</code> (price times quantity, rounded to 2 decimals), sorted by <code>order_id</code>.</p>""",
     "questions": [
         {"q": "Prix : 10.0 depuis le 01/03, 12.0 depuis le 10/03. Commande le 10/03. Quel prix ?", "o": ["10.0", "12.0", "La moyenne 11.0", "null"], "a": 1,
          "why": "« on or before » : le changement du 10/03 compte pour une commande du 10/03."},
         {"q": "Même produit, commande le 28/02. Que retourner ?", "o": ["Rien : la commande est retirée", "amount = 0", "La commande avec amount = null", "Le premier prix connu, 10.0"], "a": 2,
          "why": "« still appear in the output » avec « a null amount ». Une jointure interne la ferait disparaître : il faut une jointure gauche."},
         {"q": "Quel est le grain de la sortie ?", "o": ["Une ligne par produit", "Une ligne par commande", "Une ligne par changement de prix", "Une ligne par jour"], "a": 1,
          "why": "« return every order » : une ligne par commande, jamais dédoublée par la jointure avec les prix."},
         {"q": "Quelle méthode évite de dupliquer les commandes ?", "o": ["Joindre sur sku et ordered_on = valid_from", "Joindre sur sku avec valid_from <= ordered_on, puis garder la ligne au valid_from le plus grand par commande", "Prendre le dernier prix du produit, quelle que soit la date", "Faire un groupBy sku"], "a": 1,
          "why": "Jointure « as-of » : toutes les versions possibles, puis row_number par commande ordonné par valid_from décroissant. L'égalité stricte rate les jours sans changement."}],
     "keys": ["on or before = <=", "most recent = le plus grand avant la date", "still appear = jointure gauche", "every order = grain commande"]},

    {"id": "rd03", "title": "Bounds that are easy to get wrong", "focus": "Inclus, exclus, « more than », « at least »",
     "text": """<p>A customer is <b>inactive</b> if their last login is more than 30 days before the report date <code>as_of</code>. A customer is <b>at risk</b> if they have at least 3 support tickets opened during the 14 days that end on <code>as_of</code> (both days included). The marketing team wants to call customers who are at risk but not inactive.</p>
<p>A trial lasts 7 days: a trial started on March 1 at any time ends at the end of March 7. Logins during the trial are not counted as real logins.</p>
<p>Your task is to return the customers to call, with their number of tickets in the window, sorted by tickets descending, then <code>customer_id</code>.</p>""",
     "questions": [
         {"q": "as_of = 31/03. Dernier login le 01/03 (30 jours avant). Inactif ?", "o": ["Oui", "Non", "Ça dépend de l'heure", "On ne peut pas savoir"], "a": 1,
          "why": "« more than 30 days » veut dire > 30. Exactement 30 jours n'est pas plus de 30 : il faut > et non >=."},
         {"q": "as_of = 31/03. Quel est le premier jour de la fenêtre des tickets ?", "o": ["17/03", "18/03", "16/03", "14/03"], "a": 1,
          "why": "14 jours qui finissent le 31 inclus : 18, 19, …, 31 = 14 jours. Le calcul as_of − 14 donne le 17 et ferait 15 jours."},
         {"q": "Un client a exactement 3 tickets. À risque ?", "o": ["Oui", "Non"], "a": 0, "why": "« at least 3 » veut dire >= 3."},
         {"q": "Essai démarré le 01/03 à 18h. Un login le 07/03 à 23h compte-t-il ?", "o": ["Oui, l'essai a duré plus de 6 jours", "Non, il est encore dans l'essai", "Oui, car 7 × 24 h sont passées", "On ignore l'heure"], "a": 1,
          "why": "L'essai finit « at the end of March 7 », peu importe l'heure de début. On compare des dates, pas des durées en heures."}],
     "keys": ["more than = >", "at least = >=", "both days included = n jours, début = fin − (n − 1)", "end of the day = comparer des dates"]},

    {"id": "rd04", "title": "When is a duplicate a duplicate?", "focus": "Doublons à retirer et doublons légitimes",
     "text": """<p>Our cash registers send every sale to the head office. When the network is down, a register sends the same batch again later, so the same sale can arrive twice; a sale is identified by its <code>register</code> and its <code>ticket</code> number. A customer can of course buy the same product twice in one sale, and each unit is then a separate line with the same <code>register</code>, <code>ticket</code> and <code>sku</code>.</p>
<p><code>lines_df</code> has the columns <code>batch_id</code>, <code>register</code>, <code>ticket</code>, <code>sku</code> and <code>price</code>. Your task is to return, for each sku, the number of units sold and the revenue, sorted by revenue descending.</p>""",
     "questions": [
         {"q": "Que fait dropDuplicates() sur toutes les colonnes ici ?", "o": ["Il retire exactement les renvois", "Rien, car batch_id diffère entre l'envoi et le renvoi", "Il retire aussi les unités achetées deux fois", "Il trie les données"], "a": 1,
          "why": "Le renvoi arrive dans un autre batch : les lignes ne sont pas identiques sur toutes les colonnes."},
         {"q": "Que fait dropDuplicates([\"register\", \"ticket\", \"sku\"]) ?", "o": ["La bonne réponse", "Il retire aussi les vraies 2e unités d'un même ticket", "Il ne retire rien", "Il plante"], "a": 1,
          "why": "Deux unités du même produit sur un ticket ont la même clé : on perdrait des ventes réelles."},
         {"q": "Quelle est la bonne logique ?", "o": ["Pour chaque (register, ticket), ne garder les lignes que d'un seul batch_id", "Compter les lignes distinctes", "Garder le prix maximum", "Ignorer les tickets en double"], "a": 0,
          "why": "Un renvoi recopie tout le ticket dans un autre batch : on garde un seul batch par ticket (par exemple le plus petit batch_id), avec toutes ses lignes."},
         {"q": "Quel mot de l'énoncé signale le piège ?", "o": ["« of course »", "« revenue »", "« sorted »", "« head office »"], "a": 0,
          "why": "« of course » introduit le cas légitime qui interdit la déduplication naïve. Souligne toujours la phrase qui suit « of course », « however », « except »."}],
     "keys": ["identified by = la clé d'unicité", "the same … twice = doublon technique", "of course / however = exception à la règle", "renvoi = autre batch, mêmes lignes"]},

    {"id": "rd05", "title": "The grain of the answer", "focus": "« For each … with at least one … », lignes à zéro",
     "text": """<p>Each row of <code>visits_df</code> is a visit of a technician to a client site, with the columns <code>visit_id</code>, <code>technician</code>, <code>site</code>, <code>day</code> and <code>status</code> (<code>done</code> or <code>missed</code>). <code>technicians_df</code> lists all technicians with their <code>team</code>.</p>
<p>Your task is to return, for each team and each day on which the team had at least one visit, the number of visits done, the number missed, and the number of different sites visited (only done visits count as visited). Days are dates; teams without any visit that day do not appear. Sort by <code>team</code>, then <code>day</code>.</p>""",
     "questions": [
         {"q": "Quelle est la clé de regroupement ?", "o": ["technician, day", "team, day", "team", "site, day"], "a": 1, "why": "« for each team and each day » : une ligne par (team, day)."},
         {"q": "Une équipe n'a eu que des visites ratées un jour. Apparaît-elle ?", "o": ["Oui, avec done = 0", "Non"], "a": 0,
          "why": "« at least one visit », et une visite ratée reste une visite. Ne filtre pas sur done avant de grouper."},
         {"q": "Comment compter les sites visités ?", "o": ["countDistinct(site)", "countDistinct de site seulement quand status = done", "count(site)", "Le nombre de visites done"], "a": 1,
          "why": "« only done visits count as visited » : countDistinct(when(status == 'done', site)), car countDistinct ignore les null."},
         {"q": "Faut-il une grille de tous les jours pour toutes les équipes ?", "o": ["Oui", "Non"], "a": 1,
          "why": "« teams without any visit that day do not appear » : pas de grille, contrairement à un énoncé qui dirait « every day from … to … »."}],
     "keys": ["for each X and Y = groupBy(X, Y)", "with at least one = pas de lignes vides", "only … count = when() dans l'agrégat", "every day from … to … = grille de dates"]},

    {"id": "rd06", "title": "Nothing, zero or null?", "focus": "Valeurs vides, 0.0, null, NaN",
     "text": """<p>Sensors send readings in <code>readings_df</code> with the columns <code>sensor</code>, <code>ts</code> and <code>value</code> (string). Old sensors send an empty string or the text <code>N/A</code> when they could not measure; these are not readings. A value of <code>0</code> is a real measure.</p>
<p>Your task is to return, for each sensor of <code>sensors_df</code> (all sensors, even those that sent nothing), the number of readings, the average value rounded to 1 decimal (<code>null</code> if there is no reading), and the number of failed measures (empty or N/A), <code>0</code> if none.</p>""",
     "questions": [
         {"q": "Un capteur a envoyé « 0 », « » et « 10 ». Moyenne ?", "o": ["5.0", "3.3", "10.0", "null"], "a": 0,
          "why": "« » n'est pas une mesure, « 0 » en est une : (0 + 10) / 2 = 5.0."},
         {"q": "Un capteur n'a rien envoyé. Que vaut sa moyenne ?", "o": ["0.0", "null", "Il n'apparaît pas", "NaN"], "a": 1,
          "why": "« null if there is no reading », et il apparaît car on part de sensors_df (« all sensors »)."},
         {"q": "Et son nombre d'échecs ?", "o": ["null", "0", "Il n'apparaît pas"], "a": 1,
          "why": "« 0 if none » : après la jointure gauche, coalesce(count, 0). Une même sortie peut demander null pour une colonne et 0 pour une autre."},
         {"q": "Comment convertir value en nombre sans planter sur « N/A » en mode ANSI ?", "o": ["cast('double')", "try_cast ou expr(\"try_cast(value as double)\")", "float(value) dans une UDF", "value.isNotNull()"], "a": 1,
          "why": "En Spark 4 (ANSI), cast('double') sur « N/A » lève une erreur. try_cast renvoie null."}],
     "keys": ["not a reading = filtrer avant l'agrégat", "null if none ≠ 0 if none", "all X, even those = partir de la table complète + jointure gauche", "ANSI = try_cast"]},

    {"id": "rd07", "title": "Which files are data?", "focus": "Règles de dossiers : profondeur, extensions, fichiers cachés",
     "text": """<p>Partners upload their files into <code>input_dir</code>, one folder per partner, and sometimes in sub-folders by month. Only files ending with <code>.csv</code> are data. Upload tools leave other files behind: files starting with <code>.</code> are temporary copies, and a file named <code>MANIFEST</code> in a partner folder lists the files that were completely uploaded; a data file not listed in the manifest of its partner is still uploading and must be ignored. A partner without a manifest has not finished any upload.</p>
<p>The partner of a file is the name of the first-level folder, whatever the depth of the file. Your task is to return the number of data rows per partner.</p>""",
     "questions": [
         {"q": "input_dir/acme/2026-03/a.csv : quel partenaire ?", "o": ["2026-03", "acme", "a", "input_dir"], "a": 1, "why": "« the first-level folder, whatever the depth »."},
         {"q": "input_dir/acme/.a.csv : à lire ?", "o": ["Oui, il finit par .csv", "Non, il commence par « . »"], "a": 1, "why": "Les deux règles s'appliquent : l'exclusion des fichiers « . » gagne."},
         {"q": "Le partenaire beta n'a pas de MANIFEST mais a 3 fichiers .csv. Combien de lignes pour beta ?", "o": ["Toutes", "Aucune : beta n'apparaît pas ou a 0", "Seulement le plus récent", "On plante"], "a": 1,
          "why": "« A partner without a manifest has not finished any upload » : rien n'est complet."},
         {"q": "Pourquoi spark.read.csv(input_dir) seul est faux ici ?", "o": ["Il est trop lent", "Il lit tout, y compris les fichiers non listés, et ne donne pas le partenaire", "Il ne lit pas les .csv", "Il est interdit"], "a": 1,
          "why": "Il faut d'abord choisir les fichiers (os.walk + règles), puis lire seulement eux et garder le partenaire de chaque fichier."}],
     "keys": ["only files ending with = filtre d'extension", "starting with . = fichiers cachés", "MANIFEST / _SUCCESS = complétude", "whatever the depth = os.walk"]},

    {"id": "rd08", "title": "Days, time zones and midnight", "focus": "UTC, heure locale, jour de début",
     "text": """<p>Our drivers work in shifts. Each event of <code>events_df</code> has <code>driver</code>, <code>ts</code> (a string like <code>2026-03-04T23:10:00+01:00</code>, with the offset of the city) and <code>type</code> (<code>start</code> or <code>end</code>). A shift goes from a <code>start</code> to the next <code>end</code> of the same driver, and it can cross midnight.</p>
<p>Payroll is done in local time: a shift belongs to the local day on which it started. Your task is to return, for each driver and local day, the number of shifts and the hours worked (rounded to 2 decimals). Shifts without an end yet are not counted.</p>""",
     "questions": [
         {"q": "Shift : start 2026-03-04T23:10+01:00, end 2026-03-05T07:10+01:00. Quel jour ?", "o": ["04/03", "05/03", "Moitié sur chaque jour", "04/03 en UTC, donc 04/03"], "a": 0, "why": "« belongs to the local day on which it started » : le 04/03."},
         {"q": "Start 2026-03-05T00:30+01:00. Jour local ? Jour UTC ?", "o": ["05/03 et 05/03", "05/03 et 04/03", "04/03 et 05/03", "04/03 et 04/03"], "a": 1,
          "why": "00:30 à +01:00 = 23:30 UTC la veille. L'énoncé demande le jour local : il faut garder la date écrite, pas convertir en UTC."},
         {"q": "Comment calculer les heures d'un shift qui traverse un changement d'heure ?", "o": ["Soustraire les heures affichées", "Convertir les deux en temps absolu (UTC/epoch) puis soustraire", "Compter 8 h par shift", "Ignorer ces shifts"], "a": 1,
          "why": "La durée réelle se calcule sur des instants absolus. Le jour, lui, se lit dans l'heure locale. Deux règles différentes pour deux colonnes."},
         {"q": "Un start sans end suivant ?", "o": ["Compté avec 0 heure", "Ignoré", "Compté jusqu'à minuit"], "a": 1, "why": "« Shifts without an end yet are not counted »."}],
     "keys": ["local day ≠ UTC day", "on which it started = jour du début", "durée = instants absolus", "without an end yet = ignoré"]},

    {"id": "rd09", "title": "Ranks and ties", "focus": "Top N, départage, rank ou row_number",
     "text": """<p>For each region, the sales director wants the 3 best sellers of the month. Sellers are ranked by revenue, highest first. Two sellers with the same revenue share the same rank, and the next rank is skipped (two sellers at rank 1 are followed by rank 3). All sellers with a rank of 3 or better are returned, so a region can have more than 3 rows.</p>
<p>Return the columns <code>region</code>, <code>rank</code>, <code>seller</code> and <code>revenue</code>, sorted by <code>region</code>, then <code>rank</code>, then <code>seller</code>.</p>""",
     "questions": [
         {"q": "Quelle fonction de fenêtre ?", "o": ["row_number", "rank", "dense_rank", "ntile(3)"], "a": 1,
          "why": "« share the same rank » + « the next rank is skipped » : c'est exactement rank(). dense_rank ne saute pas, row_number ne partage pas."},
         {"q": "Revenus 100, 100, 90, 80. Combien de lignes ?", "o": ["3", "4", "2"], "a": 0,
          "why": "Rangs 1, 1, 3, 4 : on garde rang <= 3, donc 3 lignes."},
         {"q": "Revenus 100, 90, 90, 90. Combien de lignes ?", "o": ["3", "4", "2"], "a": 1, "why": "Rangs 1, 2, 2, 2 : les quatre ont un rang <= 3, d'où « more than 3 rows »."},
         {"q": "À quoi sert « then seller » dans le tri ?", "o": ["À rien", "À rendre l'ordre des ex aequo déterministe pour les tests", "À calculer le rang", "À filtrer"], "a": 1,
          "why": "Le tri final n'est pas le rang : deux vendeurs au même rang doivent sortir dans un ordre fixe, sinon le test peut échouer."}],
     "keys": ["share the same rank + skipped = rank", "no gaps = dense_rank", "tie broken by … = row_number avec plusieurs clés", "sort ≠ rank"]},

    {"id": "rd10", "title": "Types, rounding and division", "focus": "long, double, arrondi, division entière",
     "text": """<p>For each course, return <code>students</code> (long), <code>passed</code> (long), <code>pass_rate</code> (double, passed students divided by students, as a percentage rounded to 1 decimal) and <code>avg_grade</code> (double, rounded to 2 decimals, computed on the grades before rounding). A student passes with a grade of 10 or more out of 20.</p>
<p>In SQL, the columns <code>students</code> and <code>passed</code> are integers.</p>""",
     "questions": [
         {"q": "En PostgreSQL, que vaut 2 / 3 * 100 si les deux sont INT ?", "o": ["66.7", "0", "66", "67"], "a": 1,
          "why": "Division entière : 2 / 3 = 0, puis 0 × 100 = 0. Écris 100.0 * passed / students."},
         {"q": "2 réussis sur 3 étudiants. pass_rate attendu ?", "o": ["0.67", "66.7", "66.67", "67"], "a": 1, "why": "« as a percentage rounded to 1 decimal » : 66.7, pas 0.67."},
         {"q": "Notes 10.255 et 10.255 : il faut…", "o": ["arrondir chaque note puis faire la moyenne", "faire la moyenne puis arrondir", "tronquer"], "a": 1, "why": "« computed on the grades before rounding » : on arrondit une seule fois, à la fin."},
         {"q": "students en PySpark : F.count(...) donne quel type ?", "o": ["int", "long", "double"], "a": 1, "why": "count renvoie un long, comme demandé. sum d'un int donne aussi un long ; un cast est parfois nécessaire."}],
     "keys": ["percentage = × 100", "rounded to n decimals = round à la fin", "INT / INT = division entière", "long ≠ double ≠ int"]},

    {"id": "rd11", "title": "First success, last state", "focus": "Statuts : première réussite, dernier état, en cours",
     "text": """<p>Each delivery attempt is a row of <code>attempts_df</code> with <code>parcel</code>, <code>at</code> and <code>result</code> (<code>delivered</code>, <code>absent</code>, <code>refused</code> or <code>lost</code>). A parcel is <b>delivered</b> at its first <code>delivered</code> attempt, and later rows for this parcel are scanner errors. A parcel that was never delivered is <b>returned</b> if its last attempt is <code>refused</code> or if it had 3 <code>absent</code> attempts; otherwise it is still in progress.</p>
<p>Your task is to return, for each day, the number of parcels delivered that day and the average number of attempts needed, counting the attempts up to and including the delivery.</p>""",
     "questions": [
         {"q": "absent, delivered, refused. Statut ?", "o": ["Livré", "Retourné", "En cours"], "a": 0, "why": "La première réussite décide ; le « refused » d'après est une erreur de scanner."},
         {"q": "absent, absent, refused, absent. Statut ?", "o": ["Livré", "Retourné : 3 absences", "En cours"], "a": 1, "why": "Le dernier n'est pas refused, mais il y a 3 absences : la 2e règle s'applique. Les deux conditions sont liées par « or »."},
         {"q": "absent, delivered, delivered. Nombre de tentatives ?", "o": ["3", "2", "1"], "a": 1, "why": "« up to and including the delivery » : on s'arrête à la première livraison."},
         {"q": "Quel jour pour un colis livré ?", "o": ["Le jour de la 1re tentative", "Le jour de la livraison", "Le jour de la dernière ligne"], "a": 1, "why": "« delivered that day » : le jour de la première tentative delivered."}],
     "keys": ["first … = min sur la condition", "later rows … errors = couper après", "last attempt = row_number desc", "or = deux chemins vers le même statut"]},

    {"id": "rd12", "title": "Reading a project task", "focus": "Ce qui est testé dans une task à plusieurs fichiers",
     "text": """<p>This task is a small project. The package <code>billing</code> contains <code>rates.py</code>, with a function <code>rate_for(country, day)</code> already written and tested by your colleagues, and <code>invoice.py</code>, where you must write <code>solve(spark, usage_df, rates_path)</code>. <code>rates_path</code> is a JSON file that <code>rate_for</code> reads for you. Only <code>solve</code> is tested; do not change <code>rate_for</code>, because other jobs use it.</p>
<p>Your task is to return the invoices of the month, one per account, using <code>rate_for</code> to price each day of usage.</p>""",
     "questions": [
         {"q": "Que dois-tu écrire ?", "o": ["rate_for et solve", "Seulement solve, dans invoice.py", "Un nouveau fichier", "Les tests"], "a": 1, "why": "« where you must write solve » et « do not change rate_for »."},
         {"q": "Comment utiliser rate_for dans invoice.py ?", "o": ["Recopier son code", "from billing.rates import rate_for", "Lire le JSON toi-même", "Ce n'est pas possible"], "a": 1, "why": "Un vrai projet : on importe le code existant au lieu de le réécrire."},
         {"q": "rate_for est une fonction Python. Pour l'appliquer à chaque ligne d'un DataFrame…", "o": ["F.col(rate_for)", "collecter les couples (country, day) distincts, appeler rate_for, recréer un petit DataFrame et joindre", "c'est impossible", "modifier rate_for"], "a": 1,
          "why": "Peu de couples distincts : on les calcule en Python et on joint. Une UDF marche aussi, mais la jointure est plus simple et plus rapide."},
         {"q": "Avant de coder, que regarder en premier ?", "o": ["Le code et la docstring de rate_for", "Le CSS", "Rien", "Les fichiers d'autres tasks"], "a": 0, "why": "Savoir ce que rate_for prend et renvoie (types, null ?) évite la moitié des erreurs."}],
     "keys": ["only … is tested = où concentrer l'effort", "do not change = code partagé", "already written = lire avant d'écrire", "import plutôt que copier"]},

    {"id": "rd13", "title": "A full statement, read like on the day", "focus": "Méthode complète : lister toutes les règles avant de coder",
     "text": """<p>The finance team pays bonuses to the drivers of our ride app. <code>rides_df</code> has <code>ride_id</code>, <code>driver</code>, <code>city</code>, <code>ended_at</code> (timestamp), <code>fare</code> (double) and <code>rating</code> (integer from 1 to 5, <code>null</code> when the rider did not rate). Rides are sometimes logged twice with the same <code>ride_id</code>.</p>
<p>A driver earns a bonus for a week (Monday to Sunday) if they completed at least 20 rides that week and their average rating that week is 4.5 or more; rides without a rating do not count in the average, but they do count as rides. A driver with no rated ride that week cannot earn the bonus. The bonus is 5% of the fares of the week, and it is doubled in the city of <code>Casablanca</code>, whatever the case in which the city is written.</p>
<p>Your task is to return, for each week and driver who earned a bonus, the columns <code>week</code> (date of the Monday), <code>driver</code>, <code>rides</code>, <code>avg_rating</code> (rounded to 2 decimals) and <code>bonus</code> (rounded to 2 decimals), sorted by <code>week</code>, then <code>bonus</code> descending, then <code>driver</code>.</p>""",
     "questions": [
         {"q": "Combien de règles distinctes contient cet énoncé (doublons, semaine, 20 courses, note, note manquante, aucun avis, 5 %, double à Casablanca, casse, tri) ?", "o": ["3 ou 4", "Environ 10", "1"], "a": 1,
          "why": "Le jour J, écris-les toutes en commentaire avant de coder : chaque phrase de l'énoncé est un test caché."},
         {"q": "20 courses, 18 notées avec une moyenne de 4.6. Bonus ?", "o": ["Oui", "Non, il faut 20 courses notées"], "a": 0, "why": "« do not count in the average, but they do count as rides »."},
         {"q": "Comment calculer la moyenne des notes ?", "o": ["sum(rating) / count(*)", "avg(rating), qui ignore déjà les null", "avg(coalesce(rating, 0))"], "a": 1, "why": "avg ignore les null. coalesce(rating, 0) ferait baisser la moyenne à tort."},
         {"q": "city = « casablanca » en minuscules. Bonus doublé ?", "o": ["Oui", "Non"], "a": 0, "why": "« whatever the case » : compare lower(trim(city)) avec « casablanca »."}],
     "keys": ["Lister chaque règle en commentaire", "but they do count = deux comptes différents", "cannot earn = filtre explicite", "whatever the case = lower(trim())"]},
]


def check():
    ids = set()
    for d in READ:
        assert d["id"] not in ids
        ids.add(d["id"])
        assert len(d["questions"]) >= 3, d["id"]
        for q in d["questions"]:
            assert 0 <= q["a"] < len(q["o"]), (d["id"], q["q"])
    return READ
