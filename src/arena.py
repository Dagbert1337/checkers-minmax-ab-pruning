from classes import *
import json
import random


def simulate_custom_game(heuristic_white, depth_white, heuristic_black, depth_black, max_turns=100,
                         random_moves_count=1) -> tuple[int, int]:
    """
    Symuluje grę między dwoma botami z możliwością losowego otwarcia.

    :param random_moves_count: Liczba pierwszych tur, w których boty grają losowo.
    """
    game = Checkers()
    algo_white = Algorithm(heuristic_white)
    algo_black = Algorithm(heuristic_black)

    turn_counter = 1

    # Funkcja pomocnicza do wybierania ruchu (Losowo lub Minmax)
    def get_move(algo, depth, current_turn):
        # 1. Jeśli jesteśmy w fazie losowej -> Losuj
        if current_turn <= random_moves_count:
            normal, attacking = game.possible_moves()
            # Zasada bicia: jeśli są bicia (attacking), musimy z nich wybierać
            valid_moves = attacking if attacking else normal

            if not valid_moves:
                return None, None  # Brak ruchów

            # Zwracamy losowy ruch i atrapę wyniku (np. 0), bo nie oceniamy planszy
            return 0, random.choice(valid_moves)

        # 2. Jeśli faza losowa minęła -> Użyj Minmax
        else:
            return algo.minmax(game, depth)

    while turn_counter <= max_turns:
        # --- RUCH BIAŁYCH ---
        if game.color == Color.WHITE:
            _, move = get_move(algo_white, depth_white, turn_counter)

            if move is None:
                return 2, turn_counter

            while True:
                finished = game.turn(move[0], move[1], move[2])
                if finished:
                    break
                # Kontynuacja bicia (też losowa jeśli wciąż trwa faza losowa)
                _, move = get_move(algo_white, depth_white, turn_counter)
                if move is None: break

        if not any(p < 0 for p in game.board):
            return 1, turn_counter

        # --- RUCH CZARNYCH ---
        if game.color == Color.BLACK:
            _, move = get_move(algo_black, depth_black, turn_counter)

            if move is None:
                return 1, turn_counter

            while True:
                finished = game.turn(move[0], move[1], move[2])
                if finished:
                    break
                _, move = get_move(algo_black, depth_black, turn_counter)
                if move is None: break

        if not any(p > 0 for p in game.board):
            return 2, turn_counter

        turn_counter += 1

    return 3, turn_counter


def run_experiment():
    h = Heuristics(0.3)
    H_LIST = [h.random_score, h.sum_score, h.sum_and_doubling, h.doubling_aggresive, h.sum_and_backline]
    H_NAMES = ["random_score", "sum_score", "sum_and_doubling", "doubling_aggresive", "sum_and_backline"]
    data = {}
    # Scenariusz:
    # Białe: Grają agresywnie (doubling_aggresive), myślą płytko (EASY=1)
    # Czarne: Grają klasycznie (sum_score), ale myślą głęboko (MEDIUM=3)

    counter = 0
    for h1 in H_LIST:
        for h2 in H_LIST:
            for d1 in range(2,5):
                for d2 in range(2,5):
                    for _ in range(10):
                        result, turns = simulate_custom_game(
                            heuristic_white=h1,
                            depth_white=d1,
                            heuristic_black=h2,
                            depth_black=d2
                        )
                        name1 = H_NAMES[H_LIST.index(h1)]
                        name2 = H_NAMES[H_LIST.index(h2)]
                        winner_str = {1: "BIALE", 2: "CZARNE", 3: "REMIS"}[result]
                        data[counter] = {"winner": winner_str, "turns": turns, "heuristic_white": name1,
                                         "heuristic_black": name2, "depth_black": d2, "depth_white": d1}
                        counter += 1

    file = open("statistics.json", "w")
    file.write(json.dumps(data, indent=4))


