"""
Breakout Game
A classic arcade-style Breakout game built with Pygame. 
Features mouse control, multiple levels, and score/lives tracking.
"""

import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
FPS = 60

# Colors
COLOR_BG = (26, 26, 46)
COLOR_PRIMARY = (15, 52, 96)
COLOR_ACCENT = (22, 199, 132)
COLOR_TEXT = (234, 234, 234)
COLOR_PADDLE = (233, 69, 96)
COLOR_BALL = (255, 214, 10)
COLOR_BRICKS = [(233, 69, 96), (22, 199, 132), (255, 214, 10), (0, 212, 255), (167, 139, 250)]


class Paddle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = 7

    def update(self, mouse_x):
        """Update paddle position based on mouse x-coordinate."""
        self.x = max(0, min(mouse_x - self.width // 2, SCREEN_WIDTH - self.width))

    def draw(self, surface):
        """Draws the paddle with a stylish border."""
        pygame.draw.rect(surface, COLOR_PADDLE, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, (255, 107, 122), (self.x, self.y, self.width, self.height), 2)

    def collides_with(self, ball):
        """Checks if the ball has hit the paddle."""
        return (self.x < ball.x < self.x + self.width and
                self.y < ball.y + ball.radius < self.y + self.height)


class Ball:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.vx = 4
        self.vy = -4
        self.speed = 4

    def update(self):
        """Calculates ball movement and wall bounces."""
        self.x += self.vx
        self.y += self.vy

        # Bounce off left/right walls
        if self.x - self.radius < 0 or self.x + self.radius > SCREEN_WIDTH:
            self.vx = -self.vx
            self.x = self.radius if self.x - self.radius < 0 else SCREEN_WIDTH - self.radius

        # Bounce off top wall
        if self.y - self.radius < 0:
            self.vy = -self.vy
            self.y = self.radius

    def draw(self, surface):
        """Draws the ball with a subtle highlight."""
        pygame.draw.circle(surface, COLOR_BALL, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (255, 237, 78), (int(self.x), int(self.y)), self.radius, 1)

    def reset(self, x, y):
        """Resets the ball to the starting position."""
        self.x = x
        self.y = y
        self.vx = (1 if random.random() > 0.5 else -1) * 3
        self.vy = -4


class Brick:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.active = True

    def draw(self, surface):
        """Draws the brick if it hasn't been destroyed yet."""
        if not self.active:
            return
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, (255, 255, 255), (self.x, self.y, self.width, self.height), 1)

    def collides_with(self, ball):
        """Calculates if the ball has struck the brick."""
        return (self.active and
                self.x < ball.x < self.x + self.width and
                self.y < ball.y < self.y + self.height)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Breakout Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_active = False
        self.game_over = False
        self.mouse_x = SCREEN_WIDTH // 2

        self.paddle = Paddle(250, 370, 100, 20)
        self.ball = Ball(300, 350, 7)
        self.bricks = []
        self.status_message = ""
        self.status_timer = 0

        self.create_bricks()

    def create_bricks(self):
        """Initializes a new layout of bricks based on the current level."""
        self.bricks = []
        brick_width = 70
        brick_height = 15
        padding_x = 10
        padding_y = 30
        rows = min(3 + self.level, 7) # Cap rows for difficulty scaling
        cols = 7

        for row in range(rows):
            for col in range(cols):
                x = col * (brick_width + padding_x) + 15
                y = row * (brick_height + padding_y) + 30
                color = COLOR_BRICKS[row % len(COLOR_BRICKS)]
                self.bricks.append(Brick(x, y, brick_width, brick_height, color))

    def handle_events(self):
        """Captures mouse movement and keyboard input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_x = event.pos[0]
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.start_game()
                elif event.key == pygame.K_r:
                    self.reset_game()
        return True

    def start_game(self):
        """Engages the active game state."""
        if not self.game_active and not self.game_over and self.lives > 0:
            self.game_active = True
            self.status_message = ""

    def reset_game(self):
        """Resets score, lives, and level back to start."""
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_active = False
        self.game_over = False
        self.ball.reset(300, 350)
        self.create_bricks()
        self.status_message = ""
        self.status_timer = 0

    def update(self):
        """Core game logic loop."""
        if not self.game_active:
            return

        self.paddle.update(self.mouse_x)
        self.ball.update()

        # Handle paddle collision with directional bounce
        if self.paddle.collides_with(self.ball):
            self.ball.vy = -abs(self.ball.vy)
            paddle_center = self.paddle.x + self.paddle.width / 2
            ball_offset = (self.ball.x - paddle_center) / (self.paddle.width / 2)
            self.ball.vx = ball_offset * 5
            self.ball.y = self.paddle.y - self.ball.radius

        # Handle brick collisions
        for brick in self.bricks:
            if brick.collides_with(self.ball):
                brick.active = False
                self.ball.vy = -self.ball.vy
                self.score += 10
                break

        # Check for life lost
        if self.ball.y > SCREEN_HEIGHT:
            self.lives -= 1
            if self.lives <= 0:
                self.game_active = False
                self.game_over = True
                self.status_message = "Game Over! Press R to reset."
                self.status_timer = 180
            else:
                self.ball.reset(300, 350)
                self.game_active = False
                self.status_message = f"Life lost! Press SPACE to continue. Lives: {self.lives}"
                self.status_timer = 120

        # Check for level completion
        if all(not brick.active for brick in self.bricks):
            self.level += 1
            self.game_active = False
            self.create_bricks()
            self.status_message = f"Level {self.level - 1} Complete! Press SPACE for next level."
            self.status_timer = 180

        # Decrease status display timer
        if self.status_timer > 0:
            self.status_timer -= 1

    def draw(self):
        """Renders all game elements and UI to the screen."""
        # Draw background gradient
        self.screen.fill(COLOR_PRIMARY)
        for y in range(SCREEN_HEIGHT):
            shade = int(15 + (22 - 15) * (y / SCREEN_HEIGHT))
            pygame.draw.line(self.screen, (shade, shade, shade + 20), (0, y), (SCREEN_WIDTH, y))

        # Draw objects
        self.paddle.draw(self.screen)
        self.ball.draw(self.screen)
        for brick in self.bricks:
            brick.draw(self.screen)

        # Render HUD
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_TEXT)
        lives_text = self.font.render(f"Lives: {self.lives}", True, COLOR_TEXT)
        level_text = self.font.render(f"Level: {self.level}", True, COLOR_TEXT)

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (SCREEN_WIDTH // 2 - 80, 10))
        self.screen.blit(level_text, (SCREEN_WIDTH - 180, 10))

        # Overlay status messages
        if self.status_timer > 0 or (not self.game_active and self.lives > 0 and not self.game_over):
            message = self.status_message if self.status_message else "Press SPACE to start!"
            text = self.small_font.render(message, True, COLOR_ACCENT)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            pygame.draw.rect(self.screen, (0, 0, 0), text_rect.inflate(20, 20))
            self.screen.blit(text, text_rect)

        # Control instructions
        if not self.game_active and not self.game_over and self.lives > 0:
            instr_text = self.small_font.render("Use MOUSE to control paddle", True, COLOR_TEXT)
            instr_rect = instr_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
            self.screen.blit(instr_text, instr_rect)

        pygame.display.flip()

    def run(self):
        """Main execution loop."""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()