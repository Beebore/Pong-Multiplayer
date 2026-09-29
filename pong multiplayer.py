import turtle
import math
import socket
import threading
import random
import tkinter as tk
from tkinter import simpledialog


# ============================================================
# PYTHON PONG
# LOCAL + ONLINE MULTIPLAYER
# POINTS + SHOP + COLOURS + PAUSE MENU
# ============================================================


# ============================================================
# SCREEN
# ============================================================

screen = turtle.Screen()
screen.title("Python Pong")
screen.setup(width=1000, height=700)
screen.bgcolor("#080808")
screen.tracer(0)

canvas = screen.getcanvas()
root = canvas.winfo_toplevel()


# ============================================================
# FULLSCREEN
# ============================================================

fullscreen = False


def toggle_fullscreen():

    global fullscreen

    fullscreen = not fullscreen

    try:
        root.attributes("-fullscreen", fullscreen)
    except:
        pass

    screen.update()


screen.onkeypress(toggle_fullscreen, "f")


# ============================================================
# NETWORK SETTINGS
# ============================================================

NETWORK_PORT = 5000

network_socket = None
network_server = None

network_mode = "local"

connected = False

network_lock = threading.Lock()


remote_data = {
    "paddle_a": 0,
    "paddle_b": 0,
    "score_a": 0,
    "score_b": 0,
    "ball_x": 0,
    "ball_y": 0,
    "ball_dx": 0,
    "ball_dy": 0,
    "ball_speed": 5,
    "hit_count": 0,
    "waiting": True,
    "paused": False,
    "game_over": False
}


client_input = {
    "up": False,
    "down": False
}


# ============================================================
# GAME SETTINGS
# ============================================================

PADDLE_SPEED = 8

BALL_START_SPEED = 5
BALL_MAX_SPEED = 12

HITS_PER_SPEED_INCREASE = 5
BALL_SPEED_INCREASE = 1

PADDLE_LIMIT = 225
BALL_LIMIT_Y = 285

WINNING_SCORE = 10

FRAME_TIME = 16


# ============================================================
# GAME VARIABLES
# ============================================================

score_a = 0
score_b = 0

game_started = False
game_over_flag = False
paused = False

ball_waiting = True

ball_speed = BALL_START_SPEED

hit_count = 0

next_direction = 1


# ============================================================
# POINTS
# ============================================================

points_a = 0
points_b = 0


# ============================================================
# SHOP / COLOURS
# ============================================================

# name, colour, price

SHOP_COLOURS = [

    ("BLUE", "#0066FF", 0),
    ("GREEN", "#00CC44", 0),
    ("RED", "#FF2222", 0),
    ("YELLOW", "#FFD900", 50),
    ("PURPLE", "#9933FF", 75),
    ("CYAN", "#00FFFF", 100),
    ("ORANGE", "#FF8800", 125),
    ("PINK", "#FF1493", 150),
    ("LIME", "#66FF00", 175),
    ("MAGENTA", "#FF00FF", 200),
    ("TEAL", "#00B3B3", 225),
    ("GOLD", "#FFB800", 250),
    ("WHITE", "#FFFFFF", 275),
    ("SKY BLUE", "#33CCFF", 300),
    ("DARK PURPLE", "#5511AA", 325),
    ("HOT PINK", "#FF007F", 350),
    ("CORAL", "#FF6F61", 375),
    ("TURQUOISE", "#00E5C3", 400),
    ("LAVENDER", "#B57EDC", 425),
    ("NEON GREEN", "#39FF14", 450),
    ("ELECTRIC BLUE", "#00AAFF", 475),
    ("FIRE", "#FF4500", 500),
    ("ICE", "#BDF3FF", 550),
    ("ROYAL BLUE", "#4169E1", 600),
    ("CRIMSON", "#DC143C", 650),
    ("VIOLET", "#8F00FF", 700),
    ("MINT", "#98FF98", 750),
    ("DEEP PINK", "#FF1493", 800),
    ("NEON YELLOW", "#EEFF00", 900),
    ("RAINBOW", "#FF69B4", 1000)
]


# Player colours

player_a_color = "#0066FF"
player_b_color = "#FF2222"


# Owned colours

owned_a = {
    "#0066FF"
}

owned_b = {
    "#FF2222"
}


# ============================================================
# MENU STATE
# ============================================================

current_screen = "menu"

shop_page = 0

SHOP_ITEMS_PER_PAGE = 10


# ============================================================
# KEY STATES
# ============================================================

keys = {
    "w": False,
    "s": False,
    "up": False,
    "down": False
}


# ============================================================
# MENU TURTLES
# ============================================================

menu_pen = turtle.Turtle()
menu_pen.hideturtle()
menu_pen.penup()
menu_pen.speed(0)


button_pen = turtle.Turtle()
button_pen.hideturtle()
button_pen.penup()
button_pen.speed(0)


# ============================================================
# MENU BUTTONS
# ============================================================

menu_buttons = []


def clear_buttons():

    for button in menu_buttons:

        try:
            button.hideturtle()
        except:
            pass

    menu_buttons.clear()


