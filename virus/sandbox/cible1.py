#!/usr/bin/env python3
"""
Snake automatique — l'IA joue toute seule.
Algorithme : BFS vers la pomme + repli sur la queue si pas de chemin sûr.
Interface : Tkinter (aucune dépendance externe).
"""

import tkinter as tk
import random
from collections import deque

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

CELL        = 20          # taille d'une case en pixels
COLS        = 30          # nombre de colonnes
ROWS        = 30          # nombre de lignes
SPEED_MS    = 60          # délai entre deux frames (ms)
BG_COLOR    = "#111111"
GRID_COLOR  = "#1e1e1e"
SNAKE_HEAD  = "#00e676"
SNAKE_BODY  = "#00a152"
FOOD_COLOR  = "#ff5252"

DIRECTIONS = {
    "UP":    (0, -1),
    "DOWN":  (0,  1),
    "LEFT":  (-1, 0),
    "RIGHT": (1,  0),
}

# ─────────────────────────────────────────────────────────────────────────────
# LOGIQUE DU JEU
# ─────────────────────────────────────────────────────────────────────────────

class SnakeGame:
    def __init__(self, cols: int, rows: int):
        self.cols = cols
        self.rows = rows
        self.reset()

    def reset(self) -> None:
        cx, cy = self.cols // 2, self.rows // 2
        self.snake = deque([(cx, cy), (cx - 1, cy), (cx - 2, cy)])
        self.direction = "RIGHT"
        self.score = 0
        self.game_over = False
        self.food = self._spawn_food()

    def _spawn_food(self) -> tuple[int, int]:
        empty = [(x, y) for x in range(self.cols) for y in range(self.rows)
                 if (x, y) not in self.snake]
        return random.choice(empty) if empty else (0, 0)

    def step(self, direction: str) -> None:
        if self.game_over:
            return
        dx, dy = DIRECTIONS[direction]
        hx, hy = self.snake[0]
        new_head = (hx + dx, hy + dy)

        # collision murs
        if not (0 <= new_head[0] < self.cols and 0 <= new_head[1] < self.rows):
            self.game_over = True
            return

        # collision corps (la queue va bouger, sauf si on mange)
        body = set(self.snake)
        if new_head != self.food:
            body.discard(self.snake[-1])
        if new_head in body:
            self.game_over = True
            return

        self.snake.appendleft(new_head)
        self.direction = direction

        if new_head == self.food:
            self.score += 1
            self.food = self._spawn_food()
        else:
            self.snake.pop()

    # ─── IA ─────────────────────────────────────────────────────────────────

    def _neighbors(self, pos, blocked):
        x, y = pos
        for dx, dy in DIRECTIONS.values():
            nxt = (x + dx, y + dy)
            if 0 <= nxt[0] < self.cols and 0 <= nxt[1] < self.rows and nxt not in blocked:
                yield nxt

    def _bfs(self, start, goal, blocked):
        """Retourne le premier pas vers goal, ou None."""
        if start == goal:
            return None
        queue = deque([start])
        parent = {start: None}
        while queue:
            cur = queue.popleft()
            for nxt in self._neighbors(cur, blocked):
                if nxt in parent:
                    continue
                parent[nxt] = cur
                if nxt == goal:
                    # reconstruire le chemin
                    path = []
                    node = nxt
                    while node is not None:
                        path.append(node)
                        node = parent[node]
                    path.reverse()
                    return path[1] if len(path) > 1 else None
                queue.append(nxt)
        return None

    def _direction_between(self, a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        for name, (ddx, ddy) in DIRECTIONS.items():
            if (ddx, ddy) == (dx, dy):
                return name
        return None

    def _safe_move(self, head, blocked):
        """Choisit un coup qui laisse une issue vers la queue."""
        tail = self.snake[-1]
        for name, (dx, dy) in DIRECTIONS.items():
            nxt = (head[0] + dx, head[1] + dy)
            if not (0 <= nxt[0] < self.cols and 0 <= nxt[1] < self.rows):
                continue
            if nxt in blocked:
                continue
            # simule : après ce coup, peut-on encore atteindre la queue ?
            new_blocked = set(blocked)
            new_blocked.discard(tail)
            new_blocked.add(head)
            if self._bfs(nxt, tail, new_blocked) is not None:
                return name
        # dernier recours : n'importe quel coup libre
        for name, (dx, dy) in DIRECTIONS.items():
            nxt = (head[0] + dx, head[1] + dy)
            if (0 <= nxt[0] < self.cols and 0 <= nxt[1] < self.rows
                    and nxt not in blocked):
                return name
        return None

    def ai_decide(self) -> str:
        """Décide de la prochaine direction."""
        head = self.snake[0]
        # corps bloquant (sauf la queue qui va bouger)
        blocked = set(self.snake)
        blocked.discard(self.snake[-1])

        # 1) essayer d'aller vers la pomme
        if self.food not in blocked:
            nxt = self._bfs(head, self.food, blocked)
            if nxt is not None:
                d = self._direction_between(head, nxt)
                if d is not None:
                    return d

        # 2) sinon, suivre sa queue (survie)
        tail = self.snake[-1]
        nxt = self._bfs(head, tail, blocked)
        if nxt is not None:
            d = self._direction_between(head, nxt)
            if d is not None:
                return d

        # 3) sinon, coup sûr
        safe = self._safe_move(head, set(self.snake))
        if safe is not None:
            return safe

        # 4) sinon, on tente n'importe quoi (peut mourir)
        for name, (dx, dy) in DIRECTIONS.items():
            nxt = (head[0] + dx, head[1] + dy)
            if (0 <= nxt[0] < self.cols and 0 <= nxt[1] < self.rows
                    and nxt not in self.snake):
                return name
        return self.direction


# ─────────────────────────────────────────────────────────────────────────────
# INTERFACE TKINTER
# ─────────────────────────────────────────────────────────────────────────────

class SnakeApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Snake automatique")
        self.root.resizable(False, False)

        self.game = SnakeGame(COLS, ROWS)

        self.canvas = tk.Canvas(
            root,
            width=COLS * CELL,
            height=ROWS * CELL,
            bg=BG_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack()

        self.status = tk.Label(
            root,
            text="",
            bg="#000000",
            fg="#eeeeee",
            font=("Consolas", 11),
            anchor="w",
            padx=8,
        )
        self.status.pack(fill="x")

        self.draw()
        self.root.after(SPEED_MS, self.tick)

    # ─── dessin ─────────────────────────────────────────────────────────────

    def draw(self) -> None:
        self.canvas.delete("all")

        # grille légère
        for x in range(0, COLS * CELL, CELL):
            self.canvas.create_line(x, 0, x, ROWS * CELL, fill=GRID_COLOR)
        for y in range(0, ROWS * CELL, CELL):
            self.canvas.create_line(0, y, COLS * CELL, y, fill=GRID_COLOR)

        # pomme
        fx, fy = self.game.food
        self.canvas.create_oval(
            fx * CELL + 2, fy * CELL + 2,
            fx * CELL + CELL - 2, fy * CELL + CELL - 2,
            fill=FOOD_COLOR, outline="",
        )

        # serpent
        for i, (x, y) in enumerate(self.game.snake):
            color = SNAKE_HEAD if i == 0 else SNAKE_BODY
            self.canvas.create_rectangle(
                x * CELL + 1, y * CELL + 1,
                x * CELL + CELL - 1, y * CELL + CELL - 1,
                fill=color, outline="",
            )

        # statut
        state = "GAME OVER" if self.game.game_over else "en cours"
        self.status.config(
            text=f"Score : {self.game.score:3d}   |   "
                 f"Longueur : {len(self.game.snake):3d}   |   "
                 f"État : {state}   |   Espace : reset"
        )

    # ─── boucle ─────────────────────────────────────────────────────────────

    def tick(self) -> None:
        if not self.game.game_over:
            direction = self.game.ai_decide()
            self.game.step(direction)
            self.draw()

            if self.game.game_over:
                self.game_over_screen()
        self.root.after(SPEED_MS, self.tick)

    def game_over_screen(self) -> None:
        w = COLS * CELL
        h = ROWS * CELL
        self.canvas.create_rectangle(0, h // 2 - 40, w, h // 2 + 40,
                                     fill="#000000", outline="")
        self.canvas.create_text(
            w // 2, h // 2 - 10,
            text="GAME OVER",
            fill="#ff5252",
            font=("Consolas", 22, "bold"),
        )
        self.canvas.create_text(
            w // 2, h // 2 + 18,
            text="Appuyez sur ESPACE pour relancer",
            fill="#eeeeee",
            font=("Consolas", 10),
        )

    def reset(self, _event=None) -> None:
        self.game.reset()
        self.draw()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    root = tk.Tk()
    app = SnakeApp(root)
    root.bind("<space>", app.reset)
    root.mainloop()


if __name__ == "__main__":
    main()