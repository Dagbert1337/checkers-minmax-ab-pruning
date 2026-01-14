from enum import Enum
from collections.abc import Callable
import math
import random

K_VALUE = 5

class Direction(Enum): #dla parzystego wiersza liczac od 0
    UP_L = -4
    UP_R = -3
    DOWN_L = 4
    DOWN_R = 5

class Color(Enum):
    BLACK = [-1, -K_VALUE]
    WHITE = [1, K_VALUE]

class Difficulty(Enum):
    EASY = 1
    MEDIUM = 3
    HARD = 7
    
class Checkers:
    def __init__(self, board: list[int] | None = None, color = Color.WHITE, position_forced_by_attack = -1):
        if board is None:
            self.board = [-1]*12 + [0]*8 + [1]*12
        else:
            self.board = board
        self.color = color
        self.position_forced_by_attack = position_forced_by_attack
    
    def position_after_movement(self, position: int, direction: Direction, distance = 1) -> int:
        for _ in range(distance):
            if position%8 == 4 and direction in [Direction.DOWN_L, Direction.UP_L]:
                raise Exception("Out of bounds check")
            if position%8 == 3 and direction in [Direction.UP_R, Direction.DOWN_R]:
                raise Exception("Out of bounds check")
            if position <= 3 and direction in [Direction.UP_L, Direction.UP_R]:
                raise Exception("Out of bounds check")
            if position >= 28 and direction in [Direction.DOWN_L, Direction.DOWN_R]:
                raise Exception("Out of bounds check")
            
            is_row_odd = position//4 % 2
            position += direction.value - is_row_odd
            
        return position
    
    def possible_attack_in_direction(self, position: int, direction: Direction) -> list:
        distance = 1
        try:
            after_move_index = self.position_after_movement(position, direction)
            if abs(self.board[position]) == K_VALUE:
                while self.board[after_move_index] == 0:
                    after_move_index = self.position_after_movement(after_move_index, direction)
                    distance += 1
                
            after_landing_index = self.position_after_movement(after_move_index, direction)
        except:
            return []
        if self.board[after_move_index] not in self.color.value+[0] and self.board[after_landing_index] == 0:
            return [[position, direction, distance]]
            
        return []
    
    def possible_moves_in_direction(self, direction: Direction) -> tuple[list, list]:
        normal_moves=[]
        attacking_moves=[]

        for position in range(0, 32):
            if self.board[position] not in self.color.value:
                continue
            try:
                after_move_index = self.position_after_movement(position, direction)
            except:
                continue
            if self.board[position] == 1 and direction in [Direction.DOWN_L, Direction.DOWN_R]:
                continue
            if self.board[position] == -1 and direction in [Direction.UP_L, Direction.UP_R]:
                continue
            
            distance = 1
            while self.board[after_move_index] == 0:
                normal_moves.append([position, direction, distance])
                if abs(self.board[position]) != K_VALUE:
                    break
                try:
                    after_move_index = self.position_after_movement(after_move_index, direction)
                    distance += 1
                except:
                    break

            attacking_moves += self.possible_attack_in_direction(position, direction)
                
        return normal_moves, attacking_moves

    def possible_moves(self) -> tuple[list, list]:
        normal_moves_UL, attacking_moves_UL = self.possible_moves_in_direction(Direction.UP_L)
        normal_moves_DL, attacking_moves_DL = self.possible_moves_in_direction(Direction.DOWN_L)
        normal_moves_UR, attacking_moves_UR = self.possible_moves_in_direction(Direction.UP_R)
        normal_moves_DR, attacking_moves_DR = self.possible_moves_in_direction(Direction.DOWN_R)
        normal_moves = normal_moves_UL + normal_moves_UR + normal_moves_DL + normal_moves_DR
        attacking_moves = attacking_moves_UL + attacking_moves_UR + attacking_moves_DL + attacking_moves_DR
        return normal_moves, attacking_moves
    
    def move_piece(self, position: int, direction: Direction, distance: int):
        for _ in range(distance):
            after_move_position = self.position_after_movement(position, direction)
            
            if position <= 7 and self.color == Color.WHITE:
                self.board[after_move_position] = K_VALUE
            elif position > 23 and self.color == Color.BLACK:
                self.board[after_move_position] = -K_VALUE
            else:
                self.board[after_move_position] = self.board[position]
            self.board[position] = 0
            
            position = after_move_position
    
    
    def attack_with_piece(self, position: int, direction: Direction, distance: int):
        self.move_piece(position, direction, distance+1)

    
    def print_board(self):
        print("\n    1 2 3 4 5 6 7 8")
        print("   -----------------")
        for row in range(8):
            row_str = f"{row + 1} |"
            for col in range(8):
                if (row + col) % 2 == 1:
                    index = row * 4 + col // 2
                    piece = self.board[index]
                    if piece == 1:
                        row_str += " w"
                    elif piece == K_VALUE:
                        row_str += " W"
                    elif piece == -1:
                        row_str += " b"
                    elif piece == -K_VALUE:
                        row_str += " B"
                    else:
                        row_str += " ." 
                else:
                    row_str += "  " 
            print(row_str + " |")
        print("   -----------------")
        
    def turn(self, position: int, direction: Direction, distance: int) -> bool:
        if self.position_forced_by_attack >= 0 and self.position_forced_by_attack != position:
                raise Exception("You must move the piece that is currently attacking.")

        normal_moves, attacking_moves = self.possible_moves()
        
        turn_finished = True
        
        if attacking_moves == [] and [position, direction, distance] in normal_moves:
            self.move_piece(position, direction, distance)
            turn_finished = True 

        elif [position, direction, distance] in attacking_moves or [position, direction, distance] == attacking_moves:
            self.attack_with_piece(position, direction, distance)

            after_attack_pos = self.position_after_movement(position, direction, distance+1)
            can_attack_again = []
            if self.board[after_attack_pos] != Color.WHITE.value[0]:
                can_attack_again = (self.possible_attack_in_direction(after_attack_pos, Direction.DOWN_L) + 
                                    self.possible_attack_in_direction(after_attack_pos, Direction.DOWN_R)) != []
            
            if self.board[after_attack_pos] != Color.BLACK.value[0]:
                can_attack_again = (self.possible_attack_in_direction(after_attack_pos, Direction.UP_L) + 
                                    self.possible_attack_in_direction(after_attack_pos, Direction.UP_R)) != []
            
            if can_attack_again:
                self.position_forced_by_attack = after_attack_pos
                turn_finished = False
            else:
                self.position_forced_by_attack = -1
                turn_finished = True

        else:
            raise Exception("Invalid move")


        if turn_finished:
            if self.color == Color.BLACK:
                self.color = Color.WHITE
            else:
                self.color = Color.BLACK    
        
        return turn_finished

