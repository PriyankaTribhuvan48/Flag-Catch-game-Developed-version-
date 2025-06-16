
import pygame
import sys
import random
import math
import os

# Initialize pygame
pygame.init()

# Set up display dimensions
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 800
PLAYING_AREA = 600

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BROWN = (139, 69, 19)
GRAY = (100, 100, 100)
WHITE = (255, 255, 255)
LIGHT_BLUE = (173, 216, 230)
GOLD = (255, 215, 0)
GREEN = (0, 128, 0)
PURPLE = (128, 0, 128)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 0, 30)

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Flag Catcher Game")

# Input box class for signup
class InputBox:
    def __init__(self, x, y, width, height, text='', is_password=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = GRAY
        self.text = text
        self.is_password = is_password
        self.display_text = text
        self.active = False
        self.font = pygame.font.SysFont(None, 32)
        self.txt_surface = self.font.render(self.display_text, True, WHITE)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
                self.color = LIGHT_BLUE
            else:
                self.active = False
                self.color = GRAY
        
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                
                # Update display text (show asterisks for password)
                if self.is_password:
                    self.display_text = '*' * len(self.text)
                else:
                    self.display_text = self.text
                
                self.txt_surface = self.font.render(self.display_text, True, WHITE)
        return False

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect, 2)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))