def make_button(
    x,
    y,
    width,
    height,
    text,
    colour,
    action,
    text_colour="white",
    font_size=13
):

    button = turtle.Turtle()

    button.shape("square")

    button.shapesize(
        stretch_wid=height / 20,
        stretch_len=width / 20
    )

    button.color(colour)

    button.penup()

    button.goto(x, y)

    button.action = action
    button.button_text = text

    menu_buttons.append(button)

    # Text turtle

    label = turtle.Turtle()

    label.hideturtle()
    label.penup()
    label.color(text_colour)

    label.goto(x, y - font_size * 0.45)

    label.write(
        text,
        align="center",
        font=("Courier", font_size, "bold")
    )

    button.label = label

    return button


# ============================================================
# BUTTON CLICK
# ============================================================

def mouse_click(x, y):

    # Game pause menu
    if current_screen == "pause":

        for button in menu_buttons:

            if (
                x >= button.xcor() - 150
                and
                x <= button.xcor() + 150
                and
                y >= button.ycor() - 25
                and
                y <= button.ycor() + 25
            ):

                button.action()
                return

        return


    # Normal menus

    for button in menu_buttons:

        if (
            x >= button.xcor() - 150
            and
            x <= button.xcor() + 150
            and
            y >= button.ycor() - 25
            and
            y <= button.ycor() + 25
        ):

            button.action()
            return


screen.onclick(mouse_click)


# ============================================================
# TEXT
# ============================================================

def write_text(
    x,
    y,
    text,
    colour="white",
    size=14,
    bold=False
):

    style = "bold" if bold else "normal"

    menu_pen.color(colour)

    menu_pen.goto(x, y)

    menu_pen.write(
        text,
        align="center",
        font=("Courier", size, style)
    )


# ============================================================
# CLEAR MENU
# ============================================================

def clear_menu():

    menu_pen.clear()
    button_pen.clear()

    clear_buttons()


# ============================================================
# MAIN MENU
# ============================================================

def show_start_screen():

    global current_screen

    current_screen = "menu"

    clear_menu()

    screen.bgcolor("#080808")

    # Title

    write_text(
        0,
        270,
        "PYTHON PONG",
        "#FFFFFF",
        34,
        True
    )

    write_text(
        0,
        230,
        "FIRST TO 10 WINS",
        "#777777",
        13
    )

    # Points

    write_text(
        -300,
        185,
        "PLAYER A POINTS: " + str(points_a),
        player_a_color,
        12,
        True
    )

    write_text(
        300,
        185,
        "PLAYER B POINTS: " + str(points_b),
        player_b_color,
        12,
        True
    )

    # Selected colours

    write_text(
        -300,
        145,
        "A COLOUR",
        "#AAAAAA",
        10
    )

    write_text(
        -300,
        120,
        colour_name(player_a_color),
        player_a_color,
        16,
        True
    )

    write_text(
        300,
        145,
        "B COLOUR",
        "#AAAAAA",
        10
    )

    write_text(
        300,
        120,
        colour_name(player_b_color),
        player_b_color,
        16,
        True
    )

    # Buttons

    make_button(
        0,
        70,
        300,
        50,
        "START LOCAL GAME",
        "#176BFF",
        start_game
    )

    make_button(
        0,
        10,
        300,
        50,
        "COLOUR SHOP",
        "#7B2CFF",
        show_shop
    )

    make_button(
        0,
        -50,
        300,
        50,
        "HOST ONLINE GAME",
        "#009966",
        start_host_game
    )

    make_button(
        0,
        -110,
        300,
        50,
        "JOIN ONLINE GAME",
        "#0088AA",
        start_join_game
    )

    make_button(
        0,
        -170,
        300,
        50,
        "FULLSCREEN: F",
        "#333333",
        toggle_fullscreen
    )

    # Controls

    write_text(
        0,
        -235,
        "LOCAL",
        "#FFFFFF",
        12,
        True
    )

    write_text(
        0,
        -260,
        "PLAYER A: W / S     PLAYER B: UP / DOWN",
        "#AAAAAA",
        10
    )

    write_text(
        0,
        -285,
        "SPACE = START BALL     P = PAUSE",
        "#AAAAAA",
        10
    )

    screen.update()


# ============================================================
# COLOUR NAME
# ============================================================

def colour_name(colour):

    for name, value, price in SHOP_COLOURS:

        if value == colour:
            return name

    return "UNKNOWN"


# ============================================================
# SHOP
# ============================================================

def show_shop():

    global current_screen
    global shop_page

    current_screen = "shop"

    shop_page = 0

    draw_shop()


def draw_shop():

    clear_menu()

    screen.bgcolor("#080808")

    write_text(
        0,
        285,
        "COLOUR SHOP",
        "#FFFFFF",
        30,
        True
    )

    write_text(
        -300,
        250,
        "PLAYER A: " + str(points_a) + " POINTS",
        player_a_color,
        12,
        True
    )

    write_text(
        300,
        250,
        "PLAYER B: " + str(points_b) + " POINTS",
        player_b_color,
        12,
        True
    )

    start_index = shop_page * SHOP_ITEMS_PER_PAGE

    end_index = min(
        start_index + SHOP_ITEMS_PER_PAGE,
        len(SHOP_COLOURS)
    )

    items = SHOP_COLOURS[start_index:end_index]

    # Left column

    for i in range(5):

        if i >= len(items):
            break

        item = items[i]

        draw_shop_item(
            item,
            -230,
            175 - i * 65
        )

    # Right column

    for i in range(5, len(items)):

        item = items[i]

        draw_shop_item(
            item,
            230,
            175 - (i - 5) * 65
        )

    # Navigation

    if shop_page > 0:

        make_button(
            -250,
            -250,
            220,
            45,
            "< PREVIOUS",
            "#333333",
            previous_shop_page
        )

    if end_index < len(SHOP_COLOURS):

        make_button(
            250,
            -250,
            220,
            45,
            "NEXT >",
            "#333333",
            next_shop_page
        )

    make_button(
        0,
        -250,
        220,
        45,
        "BACK TO MENU",
        "#176BFF",
        show_start_screen
    )

    write_text(
        0,
        -300,
        "Click a colour to buy or equip it",
        "#777777",
        10
    )

    screen.update()