class Player:
    @staticmethod
    def position_from_xy(x: int, y: int) -> int:
        return (y-1)*4 + (x-1)//2
    
    @staticmethod
    def settings() -> tuple[str, str, int]:
        while True:
            player_1 = input("Select who plays white:\n1 - Human\n2 - Bot\n")
            if player_1 in ['1', '2']:
                break
            print("Select '1' or '2'. Try again\n")
        while True:
            player_2 = input("Select who plays black:\n1 - Human\n2 - Bot\n")
            if player_2 in ['1', '2']:
                break
            print("Select '1' or '2'. Try again\n")
        
        while True:
            difficulty = input("Choose your difficulty:\n1 - Easy\n2 - Medium\n3 - Hard\n")
            if difficulty == '1':
                depth = Difficulty.EASY.value
                break
            if difficulty == '2':
                depth = Difficulty.MEDIUM.value
                break
            if difficulty == '3':
                depth = Difficulty.HARD.value
                break
        
        return player_1, player_2, depth
    
    @staticmethod
    def user_input(game: Checkers) -> tuple[int, Direction, int]:
        game.print_board()
        if game.color == Color.WHITE:
            print("WHITE'S TURN")
        else:
            print("BLACK'S TURN")
            
        x = int(input("Enter the X coordinate: "))
        y = int(input("Enter the Y coordinate: "))
        direction = input("In which direction do you want to move your piece? (UL/DL/UR/DR): ")
        distance = int(input("By how many tiles?: "))
        position = Player.position_from_xy(x, y)
        if direction == 'UL':
            return position, Direction.UP_L, distance
        elif direction == 'DL':
            return position, Direction.DOWN_L, distance
        elif direction == 'UR':
            return position, Direction.UP_R, distance
        elif direction == 'DR':
            return position, Direction.DOWN_R, distance
        
        raise Exception("Incorrect direction")
    
    @staticmethod
    def handle_player(game: Checkers) -> Checkers:
        while True:
            try:
                position, direction, distance = Player.user_input(game)
                is_turn_finished = game.turn(position, direction, distance)
                if is_turn_finished:
                    break 
                else:
                    print("Double jump available! You must continue attacking.")
            except Exception as e:
                print(f"Error: {e}. Try again.")
        return game
    
