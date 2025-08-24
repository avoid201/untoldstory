# Sprite- und Tile-Dokumentation - Untold Story

Diese Dokumentation beschreibt alle verfügbaren Sprites und Tiles im Spiel "Untold Story" mit Ruhrpott-Setting.

## Übersicht der Ordnerstruktur

```
sprites/
├── monsters/          # Monster-Sprites (148 Dateien)
├── npcs/             # NPC-Charaktere (10 Dateien)
├── Constructed/      # Fertige, zusammengesetzte Sprites (51 Dateien)
├── Raw-water/        # Wasser-Animationen (9 Dateien)
├── Drafts/           # Entwürfe und Work-in-Progress (2 Dateien)
└── [Einzeldateien]   # Verschiedene Tiles und Objekte
```

---

## 1. Monster-Sprites (sprites/monsters/)

**Anzahl:** 148 Monster-Sprites (1.png bis 151.png)

**Beschreibung:** Alle Monster-Sprites folgen der Nummerierung 1-151. Jedes Monster hat einen eigenen Sprite für das Taming- und Kampfsystem.

**Dateien:**
- `1.png` bis `151.png` - Einzelne Monster-Sprites
- Alle Sprites sind im 16x16 Pixel Format (logische Auflösung)
- Verwendung: Monster-Collection, Kampf-UI, Party-Verwaltung

---

## 2. NPC-Charaktere (sprites/npcs/)

**Anzahl:** 10 NPC-Sprites

**Spezifische NPCs:**
- `elder.png` - Älterer/Weiser NPC
- `shopkeeper.png` - Ladenbesitzer
- `worker.png` - Arbeiter
- `miner.png` - Bergmann (Ruhrpott-Thematik)
- `npc_01.png` bis `npc_06.png` - Generische NPCs

**Verwendung:** Dialoge, Welt-Interaktionen, Quest-System

---

## 3. Konstruierte Sprites (sprites/Constructed/)

**Anzahl:** 51 Dateien

### Möbel und Einrichtung
- **Betten:** `Bed-type-01.png` / `Bed-type-01_large.png`
- **Schränke:** `Cabinet.png` / `Cabinet_large.png`
- **Tische:** `Table-type-01.png` / `Table-type-01_large.png`
- **Stühle:** 
  - `Stool-type-01.png` / `Stool-type-01_large.png`
  - `Stool-type-02.png` / `Stool-type-02_large.png`
- **Bücherregale:** `Bookshelf-type-01.png` / `Bookshelf-type-01_large.png`

### Küchengeräte
- **Herd:** `Stove.png` / `Stove_large.png`
- **Kühlschrank:** `Fridge-type-01.png` / `Fridge-type-01_large.png`
- **Spüle:** `Sink.png` / `Sink_large.png`

### Elektronik
- **Computer:** `Computer-type-01.png` / `Computer-type-01_large.png`
- **TV:** `Tv-type-01.png` / `Tv-type-01_large.png`
- **Radio:** 
  - `Radio-type-01.png` / `Radio-type-01_large.png`
  - `Radio-type-02.png` / `Radio-type-02_large.png`

### Dekoration
- **Zimmerpflanzen:** `Indoor-plant-type-01.png` / `Indoor-plant-type-01_large.png`
- **Blumen:** `Flower-johto.png` / `Flower-johto_large.gif` (animiert)
- **Kunst:** `Back-wall-art.png` / `Back-wall-art_large.png`

### Gebäude und Außenbereich
- **Gebäude:** `Building.png` / `Building_large.png`
- **Bäume:** 
  - `Tree-short.png` / `Tree-short_large.png`
  - `Tree-tall.png` / `Tree-tall_large.png`
- **Kämme/Rücken:** `Ridge.png` / `Ridge_large.png`
- **Schilder:** `Sign.png` / `Sign_large.png`

### Bodenbeläge und Übergänge
- **Indoor-Übergangsmatten:**
  - `Indoor-exit-mat-type-01.png` / `Indoor-exit-mat-type-01_large.png`
  - `Indoor-exit-mat-type-02.png` / `Indoor-exit-mat-type-02_large.png`
- **Outdoor-Übergangsmatten:**
  - `Outdoor-exit-mat-type-01.png` / `Outdoor-exit-mat-type-01_large.png`
  - `Outdoor-exit-mat-type-02.png` / `Outdoor-exit-mat-type-02_large.png`

---

## 4. Wasser-Animationen (sprites/Raw-water/)

**Anzahl:** 9 Dateien

**Beschreibung:** Animierte Wasser-Frames für Gewässer in der Spielwelt

**Dateien:**
- `Water-frame-00.png` bis `Water-frame-03.png` - Einzelne Wasser-Frames
- `Water-frame-00_large.png` bis `Water-frame-03_large.png` - Große Versionen
- `Water-frames.png` - Übersicht aller Frames

**Verwendung:** Flüsse, Seen, Brunnen, Wassereffekte

---

## 5. Einzelne Tiles und Objekte (Hauptordner)

### Bäume
- **Kurze Bäume:** `Tree-short-00.png` bis `Tree-short-03.png` (mit `_large` Varianten)
- **Hohe Bäume:** `Tree-tall-00.png` bis `Tree-tall-01.png` (mit `_large` Varianten)

