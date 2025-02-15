import pygame
import random
import sys
from pygame.locals import *

pygame.init()

# Константы для настройки игры
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
CARD_SIZE = {
    'easy': (100, 100),
    'medium': (75, 75),
    'hard': (70, 70)
}
GRID_DIMENSIONS = {
    'easy': (4, 4),
    'medium': (4, 6),
    'hard': (4, 8)
}
BACKGROUND_COLOR = (255, 255, 255)  # Белый фон
CARD_COLOR = (128, 128, 128)  # Цвет рубашки карты

# Загрузка звуков
try:
    pygame.mixer.music.load("eec95da626eda37.mp3")  # Музыка победы
    lose_sound = pygame.mixer.Sound("Неудача (разочарование, проигрыш).mp3")  # Музыка проигрыша
except FileNotFoundError:
    print("Sound files not found. Continuing without sound.")
    lose_sound = None


class Card:
    """Класс для представления карты."""

    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hidden = True  # Карты изначально закрыты
        self.matched = False  # Флаг для отслеживания совпадений

    def draw(self, screen):
        """Отрисовка карты."""
        if self.matched:  # Если карта уже найдена, она остается открытой
            pygame.draw.circle(screen, self.color, self.rect.center, min(self.rect.width, self.rect.height) // 2)
        elif self.hidden:  # Если карта скрыта, рисуем круг рубашки
            pygame.draw.circle(screen, CARD_COLOR, self.rect.center, min(self.rect.width, self.rect.height) // 2)
        else:  # Если карта открыта, рисуем цветной круг
            pygame.draw.circle(screen, self.color, self.rect.center, min(self.rect.width, self.rect.height) // 2)

    def flip(self):
        """Переворачивает карту."""
        self.hidden = not self.hidden


class MemoryGame:
    """Основной класс игры."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Memory Game")
        self.clock = pygame.time.Clock()
        self.level = None
        self.cards = []
        self.flipped_cards = []  # Список для хранения перевернутых карт
        self.game_over = False
        self.score = 0  # Счет игрока
        self.start_time = None  # Время начала игры
        self.show_initial_cards = True  # Флаг для показа карт в начале игры
        self.timer = None  # Таймер для уровня
        self.time_limit = None  # Лимит времени для уровня

        # Настройки текста
        self.font_name = "Arial"  # Название шрифта
        self.font_size = 38  # Размер шрифта
        self.font_color = (0, 0, 0)  # Цвет текста

    def start_screen(self):
        """Экран выбора уровня."""
        while True:
            self.screen.fill(BACKGROUND_COLOR)

            # Текст для выбора уровня, разделенный на строки
            level_texts = [
                "Выберите уровень:",
                "1 - Легкий (1,5 минута/8 пар)",
                "2 - Средний (3 минута/12 пар)",
                "3 - Сложный (4,5 минута/16 пар)"
            ]

            # Отрисовка каждой строки текста
            for i, text in enumerate(level_texts):
                rendered_text = self.draw_text(text, self.font_name, self.font_size, self.font_color)
                text_y = 200 + i * 50  # Размещаем строки с интервалом 50 пикселей
                self.screen.blit(rendered_text, (230, text_y))

            pygame.display.flip()

            # Обработка событий
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_1:
                        self.level = 'easy'
                        self.time_limit = 90  # 1,5 минута
                        return
                    elif event.key == K_2:
                        self.level = 'medium'
                        self.time_limit = 180  # 3 минуты
                        return
                    elif event.key == K_3:
                        self.level = 'hard'
                        self.time_limit = 270  # 4,5 минут
                        return

    def generate_cards(self):
        """Генерация карт для выбранного уровня."""
        rows, cols = GRID_DIMENSIONS[self.level]
        card_width, card_height = CARD_SIZE[self.level]

        # Генерация цветов для парных карт
        colors = list(set((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in
                          range((rows * cols) // 2)))
        colors *= 2
        random.shuffle(colors)

        self.cards = []
        for row in range(rows):
            for col in range(cols):
                x = col * card_width + (SCREEN_WIDTH - cols * card_width) // 2
                y = row * card_height + (SCREEN_HEIGHT - rows * card_height) // 2
                self.cards.append(Card(x, y, card_width, card_height, colors.pop()))

    def check_win(self):
        """Проверка на победу."""
        return all(card.matched for card in self.cards)

    def draw_text(self, text, font_name, font_size, color):
        """Метод для создания текста."""
        font = pygame.font.SysFont(font_name, font_size)
        return font.render(text, True, color)

    def show_message(self, message_lines):
        """Показывает сообщение и обрабатывает выбор пользователя."""
        self.screen.fill(BACKGROUND_COLOR)

        # Отрисовка каждой строки текста
        for i, line in enumerate(message_lines):
            rendered_text = self.draw_text(line, self.font_name, self.font_size, self.font_color)
            text_y = SCREEN_HEIGHT // 2 - len(message_lines) * 20 + i * 40  # Расположение строк
            self.screen.blit(rendered_text, (SCREEN_WIDTH // 2 - rendered_text.get_width() // 2, text_y))

        # Добавляем подсказку для пользователя
        hint_text = self.draw_text("Нажмите Y для повторной игры или N для выхода",
                                   self.font_name, self.font_size - 10, (128, 128, 128))
        self.screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2,
                                     SCREEN_HEIGHT - hint_text.get_height() - 20))

        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_y:  # Нажатие Y для перезапуска
                        self.__init__()
                        self.run()
                    elif event.key == K_n:  # Нажатие N для выхода
                        pygame.quit()
                        sys.exit()

    def run(self):
        """Основной игровой цикл."""
        self.start_screen()
        self.generate_cards()
        self.start_time = pygame.time.get_ticks()  # Начало отсчета времени
        show_initial_cards_timer = 10000  # Время показа карт в начале игры (10 секунд)
        self.timer = self.time_limit  # Устанавливаем таймер на выбранный лимит времени
        while True:
            current_time = pygame.time.get_ticks()
            elapsed_time = (current_time - self.start_time) // 1000  # Прошедшее время в секундах
            self.timer = max(0, self.time_limit - elapsed_time)  # Обратный отсчет таймера
            self.screen.fill(BACKGROUND_COLOR)  # Заполняем экран белым фоном

            # Показываем карты в начале игры
            if self.show_initial_cards and current_time - self.start_time < show_initial_cards_timer:
                for card in self.cards:
                    card.hidden = False  # Открываем все карты
            elif self.show_initial_cards:
                for card in self.cards:
                    card.hidden = True  # Закрываем карты после окончания времени
                self.show_initial_cards = False

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONDOWN and not self.game_over:
                    for card in self.cards:
                        if card.rect.collidepoint(event.pos) and card.hidden and len(self.flipped_cards) < 2:
                            card.flip()
                            self.flipped_cards.append(card)

            # Проверка совпадения карт
            if len(self.flipped_cards) == 2:
                card1, card2 = self.flipped_cards
                if card1.color == card2.color:
                    card1.matched = True
                    card2.matched = True
                    self.score += 10  # Увеличиваем счет за каждую найденную пару
                else:
                    pygame.time.delay(500)  # Задержка перед переворотом карт
                    card1.flip()
                    card2.flip()
                self.flipped_cards.clear()

            # Отрисовка карт
            for card in self.cards:
                card.draw(self.screen)

            # Отображение счета и таймера
            score_text = self.draw_text(f"Счет: {self.score}", self.font_name, self.font_size, self.font_color)
            timer_text = self.draw_text(f"Время: {self.timer} сек", self.font_name, self.font_size, self.font_color)
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(timer_text, (10, 50))

            # Проверка на победу
            if self.check_win() and not self.game_over:
                if lose_sound:
                    pygame.mixer.music.play()  # Воспроизведение музыки победы
                self.game_over = True
                win_message = [
                    "Вы выиграли!",
                    f"Ваш счет: {self.score}.",
                    "Хотите сыграть еще?"
                ]
                self.show_message(win_message)

            # Проверка на проигрыш
            if self.timer == 0 and not self.game_over:
                if lose_sound:
                    lose_sound.play()  # Воспроизведение музыки проигрыша
                self.game_over = True
                lose_message = [
                    "Время вышло!",
                    "К сожалению, вы проиграли.",
                    "Хотите сыграть еще?"
                ]
                self.show_message(lose_message)

            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == "__main__":
    game = MemoryGame()
    game.run()
