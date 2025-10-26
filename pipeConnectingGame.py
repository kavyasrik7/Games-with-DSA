import tkinter as tk
from tkinter import messagebox
import random
from collections import deque


GRID_SIZE = 8
TILE_SIZE = 60
PIPE_WIDTH = 10
CANVAS_WIDTH = GRID_SIZE * TILE_SIZE
CANVAS_HEIGHT = GRID_SIZE * TILE_SIZE

BG_COLOR = "#2c3e50"
GRID_COLOR = "#34495e"
PIPE_COLOR = "#ecf0f1"
WATER_COLOR = "#3498db"


PIPE_TYPES = {
    'straight': ['N', 'S'],
    'corner': ['N', 'E']
}

DIRECTIONS = {'N': (-1, 0), 'E': (0, 1), 'S': (1, 0), 'W': (0, -1)}
OPPOSITE = {'N': 'S', 'E': 'W', 'S': 'N', 'W': 'E'}

class PipeDream:
    def __init__(self, root):
        self.root = root
        self.root.title("Pipe Dream")
        self.root.configure(bg=BG_COLOR)


        self.canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(pady=10, padx=10)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        control_frame = tk.Frame(root, bg=BG_COLOR)
        control_frame.pack(pady=10)
        
        self.new_game_button = tk.Button(control_frame, text="New Game", command=self.new_game)
        self.new_game_button.pack(side="left", padx=10)

        self.start_flow_button = tk.Button(control_frame, text="Start Flow", command=self.start_flow)
        self.start_flow_button.pack(side="left", padx=10)

        self.status_label = tk.Label(root, text="Click a pipe to rotate it. Connect start to end!", bg=BG_COLOR, fg="white", font=("Arial", 12))
        self.status_label.pack(pady=5)
        
        self.new_game()

    def new_game(self):
        """Sets up a new, solvable game board."""
        self.game_over = False
        self.status_label.config(text="Connect the start (S) to the end (E)!")
        self.generate_solvable_board()
        self.draw_board()

    def generate_solvable_board(self):
        """Generates a board with a guaranteed path from start to end."""
        self.board = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
      
        self.start_pos = (random.randint(0, GRID_SIZE-1), 0)
        self.end_pos = (random.randint(0, GRID_SIZE-1), GRID_SIZE-1)
        self.board[self.start_pos[0]][self.start_pos[1]] = {'type': 'start', 'rotation': 1}
        self.board[self.end_pos[0]][self.end_pos[1]] = {'type': 'end', 'rotation': 3} 

      
        path = self._find_path(self.start_pos, self.end_pos)
        
        
        for i in range(len(path) - 1):
            curr_pos = path[i]
            next_pos = path[i+1]
            
        
            if curr_pos == self.start_pos or self.board[curr_pos[0]][curr_pos[1]] is not None:
                continue

            prev_pos = path[i-1]
            dr1, dc1 = prev_pos[0] - curr_pos[0], prev_pos[1] - curr_pos[1] 
            dr2, dc2 = next_pos[0] - curr_pos[0], next_pos[1] - curr_pos[1] 
            
           
            if abs(dr1 + dr2) == 0 and abs(dc1 + dc2) == 0:
                pipe_type = 'straight'
                rotation = 0 if dr1 != 0 else 1 
            else: 
                pipe_type = 'corner'
               
                dirs = {(dr1, dc1), (dr2, dc2)}
                if dirs == {(-1,0), (0,1)}: rotation = 0 
                elif dirs == {(0,1), (1,0)}: rotation = 1
                elif dirs == {(1,0), (0,-1)}: rotation = 2 
                else: rotation = 3 

            self.board[curr_pos[0]][curr_pos[1]] = {'type': pipe_type, 'rotation': rotation, 'solution_rotation': rotation}

       
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.board[r][c] is None:
                    pipe_type = random.choice(list(PIPE_TYPES.keys()))
                    self.board[r][c] = {'type': pipe_type, 'rotation': random.randint(0, 3)}

        for r, c in path:
            if (r,c) != self.start_pos and (r,c) != self.end_pos:
                self.board[r][c]['rotation'] = random.randint(0, 3)

    def _find_path(self, start, end):
        """Simple random walk to generate a path."""
        path = [start]
        curr = start
        while curr != end:
            r, c = curr
            possible_moves = []
           
            if end[1] > c: possible_moves.extend([(r, c + 1)]*3) 
            if end[1] < c: possible_moves.extend([(r, c - 1)]*3) 
            if end[0] > r: possible_moves.extend([(r + 1, c)]*3) 
            if end[0] < r: possible_moves.extend([(r - 1, c)]*3) 
            
          
            if r > 0: possible_moves.append((r-1,c))
            if r < GRID_SIZE-1: possible_moves.append((r+1,c))
            if c > 0: possible_moves.append((r,c-1))
            if c < GRID_SIZE-1: possible_moves.append((r,c+1))

            next_move = random.choice(possible_moves)
            if next_move not in path:
                path.append(next_move)
                curr = next_move
        return path


    def draw_board(self):
        """Draws the entire grid of pipes on the canvas."""
        self.canvas.delete("all")
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
               
                self.canvas.create_rectangle(c * TILE_SIZE, r * TILE_SIZE, (c + 1) * TILE_SIZE, (r + 1) * TILE_SIZE, outline=GRID_COLOR, width=2)
                
                pipe = self.board[r][c]
                if pipe:
                    self.draw_pipe(r, c, pipe, PIPE_COLOR)

    def draw_pipe(self, r, c, pipe, color):
        """Draws a single pipe piece on the canvas."""
        cx, cy = c * TILE_SIZE + TILE_SIZE / 2, r * TILE_SIZE + TILE_SIZE / 2
        
        if pipe['type'] == 'start':
            self.canvas.create_text(cx, cy, text="S", font=("Arial", 24, "bold"), fill=color)
            self.canvas.create_line(cx, cy, cx + TILE_SIZE/2, cy, width=PIPE_WIDTH, fill=color)
            return
        if pipe['type'] == 'end':
            self.canvas.create_text(cx, cy, text="E", font=("Arial", 24, "bold"), fill=color)
            self.canvas.create_line(cx - TILE_SIZE/2, cy, cx, cy, width=PIPE_WIDTH, fill=color)
            return

        connections = self.get_connections(pipe)
        
        if len(connections) > 0:
             self.canvas.create_oval(cx-PIPE_WIDTH, cy-PIPE_WIDTH, cx+PIPE_WIDTH, cy+PIPE_WIDTH, fill=color, outline="")

        for direction in connections:
            if direction == 'N':
                self.canvas.create_line(cx, cy, cx, cy - TILE_SIZE / 2, width=PIPE_WIDTH, fill=color)
            elif direction == 'S':
                self.canvas.create_line(cx, cy, cx, cy + TILE_SIZE / 2, width=PIPE_WIDTH, fill=color)
            elif direction == 'E':
                self.canvas.create_line(cx, cy, cx + TILE_SIZE / 2, cy, width=PIPE_WIDTH, fill=color)
            elif direction == 'W':
                self.canvas.create_line(cx, cy, cx - TILE_SIZE / 2, cy, width=PIPE_WIDTH, fill=color)

    def on_canvas_click(self, event):
        """Handles player clicks to rotate pipes."""
        if self.game_over:
            return
            
        c = event.x // TILE_SIZE
        r = event.y // TILE_SIZE
        
        pipe = self.board[r][c]
        if pipe and pipe['type'] not in ['start', 'end']:
            pipe['rotation'] = (pipe['rotation'] + 1) % 4
           
            self.canvas.create_rectangle(c * TILE_SIZE, r * TILE_SIZE, (c + 1) * TILE_SIZE, (r + 1) * TILE_SIZE, fill=BG_COLOR, outline=GRID_COLOR, width=2)
            self.draw_pipe(r, c, pipe, PIPE_COLOR)

    def get_connections(self, pipe):
        """Gets the absolute connection directions (N,E,S,W) for a pipe given its rotation."""
        if pipe['type'] not in PIPE_TYPES:
            if pipe['type'] == 'start': return ['E']
            if pipe['type'] == 'end': return ['W']
            return []
            
        base_connections = PIPE_TYPES[pipe['type']]
        rotated_connections = []
        all_dirs = ['N', 'E', 'S', 'W']
        for conn in base_connections:
            current_index = all_dirs.index(conn)
            new_index = (current_index + pipe['rotation']) % 4
            rotated_connections.append(all_dirs[new_index])
        return rotated_connections

    def start_flow(self):
        """Checks for a valid path and starts the flow animation if successful."""
        if self.game_over:
            return
            
        self.game_over = True
        path = self.find_solution_path()
        if path:
            self.status_label.config(text="Connected! Water is flowing...")
            self.animate_flow(path)
        else:
            self.status_label.config(text="Leak! The pipes are not connected.")
            messagebox.showinfo("Pipe Dream", "Leak! The pipes don't connect to the end.")
            self.game_over = False 

    def find_solution_path(self):
        """Uses Breadth-First Search to find a path from start to end."""
        q = deque([(self.start_pos, [self.start_pos])])
        visited = {self.start_pos}

        while q:
            (r, c), path = q.popleft()

            if (r, c) == self.end_pos:
                return path

            pipe = self.board[r][c]
            connections = self.get_connections(pipe)

            for direction in connections:
                dr, dc = DIRECTIONS[direction]
                nr, nc = r + dr, c + dc

                if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and (nr, nc) not in visited:
                    neighbor_pipe = self.board[nr][nc]
                    if neighbor_pipe:
                        neighbor_connections = self.get_connections(neighbor_pipe)
                       
                        if OPPOSITE[direction] in neighbor_connections:
                            visited.add((nr, nc))
                            new_path = path + [(nr, nc)]
                            q.append(((nr, nc), new_path))
        return None

    def animate_flow(self, path, index=0):
        """Animates the water flowing through the connected path."""
        if index >= len(path):
            self.status_label.config(text="You Win! Congratulations!")
            messagebox.showinfo("Pipe Dream", "You Win! The water reached the end.")
            return

        r, c = path[index]
        self.draw_pipe(r, c, self.board[r][c], WATER_COLOR)
        
        self.root.after(100, self.animate_flow, path, index + 1)


if __name__ == "__main__":
    root = tk.Tk()
    app = PipeDream(root)
    root.mainloop()
