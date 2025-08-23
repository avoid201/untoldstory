#!/usr/bin/env python3
"""
Simplified test for TMX integration system - with output capture
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_integration():
    """Test the TMX integration system and write results to file."""
    
    results = []
    results.append("="*60)
    results.append("TMX INTEGRATION SYSTEM TEST")
    results.append("="*60)
    results.append("")
    
    try:
        # Test 1: Import modules
        results.append("TEST 1: Import Modules")
        results.append("-" * 40)
        
        try:
            from engine.world.interaction_manager import InteractionManager
            results.append("✅ InteractionManager imported successfully")
        except Exception as e:
            results.append(f"❌ InteractionManager import failed: {e}")
            
        try:
            from engine.world.npc_manager import NPCManager
            results.append("✅ NPCManager imported successfully")
        except Exception as e:
            results.append(f"❌ NPCManager import failed: {e}")
            
        try:
            from engine.world.enhanced_map_manager import EnhancedMapManager
            results.append("✅ EnhancedMapManager imported successfully")
        except Exception as e:
            results.append(f"❌ EnhancedMapManager import failed: {e}")
        
        results.append("")
        
        # Test 2: Check data files
        results.append("TEST 2: Check Data Files")
        results.append("-" * 40)
        
        from pathlib import Path
        
        # Check interaction files
        interaction_path = Path("data/maps/interactions")
        if interaction_path.exists():
            results.append(f"✅ Interaction directory exists: {interaction_path}")
            
            for json_file in interaction_path.glob("*.json"):
                results.append(f"  ✅ Found: {json_file.name}")
        else:
            results.append(f"❌ Interaction directory missing: {interaction_path}")
        
        # Check dialog files  
        dialog_path = Path("data/dialogs/np