# Battleships (Educational Python Game)

Battleships is an educational game designed for learning basic agent-based programming and strategic thinking in Python. In this game, players develop "battleship bots" (Python scripts) that control a ship in a 2D arena. The goal is to outmaneuver, outwit, and outscore other bots by intelligent movement, accurate firing, and strategic communication.

## Game Overview

The game runs in a persistent arena where multiple bots compete simultaneously. There's no "game over" in the traditional sense; instead, it's a continuous battle for the top score.

### Key Features:

*   **Persistent Battle:** Ships respawn after being destroyed, keeping the battle continuous.
*   **Dynamic Scores:** Gain points for hitting enemies, lose points for taking damage, and incur a penalty for respawning. Scores can go negative.
*   **Health Visualization:** Ships are colored green when healthy, turning red as their health depletes, and appearing grey when destroyed (before respawning).
*   **Broadcast Communication:** Ships can send messages that all other ships receive, enabling team play or deceptive tactics.
*   **Autonomous Movement:** Ships maintain their last directed movement unless explicitly overridden by their strategy.
*   **Configurable Speed:** Adjust the game's tick rate to speed up or slow down simulations.
*   **Turn-based Decisions:** Each bot executes its strategy once per game tick.
*   **Logging:** All significant game events are logged to `battleships.log`.
*   **Pause/Resume Functionality:** Control the game flow with a dedicated pause button.

---

## How to Play (and Develop Your Strategy)

### 1. Game Structure

The game consists of the following main files/folders:

*   `main.py`: The entry point to launch the game arena.
*   `game_arena.py`: Manages the game logic, rendering, scores, and orchestrates bot actions.
*   `ship.py`: Defines the `Ship` class, representing a single battleship with its properties and capabilities.
*   `strategies/`: A folder where all player strategy modules reside.
    *   `strategies/0000.py`: A basic example bot demonstrating the strategy interface.

### 2. Setting Up Your Bot

To create your own bot:

1.  Navigate to the `strategies/` folder.
2.  Create a new Python file, for example, `my_awesome_bot.py`.
3.  Inside your new file, define a function named `update_strategy`. This is the core of your bot's intelligence.

Your `update_strategy` function *must* have the following signature (parameters):

```python
def update_strategy(current_x, current_y, current_health, current_flag,
                    current_dx, current_dy,
                    visible_ships, messages_received, arena_width, arena_height):
    # Your bot's logic goes here
    # ...
    return actions # A list of action dictionaries
```

### 3. Understanding the `update_strategy` Parameters

*   `current_x`, `current_y` (int): Your ship's current position.
*   `current_health` (int): Your ship's current health (from 0 to 100).
*   `current_flag` (int): Your ship's current integer flag. You can set this to anything you want (e.g., team ID, status code).
*   `current_dx`, `current_dy` (int): Your ship's current movement vector. These are values between -2 and 2, including 0.
*   `visible_ships` (list of dicts): Information about other ships within your `firing_range` (100 units). Each dictionary contains:
    *   `'x'`, `'y'` (int): Their position.
    *   `'health'` (int): Their current health.
    *   `'flag'` (int): Their current flag.
    *   `'distance'` (int): Their distance from your ship.
*   `messages_received` (list): All broadcast messages sent by any ship during the *previous* game tick.
*   `arena_width`, `arena_height` (int): The dimensions of the game arena.

### 4. Returning Actions

Your `update_strategy` function must return a `list` of dictionaries, where each dictionary represents an action your ship wants to perform this tick.

Possible action types:

*   **Move:** `{'type': 'move', 'dx': int, 'dy': int}`
    *   `dx`, `dy`: Horizontal and vertical movement. Values must be between -2 and 2 (inclusive). If you do not provide a 'move' action, your ship will continue its `current_dx` and `current_dy` for the next tick.
*   **Fire:** `{'type': 'fire', 'x': int, 'y': int}`
    *   `x`, `y`: Target coordinates to fire at. Hits occur if fired within ~10 units of a target ship.
