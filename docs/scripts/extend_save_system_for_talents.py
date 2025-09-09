#!/usr/bin/env python3
"""
Erweitert das Save-System um Talent-Unterstützung
"""

import json
import sys
from pathlib import Path

def load_json_file(file_path: str):
    """Lade JSON-Datei sicher."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Fehler beim Laden von {file_path}: {e}")
        return None

def save_json_file(file_path: str, data):
    """Speichere JSON-Datei sicher."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Fehler beim Speichern von {file_path}: {e}")
        return False

def extend_save_system():
    """Erweitere das Save-System um Talent-Unterstützung."""
    
    save_file = Path('engine/systems/save.py')
    if not save_file.exists():
        print("❌ save.py nicht gefunden")
        return False
    
    # Lade aktuellen Save-Code
    with open(save_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Prüfe ob bereits erweitert
    if 'talent' in content.lower():
        print("✅ Save-System hat bereits Talent-Unterstützung")
        return True
    
    # Erstelle Backup
    backup_file = save_file.with_suffix('.py.backup')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"💾 Backup erstellt: {backup_file}")
    
    # Erweitere Save-System
    new_content = content.replace(
        'from engine.systems.monsters import MonsterSpecies',
        '''from engine.systems.monsters import MonsterSpecies
from engine.systems.talent_system import TalentInstance, TalentTier'''
    )
    
    # Erweitere Monster-Serialisierung
    monster_serialization = '''
    @staticmethod
    def serialize_monster(monster) -> Dict[str, Any]:
        """Serialize monster with talent support."""
        if not monster:
            return None
            
        return {
            'species_id': monster.species.id,
            'level': monster.level,
            'experience': monster.experience,
            'current_hp': monster.current_hp,
            'nickname': monster.nickname,
            'is_shiny': monster.is_shiny,
            'stat_stages': {
                'hp': monster.stat_stages.hp,
                'atk': monster.stat_stages.atk,
                'def': monster.stat_stages.def_,
                'mag': monster.stat_stages.mag,
                'res': monster.stat_stages.res,
                'spd': monster.stat_stages.spd
            },
            'talents': [
                {
                    'talent_id': talent.talent_id,
                    'current_tier': talent.current_tier.value,
                    'experience': talent.experience,
                    'is_learned': talent.is_learned
                }
                for talent in monster.talents
            ],
            'learned_talents': [talent.talent_id for talent in monster.talents if talent.is_learned],
            'talent_experience': {
                talent.talent_id: talent.experience 
                for talent in monster.talents
            }
        }
    
    @staticmethod
    def deserialize_monster(monster_data: Dict[str, Any]) -> 'MonsterInstance':
        """Deserialize monster with talent support."""
        if not monster_data:
            return None
            
        from engine.systems.monster_instance import MonsterInstance
        from engine.systems.monsters import get_monster_database
        
        # Lade Species
        species_id = monster_data.get('species_id')
        monster_db = get_monster_database()
        species = monster_db.get_species_by_id(species_id)
        
        if not species:
            print(f"Species {species_id} nicht gefunden")
            return None
        
        # Erstelle Monster-Instanz
        monster = MonsterInstance(
            species=species,
            level=monster_data.get('level', 1),
            experience=monster_data.get('experience', 0),
            nickname=monster_data.get('nickname', ''),
            is_shiny=monster_data.get('is_shiny', False)
        )
        
        # Setze HP
        monster.current_hp = monster_data.get('current_hp', monster.max_hp)
        
        # Setze Stat-Stages
        stat_stages = monster_data.get('stat_stages', {})
        monster.stat_stages.hp = stat_stages.get('hp', 0)
        monster.stat_stages.atk = stat_stages.get('atk', 0)
        monster.stat_stages.def_ = stat_stages.get('def', 0)
        monster.stat_stages.mag = stat_stages.get('mag', 0)
        monster.stat_stages.res = stat_stages.get('res', 0)
        monster.stat_stages.spd = stat_stages.get('spd', 0)
        
        # Lade Talents
        talents_data = monster_data.get('talents', [])
        talent_experience = monster_data.get('talent_experience', {})
        
        for talent_data in talents_data:
            talent_id = talent_data.get('talent_id')
            current_tier = talent_data.get('current_tier', 1)
            experience = talent_data.get('experience', 0)
            is_learned = talent_data.get('is_learned', False)
            
            # Erstelle Talent-Instanz
            talent_instance = TalentInstance(
                talent_id=talent_id,
                current_tier=TalentTier(current_tier),
                experience=experience,
                is_learned=is_learned
            )
            
            # Füge zu Monster hinzu
            monster.talents.append(talent_instance)
        
        return monster'''
    
    # Füge Monster-Serialisierung hinzu
    if 'serialize_monster' not in new_content:
        # Finde passende Stelle zum Einfügen
        insert_point = new_content.find('    @staticmethod')
        if insert_point != -1:
            new_content = new_content[:insert_point] + monster_serialization + '\n\n    ' + new_content[insert_point:]
        else:
            # Fallback: Am Ende der Klasse hinzufügen
            class_end = new_content.rfind('    def ')
            if class_end != -1:
                new_content = new_content[:class_end] + monster_serialization + '\n\n    ' + new_content[class_end:]
    
    # Speichere erweiterten Code
    with open(save_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Save-System erfolgreich um Talent-Unterstützung erweitert")
    return True

def main():
    """Hauptfunktion."""
    print("🔄 Erweitere Save-System um Talent-Unterstützung...")
    
    success = extend_save_system()
    
    if success:
        print("✅ Save-System-Migration erfolgreich abgeschlossen!")
        return True
    else:
        print("❌ Fehler bei der Save-System-Migration")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