### Möbel (detaillierte Varianten)
- **Tische:** `Table-type-1-00.png` bis `Table-type-1-11.png` (mit `_large` Varianten)
- **Stühle:** 
  - `Stool-type-01-00.png` bis `Stool-type-01-03.png` (mit `_large` Varianten)
  - `Stool-type-02-00.png` bis `Stool-type-02-03.png` (mit `_large` Varianten)
- **Herd:** `Stove-00.png` bis `Stove-03.png` (mit `_large` Varianten)
- **Spüle:** `Sink-00.png` bis `Sink-01.png` (mit `_large` Varianten)

### Gebäude und Architektur
- **Wände:** `Back-wall-art-00.png` bis `Back-wall-art-03.png` (mit `_large` Varianten)
- **Fenster:** `Back-wall-window-00.png` bis `Back-wall-window-03.png` (mit `_large` Varianten)
- **Holzverkleidung:** `Back-wall-wood.png` / `Back-wall-wood_large.png`
- **Gebäudeverkleidung:** `Building-cladding-00.png` bis `Building-cladding-01.png`
- **Türen:** `Building-door-00.png` bis `Building-door-03.png`
- **Dächer:** `Building-roof-flat-00.png` bis `Building-roof-flat-08.png`
- **Wände:** `Building-wall-00.png` bis `Building-wall-04.png`
- **Fenster:** `Building-window.png`

### Küchengeräte
- **Kühlschrank:** `Fridge-type-01-00.png` bis `Fridge-type-01-05.png` (mit `_large` Varianten)
- **Computer:** `Computer-type-01-00.png` bis `Computer-type-01-05.png` (mit `_large` Varianten)

### Bodenbeläge
- **Fußböden:** `Flooring-type-01.png` / `Flooring-type-02.png`
- **Gras:** `Grass-flat.png`, `Grass-rustle-00.png`, `Grass-rustle-01.png`, `Grass-tall.png`
- **Wege:** `Path.png`, `Path-Gravel.png`
- **Übergangsmatten:** `Indoor-exit-mat-type-01-00.png` bis `Indoor-exit-mat-type-02-01.png`

### Dekoration
- **Zimmerpflanzen:** `Indoor-plant-type-01-00.png` bis `Indoor-plant-type-01-07.png` (mit `_large` Varianten)
- **Blumen:** `Flower-johto-00.png` / `Flower-johto-01.png`
- **Bücherregale:** `Bookshelf-type-01-00.png` bis `Bookshelf-type-01-07.png` (mit `_large` Varianten)

### Landschaft
- **Kämme:** `Ridge-00.png` bis `Ridge-08.png` (mit `_large` Varianten)
- **Schilder:** `Sign-metal-00.png` bis `Sign-metal-03.png` (mit `_large` Varianten)

### Spezielle Objekte
- **TV:** `TV-type-01-00.png` bis `TV-type-01-03.png` (mit `_large` Varianten)
- **Radio:** `Radio-type-01-00.png` bis `Radio-type-01-03.png` (mit `_large` Varianten)
- **Radio (Typ 2):** `Radio-type-02-00.png` bis `Radio-type-02-03.png` (mit `_large` Varianten)

---

## 6. Entwürfe (sprites/Drafts/)

**Anzahl:** 2 Dateien

- `Indoor-plant-00-drafts.png` / `Indoor-plant-00-drafts_large.png`
- Work-in-Progress Versionen von Zimmerpflanzen

---

## 7. Spieler-Sprite

- `player.png` - Hauptcharakter-Sprite
- Verwendung: Spieler-Bewegung, Kampf-Animationen

---

## 8. Spezielle Tiles

- `Void.png` / `Void_large.png` - Leere/unsichtbare Tiles
- `Custom.png` - Benutzerdefinierte Tiles
- `tileset.png` - Haupttileset für die Spielwelt

---

## Technische Details

### Dateiformate
- **Primär:** PNG (Portable Network Graphics)
- **Animationen:** GIF (für Wasser und Blumen)
- **Entwürfe:** ASEPRITE (.aseprite) für Animationen

### Auflösungen
- **Standard:** 16x16 Pixel (logische Spielauflösung)
- **Groß:** 64x64 Pixel (4x Skalierung für 1280x720 Display)

### Verwendung im Spiel
- **Tiles:** Weltgestaltung, Gebäude, Landschaft
- **Sprites:** Charaktere, Monster, bewegliche Objekte
- **UI:** Inventar, Kampf-Interface, Menüs

---

## Ruhrpott-Thematik

Alle Sprites sind auf das Ruhrpott-Setting abgestimmt:
- Bergbau-ähnliche Strukturen (Ridge-Tiles)
- Industrielle Gebäude (Building-Tiles)
- Bergmann-NPC (`miner.png`)
- Moderne Einrichtung (Computer, TV, Radio)

---

## Wartung und Updates

- Neue Monster-Sprites werden in `sprites/monsters/` hinzugefügt
- Fertige Sprites werden in `sprites/Constructed/` verschoben
- Entwürfe bleiben in `sprites/Drafts/` bis zur Fertigstellung
- Alle Sprites sollten sowohl in Standard- als auch in Large-Auflösung verfügbar sein

---

*Letzte Aktualisierung: [Datum]*
*Gesamtanzahl Sprites: 300+ Dateien*