# ============================================================
# SHOP ITEM
# ============================================================

def draw_shop_item(item, x, y):

    name, colour, price = item

    # Colour square

    swatch = turtle.Turtle()

    swatch.shape("square")

    swatch.shapesize(
        stretch_wid=1.8,
        stretch_len=1.8
    )

    swatch.color(colour)

    swatch.penup()

    swatch.goto(
        x - 100,
        y
    )

    menu_buttons.append(swatch)

    swatch.action = lambda c=colour: shop_colour_clicked(c)

    # Text

    owned = (
        colour in owned_a
        or
        colour in owned_b
    )

    write_text(
        x + 10,
        y + 8,
        name,
        colour,
        11,
        True
    )

    if price == 0:

        price_text = "FREE"

    elif owned:

        price_text = "OWNED"

    else:

        price_text = str(price) + " POINTS"

    write_text(
        x + 10,
        y - 12,
        price_text,
        "#AAAAAA",
        9
    )


# ============================================================
# SHOP COLOUR CLICK
# ============================================================

def shop_colour_clicked(colour):

    global player_a_color
    global player_b_color
    global points_a
    global points_b

    # Find item

    item = None

    for data in SHOP_COLOURS:

        if data[1] == colour:

            item = data
            break

    if item is None:
        return

    name, colour, price = item

    # Already owned

    if colour in owned_a and colour in owned_b:

        choose_shop_player(colour)
        return

    # Ask which player

    choose_shop_player(colour)


# ============================================================
# CHOOSE SHOP PLAYER
# ============================================================

def choose_shop_player(colour):

    global points_a
    global points_b
    global player_a_color
    global player_b_color

    item = None

    for data in SHOP_COLOURS:

        if data[1] == colour:

            item = data
            break

    if item is None:
        return

    name, colour, price = item

    # If both already own it, simply equip

    if colour in owned_a and colour in owned_b:

        player_a_color = colour
        player_b_color = colour

        draw_shop()
        return

    # If A owns it, equip A

    if colour in owned_a:

        player_a_color = colour
        draw_shop()
        return

    # If B owns it, equip B

    if colour in owned_b:

        player_b_color = colour
        draw_shop()
        return

    # Otherwise use a simple dialog

    answer = simpledialog.askstring(
        "Buy Colour",
        "Buy " + name + " for " + str(price) +
        " points for Player A or Player B?\n\n"
        "Type A or B.",
        parent=root
    )

    if not answer:
        return

    answer = answer.upper().strip()

    if answer == "A":

        if points_a >= price:

            points_a -= price

            owned_a.add(colour)

            player_a_color = colour

        else:

            show_shop_message(
                "PLAYER A NEEDS " +
                str(price - points_a) +
                " MORE POINTS"
            )

            return

    elif answer == "B":

        if points_b >= price:

            points_b -= price

            owned_b.add(colour)

            player_b_color = colour

        else:

            show_shop_message(
                "PLAYER B NEEDS " +
                str(price - points_b) +
                " MORE POINTS"
            )

            return

    else:

        return

    draw_shop()


# ============================================================
# SHOP MESSAGE
# ============================================================

def show_shop_message(text):

    write_text(
        0,
        -200,
        text,
        "#FF4444",
        11,
        True
    )

    screen.update()


# ============================================================
# SHOP PAGE
# ============================================================

def next_shop_page():

    global shop_page

    max_page = (
        len(SHOP_COLOURS) - 1
    ) // SHOP_ITEMS_PER_PAGE

    if shop_page < max_page:

        shop_page += 1

    draw_shop()


def previous_shop_page():

    global shop_page

    if shop_page > 0:

        shop_page -= 1

    draw_shop()


# ============================================================
# SCOREBOARD
# ============================================================

score_pen = turtle.Turtle()
score_pen.hideturtle()
score_pen.penup()
score_pen.speed(0)


# ============================================================
# MESSAGE
# ============================================================

message_pen = turtle.Turtle()
message_pen.hideturtle()
message_pen.penup()
message_pen.speed(0)


# ============================================================
# PADDLE A
# ============================================================

paddle_a = turtle.Turtle()

paddle_a.shape("square")

paddle_a.color(player_a_color)

paddle_a.shapesize(
    stretch_wid=5,
    stretch_len=1
)

paddle_a.penup()

paddle_a.goto(
    -430,
    0
)


# ============================================================
# PADDLE B
# ============================================================

paddle_b = turtle.Turtle()

paddle_b.shape("square")

paddle_b.color(player_b_color)

paddle_b.shapesize(
    stretch_wid=5,
    stretch_len=1
)

paddle_b.penup()

paddle_b.goto(
    430,
    0
)


# ============================================================
# BALL
# ============================================================

ball = turtle.Turtle()

