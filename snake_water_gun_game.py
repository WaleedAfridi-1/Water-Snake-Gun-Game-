import random
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox, simpledialog, scrolledtext
import json
import os
import pygame
import time
from datetime import datetime
from PIL import Image, ImageTk

# Initialize pygame mixer for sound
pygame.mixer.init()

# --- Game State ---
choices = ['snake', 'gun', 'water']
user_score = 0
computer_score = 0
draws = 0
rounds = 0
current_round = 0
player_name = ""
move_history = []
game_start_time = 0
game_active = False  # Track if game is active

# --- File Paths ---
HIGH_SCORE_FILE = "high_scores.json"

# --- Sound Effects ---
try:
    click_sound = pygame.mixer.Sound("click.wav")
    win_sound = pygame.mixer.Sound("win.wav")
    lose_sound = pygame.mixer.Sound("lose.wav")
    draw_sound = pygame.mixer.Sound("draw.wav")
except:
    print("Sound files not found. Running without sound effects.")

# --- Functions ---
def load_high_scores():
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, 'r') as file:
            return json.load(file)
    return []

def save_high_score():
    global user_score, player_name
    high_scores = load_high_scores()
    high_scores.append({"name": player_name, "score": user_score})
    high_scores = sorted(high_scores, key=lambda x: x["score"], reverse=True)[:5]
    with open(HIGH_SCORE_FILE, 'w') as file:
        json.dump(high_scores, file, indent=4)

def start_game():
    global player_name, rounds, user_score, computer_score, draws, current_round, move_history, game_start_time, game_active
    
    player_name = simpledialog.askstring("Player Name", "Enter your name:")
    if not player_name:
        messagebox.showwarning("Warning", "Player name required!")
        return
    
    try:
        rounds = int(simpledialog.askstring("Game Rounds", "Enter number of rounds (1-10):"))
        if rounds <= 0 or rounds > 10:
            raise ValueError
    except:
        messagebox.showerror("Invalid Input", "Please enter a number between 1 and 10.")
        return
    
    user_score = computer_score = draws = current_round = 0
    move_history = []
    game_start_time = time.time()
    game_active = True
    update_score()
    update_history()
    toggle_buttons(state="normal")
    result_label.config(text="Let's Play!", bootstyle="info")
    start_btn.config(state="disabled")
    reset_btn.config(state="normal")
    try:
        click_sound.play()
    except:
        pass

def play(user_choice):
    global user_score, computer_score, draws, current_round, game_active
    
    if not game_active or current_round >= rounds:
        return

    try:
        click_sound.play()
    except:
        pass

    computer_choice = random.choice(choices)
    result = ""
    result_style = "info"

    if user_choice == computer_choice:
        result = "It's a Draw!"
        draws += 1
        result_style = "warning"
        try:
            draw_sound.play()
        except:
            pass
    elif (user_choice == "snake" and computer_choice == "water") or \
         (user_choice == "gun" and computer_choice == "snake") or \
         (user_choice == "water" and computer_choice == "gun"):
        result = f"{player_name}, You Win!"
        user_score += 1
        result_style = "success"
        try:
            win_sound.play()
        except:
            pass
    else:
        result = f"{player_name}, You Lose!"
        computer_score += 1
        result_style = "danger"
        try:
            lose_sound.play()
        except:
            pass

    current_round += 1
    move_history.append(f"Round {current_round}: {player_name} chose {user_choice.capitalize()}, Computer chose {computer_choice.capitalize()} - {result}")
    user_choice_label.config(text=f"Your Choice: {user_choice.capitalize()}")
    comp_choice_label.config(text=f"Computer's Choice: {computer_choice.capitalize()}")
    result_label.config(text=result, bootstyle=result_style)
    update_score()
    update_history()

    if current_round == rounds:
        game_active = False
        toggle_buttons("disabled")
        save_high_score()
        show_leaderboard()

def update_score():
    score_label.config(
        text=f"{player_name}: {user_score}   Computer: {computer_score}   Draws: {draws}   Round: {current_round}/{rounds}"
    )

def update_history():
    history_text.delete(1.0, END)
    for move in move_history:
        history_text.insert(END, move + "\n")

