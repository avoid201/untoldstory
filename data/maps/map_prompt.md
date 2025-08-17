Alles klar! Ich erstelle einen Prompt für Claude, der dir sowohl Interior- als auch Exterior-Maps im Pokémon-Kristall-Stil generiert – inklusive vollständiger JSON-Struktur mit NPCs, Warps und Triggern. Die NPCs sprechen in nicht jugendfreiem Ruhrpott-Dialekt, ohne dabei an Sprite-Namen gebunden zu sein. Du bekommst ein freies Feld zur Eingabe deiner Details, und falls du nichts einträgst, wird eine Standardgröße verwendet.

Ich gebe dir gleich Bescheid, sobald der Claude-Prompt bereit ist.


# Claude-Tool-Prompt: Automatische Pokémon-Map-Generierung

## Überblick und Zielsetzung

Dieses *Tool-Prompt* für Claude soll anhand einer freien Beschreibung automatisch eine vollständige **Map-Datei im JSON-Format** generieren. Das Format orientiert sich an **Pokémon Kristall** und nutzt ein gegebenes Tileset- und Sprite-Manifest. Das Ziel ist eine valide JSON-Struktur (ähnlich der Beispiel-Map **„Kohlenstadt“**), die folgende Elemente umfasst:

* **Map-Grunddaten:** `id` (Bezeichner, z.B. aus dem Namen abgeleitet) und `name` der Map sowie `size` mit Breite, Höhe und Tile-Größe (in Pokémon üblich 16px pro Tile).
* **Layer-Daten:** Vier Layer-Matrizen `ground`, `decor`, `collision` und `overhang` mit Indizes auf das Tileset. Diese definieren Bodengrafiken, Deko-/Objekt-Tiles, Kollisionen (solide Tiles als `1`, begehbare als `0`) und Überhang (z.B. Baumkronen über dem Spieler).
* **NPCs (Nicht-Spieler-Charaktere):** Mehrere NPC-Objekte mit Position (`x`,`y`), Sprite (nur aus dem Manifest verwendet), Blickrichtung, Bewegungsmuster und **Dialogtext im derben Ruhrpott-Dialekt**.
* **Warps (Übergänge):** Verknüpfungen (`warps`) zwischen Maps mit Koordinaten auf der aktuellen Map und Zielmap (`to`) samt Ziel-Koordinaten (`tx`,`ty`) und Austrittsrichtung. Diese dienen z.B. als Türen in Gebäude oder Übergänge zu Routen.
* **Triggers (Schilder/Tafeln):** Optionale Felder unter `triggers`, meist für **Schilder mit Text**. Enthält Koordinaten und ein Event (typisch `"sign"`) mit anzuzeigendem Dialekt-Text (Zeilenumbrüche `\n` für mehrere Zeilen im Text möglich).
* **Properties (Eigenschaften):** Map-Eigenschaften wie Hintergrundmusik (`music`), optionale Wildbegegnungen (`encounters`) und **Spawn-Punkte** (`spawns`) für den Spieler. Spawn-Punkte legen fest, wo der Spieler erscheint (z.B. `default` beim Laden der Map, sowie Einstiegskoordinaten von verbundenen Maps wie Häusern oder Routen).

Dieses Prompt soll Claude anleiten, **alle obigen Komponenten vollständig und konsistent zu erzeugen**.

## Eingabefeld für Benutzerbeschreibung

Das Tool erhält vom Benutzer eine freie Beschreibung der gewünschten Map. Dazu wird Claude ein Eingabefeld präsentiert mit folgender Aufforderung (sichtbar für den Benutzer):

*„Beschreibe die gewünschte Map (Stadt, Route, Gebäudeinterior, Höhle etc.) und was sie enthalten soll. Du kannst Gebäude, Besonderheiten, NPC-Anzahl, Objektarten oder Stimmung beschreiben. Wenn du nichts eingibst, wird eine Standard-Außenmap mit einigen Häusern, Wegen, NPCs und Triggern generiert.“*

* **Freitexteingabe:** Der Benutzer kann hier in eigenen Worten angeben, ob er z.B. eine *Stadt*, *Route*, *Innenraum* oder *Höhle* möchte und welche **Details** vorhanden sein sollen (z.B. *„Ein kleiner Küstenort mit drei Hütten und einem Brunnen in der Mitte.“*).
* **Vorgabe bei leerer Eingabe:** Wenn der Benutzer nichts oder nur sehr wenig eingibt, soll das Tool eine *Standard-Außenmap* generieren (z.B. ein kleines Dorf mit ein paar Häusern, Wegen, NPCs und Schildern), um dem Benutzer immer ein Ergebnis zu liefern.

