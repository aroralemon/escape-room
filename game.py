import tkinter as tk
from tkinter import messagebox
from database import create_connection
from PIL import Image, ImageTk
import os


def open_game_setup(root, show_main_menu):

    # =====================================================
    # CLEAR SCREEN
    # =====================================================

    def clear_screen():

        for widget in root.winfo_children():
            widget.destroy()

    # =====================================================
    # START GAME SESSION
    # =====================================================

    def start_game_session(
        team_id,
        room_id,
        team_name,
        room_name
    ):

        connection = create_connection()

        if connection is None:
            messagebox.showerror(
                "Database Error",
                "Could not connect to database."
            )
            return

        cursor = None

        try:

            cursor = connection.cursor()

            # ---------------------------------------------
            # GET TIME LIMIT
            # ---------------------------------------------

            cursor.execute(
                """
                SELECT time_limit
                FROM rooms
                WHERE room_id = %s
                """,
                (room_id,)
            )

            result = cursor.fetchone()

            if not result:
                raise Exception("Room not found.")

            time_limit = result[0]

            # ---------------------------------------------
            # GET PUZZLES
            # ---------------------------------------------

            cursor.execute(
                """
                SELECT
                    puzzle_id,
                    puzzle_name,
                    description,
                    answer,
                    points,
                    sequence_no,
                    image_path
                FROM puzzles
                WHERE room_id = %s
                ORDER BY sequence_no
                """,
                (room_id,)
            )

            puzzles = cursor.fetchall()

            if not puzzles:

                raise Exception(
                    "This room does not have any puzzles yet."
                )

            # ---------------------------------------------
            # CREATE SESSION
            # ---------------------------------------------

            cursor.execute(
                """
                INSERT INTO game_sessions
                (
                    team_id,
                    room_id,
                    start_time,
                    status,
                    final_score
                )
                VALUES
                (
                    %s,
                    %s,
                    NOW(),
                    'ACTIVE',
                    0
                )
                """,
                (
                    team_id,
                    room_id
                )
            )

            session_id = cursor.lastrowid

            connection.commit()

            cursor.close()
            connection.close()

        except Exception as error:

            if cursor:
                connection.rollback()
                cursor.close()

            connection.close()

            messagebox.showerror(
                "Could not start game",
                str(error)
            )

            return

        # =================================================
        # GAME VARIABLES
        # =================================================

        current_puzzle = 0
        score = 0

        time_left = time_limit * 60

        hint_number = 0
        timer_id = None

        # =================================================
        # GAME SCREEN
        # =================================================

        clear_screen()

        game_frame = tk.Frame(
            root,
            bg="#101010"
        )

        game_frame.pack(
            fill="both",
            expand=True
        )

        # =================================================
        # TOP BAR
        # =================================================

        top_frame = tk.Frame(
            game_frame,
            bg="#181818",
            height=70
        )

        top_frame.pack(
            fill="x",
            padx=25,
            pady=(15, 5)
        )

        top_frame.pack_propagate(False)

        room_label = tk.Label(
            top_frame,
            text=room_name,
            font=("Helvetica", 24, "bold"),
            fg="white",
            bg="#181818"
        )

        room_label.pack(
            side="left",
            padx=20
        )

        score_label = tk.Label(
            top_frame,
            text="SCORE: 0",
            font=("Helvetica", 18, "bold"),
            fg="white",
            bg="#181818"
        )

        score_label.pack(
            side="right",
            padx=25
        )

        timer_label = tk.Label(
            top_frame,
            text="",
            font=("Helvetica", 20, "bold"),
            fg="white",
            bg="#181818"
        )

        timer_label.pack(
            side="right",
            padx=25
        )

        # =================================================
        # TEAM
        # =================================================

        tk.Label(
            game_frame,
            text=f"TEAM: {team_name}",
            font=("Helvetica", 14),
            fg="#aaaaaa",
            bg="#101010"
        ).pack(
            pady=(5, 2)
        )

        # =================================================
        # PUZZLE NUMBER
        # =================================================

        puzzle_number_label = tk.Label(
            game_frame,
            text="",
            font=("Helvetica", 18, "bold"),
            fg="#dddddd",
            bg="#101010"
        )

        puzzle_number_label.pack(
            pady=(5, 0)
        )

        # =================================================
        # PUZZLE NAME
        # =================================================

        puzzle_name_label = tk.Label(
            game_frame,
            text="",
            font=("Helvetica", 27, "bold"),
            fg="white",
            bg="#101010"
        )

        puzzle_name_label.pack(
            pady=(2, 3)
        )

        # =================================================
        # INSTRUCTION
        # =================================================

        instruction_label = tk.Label(
            game_frame,
            text="",
            font=("Helvetica", 14, "italic"),
            fg="#cccccc",
            bg="#101010",
            wraplength=1000
        )

        instruction_label.pack(
            pady=(0, 8)
        )

        # =================================================
        # VISUAL / DESCRIPTION AREA
        # =================================================

        visual_frame = tk.Frame(
            game_frame,
            bg="#101010"
        )

        visual_frame.pack(
            fill="x",
            pady=3
        )

        image_label = tk.Label(
            visual_frame,
            bg="#101010"
        )

        image_label.pack()

        description_label = tk.Label(
            visual_frame,
            text="",
            font=("Helvetica", 16),
            fg="#dddddd",
            bg="#101010",
            wraplength=1000,
            justify="center"
        )

        # =================================================
        # ANSWER AREA
        # =================================================

        answer_frame = tk.Frame(
            game_frame,
            bg="#101010"
        )

        answer_frame.pack(
            pady=(8, 2)
        )

        tk.Label(
            answer_frame,
            text="YOUR ANSWER",
            font=("Helvetica", 13, "bold"),
            fg="white",
            bg="#101010"
        ).pack(
            pady=(0, 4)
        )

        answer_entry = tk.Entry(
            answer_frame,
            font=("Helvetica", 17),
            width=25,
            justify="center"
        )

        answer_entry.pack()

        # =================================================
        # FEEDBACK
        # =================================================

        feedback_label = tk.Label(
            game_frame,
            text="",
            font=("Helvetica", 14, "bold"),
            fg="white",
            bg="#101010"
        )

        feedback_label.pack(
            pady=3
        )

        # =================================================
        # HINT
        # =================================================

        hint_label = tk.Label(
            game_frame,
            text="",
            font=("Helvetica", 13),
            fg="#d0d0d0",
            bg="#101010",
            wraplength=900,
            justify="center"
        )

        hint_label.pack(
            pady=2
        )

        # =================================================
        # PROGRESS
        # =================================================

        progress_label = tk.Label(
            game_frame,
            text="",
            font=("Helvetica", 12),
            fg="#777777",
            bg="#101010"
        )

        progress_label.pack(
            pady=4
        )

        # =================================================
        # BUTTON FRAME
        # =================================================

        button_frame = tk.Frame(
            game_frame,
            bg="#101010"
        )

        button_frame.pack(
            pady=5
        )

        # =================================================
        # FINISH GAME
        # =================================================

        def finish_game(status):

            nonlocal timer_id

            if timer_id is not None:

                try:
                    root.after_cancel(timer_id)
                except:
                    pass

                timer_id = None

            connection = create_connection()

            if connection:

                cursor = None

                try:

                    cursor = connection.cursor()

                    cursor.execute(
                        """
                        UPDATE game_sessions
                        SET
                            end_time = NOW(),
                            status = %s,
                            final_score = %s
                        WHERE session_id = %s
                        """,
                        (
                            status,
                            score,
                            session_id
                        )
                    )

                    connection.commit()

                    cursor.close()
                    connection.close()

                except Exception as error:

                    connection.rollback()

                    if cursor:
                        cursor.close()

                    connection.close()

                    messagebox.showerror(
                        "Database Error",
                        str(error)
                    )

            # ---------------------------------------------
            # RESULT SCREEN
            # ---------------------------------------------

            clear_screen()

            result_frame = tk.Frame(
                root,
                bg="#101010"
            )

            result_frame.pack(
                fill="both",
                expand=True
            )

            if status == "ESCAPED":

                title = "🎉 YOU ESCAPED!"

                message = (
                    f"Congratulations, {team_name}!\n\n"
                    f"You escaped from {room_name}."
                )

            else:

                title = "⏰ TIME'S UP!"

                message = (
                    f"Sorry, {team_name}.\n\n"
                    f"You couldn't escape from "
                    f"{room_name} in time."
                )

            tk.Label(
                result_frame,
                text=title,
                font=("Helvetica", 48, "bold"),
                fg="white",
                bg="#101010"
            ).pack(
                pady=(150, 25)
            )

            tk.Label(
                result_frame,
                text=message,
                font=("Helvetica", 20),
                fg="#cccccc",
                bg="#101010"
            ).pack(
                pady=15
            )

            tk.Label(
                result_frame,
                text=f"FINAL SCORE: {score}",
                font=("Helvetica", 30, "bold"),
                fg="white",
                bg="#101010"
            ).pack(
                pady=25
            )

            tk.Button(
                result_frame,
                text="PLAY AGAIN",
                font=("Helvetica", 16, "bold"),
                width=20,
                height=2,
                command=lambda: open_game_setup(
                    root,
                    show_main_menu
                )
            ).pack(
                pady=10
            )

            tk.Button(
                result_frame,
                text="MAIN MENU",
                font=("Helvetica", 14),
                width=15,
                command=show_main_menu
            ).pack(
                pady=10
            )

        # =================================================
        # LOAD PUZZLE
        # =================================================

        def load_puzzle():

            nonlocal hint_number

            hint_number = 0

            puzzle = puzzles[current_puzzle]

            puzzle_id = puzzle[0]
            puzzle_name = puzzle[1]
            description = puzzle[2]
            points = puzzle[4]
            sequence = puzzle[5]
            image_path_val = puzzle[6] if len(puzzle) > 6 else None

            # ---------------------------------------------
            # BASIC INFO
            # ---------------------------------------------

            puzzle_number_label.config(
                text=f"STAGE {sequence} OF {len(puzzles)}"
            )

            puzzle_name_label.config(
                text=puzzle_name
            )

            progress_label.config(
                text=(
                    f"Stage {sequence} of {len(puzzles)}"
                    f"   •   Value: {points} points"
                )
            )

            # ---------------------------------------------
            # CLEAR OLD DATA
            # ---------------------------------------------

            answer_entry.delete(
                0,
                tk.END
            )

            feedback_label.config(
                text=""
            )

            hint_label.config(
                text=""
            )

            # ---------------------------------------------
            # INSTRUCTIONS
            # ---------------------------------------------

            if sequence == 1:
                instruction_label.config(
                    text="Examine the room illustration and decipher the clue to begin your escape."
                )
            elif sequence == len(puzzles):
                instruction_label.config(
                    text="FINAL STAGE: Unlock the exit door before the countdown timer reaches zero!"
                )
            else:
                instruction_label.config(
                    text="Analyze the visual clue and riddle to unlock the next chamber."
                )

            # ---------------------------------------------
            # DYNAMIC VISUAL CLUE LOADING
            # ---------------------------------------------

            resolved_image = None
            if image_path_val:
                candidate = os.path.join(os.path.dirname(__file__), str(image_path_val).strip())
                if os.path.exists(candidate):
                    resolved_image = candidate

            if not resolved_image:
                # Fallback candidates based on room and sequence
                fallbacks = [
                    os.path.join(os.path.dirname(__file__), "images", f"room{room_id}_p{sequence}.png"),
                    os.path.join(os.path.dirname(__file__), "images", f"room{room_id}_p{sequence}.jpg"),
                ]
                if room_id == 1 and sequence == 1:
                    fallbacks.append(os.path.join(os.path.dirname(__file__), "haunted_manor_puzzle1.png"))

                for fb in fallbacks:
                    if os.path.exists(fb):
                        resolved_image = fb
                        break

            if resolved_image:
                try:
                    original_image = Image.open(resolved_image)
                    max_width = 750
                    max_height = 310

                    image_copy = original_image.copy()
                    image_copy.thumbnail(
                        (max_width, max_height),
                        Image.Resampling.LANCZOS
                    )

                    puzzle_image = ImageTk.PhotoImage(image_copy)
                    image_label.config(
                        image=puzzle_image,
                        text=""
                    )
                    image_label.image = puzzle_image
                    image_label.pack(pady=(2, 4))

                except Exception as error:
                    image_label.config(
                        text=f"[Visual clue loading error: {error}]",
                        fg="#e74c3c"
                    )
                    image_label.image = None
                    image_label.pack()
            else:
                image_label.config(
                    image="",
                    text=""
                )
                image_label.image = None
                image_label.pack_forget()

            # Always display the description / riddle text below the visual clue
            description_label.config(
                text=description,
                font=("Helvetica", 14)
            )
            description_label.pack(
                pady=(4, 6)
            )

            answer_entry.focus()

        # =================================================
        # SUBMIT ANSWER
        # =================================================

        def submit_answer():

            nonlocal current_puzzle
            nonlocal score

            answer = answer_entry.get().strip()

            if not answer:

                feedback_label.config(
                    text="⚠️ Enter an answer first.",
                    fg="#ffcc00"
                )

                answer_entry.focus()

                return

            puzzle = puzzles[current_puzzle]

            puzzle_id = puzzle[0]
            correct_answer = puzzle[3]
            points = puzzle[4]

            # ---------------------------------------------
            # CHECK ANSWER
            # ---------------------------------------------

            is_correct = (
                answer.casefold()
                == str(correct_answer).strip().casefold()
            )

            connection = create_connection()

            if connection is None:
                return

            cursor = None

            try:

                cursor = connection.cursor()

                # -----------------------------------------
                # RECORD ATTEMPT
                # -----------------------------------------

                cursor.execute(
                    """
                    INSERT INTO puzzle_attempts
                    (
                        session_id,
                        puzzle_id,
                        answer_submitted,
                        is_correct
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        session_id,
                        puzzle_id,
                        answer,
                        is_correct
                    )
                )

                connection.commit()

                cursor.close()
                connection.close()

            except Exception as error:

                connection.rollback()

                if cursor:
                    cursor.close()

                connection.close()

                messagebox.showerror(
                    "Database Error",
                    str(error)
                )

                return

            # ---------------------------------------------
            # WRONG
            # ---------------------------------------------

            if not is_correct:

                feedback_label.config(
                    text="❌ That's not it. Look again!",
                    fg="#ff5555"
                )

                answer_entry.select_range(
                    0,
                    tk.END
                )

                answer_entry.focus()

                return

            # ---------------------------------------------
            # CORRECT
            # ---------------------------------------------

            score += points

            score_label.config(
                text=f"SCORE: {score}"
            )

            feedback_label.config(
                text=f"✅ Correct! +{points} points",
                fg="#55dd88"
            )

            # ---------------------------------------------
            # LAST PUZZLE
            # ---------------------------------------------

            if current_puzzle >= len(puzzles) - 1:

                root.after(
                    900,
                    lambda: finish_game("ESCAPED")
                )

                return

            # ---------------------------------------------
            # NEXT PUZZLE
            # ---------------------------------------------

            current_puzzle += 1

            root.after(
                900,
                load_puzzle
            )

        # =================================================
        # ENTER KEY = SUBMIT
        # =================================================

        answer_entry.bind(
            "<Return>",
            lambda event: submit_answer()
        )

        # =================================================
        # USE HINT
        # =================================================

        def use_hint():

            nonlocal score
            nonlocal hint_number

            puzzle_id = puzzles[current_puzzle][0]

            connection = create_connection()

            if connection is None:
                return

            cursor = None

            try:

                cursor = connection.cursor()

                cursor.execute(
                    """
                    SELECT
                        clue_id,
                        clue_text,
                        point_penalty
                    FROM clues
                    WHERE puzzle_id = %s
                    ORDER BY clue_id
                    """,
                    (puzzle_id,)
                )

                clues = cursor.fetchall()

                if not clues:

                    hint_label.config(
                        text=(
                            "💡 No hint has been added "
                            "for this puzzle yet."
                        )
                    )

                    cursor.close()
                    connection.close()

                    return

                if hint_number >= len(clues):

                    hint_label.config(
                        text=(
                            "💡 You've used all available hints "
                            "for this puzzle."
                        )
                    )

                    cursor.close()
                    connection.close()

                    return

                clue_id = clues[hint_number][0]
                clue_text = clues[hint_number][1]
                penalty = clues[hint_number][2]

                # -----------------------------------------
                # DEDUCT SCORE
                # -----------------------------------------

                score = max(
                    0,
                    score - penalty
                )

                score_label.config(
                    text=f"SCORE: {score}"
                )

                # -----------------------------------------
                # RECORD HINT
                # -----------------------------------------

                cursor.execute(
                    """
                    INSERT INTO hints_used
                    (
                        session_id,
                        clue_id,
                        points_lost
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        session_id,
                        clue_id,
                        penalty
                    )
                )

                connection.commit()

                cursor.close()
                connection.close()

                hint_number += 1

                hint_label.config(
                    text=(
                        f"💡 Hint: {clue_text}\n"
                        f"This hint costs {penalty} points."
                    )
                )

            except Exception as error:

                connection.rollback()

                if cursor:
                    cursor.close()

                connection.close()

                messagebox.showerror(
                    "Database Error",
                    str(error)
                )

        # =================================================
        # BUTTONS
        # =================================================

        tk.Button(
            button_frame,
            text="✓ SUBMIT ANSWER",
            font=("Helvetica", 14, "bold"),
            width=20,
            height=2,
            command=submit_answer
        ).pack(
            side="left",
            padx=8
        )

        tk.Button(
            button_frame,
            text="💡 HINT",
            font=("Helvetica", 14, "bold"),
            width=12,
            height=2,
            command=use_hint
        ).pack(
            side="left",
            padx=8
        )

        def forfeit_game():
            confirm = messagebox.askyesno(
                "Forfeit Room",
                "Are you sure you want to forfeit this escape room?\nYour session will be marked as FAILED.",
                parent=root
            )
            if confirm:
                finish_game("FAILED")

        tk.Button(
            button_frame,
            text="🏳️ FORFEIT",
            font=("Helvetica", 14, "bold"),
            width=12,
            height=2,
            command=forfeit_game
        ).pack(
            side="left",
            padx=8
        )

        # =================================================
        # TIMER
        # =================================================

        def update_timer():

            nonlocal time_left
            nonlocal timer_id

            minutes = time_left // 60
            seconds = time_left % 60

            timer_label.config(
                text=f"⏱ {minutes:02d}:{seconds:02d}"
            )

            if time_left <= 0:

                finish_game(
                    "FAILED"
                )

                return

            time_left -= 1

            timer_id = root.after(
                1000,
                update_timer
            )

        # =================================================
        # START
        # =================================================

        load_puzzle()

        update_timer()

    # =====================================================
    # SETUP SCREEN
    # =====================================================

    def show_setup_screen():

        clear_screen()

        setup_frame = tk.Frame(
            root,
            bg="#151515"
        )

        setup_frame.pack(
            fill="both",
            expand=True
        )

        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

        tk.Label(
            setup_frame,
            text="GAME SETUP",
            font=("Helvetica", 42, "bold"),
            fg="white",
            bg="#151515"
        ).pack(
            pady=(70, 10)
        )

        tk.Label(
            setup_frame,
            text="Choose your team and escape room",
            font=("Helvetica", 18),
            fg="#cccccc",
            bg="#151515"
        ).pack(
            pady=(0, 40)
        )

        # -------------------------------------------------
        # TEAM
        # -------------------------------------------------

        tk.Label(
            setup_frame,
            text="SELECT TEAM",
            font=("Helvetica", 18, "bold"),
            fg="white",
            bg="#151515"
        ).pack()

        team_var = tk.StringVar()

        team_dropdown = tk.OptionMenu(
            setup_frame,
            team_var,
            "Loading..."
        )

        team_dropdown.config(
            width=35,
            font=("Helvetica", 15)
        )

        team_dropdown.pack(
            pady=10
        )

        members_label = tk.Label(
            setup_frame,
            text="",
            font=("Helvetica", 15),
            fg="#cccccc",
            bg="#151515"
        )

        members_label.pack(
            pady=5
        )

        team_data = {}

        # -------------------------------------------------
        # LOAD MEMBERS
        # -------------------------------------------------

        def load_members():

            selected_team = team_var.get()

            if selected_team not in team_data:
                return

            connection = create_connection()

            if connection is None:
                return

            try:

                cursor = connection.cursor()

                cursor.execute(
                    """
                    SELECT p.name
                    FROM players p
                    JOIN team_members tm
                        ON p.player_id = tm.player_id
                    WHERE tm.team_id = %s
                    ORDER BY p.name
                    """,
                    (team_data[selected_team],)
                )

                members = cursor.fetchall()

                cursor.close()
                connection.close()

                names = [
                    row[0]
                    for row in members
                ]

                members_label.config(
                    text="Players: " + ", ".join(names)
                )

            except Exception as error:

                messagebox.showerror(
                    "Database Error",
                    str(error)
                )

        # -------------------------------------------------
        # LOAD TEAMS
        # -------------------------------------------------

        def load_teams():

            connection = create_connection()

            if connection is None:
                return

            try:

                cursor = connection.cursor()

                cursor.execute(
                    """
                    SELECT team_id, team_name
                    FROM teams
                    ORDER BY team_name
                    """
                )

                teams = cursor.fetchall()

                cursor.close()
                connection.close()

                menu = team_dropdown["menu"]

                menu.delete(
                    0,
                    "end"
                )

                team_data.clear()

                for team_id, team_name in teams:

                    team_data[team_name] = team_id

                    menu.add_command(
                        label=team_name,
                        command=lambda name=team_name: (
                            team_var.set(name),
                            load_members()
                        )
                    )

                if teams:

                    team_var.set(
                        teams[0][1]
                    )

                    load_members()

            except Exception as error:

                messagebox.showerror(
                    "Database Error",
                    str(error)
                )

        # =================================================
        # CREATE NEW TEAM
        # =================================================

        def show_create_team_screen():

            clear_screen()

            create_frame = tk.Frame(
                root,
                bg="#151515"
            )

            create_frame.pack(
                fill="both",
                expand=True
            )

            tk.Label(
                create_frame,
                text="CREATE NEW TEAM",
                font=("Helvetica", 42, "bold"),
                fg="white",
                bg="#151515"
            ).pack(
                pady=(60, 10)
            )

            tk.Label(
                create_frame,
                text="Enter your team and player details",
                font=("Helvetica", 18),
                fg="#cccccc",
                bg="#151515"
            ).pack(
                pady=(0, 35)
            )

            tk.Label(
                create_frame,
                text="TEAM NAME",
                font=("Helvetica", 16, "bold"),
                fg="white",
                bg="#151515"
            ).pack()

            team_name_entry = tk.Entry(
                create_frame,
                font=("Helvetica", 15),
                width=35
            )

            team_name_entry.pack(
                pady=(8, 20)
            )

            player_entries = []

            for i in range(4):

                tk.Label(
                    create_frame,
                    text=f"PLAYER {i + 1}",
                    font=("Helvetica", 14, "bold"),
                    fg="white",
                    bg="#151515"
                ).pack(
                    pady=(5, 3)
                )

                entry = tk.Entry(
                    create_frame,
                    font=("Helvetica", 14),
                    width=35
                )

                entry.pack(
                    pady=(0, 8)
                )

                player_entries.append(entry)

            # -------------------------------------------------
            # SAVE TEAM
            # -------------------------------------------------

            def save_team():

                team_name = team_name_entry.get().strip()

                player_names = [
                    entry.get().strip()
                    for entry in player_entries
                    if entry.get().strip()
                ]

                if not team_name:

                    messagebox.showwarning(
                        "Missing Team Name",
                        "Please enter a team name."
                    )

                    return

                if len(player_names) < 2:

                    messagebox.showwarning(
                        "Players Required",
                        "Please enter at least 2 players."
                    )

                    return

                connection = create_connection()

                if connection is None:
                    return

                cursor = None

                try:

                    cursor = connection.cursor()

                    cursor.execute(
                        """
                        SELECT team_id
                        FROM teams
                        WHERE team_name = %s
                        """,
                        (team_name,)
                    )

                    if cursor.fetchone():

                        messagebox.showwarning(
                            "Team Exists",
                            "A team with this name already exists."
                        )

                        cursor.close()
                        connection.close()

                        return

                    cursor.execute(
                        """
                        INSERT INTO teams (team_name)
                        VALUES (%s)
                        """,
                        (team_name,)
                    )

                    team_id = cursor.lastrowid

                    for player_name in player_names:

                        cursor.execute(
                            """
                            INSERT INTO players (name)
                            VALUES (%s)
                            """,
                            (player_name,)
                        )

                        player_id = cursor.lastrowid

                        cursor.execute(
                            """
                            INSERT INTO team_members
                            (
                                team_id,
                                player_id
                            )
                            VALUES
                            (
                                %s,
                                %s
                            )
                            """,
                            (
                                team_id,
                                player_id
                            )
                        )

                    connection.commit()

                    cursor.close()
                    connection.close()

                    messagebox.showinfo(
                        "Team Created!",
                        f"{team_name} has been created."
                    )

                    show_setup_screen()

                except Exception as error:

                    connection.rollback()

                    if cursor:
                        cursor.close()

                    connection.close()

                    messagebox.showerror(
                        "Database Error",
                        str(error)
                    )

            # -------------------------------------------------
            # BUTTONS
            # -------------------------------------------------

            button_frame = tk.Frame(
                create_frame,
                bg="#151515"
            )

            button_frame.pack(
                pady=25
            )

            tk.Button(
                button_frame,
                text="CREATE TEAM",
                font=("Helvetica", 15, "bold"),
                width=18,
                height=2,
                command=save_team
            ).pack(
                side="left",
                padx=10
            )

            tk.Button(
                button_frame,
                text="← BACK",
                font=("Helvetica", 15),
                width=12,
                height=2,
                command=show_setup_screen
            ).pack(
                side="left",
                padx=10
            )

            team_name_entry.focus()

        # -------------------------------------------------
        # CREATE TEAM BUTTON
        # -------------------------------------------------

        tk.Button(
            setup_frame,
            text="➕ CREATE NEW TEAM",
            font=("Helvetica", 14, "bold"),
            width=25,
            height=2,
            command=show_create_team_screen
        ).pack(
            pady=15
        )

        # =================================================
        # ROOM
        # =================================================

        tk.Label(
            setup_frame,
            text="SELECT ESCAPE ROOM",
            font=("Helvetica", 18, "bold"),
            fg="white",
            bg="#151515"
        ).pack(
            pady=(30, 5)
        )

        room_var = tk.StringVar()

        room_dropdown = tk.OptionMenu(
            setup_frame,
            room_var,
            "Loading..."
        )

        room_dropdown.config(
            width=35,
            font=("Helvetica", 15)
        )

        room_dropdown.pack(
            pady=10
        )

        room_info = tk.Label(
            setup_frame,
            text="",
            font=("Helvetica", 15),
            fg="#cccccc",
            bg="#151515"
        )

        room_info.pack(
            pady=8
        )

        room_data = {}

        # -------------------------------------------------
        # ROOM INFO
        # -------------------------------------------------

        def update_room_info():

            selected = room_var.get()

            if selected in room_data:

                data = room_data[selected]

                room_info.config(
                    text=(
                        f"Theme: {data['theme']}   |   "
                        f"Difficulty: {data['difficulty']}   |   "
                        f"Time: {data['time_limit']} minutes"
                    )
                )

        # -------------------------------------------------
        # LOAD ROOMS
        # -------------------------------------------------

        def load_rooms():

            connection = create_connection()

            if connection is None:
                return

            try:

                cursor = connection.cursor()

                cursor.execute(
                    """
                    SELECT
                        room_id,
                        room_name,
                        theme,
                        difficulty,
                        time_limit
                    FROM rooms
                    ORDER BY room_id
                    """
                )

                rooms = cursor.fetchall()

                cursor.close()
                connection.close()

                menu = room_dropdown["menu"]

                menu.delete(
                    0,
                    "end"
                )

                room_data.clear()

                for (
                    room_id,
                    room_name,
                    theme,
                    difficulty,
                    time_limit
                ) in rooms:

                    room_data[room_name] = {
                        "room_id": room_id,
                        "theme": theme,
                        "difficulty": difficulty,
                        "time_limit": time_limit
                    }

                    menu.add_command(
                        label=room_name,
                        command=lambda name=room_name: (
                            room_var.set(name),
                            update_room_info()
                        )
                    )

                if rooms:

                    room_var.set(
                        rooms[0][1]
                    )

                    update_room_info()

            except Exception as error:

                messagebox.showerror(
                    "Database Error",
                    str(error)
                )

        # =================================================
        # ENTER ROOM
        # =================================================

        def enter_room():

            selected_team = team_var.get()
            selected_room = room_var.get()

            if selected_team not in team_data:

                messagebox.showwarning(
                    "Select Team",
                    "Please select a team."
                )

                return

            if selected_room not in room_data:

                messagebox.showwarning(
                    "Select Room",
                    "Please select an escape room."
                )

                return

            start_game_session(
                team_data[selected_team],
                room_data[selected_room]["room_id"],
                selected_team,
                selected_room
            )

        # -------------------------------------------------
        # ENTER ROOM
        # -------------------------------------------------

        tk.Button(
            setup_frame,
            text="🔐 ENTER ROOM",
            font=("Helvetica", 18, "bold"),
            width=25,
            height=2,
            command=enter_room
        ).pack(
            pady=25
        )

        # -------------------------------------------------
        # BACK
        # -------------------------------------------------

        tk.Button(
            setup_frame,
            text="← BACK",
            font=("Helvetica", 13),
            width=12,
            command=show_main_menu
        ).pack()

        load_teams()
        load_rooms()

    # =====================================================
    # OPEN SETUP
    # =====================================================

    show_setup_screen()


if __name__ == "__main__":
    import subprocess
    import sys
    script_path = os.path.join(os.path.dirname(__file__), "main.py")
    subprocess.run([sys.executable, script_path])