ball.shape("circle")

ball.color("white")

ball.penup()

ball.goto(
    0,
    0
)

ball.dx = 0
ball.dy = 0


# ============================================================
# SCOREBOARD
# ============================================================

def update_scoreboard():

    score_pen.clear()

    score_pen.color("white")

    score_pen.goto(
        0,
        300
    )

    score_pen.write(
        "A: {}     B: {}     SPEED: {:.1f}     HITS: {}".format(
            score_a,
            score_b,
            ball_speed,
            hit_count
        ),
        align="center",
        font=("Courier", 13, "normal")
    )

    score_pen.goto(
        -420,
        270
    )

    score_pen.color(player_a_color)

    score_pen.write(
        "POINTS: " + str(points_a),
        align="left",
        font=("Courier", 11, "bold")
    )

    score_pen.goto(
        420,
        270
    )

    score_pen.color(player_b_color)

    score_pen.write(
        "POINTS: " + str(points_b),
        align="right",
        font=("Courier", 11, "bold")
    )


# ============================================================
# MESSAGE
# ============================================================

def clear_message():

    message_pen.clear()


def show_message(
    text,
    colour="white",
    size=18
):

    message_pen.clear()

    message_pen.color(colour)

    message_pen.goto(
        0,
        0
    )

    message_pen.write(
        text,
        align="center",
        font=("Courier", size, "bold")
    )


# ============================================================
# MOVE PADDLES
# ============================================================

def move_paddles():

    # LOCAL

    if network_mode == "local":

        if keys["w"]:

            paddle_a.sety(
                min(
                    PADDLE_LIMIT,
                    paddle_a.ycor() + PADDLE_SPEED
                )
            )

        if keys["s"]:

            paddle_a.sety(
                max(
                    -PADDLE_LIMIT,
                    paddle_a.ycor() - PADDLE_SPEED
                )
            )

        if keys["up"]:

            paddle_b.sety(
                min(
                    PADDLE_LIMIT,
                    paddle_b.ycor() + PADDLE_SPEED
                )
            )

        if keys["down"]:

            paddle_b.sety(
                max(
                    -PADDLE_LIMIT,
                    paddle_b.ycor() - PADDLE_SPEED
                )
            )

    # HOST

    elif network_mode == "host":

        if keys["w"]:

            paddle_a.sety(
                min(
                    PADDLE_LIMIT,
                    paddle_a.ycor() + PADDLE_SPEED
                )
            )

        if keys["s"]:

            paddle_a.sety(
                max(
                    -PADDLE_LIMIT,
                    paddle_a.ycor() - PADDLE_SPEED
                )
            )

        with network_lock:

            remote_up = client_input["up"]
            remote_down = client_input["down"]

        if remote_up:

            paddle_b.sety(
                min(
                    PADDLE_LIMIT,
                    paddle_b.ycor() + PADDLE_SPEED
                )
            )

        if remote_down:

            paddle_b.sety(
                max(
                    -PADDLE_LIMIT,
                    paddle_b.ycor() - PADDLE_SPEED
                )
            )

    # CLIENT

    elif network_mode == "client":

        if keys["up"]:

            paddle_b.sety(
                min(
                    PADDLE_LIMIT,
                    paddle_b.ycor() + PADDLE_SPEED
                )
            )

        if keys["down"]:

            paddle_b.sety(
                max(
                    -PADDLE_LIMIT,
                    paddle_b.ycor() - PADDLE_SPEED
                )
            )

        send_client_input()


# ============================================================
# KEYBOARD
# ============================================================

def press_w():
    keys["w"] = True


def release_w():
    keys["w"] = False


def press_s():
    keys["s"] = True


def release_s():
    keys["s"] = False


def press_up():
    keys["up"] = True


def release_up():
    keys["up"] = False


def press_down():
    keys["down"] = True


def release_down():
    keys["down"] = False


screen.listen()

screen.onkeypress(press_w, "w")
screen.onkeyrelease(release_w, "w")

screen.onkeypress(press_s, "s")
screen.onkeyrelease(release_s, "s")

screen.onkeypress(press_up, "Up")
screen.onkeyrelease(release_up, "Up")

screen.onkeypress(press_down, "Down")
screen.onkeyrelease(release_down, "Down")


# ============================================================
# BALL SPEED
# ============================================================

def set_ball_speed(speed):

    current_speed = math.sqrt(
        ball.dx * ball.dx +
        ball.dy * ball.dy
    )

    if current_speed == 0:
        return

    multiplier = speed / current_speed

    ball.dx *= multiplier
    ball.dy *= multiplier


def increase_ball_speed():

    global ball_speed

    ball_speed += BALL_SPEED_INCREASE

    if ball_speed > BALL_MAX_SPEED:

        ball_speed = BALL_MAX_SPEED

    set_ball_speed(ball_speed)


# ============================================================
# PADDLE HIT
# ============================================================

def register_paddle_hit():

    global hit_count

    hit_count += 1

    if (
        hit_count % HITS_PER_SPEED_INCREASE == 0
    ):

        increase_ball_speed()

    update_scoreboard()


# ============================================================
# RESET BALL
# ============================================================

def reset_ball():

    global ball_waiting

    ball.goto(
        0,
        0
    )

    ball.dx = 0
    ball.dy = 0

    ball.color("white")

    ball_waiting = True

    update_scoreboard()

    show_message(
        "PRESS SPACE TO CONTINUE",
        "white",
        18
    )