class Heuristics:
    def __init__(self, weight: float = 0.3) -> None:
        self.weight = weight
        
    @staticmethod
    def random_score(board: list[int]) -> float:
        return random.random()
    
    @staticmethod
    def sum_score(board: list[int]) -> float:
        if not any(piece in board for piece in Color.BLACK.value):
            return math.inf
        if not any(piece in board for piece in Color.WHITE.value):
            return -math.inf
        return sum(board)
        

    def sum_and_backline(self, board: list[int]) -> float:
        if not any(piece in board for piece in Color.BLACK.value):
            return math.inf
        if not any(piece in board for piece in Color.WHITE.value):
            return -math.inf
        
        score = sum(board)
        for i in range(4):
            if board[i] in Color.BLACK.value:
                score -= self.weight
                
        for i in range(28, 32):
            if board[i] in Color.WHITE.value:
                score += self.weight
        
        return score
    

    def sum_and_doubling(self, board: list[int]) -> float:
        if not any(piece in board for piece in Color.BLACK.value):
            return math.inf
        if not any(piece in board for piece in Color.WHITE.value):
            return -math.inf
        
        score = sum(board)
        
        for pos in range(28):
            is_row_odd = pos//4 % 2
            if pos % 8 == 4:
                continue
            
            if board[pos] in Color.BLACK.value and board[pos + Direction.DOWN_L.value - is_row_odd] in Color.BLACK.value:
                score -= self.weight
            elif board[pos] in Color.WHITE.value and board[pos + Direction.DOWN_L.value - is_row_odd] in Color.WHITE.value:
                score += self.weight
        
        for pos in range(27):
            is_row_odd = pos//4 % 2
            if pos % 8 == 3:
                continue
            
            if board[pos] in Color.BLACK.value and board[pos + Direction.DOWN_R.value - is_row_odd] in Color.BLACK.value:
                score -= self.weight
            elif board[pos] in Color.WHITE.value and board[pos + Direction.DOWN_R.value - is_row_odd] in Color.WHITE.value:
                score += self.weight
            
        return score
        
    def doubling_aggresive(self, board: list[int]) -> float:
        if not any(piece in board for piece in Color.BLACK.value):
            return math.inf
        if not any(piece in board for piece in Color.WHITE.value):
            return -math.inf
        
        score = sum(board)
        
        for pos in range(28):
            is_row_odd = pos//4 % 2
            if pos % 8 == 4:
                continue
            
            if board[pos] in Color.BLACK.value and board[pos + Direction.DOWN_L.value - is_row_odd] in Color.BLACK.value:
                score -= self.weight
            elif board[pos] in Color.WHITE.value and board[pos + Direction.DOWN_L.value - is_row_odd] in Color.WHITE.value:
                score += self.weight
        
        for pos in range(27):
            is_row_odd = pos//4 % 2
            if pos % 8 == 3:
                continue
            
            if board[pos] in Color.BLACK.value and board[pos + Direction.DOWN_R.value - is_row_odd] in Color.BLACK.value:
                score -= self.weight
            elif board[pos] in Color.WHITE.value and board[pos + Direction.DOWN_R.value - is_row_odd] in Color.WHITE.value:
                score += self.weight
            
            for pos in range(31):
                if board[pos] == 0:
                    continue
                elif board[pos] in Color.BLACK.value:
                    score -= pos//4 * self.weight
                else:
                    score += (31-pos)//4 * self.weight
            
        return score
    
    
