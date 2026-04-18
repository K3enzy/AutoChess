from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import time
import chess
import chess.pgn
import io
import requests
import keyboard
import threading
#from collections import defaultdict

url ="https://www.chess.com/login_and_go?returnUrl=https://www.chess.com/"
webdriver_path = r"D:\Selenium\chromedriver-win64\chromedriver-win64\chromedriver.exe"
path = r"D:\CodeProject\Python\Made\Chess\Chess-com-Keyboard-Chrome-Web-Store"
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--log-level=off")
options.add_argument("--enable-unsafe-extension-debugging")
options.add_argument("--remote-debugging-pipe")
options.add_argument('--ignore-certificate-errors')
options.add_experimental_option("detach", True)
options.enable_webextensions = True
options.enable_bidi = True
driver_service = Service(executable_path=webdriver_path,log_output='NUL')
driver = webdriver.Chrome(options=options,service=driver_service)
driver.webextension.install(path)
driver.get(url)
wait = WebDriverWait(driver, 15)

username="mejox68384@ckuer.com"
password="h2zJCuFv6H%P6Ws"
try:
    wait.until(EC.presence_of_element_located((By.ID, "login-username")))
    driver.find_element(By.ID,"login-username").send_keys(username)
    driver.find_element(By.ID,"login-password").send_keys(password)
    driver.find_element(By.ID,"login").send_keys(Keys.ENTER)
except:
    print("Login page failed to load.")
    driver.quit()
def listen_for_quit():
    keyboard.wait('ctrl+q')
    print("Hotkey pressed! Quitting...")
    driver.quit() 
hotkey_thread = threading.Thread(target=listen_for_quit, daemon=True)
hotkey_thread.start()
def best_move(game_fen):
    while True:
        try:
            # Define the endpoint and parameters
            endpoint = "https://stockfish.online/api/s/v2.php"
            fen = game_fen 
            depth = 9  # Example depth (any value <16)

            # Create the parameters dictionary
            params = {
                "fen": fen,
                "depth": depth
            }
            response = requests.get(endpoint, params=params)    
            if response.status_code == 200:
                all_response= response.json()
                fourth_value=all_response.get(list(all_response.keys())[3],"")
                split_value = fourth_value.split(" ")
                best=split_value[1]
                #if play_move(best):
                    #best=ponder(fen)
                    #board.push_san(best)
                    #current_fen = board.fen()[:-6]
                    #fen_count[current_fen] += 1
                return best

            else:
                print("Error:", response.status_code)
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
        finally:
            if 'response' in locals():
                del response # pyright: ignore[reportPossiblyUnboundVariable]
def pgntofen(pgn):
    pgn_file = io.StringIO(pgn)
    # Create a PGN_game game object from the string
    pgn_game = chess.pgn.read_game(pgn_file)

    # Create a board object from the PGN_game
    board = pgn_game.end().board()  # type: ignore # Get the final board position

    # Get the FEN for the current position
    fen = board.fen()

    # Return the FEN string
    return fen
def extract_piece_icon(div_element):
    while True:
        try:
            # Check if there's a piece icon
            piece_icons = {
                "knight-white": "N",
                "bishop-white": "B",
                "rook-white": "R",
                "queen-white": "Q",
                "king-white": "K",
                "knight-black": "N",
                "bishop-black": "B",
                "rook-black": "R",
                "queen-black": "Q",
                "king-black": "K"
            }

            # Search for any known piece icon within the move div
            for icon_class, piece_notation in piece_icons.items():
                piece_icon = div_element.find_elements(By.CLASS_NAME, icon_class)
                if piece_icon:
                    return piece_notation
            return ""
        except Exception as e:
            print(f"Error extracting piece icon: {e}")
