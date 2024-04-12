import pygame
import cairosvg
import io
import random
import math

class DVDLogo:
    def __init__(self, logo_path, width, height):
        self.width = width
        self.height = height
        self.logo_path = logo_path
        self.logo_svg_content = self.load_svg_content(logo_path)
        self.colors = [
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (255, 255, 0),
            (255, 165, 0),
            (255, 20, 147) 
        ]
        self.logo = self.load_logo(self.logo_svg_content)
        self.logo_width, self.logo_height = self.logo.get_width(), self.logo.get_height()
        self.x_positions = width - self.logo_width + 1
        self.y_positions = height - self.logo_height + 1
        self.reset()
        
    def change_color(self):
        color = random.choice(self.colors)
        color_hex = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
        self.logo_svg_content = self.logo_svg_content.replace(self.current_color, color_hex)
        self.current_color = color_hex
        self.logo = self.load_logo(self.logo_svg_content)

    def load_svg_content(self, logo_path):
        with open(logo_path, "r") as file:
            svg_content = file.read()
        self.current_color = "#00feff"
        return svg_content

    def load_logo(self, svg_content):
        png_data = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'))
        return pygame.image.load(io.BytesIO(png_data))

    def reset(self):
        self.x = random.randint(0, self.width - self.logo_width)
        self.y = random.randint(0, self.height - self.logo_height)
        self.dx = random.choice([-2, 2])
        self.dy = random.choice([-2, 2])

    def update(self):
        self.x += self.dx
        self.y += self.dy

        boundary_hit = False

        if self.x <= 0 or self.x + self.logo_width >= self.width:
            self.dx = -self.dx
            boundary_hit = True
        if self.y <= 0 or self.y + self.logo_height >= self.height:
            self.dy = -self.dy
            boundary_hit = True

        if boundary_hit:
            self.change_color()

    def corner_hit(self):
        hit = (self.x == 0 and self.y == 0) or \
              (self.x == 0 and self.y == self.height - self.logo_height) or \
              (self.x == self.width - self.logo_width and self.y == 0) or \
              (self.x == self.width - self.logo_width and self.y == self.height - self.logo_height)
        if hit:
            self.change_color()
        return hit

    def time_to_next_corner_hit(self):
        dx = abs(self.dx)
        dy = abs(self.dy)
        gcd_value = DVDSimulation.gcd(self.x_positions, self.y_positions)
        lcm_value = DVDSimulation.lcm(self.x_positions, self.y_positions)

        if self.dx * self.dy > 0:
            if (self.x - self.y) % gcd_value != 0:
                return float('inf')
        else:
            if (self.x + self.y) % gcd_value != 0:
                return float('inf')

        return lcm_value / (dx + dy)

    def draw(self, screen):
        screen.blit(self.logo, (self.x, self.y))

class DVDSimulation:
    def __init__(self, width, height, logo_path):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF)
        pygame.display.set_caption("DVD Bouncing Logo")
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.dvd_logo = DVDLogo(logo_path, width, height)

    @staticmethod
    def gcd(a, b):
        while b != 0:
            a, b = b, a % b
        return a

    @staticmethod
    def lcm(a, b):
        return (a * b) // DVDSimulation.gcd(a, b)

    def run(self):
        running = True
        frame_count = 0
        corner_hit = False
        time_to_corner = self.dvd_logo.time_to_next_corner_hit()

        if math.isinf(time_to_corner):
            print("The DVD logo will never hit a corner.")
        else:
            print(f"The DVD logo will hit a corner in {time_to_corner:.2f} frames.")

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.screen.fill((0, 0, 0))
            self.dvd_logo.update()
            self.dvd_logo.draw(self.screen)

            if self.dvd_logo.corner_hit():
                corner_hit = True

            time_left = time_to_corner - frame_count
            if not math.isinf(time_to_corner) and time_left >= 0:
                seconds_left = round(time_left / self.fps)
                time_left_text = f"Time left until corner hit: {round(time_left)} frames - ({seconds_left} seconds)"
                font = pygame.font.Font(None, 30)
                text = font.render(time_left_text, True, (255, 255, 255))
                self.screen.blit(text, (10, 10))

            pygame.display.flip()
            self.clock.tick(self.fps)
            frame_count += 1

            if frame_count >= time_to_corner:
                if not corner_hit:
                    print("The DVD logo did not hit a corner within the expected time.")
                else:
                    print(f"The DVD logo hit a corner at frame {frame_count}.")
                running = False

        pygame.quit()

def main():
    width, height = 800, 600
    logo_path = "dvdlogo.svg"
    simulation = DVDSimulation(width, height, logo_path)
    simulation.run()

if __name__ == "__main__":
    main()