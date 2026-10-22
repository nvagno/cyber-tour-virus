#!/usr/bin/env python3
"""
Casse-briques (Breakout) automatique — l'IA joue toute seule.
L'IA prédit la position d'arrivée de la balle et déplace la raquette.
Interface : Tkinter (aucune dépendance externe).
"""

import tkinter as tk
import random
import math

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

WIDTH       = 640
HEIGHT      = 480
FPS_MS      = 16              # ~60 fps

PADDLE_W    = 90
PADDLE_H    = 12
PADDLE_Y    = HEIGHT - 30
PADDLE_SPEED = 9              # px par frame (max)

BALL_R      = 7
BALL_SPEED  = 5.0

BRICK_ROWS  = 6
BRICK_COLS  = 12
BRICK_W     = WIDTH // BRICK_COLS
BRICK_H     = 22
BRICK_TOP   = 50

BG_COLOR     = "#0d1117"
PADDLE_COLOR = "#58a6ff"
BALL_COLOR   = "#f0f6fc"
BRICK_COLORS = ["#f85149", "#ffa657", "#d29922",
                "#3fb950", "#58a6ff", "#bc8cff"]


# ─────────────────────────────────────────────────────────────────────────────
# LOGIQUE DU JEU
# ─────────────────────────────────────────────────────────────────────────────

class Brick:
    __slots__ = ("x", "y", "w", "h", "alive", "color")
    def __init__(self, x, y, w, h, color):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.alive = True
        self.color = color


class BreakoutGame:
    def __init__(self):
        self.reset()

    def reset(self):
        self.paddle_x = (WIDTH - PADDLE_W) / 2
        self.ball_x   = WIDTH / 2
        self.ball_y   = HEIGHT / 2
        angle = random.uniform(-math.pi / 4, math.pi / 4)
        direction = random.choice([-1, 1])
        self.ball_vx = BALL_SPEED * math.sin(angle) * direction
        self.ball_vy = -BALL_SPEED * math.cos(angle)

        self.bricks = []
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                x = col * BRICK_W
                y = BRICK_TOP + row * BRICK_H
                color = BRICK_COLORS[row % len(BRICK_COLORS)]
                self.bricks.append(Brick(x, y, BRICK_W - 2, BRICK_H - 2, color))

        self.score = 0
        self.lives = 3
        self.game_over = False
        self.win = False

    # ─── physique ───────────────────────────────────────────────────────────

    def step(self):
        if self.game_over or self.win:
            return

        # ── IA : déplace la raquette vers la cible
        target = self._predict_landing()
        diff = target - (self.paddle_x + PADDLE_W / 2)
        if abs(diff) > PADDLE_SPEED:
            self.paddle_x += PADDLE_SPEED if diff > 0 else -PADDLE_SPEED
        else:
            self.paddle_x += diff
        # clamp
        self.paddle_x = max(0, min(WIDTH - PADDLE_W, self.paddle_x))

        # ── balle
        self.ball_x += self.ball_vx
        self.ball_y += self.ball_vy

        # murs gauche/droite
        if self.ball_x - BALL_R <= 0:
            self.ball_x = BALL_R
            self.ball_vx = abs(self.ball_vx)
        elif self.ball_x + BALL_R >= WIDTH:
            self.ball_x = WIDTH - BALL_R
            self.ball_vx = -abs(self.ball_vx)

        # mur haut
        if self.ball_y - BALL_R <= 0:
            self.ball_y = BALL_R
            self.ball_vy = abs(self.ball_vy)

        # raquette
        if (self.ball_vy > 0
                and PADDLE_Y <= self.ball_y + BALL_R <= PADDLE_Y + PADDLE_H
                and self.paddle_x <= self.ball_x <= self.paddle_x + PADDLE_W):
            self.ball_y = PADDLE_Y - BALL_R
            # angle selon le point d'impact
            offset = (self.ball_x - (self.paddle_x + PADDLE_W / 2)) / (PADDLE_W / 2)
            offset = max(-1.0, min(1.0, offset))
            angle = offset * (math.pi / 3)
            self.ball_vx = BALL_SPEED * math.sin(angle)
            self.ball_vy = -BALL_SPEED * math.cos(angle)

        # briques
        for b in self.bricks:
            if not b.alive:
                continue
            if (b.x <= self.ball_x <= b.x + b.w
                    and b.y <= self.ball_y <= b.y + b.h):
                b.alive = False
                self.score += 10
                # rebond : déterminer le côté le plus proche
                overlap_x = min(abs(self.ball_x - b.x), abs(self.ball_x - (b.x + b.w)))
                overlap_y = min(abs(self.ball_y - b.y), abs(self.ball_y - (b.y + b.h)))
                if overlap_x < overlap_y:
                    self.ball_vx *= -1
                else:
                    self.ball_vy *= -1
                break

        # balle perdue
        if self.ball_y - BALL_R > HEIGHT:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                self._reset_ball()

        # victoire
        if all(not b.alive for b in self.bricks):
            self.win = True

    def _reset_ball(self):
        self.ball_x = self.paddle_x + PADDLE_W / 2
        self.ball_y = PADDLE_Y - BALL_R - 1
        angle = random.uniform(-math.pi / 4, math.pi / 4)
        direction = random.choice([-1, 1])
        self.ball_vx = BALL_SPEED * math.sin(angle) * direction
        self.ball_vy = -BALL_SPEED * math.cos(angle)

    def _predict_landing(self):
        """
        Simule le trajet de la balle (avec rebonds murs) jusqu'à la ligne
        de la raquette, et renvoie la coordonnée x d'arrivée.
        """
        x, y = self.ball_x, self.ball_y
        vx, vy = self.ball_vx, self.ball_vy

        if vy <= 0:
            # la balle monte : on renvoie la position actuelle (la raquette
            # n'a pas besoin de bouger tout de suite)
            return x

        while y < PADDLE_Y - BALL_R:
            # avance par petits pas
            step = 1.0
            y += vy * step
            x += vx * step
            if x - BALL_R <= 0:
                x = BALL_R
                vx = abs(vx)
            elif x + BALL_R >= WIDTH:
                x = WIDTH - BALL_R
                vx = -abs(vx)
        return x


