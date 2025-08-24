#!/bin/bash

# Test-Ausführungs-Skript für Untold Story
# Führt alle Tests aus und generiert Berichte

set -e  # Beende bei Fehlern

# Farben für Ausgabe
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Projekt-Verzeichnis
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo -e "${BLUE}🎮 UNTOLD STORY - TEST-AUSFÜHRUNG 🎮${NC}"
echo "=================================================="
echo "Projekt-Verzeichnis: $PROJECT_DIR"
echo "Zeitstempel: $(date)"
echo "=================================================="

# Funktionen
print_header() {
    echo -e "\n${BLUE}$1${NC}"
    echo "----------------------------------------"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_dependencies() {
    print_header "Überprüfe Abhängigkeiten"
    
    # Python-Version prüfen
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        print_success "Python gefunden: $PYTHON_VERSION"
    else
        print_error "Python3 nicht gefunden"
        exit 1
    fi
    
    # Pytest prüfen
    if python3 -m pytest --version &> /dev/null; then
        PYTEST_VERSION=$(python3 -m pytest --version 2>&1)
        print_success "Pytest gefunden: $PYTEST_VERSION"
    else
        print_warning "Pytest nicht gefunden - installiere..."
        pip3 install pytest pytest-cov
    fi
    
    # Virtuelle Umgebung prüfen
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        print_success "Virtuelle Umgebung aktiv: $VIRTUAL_ENV"
    else
        print_warning "Keine virtuelle Umgebung aktiv"
    fi
}

run_validation() {
    print_header "Führe Projekt-Validierung durch"
    
    if [[ -f "tools/validation_tools/enhanced_validator.py" ]]; then
        print_success "Starte erweiterten Validator..."
        python3 tools/validation_tools/enhanced_validator.py
        VALIDATION_EXIT_CODE=$?
        
        if [[ $VALIDATION_EXIT_CODE -eq 0 ]]; then
            print_success "Validierung erfolgreich"
        elif [[ $VALIDATION_EXIT_CODE -eq 1 ]]; then
            print_warning "Validierung mit Warnungen"
        else
            print_error "Validierung fehlgeschlagen"
            return 1
        fi
    else
        print_warning "Erweiterter Validator nicht gefunden - verwende Standard"
        python3 tools/validation_tools/check_project.py
    fi
}

run_tests() {
    print_header "Führe Tests aus"
    
    # Test-Verzeichnisse
    TEST_DIRS=("tests/systems" "tests/battle" "tests/story")
    
    TOTAL_TESTS=0
    TOTAL_PASSED=0
    TOTAL_FAILED=0
    
    for test_dir in "${TEST_DIRS[@]}"; do
        if [[ -d "$test_dir" ]]; then
            echo "Teste $test_dir..."
            
            # Tests ausführen
            if python3 -m pytest "$test_dir" -v --tb=short; then
                print_success "$test_dir: Alle Tests bestanden"
                # Zähle Tests
                TEST_COUNT=$(python3 -m pytest "$test_dir" --collect-only -q 2>/dev/null | grep "test session starts" | awk '{print $6}' | sed 's/[^0-9]//g')
                TOTAL_TESTS=$((TOTAL_TESTS + TEST_COUNT))
                TOTAL_PASSED=$((TOTAL_PASSED + TEST_COUNT))
            else
                print_error "$test_dir: Einige Tests fehlgeschlagen"
                # Zähle Tests
                TEST_COUNT=$(python3 -m pytest "$test_dir" --collect-only -q 2>/dev/null | grep "test session starts" | awk '{print $6}' | sed 's/[^0-9]//g')
                TOTAL_TESTS=$((TOTAL_TESTS + TEST_COUNT))
                # Schätze fehlgeschlagene Tests
                TOTAL_FAILED=$((TOTAL_FAILED + 1))
            fi
        else
            print_warning "Test-Verzeichnis $test_dir nicht gefunden"
        fi
    done
    
    # Zusammenfassung
    echo ""
    print_header "Test-Zusammenfassung"
    echo "Gesamt-Tests: $TOTAL_TESTS"
    echo "Bestanden: $TOTAL_PASSED"
    echo "Fehlgeschlagen: $TOTAL_FAILED"
    
    if [[ $TOTAL_FAILED -eq 0 ]]; then
        print_success "Alle Tests bestanden!"
        return 0
    else
        print_error "Einige Tests fehlgeschlagen"
        return 1
    fi
}

run_coverage_analysis() {
    print_header "Führe Coverage-Analyse durch"
    
    if [[ -f "tools/testing_tools/coverage_analyzer.py" ]]; then
        print_success "Starte Coverage-Analyse..."
        python3 tools/testing_tools/coverage_analyzer.py --save-report
        COVERAGE_EXIT_CODE=$?
        
        if [[ $COVERAGE_EXIT_CODE -eq 0 ]]; then
            print_success "Coverage-Analyse erfolgreich"
        else
            print_warning "Coverage-Analyse mit Problemen"
        fi
    else
        print_warning "Coverage-Analyzer nicht gefunden"
        
        # Einfache Coverage mit pytest
        if command -v python3 -m pytest &> /dev/null; then
            echo "Verwende pytest-cov für Coverage..."
            python3 -m pytest tests/ --cov=engine --cov-report=term-missing --cov-report=html
        fi
    fi
}

generate_report() {
    print_header "Generiere Test-Bericht"
    
    REPORT_FILE="test_execution_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "UNTOLD STORY - TEST-AUSFÜHRUNGS-BERICHT"
        echo "=========================================="
        echo "Datum: $(date)"
        echo "Projekt: $PROJECT_DIR"
        echo ""
        echo "ZUSAMMENFASSUNG:"
        echo "- Python: $(python3 --version 2>&1)"
        echo "- Pytest: $(python3 -m pytest --version 2>&1)"
        echo "- Tests: $TOTAL_TESTS"
        echo "- Bestanden: $TOTAL_PASSED"
        echo "- Fehlgeschlagen: $TOTAL_FAILED"
        echo ""
        echo "DETAILS:"
        echo "Siehe pytest-Ausgabe oben für Details zu fehlgeschlagenen Tests."
        echo ""
        echo "NÄCHSTE SCHRITTE:"
        if [[ $TOTAL_FAILED -gt 0 ]]; then
            echo "1. Fehlgeschlagene Tests analysieren"
            echo "2. Fehler beheben"
            echo "3. Tests erneut ausführen"
        else
            echo "1. Coverage-Analyse durchführen"
            echo "2. Neue Tests für ungetestete Bereiche hinzufügen"
            echo "3. Performance-Tests implementieren"
        fi
    } > "$REPORT_FILE"
    
    print_success "Bericht gespeichert: $REPORT_FILE"
}