class Algorithm:
    def __init__(self, heuristic: Callable[[list[int]], float]):
        self.heuristic = heuristic
        self.memory = {}
        self.init_zobrist()
    
    def init_zobrist(self):
        # random bitstrings for zobrist hashing
        self.z_board = [[random.getrandbits(64) for _ in range(4)] for _ in range(32)]
        self.z_black_turn = random.getrandbits(64)
        # 33 positions for forced attack: 0-31 for board indices, 32 for value -1 (no forced move)
        self.z_forced_pos = [random.getrandbits(64) for _ in range(33)]

        self.piece_map = {Color.WHITE.value[0]: 0, Color.WHITE.value[1]: 1, Color.BLACK.value[0]: 2, Color.BLACK.value[1]: 3}
    
    def compute_zobrist_hash(self, game: Checkers):
        h = 0
        for position in range(32):
            piece = game.board[position]
            if piece != 0:
                piece_idx = self.piece_map[piece]
                h ^= self.z_board[position][piece_idx]
        
        if game.color == Color.BLACK:
            h ^= self.z_black_turn

        forced_idx = 32 if game.position_forced_by_attack == -1 else game.position_forced_by_attack
        h ^= self.z_forced_pos[forced_idx]
        
        return h
    
    def minmax(self, game: Checkers, depth: int, alpha = -math.inf, beta = math.inf) -> tuple[float, list | None]:
        alpha_orig = alpha
        beta_orig = beta
        board_hash = self.compute_zobrist_hash(game)
        
        if board_hash in self.memory:
            stored_depth, stored_score, stored_move, flag = self.memory[board_hash]
            if stored_depth >= depth:
                if flag == 'EXACT':
                    return stored_score, stored_move
                elif flag == 'LOWER':
                    alpha = max(alpha, stored_score)
                elif flag == 'UPPER':
                    beta = min(beta, stored_score)
                
                if alpha >= beta:
                    return stored_score, stored_move
                
                
        if depth < 1:   
            return self.heuristic(game.board), None
        
        normal_moves, attacking_moves = game.possible_moves()
        possible_moves = attacking_moves if attacking_moves else normal_moves

        version = -1 if game.color == Color.BLACK else 1
        
        minmax_score = -math.inf * version
        best_move = None
        
        if not possible_moves:
            return self.heuristic(game.board), None
        
        for [position, direction, distance] in possible_moves:
            board_copy = game.board[:]
            game_to_check = Checkers(board_copy, game.color, game.position_forced_by_attack)
            try:
                is_turn_finished = game_to_check.turn(position, direction, distance)
                
                if is_turn_finished:
                    score, _ = self.minmax(game_to_check, depth - 1, alpha, beta)
                else:
                    score, _ = self.minmax(game_to_check, depth, alpha, beta)
            
                if score * version >= minmax_score * version:
                        minmax_score = score
                        best_move = [position, direction, distance]
                
                if version == 1:
                    alpha = max(alpha, minmax_score)
                    if alpha >= beta:
                        break
                else:
                    beta = min(beta, minmax_score)
                    if beta <= alpha:
                        break
                    
            except Exception:
                continue
        
        tt_flag = 'EXACT'
        if minmax_score <= alpha_orig:
            tt_flag = 'UPPER'
        elif minmax_score >= beta_orig:
            tt_flag = 'LOWER'
            
        self.memory[board_hash] = (depth, minmax_score, best_move, tt_flag)
        
        return minmax_score, best_move