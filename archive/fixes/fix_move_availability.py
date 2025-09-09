#!/usr/bin/env python3
"""
Fix 3: Sichere Move-Verfügbarkeit
Stellt sicher, dass alle Monster Start-Moves haben
"""

import json
import os

def create_default_moves():
    """Erstellt Standard-Moves für das Battle-System"""
    
    moves_data = {
        "basic_moves": [
            {
                "id": "tackle",
                "name": "Rempler",
                "type": "Bestie",
                "category": "phys",
                "power": 40,
                "accuracy": 100,
                "pp": 35,
                "max_pp": 35,
                "priority": 0,
                "targeting": "enemy",
                "effects": [{"kind": "damage", "power": 40}],
                "description": "Ein einfacher Körperangriff"
            },
            {
                "id": "scratch",
                "name": "Kratzer",
                "type": "Bestie",
                "category": "phys",
                "power": 35,
                "accuracy": 100,
                "pp": 35,
                "max_pp": 35,
                "priority": 0,
                "targeting": "enemy",
                "effects": [{"kind": "damage", "power": 35}],
                "description": "Kratzt mit scharfen Klauen"
            },
            {
                "id": "ember",
                "name": "Glut",
                "type": "Feuer",
                "category": "mag",
                "power": 40,
                "accuracy": 100,
                "pp": 25,
                "max_pp": 25,
                "priority": 0,
                "targeting": "enemy",
                "effects": [
                    {"kind": "damage", "power": 40},
                    {"kind": "status", "status": "burn", "chance": 10}
                ],
                "description": "Ein schwacher Feuerangriff"
            },
            {
                "id": "water_gun",
                "name": "Aquaknarre",
                "type": "Wasser",
                "category": "mag",
                "power": 40,
                "accuracy": 100,
                "pp": 25,
                "max_pp": 25,
                "priority": 0,
                "targeting": "enemy",
                "effects": [{"kind": "damage", "power": 40}],
                "description": "Spritzt Wasser auf den Gegner"
            },
            {
                "id": "vine_whip",
                "name": "Rankenhieb",
                "type": "Pflanze",
                "category": "phys",
                "power": 45,
                "accuracy": 100,
                "pp": 25,
                "max_pp": 25,
                "priority": 0,
                "targeting": "enemy",
                "effects": [{"kind": "damage", "power": 45}],
                "description": "Peitscht mit dünnen Ranken"
            }
        ]
    }
    
    return moves_data

