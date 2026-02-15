import pygame
import random
import json
import os

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 550  # Increased to fit next piece preview
SCREEN_HEIGHT = 700
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
GAME_AREA_X = 50
GAME_AREA_Y = 50

# High score file path
HIGH_SCORE_FILE = 'tetris_highscore.json'

# Colors (RGB format)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (50, 50, 50)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

# Tetromino shapes (the classic 7 pieces)
# Each shape is a list of coordinates relative to a center point
SHAPES = {
    'I': [[0, 0], [0, 1], [0, 2], [0, 3]],      # Line piece
    'O': [[0, 0], [0, 1], [1, 0], [1, 1]],      # Square piece
    'T': [[0, 1], [1, 0], [1, 1], [1, 2]],      # T-piece
    'S': [[0, 1], [0, 2], [1, 0], [1, 1]],      # S-piece
    'Z': [[0, 0], [0, 1], [1, 1], [1, 2]],      # Z-piece
    'J': [[0, 0], [1, 0], [1, 1], [1, 2]],      # J-piece
    'L': [[0, 2], [1, 0], [1, 1], [1, 2]]       # L-piece
}

# Colors for each shape
SHAPE_COLORS = {
    'I': CYAN,
    'O': YELLOW,
    'T': PURPLE,
    'S': GREEN,
    'Z': RED,
    'J': BLUE,
    'L': ORANGE
}

# SRS (Super Rotation System) Wall Kick Data
# Format: rotation_state -> list of (x_offset, y_offset) to try
# Simplified version - less aggressive kicks for more natural feel

# Wall kicks for J, L, T, S, Z pieces
WALL_KICK_DATA = {
    (0, 1): [(0, 0), (-1, 0), (1, 0), (0, -1)],  # 0->R
    (1, 0): [(0, 0), (1, 0), (-1, 0), (0, 1)],   # R->0
    (1, 2): [(0, 0), (1, 0), (-1, 0), (0, -1)],  # R->2
    (2, 1): [(0, 0), (-1, 0), (1, 0), (0, 1)],   # 2->R
    (2, 3): [(0, 0), (1, 0), (-1, 0), (0, -1)],  # 2->L
    (3, 2): [(0, 0), (-1, 0), (1, 0), (0, 1)],   # L->2
    (3, 0): [(0, 0), (-1, 0), (1, 0), (0, 1)],   # L->0
    (0, 3): [(0, 0), (1, 0), (-1, 0), (0, -1)],  # 0->L
}

# Wall kicks for I piece (still needs more kicks due to its shape)
WALL_KICK_DATA_I = {
    (0, 1): [(0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0)],  # 0->R
    (1, 0): [(0, 0), (1, 0), (-1, 0), (2, 0), (-2, 0)],  # R->0
    (1, 2): [(0, 0), (1, 0), (-1, 0), (2, 0), (-2, 0)],  # R->2
    (2, 1): [(0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0)],  # 2->R
    (2, 3): [(0, 0), (1, 0), (-1, 0), (2, 0), (-2, 0)],  # 2->L
    (3, 2): [(0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0)],  # L->2
    (3, 0): [(0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0)],  # L->0
    (0, 3): [(0, 0), (1, 0), (-1, 0), (2, 0), (-2, 0)],  # 0->L
}


class Tetromino:
    """Represents a single Tetris piece"""
    
    def __init__(self, shape_name):
        self.shape_name = shape_name
        self.shape = [block[:] for block in SHAPES[shape_name]]  # Deep copy
        self.color = SHAPE_COLORS[shape_name]
        # Start at the top center of the grid
        self.x = GRID_WIDTH // 2 - 1
        self.y = 0
        # Track rotation state for SRS wall kicks (0=spawn, 1=right, 2=180, 3=left)
        self.rotation_state = 0
        
    def get_blocks(self):
        """Returns the absolute grid positions of all blocks in this piece"""
        return [[self.x + block[0], self.y + block[1]] for block in self.shape]
    
    def rotate(self):
        """Rotates the piece 90 degrees clockwise"""
        # Rotation formula: (x, y) becomes (y, -x)
        # Special case: don't rotate the square piece
        if self.shape_name == 'O':
            return
        
        self.shape = [[block[1], -block[0]] for block in self.shape]
        # Update rotation state (0->1->2->3->0)
        self.rotation_state = (self.rotation_state + 1) % 4
    
    def copy(self):
        """Creates a copy of this tetromino"""
        new_piece = Tetromino(self.shape_name)
        new_piece.shape = [block[:] for block in self.shape]
        new_piece.x = self.x
        new_piece.y = self.y
        new_piece.rotation_state = self.rotation_state
        return new_piece