# ============================================================
# LAUNCH BALL
# ============================================================

def launch_ball():

    global ball_waiting

    if not game_started:
        return

    if game_over_flag:
        return

    if paused:
        return

    if not ball_waiting:
        return

    if network_mode == "client":

        send_network_message("LAUNCH")

        return

    ball_waiting = False

    clear_message()

    horizontal_speed = ball_speed * 0.8

    vertical_speed = ball_speed * 0.6

    ball.dx = (
        horizontal_speed *
        next_direction
    )

    ball.dy = vertical_speed


screen.onkeypress(
    launch_ball,
    "space"
)


# ============================================================
# NETWORK SEND
# ============================================================

def send_network_message(message):

    global network_socket

    if network_socket is None:
        return

    try:

        network_socket.sendall(
            (message + "\n").encode()
        )

    except:
        pass


# ============================================================
# CLIENT INPUT
# ============================================================

def send_client_input():

    if network_mode != "client":
        return

    message = "INPUT|{}|{}".format(
        int(keys["up"]),
        int(keys["down"])
    )

    send_network_message(message)


# ============================================================
# RECEIVE LINE
# ============================================================

def receive_line(sock):

    data = b""

    try:

        while True:

            character = sock.recv(1)

            if not character:
                return None

            if character == b"\n":
                break

            data += character

        return data.decode().strip()

    except:

        return None


# ============================================================
# HOST SERVER
# ============================================================

def host_server(password):

    global network_server
    global network_socket
    global connected

    try:

        network_server = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        network_server.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        network_server.bind(
            ("0.0.0.0", NETWORK_PORT)
        )

        network_server.listen(1)

        client, address = network_server.accept()

        network_socket = client

        received = receive_line(client)

        if received != "PASSWORD|" + password:

            client.sendall(
                b"WRONG_PASSWORD\n"
            )

            client.close()

            network_socket = None

            return

        client.sendall(
            b"PASSWORD_OK\n"
        )

        connected = True

        send_network_message(
            "CONNECTED"
        )

        show_message(
            "PLAYER CONNECTED!",
            "#00FF66",
            18
        )

        while connected:

            line = receive_line(client)

            if line is None:
                break

            handle_client_message(line)

    except Exception as error:

        print(
            "Host networking error:",
            error
        )

    connected = False


# ============================================================
# CLIENT MESSAGE HANDLER
# ============================================================

def handle_client_message(line):

    global client_input
    global ball_waiting
    global paused

    if line.startswith("INPUT|"):

        parts = line.split("|")

        if len(parts) >= 3:

            with network_lock:

                client_input["up"] = (
                    parts[1] == "1"
                )

                client_input["down"] = (
                    parts[2] == "1"
                )

        return

    if line == "LAUNCH":

        if ball_waiting and not paused:

            launch_ball()

        return

    if line == "PAUSE":

        if (
            game_started
            and
            not game_over_flag
            and
            not ball_waiting
        ):

            paused = not paused

        return

    if line == "RESTART":

        if game_over_flag:

            restart_game()

        return


# ============================================================
# SEND GAME STATE
# ============================================================

def send_game_state():

    if network_mode != "host":
        return

    if not connected:
        return

    message = (
        "STATE|"
        + str(round(paddle_a.ycor(), 2))
        + "|"
        + str(round(paddle_b.ycor(), 2))
        + "|"
        + str(score_a)
        + "|"
        + str(score_b)
        + "|"
        + str(round(ball.xcor(), 2))
        + "|"
        + str(round(ball.ycor(), 2))
        + "|"
        + str(round(ball.dx, 4))
        + "|"
        + str(round(ball.dy, 4))
        + "|"
        + str(ball_speed)
        + "|"
        + str(hit_count)
        + "|"
        + str(int(ball_waiting))
        + "|"
        + str(int(paused))
        + "|"
        + str(int(game_over_flag))
        + "|"
        + str(points_a)
        + "|"
        + str(points_b)
    )

    send_network_message(
        message
    )


# ============================================================
# APPLY NETWORK STATE
# ============================================================

def apply_network_state():

    if network_mode != "client":
        return

    with network_lock:

        data = remote_data.copy()

    paddle_a.sety(
        data["paddle_a"]
    )

    paddle_b.sety(
        data["paddle_b"]
    )

    ball.goto(
        data["ball_x"],
        data["ball_y"]
    )

    ball.dx = data["ball_dx"]
    ball.dy = data["ball_dy"]

    ball_waiting = data["waiting"]

    update_scoreboard()

    if data["paused"]:

        show_message(
            "PAUSED",
            "white",
            22
        )

    elif data["waiting"]:

        if not data["game_over"]:

            show_message(
                "PRESS SPACE TO START",
                "white",
                18
            )

    else:

        clear_message()


# ============================================================
# CLIENT NETWORK THREAD
# ============================================================