*   **Flag:** `{'type': 'flag', 'value': int}`
    *   `value`: An integer flag. Can be used for team identification, status, or any custom purpose.
*   **Message:** `{'type': 'message', 'content': str}`
    *   `content`: The message string to broadcast to all other ships. There is a basic spam prevention mechanism (approx. 1 message every 5 ticks per ship).

**Example Action Sequence:**

```python
actions = [
    {'type': 'move', 'dx': 1, 'dy': -2},
    {'type': 'fire', 'x': 300, 'y': 450},
    {'type': 'flag', 'value': 1234},
    {'type': 'message', 'content': "Attacking quadrant B!"}
]
return actions
```

### 5. Running the Game

1.  Make sure you have [Pillow](https://pypi.org/project/Pillow/) installed: `pip install Pillow`
2.  Save your bot file (e.g., `my_awesome_bot.py`) in the `strategies/` folder.
3.  Open your terminal or command prompt.
4.  Run the game: `python main.py`

The game window will appear, loading all `.py` files found in the `strategies/` folder as competing bots.

### 6. Score System

*   **Destroy an enemy:** +1 point.
*   **Respawn:** -1 point.
*   Scores can be negative.

### 7. Health Regeneration

*   Ships regenerate 1 health point periodically (currently every `ticks_per_second // 2` ticks) when below `initial_health` (100 HP) and above 0 HP.

### 8. Logging

All significant game events (game start/pause/resume, ship respawns, flag changes, messages, attacks, destruction) are written to `battleships.log`. This can be invaluable for debugging and analyzing bot performance.

---

## Strategy Development Guide

This is an educational game, so experiment! Here are some ideas:

### Basic Tactics:

*   **Movement:**
    *   **Wall Bouncing:** Like `example_strategy.py`, move away from arena edges.
    *   **Chasing:** Move towards the nearest enemy.
    *   **Evading:** Move away from the nearest enemy, especially if your health is low.
    *   **Random Walk:** Simple, but makes you unpredictable.
*   **Firing:**
    *   **Nearest Enemy:** Always target the closest visible ship.
    *   **Lowest Health:** Target the visible ship with the lowest health to try and secure a kill.
    *   **Prioritize Threats:** Target ships that have recently hit you.

### Advanced Concepts:

*   **State Management:**
    *   Bots are stateless by default per `update_strategy` call. You can persist state (e.g., a target ID, a last known enemy position, a team strategy) using global variables within your strategy module, or by having your strategy function somehow access an object that holds state.
*   **Team Play (via Flags & Messages):**
    *   **Team Flags:** Agree on a common `flag` value with other bots to identify friends.
    *   **Broadcast Warnings:** If you see a large group of enemies, broadcast a warning (`"Enemy detected at X,Y!"`).
    *   **Coordinate Attacks:** Broadcast your target `ID` or `(X, Y)` to encourage teammates to focus fire.
    *   **Distress Calls:** If low on health, broadcast for help, giving your location.
*   **Evasion & Defense:**
    *   **Dodge incoming fire:** If you receive a message about an attack on your location, try to move away.
    *   **Strategic Retreat:** If heavily outnumbered or low on health, move towards a corner or away from enemies to regenerate health.
*   **"Vision" Management:** The `firing_range` acts as your bot's line-of-sight. Consider aggressive forward movement to gain vision, or cautious movement to stay out of range.
*   **Prediction:** Can you predict where an enemy will move based on their `current_dx`, `current_dy`, or common bot patterns? Fire at that predicted location instead of their current one.
*   **Resource Management:** If firing has a cost (not implemented here, but common in games like this), you'd manage ammunition. Here, messages have a spam limit, so use them wisely.

### Debugging Your Bot:

*   Use `print()` logs to see what your bot is "thinking" and what inputs it's receiving.
*   **Visual Observation:** Watch the game! Does your bot do what you expect? Does it get stuck?
*   **Breakpoints:** If you're using an IDE (like VS Code or PyCharm), set breakpoints in your `update_strategy` function to step through its logic.

Have fun coding your ultimate battleship!