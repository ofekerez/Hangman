import pygame
import math
import random
from threading import Thread
from socket import socket

# Name: Ofek Erez
# Date of creation: 30/7/21
# Project name: PYGAME summer project - Hangman with sockets implementation


# Set up display
pygame.init()
WIDTH, HEIGHT = 800, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hangman Game! Server Side!")

# BUTTON VARIABLES
RADIUS = 20
GAP = 15
letters = []
start_x = round((WIDTH - (RADIUS * 2 + GAP) * 13) / 2)
start_y = 400
A = 65
for i in range(26):
    x = start_x + GAP * 2 + ((RADIUS * 2 + GAP) * (i % 13))
    y = start_y + ((i // 13) * (GAP + RADIUS * 2))
    letters.append([x, y, chr(A + i), True])

# Fonts
LETTER_FONT = pygame.font.SysFont('comicsans', 40)
WORD_FONT = pygame.font.SysFont('comicsans', 60)
TITLE_FONT = pygame.font.SysFont('comicsans', 70)
# Loading the images
images = []
for i in range(7):
    images.append(pygame.image.load(f'images/hangman{i}.png'))

# GAME VARIABLES
words = ['PYTHON', 'PYGAME', 'CYBER', 'PACKET', 'GAME', 'NETWORK', 'SOCKET', 'SECURITY', 'DEVELOPER', 'HANGMAN']
word = random.choice(words)
guessed = []
running = True
hangman_status = 0

# COLORS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class Server(Thread):  # A thread is a sequence of instructions within a function/process that can be executed
    # independently of other codes. I used threading in order to have my network independent of the game,
    # meaning that the client and server can transfer messages between them all along the game and not necessarily in
    # turns.
    PORT = 8100
    WINNING_MESSAGE = b'YOU WON ! '  # Casting to bytes
    LOSING_MESSAGE = b'YOU LOST !'

    def __init__(self):
        """The server object constructor, it creates a new socket and binds it to the PORT and IP address. The super(
        ) function returns a proxy object (a temporary object of the superclass) which is in this case thread,
        that allows us to access methods of the base class(threading). """
        super(Server, self).__init__()
        self.socket = socket()
        self.socket.bind(('0.0.0.0', self.PORT))
        self.socket.listen(1)

        self.listening = True  # A variable that determines whether or not the server is able to accept requests.

        self.client_socket, self.client_address = self.socket.accept()
        self.commands = {
            self.WINNING_MESSAGE: self.win,
            self.LOSING_MESSAGE: self.lose
        }

    def win(self, flag=False):
        """The function is called whenever the server wins, the flag is determining which way did the server win: by
        guessing the word correctly, or by the loss of the client. if the flag is True thus the server has guessed the
        word correctly, otherwise, the client has lost and ended the game. It is crucial to distinguish between these
        two situations to determine whether or not the server has to send the client if he won or lost.
        if the client lost, and because of it the server won, there is no need to send the client that he lost,
        because his lose function has been already executed on his side."""
        if flag:
            self.send_lose()
        global running
        running = False
        self.listening = False
        display_message('YOU WON ! ')

    def lose(self, flag=False):
        """The function is called whenever the server loses, the flag is determining which way did the server lose:
        by using all his wrong guesses, or by the correct guess of the client. if the flag is True thus the server
        has used all his guesses, otherwise, the client has won and ended the game. It is crucial to distinguish
        between these two situations do determine whether or not the server has to send the client if he won or lost.
        if the client won, and because of it the server lost, there is no need to send the client that he won,
        because his win function has been already executed on his side. """
        if flag:
            self.send_win()
        global running
        running = False
        self.listening = False
        display_message('YOU LOST!')

    def run(self):
        """The running loop of the server, listening to requests at any time as long self.listening is True,
        it receives messages from the client and calls the functions when winning or losing accordingly.
        """
        global running
        while self.listening:
            data = self.client_socket.recv(10)
            self.commands.get(data, lambda: None)()

    def send_win(self):
        """The function sends to the client a message that he won."""
        self.client_socket.send(self.WINNING_MESSAGE)

    def send_lose(self):
        """The function sends to the client a message that he lost."""
        self.client_socket.send(self.LOSING_MESSAGE)


def draw():
    """The function receives the hangman current status and draws all the labels, images and letters already guessed
    right. """
    screen.fill(WHITE)
    # draw title
    title = TITLE_FONT.render('Network Hangman', 1, BLACK)
    screen.blit(title, (WIDTH / 2 - title.get_width() / 2, 20))
    # draw word
    display_word = ""
    for letter in word:
        if letter in guessed:
            display_word += letter + ' '
        else:
            display_word += '_ '
    text = WORD_FONT.render(display_word, 1, BLACK)
    screen.blit(text, (400, 200))
    # draw buttons
    for letter in letters:
        x, y, ltr, visible = letter
        if visible:
            pygame.draw.circle(screen, BLACK, (x, y), RADIUS, 3)
            text = LETTER_FONT.render(ltr, 1, BLACK)
            screen.blit(text, (x - text.get_width() / 2, y - text.get_height() / 2))
    screen.blit(images[hangman_status], (150, 100))
    pygame.display.update()
    """ The function draws circle buttons and the hangman at it's  starting point."""


def display_message(message: str):
    """The function receives a message and displays it as a label on the screen."""
    pygame.time.delay(1000)
    screen.fill(WHITE)
    text = WORD_FONT.render(message, 1, BLACK)
    screen.blit(text, (WIDTH / 2 - text.get_width() / 2, HEIGHT / 2 - text.get_height() / 2))
    pygame.display.update()
    pygame.time.delay(3000)
    quit()


def main():
    """The function is the main function of the game, containing the game loop, and determines whether you have won
    or lost the game. """
    global hangman_status, running
    REFRESH_RATE = 60
    clock = pygame.time.Clock()

    # Setting up the game loop
    while running:
        clock.tick(REFRESH_RATE)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
                running = False
                server.send_win()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for letter in letters:
                    x, y, ltr, visible = letter
                    if visible:
                        dis = math.sqrt((x - mouse_x) ** 2 + (y - mouse_y) ** 2)
                        if dis < RADIUS:
                            letter[3] = False
                            guessed.append(ltr)
                            if ltr not in word:
                                hangman_status += 1
        draw()
        count = 0
        for letter in word:
            if letter not in guessed and hangman_status == 6:
                server.lose(flag=True)
            elif letter in guessed:
                count += 1
        if count == len(word):
            server.win(flag=True)


server = Server()
server.start()
th = Thread(target=main())
th.start()
