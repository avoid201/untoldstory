# Feld-Effekt-System Dokumentation

## Übersicht

Das Feld-Effekt-System für "Untold Story" implementiert umfassende Wetter-, Terrain- und Spezialeffekte, die das Kampfgeschehen dynamisch beeinflussen. Das System ist vollständig in die bestehende Kampfmechanik integriert und erweitert diese um strategische Tiefe.

## Architektur

### Kern-Komponenten

1. **FieldEffect** - Basis-Klasse für alle Feld-Effekte
2. **WeatherEffect** - Wetter-basierte Effekte (Sonnenschein, Regen, etc.)
3. **TerrainEffect** - Terrain-basierte Effekte (Gras, Elektro, etc.)
4. **SpecialEffect** - Spezielle Kampfplatz-Effekte (Zeitriss, Gravity, etc.)
5. **FieldEffectManager** - Verwaltet alle aktiven Effekte
6. **WeatherSystem** - Spezialisiertes Wetter-System mit Animationen

### Dateistruktur

```
engine/systems/
├── field_effects.py      # Hauptsystem
├── weather.py            # Wetter-spezifische Logik
└── battle/
    ├── damage_calc.py    # Bestehende Schadensberechnung
    └── battle.py         # Kampfsystem-Integration

data/
└── field_effects.json    # Konfiguration aller Effekte
```

## Wetter-Effekte

### Verfügbare Wetter-Typen

| Wetter | Effekt | Dauer | Indoor |
|--------|--------|-------|---------|
| **Sonnenschein** | Feuer +50%, Wasser -50% | 5 Runden | ❌ |
| **Regen** | Wasser +50%, Feuer -50% | 5 Runden | ❌ |
| **Sandsturm** | Erde +20%, andere -1/16 HP | 5 Runden | ❌ |
| **Hagel** | Luft +20%, andere -1/16 HP | 5 Runden | ❌ |
| **Nebel** | Alle Attacken -20% Genauigkeit | 5 Runden | ✅ |

### Wetter-Mechaniken

- **Schadensmodifikatoren**: Direkte Multiplikatoren für bestimmte Typen
- **End-Runden-Schaden**: Automatischer Schaden für nicht-immune Typen
- **Immunitäten**: Bestimmte Typen sind vor Wetter-Schaden geschützt
- **Indoor-Beschränkungen**: Wetter funktioniert nicht in Gebäuden

### Wetter-Setter

**Legendäre Monster:**
- Sonnenkönig → Sonnenschein (8 Runden)
- Regenherr → Regen (8 Runden)
- Sandsturm → Sandsturm (8 Runden)
- Eisriese → Hagel (8 Runden)

**Normale Monster:**
- Nebelgeist → Nebel (6 Runden)

## Terrain-Effekte

### Verfügbare Terrain-Typen

| Terrain | Effekt | Dauer | Indoor |
|---------|--------|-------|---------|
| **Gras** | Pflanze +30%, HP-Regeneration | 5 Runden | ✅ |
| **Elektro** | Energie +30%, Schlaf-Immunität | 5 Runden | ✅ |
| **Psycho** | Mystik +30%, Priorität blockiert | 5 Runden | ✅ |
| **Nebel** | Chaos -50%, Status-Immunität | 5 Runden | ✅ |

### Terrain-Mechaniken

- **Schadensmodifikatoren**: Typ-spezifische Verstärkungen
- **Status-Immunitäten**: Schutz vor bestimmten Status-Effekten
- **HP-Regeneration**: Automatische Heilung pro Runde
- **Prioritäts-Blockierung**: Verhindert Prioritäts-Attacken

## Spezial-Effekte

### Verfügbare Spezial-Effekte

| Effekt | Beschreibung | Dauer | Story-Progress |
|---------|--------------|-------|----------------|
| **Zeitriss** | Realitätsverzerrung, Typ-Änderungen | 3 Runden | 30%+ |
| **Gravity** | Flug-Immunitäten aufgehoben | 5 Runden | 0%+ |
| **Trick Room** | Geschwindigkeits-Reihenfolge umgekehrt | 5 Runden | 0%+ |

