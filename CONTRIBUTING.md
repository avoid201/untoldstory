# 🤝 Contributing to Untold Story

Vielen Dank, dass du zu Untold Story beitragen möchtest! Hier ist eine Anleitung, wie du am besten vorgehst.

## 🚀 Getting Started

### 1. Repository forken
```bash
git clone https://github.com/dein-username/untoldstory.git
cd untoldstory
```

### 2. Development Environment einrichten
```bash
# Virtual Environment erstellen
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# oder
.venv\Scripts\activate     # Windows

# Dependencies installieren
pip install -r requirements.txt
pip install pytest  # für Tests
```

### 3. Branch erstellen
```bash
git checkout -b feature/deine-feature
# oder
git checkout -b bugfix/bug-beschreibung
```

## 📝 Code Standards

### Python Style
- **PEP 8** befolgen
- **Type Hints** für alle Funktionen
- **Docstrings** für öffentliche Methoden
- **Max 120 Zeichen** pro Zeile

### Beispiel:
```python
def calculate_damage(attacker: MonsterInstance, defender: MonsterInstance, move: Move) -> int:
    """
    Berechne Schaden basierend auf DQM-Formeln.
    
    Args:
        attacker: Angreifendes Monster
        defender: Verteidigendes Monster
        move: Verwendeter Move
        
    Returns:
        Berechneter Schaden
    """
    # Implementation hier
    pass
```

## 🧪 Testing

### Tests ausführen
```bash
# Alle Tests
python -m pytest tests/ -v

# Spezifische Tests
python -m pytest tests/test_talent_system_comprehensive.py -v

# Mit Coverage
python -m pytest tests/ --cov=engine --cov-report=html
```

### Neue Tests schreiben
- Tests in `tests/` Verzeichnis
- Dateiname: `test_*.py`
- Funktionen: `test_*()`
- Verwende aussagekräftige Namen

## 🎮 Game-spezifische Guidelines

### Battle-System
- **DQM-Formeln** befolgen
- **Type-Effectiveness** korrekt implementieren
- **Status-Effekte** konsistent handhaben

### Talent-System
- **TalentManager** für zentrale Verwaltung
- **MonsterInstance** erweitern, nicht ersetzen
- **JSON-Daten** validieren

### UI-System
- **pygame-ce** Patterns verwenden
- **Responsive Design** berücksichtigen
- **Accessibility** beachten

## 📋 Pull Request Process

### 1. Code committen
```bash
git add .
git commit -m "feat: neue Talent-Funktion hinzugefügt"
```

### 2. Push und PR erstellen
```bash
git push origin feature/deine-feature
# Dann PR auf GitHub erstellen
```

### 3. PR Template ausfüllen
- Beschreibung der Änderungen
- Tests hinzugefügt/aktualisiert
- Breaking Changes dokumentiert
- Screenshots (falls UI-Änderungen)

## 🏷️ Commit Messages

Verwende das [Conventional Commits](https://www.conventionalcommits.org/) Format:

```
type(scope): description

feat(talent): neue Talent-Upgrade-Funktion
fix(battle): Schadensberechnung korrigiert
docs(readme): Installation aktualisiert
test(talent): umfassende Tests hinzugefügt
```

**Types:**
- `feat`: Neue Funktion
- `fix`: Bug-Fix
- `docs`: Dokumentation
- `style`: Code-Formatierung
- `refactor`: Code-Refactoring
- `test`: Tests
- `chore`: Wartungsarbeiten

## 🐛 Bug Reports

Verwende das Bug-Report Template:
1. Gehe zu Issues → New Issue
2. Wähle "Bug Report"
3. Fülle alle Felder aus
4. Füge Screenshots hinzu (falls möglich)

## ✨ Feature Requests

Verwende das Feature-Request Template:
1. Gehe zu Issues → New Issue
2. Wähle "Feature Request"
3. Beschreibe die Funktion detailliert
4. Erkläre den Nutzen

## 📞 Support

- **Discord:** [Link zu Discord-Server]
- **Email:** [Kontakt-Email]
- **Issues:** GitHub Issues für Bugs/Features

## 🎯 Roadmap

Aktuelle Prioritäten:
- [ ] Multiplayer-Battle
- [ ] Erweiterte Monster-Synthesis
- [ ] Quest-System
- [ ] Sound-Integration

## 📄 License

Durch das Beitragen stimmst du zu, dass dein Code unter der MIT-Lizenz veröffentlicht wird.

---

**Viel Erfolg beim Entwickeln! 🚀**