def scrap_data(colour, depth, heuristic):
    # Używamy konstrukcji 'with open', żeby plik bezpiecznie się zamknął po odczycie
    try:
        with open("statistics.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        print("Nie znaleziono pliku statistics.json")
        return []

    total_games = 0
    total_wins = 0
    total_loses = 0
    total_draws = 0

    # Sumy długości gier (do średniej)
    sum_win_length = 0
    sum_lose_length = 0
    sum_draw_length = 0

    # POPRAWKA 1: Używamy data.values(), żeby iterować po obiektach gier, a nie po kluczach "0", "1"...
    games_list = data.values()

    if colour == "B":
        for game in games_list:
            # Sprawdzamy czy parametry się zgadzają
            if game.get("heuristic_black") == heuristic and game.get("depth_black") == depth:
                total_games += 1
                winner = game.get("winner")
                turns = game.get("turns", 0)

                if winner == "CZARNE":
                    total_wins += 1
                    sum_win_length += turns
                elif winner == "REMIS":
                    total_draws += 1
                    sum_draw_length += turns
                elif winner == "BIALE":
                    total_loses += 1
                    sum_lose_length += turns

    elif colour == "W":
        for game in games_list:
            if game.get("heuristic_white") == heuristic and game.get("depth_white") == depth:
                total_games += 1
                winner = game.get("winner")
                turns = game.get("turns", 0)

                if winner == "BIALE":
                    total_wins += 1
                    sum_win_length += turns
                elif winner == "REMIS":
                    total_draws += 1
                    sum_draw_length += turns
                elif winner == "CZARNE":
                    total_loses += 1
                    sum_lose_length += turns

    # POPRAWKA 2: Zabezpieczenie przed dzieleniem przez zero
    if total_games == 0:
        return [0, 0, 0, 0, 0, 0, 0.0, 0.0, 0.0]

    avg_win_length = sum_win_length / total_wins if total_wins > 0 else 0
    avg_lose_length = sum_lose_length / total_loses if total_loses > 0 else 0
    avg_draw_length = sum_draw_length / total_draws if total_draws > 0 else 0

    win_rate = total_wins / total_games
    lose_rate = total_loses / total_games
    draw_rate = total_draws / total_games

    return [total_wins, total_loses, total_draws, avg_win_length, avg_lose_length, avg_draw_length, win_rate, lose_rate,
            draw_rate]

def do_data_magic():
    H_NAMES = ["random_score", "sum_score", "sum_and_doubling", "doubling_aggresive", "sum_and_backline"]

    for heur in H_NAMES:
        print(f"Data for {heur} :")
        for depth in range(2,5):
            data = scrap_data("W",depth, heur)

            print(f"FOR DEPTH={depth}")
            print(f"FOR COLOR=WHITE")
            print(f"total wins : {data[0]}, loses:{data[1]}, draws : {data[2]}")
            print(f"avg game lenths : wins : {data[3]}, loses : {data[4]}, draws : {data[5]}")
            print(f"rates : wins : {data[6]}, loses : {data[7]}, draws : {data[8]}")
            data = scrap_data("B",depth, heur)
            print("FOR COLOR=BLACK")
            print(f"total wins : {data[0]}, loses:{data[1]}, draws : {data[2]}")
            print(f"avg game lenths : wins : {data[3]}, loses : {data[4]}, draws : {data[5]}")
            print(f"rates : wins : {data[6]}, loses : {data[7]}, draws : {data[8]}")
            print("_______________________________________")

def black_or_white():
    file = open("statistics.json", "r")
    data = json.load(file)
    H_NAMES = ["random_score", "sum_score", "sum_and_doubling", "doubling_aggresive", "sum_and_backline"]


    for H in H_NAMES:
        wins = 0
        loses = 0
        draws = 0
        counter = 0
        for game in data.values():
            if game.get("winner") == "CZARNE" and game.get("heuristic_black") == H:
                wins += 1
            if game.get("winner") == "REMIS" and game.get("heuristic_black") == H or game.get("heuristic_white") == H:
                draws += 1
            if game.get("winner") == "BIALE" and game.get("heuristic_white") == H:
                wins += 1
            if game.get("winner") == "CZARNE" and game.get("heuristic_white") == H:
                loses += 1
            if game.get("winner") == "BIALE" and game.get("heuristic_black") == H:
                loses+=1
            if game.get("heuristic_black") == H or game.get("heuristic_white") == H:
                counter += 1
        print(f"{H} RATES : WINS {wins/counter} LOSES {loses/counter} DRAW {draws/counter}")

if __name__ == "__main__":
    H_NAMES = ["random_score", "sum_score", "sum_and_doubling", "doubling_aggresive", "sum_and_backline"]
    print("start")
    #run_experiment()
    #do_data_magic()
    #print( scrap_data("W",3,H_NAMES[0] ) )
    black_or_white()
    print("done")