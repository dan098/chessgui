import pygame
import chess
import chess.engine

# Inizializzazione di Pygame
pygame.init()

# Configurazione della finestra
WIDTH, HEIGHT = 1000, 800
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Scacchi Dan")

# Colori
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (70, 130, 180)

# Font
FONT = pygame.font.Font(None, 28)

# Dimensioni della scacchiera
BOARD_SIZE = 8
SQUARE_SIZE = 80

# Caricamento delle immagini dei pezzi
PIECES = {}
for piece in ['p', 'r', 'n', 'b', 'q', 'k']:
    PIECES[piece] = pygame.transform.scale(pygame.image.load(f"pieces/b{piece}.png"), (SQUARE_SIZE, SQUARE_SIZE))
    PIECES[piece.upper()] = pygame.transform.scale(pygame.image.load(f"pieces/w{piece}.png"), (SQUARE_SIZE, SQUARE_SIZE))

# Inizializzazione della scacchiera
board = chess.Board()

# Inizializzazione del motore Stockfish
engine = chess.engine.SimpleEngine.popen_uci("./stockfish-ubuntu-avx2") # place the stockfish executable path here !!!

def draw_board():
    """
    Funzione: draw_board
    Disegna la scacchiera sulla superficie di gioco

    Parametri formali: Nessuno
    Valore di ritorno: Nessuno
    """
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = WHITE if (row + col) % 2 == 0 else GRAY
            pygame.draw.rect(SCREEN, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    return

def draw_pieces():
    """
    Funzione: draw_pieces
    Disegna i pezzi sulla scacchiera

    Parametri formali: Nessuno
    Valore di ritorno: Nessuno
    """
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            x = chess.square_file(square) * SQUARE_SIZE
            y = (7 - chess.square_rank(square)) * SQUARE_SIZE
            SCREEN.blit(PIECES[piece.symbol()], (x, y))
    return

def get_square_from_pos(pos: tuple) -> chess.Square:
    """
    Funzione: get_square_from_pos
    Converte una posizione del mouse in una casella della scacchiera

    Parametri formali:
    tuple pos -> La posizione del mouse (x, y)

    Valore di ritorno:
    chess.Square -> La casella della scacchiera corrispondente
    """
    x, y = pos
    file = x // SQUARE_SIZE
    rank = 7 - (y // SQUARE_SIZE)
    return chess.square(file, rank)

def get_best_move(difficulty: float) -> chess.engine.PlayResult:
    """
    Funzione: get_best_move
    Ottiene la migliore mossa dal motore di scacchi

    Parametri formali:
    float difficulty -> Il livello di difficoltà (tempo di pensiero per il motore)

    Valore di ritorno:
    chess.engine.PlayResult -> Il risultato dell'analisi del motore
    """
    return engine.play(board, chess.engine.Limit(time=difficulty))

def highlight_legal_moves(square: chess.Square):
    """
    Funzione: highlight_legal_moves
    Evidenzia le mosse legali per un pezzo selezionato dall utente
    estraendole da board.legal_moves se lo square di partenza corrisponde a quello selezionato dall utente

    Parametri formali:
    chess.Square square -> La casella del pezzo selezionato

    Valore di ritorno: Nessuno
    """
    legal_moves = [move for move in board.legal_moves if move.from_square == square]
    for move in legal_moves:
        x = chess.square_file(move.to_square) * SQUARE_SIZE
        y = (7 - chess.square_rank(move.to_square)) * SQUARE_SIZE
        pygame.draw.rect(SCREEN, (0, 255, 0, 128), (x, y, SQUARE_SIZE, SQUARE_SIZE), 4)
    return

def draw_game_ui(player_color: chess.Color, show_hint: bool) -> pygame.Rect:
    """
    Funzione: draw_game_ui
    Disegna l'interfaccia utente del gioco

    Parametri formali:
    chess.Color player_color -> Il colore del giocatore corrente
    bool show_hint -> Indica se mostrare o meno il suggerimento

    Valore di ritorno:
    pygame.Rect -> Il rettangolo del pulsante suggerimento
    """
    draw_board()
    draw_pieces()

    # pannello laterale azzurro
    pygame.draw.rect(SCREEN, LIGHT_BLUE, (BOARD_SIZE * SQUARE_SIZE, 0, WIDTH - BOARD_SIZE * SQUARE_SIZE, HEIGHT))
    # mostra turno
    turn_text = FONT.render(f"Turno: {'Bianco' if board.turn == chess.WHITE else 'Nero'}", True, BLACK)
    SCREEN.blit(turn_text, (BOARD_SIZE * SQUARE_SIZE + 20, 20))
    # stampa cronologia mosse
    move_history = FONT.render("Cronologia mosse:", True, BLACK)
    SCREEN.blit(move_history, (BOARD_SIZE * SQUARE_SIZE + 20, 60))
    # creo una copia di Board per riprodurre le mosse evitando errori
    temp_board = chess.Board()
    moves_surface = pygame.Surface((WIDTH - BOARD_SIZE * SQUARE_SIZE - 40, HEIGHT - 200))
    moves_surface.fill(LIGHT_BLUE)
    for i, move in enumerate(board.move_stack):
        try:
            move_san = temp_board.san(move)
            temp_board.push(move)
            move_text = FONT.render(f"{i//2 + 1}. {move_san}", True, BLACK)
            moves_surface.blit(move_text, (0, i * 30))
        except AssertionError: # mossa non valida
            move_text = FONT.render(f"{i//2 + 1}. {move.uci()}", True, BLACK)
            moves_surface.blit(move_text, (0, i * 30))

    SCREEN.blit(moves_surface, (BOARD_SIZE * SQUARE_SIZE + 20, 100))
    # pulsante per suggerimenti
    hint_button = pygame.Rect(BOARD_SIZE * SQUARE_SIZE + 20, HEIGHT - 60, 200, 40)
    pygame.draw.rect(SCREEN, DARK_BLUE, hint_button)
    hint_text = FONT.render("Suggerimento", True, WHITE)
    SCREEN.blit(hint_text, (hint_button.centerx - hint_text.get_width() // 2, hint_button.centery - hint_text.get_height() // 2))

    return hint_button


def show_winner(result: str):
    """
    Funzione: show_winner
    Mostra il risultato della partita

    Parametri formali:
    str result -> Il risultato della partita

    Valore di ritorno: Nessuno
    """
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    SCREEN.blit(overlay, (0, 0))

    if result == "1-0":
        winner_text = "Il Bianco ha vinto!"
    elif result == "0-1":
        winner_text = "Il Nero ha vinto!"
    else:
        winner_text = "Partita patta!"

    text = FONT.render(winner_text, True, WHITE)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    SCREEN.blit(text, text_rect)

    pygame.display.flip()
    pygame.time.wait(5000)  # Mostra il risultato per 5 secondi
    return

def draw_menu() -> list:
    """
    Funzione: draw_menu
    Disegna il menu principale del gioco

    Parametri formali: Nessuno

    Valore di ritorno:
    list -> Lista di tuple contenenti il testo del pulsante e la sua posizione
    """
    SCREEN.fill(LIGHT_BLUE)
    title = FONT.render("Menu Principale", True, BLACK)
    SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

    buttons = [
        ("Giocatore vs Giocatore", (WIDTH // 2 - 150, 200)),
        ("Giocatore vs Computer", (WIDTH // 2 - 150, 300))
    ]

    for text, pos in buttons:
        pygame.draw.rect(SCREEN, DARK_BLUE, (pos[0], pos[1], 300, 50))
        button_text = FONT.render(text, True, WHITE)
        SCREEN.blit(button_text, (pos[0] + 150 - button_text.get_width() // 2, pos[1] + 25 - button_text.get_height() // 2))

    return buttons

def draw_difficulty_menu() -> list:
    """
    Funzione: draw_difficulty_menu
    Disegna il menu per la selezione della difficoltà

    Parametri formali: Nessuno

    Valore di ritorno:
    list -> Lista di tuple contenenti il testo del pulsante e la sua posizione
    """
    SCREEN.fill(LIGHT_BLUE)
    title = FONT.render("Seleziona la difficoltà", True, BLACK)
    SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

    buttons = [
        ("Facile", (WIDTH // 2 - 150, 200)),
        ("Medio", (WIDTH // 2 - 150, 300)),
        ("Difficile", (WIDTH // 2 - 150, 400))
    ]

    for text, pos in buttons:
        pygame.draw.rect(SCREEN, DARK_BLUE, (pos[0], pos[1], 300, 50))
        button_text = FONT.render(text, True, WHITE)
        SCREEN.blit(button_text, (pos[0] + 150 - button_text.get_width() // 2, pos[1] + 25 - button_text.get_height() // 2))

    return buttons

def main():
    """
    Funzione: main
    Funzione principale del gioco

    Parametri formali: Nessuno
    Valore di ritorno: Nessuno
    """
    game_mode = None
    difficulty = None
    selected_square = None
    player_color = None
    show_hint = False

    while True:
        if game_mode is None: # seleziono modalita di gioco
            buttons = draw_menu()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for text, pos in buttons:
                        if pygame.Rect(pos[0], pos[1], 300, 50).collidepoint(event.pos):
                            if text == "Giocatore vs Giocatore":
                                game_mode = "pvp"
                                player_color = chess.WHITE
                            elif text == "Giocatore vs Computer":
                                game_mode = "pvc"
        elif game_mode == "pvc" and player_color is None: # contro computer
            SCREEN.fill(LIGHT_BLUE) # ricreo la schermata per selezionare colore se player_color == None
            title = FONT.render("Scegli il tuo colore", True, BLACK)
            SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

            white_button = pygame.Rect(WIDTH // 2 - 150, 200, 300, 50)
            black_button = pygame.Rect(WIDTH // 2 - 150, 300, 300, 50)

            pygame.draw.rect(SCREEN, DARK_BLUE, white_button)
            pygame.draw.rect(SCREEN, DARK_BLUE, black_button)

            white_text = FONT.render("Gioca con il Bianco", True, WHITE)
            black_text = FONT.render("Gioca con il Nero", True, WHITE)

            SCREEN.blit(white_text, (white_button.centerx - white_text.get_width() // 2, white_button.centery - white_text.get_height() // 2))
            SCREEN.blit(black_text, (black_button.centerx - black_text.get_width() // 2, black_button.centery - black_text.get_height() // 2))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if white_button.collidepoint(event.pos):
                        player_color = chess.WHITE
                    elif black_button.collidepoint(event.pos):
                        player_color = chess.BLACK
        elif game_mode == "pvc" and difficulty is None:
            buttons = draw_difficulty_menu() # seleziono difficolta' computer
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for text, pos in buttons:
                        if pygame.Rect(pos[0], pos[1], 300, 50).collidepoint(event.pos):
                            if text == "Facile":
                                difficulty = 0.1 # da adeguare alle prestazioni della macchina
                            elif text == "Medio":
                                difficulty = 0.5
                            elif text == "Difficile":
                                difficulty = 1.0
        else: # la partita puo' iniziare (sia pvp che pvc gestiti qua)
            hint_button = draw_game_ui(player_color, show_hint) 
            for event in pygame.event.get():
                if event.type == pygame.QUIT: # Chiusura gioco
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Click sinistro
                        pos = pygame.mouse.get_pos()
                        if pos[0] < BOARD_SIZE * SQUARE_SIZE:
                            square = get_square_from_pos(pos)
                            if selected_square is None: 
                                # Controllo se puo' selezionare quel pezzo
                                if board.color_at(square) == player_color or game_mode == "pvp":
                                    selected_square = square
                            else:
                                move = chess.Move(selected_square, square)
                                if move in board.legal_moves:
                                    board.push(move) # aggiorno la scacchiera
                                    selected_square = None
                                    if game_mode == "pvp":
                                        player_color = not player_color
                                else:
                                    selected_square = None
                        elif hint_button.collidepoint(pos): 
                            # attivo/disattivo suggerimenti se click sul bottone
                            show_hint = not show_hint

            if selected_square is not None: 
                # Mostro mosse giocabili per il pezzo selezionato
                highlight_legal_moves(selected_square)

            if show_hint:
                if game_mode == "pvc":
                    best_move = get_best_move(difficulty).move
                else:
                    # In modalità pvp, usiamo un tempo fisso per il suggerimento (0.1)
                    best_move = get_best_move(0.1).move
                x1 = chess.square_file(best_move.from_square) * SQUARE_SIZE
                y1 = (7 - chess.square_rank(best_move.from_square)) * SQUARE_SIZE
                x2 = chess.square_file(best_move.to_square) * SQUARE_SIZE
                y2 = (7 - chess.square_rank(best_move.to_square)) * SQUARE_SIZE
                pygame.draw.line( # linea rossa di suggerimento della mossa migliore
                    SCREEN, 
                    (255, 0, 0), 
                    (x1 + SQUARE_SIZE // 2, y1 + SQUARE_SIZE // 2), # Partenza = coordinate quadrato + mezzo square_size per centrarlo 
                    (x2 + SQUARE_SIZE // 2, y2 + SQUARE_SIZE // 2), # Arrivo
                    5 # spessore linea
                )

            if board.is_game_over():
                # Mostra il risultato della partita e resetto la scacchiera
                result = board.result()
                show_winner(result)
                game_mode = None
                player_color = None
                difficulty = None
                board.reset()

            if game_mode == "pvc" and board.turn != player_color:
                # Mossa dell engine in pvc mode
                computer_move = get_best_move(difficulty).move 
                board.push(computer_move)

        pygame.display.flip() # Aggiorna la finestra di gioco

if __name__ == "__main__":
    main()
    engine.quit()
    pygame.quit()