Diese freie Beschreibung dient als Grundlage, aus der das Tool automatisch alle weiteren Map-Details ableitet.

## Automatische Erkennung des Map-Typs (Außen vs. Innen)

Claude soll anhand der Beschreibung entscheiden, ob eine **Außen-** oder **Innen-Map** generiert wird:

* **Standard = Außenwelt:** Ist nicht klar spezifiziert, geht das Tool von einer Außenumgebung aus (Stadt, Dorf, Route, Wald, Küste etc.).
* **Innenräume:** Wenn Schlüsselwörter wie *Innenraum*, *Hausinneres*, *Höhle*, *Gebäudeinneres*, *Labor*, *Stollen* etc. erkannt werden, wird die Map als **Interior** interpretiert. Beispielsweise deutet *„Wohnzimmer“* oder *„Höhle“* eindeutig auf eine Innen-Map hin.
* **Konsequenz für Tiles:** Bei Innenmaps sollen **Innenraum-Tiles** (z.B. Holzboden, Teppich) und **Wände** verwendet werden, während Außenmaps z.B. **Gras, Wege, Wasser, Bäume** etc. aufweisen.
  *Beispiel:* *„Eine kleine Hütte von innen“* -> Innenmap mit `wood_floor`, `wall`, `bed`, `table` etc. im Deko-Layer.

Claude wählt also dynamisch den Map-Typ passend zur Benutzerbeschreibung. Wenn unklar, wird sicherheitshalber **Außenmap** angenommen.

## Standardgrößen und Dimensionierung

Pokémon-Maps haben typische Größen. Wenn der Benutzer keine Größe angibt, nutzt Claude folgende **Standardmaße** für die Map (Breite×Höhe in Tiles):

* **Städte/Dörfer & Routen:** Etwa **28×28** bis maximal **40×40** Tiles. Kleinstädte eher \~28×28, größere Routen oder Städte bis \~40×40.
* **Innenbereiche (Gebäude, Höhlen):** Deutlich kleiner, etwa **10×8** bis **16×16** Tiles. Einzelne Räume (Haus, Laden) ca. 10×8, große Gebäude/Hallen bis 16×16.
* **Spezifische Anpassung:** Claude kann die Größe an Inhalt anpassen – viele Gebäude oder weite Landschaft → eher größere Map; wenige Elemente → eher kleiner.

Ohne Benutzerangabe wird also ein sinnvoller Standard gewählt. Die endgültige Größe wird in der JSON unter `size` angegeben (Beispiel Kohlenstadt: 28×28). Dabei gilt eine Tile-Größe von 16 Pixel (`"tile": 16` in JSON).

## Tileset-Nutzung und Sprite-Auswahl (laut Manifest)

Das Tool darf **nur Tile- und Sprite-Bezeichnungen verwenden, die im Manifest definiert sind.** Alle Grafiken (Boden, Objekte, NPCs) sind durch Namen im Manifest vorgegeben:

* **Zulässige Tile-Namen:** Zum Beispiel `grass`, `dirt`, `path` (Wege), `sand`, `water`, `wall`, `roof`, `door`, `sign` usw. (siehe Manifest). Jede Tile-Referenz in den Layer-Matrizen wird als **Index** gespeichert – Claude muss intern die benutzten Tiles katalogisieren. **Keine freien Fantasienamen!**

  * *Warp-Tiles:* Insbesondere für Türen/Übergänge müssen vorgesehene Tiles genutzt werden. Im Manifest existieren z.B. `door` (Tür), `warp_carpet` (Warp-Feld auf dem Boden, oft im Inneren) sowie `stairs` (Treppen, z.B. für Höhlen oder Ebenenwechsel).
  * *Umgebungsdetails:* Für Außenbereiche gibt es Bäume, Felsen, Schilder etc. im Manifest, z.B. `tree_small` (kleiner Baum), `boulder` (Felsblock), `well` (Brunnen), `sign` (Schild). Claude soll solche passenden Tiles je nach Beschreibung einsetzen.