def client_receive_thread(sock):

    global connected

    while connected:

        line = receive_line(sock)

        if line is None:

            connected = False

            break

        if line == "CONNECTED":

            continue

        if line.startswith("STATE|"):

            parts = line.split("|")

            if len(parts) >= 17:

                try:

                    with network_lock:

                        remote_data["paddle_a"] = float(parts[1])
                        remote_data["paddle_b"] = float(parts[2])

                        remote_data["score_a"] = int(parts[3])
                        remote_data["score_b"] = int(parts[4])

                        remote_data["ball_x"] = float(parts[5])
                        remote_data["ball_y"] = float(parts[6])

                        remote_data["ball_dx"] = float(parts[7])
                        remote_data["ball_dy"] = float(parts[8])

                        remote_data["ball_speed"] = float(parts[9])

                        remote_data["hit_count"] = int(parts[10])

                        remote_data["waiting"] = (
                            parts[11] == "1"
                        )

                        remote_data["paused"] = (
                            parts[12] == "1"
                        )

                        remote_data["game_over"] = (
                            parts[13] == "1"
                        )

                        remote_data["points_a"] = int(parts[14])
                        remote_data["points_b"] = int(parts[15])

                except:
                    pass


# ============================================================
# GET IP
# ============================================================

def get_local_ip():

    try:

        temp_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        temp_socket.connect(
            ("8.8.8.8", 80)
        )

        ip = temp_socket.getsockname()[0]

        temp_socket.close()

        return ip

    except:

        return "127.0.0.1"


# ============================================================
# PASSWORD
# ============================================================

def generate_password():

    return str(
        random.randint(
            100000,
            999999
        )
    )


# ============================================================
# HOST GAME
# ============================================================

def start_host_game():

    global game_started
    global game_over_flag
    global paused
    global score_a
    global score_b
    global ball_speed
    global hit_count
    global ball_waiting
    global next_direction
    global network_mode
    global connected

    if game_started:
        return

    password = generate_password()

    network_mode = "host"

    game_started = True
    game_over_flag = False
    paused = False

    score_a = 0
    score_b = 0

    ball_speed = BALL_START_SPEED
    hit_count = 0

    next_direction = 1
    ball_waiting = True

    connected = False

    clear_menu()

    paddle_a.color(
        player_a_color
    )

    paddle_b.color(
        player_b_color
    )

    paddle_a.goto(
        -430,
        0
    )

    paddle_b.goto(
        430,
        0
    )

    ball.goto(
        0,
        0
    )

    ball.dx = 0
    ball.dy = 0

    update_scoreboard()

    ip = get_local_ip()

    show_message(
        "HOST GAME\n\n"
        "IP: " + ip +
        "\nPASSWORD: " + password +
        "\n\nWaiting for player...",
        "#00FFFF",
        16
    )

    screen.update()

    thread = threading.Thread(
        target=host_server,
        args=(password,),
        daemon=True
    )

    thread.start()


# ============================================================
# JOIN GAME
# ============================================================

def start_join_game():

    global game_started
    global game_over_flag
    global paused
    global score_a
    global score_b
    global ball_speed
    global hit_count
    global ball_waiting
    global network_mode
    global network_socket
    global connected

    if game_started:
        return

    host_ip = simpledialog.askstring(
        "Join Pong",
        "Enter the HOST IP address:",
        parent=root
    )

    if not host_ip:
        return

    password = simpledialog.askstring(
        "Join Pong",
        "Enter the 6-digit password:",
        parent=root
    )

    if not password:
        return

    network_mode = "client"

    clear_menu()

    show_message(
        "CONNECTING...",
        "#00FFFF",
        18
    )

    screen.update()

    try:

        client = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        client.settimeout(8)

        client.connect(
            (
                host_ip,
                NETWORK_PORT
            )
        )

        client.sendall(
            (
                "PASSWORD|" +
                password +
                "\n"
            ).encode()
        )

        response = receive_line(client)

        if response != "PASSWORD_OK":

            client.close()

            network_mode = "local"

            show_message(
                "WRONG PASSWORD",
                "#FF3333",
                18
            )

            screen.ontimer(
                show_start_screen,
                2000
            )

            return

        client.settimeout(None)

        network_socket = client

        connected = True

        game_started = True
        game_over_flag = False
        paused = False

        score_a = 0
        score_b = 0

        ball_speed = BALL_START_SPEED
        hit_count = 0

        ball_waiting = True

        paddle_a.goto(
            -430,
            0
        )

        paddle_b.goto(
            430,
            0
        )

        paddle_a.color(
            player_a_color
        )

        paddle_b.color(
            player_b_color
        )

        thread = threading.Thread(
            target=client_receive_thread,
            args=(client,),
            daemon=True
        )

        thread.start()

        show_message(
            "CONNECTED!\n\n"
            "YOU ARE PLAYER B\n\n"
            "PRESS SPACE TO START",
            "#00FF66",
            16
        )

    except Exception as error:

        print(
            "Join error:",
            error
        )

        network_mode = "local"

        show_message(
            "COULD NOT CONNECT",
            "#FF3333",
            18
        )

        screen.ontimer(
            show_start_screen,
            2000
        )


# ============================================================
# START LOCAL GAME
# ============================================================

def start_game():

    global game_started
    global game_over_flag
    global paused
    global score_a
    global score_b
    global ball_speed
    global hit_count
    global ball_waiting
    global next_direction
    global network_mode

    if game_started:
        return

    network_mode = "local"

    game_started = True
    game_over_flag = False
    paused = False

    score_a = 0
    score_b = 0

    ball_speed = BALL_START_SPEED
    hit_count = 0

    next_direction = 1

    ball_waiting = True

    clear_menu()

    paddle_a.color(
        player_a_color
    )

    paddle_b.color(
        player_b_color
    )

    paddle_a.goto(
        -430,
        0
    )

    paddle_b.goto(
        430,
        0
    )

    ball.goto(
        0,
        0
    )

    ball.dx = 0
    ball.dy = 0

    ball.color("white")

    update_scoreboard()

    show_message(
        "PRESS SPACE TO START",
        "white",
        18
    )

    screen.update()


