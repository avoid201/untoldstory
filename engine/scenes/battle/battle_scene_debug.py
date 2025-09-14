"""
Battle Scene Debug - Debug functions and logging
Max 50 lines - contains only debug utilities
"""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


def debug_battle_info(msg: str) -> None:
    """Log battle info message."""
    print(f"[BATTLE INFO] {msg}")
    logger.info(msg)


def debug_battle_error(msg: str, exc_info: bool = False) -> None:
    """Log battle error message."""
    print(f"[BATTLE ERROR] {msg}")
    logger.error(msg)
    if exc_info:
        import traceback
        traceback.print_exc()


def debug_battle_debug(msg: str) -> None:
    """Log battle debug message."""
    print(f"[BATTLE DEBUG] {msg}")
    logger.debug(msg)


def debug_battle_warning(msg: str) -> None:
    """Log battle warning message."""
    print(f"[BATTLE WARNING] {msg}")
    logger.warning(msg)


def debug_battle_success(msg: str) -> None:
    """Log battle success message."""
    print(f"[BATTLE SUCCESS] {msg}")
    logger.info(f"✅ {msg}")


def debug_battle_failure(msg: str) -> None:
    """Log battle failure message."""
    print(f"[BATTLE FAILURE] {msg}")
    logger.error(f"❌ {msg}")


def debug_battle_phase(phase: str) -> None:
    """Log battle phase change."""
    print(f"[BATTLE PHASE] {phase}")
    logger.info(f"🔄 {phase}")


def debug_battle_action(action: str) -> None:
    """Log battle action."""
    print(f"[BATTLE ACTION] {action}")
    logger.info(f"⚔️ {action}")


def debug_battle_ui(ui_state: str) -> None:
    """Log UI state change."""
    print(f"[BATTLE UI] {ui_state}")
    logger.info(f"🖥️ {ui_state}")


def debug_battle_event(event: str) -> None:
    """Log battle event."""
    print(f"[BATTLE EVENT] {event}")
    logger.info(f"📡 {event}")