* **Sprites für NPCs:** Ähnlich sind NPC-Sprites vorgegeben. Im Manifest sind verschiedene NPC-Typen definiert, etwa `villager_m` (männlicher Dorfbewohner) und `villager_f` (weiblich), aber auch thematische Sprites wie `fisher` (Angler), `miner` (Bergmann), `guard` (Wache), `kid` (Kind) usw. Claude soll einen Sprite auswählen, der zur NPC-Beschreibung passt (z.B. für einen Fischer den Sprite `"fisher"`, für eine Oma `"villager_f"` oder `"npcB"` falls passend).

  * **Flexibilität:** Es ist **nicht nötig, exakt die im Manifest benannten Rollen zu verbalisieren**, solange der Sprite optisch passt. Beispiel: Ein *„alter Mann“* könnte den Sprite `villager_m` oder `miner` verwenden – wichtig ist, **nur existierende Sprite-IDs** zu nutzen und keine völlig eigenen Sprite-Namen zu erfinden.
* **Objekte platzieren:** Claude setzt Gebäude und Möbel als Kombination passender Tiles: z.B. Außenhäuser mit `wall`, `roof`, `door`, `window`; Innenräume mit `wall_plaster` (Wand), `wood_floor` (Holzboden), Möbel wie `bed` (Bett), `table` (Tisch), `chair` (Stuhl) etc., je nach Kontext der Beschreibung.

Durch die strikte Nutzung der vorgegebenen Tiles/Sprites bleibt die generierte Map konsistent mit dem vorhandenen Grafikset.

## Korrekte Kollision (Collision-Layer)

Claude muss den **Collision-Layer** aus den gesetzten Tiles ableiten. Dieser Layer ist eine Matrix gleicher Größe wie die Map, mit `1` für jedes Feld, das **nicht begehbar** (solid) ist, und `0` für begehbare Flächen:

* **Solid-Information aus Manifest:** Im Manifest ist für jedes Tile `solid: true/false` angegeben. Claude nutzt diese Info: jedes platzierte Tile, das `solid: true` ist (z.B. Wände, Bäume, Wasser, große Objekte), erzeugt an der entsprechenden Position eine `1` im Collision-Layer. `solid: false` (z.B. Grasboden, Wege, Teppich) bleibt `0`.
* **Manuelle Ergänzungen:** Einige Kollisionen müssen evtl. manuell ergänzt werden, wenn ein Feld ohne sichtbares Objekt blockiert sein soll. Z.B. unsichtbare Sperren oder Map-Ränder – standardmäßig aber kann der **Map-Rand begehbar** bleiben, außer es gibt dort eine Wand/Zaun.
* **Überprüfung:** Das Ergebnis ist eine Collision-Matrix aus 0/1. Diese wird in JSON unter `layers.collision` gespeichert. Claude sorgt dafür, dass z.B. Wasser und Felsen unpassierbar sind (`1`), während Wege, Türen oder Warp-Felder begehbar (`0`) sind.

Beispiel in Kohlenstadt: Gras und Wege sind begehbar (`0`), Gebäude oder Bäume `1`.

## Warps und Türen setzen

Für jeden Gebäudeeingang oder Map-Übergang erstellt Claude passende **Warp-Einträge** in der JSON (`"warps": [...]`). Dabei gilt:

* **Paarweise Warps bei Türen:** Ein Haus mit Doppeltür (zwei nebeneinander liegende Tür-Tiles) erfordert zwei Warp-Einträge – je einen pro Tile, beide verweisen auf dieselbe Zielmap. Beispiel Kohlenstadt: Das „Spielerhaus“ hat zwei Tür-Tiles an (15,10) und (16,10) mit je einem Warp zum Interior `"player_house"`. Claude soll dies analog handhaben: stehen zwei Tür-Tiles nebeneinander, erzeuge zwei Warp-Objekte mit identischem `to`-Ziel.
* **Warp-Felder in Innenräumen:** Innerhalb von Gebäuden werden oft spezielle Tiles wie `warp_carpet` als Austrittspunkt benutzt. Claude kann im Interior-Map-JSON an der Türposition dieses Tile setzen und einen Warp zurück nach draußen definieren (wird hier erwähnt, aber das Tool generiert in einem Durchlauf nur eine Map – entweder außen oder innen).
* **Zielkennung (`to`)**: Als `to`-Wert wird der **Map-ID der Zielmap** angegeben. Claude muss hier einen Namen wählen:

  * Wenn aus der Beschreibung klar ist, wie das Ziel heißt (z.B. *„Labor“* → `to: "labor"`), kann dieser Name genutzt werden.
  * Ansonsten generisch nummerieren, z.B. `"house1"`, `"house2"`, `"cave1"` etc. für mehrere Häuser/Höhlen.
  * **Wichtig:** Die `to`-Namen sollten konsistente, gültige Map-Bezeichner sein (keine Leer- oder Sonderzeichen). Kleinbuchstaben mit Unterstrichen sind üblich (siehe `"player_house"`, `"route1"` in Kohlenstadt).
