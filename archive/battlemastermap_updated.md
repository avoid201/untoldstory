# 🎮 Untold Story - Battle System Design Document
## DQM × Pokémon Hybrid - AI-Optimized Reference
## **AKTUALISIERT: 2025-01-09** - Battle-Flow Fixes & Debug-Analyse

---

## 🚨 **KRITISCHE BATTLE-FLOW PROBLEME (2025-01-09)**

### **HAUPTPROBLEM IDENTIFIZIERT:**
Der Kampf endet fälschlicherweise nach dem ersten Angriff, obwohl beide Monster noch HP haben. Die `check_battle_end()` Methode wird nach JEDER einzelnen Action aufgerufen statt nur am Ende des kompl