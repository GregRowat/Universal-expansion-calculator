import pygame
import math
import sys
import random

pygame.init()

# define the display dimensions dynamically based on system specs.
screen_info = pygame.display.Info()
WIDTH, HEIGHT = (screen_info.current_w - 200), (screen_info.current_h - 200)
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Planet Simulation")

# Define the dimensions of each part
main_part_width = WIDTH - 400  # Width of the main part
left_part_width = 200  # Width of the left part
right_part_width = 200  # Width of the right part

# Define the Rect objects for each part
main_part_rect = pygame.Rect(0, 0, main_part_width, HEIGHT)
left_part_rect = pygame.Rect(main_part_width, 0, left_part_width, HEIGHT)
right_part_rect = pygame.Rect(main_part_width + left_part_width, 0, right_part_width, HEIGHT)

# Class to define image sprites of planets for the visualization
class Planet(pygame.sprite.Sprite):
    def __init__(self, x, y, radius, speed, image=None):
        super().__init__()
        self.lap4_completed = False
        self.image = image
        self.image = pygame.transform.scale(self.image, (radius * 2, radius * 2))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.angle = 0
        self.laps_completed = 0
        self.message = [" ", " "]

    # function to update the visualization of the orbiting planet
    def update(self, center_x, center_y):
        if self.speed != 0 and self.laps_completed < 4:  # Skip the update for the blue planet and after 4 laps
            self.angle += self.speed

            # Update position based on the angle and laps completed
            if self.laps_completed < 4:
                radius = 150 + self.laps_completed * 50
            else:
                radius = 200 + (self.laps_completed - 3) * 50

            self.rect.center = (
                center_x + radius * math.cos(math.radians(self.angle)),
                center_y + radius * math.sin(math.radians(self.angle))
            )

            # Check if the planet completed a full lap
            if self.angle >= 360:
                self.angle = 0
                self.laps_completed += 1

        if self.laps_completed == 4:
            self.lap4_completed = True
            self.message = ["Distance to the edge of observable Universe", "  46.508 billion light years"]

    # function to draw sprite to surface
    def draw(self, win):
        win.blit(self.image, self.rect)


# function to initialize and run the visualizer as a pygame process
def create_visualization_screen(selected_planet, distance, sec_mass, efficiency_index, t, calc, starting_velocity,
                                num_calc, step):
    run = True
    clock = pygame.time.Clock()
    center_x = WIDTH // 2
    center_y = HEIGHT // 2
    p_index = random.randint(1, 6)

    # Load and resize the background image
    background_image = pygame.image.load("./images/visualization_background.jpg")
    background_surface = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

    planets_group = pygame.sprite.Group()

    # Create the Earth planet with an image
    earth_image_path = "./images/earth.png"
    earth_radius = 30
    earth_image = pygame.image.load(earth_image_path).convert_alpha()
    earth = Planet(center_x, center_y, earth_radius, 0, earth_image)
    planets_group.add(earth)

    # Create the Calculation planet
    orbiting_image = pygame.image.load(f"./images/planets/planet ({p_index}).png")
    orbit_speed = 2  # Increase the orbit speed
    orbiting_planet = Planet(center_x + 150, center_y, 20, orbit_speed, orbiting_image)
    planets_group.add(orbiting_planet)

    while run:
        # Check if the user has pressed the window X or the escape key to exit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                    break

        # Do not execute the logic below if the animation has finished
        if (orbiting_planet.speed == 0):
            continue

        orbiting_planet.update(center_x, center_y)

        WIN.blit(background_surface, (0, 0))  # Blit the background image onto the window

        # Planet Orbit Draws as It Revolves around earth
        for i in range(orbiting_planet.laps_completed + 1):
            if i < 4:
                radius = 150 + i * 50
                ring_color = pygame.Color("red") if i == 3 else pygame.Color("white")
                pygame.draw.circle(WIN, ring_color, (center_x, center_y), radius, 1)

        planets_group.update(center_x, center_y)
        planets_group.draw(WIN)

        # Display algorithm results
        result_lines = [
            "Planet Name: {}".format(selected_planet),
            "Distance from Earth: {} pc".format(distance),
            "Mass: {} Earth Masses".format(sec_mass),
            "Calculation Efficiency Index: {}".format(efficiency_index)
        ]
        if orbiting_planet.lap4_completed:
            result_lines.extend((
                "------------------Algorithm Results------------------",
                "Expansion Time: {}".format(t),
                "Calculation Time: {} Seconds".format(str(round(float(calc), 4))),
                "Number of Calculations: {}".format(num_calc),
                "Initial Velocity: {} km/s".format(str(round(float(starting_velocity), 4))),
                "----------------Calculation Formula------------------",
                "First iteration of Calculation:",
                "Hubble Constant = 69.8km/s/Mpc",
                "Current velocity = Vi",
                "Vi = Hubble Const. * Mega Parsecs from Earth ",
                "For {}:".format(selected_planet),
                "Vi = 69.8 * {}".format(distance),
                "Therefore Vi = {}".format(str(round(float(starting_velocity), 4))),
                "Step size = {} Km at Efficiency Index of {} ".format(step, efficiency_index),
                "Time = step / Vi ",
                "Mpc from Earth = Current distance + Step size",
                "Recalculate each iteration with new distance ",
                "and velocity to determine total time."
            ))

        result_surface = pygame.Surface((480, len(result_lines) * 30))

        font = pygame.font.SysFont("Times New Roman", 24)
        font_color = pygame.Color("white")

        for i, line in enumerate(result_lines):
            line_surface = font.render(line, True, font_color)
            result_surface.blit(line_surface, (10, i * 30))

        WIN.blit(result_surface, (10, 100))

        # Display distance to edge of observable universe
        planet_message = font.render(orbiting_planet.message[0], True, pygame.Color("white"))
        planet_message2 = font.render(orbiting_planet.message[1], True,
                                      pygame.Color("white"))
        message_x = orbiting_planet.rect.centerx + 10
        message_y = orbiting_planet.rect.centery - 40

        WIN.blit(planet_message, (message_x, message_y))
        WIN.blit(planet_message2, (message_x, message_y + planet_message.get_height()))
        pygame.display.update()

        clock.tick(60)

        # Increment distance after completing three laps
        if orbiting_planet.laps_completed == 3:
            orbiting_planet.distance_incremented = True

        # Stop orbiting after the fourth lap
        if orbiting_planet.laps_completed == 4:
            orbiting_planet.speed = 0

    pygame.quit()


if __name__ == "__main__":
    selected_planet = sys.argv[1]
    efficiency_index = sys.argv[2]
    sec_mass = sys.argv[3]
    distance = sys.argv[4]
    t = sys.argv[5]
    calc = sys.argv[6]
    starting_velocity = sys.argv[7]
    num_calc = sys.argv[8]
    step = sys.argv[9]

    create_visualization_screen(selected_planet, distance, sec_mass, efficiency_index, t, calc, starting_velocity,
                                num_calc, step)