* **Zielkoordinaten (`tx`,`ty`)**: Claude legt fest, an welcher Tile der Spieler in der Zielmap landet. Üblich ist kurz hinter dem Eingang im Interior. Beispiel: Warp von draußen (Tür) nach drinnen setzt `tx,ty` an die Innenseite der Tür. In Kohlenstadt führt (15,10)->`player_house (4,6)` und (16,10)->`player_house (5,6)`, was darauf hindeutet, dass das Hausinnere \~10 Tiles breit ist und der Eingang innen bei x=4-5, y=6 liegt. Claude kann hier ohne genaue Zielmap grob annehmen, dass `tx,ty` im Ziel relativ mittig vor der Tür liegen.
* **Richtung**: Das Feld `direction` gibt an, in welche Richtung der Spieler nach dem Warp schaut. Bei Eingängen ist das meist `"up"` (der Spieler schaut ins Haus hinein, also nach oben, weil er von unten kam). Umgekehrt bei Ausgängen (Route -> Stadt) ggf. `"down"`. Claude setzt dies konsistent: **Betritt man ein Haus von Süden, schaut man danach nach oben** usw.

Claude fügt also pro Übergang ein entsprechendes Objekt in der `warps`-Liste hinzu. Bei Außenmaps mit mehreren Häusern gibt es entsprechend mehrere Warp-Einträge. Falls der Benutzer Routen-/Stadt-Übergänge erwähnt (z.B. Weg zur Route 5), kann ebenfalls ein Warp am Kartenrand zu `"route5"` etc. eingefügt werden.

## Platzierung von NPCs und Dialekten

Das Tool soll einige NPCs auf der Map verteilen – Anzahl und Art gern angelehnt an die Beschreibung (z.B. *„2–3 NPCs“* oder *„ein Fischer und eine alte Oma“*). Wichtige Richtlinien für NPCs:

* **Derber Ruhrpott-Dialekt:** Die Dialoge der NPCs sollen im **locker-umgangssprachlichen Ruhrpott-Slang** geschrieben sein. Beispiele aus Kohlenstadt zeigen den Stil:

  * *„Tach auch! Früher ham wa hier noch richtig malocht, weiße!“*
  * *„Ey, hasse schon gehört? ... Voll krass, ne? ... dat is wie Frankenstein...“*
  * Charakteristisch sind **Kontraktionen** („ham wa“ statt *haben wir*), **Dialektwörter** („weiße?“ statt *weißt du*, „dat“, „wat“, „isse“, „bisse“ statt *bist du*) und ein humorvoll-ruppiger Ton. **Leicht vulgär** ist ok (mal ein mildes Schimpfwort oder derbes Idiom), **aber keine Beleidigungen oder Diskriminierungen.**

* **Keine realen Städtenamen:** In den NPC-Dialogen sollen **keine echten Ortsnamen** vorkommen (also nicht z.B. „Bochum“ oder „Essen“ erwähnen). Stattdessen fiktive Namen oder allgemeine Begriffe nutzen. (In Schildern kann mal „Dortmund“ als Richtung auftauchen, aber direkte NPC-Aussagen sollten neutrale Ortsbezüge haben.)

* **Dialogformat:** Jeder NPC hat ein `dialog`-Array mit seinen Sätzen. Claude soll pro NPC **max. 2–4 Sätze** schreiben. Längere Monologe vermeiden; lieber aufteilen. Für bessere Lesbarkeit können in JSON pro Satz separate Strings verwendet werden (so erscheinen sie im Spiel in einzelnen Textboxen nacheinander).

