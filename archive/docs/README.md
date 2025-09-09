# 🎮 Untold Story - Vollständige Spielübersicht

> **Die offizielle Hauptdokumentation für das 2D-RPG "Untold Story"**

[![Zurück zur Haupt-README](../README.md)](../README.md) | [📚 Dokumentations-Index](#-dokumentations-index)

---

## 📋 Inhaltsverzeichnis

- [🎯 Spielkonzept](#-spielkonzept)
- [🌍 Spielwelt](#-spielwelt)
- [👹 Monster-System](#-monster-system)
- [⚔️ Kampfsystem](#️-kampfsystem)
- [🎒 Item-System](#-item-system)
- [🗺️ Welt & Karten](#️-welt--karten)
- [🎮 Spielmechaniken](#-spielmechaniken)
- [💾 Speichersystem](#-speichersystem)
- [🔧 Technische Details](#-technische-details)
- [📚 Dokumentations-Index](#-dokumentations-index)

---

## 🎯 Spielkonzept

**Untold Story** ist ein 2D-RPG, das die besten Elemente von Dragon Quest Monsters und Pokémon kombiniert, eingebettet in eine authentische deutsche Ruhrpott-Atmosphäre.

### 🎭 Kernkonzept

- **Monster-Taming**: Fange und trainiere Monster durch Interaktion
- **Synthese-System**: Kombiniere Monster zu neuen, stärkeren Kreaturen
- **Ruhrpott-Setting**: Authentische deutsche Umgebung mit lokaler Atmosphäre
- **Story-getrieben**: Narrative RPG-Erfahrung mit Monster-Sammlung

### 🎯 Zielgruppe

- **Hauptzielgruppe**: RPG-Fans, Monster-Collector, deutsche Spieler
- **Altersgruppe**: 12+ (familienfreundlich)
- **Schwierigkeitsgrad**: Einsteiger bis Fortgeschrittene
- **Spieldauer**: 20-40 Stunden für Hauptstory, 100+ für Vollständigkeit

---

## 🌍 Spielwelt

### 🏭 Ruhrpott-Setting

**Untold Story** spielt in einer fiktionalisierten Version des Ruhrgebiets, die die industrielle Vergangenheit mit modernen Elementen verbindet.

#### 🏗️ Hauptregionen

- **Kohlenstadt**: Industrielle Vergangenheit, alte Zechen
- **Stahlburg**: Moderne Stadt mit historischem Kern
- **Grünland**: Naturschutzgebiete und Parks
- **Hafenviertel**: Lebendige Hafenatmosphäre
- **Bergland**: Hügel und Wälder am Rande des Ruhrgebiets

#### 🏭 Lokale Atmosphäre

- **Architektur**: Industriedenkmäler, moderne Gebäude, historische Straßen
- **Kultur**: Lokale Feste, Traditionen, Ruhrpott-Mentalität
- **Dialekt**: Authentische Ruhrpott-Sprache in allen Dialogen
- **Geschichte**: Bezug zur industriellen Vergangenheit der Region

### 🌍 Weltdesign

- **2D-Perspektive**: Top-down Ansicht für optimale Übersicht
- **Grid-System**: 16×16 Pixel Tiles für präzise Bewegung
- **Auflösung**: 320×180 (logisch), skaliert auf 1280×720
- **Stil**: Pixel-Art mit modernen Shader-Effekten

---

## 👹 Monster-System

### 🎯 Monster-Konzept

Monster sind die Seele des Spiels - sie sind nicht nur Kampfgefährten, sondern auch Charaktere mit eigener Persönlichkeit und Geschichte.

#### 🧬 Monster-Typen

Das Spiel verfügt über **12 verschiedene Typen**, die sich gegenseitig beeinflussen:

1. **Feuer** 🔥 - Stärke gegen Eis, Schwäche gegen Wasser
2. **Wasser** 💧 - Stärke gegen Feuer, Schwäche gegen Elektro
3. **Elektro** ⚡ - Stärke gegen Wasser, Schwäche gegen Erde
4. **Erde** 🌍 - Stärke gegen Elektro, Schwäche gegen Feuer
5. **Luft** 💨 - Stärke gegen Erde, Schwäche gegen Eis
6. **Eis** ❄️ - Stärke gegen Luft, Schwäche gegen Feuer
7. **Pflanze** 🌱 - Stärke gegen Wasser, Schwäche gegen Feuer
8. **Gift** ☠️ - Stärke gegen Pflanze, Schwäche gegen Erde
9. **Kampf** 👊 - Stärke gegen Normal, Schwäche gegen Luft
10. **Psycho** 🧠 - Stärke gegen Kampf, Schwäche gegen Gift
11. **Geist** 👻 - Stärke gegen Psycho, Schwäche gegen Normal
12. **Normal** ⚪ - Ausgewogen, keine besonderen Stärken/Schwächen

#### 🏆 Monster-Ränge

Monster werden in **9 Rängen** eingeteilt, von F (schwach) bis X (legendär):

- **F-Rang**: Schwache Monster, gut für Anfänger
- **E-Rang**: Grundlegende Monster
- **D-Rang**: Entwickelte Monster
- **C-Rang**: Mittlere Stärke
- **B-Rang**: Starke Monster
- **A-Rang**: Sehr starke Monster
- **S-Rang**: Elite-Monster
- **SS-Rang**: Ultra-seltene Monster
- **X-Rang**: Legendäre Monster

### 🎣 Taming-System

#### 🎯 Taming-Mechanik

- **Keine Pokébälle**: Monster werden durch Interaktion gewonnen
- **Vertrauen aufbauen**: Zeit und Aufmerksamkeit investieren
- **Gemeinsame Erlebnisse**: Monster durch Abenteuer gewinnen
- **Persönliche Bindung**: Jedes Monster hat eigene Vorlieben

#### 🔄 Synthese-System

- **Monster-Fusion**: Kombiniere zwei Monster zu einem neuen
- **Vererbung**: Eigenschaften werden von Eltern weitergegeben
- **Neue Typen**: Durch Fusion können neue Typ-Kombinationen entstehen
- **Seltene Kombinationen**: Spezielle Monster nur durch Synthese

### 👥 Party-System

- **Maximale Größe**: 6 Monster gleichzeitig
- **Storage-System**: Überschüssige Monster in Boxen lagern
- **Team-Strategie**: Verschiedene Monster-Typen kombinieren
- **Persönliche Bindung**: Jedes Monster entwickelt sich individuell

---

## ⚔️ Kampfsystem

### 🎭 Kampf-Phasen

Das Kampfsystem läuft in **5 definierten Phasen** ab:

#### 1. 🎬 Intro-Phase
- **Kampfbeginn**: Animation und Einführung
- **Monster-Präsentation**: Beide Monster werden vorgestellt
- **Umgebung**: Kampfarena wird etabliert

#### 2. 🎮 Input-Phase
- **Aktionsauswahl**: Spieler wählt Monster-Aktionen
- **Strategie-Planung**: Verschiedene Angriffe und Verteidigung
- **Item-Verwendung**: Heilung und Verstärkung

#### 3. ⚡ Execution-Phase
- **Aktionsausführung**: Alle Aktionen werden ausgeführt
- **Geschwindigkeits-Reihenfolge**: Schnellere Monster agieren zuerst
- **Effekt-Berechnung**: Schaden, Heilung, Status-Effekte

#### 4. 📊 Aftermath-Phase
- **Ergebnis-Anzeige**: Kampf-Ergebnisse werden präsentiert
- **Erfahrung**: Monster erhalten EP und entwickeln sich
- **Status-Updates**: Gesundheit, Level, neue Fähigkeiten

#### 5. 🏁 End-Phase
- **Kampf-Ende**: Sieg, Niederlage oder Flucht
- **Belohnungen**: Items, Erfahrung, neue Monster
- **Welt-Rückkehr**: Zurück zur Erkundung

### ⚔️ Kampf-Mechaniken

#### 🎯 Angriffs-Typen

- **Physische Angriffe**: Direkter Schaden, abhängig von Stärke
- **Spezial-Angriffe**: Magischer Schaden, abhängig von Intelligenz
- **Status-Angriffe**: Vergiftung, Paralyse, Schlaf
- **Verteidigungs-Angriffe**: Schild, Ausweichen, Konter

#### 🔄 Typ-Effektivität

- **Super-Effektiv**: 2x Schaden
- **Normal**: 1x Schaden
- **Nicht sehr effektiv**: 0.5x Schaden
- **Keine Wirkung**: 0x Schaden

#### 📈 Status-Effekte

- **Vergiftung**: Kontinuierlicher Schaden
- **Paralyse**: Reduzierte Geschwindigkeit
- **Schlaf**: Keine Aktionen möglich
- **Verwirrung**: Zufällige Aktionen
- **Versteinerung**: Komplett handlungsunfähig

---

## 🎒 Item-System

### 🎯 Item-Kategorien

#### 💊 Heilungs-Items
- **Trank**: Wiederherstellung von Gesundheit
- **Elixier**: Vollständige Heilung
- **Antidot**: Heilung von Vergiftung
- **Aufwecker**: Heilung von Schlaf

#### ⚔️ Kampf-Items
- **Verstärker**: Temporäre Kampf-Boosts
- **Schutz-Items**: Verteidigungs-Verbesserungen
- **Spezial-Items**: Einmalige Kampf-Effekte

#### 🎁 Sammel-Items
- **Synthese-Material**: Für Monster-Fusion
- **Verkaufs-Items**: Für Währung
- **Story-Items**: Für Quests und Fortschritt

### 🛒 Wirtschaftssystem

- **Währung**: Euro (€) als lokale Währung
- **Einkommen**: Monster-Kämpfe, Quests, Verkauf von Items
- **Ausgaben**: Items, Ausrüstung, Monster-Pflege
- **Inflation**: Dynamisches Preissystem basierend auf Spieler-Level

---

## 🗺️ Welt & Karten

### 🏗️ Kartensystem

#### 📐 Tile-basierte Struktur
- **Tile-Größe**: 16×16 Pixel
- **Auflösung**: 320×180 (logisch)
- **Skalierung**: 4x auf 1280×720
- **Performance**: Optimiert für flüssige Bewegung

#### 🎨 Kartentypen

- **Außenkarten**: Offene Welten, Städte, Natur
- **Innenkarten**: Gebäude, Höhlen, Dungeons
- **Übergangskarten**: Verbindungen zwischen Bereichen
- **Spezialkarten**: Event-Bereiche, Boss-Arenen

### 🎮 Kamerabewegung

#### 📷 Kamera-System
- **Folge-Kamera**: Folgt dem Spieler-Charakter
- **Smooth-Scrolling**: Flüssige Übergänge
- **Zoom-Funktionen**: Verschiedene Ansichten
- **Kollisionserkennung**: Verhindert Kamera-Durchdringung

---

## 🎮 Spielmechaniken

### 🚶 Bewegungssystem

#### 🎯 Grid-basierte Bewegung
- **Präzise Kontrolle**: 16×16 Pixel Schritte
- **Kollisionserkennung**: Verhindert Durchdringung
- **Animation**: Flüssige Bewegungs-Übergänge
- **Geschwindigkeit**: Verschiedene Bewegungsgeschwindigkeiten

#### 🎮 Steuerung
- **Pfeiltasten**: Grundbewegung
- **WASD**: Alternative Steuerung
- **Laufen**: Shift-Taste für schnelle Bewegung
- **Interaktion**: ENTER oder Leertaste

### 💾 Speichersystem

#### 🎯 Speicher-Mechanik
- **Auto-Save**: Automatisches Speichern nach wichtigen Events
- **Manuelles Speichern**: Speichern an bestimmten Punkten
- **Mehrere Slots**: Bis zu 10 Speicherstände
- **Cloud-Sync**: Optional für Online-Speicherung

#### 📁 Speicher-Format
- **JSON-basiert**: Lesbare Speicherdateien
- **ZIP-Kompression**: Reduzierte Dateigröße
- **Backup-System**: Automatische Sicherungskopien
- **Import/Export**: Speicherstände teilen

---

## 🔧 Technische Details

### 🖥️ Systemanforderungen

#### 💻 Mindestanforderungen
- **Betriebssystem**: Windows 10, macOS 10.15, Linux
- **Prozessor**: Intel i3 oder AMD Ryzen 3
- **Arbeitsspeicher**: 4 GB RAM
- **Grafik**: Integrierte Grafikkarte
- **Speicherplatz**: 2 GB freier Speicherplatz

#### 🚀 Empfohlene Anforderungen
- **Betriebssystem**: Windows 11, macOS 12, Linux
- **Prozessor**: Intel i5 oder AMD Ryzen 5
- **Arbeitsspeicher**: 8 GB RAM
- **Grafik**: Dedizierte Grafikkarte
- **Speicherplatz**: 5 GB freier Speicherplatz

### 🐍 Technologie-Stack

#### 🎮 Engine
- **Python 3.13.5+**: Moderne Python-Features
- **pygame-ce 2.5+**: Aktuelle Pygame-Version
- **OpenGL**: Hardware-beschleunigte Grafik
- **SDL2**: Audio und Input-Handling

#### 🏗️ Architektur
- **Modulare Struktur**: Wartbare und erweiterbare Systeme
- **Event-System**: Lose gekoppelte Komponenten
- **Ressourcen-Management**: Optimierte Asset-Verwaltung
- **Plugin-System**: Erweiterbare Funktionalität

### 📊 Performance-Optimierung

#### 🎯 Optimierungen
- **Sprite-Batching**: Effiziente Grafik-Rendering
- **Ressourcen-Caching**: Reduzierte Ladezeiten
- **LOD-System**: Level of Detail für verschiedene Distanzen
- **Multithreading**: Parallele Verarbeitung wo möglich

---

## 📚 Dokumentations-Index

### 🎯 Feature-Dokumentation
- **[Kampfsystem](features/BATTLE_SYSTEM.md)** - Detaillierte Kampfmechaniken
- **[Monster-System](features/MONSTER_SYSTEM.md)** - Monster-Typen, Ränge, Entwicklung
- **[Item-System](features/ITEM_SYSTEM.md)** - Items, Wirtschaft, Verwendung
- **[Welt-System](features/WORLD_SYSTEM.md)** - Karten, Kamera, Bewegung

### 📖 Entwicklungs-Guides
- **[Anfänger-Guide](guides/BEGINNER_GUIDE.md)** - Erste Schritte für neue Entwickler
- **[System-Integration](guides/SYSTEM_INTEGRATION.md)** - Integration verschiedener Systeme
- **[Asset-Integration](guides/ASSET_INTEGRATION.md)** - Grafik und Audio einbinden
- **[Testing-Guide](guides/TESTING_GUIDE.md)** - Tests schreiben und ausführen

### ⚙️ Technische Dokumentation
- **[Engine-Architektur](technical/ENGINE_ARCHITECTURE.md)** - Technische Implementierung
- **[Ressourcen-Management](technical/RESOURCE_MANAGEMENT.md)** - Asset-Verwaltung
- **[Performance-Optimierung](technical/PERFORMANCE_OPTIMIZATION.md)** - Optimierungstechniken
- **[Debug-System](technical/DEBUG_SYSTEM.md)** - Entwickler-Tools

### 📋 Zusammenfassungen
- **[Implementierungs-Status](summaries/IMPLEMENTATION_STATUS.md)** - Aktueller Entwicklungsstand
- **[System-Updates](summaries/SYSTEM_UPDATES.md)** - Neue Features und Verbesserungen
- **[Migration-Guides](summaries/MIGRATION_GUIDES.md)** - System-Übergänge

### 📊 Entwicklungsberichte
- **[Wöchentliche Updates](reports/WEEKLY_UPDATES.md)** - Regelmäßige Status-Updates
- **[Milestone-Berichte](reports/MILESTONE_REPORTS.md)** - Wichtige Meilensteine
- **[Bug-Reports](reports/BUG_REPORTS.md)** - Bekannte Probleme und Lösungen

---

## 🚀 Nächste Schritte

1. **Lies die [Feature-Dokumentation](features/)** für detaillierte Systembeschreibungen
2. **Folge den [Entwicklungs-Guides](guides/)** für praktische Anleitungen
3. **Schau dir die [technische Dokumentation](technical/)** für Implementierungsdetails an
4. **Bleib auf dem Laufenden** mit den [Entwicklungsberichten](reports/)

---

**Zurück zur [Haupt-README](../README.md)** | **📚 [Dokumentations-Index](#-dokumentations-index)**

---

*"Dat is ja mal ne richtig geile Dokumentation, wa? Jetzt kannste richtig durchstarten!"* 🎮✨

