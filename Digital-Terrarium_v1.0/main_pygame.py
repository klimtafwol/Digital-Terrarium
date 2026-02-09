from world import World
from render import Renderer

def main():
    world = World(width=20, height=10)
    renderer = Renderer(world, tile_size=28, fps=60)
    renderer.run(ticks_per_second=10)

if __name__ == "__main__":
    main()
