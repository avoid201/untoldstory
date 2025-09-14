#!/bin/bash
# Start-Skript für Untold Story auf macOS

echo "🎮 Untold Story Launcher"
echo "========================"
echo ""
echo "Was möchtest du starten?"
echo ""
echo "1) Hauptspiel"
echo "2) Map Viewer (player_house)"
echo "3) TMX Debug"
echo "4) Test Rendering"
echo ""
read -p "Wähle (1-4): " choice

case $choice in
    1)
        echo "▶️ Starte Hauptspiel..."
        python3 main.py
        ;;
    2)
        echo "▶️ Starte Map Viewer..."
        python3 view_map.py
        ;;
    3)
        echo "▶️ Starte TMX Debug..."
        python3 debug_tilesets.py
        ;;
    4)
        echo "▶️ Starte Test Rendering..."
        python3 test_tmx_rendering.py
        ;;
    *)
        echo "❌ Ungültige Auswahl"
        ;;
esac