class PieceBag:
    """Implements the 7-bag random system for fair piece distribution"""
    
    def __init__(self):
        self.bag = []
        self.refill_bag()
    
    def refill_bag(self):
        """Fills the bag with all 7 pieces in random order"""
        pieces = list(SHAPES.keys())
        random.shuffle(pieces)
        self.bag.extend(pieces)
    
    def get_next_piece(self):
        """Gets the next piece from the bag"""
        if len(self.bag) == 0:
            self.refill_bag()
        return self.bag.pop(0)


class Particle:
    """Simple particle for visual effects"""
    
    def __init__(self, x, y, color, velocity_x, velocity_y, lifetime):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = random.randint(3, 8)
    
    def update(self, delta_time):
        """Update particle position and lifetime"""
        self.x += self.velocity_x * delta_time / 16.67  # Normalize to ~60fps
        self.y += self.velocity_y * delta_time / 16.67
        self.lifetime -= delta_time
        return self.lifetime > 0  # Return False when particle should be removed
    
    def draw(self, screen, offset_x, offset_y):
        """Draw the particle"""
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        size = int(self.size * (self.lifetime / self.max_lifetime))
        if size > 0:
            particle_surface = pygame.Surface((size * 2, size * 2))
            particle_surface.set_alpha(alpha)
            particle_surface.fill(self.color)
            screen.blit(particle_surface, (int(self.x + offset_x - size), int(self.y + offset_y - size)))


class ParticleSystem:
    """Manages all particles"""
    
    def __init__(self):
        self.particles = []
    
    def add_line_clear_particles(self, grid_y, grid_width, block_size, offset_x, offset_y):
        """Create particles for a cleared line"""
        for x in range(grid_width):
            pixel_x = x * block_size
            pixel_y = grid_y * block_size
            
            # Create multiple particles per block
            for _ in range(3):
                velocity_x = random.uniform(-3, 3)
                velocity_y = random.uniform(-5, -2)
                color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
                lifetime = random.uniform(300, 600)
                
                particle = Particle(pixel_x, pixel_y, color, velocity_x, velocity_y, lifetime)
                self.particles.append(particle)
    
    def add_level_up_particles(self, center_x, center_y):
        """Create particles for level up"""
        for _ in range(30):
            angle = random.uniform(0, 2 * 3.14159)
            speed = random.uniform(2, 6)
            velocity_x = speed * (angle ** 0.5)  # Use angle for variation
            velocity_y = speed * ((angle + 1) ** 0.5)
            color = (255, random.randint(150, 255), random.randint(0, 100))
            lifetime = random.uniform(400, 800)
            
            particle = Particle(center_x, center_y, color, velocity_x, velocity_y, lifetime)
            self.particles.append(particle)
    
    def update(self, delta_time):
        """Update all particles"""
        self.particles = [p for p in self.particles if p.update(delta_time)]
    
    def draw(self, screen, offset_x, offset_y):
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(screen, offset_x, offset_y)