def fix_monster_instance():
    """Aktualisiert MonsterInstance._initialize_moves()"""
    
    monster_instance_path = "/Users/leon/Desktop/untold_story/engine/systems/monster_instance.py"
    
    with open(monster_instance_path, 'r') as f:
        original_content = f.read()
    
    # Backup
    with open(monster_instance_path + '.backup', 'w') as f:
        f.write(original_content)
    
    # Neue _initialize_moves Methode
    new_method = '''    def _initialize_moves(self) -> List[Move]:
        """Initialize moves based on level and species."""
        moves = []
        
        try:
            # Import here to avoid circular dependency
            from engine.systems.moves import Move, MoveCategory, MoveTarget, MoveEffect, EffectKind
            
            # Basis-Moves die jedes Monster kann
            basic_moves = [
                Move(
                    id="tackle",
                    name="Rempler",
                    type=self.types[0] if self.types else "Bestie",
                    category=MoveCategory.PHYSICAL,
                    power=40,
                    accuracy=100,
                    pp=35,
                    max_pp=35,
                    priority=0,
                    targeting=MoveTarget.ENEMY,
                    effects=[MoveEffect(kind=EffectKind.DAMAGE, power=40)],
                    description="Ein einfacher Körperangriff"
                ),
                Move(
                    id="growl",
                    name="Heuler",
                    type="Bestie",
                    category=MoveCategory.SUPPORT,
                    power=0,
                    accuracy=100,
                    pp=40,
                    max_pp=40,
                    priority=0,
                    targeting=MoveTarget.ENEMY,
                    effects=[MoveEffect(kind=EffectKind.DEBUFF, stat="atk", stages=-1)],
                    description="Senkt den Angriff des Gegners"
                )
            ]
            
            # Füge typ-spezifische Moves hinzu
            if self.types:
                primary_type = self.types[0].lower()
                
                type_moves = {
                    "feuer": Move(
                        id="ember", name="Glut", type="Feuer",
                        category=MoveCategory.MAGICAL, power=40, accuracy=100,
                        pp=25, max_pp=25, priority=0, targeting=MoveTarget.ENEMY,
                        effects=[MoveEffect(kind=EffectKind.DAMAGE, power=40)],
                        description="Ein schwacher Feuerangriff"
                    ),
                    "wasser": Move(
                        id="water_gun", name="Aquaknarre", type="Wasser",
                        category=MoveCategory.MAGICAL, power=40, accuracy=100,
                        pp=25, max_pp=25, priority=0, targeting=MoveTarget.ENEMY,
                        effects=[MoveEffect(kind=EffectKind.DAMAGE, power=40)],
                        description="Spritzt Wasser auf den Gegner"
                    ),
                    "pflanze": Move(
                        id="vine_whip", name="Rankenhieb", type="Pflanze",
                        category=MoveCategory.PHYSICAL, power=45, accuracy=100,
                        pp=25, max_pp=25, priority=0, targeting=MoveTarget.ENEMY,
                        effects=[MoveEffect(kind=EffectKind.DAMAGE, power=45)],
                        description="Peitscht mit dünnen Ranken"
                    ),
                    "energie": Move(
                        id="thunder_shock", name="Donnerschock", type="Energie",
                        category=MoveCategory.MAGICAL, power=40, accuracy=100,
                        pp=30, max_pp=30, priority=0, targeting=MoveTarget.ENEMY,
                        effects=[MoveEffect(kind=EffectKind.DAMAGE, power=40)],
                        description="Ein elektrischer Schock"
                    ),
                    "erde": Move(
                        id="mud_slap", name="Lehmschelle", type="Erde",
                        category=MoveCategory.PHYSICAL, power=20, accuracy=100,
                        pp=30, max_pp=30, priority=0, targeting=MoveTarget.ENEMY,
                        effects=[
                            MoveEffect(kind=EffectKind.DAMAGE, power=20),
                            MoveEffect(kind=EffectKind.DEBUFF, stat="acc", stages=-1)
                        ],
                        description="Wirft Schlamm und senkt Genauigkeit"
                    )
                }
                
                if primary_type in type_moves:
                    basic_moves.append(type_moves[primary_type])
            
            # Füge alle Basic-Moves hinzu
            moves.extend(basic_moves)
            
            # Versuche species-spezifische Moves zu laden (falls vorhanden)
            if hasattr(self.species, 'learnset'):
                for learn_data in self.species.learnset:
                    if learn_data.get('level', 100) <= self.level:
                        # Hier könnten wir species-spezifische Moves laden
                        pass
            
            return moves
            
        except Exception as e:
            logger.error(f"Fehler beim Initialisieren der Moves: {e}")
            # Fallback: Mindestens einen Move zurückgeben
            from engine.systems.moves import Move, MoveCategory, MoveTarget, MoveEffect, EffectKind
            return [Move(
                id="struggle",
                name="Verzweifler",
                type="Bestie",
                category=MoveCategory.PHYSICAL,
                power=50,
                accuracy=100,
                pp=999,
                max_pp=999,
                priority=0,
                targeting=MoveTarget.ENEMY,
                effects=[MoveEffect(kind=EffectKind.DAMAGE, power=50)],
                description="Letzter Ausweg wenn keine Moves verfügbar"
            )]'''
    
    # Ersetze die alte Methode
    lines = original_content.split('\n')
    new_lines = []
    in_method = False
    skip_count = 0
    
    for i, line in enumerate(lines):
        if skip_count > 0:
            skip_count -= 1
            continue
            
        if 'def _initialize_moves(self)' in line:
            in_method = True
            new_lines.append(new_method)
            # Skip alte Methode
            indent = len(line) - len(line.lstrip())
            for j in range(i+1, len(lines)):
                if lines[j].strip() and not lines[j].startswith(' ' * (indent + 1)):
                    skip_count = j - i - 1
                    break
        elif not in_method:
            new_lines.append(line)
        else:
            in_method = False
    
    with open(monster_instance_path, 'w') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ MonsterInstance._initialize_moves() aktualisiert")

if __name__ == "__main__":
    # Erstelle Basis-Moves falls nötig
    moves = create_default_moves()
    print(f"✅ {len(moves['basic_moves'])} Basis-Moves definiert")
    
    # Fixe MonsterInstance
    fix_monster_instance()
    
    print("\n✅ Fix 3 abgeschlossen: Alle Monster haben jetzt Start-Moves")