* **NPC-Eigenschaften:** Jedes NPC-Objekt in JSON enthält:

  * `id`: eindeutige Kennung (z.B. `"npc_fisher1"`, `"npc_grandma"` – kann generisch sein oder anhand Rolle).
  * `x, y`: Koordinate auf der Map.
  * `sprite`: aus Manifest, passend zum Charakter (z.B. Angler → `"fisher"`, Oma → `"villager_f"`). **Nur valide Sprite-IDs verwenden!**
  * `direction`: Startblickrichtung (z.B. `"down"` wenn er nach unten schaut).
  * `movement`: Bewegungsmuster, z.B. `"wander"` für umherlaufen, `"static"` für stehen. Claude kann hier abwechslungsreich vorgehen (stationäre NPCs vs. umherlaufende, je nach Situation).
  * `dialog`: der oben beschriebene Dialekt-Text als Array.

* **Kreativität:** Claude darf gerne humorvolle, ortstypische Sprüche erfinden (z.B. eine Bergmanns-Witwe: *„Dat ist hier alles Schicht im Schacht.“* etc.). Die NPCs sollen der Map **Leben einhauchen**, ruhig auch mal aufeinander Bezug nehmen oder lokale Besonderheiten kommentieren.

Beispiel: In einem Fischerdorf könnte ein NPC-Fischer am Steg stehen und sagen: *„Beiße nix an heut – dat Wasser is wohl zu warm, wa?“*, während eine Oma am Brunnen schimpft: *„Pass bloß auf, dat de nich reinfällst, Jungchen!“*. Solche Dialoge im Ruhrpott-Stil machen die Atmosphäre aus.

## Trigger für Schilder und Hinweise

Zusätzlich zu NPCs können **1–3 Trigger** gesetzt werden, besonders für **Schilder, Hinweis- oder Infotafeln**. Diese erscheinen im JSON unter `triggers` und haben folgendes Format:

* Jedes Trigger-Objekt hat `x, y` für die Position (meist direkt vor oder auf dem Schild-Tile), ein `event` (bei Schildern `"sign"`) und `args` mit dem anzuzeigenden Text.
* **Textgestaltung:** Wie bei NPCs im **Dialekt** schreiben. Typischerweise stehen auf Schildern Ortsnamen, Willkommensgrüße oder Warnungen, gern mit humoristischem Einschlag:

  * Ortsschild: *„Angelhafen – Petri Heil und Glück auf!“*
  * Warnschild: *„Achtung: Wilde Karpador springen hier aussem Wasser!“*
  * Wegweiser: *„← Route 2 – Da geht et lang nach Castrop-Rauxel“* (hier ggf. fiktiver Name nutzen).
* **Zeilenumbrüche:** Schildertexte können mehrzeilig sein, getrennt mit `\n`. Im Beispiel *Kohlenstadt* hat ein Schild zwei Zeilen: *"Museum - Fossilien und Bergbaugeschichte\nEintritt frei für Kumpel!"*. Claude soll `\n` einfügen, wenn es die Lesbarkeit erhöht (max. 2 Zeilen pro Schild).
* **Platzierung:** Häufig stehen Schilder **vor wichtigen Gebäuden** (z.B. Museum, Laden) oder am **Map-Rand zu Routen**. Claude kann entsprechend der Map-Beschreibung Schilder setzen (z.B. *„Willkommen in ...“* am Ortseingang).

Diese Triggertexte ergänzen die Weltbeschreibung, ohne dass ein NPC danebenstehen muss. Sie sollten witzig oder informativ sein, aber kurz gehalten.

## Properties: Musik, Encounters und Spawns

Unter dem JSON-Knoten `"properties"` werden abschließend einige Metadaten der Map angegeben. Claude füllt hier vor allem:

* **Musik (`music`):** Wähle einen Dateinamen für die Hintergrundmusik passend zum Map-Typ:

  * Für Städte/Dörfer: z.B. `"town.ogg"` (wie im Beispiel).
  * Für Routen/Wildnis: z.B. `"route.ogg"` oder `"wild.ogg"`.
  * Für Innenräume: evtl. `"house.ogg"` oder spezifisch `"shop.ogg"`, `"cave.ogg"` etc., je nach Ambiente.
