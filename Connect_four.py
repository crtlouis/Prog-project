import tkinter as tk
from tkinter import messagebox

#  CONFIG (modern palette) 
ROWS, COLS = 6, 7
CELL = 92
MARGIN = 20

BG        = "#FFFFFF"   # window bg
BOARD     = "#00285c"   # navy board
EMPTY     = "#dfe7ee"   # empty hole fill
RED       = "#ff6b6b"   # player 1 color
YELLOW    = "#ffd166"   # player 2 color
TEXT_DARK = "#20334d"

DROP_PIXELS_PER_STEP = 14      # falling speed (pixels)
DROP_STEP_MS         = 12      # frame delay (ms)
WIN_DELAY_MS         = 2000    # 2 seconds before victory screen

#  PURE BOARD LOGIC 
def new_board():
    """Create an empty Connect Four board."""
    return [[0 for _ in range(COLS)] for _ in range(ROWS)]

def column_has_space(board, col):
    """Check if the selected column still has empty space."""
    return 0 <= col < COLS and board[ROWS-1][col] == 0

def next_open_row(board, col):
    """Return the first available row in a column, starting from the bottom."""
    for r in range(ROWS):
        if board[r][col] == 0:
            return r
    return None

def place_piece(board, r, c, piece):
    """Place a piece on the board."""
    board[r][c] = piece

def winning_cells(board, piece):
    """Check if a player has four in a row. Return winning cells or None."""
    dirs = [(0,1), (1,0), (1,1), (-1,1)]  # →, ↑, ↗, ↖
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] != piece:
                continue
            for dr, dc in dirs:
                cells = [(r + k*dr, c + k*dc) for k in range(4)]
                if all(0 <= rr < ROWS and 0 <= cc < COLS for rr, cc in cells):
                    if all(board[rr][cc] == piece for rr, cc in cells):
                        return cells
    return None

def is_full(board):
    """Return True if the board is completely full."""
    return all(board[ROWS-1][c] != 0 for c in range(COLS))

