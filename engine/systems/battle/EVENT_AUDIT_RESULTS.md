# Event Emission Audit Results

**Gefundene Event-Emissionen:** 10
**Dateien mit Events:** 8
**Event-Types gefunden:** 8
**Duplikate gefunden:** 0

## Detaillierte Auflistung

### engine/systems/battle/event_processor.py

- L185: self.emit_event(event)

### engine/systems/battle/turn_processor.py

- L273: self.state.event_processor.emit_event(event_type, data)

### engine/systems/battle/action_processor.py

- L78: self.state.event_processor.emit_event(

### engine/systems/battle/core/battle_controller_phases.py

- L57: self.event_processor.emit_event(

### engine/systems/battle/processors/special_action_processor.py

- L207: self.state.event_processor.emit_event(

### engine/systems/battle/processors/item_action_processor.py

- L149: self.state.event_processor.emit_event(

### engine/systems/battle/processors/attack_action_processor.py

- L166: self.state.event_processor.emit_event(
- L172: self.state.event_processor.emit_event(
- L152: self.state.event_processor.emit_event(

### engine/systems/battle/events/event_processor_facade.py

- L146: self.emit_event(event)