def show_leaderboard():
    high_scores = load_high_scores()
    if user_score > computer_score:
        winner = f"🎉 {player_name} Wins!"
    elif computer_score > user_score:
        winner = "🤖 Computer Wins!"
    else:
        winner = "😐 It's a Tie!"

    msg = f"Game Over!\n\n{player_name}: {user_score}\nComputer: {computer_score}\nDraws: {draws}\n\n{winner}\n\nHigh Scores:\n"
    for i, score in enumerate(high_scores, 1):
        msg += f"{i}. {score['name']}: {score['score']}\n"
    messagebox.showinfo("Game Over - Leaderboard", msg)
    start_btn.config(state="normal")
    reset_btn.config(state="normal")

def reset_game():
    global user_score, computer_score, draws, current_round, move_history, game_active
    
    user_score = computer_score = draws = current_round = 0
    move_history = []
    game_active = False
    update_score()
    update_history()
    user_choice_label.config(text="Your Choice:")
    comp_choice_label.config(text="Computer's Choice:")
    result_label.config(text="Game Reset!", bootstyle="info")
    toggle_buttons("disabled")
    start_btn.config(state="normal")
    try:
        click_sound.play()
    except:
        pass

def toggle_buttons(state):
    snake_btn.config(state=state)
    gun_btn.config(state=state)
    water_btn.config(state=state)

def exit_game():
    if messagebox.askyesno("Exit Game", "Are you sure you want to quit?"):
        app.destroy()

# --- GUI Setup ---
app = tb.Window(themename="cyborg")
app.title("Snake Gun Water - Fixed Version")
app.geometry("700x650")

# --- Widgets ---
title_label = tb.Label(app, text="🐍 Snake - 🔫 Gun - 💧 Water", font=("Arial", 28, "bold"))
title_label.pack(pady=10)

rules_label = tb.Label(
    app,
    text="📜 Rules:\n1. Snake drinks Water 🐍 > 💧\n2. Water drowns Gun 💧 > 🔫\n3. Gun shoots Snake 🔫 > 🐍",
    font=("Arial", 12), 
    justify="left",
    bootstyle="secondary"
).pack(pady=5)

user_choice_label = tb.Label(app, text="Your Choice:", font=("Arial", 14), bootstyle="info")
user_choice_label.pack(pady=5)

comp_choice_label = tb.Label(app, text="Computer's Choice:", font=("Arial", 14), bootstyle="info")
comp_choice_label.pack(pady=5)

result_label = tb.Label(app, text="", font=("Arial", 16, "bold"), bootstyle="info")
result_label.pack(pady=10)

score_label = tb.Label(app, text="User: 0   Computer: 0   Draws: 0   Round: 0/0", font=("Arial", 14))
score_label.pack(pady=10)

# Move History
history_label = tb.Label(app, text="Move History", font=("Arial", 12, "bold"))
history_label.pack()
history_text = scrolledtext.ScrolledText(app, height=5, width=60, font=("Arial", 10))
history_text.pack(pady=5)

# Button Frame
btn_frame = tb.Frame(app)
btn_frame.pack(pady=10)

snake_btn = tb.Button(btn_frame, text="Snake 🐍", bootstyle="success", width=15, command=lambda: play("snake"), state="disabled")
snake_btn.grid(row=0, column=0, padx=10)

gun_btn = tb.Button(btn_frame, text="Gun 🔫", bootstyle="info", width=15, command=lambda: play("gun"), state="disabled")
gun_btn.grid(row=0, column=1, padx=10)

water_btn = tb.Button(btn_frame, text="Water 💧", bootstyle="primary", width=15, command=lambda: play("water"), state="disabled")
water_btn.grid(row=0, column=2, padx=10)

# Control Buttons
control_frame = tb.Frame(app)
control_frame.pack(pady=10)

start_btn = tb.Button(control_frame, text="🎮 Start Game", bootstyle="warning", command=start_game)
start_btn.grid(row=0, column=0, padx=5)

reset_btn = tb.Button(control_frame, text="🔄 Reset Game", bootstyle="secondary", command=reset_game, state="disabled")
reset_btn.grid(row=0, column=1, padx=5)

exit_btn = tb.Button(control_frame, text="🚪 Exit Game", bootstyle="danger", command=exit_game)
exit_btn.grid(row=0, column=2, padx=5)

# Run App
app.mainloop()