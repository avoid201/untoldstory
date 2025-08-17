"""
Running Shoes Item für das Movement System
Ermöglicht dem Spieler das Rennen
"""


class RunningShoes:
    """Running shoes item that enables running"""
    
    @staticmethod
    def give_running_shoes(game):
        """Give the player running shoes"""
        game.story_manager.set_flag('has_running_shoes', True)
        game.current_scene.dialogue_box.show_text(
            "Du hast die TURBOSCHUHE erhalten! Halte B gedrückt zum Rennen!"
        )
    
    @staticmethod
    def can_run(game) -> bool:
        """Check if player can run"""
        # Require running shoes to run
        if hasattr(game, 'story_manager'):
            return game.story_manager.get_flag('has_running_shoes', False)
        return False
    
    @staticmethod
    def check_running_shoes_obtained(game: 'Game') -> bool:
        """Check if player has obtained running shoes"""
        if hasattr(game, 'story_manager'):
            return game.story_manager.get_flag('has_running_shoes', False)
        return False
    
    @staticmethod
    def show_running_tutorial(game: 'Game') -> None:
        """Show tutorial for running shoes"""
        if hasattr(game, 'current_scene') and game.current_scene:
            if hasattr(game.current_scene, 'dialogue_box'):
                game.current_scene.dialogue_box.show_text(
                    "Tipp: Halte B gedrückt um zu rennen! Das macht das Erkunden viel schneller!"
                )
    
    @staticmethod
    def get_running_speed_multiplier(game: 'Game') -> float:
        """Get the running speed multiplier"""
        if RunningShoes.can_run(game):
            return 1.5  # 50% faster than walking
        return 1.0  # Normal walking speed