cleanup() {
    print_header "Bereinigung"
    
    # Temporäre Dateien löschen
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    print_success "Bereinigung abgeschlossen"
}

# Hauptfunktion
main() {
    echo "Starte Test-Ausführung..."
    
    # Abhängigkeiten prüfen
    check_dependencies
    
    # Validierung durchführen
    if ! run_validation; then
        print_error "Projekt-Validierung fehlgeschlagen - Tests werden übersprungen"
        exit 1
    fi
    
    # Tests ausführen
    if ! run_tests; then
        print_warning "Einige Tests fehlgeschlagen"
    fi
    
    # Coverage-Analyse
    run_coverage_analysis
    
    # Bericht generieren
    generate_report
    
    # Bereinigung
    cleanup
    
    echo ""
    print_header "TEST-AUSFÜHRUNG ABGESCHLOSSEN"
    
    if [[ $TOTAL_FAILED -eq 0 ]]; then
        print_success "Alle Tests erfolgreich ausgeführt!"
        echo "Das Projekt ist bereit für den nächsten Entwicklungsschritt."
    else
        print_warning "Tests mit Problemen abgeschlossen"
        echo "Bitte behebe die fehlgeschlagenen Tests vor dem nächsten Commit."
    fi
    
    echo ""
    echo "Berichte:"
    echo "- Test-Ausführung: $REPORT_FILE"
    echo "- Coverage: coverage_report.json (falls verfügbar)"
    echo "- HTML-Coverage: htmlcov/index.html (falls verfügbar)"
}

# Skript ausführen
main "$@"
