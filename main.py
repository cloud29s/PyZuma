from game.Path import Path
from game.Sprites import *
from game.BallGenerator import BallGenerator
from game.ShootingManager import ShootingManager
from game.BonusManager import BonusManager
from game.ScoreManager import ScoreManager
from game.Ui import *


class Level:
    def __init__(self, number, score_manager):
        self.number = number
        self.path = Path(number)
        self.ball_generator = BallGenerator(self.path, number * 50, score_manager)
        self.bonus_manager = BonusManager(self.ball_generator)
        self.player = Player(number)
        self.finish = Finish(self.path, self.ball_generator.balls, score_manager)
        self.shooting_manager = ShootingManager(self.ball_generator, self.player.pos, self.bonus_manager, score_manager)


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption("Zuma Ultimate Gigachad Python Anniversery Edition")

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.level_num = 1
        self.score_manager = ScoreManager()
        self.setup_new_game()
        self.is_quit = False

    def play(self):
        self.continue_game(self.ui_manager.start_game_btn,
                           self.ui_manager.start_game_display)
        while not self.is_quit:
            self.setup_new_game()
            self.play_game()

        pygame.quit()

    def setup_new_game(self):
        self.level = Level(self.level_num, self.score_manager)
        self.ui_manager = UiManager(self.screen, self.level)

    def play_game(self):
        game_finished = False

        while not game_finished and not self.is_quit:
            self.level.ball_generator.generate()

            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_quit = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.level.shooting_manager.shoot(pygame.mouse.get_pos())

            self.update_sprites()
            self.update_display(self.ui_manager.game_display)

            if self.score_manager.is_win:
                game_finished = True
                self.handle_win()
            elif self.score_manager.is_lose:
                game_finished = True
                self.handle_lose()

    def handle_win(self):
        if self.level_num == 3:
            self.win_game()
        else:
            self.continue_game(self.ui_manager.continue_btn,
                               self.ui_manager.win_level_display)
            self.level_num += 1
            self.score_manager.setup_next_level()

    def handle_lose(self):
        self.score_manager.take_live()
        if self.score_manager.lose_game:
            self.continue_game(self.ui_manager.new_game_button,
                               self.ui_manager.lose_game_display)
            self.level_num = 1
            self.score_manager = ScoreManager()
        else:
            self.continue_game(self.ui_manager.start_level_again_btn,
                               self.ui_manager.lose_level_display)
            self.score_manager.setup_next_level()

    def continue_game(self, button, window):
        game_continued = False
        while not game_continued and not self.is_quit:
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_quit = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if button.rect.collidepoint(mouse):
                        game_continued = True
            self.update_display(window)

    def win_game(self):
        on_win_window = True
        while on_win_window and not self.is_quit:
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_quit = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.ui_manager.start_game_again_btn.rect.collidepoint(mouse):
                        on_win_window = False
                        self.level_num = 1
                    elif self.ui_manager.finish_btn.rect.collidepoint(mouse):
                        self.is_quit = True

            self.update_display(self.ui_manager.win_game_display)

    def update_sprites(self):
        self.level.player.update()
        self.level.shooting_manager.update()
        self.level.ball_generator.update()
        self.level.bonus_manager.update()
        self.level.finish.update()

    def update_display(self, display):
        self.ui_manager.draw_window(display)
        if display is self.ui_manager.game_display:
            self.ui_manager.show_score(self.score_manager.score)
            self.ui_manager.show_lives(self.score_manager.lives)
        pygame.display.update()


if __name__ == '__main__':
    game = Game()
    game.play()