screen.onkeypress(
    start_game,
    "Return"
)


# ============================================================
# PAUSE MENU
# ============================================================

def show_pause_menu():

    global current_screen

    current_screen = "pause"

    clear_menu()

    screen.bgcolor("#080808")

    write_text(
        0,
        200,
        "GAME PAUSED",
        "#FFFFFF",
        30,
        True
    )

    write_text(
        0,
        160,
        "THE GAME IS PAUSED",
        "#777777",
        11
    )

    make_button(
        0,
        80,
        300,
        50,
        "RESUME",
        "#009966",
        resume_game
    )

    make_button(
        0,
        20,
        300,
        50,
        "COLOUR SHOP",
        "#7B2CFF",
        pause_open_shop
    )

    make_button(
        0,
        -40,
        300,
        50,
        "BACK TO MENU",
        "#176BFF",
        back_to_menu
    )

    make_button(
        0,
        -100,
        300,
        50,
        "FULLSCREEN: F",
        "#333333",
        toggle_fullscreen
    )

    write_text(
        0,
        -180,
        "PRESS P TO RESUME",
        "#777777",
        11
    )

    screen.update()


# ============================================================
# PAUSE
# ============================================================

def toggle_pause():

    global paused

    if not game_started:
        return

    if game_over_flag:
        return

    if ball_waiting:
        return

    if network_mode == "client":

        send_network_message(
            "PAUSE"
        )

        return

    paused = not paused

    if paused:

        show_pause_menu()

    else:

        resume_game()


def resume_game():

    global paused
    global current_screen

    paused = False

    current_screen = "game"

    clear_menu()

    clear_message()

    update_scoreboard()


screen.onkeypress(
    toggle_pause,
    "p"
)


# ============================================================
# SHOP FROM PAUSE
# ============================================================

def pause_open_shop():

    global current_screen

    current_screen = "shop_pause"

    clear_menu()

    screen.bgcolor("#080808")

    write_text(
        0,
        285,
        "COLOUR SHOP",
        "#FFFFFF",
        30,
        True
    )

    write_text(
        -300,
        250,
        "PLAYER A: " + str(points_a),
        player_a_color,
        12,
        True
    )

    write_text(
        300,
        250,
        "PLAYER B: " + str(points_b),
        player_b_color,
        12,
        True
    )

    start_index = shop_page * SHOP_ITEMS_PER_PAGE

    end_index = min(
        start_index + SHOP_ITEMS_PER_PAGE,
        len(SHOP_COLOURS)
    )

    items = SHOP_COLOURS[start_index:end_index]

    for i in range(5):

        if i >= len(items):
            break

        draw_shop_item(
            items[i],
            -230,
            175 - i * 65
        )

    for i in range(5, len(items)):

        draw_shop_item(
            items[i],
            230,
            175 - (i - 5) * 65
        )

    make_button(
        0,
        -250,
        220,
        45,
        "BACK TO PAUSE",
        "#176BFF",
        show_pause_menu
    )

    screen.update()


# ============================================================
# BACK TO MENU
# ============================================================

def back_to_menu():

    global game_started
    global paused
    global game_over_flag
    global current_screen
    global network_mode

    game_started = False
    paused = False
    game_over_flag = False

    network_mode = "local"

    ball.dx = 0
    ball.dy = 0

    ball.goto(
        0,
        0
    )

    score_pen.clear()
    message_pen.clear()

    show_start_screen()


# ============================================================
# GAME OVER
# ============================================================

def game_over():

    global game_started
    global game_over_flag
    global ball_waiting
    global points_a
    global points_b

    game_started = False

    game_over_flag = True

    ball_waiting = False

    ball.dx = 0
    ball.dy = 0

    score_pen.clear()
    message_pen.clear()

    # Award points

    if score_a >= WINNING_SCORE:

        points_a += 100

        winner = "PLAYER A"
        winner_colour = player_a_color

    else:

        points_b += 100

        winner = "PLAYER B"
        winner_colour = player_b_color

    score_pen.color(
        winner_colour
    )

    score_pen.goto(
        0,
        80
    )

    score_pen.write(
        winner + " WINS!",
        align="center",
        font=("Courier", 30, "bold")
    )

    score_pen.color("white")

    score_pen.goto(
        0,
        35
    )

    score_pen.write(
        "FINAL SCORE: {} - {}".format(
            score_a,
            score_b
        ),
        align="center",
        font=("Courier", 16, "normal")
    )

    score_pen.goto(
        0,
        -10
    )

    score_pen.write(
        "+100 POINTS",
        align="center",
        font=("Courier", 16, "bold")
    )

    score_pen.goto(
        0,
        -60
    )

    score_pen.write(
        "PRESS R TO PLAY AGAIN",
        align="center",
        font=("Courier", 14, "bold")
    )

    score_pen.goto(
        0,
        -100
    )

    score_pen.write(
        "PRESS M FOR MENU",
        align="center",
        font=("Courier", 12, "normal")
    )

    screen.update()


# ============================================================
# RESTART
# ============================================================

