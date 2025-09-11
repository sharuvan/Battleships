import tkinter as tk
import math
import importlib
import os
import random
from ship import Ship
from datetime import datetime
from PIL import Image, ImageTk

class GameArena:
    def __init__(self, width=1000, height=1000, ticks_per_second=10):
        self.width = width
        self.height = height
        self.tick = 0
        self.ticks_per_second = ticks_per_second
        self.update_interval = int(1000 / ticks_per_second)
        if self.update_interval <= 0:
            self.update_interval = 1 # Minimum 1ms to prevent infinite loop

        self.ships = []
        self.messages_queue = [] # Renamed to messages_queue for clarity, to store messages to be broadcast
        self.paused = False

        self.root = tk.Tk()
        self.root.title("Battleships")
        icon_path = "icon.png"
        if os.path.exists(icon_path):
            try:
                pil_image = Image.open(icon_path)
                self.icon_photo = ImageTk.PhotoImage(pil_image)
                self.root.iconphoto(True, self.icon_photo)
            except Exception as e:
                self.write_log(f"Error loading icon {icon_path}: {e}")
        else:
            self.write_log(f"Icon file not found at: {icon_path}")

        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="light blue")
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)

        self.scoreboard_frame = tk.Frame(self.root, width=200)
        self.scoreboard_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.scoreboard_label = tk.Label(self.scoreboard_frame, text="Scores:")
        self.scoreboard_label.pack(pady=5)
        self.score_labels = {} # To hold labels for individual ship scores

        # Pause/Resume Button
        self.pause_button = tk.Button(self.scoreboard_frame, text="Pause", command=self.toggle_pause)
        self.pause_button.pack(side=tk.BOTTOM, pady=10)

        self.firing_range = 100 # Ships receive info if within this range
        self.initial_health = 100 # Define initial and respawn health
        self.respawn_penalty = -1 # Points subtracted on respawn
        self.kill_points = 1 # Points gained on kill

        self.log_file = open("battleships.log", "a")
        self.write_log("Game started")

    def load_strategies(self, strategy_folder="strategies"):
        """Loads all ship strategies from the specified folder."""
        if not os.path.exists(strategy_folder):
            print(f"Strategy folder '{strategy_folder}' not found.")
            return

        print(f"Loading strategies from: {strategy_folder}")
        for filename in os.listdir(strategy_folder):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = filename[:-3] # Remove .py extension
                try:
                    spec = importlib.util.spec_from_file_location(module_name, os.path.join(strategy_folder, filename))
                    strategy_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(strategy_module)

                    if hasattr(strategy_module, 'update_strategy'):
                        print(f"Successfully loaded strategy: {module_name}")
                        self.register_ship_strategy(strategy_module, module_name)
                    else:
                        print(f"Warning: {filename} does not contain an 'update_strategy' function.")
                except Exception as e:
                    print(f"Error loading strategy {filename}: {e}")

    def register_ship_strategy(self, strategy_module, player_name):
        """
        Registers a new ship with its strategy.
        Initial positions will be random for now.
        Health starts at self.initial_health.
        """
        initial_x = random.randint(self.width * 0.1, self.width * 0.9)
        initial_y = random.randint(self.height * 0.1, self.height * 0.9)
        initial_health = self.initial_health
        initial_flag = 0 # Default flag
        new_ship = Ship(player_name, initial_x, initial_y, initial_health, initial_flag, strategy_module)
        self.ships.append(new_ship)
        self.score_labels[player_name] = tk.Label(self.scoreboard_frame, text=f"{player_name}: {new_ship.score}")
        self.score_labels[player_name].pack(pady=2)

    def run(self):
        """Starts the game loop."""
        self.root.after(self.update_interval, self._game_loop)
        self.root.mainloop()

    def toggle_pause(self):
        """Toggles the game's paused state."""
        self.paused = not self.paused
        if self.paused:
            self.pause_button.config(text="Resume")
            self.write_log("Game paused")
            if self._after_id:
                self.root.after_cancel(self._after_id)
                self._after_id = None
        else:
            self.pause_button.config(text="Pause")
            self.write_log("Game resumed")
            if not self._after_id:
                self._after_id = self.root.after(self.update_interval, self._game_loop)

    def write_log(self, content):
        print(content)
        self.log_file.write(datetime.isoformat(datetime.now()) + " " + content + "\n")
        self.log_file.flush()

    def _game_loop(self):
        """
        Main game loop. Called repeatedly by Tkinter's after method.
        """
        
        self.tick += 1
        self.canvas.delete("all")

        # Prepare messages from the queue to be passed to each ship
        # In this broadcast-only model, all messages go to all ships
        current_tick_messages = self.messages_queue[:]
        self.messages_queue = []
        random.shuffle(self.ships)

        for ship in self.ships:
            # Check for respawn if ship is destroyed
            if ship.health <= 0:
                ship.respawn(self.width, self.height, self.initial_health, self.respawn_penalty)
            # Replenish health
            elif ship.health < 100:
                if self.tick % 3 == 0:
                    ship.health += 1

            # Prepare visible ships info for the current ship's strategy
            visible_ships_info = []
            for other_ship in self.ships:
                if other_ship != ship and other_ship.health > 0: # Only show alive ships
                    distance = math.sqrt((ship.x - other_ship.x)**2 + (ship.y - other_ship.y)**2)
                    if distance <= self.firing_range: # Only provide info if within range
                        visible_ships_info.append({
                            'x': other_ship.x,
                            'y': other_ship.y,
                            'health': other_ship.health,
                            'flag': other_ship.flag,
                            'distance': int(distance)
                        })

            # Call the ship's strategy to get actions
            actions = ship.strategy_module.update_strategy(
                current_x=ship.x,
                current_y=ship.y,
                current_health=ship.health,
                current_flag=ship.flag,
                current_dx=ship.move_dx,
                current_dy=ship.move_dy,
                visible_ships=visible_ships_info,
                messages_received=current_tick_messages,
                arena_width=self.width,
                arena_height=self.height
            )

            # Process actions
            self._process_ship_actions(ship, actions)

        # Apply movements and resolve attacks after all strategies have decided
        self._update_all_ships_state()
        self._resolve_attacks()

        self._draw_ships()
        self._update_scoreboard()

        if not self.paused:
            self._after_id = self.root.after(self.update_interval, self._game_loop)
        else:
            self._after_id = None

    def _process_ship_actions(self, ship, actions):
        """Processes the actions returned by a ship's strategy."""
        # Reset movement intent for the current tick, but not the ship's actual dx/dy
        # The ship's internal dx/dy will only change if a 'move' action is given
        move_action_given = False
        move_processed = False
        fire_processed = False
        flag_processed = False
        message_processed = False
        for action in actions:
            action_type = action.get('type')
            if action_type == 'move':
                if move_processed: continue
                dx = action.get('dx', 0)
                dy = action.get('dy', 0)
                ship.set_movement(dx, dy)
                move_processed = True
                move_action_given = True
            elif action_type == 'fire':
                if fire_processed: continue
                target_x = action.get('x')
                target_y = action.get('y')
                if target_x is not None and target_y is not None:
                    ship.set_fire_target(target_x, target_y)
                fire_processed = True
            elif action_type == 'flag':
                if flag_processed: continue
                new_flag = action.get('value')
                if isinstance(new_flag, int):
                    ship.set_new_flag(new_flag)
                    self.write_log(f"Flag updated by {ship.player_name}: {new_flag}")
                flag_processed = True
            elif action_type == 'message':
                if message_processed: continue
                # if (ship.messages / self.tick) < 0.05: # Prevent spam
                message_content = action.get('content', '')
                if isinstance(message_content, str) and len(message_content) <= 100:
                    self.messages_queue.append(message_content)
                    ship.increment_messages()
                    self.write_log(f"Message from {ship.player_name}: {message_content}")
                message_processed = True

    def _update_all_ships_state(self):
        """Applies movement to all ships and keeps them within bounds."""
        for ship in self.ships:
            if ship.health > 0: # Only move if alive
                ship.x += ship.move_dx # Ships sustain last movement
                ship.y += ship.move_dy

                # Keep ships within arena bounds
                ship.x = max(0, min(ship.x, self.width))
                ship.y = max(0, min(ship.y, self.height))

    def _resolve_attacks(self):
        """Resolves all firing actions for the current tick."""
        for ship in self.ships:
            if ship.health <= 0:
                continue

            if ship.fire_target_x is not None and ship.fire_target_y is not None:
                hit_something = False
                for target_ship in self.ships:
                    if target_ship != ship and target_ship.health > 0: # Only hit alive targets
                        distance_to_target = math.sqrt((ship.fire_target_x - target_ship.x)**2 + (ship.fire_target_y - target_ship.y)**2)
                        if distance_to_target < 10: # A small radius for hits
                            damage = 4
                            # Target ship takes damage and loses points
                            target_ship.take_damage(damage)
                            # Award points to the shooter
                            if target_ship.health <= 0: # If the hit destroys the target
                                ship.add_score(self.kill_points)
                                self.write_log(f"{ship.player_name} destroyed {target_ship.player_name}")
                                self.write_log(f"Score updated {ship.player_name}:{ship.score} {target_ship.player_name}:{target_ship.score-1}")
                            hit_something = True
                
                # If a ship fires but doesn't hit anything, no penalty for missing
                ship.clear_fire_target() # Clear target after processing

    def _draw_ships(self):
        """Draws all ships on the canvas, with color indicating health."""
        for ship in self.ships:
            x, y = ship.x, ship.y
            ship_size = 5

            # Determine color based on health
            if ship.health <= 0:
                fill_color = "grey" # Destroyed ships are grey
                text_color = "dark grey"
            else:
                # Interpolate between green (100% health) and red (0% health)
                # Max health is self.initial_health
                ratio = ship.health / self.initial_health
                # Ensure ratio is within [0, 1]
                ratio = max(0, min(ratio, 1))

                # Green component decreases as health goes down
                # Red component increases as health goes down
                red_val = int(255 * (1 - ratio))
                green_val = int(255 * ratio)
                blue_val = 0
                fill_color = f"#{red_val:02x}{green_val:02x}{blue_val:02x}"
                text_color = "black"


            self.canvas.create_rectangle(x - ship_size, y - ship_size, x + ship_size, y + ship_size, fill=fill_color, outline="dark green")
            # Display player name and health
            self.canvas.create_text(x, y - ship_size - 5, text=ship.player_name, fill=text_color, font=("Arial", 8))

    def _update_scoreboard(self):
        """Updates the scoreboard with current scores and health."""
        # Clear existing score labels
        for label in self.score_labels.values():
            label.destroy()
        self.score_labels.clear()

        # Sort ships by score for a leaderboard effect, then by player_name alphabetically
        sorted_ships = sorted(
            self.ships,
            key=lambda s: (-s.score, s.player_name)
        )

        for ship in sorted_ships:
            color = "black"
            if ship.health <= 0:
                color = "dark grey" # Indicate destroyed ships on scoreboard
            self.score_labels[ship.player_name] = tk.Label(
                self.scoreboard_frame,
                text=f"{ship.player_name} {ship.score}",
                fg=color
            )
            self.score_labels[ship.player_name].pack(pady=2, anchor=tk.W)
