import random

def update_strategy(current_x, current_y, current_health, current_flag,
                    current_dx, current_dy,
                    visible_ships, messages_received, arena_width, arena_height):
    """
    A basic example strategy for a battleship bot.

    Args:
        current_x (int): The ship's current X coordinate.
        current_y (int): The ship's current Y coordinate.
        current_health (int): The ship's current health.
        current_flag (int): The ship's current flag value.
        current_dx (int): The ship's current movement in X direction (-2 to 2).
        current_dy (int): The ship's current movement in Y direction (-2 to 2).
        visible_ships (list): A list of dictionaries, each containing info
                              about other ships within range (x, y, health, flag, distance).
        messages_received (list): A list of strings, each containing a broadcast message.
        arena_width (int): The width of the game arena.
        arena_height (int): The height of the game arena.

    Returns:
        list: A list of action dictionaries.
              Possible actions:
              - {'type': 'move', 'dx': int, 'dy': int} (dx, dy from -2 to 2)
              - {'type': 'fire', 'x': int, 'y': int}
              - {'type': 'flag', 'value': int}
              - {'type': 'message', 'content': str} (always broadcast)
    """
    actions = []

    # Movement strategy: Bounce off walls and maintain direction
    move_dx = current_dx # Default to current movement
    move_dy = current_dy # Default to current movement

    # Simple wall bouncing
    if current_x < 10:
        move_dx = 1
    elif current_x > arena_width - 10:
        move_dx = -1

    if current_y < 10:
        move_dy = 1
    elif current_y > arena_height - 10:
        move_dy = -1
    
    # Make sure the ship is moving
    if abs(current_dx) < 1:
        move_dx = random.choice([-1, 1])
    if abs(current_dy) < 1:
        move_dy = random.choice([-1, 1])

    # Ensure move_dx and move_dy are within valid bounds (-2 to 2)
    move_dx = max(-2, min(move_dx, 2))
    move_dy = max(-2, min(move_dy, 2))

    # Evation strategy: Flee from the nearest ship
    if visible_ships:
        nearest_ship = None
        min_distance = float('inf')

        for ship_info in visible_ships:
            if ship_info['health'] > 0 and ship_info['distance'] < min_distance:
                min_distance = ship_info['distance']
                nearest_ship = ship_info

        if nearest_ship:
            if nearest_ship['x'] > current_x:
                move_dx = -2
            else:
                move_dx = 2
            if nearest_ship['y'] > current_y:
                move_dy = -2
            else:
                move_dy = 2

    actions.append({'type': 'move', 'dx': move_dx, 'dy': move_dy})

    return actions