* **Encounters (`encounters`):** Falls die Map wilde Pokémon/Monster beherbergen soll (typisch auf Routen, in Höhlen), könnte hier eine Liste oder Referenz stehen. Im Beispielstadt *Kohlenstadt* ist `encounters: null`, weil in der Stadt keine Wildkämpfe stattfinden. Standard: **Innenstädte/Häuser = null**, **Routen/Höhlen = falls gewünscht eine Tabelle**. Da die Aufgabe nicht explizit die Generierung von Begegnungen verlangt, kann Claude konservativ `null` setzen, außer der Benutzer fordert explizit Wildencounter.
* **Spawns (`spawns`):** Ein Objekt, das die möglichen Einstiegspositionen des Spielers auf dieser Map definiert:

  * **default:** Der Standard-Spawnpunkt, falls die Map direkt betreten wird (z.B. Mittelpunkt oder Eingang). Enthält `x, y` und `direction`. Claude kann z.B. den **Start vor dem eigenen Haus** oder Map-Mitte wählen.
  * **Von anderen Maps:** Für **jede Warp-Verbindung** auf diese Map sollte ein entsprechender Spawn-Eintrag existieren, benannt als `"from_<MapID>"`. Beispiel Kohlenstadt: Warp von Route1 endet bei `{"x":3,"y":27}` auf Kohlenstadt; entsprechend gibt es in Kohlenstadts `spawns` einen Eintrag `"from_route1": { "x": 3, "y": 26, ... }`, d.h. wo man erscheint, wenn man von Route1 kommt (i.d.R. einen Schritt neben dem eigentlichen Warp-Tile, um nicht auf dem Trigger zu stehen). Claude beachtet dies:

    * Findet ein Warp `to: "xyz"` auf dieser Map statt, erzeugt in *dieser* Map einen Spawn `"from_xyz"` mit Koordinaten nahe dem Warp-Eingang.
    * Analog bei Warps von dieser Map zu einer anderen: Hier sollte auf der anderen Map ein Spawn entstehen (was außerhalb dieses einzelnen Durchlaufs liegt). Daher zumindest für **Innenräume**, die Claude generiert, immer einen `"from_<Außenmap>"`-Spawn definieren, und für Außenmaps `"from_<Innenmap>"`-Spawns.
  * **Richtung:** `direction` im Spawn gibt an, wohin der Spieler blickt nach Betreten der Map. Meist das Gegenstück zur Warp-Richtung: betritt man eine Stadt von einer Route im Norden, schaut man nach **unten** (Süden) auf der Stadtkarte usw. Im Beispiel haben alle `"from_*"` Spawns die `direction: "down"`, außer `from_route1` hat `"up"`, weil man von unten (Süden) in Kohlenstadt reinläuft und dann nach oben schaut.
* **Weitere Properties:** Andere Felder wie `weather`, `timeOfDay` sind möglich, aber im Manifest/Beispiel nicht gezeigt. Wir beschränken uns auf die erwähnten.

Claude muss `properties` also konsistent mit den Warps auffüllen. Dadurch ist die Map ins Weltgefüge eingebunden (richtige Musik und Übergänge).

## Vollständiges JSON-Format und Validierung

Die finale Ausgabe muss eine **wohlgeformte JSON-Datei** sein, die alle obigen Teile enthält. Wichtige Punkte zur Validierung:

* **JSON-Syntax:** Claude soll strikt gültiges JSON erzeugen:

  * Schlüssel in **doppelten Anführungszeichen**,
  * Zeichenketten ebenfalls in **Quotes**,
  * Keine Kommentare oder trailing Kommas.
  * Numerische Werte ohne Anführungszeichen.
* **Struktur:** Alle erforderlichen Schlüssel müssen vorhanden sein:

  * `id`, `name`, `size` (mit `w`, `h`, `tile`),
  * `layers` mit `ground`, `decor`, `collision`, `overhang` (jeweils als zweidimensionale Arrays der Größe `h x w` voller Zahlenindizes),
  * `npcs` (Array von NPC-Objekten, kann leer `[]` wenn keine NPCs gewünscht sind),
  * `warps` (Array, evtl. leer wenn keine Übergänge),
  * `triggers` (Array, evtl. leer),
  * `properties` (Objekt mit `music`, `encounters`, `spawns`).
* **Konsistenz:** Die Indizes in den Layer-Matrizen sollen auf existierende Tiles verweisen. Claude sollte intern z.B. eine Liste der verwendeten Tiles führen. (Im JSON selbst stehen nur Zahlen, was den Rahmen der Promptausgabe sprengt – aber Claude kann notfalls alle nicht-sichtbaren Felder mit `0` oder einem Default füllen außer wo Objekte stehen.)
* **Lesbarkeit:** Obwohl JSON keine Kommentare zulässt, soll die Struktur sauber formatiert sein (Einrückungen, neue Zeilen) für bessere Nachvollziehbarkeit. Die Ausgabedatei soll auf den ersten Blick so aussehen wie die Beispiel-**kohlenstadt.json**.