#  MAIN APP CLASS 
class ConnectFourApp:
    """GUI class that handles visuals, logic, and interaction."""

    def __init__(self, root):
        """Initialize window, board, and UI layout."""
        self.root = root
        self.root.title("Connect Four")
        self.root.configure(bg=BG)

        self.board = new_board()
        self.turn = 1               # 1 = red, 2 = yellow
        self.animating = False
        self.game_over = False

        # Layout setup
        self.top = tk.Frame(root, bg=BG)
        self.top.pack(pady=(16, 8))
        self.center = tk.Frame(root, bg=BG)
        self.center.pack()
        self.bottom = tk.Frame(root, bg=BG)
        self.bottom.pack(pady=14)

        # Title + turn display
        self.title = tk.Label(self.top, text="Connect Four", bg=BG, fg=TEXT_DARK,
                              font=("Segoe UI", 22, "bold"))
        self.title.pack()
        self.turn_var = tk.StringVar()
        self.turn_lbl = tk.Label(self.top, textvariable=self.turn_var, bg=BG, fg=TEXT_DARK,
                                 font=("Segoe UI", 14, "bold"))
        self.turn_lbl.pack(pady=(4, 0))

        # Canvas for board
        self.board_left = MARGIN
        self.board_top  = MARGIN + CELL
        self.board_w    = COLS * CELL
        self.board_h    = ROWS * CELL
        self.canvas_w   = self.board_left + self.board_w + MARGIN
        self.canvas_h   = self.board_top  + self.board_h + MARGIN

        self.canvas = tk.Canvas(self.center, width=self.canvas_w, height=self.canvas_h,
                                bg=BG, highlightthickness=0)
        self.canvas.pack()

        # Restart button
        self.restart_btn = tk.Button(self.bottom, text="Restart",
                                     font=("Segoe UI", 12, "bold"),
                                     bg="#2d6cdf", fg="white",
                                     activebackground="#1f56bd", activeforeground="white",
                                     relief="flat", padx=18, pady=8,
                                     command=self.restart_game)
        self.restart_btn.pack()

        # Bind mouse clicks
        self.canvas.bind("<Button-1>", self.on_click)

        # Initial draw
        self.draw_all()
        self.update_turn_label()

    #  Drawing 
    def cell_rect(self, r, c):
        """Return pixel coordinates for a cell."""
        x1 = self.board_left + c*CELL
        y1 = self.board_top + (ROWS-1-r)*CELL
        return x1, y1, x1+CELL, y1+CELL

    def cell_center(self, r, c):
        """Return the center of a cell."""
        x1, y1, x2, y2 = self.cell_rect(r, c)
        return (x1+x2)/2, (y1+y2)/2

    def draw_all(self):
        """Redraw the entire board and its pieces."""
        self.canvas.delete("all")
        self.canvas.create_rectangle(self.board_left, self.board_top,
                                     self.board_left+self.board_w,
                                     self.board_top+self.board_h,
                                     fill=BOARD, outline=BOARD)
        for r in range(ROWS):
            for c in range(COLS):
                x1, y1, x2, y2 = self.cell_rect(r, c)
                fill = EMPTY
                if self.board[r][c] == 1:
                    fill = RED
                elif self.board[r][c] == 2:
                    fill = YELLOW
                self.canvas.create_oval(x1+10, y1+10, x2-10, y2-10, fill=fill, outline="#0d1c33")

    def update_turn_label(self):
        """Show which player's turn it is."""
        who = "Player 1 (Red)" if self.turn == 1 else "Player 2 (Yellow)"
        self.turn_var.set(f"Turn: {who}")

    #  Player Input 
    def on_click(self, event):
        """Handle player clicks on the board."""
        if self.game_over or self.animating:
            return
        col = int((event.x - self.board_left) // CELL)
        if not column_has_space(self.board, col):
            self.root.bell()
            return
        row = next_open_row(self.board, col)
        if row is None:
            self.root.bell()
            return

        self.animating = True
        color = RED if self.turn == 1 else YELLOW
        self.animate_drop(col, row, color, on_done=lambda: self.after_drop(row, col))

    #  Animation 
    def animate_drop(self, col, row, color, on_done):
        """Animate the falling disc."""
        x = self.board_left + col*CELL + CELL/2
        y = MARGIN + CELL/2
        _, end_y = self.cell_center(row, col)
        rad = CELL*0.37

        temp = self.canvas.create_oval(x-rad, y-rad, x+rad, y+rad, fill=color, outline="#0d1c33")

        def step():
            nonlocal y
            if y < end_y:
                y = min(y + DROP_PIXELS_PER_STEP, end_y)
                self.canvas.coords(temp, x-rad, y-rad, x+rad, y+rad)
                self.root.after(DROP_STEP_MS, step)
            else:
                self.canvas.delete(temp)
                on_done()
        step()

    #  Game Logic 
    def after_drop(self, row, col):
        """Update board after a piece is placed."""
        place_piece(self.board, row, col, self.turn)
        self.draw_all()
        self.animating = False

        cells = winning_cells(self.board, self.turn)
        if cells:
            self.game_over = True
            self.draw_win_line(cells, self.turn)
            self.root.after(WIN_DELAY_MS, lambda: self.show_victory_screen(self.turn))
            return

        if is_full(self.board):
            self.game_over = True
            self.show_victory_screen(0)
            return

        self.turn = 2 if self.turn == 1 else 1
        self.update_turn_label()

    def draw_win_line(self, cells, winner_piece):
        """Draw a colored line through the winning four."""
        (r1, c1), (r4, c4) = cells[0], cells[-1]
        x1, y1 = self.cell_center(r1, c1)
        x4, y4 = self.cell_center(r4, c4)
        color = RED if winner_piece == 1 else YELLOW
        self.canvas.create_line(x1, y1, x4, y4, fill=color, width=12, capstyle="round")

    def show_victory_screen(self, result):
        """Show a message after the game ends."""
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, self.canvas_w, self.canvas_h, fill=BG, outline=BG)

        if result == 1:
            msg, col = "RED PLAYER WINS!", RED
        elif result == 2:
            msg, col = "YELLOW PLAYER WINS!", YELLOW
        else:
            msg, col = "IT'S A DRAW!", TEXT_DARK

        self.canvas.create_text(self.canvas_w/2, self.canvas_h/2 - 20,
                                text=msg, fill=col, font=("Segoe UI", 28, "bold"))

        big_btn = tk.Button(self.center, text="RESTART", font=("Segoe UI", 14, "bold"),
                            bg="#2d6cdf", fg="white", relief="flat",
                            command=self.restart_game)
        big_btn.place(x=self.canvas_w/2 - 70, y=self.canvas_h/2 + 20)
        self._big_restart = big_btn

    def restart_game(self):
        """Restart the game and reset variables."""
        if hasattr(self, "_big_restart") and self._big_restart.winfo_exists():
            self._big_restart.destroy()
        self.board = new_board()
        self.turn = 1
        self.animating = False
        self.game_over = False
        self.draw_all()
        self.update_turn_label()

# RUN 
if __name__ == "__main__":
    root = tk.Tk()
    app = ConnectFourApp(root)
    root.mainloop()
