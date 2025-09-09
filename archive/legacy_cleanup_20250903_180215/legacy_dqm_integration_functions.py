"""
LEGACY BACKUP: Deprecated functions from dqm_integration.py
This file contains the deprecated integration functions that were removed.
"""

import logging
from typing import Dict, Any, List, Optional, TYPE_CHECKING

logger = logging.getLogger(__name__)

def enable_dqm_formulas(pipeline: 'DamageCalculationPipeline') -> None:
    """
    Enable DQM formulas in the damage calculation pipeline.
    NOTE: This function is deprecated - use UnifiedDamageCalculator instead.
    
    Args:
        pipeline: The pipeline to modify
    """
    logger.warning("enable_dqm_formulas is deprecated - use UnifiedDamageCalculator instead")
    # Implementation would integrate with pipeline
    pass

def disable_dqm_formulas(pipeline: 'DamageCalculationPipeline') -> None:
    """
    Disable DQM formulas and restore original calculation.
    NOTE: This function is deprecated - use UnifiedDamageCalculator instead.
    
    Args:
        pipeline: The pipeline to restore
    """
    logger.warning("disable_dqm_formulas is deprecated - use UnifiedDamageCalculator instead")
    # Implementation would rollback pipeline
    pass

class DQMIntegration:
    """
    Integration layer for DQM formulas into the existing battle system.
    This class modifies the damage calculation pipeline to use DQM formulas.
    """
    
    def __init__(self):
        """Initialize DQM integration."""
        # Lazy initialization to avoid circular imports
        self._unified_calculator: Optional['UnifiedDamageCalculator'] = None
        self._dqm_calculator: Optional['DQMCalculator'] = None  # Deprecated wrapper
        self._dqm_skill_calc: Optional['DQMSkillCalculator'] = None  # Deprecated wrapper
        self._original_stages = {}
    
    def integrate_with_pipeline(self, pipeline: 'DamageCalculationPipeline') -> None:
        """
        Integrate DQM formulas into the existing damage pipeline.
        NOTE: This method is deprecated - use UnifiedDamageCalculator instead.
        
        Args:
            pipeline: The damage calculation pipeline to modify
        """
        logger.warning("integrate_with_pipeline is deprecated - use UnifiedDamageCalculator instead")
        # Implementation would modify pipeline
        pass
    
    def rollback_integration(self, pipeline: 'DamageCalculationPipeline') -> None:
        """
        Rollback to original damage calculation.
        NOTE: This method is deprecated - use UnifiedDamageCalculator instead.
        
        Args:
            pipeline: The pipeline to restore
        """
        logger.warning("rollback_integration is deprecated - use UnifiedDamageCalculator instead")
        # Implementation would restore original pipeline
        pass
