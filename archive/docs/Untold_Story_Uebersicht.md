# Untold Story – Spielübersicht

**Titel:** Untold Story  
**Genre:** 2D-Top-Down-RPG / Monster-Sammelspiel / Story-Adventure  
**Dialekt & Ton:**Ruhrpott-Slang as Flavor**  
**Technologie:** Python 3.13.5, pygame-ce 2.5.5, JSON-basiert

---

## 1. Kurzbeschreibung

Spieler sammelt, zähmt und trainiert prähistorische, gegenwärtige und Zukunftsmonster, kämpft rundenbasiert à la *Dragon Quest Monsters*, löst Story-Quests und Trials, und deckt das Geheimnis um Zeitrisse auf. Neben klassischen Trainerkämpfen gibt es wilde Begegnungen mit Scout-/Zähm-Mechanik und am Ende eine Liga. Legendäre Monster beeinflussen das Weltgeschehen.

---

## 2. Story (Bis erstes Trial & Ausblick)

- Start in **Kohlstadt** im Spielerhaus.  
- Professor erweckt zwei Fossilien (Starter-Monster).  
- Einführung durch Rivalen-Kampf (Kalle) und Tutorial (Zähmkampf), dann erstes Trial 
- Ziel: 10 Trials absolvieren, Zeichen sammeln, Liga erreichen.  
- Antagonistengruppe experimentiert mit Zeitrissen, um stärkere Monster aus der Zukunft zu holen.  
- Ab Trial 5 tauchen **Zeitrisse** auf: Zukunftsmonster erscheinen, auch bei anderen Zähmern.  
- Der Professor wird verdächtigt und inhaftiert; der Spieler muss ihn befreien.  
- Finale: Zeitrisse schließen + Liga abschließen.  
- **Legendäre Monster:** 11 besondere Einheiten (5er Pantheon, 3er Konstellation, 3 Einzeln), mit narrativem Einfluss.

---

## 3. Kernmechaniken

### Kampf
- Rundenbasiert, jedes aktive Monster erhält Aktionen (standard: 1, erweiterbar durch Traits).  
- **Initiative:** Geschwindigkeit + leichte Zufallskomponente.  
- Aktionen: **Angriff**, **Zähmen** (nur gegen wilde), **Items**, **Auto (KI)**, **Flucht** (nur wild).  
- **Typen & Effektivität:** Mehrere Typen mit Stärken/Schwächen.  
- **Stages/Buffs/Debuffs:** ATK, DEF, SPD, MAG, RES, ACC, EVA.  
- **Status:** Schlaf, Paralyse, Gift etc. beeinflussen Ablauf.  
- **Kritische Treffer** und Treffergenauigkeit.  
- **Trainer- vs. Wilde Kämpfe:** Wilde Kämpfe erlauben Scouten/Zähmen; Trainer-Monster sind davon ausgeschlossen.  
- **Battle Log:** Klarer Textfeed über Aktionen, Treffer, Effekte, Zähm-Fortschritt, KOs.

### Scouten / Zähmen
- Aktion „Zähmen“ im Kampf gegen wilde Monster.  
- Chance basiert auf Offense (ATK/WIS) des Teams relativ zur Defense/HP des Ziels plus Status- & Item-Boni.  
- Items (z. B. Fleisch) verbessern die Zähm-Chance temporär.  
- Status-Effekte wie Schlaf/Paralyse erhöhen Erfolg.  
- Bei Erfolg wird das wilde Monster direkt ins Team übernommen.  
- Trainer-Monster **nicht** zähmbar.

### Monster-System
- **151 Monster** insgesamt, Erweckte prähistorische Monster (Fossilien die wiedererweckt wurden, wenige erweckte in der Welt, keine in der Wildnis, bis sie auch aus den Zeitrissen später in der Story kommen), Normale Gegenwartsmonster (Jahr 2025 (aktuell) in der Wildnis und bei Zähmen zu finden), Zukunftsmonster aus Zeitrissen (erst später verfügbar, Eintrag existiert aber schon)
- **12 Typen:** Feuer, Wasser, Luft, Erde, Pflanze, Bestie, Energie, Mystisch, Chaos, Seuche, Göttlich, Teuflisch. (Teuflisch und Göttlich nur bei Rang X und SS,bei Rang E bis A sind die anderen Typen gleichmäßig verteilt)  
- **Ränge:** F, E, D, C, B, A, S, SS, X (verteilte Häufigkeiten:5 X, 12 SS, 14 S, 20 A, 20 B, 20 C, 20 D, 20 F, 20 E).  
- **Epochen:** Vergangenheit (Fossilien), Gegenwart, Zukunft (aus Zeitrissen).  
- **Evolutionsstufen** und individuelle Wachstumskurven.  
- **Plus-Wert:** Steigert langfristiges Potenzial / Levelcap (Synthese-basiert).  
- **Instanzen:** `MonsterInstance` mit Level, HP, Status, Traits, erlernten Moves, Spannung, plus_value, etc.  
- **Trait-System:** Passive/battle-relevante Eigenschaften (z. B. Mehraktionen später).  
- **Skillsets (in Planung):** Erweiterbar, vererbbar bei Synthese.  
- **Legendäre Monster:** 11 besondere mit Story-Verknüpfung.  
- **Synthese:** Fusion zweier Monster zu einem neuen, stärkeren mit vererbten Eigenschaften, erhöhtem Plus/Levelcap, kombinierten Startstats.

---

## 4. Welt & Karten

Vorhandene Kartennamen / Szenen:
- noch ausstehend

## 5. UI / UX

- **Menüs:** Auswahl mit Markierung, Titel, Navigation (Angriff, Items, Scout, Flucht usw.).  
- **HUD:** Zone, Ära, Zugnummer, Log (letzte Aktionen).  
- **Team-Panels:** HP-Balken, Name, Statusanzeigen.  
- **Dialogboxen:** Automatischer Umbruch, Fortschrittsanzeige in Tutorials.  
- **Feedback:** Farben, Hervorhebungen für Auswahl, kritische Treffer, Scout-Fortschritt.

## 6. (Beispiel Flow nach Spielstart)

1. Start im Haus → verlassen des Hauses → Kohlenstadt → museum  
2. Professor belebt Fossilien → Starter wählen  
3. Labor und Museum verlassen → Rivalenkampf → Erkundung town_exterior oder verloren im Rivalenkampf und aufwachen im bergmannsheil dann
5. Betreten Route 1 nach Erhalt des Starters möglich
6. Erkundung Route 1 → Zähmen und Kämpfen von Monstern → Monster aufleveln