# ─────────────────────────────────────────────────────────────────────────────
# INTERFACE TKINTER
# ─────────────────────────────────────────────────────────────────────────────

class BreakoutApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Casse-briques automatique")
        self.root.resizable(False, False)

        self.game = BreakoutGame()

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT,
                                bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack()

        self.status = tk.Label(root, text="", bg="#000000", fg="#eeeeee",
                               font=("Consolas", 11), anchor="w", padx=8)
        self.status.pack(fill="x")

        self.draw()
        self.root.after(FPS_MS, self.tick)

    # ─── dessin ─────────────────────────────────────────────────────────────

    def draw(self):
        c = self.canvas
        c.delete("all")

        for b in self.game.bricks:
            if b.alive:
                c.create_rectangle(b.x, b.y, b.x + b.w, b.y + b.h,
                                   fill=b.color, outline="")

        c.create_rectangle(
            self.game.paddle_x, PADDLE_Y,
            self.game.paddle_x + PADDLE_W, PADDLE_Y + PADDLE_H,
            fill=PADDLE_COLOR, outline="",
        )

        c.create_oval(
            self.game.ball_x - BALL_R, self.game.ball_y - BALL_R,
            self.game.ball_x + BALL_R, self.game.ball_y + BALL_R,
            fill=BALL_COLOR, outline="",
        )

        etat = "GAGNÉ" if self.game.win else ("PERDU" if self.game.game_over else "en cours")
        self.status.config(
            text=f"Score : {self.game.score:4d}   |   "
                 f"Vies : {self.game.lives}   |   "
                 f"Briques : {sum(1 for b in self.game.bricks if b.alive):2d}   |   "
                 f"État : {etat}   |   Espace : reset"
        )

    # ─── boucle ─────────────────────────────────────────────────────────────

    def tick(self):
        self.game.step()
        self.draw()

        if self.game.game_over or self.game.win:
            self.end_screen()

        self.root.after(FPS_MS, self.tick)

    def end_screen(self):
        msg = "VICTOIRE !" if self.game.win else "GAME OVER"
        color = "#3fb950" if self.game.win else "#f85149"
        self.canvas.create_rectangle(0, HEIGHT // 2 - 40, WIDTH, HEIGHT // 2 + 40,
                                     fill="#000000", outline="")
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2 - 12, text=msg,
                                fill=color, font=("Consolas", 24, "bold"))
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2 + 20,
                                text="ESPACE pour relancer",
                                fill="#eeeeee", font=("Consolas", 10))

    def reset(self, _event=None):
        self.game.reset()
        self.draw()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    app = BreakoutApp(root)
    root.bind("<space>", app.reset)
    root.mainloop()


if __name__ == "__main__":
    main()