### Spezial-Effekt-Mechaniken

#### Zeitriss
- **Frühe Phase** (30-49%): Typ-Änderungen aktiv
- **Späte Phase** (80%+): Zukünftige Monster erscheinen
- **Story-Integration**: Effekte hängen vom Fortschritt ab

#### Gravity
- Entfernt alle Flug-Immunitäten
- Boden-Attacken werden gegen fliegende Monster effektiv
- Beeinflusst Prioritäts-Berechnungen

#### Trick Room
- Kehrt die Geschwindigkeits-Reihenfolge um
- Langsame Monster greifen zuerst an
- Ignoriert Prioritäts-Werte

## Integration in das Kampfsystem

### Schadensberechnung

```python
# Feld-Effekte werden automatisch in die Schadensberechnung integriert
base_damage = 100
final_damage = field_effect_manager.modify_damage(base_damage, "feuer")
# Bei Sonnenschein: 100 * 1.5 = 150
```

### Genauigkeitsberechnung

```python
# Wetter-Effekte beeinflussen die Trefferwahrscheinlichkeit
base_accuracy = 0.9
final_accuracy = field_effect_manager.modify_accuracy(base_accuracy, "feuer")
# Bei Nebel: 0.9 * 0.8 = 0.72
```

### End-Runden-Effekte

```python
# Automatische Effekte am Ende jeder Runde
effects = field_effect_manager.apply_end_turn_effects("feuer", 100)
# Bei Sandsturm: {"damage": 6, "healing": 0}
```

## Visuelle Effekte

### Partikel-Systeme

- **Regen**: 100 blaue Tropfen, fallende Animation
- **Sandsturm**: 150 braune Partikel, horizontale Bewegung
- **Hagel**: 80 weiße Partikel, schnelle Fallbewegung
- **Gras**: 30 grüne Partikel, sanfte Aufwärtsbewegung

### Bildschirm-Überlagerungen

- **Sonnenschein**: Helle, gelbe Überlagerung (Add-Blend)
- **Regen**: Dunkle, blaue Überlagerung (Multiply-Blend)
- **Nebel**: Transparente graue Überlagerung

### Sound-Effekte

- Jedes Wetter hat eigene Ambient-Sounds
- Übergänge zwischen Wetter-Zuständen
- Partikel-Sounds für intensive Effekte

## Speichern und Laden

### Serialisierung

Alle Feld-Effekte sind vollständig serialisierbar:

```python
# Speichern
effect_data = field_effect_manager.to_dict()
save_data["field_effects"] = effect_data

# Laden
field_effect_manager = FieldEffectManager.from_dict(load_data["field_effects"])
```

### Persistenz

- Aktive Effekte werden gespeichert
- Effekt-Historie wird bewahrt
- Indoor/Outdoor-Status wird beibehalten

## Konfiguration

### JSON-Konfiguration

Alle Effekte sind in `data/field_effects.json` konfiguriert:

```json
{
  "weather_effects": {
    "sunny": {
      "name": "Sonnenschein",
      "damage_modifiers": {"feuer": 1.5, "wasser": 0.5},
      "visual_effects": ["bright_overlay", "sun_rays"]
    }
  }
}
```

### Anpassbare Parameter

- **Dauer**: Standard 5 Runden, konfigurierbar
- **Modifikatoren**: Schadens- und Genauigkeits-Multiplikatoren
- **Visuelle Effekte**: Partikel-Zahlen, Farben, Animationen
- **Sound-Effekte**: Dateinamen und Lautstärke

## Debug-Features

### TAB-Taste Funktionen

- **Feld-Effekt-Status**: Zeigt alle aktiven Effekte
- **Effekt-Historie**: Liste der vergangenen Effekte
- **Performance-Metriken**: Partikel-Zahlen und FPS-Impact

