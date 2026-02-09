import random
import math



class World:
    """A simple world simulation for a digital terrarium. Manages the state of the world, including food growth and decay, and seasonal changes."""
    
    def __init__(self, width=20, height=10):
        self.time = 0
        self.width = width
        self.height = height

        self.season_period = 365  # ticks per cycle
        self.season_amplitude = 0.7  # max multiplier

        # 2D grid of food amounts
        self.food = [[0 for _ in range(width)] for _ in range(height)]

        # Tuning knobs
        self.growth_spawns_per_tick = 6
        self.decay_rate = 0.10
        self.max_food_per_tile = 9

        random.seed(1)
    def season_phase(self) -> float:
        """Returns the current season phase, from 0 to 1"""
        return (self.time % self.season_period) / self.season_period

    def season_multiplier(self) -> float:
        """returns a smooth multiplier based on the current season"""
        phase = self.season_phase()
        # Smooth transition between seasons
        #convert 0..1 phase into 0 2pi angle
        angle = 2.0 * math.pi * phase
        return 1.0 + self.season_amplitude * math.sin(angle)
    
    def season_name(self) -> str:
        """Returns the name of the current season"""
        phase = self.season_phase()
        if phase < 0.25:
            return "Spring"
        elif phase < 0.5:
            return "Summer"
        elif phase < 0.75:
            return "Fall"
        else:
            return "Winter"

    def total_food(self) -> int:
        return sum(sum(row) for row in self.food)

    def _random_neighbor(self, x, y):
        nx = max(0, min(self.width - 1, x + random.choice([-1, 0, 1])))
        ny = max(0, min(self.height - 1, y + random.choice([-1, 0, 1])))
        return nx, ny

    def update(self):
        self.time += 1

        # --- Seasons  (smooth) ---
        spawns = int(self.growth_spawns_per_tick * self.season_multiplier())
        spawns = max(0,spawns)  # safety dont allow negative spawns

        # --- Growth ---
        for _ in range(spawns):
            x = random.randrange(self.width)
            y = random.randrange(self.height)

            if self.food[y][x] < self.max_food_per_tile:
                self.food[y][x] += 1

            # 50% chance to grow nearby (patching)
            if random.random() < 0.5:
                nx, ny = self._random_neighbor(x, y)
                if self.food[ny][nx] < self.max_food_per_tile:
                    self.food[ny][nx] += 1

        # --- Decay ---
        decayed = 0
        for y in range(self.height):
            for x in range(self.width):
                amount = self.food[y][x]
                if amount <= 0:
                    continue

                rot = 0
                for _ in range(amount):
                    if random.random() < self.decay_rate:
                        rot += 1

                if rot > 0:
                    self.food[y][x] -= rot
                    decayed += rot

        #print(f"Tick {self.time:3} | total_food={self.total_food():3} | decayed={decayed:2}")

    def debug_print_food(self):
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                v = self.food[y][x]
                row += "." if v == 0 else str(min(v, 9))
            print(row)