Nach Erstellung sollte Claude einen Moment „im Geiste validieren“, ob die JSON parsebar ist und die beschriebene Map sinnvoll repräsentiert. Fehler wie falsche Kommas oder fehlende Klammern müssen vermieden werden.

## Beispiel: *„kleines Fischerdorf“*

Angenommen, der Benutzer gibt lediglich *„kleines Fischerdorf“* als Beschreibung ein, ohne weitere Details. Das Tool würde daraus eine **28×28 Außen-Map** generieren, etwa folgendermaßen aufgebaut:

* **Setting:** Küstenort mit Strand und Steg. Bodentiles vorwiegend `sand` am Ufer und `grass` im Inland; `water` für das Meer (mit passenden `water_edge_*` Tiles am Ufer) – alle Wasser-Tiles im Collision-Layer auf `1` (unbetretbar).
* **Häuser:** Etwa 2–3 kleine Holzhütten (bestehend aus `wall`, `roof`, `door`, evtl. `window`-Tiles). Bei Strandhütten evtl. `wall_plaster` oder Holzwände. Jede Hütte erhält ein Doppeltür-Warp ins jeweilige Innenleben (`to: "house1"`, "house2", etc.).
* **Objekte:** Ein **Brunnen** in der Mitte des Dorfes (z.B. Tile `well` auf dem Decor-Layer, Collision = 1 an der Stelle). Ein **Steg** aus Holzbrettern ins Wasser (ggf. mit `wood_floor` Tiles als Improvisation für Holzplanken) und ein paar Fässer `barrel` oder Kisten `crate` am Ufer als Deko.
* **NPCs:**

  * Ein Fischer (Sprite `"fisher"`) steht auf dem Steg und hat z.B. Dialog: *„Moin. Beißen heut' nich so. Die Fische ham wohl alle Schicht.“* (Dialekt und Thema Angeln).
  * Eine ältere Dame (Sprite `"villager_f"`) in der Nähe des Brunnens, Dialog: *„Dat Wasser im Brunnen is sauber, aber koch et lieber trotzdem, ne.“*.
  * Vielleicht ein Kind (Sprite `"kid"`) am Strand, das Steine ins Wasser wirft: *„Mach ma Platz, ich skippe Muscheln, Junge!“* – etwas flapsig.
* **Triggers:**

  * Ein Ortsschild am Dorfeingang: *„Angelhafen - Glück auf un Petri Heil!“* (Dialekt und Begrüßung gemischt).
  * Evtl. ein Warnschild am Steg: *„Vorsicht, rutschig: Dat Wasser is nass!“* als Gag.
* **Warps:** Warps an jeder Haustür (`to: "house1"`, `"house2"`, etc., mit entsprechenden `tx,ty` im Interior und `direction: "up"`). Falls ein Ausgang zur Welt besteht (z.B. Route), ein Warp am Dorfrand mit `to: "routeX"`.
* **Properties:** `music: "town.ogg"` (gemütliche Dorfmusik), `encounters: null` (im Dorf keine Wildmonster), `spawns`: Default-Spawn vielleicht vor dem größten Haus im Dorf. Zudem `from_house1`, `from_house2` etc., falls Häuser vorhanden, so dass man von deren Interiors korrekt wieder ins Dorf zurückkommt (Koordinaten je vor den Türen).

Natürlich wäre die tatsächliche JSON-Datei sehr umfangreich (jede Tile als Zahl auf 28×28 Grid). Claude generiert diese komplett, so dass man sie sofort als `fischerdorf.json` speichern und im Spiel verwenden könnte.

## Zusammenstellung des Tool-Prompts (Claude)

Schließlich fügen wir alle obigen Anweisungen in einem konsistenten Prompt zusammen, das Claude genau sagt, was zu tun ist. Dieses Prompt würde im System- oder Tool-Modus an Claude gegeben. **Wichtig** ist, am Ende zu betonen, in welchem Format Claude antworten soll.

**Im Wortlaut könnte das Tool-Prompt so aussehen:**