### Logging

```python
# Alle Effekt-Änderungen werden geloggt
[Field Effects] Sonnenschein aktiviert (5 Runden verbleibend)
[Field Effects] Sandsturm abgelaufen
[Field Effects] Gras-Terrain hinzugefügt
```

## Performance-Optimierungen

### Effiziente Verwaltung

- **Maximal 3 aktive Effekte** (1 pro Kategorie)
- **Lazy Loading** für visuelle Effekte
- **Partikel-Pooling** für bessere Performance

### Skalierung

- **Partikel-Zahlen** passen sich der Bildschirmgröße an
- **Effekt-Intensität** skaliert mit Monster-Level
- **Story-Progress** beeinflusst Effekt-Komplexität

## Balance und Gameplay

### Strategische Tiefe

- **Typ-Synergien**: Feuer-Monster profitieren von Sonnenschein
- **Team-Building**: Wetter-spezifische Teams möglich
- **Gegenstrategien**: Terrain-Effekte können Wetter ausgleichen

### Progression

- **Frühe Phase**: Einfache Wetter-Effekte
- **Mittlere Phase**: Terrain-Effekte verfügbar
- **Späte Phase**: Zeitriss und komplexe Spezial-Effekte

### Schwierigkeitsanpassung

- **Einfach**: Reduzierte Effekt-Dauer
- **Normal**: Standard-Einstellungen
- **Schwer**: Verstärkte Effekte, längere Dauer

## Zukünftige Erweiterungen

### Geplante Features

1. **Dynamisches Wetter**: Wetter ändert sich während des Kampfes
2. **Kombinations-Effekte**: Wetter + Terrain Synergien
3. **Story-Integration**: Wetter reagiert auf Handlungsverlauf
4. **Multiplayer-Synchronisation**: Wetter wird zwischen Spielern geteilt

### Modding-Unterstützung

- **JSON-basierte Konfiguration** für einfache Anpassungen
- **Plugin-System** für neue Effekt-Typen
- **Asset-Integration** für benutzerdefinierte visuelle Effekte

## Fehlerbehandlung

### Robuste Implementierung

```python
try:
    effect = field_effect_manager.add_effect(weather_effect)
except Exception as e:
    logger.error(f"Fehler beim Hinzufügen des Wetter-Effekts: {e}")
    # Fallback: Effekt wird ignoriert, Kampf läuft normal weiter
```

### Graceful Degradation

- **Fehlende Assets**: Effekte werden ohne visuelle Darstellung ausgeführt
- **Konfigurationsfehler**: Standard-Werte werden verwendet
- **Performance-Probleme**: Partikel-Zahlen werden automatisch reduziert

## Testing

### Unit Tests

```python
def test_sunny_weather_damage():
    weather = create_sunny_weather()
    damage = weather.modify_damage(100, "feuer")
    assert damage == 150
    
def test_sandstorm_immunity():
    weather = create_sandstorm_weather()
    assert weather.check_immunity("erde") == True
```

### Integration Tests

```python
def test_field_effect_manager_integration():
    manager = FieldEffectManager()
    weather = create_sunny_weather()
    manager.add_effect(weather)
    
    damage = manager.modify_damage(100, "feuer")
    assert damage == 150
```

### Performance Tests

```python
def test_particle_performance():
    weather = create_sandstorm_weather()
    particles = weather.get_weather_particles(60)
    assert len(particles) <= 150  # Max Partikel-Zahl
```

## Fazit

Das Feld-Effekt-System fügt "Untold Story" eine neue strategische Dimension hinzu, ohne die bestehende Kampfmechanik zu beeinträchtigen. Es ist vollständig integriert, performant und erweiterbar, was es zu einem wertvollen Bestandteil des Spiels macht.

Die Implementierung folgt den etablierten Codestandards des Projekts und bietet eine solide Grundlage für zukünftige Erweiterungen und Modding-Möglichkeiten.