# Button class
class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.font = pygame.font.SysFont(None, 32)
        self.txt_surface = self.font.render(text, True, WHITE)

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        text_width = self.txt_surface.get_width()
        text_height = self.txt_surface.get_height()
        screen.blit(self.txt_surface, 
                   (self.rect.x + (self.rect.width - text_width) // 2, 
                    self.rect.y + (self.rect.height - text_height) // 2))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


# Background elements
class Background:
    def __init__(self, level=1):
        self.stars = []
        self.offset_x = 0
        self.offset_y = 0
        self.color = DARK_BLUE
        self.generate_stars(50)
    
    def generate_stars(self, count):
        self.stars = []
        for _ in range(count):
            self.stars.append({
                'x': random.randint(0, WINDOW_WIDTH),
                'y': random.randint(0, PLAYING_AREA),
                'size': random.randint(1, 3),
                'brightness': random.randint(100, 255),
                'speed': random.uniform(0.2, 1.0)
            })
    
    def update(self):
        # Move stars for parallax effect
        self.offset_x = (self.offset_x + 0.5) % WINDOW_WIDTH
    
    def draw(self):
        # Draw background color
        screen.fill(self.color)
        
        # Draw moving stars
        for star in self.stars:
            # Calculate position with parallax effect
            x = (star['x'] - self.offset_x * star['speed']) % WINDOW_WIDTH
            y = star['y']
            
            # Make stars twinkle
            brightness = star['brightness'] + random.randint(-20, 20)
            brightness = max(100, min(255, brightness))
            pygame.draw.circle(screen, (brightness, brightness, brightness), 
                              (int(x), int(y)), star['size'])

# Flag properties
class Flag:
    def __init__(self, x, y, color, level=1, points=50):
        self.x = x
        self.y = y
        self.color = color
        self.captured = False
        speed_multiplier = 1.0 + (level * 0.1)  # Increase speed with level
        self.speed_x = random.uniform(-1.5, 1.5) * speed_multiplier
        self.speed_y = random.uniform(-1.5, 1.5) * speed_multiplier
        self.points = points + (level * 10)  # More points in higher levels
    
    def draw(self):
        if not self.captured:
            # Draw flag pole
            pygame.draw.line(screen, BROWN, (self.x, self.y), (self.x, self.y - 30), 3)
            
            # Draw triangular flag
            flag_points = [
                (self.x, self.y - 30),
                (self.x + 20, self.y - 20),
                (self.x, self.y - 10)
            ]
            pygame.draw.polygon(screen, self.color, flag_points)
    
    def move(self):
        if not self.captured:
            # Move the flag
            self.x += self.speed_x
            self.y += self.speed_y
            
            # Bounce off walls
            if self.x < 20 or self.x > WINDOW_WIDTH - 20:
                self.speed_x *= -1
            if self.y < 40 or self.y > PLAYING_AREA - 10:
                self.speed_y *= -1
    
    def check_capture(self, player_x, player_y, player_radius):
        if not self.captured:
            distance = ((player_x - self.x) ** 2 + (player_y - self.y) ** 2) ** 0.5
            if distance < player_radius + 10:
                self.captured = True
                return True
        return False

# Obstacle class
class Obstacle:
    def __init__(self, x, y, width, height, level=1):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = GRAY
        speed_multiplier = 0.5 + (level * 0.1)
        self.speed_x = random.uniform(-1, 1) * speed_multiplier
        self.speed_y = random.uniform(-1, 1) * speed_multiplier
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
    
    def move(self):
        # Move the obstacle
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Bounce off walls
        if self.x < 0 or self.x + self.width > WINDOW_WIDTH:
            self.speed_x *= -1
        if self.y < 0 or self.y + self.height > PLAYING_AREA:
            self.speed_y *= -1
    
    def check_collision(self, player_x, player_y, player_radius):
        # Check if player collides with obstacle
        closest_x = max(self.x, min(player_x, self.x + self.width))
        closest_y = max(self.y, min(player_y, self.y + self.height))
        
        distance = ((player_x - closest_x) ** 2 + (player_y - closest_y) ** 2) ** 0.5
        return distance < player_radius


# Function to create new flags
def create_flags(level=1):
    colors = [RED, GREEN, BLUE, PURPLE, GOLD, LIGHT_BLUE]
    new_flags = []
    # More flags in higher levels (6-10 flags)
    num_flags = min(6 + (level // 10), 10)
    
    for i in range(num_flags):
        flag_x = random.randint(30, WINDOW_WIDTH - 30)
        flag_y = random.randint(30, PLAYING_AREA - 30)
        new_flags.append(Flag(flag_x, flag_y, colors[i % len(colors)], level))
    return new_flags

# Function to create obstacles
def create_obstacles(level):
    obstacles = []
    # Start adding obstacles from level 2, more obstacles in higher levels
    if level >= 2:
        num_obstacles = min(level // 2, 8)  # Max 8 obstacles
        for _ in range(num_obstacles):
            width = random.randint(30, 60)
            height = random.randint(30, 60)
            x = random.randint(50, WINDOW_WIDTH - width - 50)
            y = random.randint(50, PLAYING_AREA - height - 50)
            obstacles.append(Obstacle(x, y, width, height, level))
    return obstacles

# Show signup screen
def signup_screen():
    # Create input boxes
    email_box = InputBox(WINDOW_WIDTH // 2 - 150, 300, 300, 40)
    password_box = InputBox(WINDOW_WIDTH // 2 - 150, 380, 300, 40, is_password=True)
    
    # Create button
    signup_button = Button(WINDOW_WIDTH // 2 - 100, 460, 200, 50, "Sign Up", GREEN)
    
    # Title font
    title_font = pygame.font.SysFont(None, 64)
    label_font = pygame.font.SysFont(None, 32)
    
    # Error message
    error_message = ""
    
    # Main loop
    running = True
    clock = pygame.time.Clock()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Handle input box events
            email_box.handle_event(event)
            password_box.handle_event(event)
            
            # Check for button click
            if event.type == pygame.MOUSEBUTTONDOWN:
                if signup_button.is_clicked(event.pos):
                    # Validate inputs
                    if len(email_box.text) < 5 or '@' not in email_box.text:
                        error_message = "Please enter a valid email address"
                    elif len(password_box.text) < 4:
                        error_message = "Password must be at least 4 characters"
                    else:
                        # Return success with user data
                        return True, email_box.text
        
        # Draw background
        screen.fill(DARK_BLUE)
        
        # Draw stars (simple background)
        for i in range(50):
            x = (i * 17) % WINDOW_WIDTH
            y = (i * 23) % WINDOW_HEIGHT
            pygame.draw.circle(screen, WHITE, (x, y), 1)
        
        # Draw title
        title_text = title_font.render("Flag Catcher Game", True, WHITE)
        screen.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 100))
        
        # Draw subtitle
        subtitle_text = label_font.render("Create Your Account", True, LIGHT_BLUE)
        screen.blit(subtitle_text, (WINDOW_WIDTH // 2 - subtitle_text.get_width() // 2, 180))
        
        # Draw labels
        email_label = label_font.render("Email:", True, WHITE)
        screen.blit(email_label, (WINDOW_WIDTH // 2 - 150, 270))
        
        password_label = label_font.render("Password:", True, WHITE)
        screen.blit(password_label, (WINDOW_WIDTH // 2 - 150, 350))
        
        # Draw input boxes
        email_box.draw()
        password_box.draw()
        
        # Draw button
        signup_button.draw()
        
        # Draw error message if any
        if error_message:
            error_text = label_font.render(error_message, True, RED)
            screen.blit(error_text, (WINDOW_WIDTH // 2 - error_text.get_width() // 2, 530))
        
        pygame.display.flip()
        clock.tick(30)
    
    return False, ""

# Main game function
def run_game(user_email):
    # Game variables
    player_x = WINDOW_WIDTH // 2
    player_y = PLAYING_AREA // 2
    player_speed = 5
    player_radius = 25
    
    # Level variables
    level = 1
    max_level = 50
    
    # Create background
    background = Background()
    
    # Create flags and obstacles
    flags = create_flags(level)
    obstacles = create_obstacles(level)
    
    # Game state
    score = 0
    game_over = False
    level_complete = False
    font = pygame.font.SysFont(None, 36)
    large_font = pygame.font.SysFont(None, 72)
    
    # Timer variables - 5 minutes per level
    level_duration = 300000  # 5 minutes in milliseconds
    level_start_time = pygame.time.get_ticks()
    
    # Game loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Get keyboard input
        keys = pygame.key.get_pressed()
        
        # Update background
        background.update()
        
        # Draw background
        background.draw()
        
        # Draw separator line
        pygame.draw.line(screen, GRAY, (0, PLAYING_AREA), (WINDOW_WIDTH, PLAYING_AREA), 2)
        
        if not game_over and not level_complete:
            # Check time remaining
            current_time = pygame.time.get_ticks()
            time_left = max(0, level_duration - (current_time - level_start_time))
            
            # Move the player based on arrow key presses
            if keys[pygame.K_LEFT] and player_x - player_speed > player_radius:
                player_x -= player_speed
            if keys[pygame.K_RIGHT] and player_x + player_speed < WINDOW_WIDTH - player_radius:
                player_x += player_speed
            if keys[pygame.K_UP] and player_y - player_speed > player_radius:
                player_y -= player_speed
            if keys[pygame.K_DOWN] and player_y + player_speed < PLAYING_AREA - player_radius:
                player_y += player_speed
            
            # Check collision with obstacles
            collision = False
            for obstacle in obstacles:
                obstacle.move()
                if obstacle.check_collision(player_x, player_y, player_radius):
                    collision = True
                    break
            
            # Revert position if collision detected
            if collision:
                player_x = WINDOW_WIDTH // 2
                player_y = PLAYING_AREA // 2
            
            # Draw obstacles
            for obstacle in obstacles:
                obstacle.draw()
            
            # Move and check for flag captures
            flags_captured = 0
            for flag in flags:
                flag.move()  # Move the flags
                if flag.check_capture(player_x, player_y, player_radius):
                    score += flag.points
                
                if flag.captured:
                    flags_captured += 1
            
            # Check if all flags are captured - level up
            if flags_captured == len(flags):
                if level < max_level:
                    level += 1
                    level_complete = True
                else:
                    game_over = True
            
            # Check if time is up
            if time_left == 0:
                game_over = True
            
            # Draw the flags
            for flag in flags:
                flag.draw()
            
            # Draw the player
            pygame.draw.circle(screen, WHITE, (player_x, player_y), player_radius)
            
            # Draw level and score
            level_text = font.render(f"Level: {level}/{max_level}", True, WHITE)
            screen.blit(level_text, (50, 10))
            
            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (50, PLAYING_AREA + 30))
            
            # Draw timer
            minutes = time_left // 60000
            seconds = (time_left % 60000) // 1000
            timer_text = font.render(f"Time: {minutes:02d}:{seconds:02d}", True, WHITE)
            screen.blit(timer_text, (WINDOW_WIDTH - 150, 10))
            
            # Draw user email
            email_text = font.render(f"User: {user_email}", True, WHITE)
            screen.blit(email_text, (WINDOW_WIDTH - 250, PLAYING_AREA + 30))
            
        elif level_complete:
            # Draw level complete screen
            level_text = large_font.render(f"Level {level-1} Complete!", True, GREEN)
            screen.blit(level_text, (WINDOW_WIDTH // 2 - 200, PLAYING_AREA // 2 - 50))
            
            next_text = font.render("Press SPACE to continue", True, WHITE)
            screen.blit(next_text, (WINDOW_WIDTH // 2 - 120, PLAYING_AREA // 2 + 20))
            
            # Check for space key to continue
            if keys[pygame.K_SPACE]:
                level_complete = False
                player_x = WINDOW_WIDTH // 2
                player_y = PLAYING_AREA // 2
                flags = create_flags(level)
                obstacles = create_obstacles(level)
                level_start_time = pygame.time.get_ticks()
                
        else:  # Game over
            # Draw game over screen
            if level >= max_level:
                game_over_text = large_font.render("YOU WIN!", True, GOLD)
            else:
                game_over_text = large_font.render("GAME OVER", True, RED)
                
            screen.blit(game_over_text, (WINDOW_WIDTH // 2 - 150, PLAYING_AREA // 2 - 50))
            
            final_score_text = font.render(f"Final Score: {score}", True, WHITE)
            screen.blit(final_score_text, (WINDOW_WIDTH // 2 - 80, PLAYING_AREA // 2 + 20))
            
            level_text = font.render(f"Level Reached: {level}/{max_level}", True, WHITE)
            screen.blit(level_text, (WINDOW_WIDTH // 2 - 100, PLAYING_AREA // 2 + 60))
            
            # Draw play again instruction
            reset_text = font.render("Press 'R' to play again", True, WHITE)
            screen.blit(reset_text, (WINDOW_WIDTH // 2 - 120, PLAYING_AREA // 2 + 100))
            
            # Check for reset key
            if keys[pygame.K_r]:
                game_over = False
                level = 1
                score = 0
                player_x = WINDOW_WIDTH // 2
                player_y = PLAYING_AREA // 2
                flags = create_flags(level)
                obstacles = create_obstacles(level)
                level_start_time = pygame.time.get_ticks()
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)

# Main function
def main():
    # Show signup screen first
    success, user_email = signup_screen()
    
    # If signup successful, run the game
    if success:
        run_game(user_email)
    
    # Quit pygame
    pygame.quit()
    sys.exit()

# Run the game
if __name__ == "__main__":
    main()