def extract_moves():
    try:
        if draw_denied:
            draw()
        # Find all rows that contain moves
        move_rows = driver.find_elements(By.CLASS_NAME, "main-line-row")

        moves = []
        for row in move_rows:
            try:
                white_move_div = row.find_element(By.CSS_SELECTOR, "div.white-move span")
                white_move = white_move_div.text.strip()

                # Check for special piece icons and prepend the piece notation if found
                piece_icon = extract_piece_icon(white_move_div)
                if piece_icon:
                    white_move = piece_icon + white_move

                moves.append(white_move)
            except Exception as e:
                pass

            try:
                black_move_div = row.find_element(By.CSS_SELECTOR, "div.black-move span")
                black_move = black_move_div.text.strip()

                # Check for special piece icons and prepend the piece notation if found
                piece_icon = extract_piece_icon(black_move_div)
                if piece_icon:
                    black_move = piece_icon + black_move

                moves.append(black_move)
            except Exception as e:
                pass
        return moves
    except Exception as e:
        print(f"Error extracting moves: {e}")
        return []
def enter_move(best_move):
        global move_input
        try:
            if move_input is None:
                move_input = wait.until(
                    EC.presence_of_element_located((By.ID, "ccHelper-input"))
                )
            move_input.send_keys(best_move)
            move_input.send_keys(Keys.ENTER)
        except Exception as e:
            # Handle stale element case, find the element again if necessary
            if isinstance(e, StaleElementReferenceException):
                try:
                    # Re-locate the input field if it became stale
                    move_input_element = wait.until(
                        EC.presence_of_element_located((By.ID, "ccHelper-input"))
                    )
                    move_input_element.send_keys(best_move)
                    move_input_element.send_keys(Keys.ENTER)
                except Exception as e:
                    print(f"Error re-locating input field after stale element: {e}")
            else:
                print(f"Error interacting with input fields: {e}")
def is_white(driver):
    try:
        wait = WebDriverWait(driver, 10)
        corner_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'svg text[x="10"][y="99"]'))
        )
        corner_letter=corner_element.text
        if corner_letter=="a":
            return True
        elif corner_letter=="h":
            return False
    except Exception as e:
        print(f"Error in is_white function: {e}")
        return None
def is_game_ongoing():
    global status
    try:
        initial_element= driver.find_element(By.XPATH, '//*[@id="board-layout-player-bottom"]/div[2]/span')
        initial_time=initial_element.text
        time.sleep(0.5)
        after_element= driver.find_element(By.XPATH, '//*[@id="board-layout-player-bottom"]/div[2]/span')
        after_time=after_element.text

        if initial_time != after_time:
            clear_enter()
            status= True
            return True
        else:
            status= False
            return False  # The rotation hasn't changed, meaning the game might be paused
    except Exception as e:
        status = False
def white_turn(driver):
    try:
        wait = WebDriverWait(driver, 10)
        first_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div class="move-time-content move-time-monospace"'))
        )
        first_timer=first_element.text
        second_timer=first_timer.copy() # pyright: ignore[reportAttributeAccessIssue]
        if first_timer!=second_timer:
            return True
    except Exception as e:
        print(f"Error in is_white function: {e}")
        return None
def process_moves(current_moves):
    global previous, PGN_game, num, status, current, first_move, board, fen_count
    if game_over():
        if is_white(driver) and len(current_moves)!=0 and  "#" in current_moves[-1]:
            PGN_game += f"{num}. {current[-1]} "
            print(PGN_game)
        status = False
        num = 1
        previous = []
        current = []
        PGN_game = ""
        first_move = True
        #board=chess.Board()
        #fen_count.clear()
        print("Game over. Resetting variables...")
        return
    # If there's a mismatch in the number of moves (i.e., both white and black are played at once)
    if len(current_moves) - len(previous) == 2:
        white_move = current_moves[-2]
        black_move = current_moves[-1]
    
        PGN_game += f"{num}. {white_move} {black_move} "
        
        fen = pgntofen(PGN_game)

        num += 1
        # Handle best move suggestion if needed
        if is_white(driver):
            #board.push_san(black_move)
            #current_fen = board.fen()[:-6]
            #fen_count[current_fen] += 1
            best_moves=best_move(fen)
            print(f"Best Move(White2): {best_moves}")
            enter_move(best_moves)
    elif len(current_moves) % 2 == 1:
        white_move = current_moves[-1]
        PGN_game += f"{num}. {white_move} "
        fen = pgntofen(PGN_game)
        if is_white(driver)==False:
            #board.push_san(white_move)
            #current_fen = board.fen()[:-6]  
            #fen_count[current_fen] += 1
            best_moves=best_move(fen)
            print("Best Move(Black): " + best_moves)
            enter_move(best_moves)
    elif len(current_moves) % 2 == 0 and len(current_moves)!=0:
        black_move = current_moves[-1]
        PGN_game += f"{black_move} "
        fen = pgntofen(PGN_game)
        num += 1
        if is_white(driver):
            #board.push_san(black_move)
            #current_fen = board.fen()[:-6]  
            #fen_count[current_fen] += 1
            best_moves=best_move(fen)
            print("Best Move(White): " + best_moves)
            enter_move(best_moves)
    previous = current.copy()
