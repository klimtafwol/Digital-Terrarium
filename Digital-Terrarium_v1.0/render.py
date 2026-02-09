import pygame



class Renderer:
    """Pygame renderer for the terrarium simulation. Handles input, timing, and drawing."""

    def __init__(self, world, tile_size=28, fps=60):
        self.world = world
        self.tile_size = tile_size
        self.fps = fps
        self.paused = False

        pygame.init()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 20)

        w = world.width * tile_size
        h = world.height * tile_size + 30
        self.screen = pygame.display.set_mode((w, h))
        pygame.display.set_caption("AI Terrarium")
    
    def _season_tint(self):
        phase = self.world.season_phase()

        spring = (0.95, 1.20, 0.95) # light green, fresh new growth
        summer = (0.95, 1.05, 0.90) # light yellow, warm
        autumn = (1.15, 0.95, 0.85) # light red, harvest
        winter = (0.90, 0.95, 1.20) # light blue, frosty

        # split year into four seasons and blend between adjacent seasons
        quarter = phase * 4.0
        idx = int(quarter) % 4
        t = quarter - int(quarter)

        t = t * t * (3 - 2 * t) # smoothstep

        palette = [spring, summer, autumn, winter, spring] # wrap around
        a = palette [idx]
        b = palette [idx + 1] 

        return (
            self._lerp(a[0], b[0], t),
            self._lerp(a[1], b[1], t),
            self._lerp(a[2], b[2], t),
        )

    def _brightness_for_food(self, value: int, max_value: int):
        # simple grayscale mapping
        if max_value <= 0:
            max_value = 1
        t = max(0.0, min(1.0, value / max_value))
        
        return int(255 * t)

    def _clamp255(self, v: float) -> int:
        return max(0, min(255, int(v)))
    
    def _lerp(self, a: float, b: float, t: float) -> float:
        return a + (b - a) * t      

    def draw(self):
        self.screen.fill((0, 0, 0))

        # scale brightness relative to current max tile
        max_food = 0
        for row in self.world.food:
            if row:
                max_food = max(max_food, max(row))

        # draw grid
        tint_r, tint_g, tint_b = self._season_tint()
        for y in range(self.world.height):
            for x in range(self.world.width):
                v = self.world.food[y][x]
                brightness = self._brightness_for_food(v, max_food)
                r = self._clamp255(brightness * tint_r)
                g = self._clamp255(brightness * tint_g)
                b = self._clamp255(brightness * tint_b)
                color = (r, g, b)
                
                rect = pygame.Rect(
                    x * self.tile_size,
                    y * self.tile_size,
                    self.tile_size - 1,
                    self.tile_size - 1
                )
                pygame.draw.rect(self.screen, color, rect)

        # HUD bar
        hud_y = self.world.height * self.tile_size
        pygame.draw.rect(self.screen, (20, 20, 20), pygame.Rect(0, hud_y, self.screen.get_width(), 30))
        text = (
            f"Tick: {self.world.time}   "
            f"Season: {self.world.season_name()}    "
            f"Total food: {self.world.total_food()}    "
            f" [SPACE] = pause/resume    "
        )
        surf = self.font.render(text, True, (220, 220, 220))
        self.screen.blit(surf, (8, hud_y + 7))

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
        return True

    def run(self, ticks_per_second=10):
        running = True
        accumulator = 0.0
        step = 1.0 / ticks_per_second

        while running:
            dt = self.clock.tick(self.fps) / 1000.0
            running = self.handle_events()

            if not self.paused:
                accumulator += dt
                while accumulator >= step:
                    self.world.update()
                    accumulator -= step

            self.draw()

        pygame.quit()
