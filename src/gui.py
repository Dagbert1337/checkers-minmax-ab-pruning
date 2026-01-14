import sys
import pygame
from classes import Checkers, Color, Direction, Heuristics, Algorithm, K_VALUE, Difficulty

def get_row_col_from_index(index: int) -> tuple[int,int]:
    row = index // 4
    col_offset = 1 if row % 2 == 0 else 0
    col = (index % 4) * 2 + col_offset
    return row, col

def calculate_move_params(start_index: int, end_index: int) -> tuple[Direction | None, int | None]:
    r0, c0 = get_row_col_from_index(start_index)
    r1, c1 = get_row_col_from_index(end_index)
    
    dy = r1 - r0
    dx = c1 - c0
    
    distance = abs(dy)
    
    if distance == 0 or abs(dx) != distance:
        return None, None 
    
    direction = None
    if dy < 0 and dx < 0:
        direction = Direction.UP_L
    elif dy < 0 and dx > 0:
        direction = Direction.UP_R
    elif dy > 0 and dx < 0:
        direction = Direction.DOWN_L
    elif dy > 0 and dx > 0:
        direction = Direction.DOWN_R
        
    return direction, distance

class CheckersUI:
    def __init__(self, PLAYER_COLOR_STR: str = 'w') -> None:
        if PLAYER_COLOR_STR.lower() == 'w':
            self.PLAYER_COLOR = Color.WHITE
            self.BOT_COLOR = Color.BLACK
        else:
            self.PLAYER_COLOR = Color.BLACK
            self.BOT_COLOR = Color.WHITE

        pygame.init()
        pygame.font.init()

        self.WIDTH, self.HEIGHT = 600, 650
        self.BOARD_HEIGHT = 600
        self.SQUARE_SIZE = self.WIDTH // 8

        self.SCREEN = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption(f"Checkers: You are {self.PLAYER_COLOR.name}")
        self.CLOCK = pygame.time.Clock()

        self.FONT_INDEX = pygame.font.SysFont("Arial", 12, bold=True)
        self.FONT_INPUT = pygame.font.SysFont("Consolas", 24, bold=True)
        self.FONT_MENU = pygame.font.SysFont("Consolas", 30, bold=True)
        self.FONT_TITLE = pygame.font.SysFont("Consolas", 40, bold=True)

        self.CREAM = (238, 238, 210)
        self.GREEN = (118, 150, 86)
        self.BLACK_PIECE = (20, 20, 20)
        self.WHITE_PIECE = (240, 240, 240)
        self.GOLD = (255, 215, 0)
        self.UI_BG = (50, 50, 50)
        self.TEXT_COLOR = (255, 255, 255)
        self.ERROR_COLOR = (255, 100, 100)
        self.INFO_COLOR = (100, 200, 255)


        self.game = Checkers()
        heuristic = Heuristics(0.3)
        self.bot_algo = Algorithm(heuristic.doubling_aggresive) 
        
        
        self.bot_depth = Difficulty.MEDIUM.value
        self.game_state = "MENU" 

        self.user_text = ""
        self.status_message = "Enter move (e.g. 9.13):"
        self.status_color = self.TEXT_COLOR

    def draw_menu(self) -> None:
        self.SCREEN.fill(self.UI_BG)
        
        title_surf = self.FONT_TITLE.render("CHECKERS", True, self.GOLD)
        subtitle_surf = self.FONT_MENU.render("Select Difficulty:", True, self.TEXT_COLOR)
        
        opt1 = self.FONT_INPUT.render("1 - Easy", True, self.INFO_COLOR)
        opt2 = self.FONT_INPUT.render("2 - Medium", True, self.INFO_COLOR)
        opt3 = self.FONT_INPUT.render("3 - Hard", True, self.ERROR_COLOR)
        
        cx = self.WIDTH // 2
        self.SCREEN.blit(title_surf, (cx - title_surf.get_width() // 2, 100))
        self.SCREEN.blit(subtitle_surf, (cx - subtitle_surf.get_width() // 2, 200))
        
        self.SCREEN.blit(opt1, (cx - opt1.get_width() // 2, 300))
        self.SCREEN.blit(opt2, (cx - opt2.get_width() // 2, 350))
        self.SCREEN.blit(opt3, (cx - opt3.get_width() // 2, 400))

    def draw_board(self) -> None:
        pygame.draw.rect(self.SCREEN, self.CREAM, (0, 0, self.WIDTH, self.BOARD_HEIGHT))

        for row in range(8):
            for col in range(8):
                if (row % 2 == 0 and col % 2 == 1) or (row % 2 == 1 and col % 2 == 0):
                    x = col * self.SQUARE_SIZE
                    y = row * self.SQUARE_SIZE

                    pygame.draw.rect(self.SCREEN, self.GREEN, (x, y, self.SQUARE_SIZE, self.SQUARE_SIZE))

                    index = row * 4 + (col // 2)
                    text_surface = self.FONT_INDEX.render(str(index), True, (200, 200, 200, 150))
                    self.SCREEN.blit(text_surface, (x + 5, y + 5))

    def draw_pieces(self) -> None:
        radius = self.SQUARE_SIZE // 2 - 10
        attacking_indices = set()
        
        if self.game.position_forced_by_attack != -1:
            attacking_indices.add(self.game.position_forced_by_attack)
        else:
            _, attacking_moves = self.game.possible_moves()
            
            for move in attacking_moves:
                attacking_indices.add(move[0])

        for i, piece_val in enumerate(self.game.board):
            if piece_val == 0:
                continue

            row, col = get_row_col_from_index(i)
            x = col * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
            y = row * self.SQUARE_SIZE + self.SQUARE_SIZE // 2

            color = self.WHITE_PIECE if piece_val > 0 else self.BLACK_PIECE
            pygame.draw.circle(self.SCREEN, color, (x, y), radius)
            if abs(piece_val) == K_VALUE:
                pygame.draw.circle(self.SCREEN, self.GOLD, (x, y), radius, 5)
            
            if i in attacking_indices:
                pygame.draw.circle(self.SCREEN, self.ERROR_COLOR, (x, y), radius + 2, 2)
                
    def draw_ui_panel(self) -> None:
        panel_rect = (0, self.BOARD_HEIGHT, self.WIDTH, self.HEIGHT - self.BOARD_HEIGHT)
        pygame.draw.rect(self.SCREEN, self.UI_BG, panel_rect)

        prompt_surf = self.FONT_INPUT.render(self.status_message, True, self.status_color)
        self.SCREEN.blit(prompt_surf, (10, self.BOARD_HEIGHT + 10))

        cursor = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
        input_surf = self.FONT_INPUT.render(f"> {self.user_text}{cursor}", True, self.GOLD)
        self.SCREEN.blit(input_surf, (350, self.BOARD_HEIGHT + 10))
        
        turn_text = "WHITE" if self.game.color == Color.WHITE else "BLACK"
        turn_col = self.WHITE_PIECE if self.game.color == Color.WHITE else (0,0,0)
        
        pygame.draw.rect(self.SCREEN, turn_col, (self.WIDTH - 20, self.BOARD_HEIGHT + 5, 15, 15))

    def handle_input(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_BACKSPACE:
            self.user_text = self.user_text[:-1]
        elif event.key == pygame.K_RETURN:
            self.process_human_command()
        else:
            if event.unicode in "0123456789.":
                self.user_text += event.unicode

    def process_human_command(self) -> None:
        text = self.user_text.strip()

        if "." not in text:
            self.status_message = "Use format: start.end"
            self.status_color = self.ERROR_COLOR
            return

        try:
            parts = text.split('.')
            if len(parts) != 2: raise ValueError
            p0 = int(parts[0])
            p1 = int(parts[1])
        except ValueError:
            self.status_message = "Invalid numbers."
            self.status_color = self.ERROR_COLOR
            return

        if not (0 <= p0 < 32 and 0 <= p1 < 32):
            self.status_message = "Indexes must be 0-31."
            self.status_color = self.ERROR_COLOR
            return

        direction, distance = calculate_move_params(p0, p1)
        
        if direction is None or distance is None:
            self.status_message = "Move is not diagonal."
            self.status_color = self.ERROR_COLOR
            return

        try:
            print(f"Human attempting: {p0} -> {p1} ({direction.name}, dist={distance})")
            
            turn_finished = self.game.turn(p0, direction, distance)
            
            if turn_finished:
                self.status_message = "Move accepted."
                self.status_color = self.TEXT_COLOR
            else:
                self.status_message = "Jump! continue attacking."
                self.status_color = self.INFO_COLOR
                
            self.user_text = ""
            
        except Exception as e:
            self.status_message = str(e)
            self.status_color = self.ERROR_COLOR

    def process_bot_move(self) -> None:
        self.draw_board()
        self.draw_pieces()
        self.draw_ui_panel()
        pygame.display.flip()
        
        print(f"Bot is thinking (Depth {self.bot_depth})...")
        
        _, move = self.bot_algo.minmax(self.game, self.bot_depth)
        
        if move is None:
            self.status_message = "Bot cannot move! You win."
            self.status_color = self.GOLD
            return

        position, direction, distance = move
        
        try:
            turn_finished = self.game.turn(position, direction, distance)
            
            end_pos = self.game.position_after_movement(position, direction, distance)
            
            print(f"Bot moved: {position} to {end_pos}")
            self.status_message = f"Bot: {position}.{end_pos}"
            self.status_color = self.INFO_COLOR
            
            if not turn_finished:
                pass
                
        except Exception as e:
            print(f"Bot Error: {e}")

    def run(self) -> None:
        running = True
        while running:
            
            if self.game_state == "MENU":
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_1:
                            self.bot_depth = Difficulty.EASY.value
                            self.game_state = "GAME"
                        elif event.key == pygame.K_2:
                            self.bot_depth = Difficulty.MEDIUM.value
                            self.game_state = "GAME"
                        elif event.key == pygame.K_3:
                            self.bot_depth = Difficulty.HARD.value
                            self.game_state = "GAME"
                
                self.draw_menu()
                pygame.display.flip()
                self.CLOCK.tick(30)
                continue

            if self.game.color == self.BOT_COLOR:
                pygame.time.delay(500)
                self.process_bot_move()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if self.game.color == self.PLAYER_COLOR:
                    if event.type == pygame.KEYDOWN:
                        self.handle_input(event)

            self.draw_board()
            self.draw_pieces()
            self.draw_ui_panel()

            white_exists = any(p > 0 for p in self.game.board)
            black_exists = any(p < 0 for p in self.game.board)
            
            if not white_exists:
                self.status_message = "BLACK WINS!"
                self.status_color = self.GOLD
            elif not black_exists:
                self.status_message = "WHITE WINS!"
                self.status_color = self.GOLD

            pygame.display.flip()
            self.CLOCK.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    # You can change 'w' to 'b' here to play as Black
    ui = CheckersUI('w')
    ui.run()