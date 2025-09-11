from game_arena import GameArena
import os

if __name__ == "__main__":
    # Create the strategies folder if it doesn't exist
    if not os.path.exists("strategies"):
        os.makedirs("strategies")
        print("Created 'strategies' folder. Please place your strategy files there.")

    # Instantiate the game arena
    # Set game speed: e.g., 10 ticks per second
    game_speed_tps = 10
    arena = GameArena(width=800, height=600, ticks_per_second=game_speed_tps)

    # Load strategies dynamically.
    arena.load_strategies()

    if not arena.ships:
        print("No strategies loaded or no ships registered. Ensure 'strategies' folder exists and contains valid strategy files.")
    else:
        arena.run()