def game_over():
    try:
        game_result= driver.find_element(By.CLASS_NAME, 'game-result')
        result = game_result.text
        if result:
            print(f"Game result detected: {result}")
            return True
    except NoSuchElementException:
        return False
def new_game():     
    try:
        if not is_game_ongoing():
            driver.find_element(By.XPATH, "//*[@id='board-layout-chessboard']/div[4]/div/div/div/div[3]/div/button[1]").click()
            WebDriverWait(driver, 30).until(lambda driver: is_game_ongoing())
            print("Successfully started a new game.")
            return
    except Exception:
        return
def clear_enter():
    try:
        move_input = wait.until(
        EC.presence_of_element_located((By.ID, "ccHelper-input"))
        )
        move_input.clear()
        return
    except Exception as e:
                print(f"Error interacting with input fields: {e}")
def draw():
    global draw_denied
    try:
        driver.find_element(By.XPATH, '//*[@id="live-game-tab-scroll-container"]/div[2]/a').click()
        print("Successfully Decline Draw.")
        draw_denied=False
    except Exception:
        return
def check_threefold_repetition(board, fen_count):
    current_fen = board.fen()[:-6]  
    fen_count[current_fen] += 1
    if fen_count[current_fen] == 3:
        fen_count[current_fen]-=1
        return True
    return False
def play_move(move):
    board.push_san(move) # pyright: ignore[reportUnboundVariable, reportAttributeAccessIssue]
    if check_threefold_repetition(board, fen_count): # type: ignore
        print("Threefold repetition is imminent!")
        board.pop() # type: ignore
        return True
    else:
        return False
def ponder(ponder_fen):
    while True:
        try:
            # Define the endpoint and parameters
            endpoint = "https://stockfish.online/api/s/v2.php"
            fen = ponder_fen 
            depth = 14  # Example depth (any value <16)

            # Create the parameters dictionary
            params = {
                "fen": fen,
                "depth": depth
            }
            response = requests.get(endpoint, params=params)    
            if response.status_code == 200:
                all_response= response.json() 
                fourth_value=all_response.get(list(all_response.keys())[3],"")
                split_value = fourth_value.split(" ")
                best=split_value[1]
                return best

            else:
                print("Error:", response.status_code)
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
        finally:
            if 'response' in locals():
                del response # type: ignore

#board = chess.Board()
#fen_count = defaultdict(int)
draw_denied=True
move_input=None
num = 1
PGN_game = ""
previous = []
current = []
status = False
first_move=True

while True:
    if not status:
        is_game_ongoing()
        if game_over():
            new_game()
    elif status:
        if is_white(driver):
            if first_move:
                enter_move("e2e4")
                #board.push_san("e2e4")
                #current_fen = board.fen()[:-6]  
                #fen_count[current_fen] += 1
                first_move=False
        current = extract_moves()
        if game_over():
            process_moves(current)
            new_game()
            time.sleep(1)
            if not is_game_ongoing():
                new_game()
        if current != previous:
            process_moves(current)
    time.sleep(0.1)