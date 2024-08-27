import pygame
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60

WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Poker')

# Load card images
card_images = {}
for suit in ['diamonds', 'hearts', 'clubs', 'spades']:
    for rank in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']:
        card_name = f'{suit}/{rank}.png'
        card_images[card_name] = pygame.image.load(f'card/{card_name}')

# Load background image
bg_img = pygame.image.load('card/table.png')
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

class Card:
    suits = ['diamonds', 'hearts', 'clubs', 'spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']

    def __init__(self, suit=0, rank=0):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{Card.suits[self.suit]}/{Card.ranks[self.rank]}"

    def image_name(self):
        return f"{Card.suits[self.suit]}/{Card.ranks[self.rank]}.png"


class Deck:
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in range(4) for rank in range(13)]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        if self.cards:
            return self.cards.pop()
        else:
            raise ValueError("Error: The deck is empty.")


class Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)


class Player:
    def __init__(self, name, chips=1000):
        self.name = name
        self.chips = chips
        self.hand = Hand()

    def bet(self, amount):
        if amount <= self.chips:
            self.chips -= amount
            return amount
        else:
            return 0

    def fold(self):
        print(f"{self.name} folds.")

    def raise_bet(self, amount):
        if amount <= self.chips:
            self.chips -= amount
            print(f"{self.name} raises the bet by {amount}.")
            return amount
        else:
            print("Not enough chips to raise.")
            return 0

    def check(self):
        print(f"{self.name} checks.")


class Bot(Player):
    def __init__(self, name):
        super().__init__(name)


class PokerGame:
    def __init__(self, players):
        self.players = players
        self.deck = Deck()
        self.community_cards = []
        self.deal_button_rect = pygame.Rect(380, HEIGHT - 50, 90, 40) 
        self.deal_button_clicked = False  
        self.round_started = False  

    def deal_hands(self):
        for player in self.players:
            player.hand.cards.clear()  
            for _ in range(2):
                player.hand.add_card(self.deck.draw())

    def deal_community_cards(self, num_cards):
        for _ in range(num_cards):
            self.community_cards.append(self.deck.draw())

    def start_new_round(self):
        self.deck.shuffle()
        self.community_cards.clear()

        print("New round:")
        self.deal_hands()  
        self.deal_community_cards(3)  

        print("Community cards:", [str(card) for card in self.community_cards])

    def draw(self):
        win.blit(bg_img, (0, 0))  

        self.draw_player_hands()
        self.draw_community_cards()

        self.draw_button("Fold", (50, HEIGHT - 50, 90, 40), (80, HEIGHT - 40))
        self.draw_button("Check", (160, HEIGHT - 50, 90, 40), (180, HEIGHT - 40))
        self.draw_button("Bet", (270, HEIGHT - 50, 90, 40), (300, HEIGHT - 40))
        self.draw_button("Deal", self.deal_button_rect, (410, HEIGHT - 40))

        if self.deal_button_clicked and not any(player.hand.cards for player in self.players):
            self.start_new_round()
            self.deal_button_clicked = False

        if self.round_started and len(self.community_cards) < 5:  
            self.deal_community_cards(1)  
            self.round_started = False  

        pygame.display.update()

    def draw_player_hands(self):
        for i, player in enumerate(self.players):
            total_cards = len(player.hand.cards)
            total_width = total_cards * 70 + (total_cards - 1) * 10
            start_x = (WIDTH - total_width) / 2

            for j, card in enumerate(player.hand.cards):
                card_img = card_images[card.image_name()]
                card_width, card_height = card_img.get_width(), card_img.get_height()

                x = start_x + j * (card_width + 10)
                y = 300 + i * (card_height + 10)

                win.blit(card_img, (x, y))

    def draw_community_cards(self):
        card_spacing = 10  
        total_community_cards = len(self.community_cards)

        if total_community_cards > 0:
            community_card_width = card_images[self.community_cards[0].image_name()].get_width()
            start_x = (WIDTH - (community_card_width * total_community_cards + card_spacing * (total_community_cards - 1))) / 2

            for i, card in enumerate(self.community_cards):
                card_img = card_images[card.image_name()]
                x = start_x + i * (card_img.get_width() + card_spacing)  
                y = (HEIGHT - card_img.get_height()) / 2  
                win.blit(card_img, (x, y))  

    def draw_button(self, text, rect, text_pos):
        mouse_pos = pygame.mouse.get_pos()
        button_rect = pygame.Rect(rect)

        if button_rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0]:
                if text == "Deal" and not any(player.hand.cards for player in self.players):
                    self.deal_button_clicked = True
                    return
                if text == "Fold":
                    self.players[0].fold()
                    if any(player.hand.cards for player in self.players):
                        self.start_new_round()  # Chia lại từ đầu nếu có người chơi fold
                    else:
                        self.deal_button_clicked = True  # Nếu tất cả người chơi fold, chia lại từ đầu sau khi nhấp nút Deal
                elif text == "Check":
                    self.players[0].check()
                    self.round_started = True  
                elif text == "Bet":
                    self.players[0].raise_bet(50)
                    self.round_started = True  

        button_color = (255, 0, 0)
        button_hover_color = (200, 0, 0)

        if button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(win, button_hover_color, button_rect)
        else:
            pygame.draw.rect(win, button_color, button_rect)

        font = pygame.font.SysFont(None, 24)
        text_surface = font.render(text, True, (255, 255, 255))
        win.blit(text_surface, text_pos)

    def run_game(self):
        run = True
        while run:
            clock.tick(fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            self.draw()

        pygame.quit()

players = [Player("Player 1")]
game = PokerGame(players)
game.run_game()