class TetrisGame:
    """Main game class that handles all game logic"""
    
    def __init__(self):
        # Create the game window
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Classic Tetris - Enhanced')
        self.clock = pygame.time.Clock()
        
        # Game state
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.next_piece_name = None
        self.piece_bag = PieceBag()
        self.game_over = False
        self.score = 0
        self.high_score = self.load_high_score()
        self.level = 1
        self.lines_cleared = 0
        
        # Timing (piece falls automatically)
        self.fall_time = 0
        self.fall_speed = 500  # Milliseconds between automatic drops (gets faster with levels)
        
        # DAS (Delayed Auto Shift) for smooth movement
        self.das_delay = 170  # Initial delay before repeating (ms)
        self.das_repeat = 50  # Time between repeats (ms)
        self.das_timer = 0
        self.das_direction = None  # 'left', 'right', or 'down'
        self.key_pressed = False
        
        # Font for displaying text
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Particle system for visual effects
        self.particles = ParticleSystem()
        
        # Animation states
        self.line_clear_animation = []  # List of (y_position, timer) for flashing lines
        self.line_clear_timer = 0
        self.level_up_flash = 0  # Timer for level up flash effect
        self.new_high_score = False  # Flag for new high score achievement
        
        # Spawn the first piece and prepare next piece
        self.next_piece_name = self.piece_bag.get_next_piece()
        self.spawn_piece()
    
    def load_high_score(self):
        """Load high score from file"""
        try:
            if os.path.exists(HIGH_SCORE_FILE):
                with open(HIGH_SCORE_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get('high_score', 0)
        except:
            pass
        return 0
    
    def save_high_score(self):
        """Save high score to file"""
        try:
            with open(HIGH_SCORE_FILE, 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except:
            pass
    
    def update_high_score(self):
        """Check and update high score if current score is higher"""
        if self.score > self.high_score:
            self.high_score = self.score
            self.new_high_score = True
            self.save_high_score()
    
    def spawn_piece(self):
        """Creates a new piece at the top of the grid"""
        self.current_piece = Tetromino(self.next_piece_name)
        self.next_piece_name = self.piece_bag.get_next_piece()
        
        # Check if the new piece immediately collides (game over condition)
        if self.check_collision(self.current_piece):
            self.game_over = True
    
    def check_collision(self, piece, offset_x=0, offset_y=0):
        """Checks if a piece collides with the grid or boundaries"""
        for block in piece.get_blocks():
            x = block[0] + offset_x
            y = block[1] + offset_y
            
            # Check boundaries
            if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
                return True
            
            # Check collision with placed blocks (but not if above the grid)
            if y >= 0 and self.grid[y][x] is not None:
                return True
        
        return False
    
    def get_ghost_piece(self):
        """Returns a copy of the current piece at its drop position"""
        if not self.current_piece:
            return None
        
        ghost = self.current_piece.copy()
        
        # Move the ghost piece down until it collides
        while not self.check_collision(ghost, 0, 1):
            ghost.y += 1
        
        return ghost
    
    def move_piece(self, dx, dy):
        """Attempts to move the current piece by dx, dy"""
        if not self.check_collision(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        return False
    
    def rotate_piece(self):
        """Attempts to rotate the current piece using SRS wall kicks"""
        if self.current_piece.shape_name == 'O':
            return  # O piece doesn't rotate
        
        # Save the old state in case all rotations fail
        old_shape = [block[:] for block in self.current_piece.shape]
        old_rotation_state = self.current_piece.rotation_state
        
        # Perform the rotation
        self.current_piece.rotate()
        new_rotation_state = self.current_piece.rotation_state
        
        # Get the appropriate wall kick data
        kick_key = (old_rotation_state, new_rotation_state)
        if self.current_piece.shape_name == 'I':
            kick_tests = WALL_KICK_DATA_I.get(kick_key, [(0, 0)])
        else:
            kick_tests = WALL_KICK_DATA.get(kick_key, [(0, 0)])
        
        # Try each wall kick offset
        for offset_x, offset_y in kick_tests:
            if not self.check_collision(self.current_piece, offset_x, offset_y):
                # This kick works! Apply the offset
                self.current_piece.x += offset_x
                self.current_piece.y += offset_y
                return  # Success!
        
        # All wall kicks failed, revert the rotation
        self.current_piece.shape = old_shape
        self.current_piece.rotation_state = old_rotation_state
    
    def lock_piece(self):
        """Locks the current piece into the grid"""
        for block in self.current_piece.get_blocks():
            x, y = block[0], block[1]
            if 0 <= y < GRID_HEIGHT:
                self.grid[y][x] = self.current_piece.color
        
        # Check for completed lines
        self.clear_lines()
        
        # Spawn a new piece
        self.spawn_piece()
    
    def clear_lines(self):
        """Removes completed lines and updates score"""
        lines_to_clear = []
        
        # Find all completed lines
        for y in range(GRID_HEIGHT):
            if all(self.grid[y][x] is not None for x in range(GRID_WIDTH)):
                lines_to_clear.append(y)
        
        # Add particles for cleared lines
        if lines_to_clear:
            for y in lines_to_clear:
                self.particles.add_line_clear_particles(y, GRID_WIDTH, BLOCK_SIZE, GAME_AREA_X, GAME_AREA_Y)
        
        # Remove completed lines and add empty lines at the top
        for y in lines_to_clear:
            del self.grid[y]
            self.grid.insert(0, [None for _ in range(GRID_WIDTH)])
        
        # Update score and level
        if lines_to_clear:
            old_level = self.level
            self.lines_cleared += len(lines_to_clear)
            # Classic Tetris scoring: 1 line=100, 2=300, 3=500, 4=800
            points = [0, 100, 300, 500, 800]
            self.score += points[len(lines_to_clear)] * self.level
            
            # Check for high score
            self.update_high_score()
            
            # Increase level every 10 lines
            self.level = self.lines_cleared // 10 + 1
            
            # Check if leveled up
            if self.level > old_level:
                self.level_up_flash = 500  # Flash for 500ms
                # Add level up particles
                center_x = GAME_AREA_X + (GRID_WIDTH * BLOCK_SIZE) // 2
                center_y = GAME_AREA_Y + (GRID_HEIGHT * BLOCK_SIZE) // 2
                self.particles.add_level_up_particles(center_x, center_y)
            
            # Make pieces fall faster as level increases
            self.fall_speed = max(100, 500 - (self.level - 1) * 50)
    
    def drop_piece(self):
        """Instantly drops the piece to the bottom"""
        while self.move_piece(0, 1):
            self.score += 1  # Small bonus for hard dropping
        self.update_high_score()  # Check if we beat high score
        self.lock_piece()
    
    def draw_grid(self):
        """Draws the game grid and all placed blocks"""
        # Draw the grid background
        grid_rect = pygame.Rect(GAME_AREA_X, GAME_AREA_Y, 
                               GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE)
        pygame.draw.rect(self.screen, BLACK, grid_rect)
        
        # Level up flash effect
        if self.level_up_flash > 0:
            flash_alpha = int(100 * (self.level_up_flash / 500))
            flash_surface = pygame.Surface((GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE))
            flash_surface.set_alpha(flash_alpha)
            flash_surface.fill((255, 215, 0))  # Gold color
            self.screen.blit(flash_surface, (GAME_AREA_X, GAME_AREA_Y))
        
        pygame.draw.rect(self.screen, WHITE, grid_rect, 2)
        
        # Draw placed blocks
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x] is not None:
                    self.draw_block(x, y, self.grid[y][x])
        
        # Draw grid lines (subtle)
        for x in range(GRID_WIDTH + 1):
            start_pos = (GAME_AREA_X + x * BLOCK_SIZE, GAME_AREA_Y)
            end_pos = (GAME_AREA_X + x * BLOCK_SIZE, GAME_AREA_Y + GRID_HEIGHT * BLOCK_SIZE)
            pygame.draw.line(self.screen, GRAY, start_pos, end_pos, 1)
        
        for y in range(GRID_HEIGHT + 1):
            start_pos = (GAME_AREA_X, GAME_AREA_Y + y * BLOCK_SIZE)
            end_pos = (GAME_AREA_X + GRID_WIDTH * BLOCK_SIZE, GAME_AREA_Y + y * BLOCK_SIZE)
            pygame.draw.line(self.screen, GRAY, start_pos, end_pos, 1)
    
    def draw_block(self, grid_x, grid_y, color, alpha=255):
        """Draws a single block at the given grid position"""
        pixel_x = GAME_AREA_X + grid_x * BLOCK_SIZE
        pixel_y = GAME_AREA_Y + grid_y * BLOCK_SIZE
        
        # Create a surface for transparency support
        block_surface = pygame.Surface((BLOCK_SIZE - 2, BLOCK_SIZE - 2))
        block_surface.set_alpha(alpha)
        block_surface.fill(color)
        
        # Draw the main block
        self.screen.blit(block_surface, (pixel_x + 1, pixel_y + 1))
        
        # Draw a border for depth (only for solid blocks)
        if alpha == 255:
            pygame.draw.rect(self.screen, WHITE, 
                            (pixel_x + 1, pixel_y + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2), 2)
    
    def draw_ghost_piece(self):
        """Draws the ghost piece (shadow) showing where the piece will land"""
        ghost = self.get_ghost_piece()
        if ghost:
            for block in ghost.get_blocks():
                if block[1] >= 0:  # Only draw blocks that are visible
                    self.draw_block(block[0], block[1], ghost.color, alpha=60)
    
    def draw_current_piece(self):
        """Draws the currently falling piece"""
        if self.current_piece:
            for block in self.current_piece.get_blocks():
                if block[1] >= 0:  # Only draw blocks that are visible
                    self.draw_block(block[0], block[1], self.current_piece.color)
    
    def draw_next_piece(self):
        """Draws the next piece preview"""
        # Draw the preview box
        preview_x = GAME_AREA_X + GRID_WIDTH * BLOCK_SIZE + 30
        preview_y = GAME_AREA_Y + 50
        preview_width = 120
        preview_height = 120
        
        # Box background
        preview_rect = pygame.Rect(preview_x, preview_y, preview_width, preview_height)
        pygame.draw.rect(self.screen, DARK_GRAY, preview_rect)
        pygame.draw.rect(self.screen, WHITE, preview_rect, 2)
        
        # "Next" label
        next_text = self.small_font.render('NEXT', True, WHITE)
        text_rect = next_text.get_rect(center=(preview_x + preview_width // 2, preview_y - 20))
        self.screen.blit(next_text, text_rect)
        
        # Draw the next piece centered in the preview box
        next_piece = Tetromino(self.next_piece_name)
        
        # Calculate bounds of the piece to center it
        blocks = next_piece.shape
        min_x = min(block[0] for block in blocks)
        max_x = max(block[0] for block in blocks)
        min_y = min(block[1] for block in blocks)
        max_y = max(block[1] for block in blocks)
        
        piece_width = (max_x - min_x + 1) * BLOCK_SIZE
        piece_height = (max_y - min_y + 1) * BLOCK_SIZE
        
        # Center the piece in the preview box
        offset_x = preview_x + (preview_width - piece_width) // 2 - min_x * BLOCK_SIZE
        offset_y = preview_y + (preview_height - piece_height) // 2 - min_y * BLOCK_SIZE
        
        for block in blocks:
            pixel_x = offset_x + block[0] * BLOCK_SIZE
            pixel_y = offset_y + block[1] * BLOCK_SIZE
            
            # Draw the block
            pygame.draw.rect(self.screen, next_piece.color,
                           (pixel_x + 1, pixel_y + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2))
            pygame.draw.rect(self.screen, WHITE,
                           (pixel_x + 1, pixel_y + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2), 2)
    
    def draw_ui(self):
        """Draws the score, level, and instructions"""
        # Score
        score_text = self.font.render(f'Score: {self.score}', True, WHITE)
        self.screen.blit(score_text, (20, 10))
        
        # High Score (below current score)
        high_score_color = (255, 215, 0) if self.new_high_score else WHITE  # Gold if new high score
        high_score_text = self.small_font.render(f'High: {self.high_score}', True, high_score_color)
        self.screen.blit(high_score_text, (20, 45))
        
        # Level (right side)
        info_x = GAME_AREA_X + GRID_WIDTH * BLOCK_SIZE + 30
        level_text = self.small_font.render(f'Level: {self.level}', True, WHITE)
        self.screen.blit(level_text, (info_x, 200))
        
        # Lines
        lines_text = self.small_font.render(f'Lines: {self.lines_cleared}', True, WHITE)
        self.screen.blit(lines_text, (info_x, 230))
        
        # Instructions (moved to right side, below stats)
        instructions = [
            'Arrow Keys: Move',
            'Up: Rotate',
            'Space: Drop',
            'R: Restart'
        ]
        y_offset = 280  # Start below the level/lines stats
        for instruction in instructions:
            text = self.small_font.render(instruction, True, WHITE)
            self.screen.blit(text, (info_x, y_offset))
            y_offset += 25
    
    def draw_game_over(self):
        """Draws the game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game Over text
        game_over_text = self.font.render('GAME OVER', True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        self.screen.blit(game_over_text, text_rect)
        
        # New High Score message if applicable
        if self.new_high_score:
            new_high_text = self.font.render('NEW HIGH SCORE!', True, (255, 215, 0))
            high_rect = new_high_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            self.screen.blit(new_high_text, high_rect)
        
        # Final score
        score_y = SCREEN_HEIGHT // 2 + 20 if self.new_high_score else SCREEN_HEIGHT // 2 + 10
        score_text = self.font.render(f'Score: {self.score}', True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, score_y))
        self.screen.blit(score_text, score_rect)
        
        # High score (if not new high score)
        if not self.new_high_score:
            high_text = self.small_font.render(f'High Score: {self.high_score}', True, WHITE)
            high_rect = high_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(high_text, high_rect)
        
        # Restart instruction
        restart_y = SCREEN_HEIGHT // 2 + 90
        restart_text = self.small_font.render('Press R to Restart', True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, restart_y))
        self.screen.blit(restart_text, restart_rect)
    
    def reset_game(self):
        """Resets the game to initial state"""
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.game_over = False
        self.score = 0
        self.new_high_score = False  # Reset the flag, but keep the high_score value
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 500
        self.piece_bag = PieceBag()
        self.particles = ParticleSystem()
        self.level_up_flash = 0
        self.das_timer = 0
        self.das_direction = None
        self.next_piece_name = self.piece_bag.get_next_piece()
        self.spawn_piece()
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Calculate time since last frame
            delta_time = self.clock.tick(60)  # 60 FPS
            
            # Handle events (keyboard input)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if self.game_over:
                        if event.key == pygame.K_r:
                            self.reset_game()
                    else:
                        if event.key == pygame.K_LEFT:
                            self.move_piece(-1, 0)
                            self.das_direction = 'left'
                            self.das_timer = 0
                            self.key_pressed = True
                        elif event.key == pygame.K_RIGHT:
                            self.move_piece(1, 0)
                            self.das_direction = 'right'
                            self.das_timer = 0
                            self.key_pressed = True
                        elif event.key == pygame.K_DOWN:
                            if self.move_piece(0, 1):
                                self.score += 1  # Small bonus for soft drop
                            self.das_direction = 'down'
                            self.das_timer = 0
                            self.key_pressed = True
                        elif event.key == pygame.K_UP:
                            self.rotate_piece()
                        elif event.key == pygame.K_SPACE:
                            self.drop_piece()
                        elif event.key == pygame.K_r:
                            self.reset_game()
                
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT and self.das_direction == 'left':
                        self.das_direction = None
                        self.key_pressed = False
                    elif event.key == pygame.K_RIGHT and self.das_direction == 'right':
                        self.das_direction = None
                        self.key_pressed = False
                    elif event.key == pygame.K_DOWN and self.das_direction == 'down':
                        self.das_direction = None
                        self.key_pressed = False
            
            # DAS (Delayed Auto Shift) - smooth continuous movement
            if not self.game_over and self.das_direction and self.key_pressed:
                self.das_timer += delta_time
                
                # Check if we should repeat the movement
                if self.das_timer >= self.das_delay:
                    # Calculate how many times to repeat based on elapsed time
                    repeats = int((self.das_timer - self.das_delay) / self.das_repeat) + 1
                    self.das_timer = self.das_delay  # Reset to repeat interval
                    
                    for _ in range(repeats):
                        if self.das_direction == 'left':
                            self.move_piece(-1, 0)
                        elif self.das_direction == 'right':
                            self.move_piece(1, 0)
                        elif self.das_direction == 'down':
                            if self.move_piece(0, 1):
                                self.score += 1
            
            # Automatic piece falling (only if game is not over)
            if not self.game_over:
                self.fall_time += delta_time
                if self.fall_time >= self.fall_speed:
                    self.fall_time = 0
                    if not self.move_piece(0, 1):
                        self.lock_piece()
            
            # Update particles
            self.particles.update(delta_time)
            
            # Update level up flash
            if self.level_up_flash > 0:
                self.level_up_flash = max(0, self.level_up_flash - delta_time)
            
            # Drawing
            self.screen.fill(BLACK)
            self.draw_grid()
            self.draw_ghost_piece()  # Draw ghost first (behind current piece)
            self.draw_current_piece()
            
            # Draw particles on top of everything
            self.particles.draw(self.screen, 0, 0)
            
            self.draw_next_piece()
            self.draw_ui()
            
            if self.game_over:
                self.draw_game_over()
            
            pygame.display.flip()
        
        pygame.quit()


# Main entry point
if __name__ == '__main__':
    game = TetrisGame()
    game.run()