def restart_game():

    global game_started
    global game_over_flag
    global paused
    global score_a
    global score_b
    global ball_speed
    global hit_count
    global ball_waiting
    global next_direction

    if not game_over_flag:
        return

    if network_mode == "client":

        send_network_message(
            "RESTART"
        )

        return

    score_a = 0
    score_b = 0

    ball_speed = BALL_START_SPEED
    hit_count = 0

    game_started = True
    game_over_flag = False
    paused = False

    next_direction = 1

    ball_waiting = True

    paddle_a.goto(
        -430,
        0
    )

    paddle_b.goto(
        430,
        0
    )

    ball.goto(
        0,
        0
    )

    ball.dx = 0
    ball.dy = 0

    score_pen.clear()

    update_scoreboard()

    show_message(
        "PRESS SPACE TO START",
        "white",
        18
    )


screen.onkeypress(
    restart_game,
    "r"
)


# ============================================================
# MENU KEY
# ============================================================

def menu_key():

    if game_over_flag:

        back_to_menu()


screen.onkeypress(
    menu_key,
    "m"
)


# ============================================================
# PADDLE COLLISION
# ============================================================

def check_paddle_collision():

    # RIGHT

    if ball.dx > 0:

        if ball.xcor() >= 405:

            paddle_top = (
                paddle_b.ycor() + 55
            )

            paddle_bottom = (
                paddle_b.ycor() - 55
            )

            if (
                paddle_bottom
                <= ball.ycor()
                <= paddle_top
            ):

                ball.setx(404)

                ball.dx = -abs(
                    ball.dx
                )

                ball.color(
                    player_b_color
                )

                difference = (
                    ball.ycor()
                    -
                    paddle_b.ycor()
                )

                ball.dy += (
                    difference * 0.08
                )

                set_ball_speed(
                    ball_speed
                )

                register_paddle_hit()

    # LEFT

    elif ball.dx < 0:

        if ball.xcor() <= -405:

            paddle_top = (
                paddle_a.ycor() + 55
            )

            paddle_bottom = (
                paddle_a.ycor() - 55
            )

            if (
                paddle_bottom
                <= ball.ycor()
                <= paddle_top
            ):

                ball.setx(-404)

                ball.dx = abs(
                    ball.dx
                )

                ball.color(
                    player_a_color
                )

                difference = (
                    ball.ycor()
                    -
                    paddle_a.ycor()
                )

                ball.dy += (
                    difference * 0.08
                )

                set_ball_speed(
                    ball_speed
                )

                register_paddle_hit()


# ============================================================
# WALL COLLISION
# ============================================================

def check_wall_collision():

    if ball.ycor() >= BALL_LIMIT_Y:

        ball.sety(
            BALL_LIMIT_Y
        )

        ball.dy = -abs(
            ball.dy
        )

    elif ball.ycor() <= -BALL_LIMIT_Y:

        ball.sety(
            -BALL_LIMIT_Y
        )

        ball.dy = abs(
            ball.dy
        )


# ============================================================
# SCORING
# ============================================================

def check_score():

    global score_a
    global score_b
    global next_direction
    global points_a
    global points_b

    if ball.xcor() > 500:

        score_a += 1

        # Score points for the point won

        points_a += 10

        next_direction = -1

        if score_a >= WINNING_SCORE:

            game_over()

            return

        reset_ball()

        return

    if ball.xcor() < -500:

        score_b += 1

        points_b += 10

        next_direction = 1

        if score_b >= WINNING_SCORE:

            game_over()

            return

        reset_ball()


# ============================================================
# NETWORK UPDATE
# ============================================================

def network_update():

    if network_mode == "host":

        send_game_state()

    elif network_mode == "client":

        apply_network_state()

    screen.ontimer(
        network_update,
        30
    )


# ============================================================
# MAIN GAME LOOP
# ============================================================

def game_loop():

    global paused

    if (
        game_started
        and
        not game_over_flag
        and
        current_screen == "game"
    ):

        if not paused:

            move_paddles()

            if (
                network_mode != "client"
                and
                not ball_waiting
            ):

                ball.setx(
                    ball.xcor()
                    +
                    ball.dx
                )

                ball.sety(
                    ball.ycor()
                    +
                    ball.dy
                )

                check_wall_collision()

                check_paddle_collision()

                check_score()

    screen.update()

    screen.ontimer(
        game_loop,
        FRAME_TIME
    )


# ============================================================
# FIX GAME SCREEN STATE
# ============================================================

def force_game_screen():

    global current_screen

    if game_started and not paused:

        current_screen = "game"


# ============================================================
# BUTTON OVERRIDE FOR STARTING GAME
# ============================================================

old_start_game = start_game


def start_game():

    global current_screen

    old_start_game()

    current_screen = "game"

    screen.update()


# ============================================================
# OVERRIDE HOST
# ============================================================

old_start_host_game = start_host_game


def start_host_game():

    global current_screen

    old_start_host_game()

    current_screen = "game"

    screen.update()


# ============================================================
# OVERRIDE JOIN
# ============================================================

old_start_join_game = start_join_game


def start_join_game():

    global current_screen

    old_start_join_game()

    if game_started:

        current_screen = "game"

    screen.update()


# ============================================================
# SAFE INITIAL START
# ============================================================

screen.listen()

show_start_screen()

network_update()

game_loop()

screen.mainloop()
