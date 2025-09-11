import random

class Ship:
    def __init__(self, player_name, x, y, health, flag, strategy_module):
        self.player_name = player_name
        self.x = x
        self.y = y
        self.health = health
        self.flag = flag
        self.score = 0
        self.messages = 0
        self.strategy_module = strategy_module

        # Action states for the current tick
        self.move_dx = 0
        self.move_dy = 0
        self.fire_target_x = None
        self.fire_target_y = None

    def set_movement(self, dx, dy):
        """Sets the desired movement for the next tick."""
        self.move_dx = max(-2, min(dx, 2))
        self.move_dy = max(-2, min(dy, 2))

    def clear_movement(self):
        """Clears movement for the next tick after it's been applied."""
        self.move_dx = 0
        self.move_dy = 0

    def set_fire_target(self, x, y):
        """Sets the target coordinates for firing."""
        self.fire_target_x = x
        self.fire_target_y = y

    def clear_fire_target(self):
        """Clears the fire target after processing the shot."""
        self.fire_target_x = None
        self.fire_target_y = None

    def set_new_flag(self, new_flag_value):
        """Sets a new flag value for the ship."""
        self.flag = new_flag_value

    def take_damage(self, amount):
        """Reduces ship health by the given amount and subtracts points."""
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def add_score(self, amount):
        """Increases or decreases the ship's score."""
        self.score += amount
    
    def increment_messages(self):
        """Increments messages count"""
        self.messages += 1

    def respawn(self, arena_width, arena_height, initial_health, respawn_penalty):
        """Respawns the ship at a random location with full health and applies penalty."""
        self.x = random.randint(arena_width * 0.1, arena_width * 0.9)
        self.y = random.randint(arena_height * 0.1, arena_height * 0.9)
        self.health = initial_health
        self.add_score(respawn_penalty) # Apply score penalty
        self.clear_movement() # Clear any pending movement
        self.clear_fire_target() # Clear any pending fire target
        self.flag = 0 # Reset flag on respawn

    def __repr__(self):
        return f"Ship({self.player_name}, X:{self.x}, Y:{self.y}, HP:{self.health})"
