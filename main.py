import tkinter as tk
from tkinter import messagebox, ttk
from database import create_connection
from game import open_game_setup


# =========================================================
# MAIN MENU
# =========================================================

def show_main_menu():

    # Clear current screen
    for widget in root.winfo_children():
        widget.destroy()

    # Main frame
    main_frame = tk.Frame(
        root,
        bg="#141414"
    )

    main_frame.pack(
        fill="both",
        expand=True
    )

    # Center card container
    center_frame = tk.Frame(
        main_frame,
        bg="#141414"
    )
    center_frame.place(relx=0.5, rely=0.5, anchor="center")

    # -----------------------------------------------------
    # TITLE & SUBTITLE
    # -----------------------------------------------------

    tk.Label(
        center_frame,
        text="🔐 ESCAPE ROOM",
        font=("Helvetica", 46, "bold"),
        fg="#ffffff",
        bg="#141414"
    ).pack(pady=(0, 10))

    tk.Label(
        center_frame,
        text="A Database-Driven Mystery Experience",
        font=("Helvetica", 17, "italic"),
        fg="#aaaaaa",
        bg="#141414"
    ).pack(pady=(0, 8))

    tk.Label(
        center_frame,
        text="Solve the puzzles, beat the clock, and claim your place on the leaderboard!",
        font=("Helvetica", 14),
        fg="#888888",
        bg="#141414"
    ).pack(pady=(0, 40))

    # -----------------------------------------------------
    # START GAME
    # -----------------------------------------------------

    tk.Button(
        center_frame,
        text="🎮  START GAME",
        font=("Helvetica", 16, "bold"),
        bg="#27ae60",
        fg="black",
        activebackground="#2ecc71",
        width=26,
        height=2,
        cursor="hand2",
        command=lambda: open_game_setup(root, show_main_menu)
    ).pack(pady=10)

    # -----------------------------------------------------
    # HOW TO PLAY
    # -----------------------------------------------------

    def show_how_to_play():
        rules_win = tk.Toplevel(root)
        rules_win.title("How to Play - Escape Room")
        rules_win.geometry("700x560")
        rules_win.configure(bg="#1c1c1c")
        rules_win.transient(root)
        rules_win.grab_set()

        content_frame = tk.Frame(rules_win, bg="#1c1c1c", padx=30, pady=25)
        content_frame.pack(fill="both", expand=True)

        tk.Label(
            content_frame,
            text="📖 HOW TO PLAY",
            font=("Helvetica", 22, "bold"),
            fg="#f1c40f",
            bg="#1c1c1c"
        ).pack(pady=(0, 15))

        rules_text = (
            "1. TEAM & ROOM SELECTION:\n"
            "   • Choose an existing team or register a brand-new team of 2+ players.\n"
            "   • Pick an Escape Room theme (3 detailed rooms with rich visual clues & varying time limits).\n\n"
            "2. PUZZLES & PROGRESSION:\n"
            "   • Each room contains 5 sequential puzzles.\n"
            "   • Read the description, decipher the riddles or images, and type your answer.\n"
            "   • Answers are case-insensitive (press Enter or click Submit).\n\n"
            "3. HINTS & SCORING:\n"
            "   • Each puzzle awards 100 to 150 points.\n"
            "   • If stuck, click '💡 HINT'. Each hint deducts points from your total score!\n\n"
            "4. TIME LIMIT:\n"
            "   • Watch the countdown timer in the top right corner.\n"
            "   • Solve all 5 puzzles before the timer runs out to ESCAPE!\n\n"
            "5. FORFEITING:\n"
            "   • If needed, you can forfeit a room during play to return to the main menu."
        )

        tk.Label(
            content_frame,
            text=rules_text,
            font=("Helvetica", 13),
            fg="#dddddd",
            bg="#1c1c1c",
            justify="left",
            wraplength=640
        ).pack(pady=10, fill="both")

        tk.Button(
            content_frame,
            text="Got it!",
            font=("Helvetica", 13, "bold"),
            width=15,
            height=1,
            cursor="hand2",
            command=rules_win.destroy
        ).pack(pady=(15, 0))

    tk.Button(
        center_frame,
        text="📖  HOW TO PLAY",
        font=("Helvetica", 16, "bold"),
        width=26,
        height=2,
        cursor="hand2",
        command=show_how_to_play
    ).pack(pady=10)

    # -----------------------------------------------------
    # LEADERBOARD
    # -----------------------------------------------------

    def show_leaderboard():
        connection = create_connection()

        if connection is None:
            messagebox.showerror(
                "Database Error",
                "Could not connect to the database.\nPlease check MySQL status."
            )
            return

        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT
                    team_name,
                    games_played,
                    games_escaped,
                    highest_score,
                    average_score
                FROM leaderboard
                ORDER BY highest_score DESC, games_escaped DESC;
            """)
            results = cursor.fetchall()
            cursor.close()
            connection.close()

            # Create styled modal dialog for leaderboard
            lb_win = tk.Toplevel(root)
            lb_win.title("Leaderboard - Top Teams")
            lb_win.geometry("780x580")
            lb_win.configure(bg="#181818")
            lb_win.transient(root)
            lb_win.grab_set()

            lb_frame = tk.Frame(lb_win, bg="#181818", padx=25, pady=20)
            lb_frame.pack(fill="both", expand=True)

            tk.Label(
                lb_frame,
                text="🏆 HALL OF FAME LEADERBOARD",
                font=("Helvetica", 22, "bold"),
                fg="#f1c40f",
                bg="#181818"
            ).pack(pady=(0, 15))

            # Table Frame
            table_container = tk.Frame(lb_frame, bg="#222222")
            table_container.pack(fill="both", expand=True, pady=10)

            # Headers
            headers = ["Rank", "Team Name", "Played", "Escaped", "Best Score", "Avg Score"]
            col_widths = [8, 24, 10, 10, 12, 12]

            header_frame = tk.Frame(table_container, bg="#2d3436")
            header_frame.pack(fill="x")

            for h, w in zip(headers, col_widths):
                tk.Label(
                    header_frame,
                    text=h,
                    font=("Helvetica", 12, "bold"),
                    fg="#ffffff",
                    bg="#2d3436",
                    width=w,
                    anchor="center",
                    pady=8
                ).pack(side="left")

            # Data rows
            canvas = tk.Canvas(table_container, bg="#1e272e", highlightthickness=0)
            scrollbar = tk.Scrollbar(table_container, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="#1e272e")

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            medals = ["🥇", "🥈", "🥉"]

            if not results:
                tk.Label(
                    scrollable_frame,
                    text="No games recorded yet. Be the first team to escape!",
                    font=("Helvetica", 13, "italic"),
                    fg="#888888",
                    bg="#1e272e",
                    pady=20
                ).pack()
            else:
                for i, row in enumerate(results, start=1):
                    team_name, played, escaped, highest, avg = row
                    rank_icon = medals[i - 1] if i <= 3 else f"#{i}"
                    row_bg = "#222f3e" if i % 2 == 0 else "#1e272e"

                    row_frame = tk.Frame(scrollable_frame, bg=row_bg)
                    row_frame.pack(fill="x")

                    row_values = [
                        rank_icon,
                        team_name,
                        str(played),
                        str(escaped),
                        str(highest),
                        f"{avg:.1f}"
                    ]

                    for val, w in zip(row_values, col_widths):
                        tk.Label(
                            row_frame,
                            text=val,
                            font=("Helvetica", 12),
                            fg="#ecf0f1",
                            bg=row_bg,
                            width=w,
                            anchor="center",
                            pady=7
                        ).pack(side="left")

            tk.Button(
                lb_frame,
                text="Close",
                font=("Helvetica", 13, "bold"),
                width=15,
                cursor="hand2",
                command=lb_win.destroy
            ).pack(pady=(15, 0))

        except Exception as error:
            messagebox.showerror(
                "Database Error",
                f"Could not load leaderboard:\n{error}"
            )

    tk.Button(
        center_frame,
        text="🏆  LEADERBOARD",
        font=("Helvetica", 16, "bold"),
        width=26,
        height=2,
        cursor="hand2",
        command=show_leaderboard
    ).pack(pady=10)

    # -----------------------------------------------------
    # EXIT
    # -----------------------------------------------------

    tk.Button(
        center_frame,
        text="❌  EXIT",
        font=("Helvetica", 16, "bold"),
        width=26,
        height=2,
        cursor="hand2",
        command=root.destroy
    ).pack(pady=10)

    # Footer note
    tk.Label(
        main_frame,
        text="Press [Esc] to exit fullscreen  •  Press [F11] to toggle fullscreen",
        font=("Helvetica", 11),
        fg="#555555",
        bg="#141414"
    ).pack(side="bottom", pady=15)


# =========================================================
# WINDOW CONFIGURATION
# =========================================================

root = tk.Tk()
root.title("Escape Room - DBMS Project")
root.geometry("1280x820")
root.minsize(1024, 700)
root.configure(bg="#141414")

# Center window on screen
root.update_idletasks()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = max(0, (screen_width - 1280) // 2)
y = max(0, (screen_height - 820) // 2)
root.geometry(f"1280x820+{x}+{y}")

# Bring window to front on macOS
root.lift()
root.attributes("-topmost", True)
root.after_idle(root.attributes, "-topmost", False)
root.focus_force()

# FULLSCREEN TOGGLE
is_fullscreen = False


def exit_fullscreen(event=None):
    global is_fullscreen
    is_fullscreen = False
    root.attributes("-fullscreen", False)


def toggle_fullscreen(event=None):
    global is_fullscreen
    is_fullscreen = not is_fullscreen
    root.attributes("-fullscreen", is_fullscreen)


root.bind("<Escape>", exit_fullscreen)
root.bind("<F11>", toggle_fullscreen)

# Show main menu
show_main_menu()

root.mainloop()