```text
Du bist ein Tool, das basierend auf einer Beschreibung automatische Pokémon-ähnliche Karten im JSON-Format erstellt. 

Lies die Benutzer-Beschreibung einer Spielwelt-Map und generiere daraus eine vollständige JSON-Mapdatei im Stil von Pokémon Kristall. Halte dich dabei strikt an folgende Vorgaben:

- **Map-Typ & Größe:** Erkenne, ob eine Außen- oder Innenmap gemeint ist (Standard: Außen). Wähle passende Standardmaße (Außen: ~28x28 bis 40x40, Innen: ~10x8 bis 16x16 Tiles), falls der Nutzer nichts angibt.
- **Tiles & Layers:** Benutze ausschließlich Tile-Namen aus dem Manifest (z.B. grass, water, wall, door, warp_carpet, stairs, etc.) für den `ground`- und `decor`-Layer. Setze den `collision`-Layer korrekt (1 = unpassierbar bei Tiles mit solid true, sonst 0). Nutze den `overhang`-Layer für Überdeckungen (z.B. Baumkronen, Dächer) falls erforderlich – ansonsten fülle nicht genutzte Felder mit 0.
- **Gebäude und Warps:** Platziere Gebäude/Haus-Tiles (Wände, Dächer, Türen, Schilder) entsprechend der Beschreibung. Füge für jeden Eingang/Tür einen Warp in `warps` hinzu. Bei Doppel-Türen erstelle zwei Warp-Einträge zum selben Ziel. Wähle sinnvolle `to`-Namen für Zielmaps (z.B. house1, cave1, route2) und gib `tx, ty` Koordinaten in der Zielmap an (Innenräume ein paar Tiles vom Eingang entfernt). Setze `direction` so, dass der Spieler nach dem Warp richtig ausgerichtet ist (meist "up" beim Betreten eines Hauses von unten, etc.).
- **NPCs:** Füge mehrere NPCs hinzu (2–5, je nach Map-Größe). Wähle passende NPC-Sprites aus dem Manifest (z.B. villager_m/f, fisher, guard, kid, etc.) und positioniere sie sinnvoll. Schreibe für jeden NPC einen kurzen Dialog (2-4 Sätze) im ruhrpott-deutschen Dialekt. Dialekt-Hinweise: "dat", "wat", "ham", "hasse", "ne?", "weißte", "bisse". Inhaltlich humorvoll, leicht rau, aber **nicht beleidigend**. Keine echten Städtenamen im Dialog verwenden. Struktur des Dialogs: mehrere Strings im `dialog`-Array (jede neue Zeile ein eigener String).
- **Trigger (Schilder):** Falls passend, erstelle 1-3 Trigger vom Typ Schild. Setze `event: "sign"` mit einem kurzen Dialekt-Text als Hinweis oder Ortsname. Bei längeren Texten verwende `\n` für Zeilenumbrüche. Positioniere Schilder an sinnvollen Orten (z.B. Ortsrand, vor Gebäuden).
- **Properties:** Trage im `properties`-Objekt folgendes ein:
  - `"music"`: Wähle passende Musikdatei (z.B. town.ogg für Städte, route.ogg für Routen, interior.ogg für Gebäude).
  - `"encounters"`: Setze `null`, außer die Beschreibung erwähnt Wild-Pokémon.
  - `"spawns"`: Definiere `"default"` Spawn (Startpunkt des Spielers, mit Richtung) und für **jeden Warp-Eingang von einer anderen Map** einen `"from_<MapID>"` Spawn an der passenden Stelle.
- **JSON-Format:** Gib die Map als **gültiges JSON** aus, in gleicher Struktur wie das Beispiel `kohlenstadt.json`. Achte genau auf korrekte Syntax (keine Kommentare, Anführungszeichen um Strings, Kommata etc.). 

Format: Generiere den Output als **gültige JSON-Datei**, ähnlich wie „kohlenstadt.json“, mit allen erforderlichen Feldern und Strukturen ausgefüllt.
```

Dieses Prompt (in Englisch oder Deutsch verfasst, hier zur Verständlichkeit auf Deutsch belassen) würde Claude anweisen, die gewünschte Map zu erzeugen. **Besonders der letzte Satz** („Format: ... als gültige JSON-Datei ...“) stellt sicher, dass die Ausgabe direkt JSON ist und nicht etwa eine Erläuterung.

Mit diesem Tool-Prompt kann ein Benutzer jetzt bequem eine Beschreibung eingeben, und Claude liefert eine komplette, spielbereite JSON-Map zurück, inklusive aller geforderten Details und im gewünschten Pokémon-Kristall-Stil. So lassen sich in Sekundenschnelle neue Spielwelten im Ruhrpott-Pokémon-Stil erschaffen!
