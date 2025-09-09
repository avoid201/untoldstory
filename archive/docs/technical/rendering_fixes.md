# Rendering-Überschneidungen behoben

## Identifizierte Probleme

### 1. **Inkonsistente Layer-Reihenfolge**
**Problem:** Verschiedene Dateien verwendeten unterschiedliche Layer-Reihenfolgen:
- `engine/world/area.py`: `['ground', 'decor', 'collision', 'overhang', 'objects']`
- `engine/graphics/tile_renderer.py`: `['ground', 'decor', 'furniture', 'decoration']`

**Lösung:** Einheitliche Layer-Reihenfolge in allen Dateien:
```python
layer_order = ['ground', 'decor', 'furniture', 'decoration']
```

### 2. **Doppeltes Rendering von Möbeln**
**Problem:** Möbel wurden sowohl über den `furniture`-Layer als auch über `furniture_placement` gerendert.

**Lösung:** Entfernung des doppelten Renderings in `tile_renderer.py`.

### 3. **Fehlende Z-Order-Behandlung**
**Problem:** Entities wurden ohne korrekte Tiefensortierung gerendert, was zu Überschneidungen führte.

**Lösung:** Implementierung eines zentralen `RenderManager` mit definierten Z-Indizes.

### 4. **Fehlende Transparenz-Behandlung**
**Problem:** Tiles ohne Transparenz wurden trotzdem gerendert.

**Lösung:** Prüfung der Alpha-Werte vor dem Rendering.

## Neue Rendering-Architektur

### RenderManager
Der neue `RenderManager` koordiniert alle Rendering-Operationen:

```python
class RenderManager:
    def __init__(self):
        self.layers = {
            "background": 0,      # Hintergrund
            "ground": 100,        # Boden
            "decor": 200,         # Dekoration
            "furniture": 300,     # Möbel
            "entities": 400,      # Spieler, NPCs
            "overhang": 500,      # Überhang (Bäume, etc.)
            "decoration": 600,    # Dekoration
            "ui": 1000,           # UI-Elemente
            "dialogue": 1100      # Dialog-Boxen
        }
```

### Vorteile der neuen Architektur

1. **Zentrale Kontrolle:** Alle Rendering-Operationen laufen über einen Manager
2. **Korrekte Z-Order:** Definiierte Layer-Reihenfolge verhindert Überschneidungen
3. **Effizientes Culling:** Nur sichtbare Tiles werden gerendert
4. **Transparenz-Behandlung:** Tiles werden nur gerendert wenn sie sichtbar sind
5. **Einheitliche API:** Konsistente Rendering-Methoden in allen Szenen

## Implementierte Änderungen

### Dateien geändert:
- `engine/world/area.py` - Einheitliche Layer-Reihenfolge
- `engine/graphics/tile_renderer.py` - Entfernung doppelten Renderings
- `engine/scenes/field_scene.py` - Integration des RenderManagers

### Neue Dateien:
- `engine/graphics/render_manager.py` - Zentraler Rendering-Manager

## Verwendung

### In Szenen:
```python
# RenderManager automatisch initialisieren
if not hasattr(self, 'render_manager'):
    from engine.graphics.render_manager import RenderManager
    self.render_manager = RenderManager()

# Szene rendern
self.render_manager.render_scene(surface, area, camera, ui_elements)
```

### Layer hinzufügen:
```python
render_manager.add_layer("custom_layer", 150)  # Zwischen ground (100) und decor (200)
```

## Debug-Features

Der RenderManager unterstützt Debug-Modi:
- `render_manager.set_debug_mode(True)` - Aktiviert Debug-Ausgaben
- Layer-Sichtbarkeit kann pro Layer gesteuert werden
- Z-Index-Informationen werden angezeigt

## Nächste Schritte

1. **Battle-Scene integrieren:** RenderManager auch in der BattleScene verwenden
2. **Performance-Optimierung:** Weitere Culling-Optimierungen implementieren
3. **Layer-Animationen:** Unterstützung für animierte Layer hinzufügen
4. **Shader-Integration:** Moderne Rendering-Techniken für bessere Performance
