from game.Sprites import ShootingBall
from game.Settings import *
from game.BonusManager import Bonus
import random
import datetime


class ShootingManager:
    def __init__(self, ball_generator, pos, bonus_manager, score_manager):
        self.ball_generator = ball_generator
        self.bonus_manager = bonus_manager
        self.score_manager = score_manager

        self.pos = pos
        self.charged_ball = ShootingBall(random.choice(
            self.ball_generator.colors), self.pos)

        self.shooting_balls = []

        self.combo_chain = []

        self.speed = False

    def shoot(self, target):
        if len(self.shooting_balls) == 0 or self.speed or \
                (datetime.datetime.now() -
                 self.shooting_balls[-1].time).microseconds > 300000:
            shooting_ball = self.charged_ball
            shooting_ball.set_target(target)
            shooting_ball.set_time(datetime.datetime.now())
            self.charged_ball = self.recharge()
            self.shooting_balls.append(shooting_ball)

    def recharge(self):
        return ShootingBall(random.choice(
            self.ball_generator.get_available_colors()), self.pos)

    def draw(self, screen):
        self.charged_ball.draw(screen)
        for ball in self.shooting_balls:
            ball.draw(screen)

    def update(self):
        self.speed = self.bonus_manager.handle_speed_bonus()
        self.charged_ball.update()
        for ball in self.shooting_balls:
            ball.update()
            self.remove_flown_away(ball)
            self.handle_shoot(ball)

    def remove_flown_away(self, ball):
        x = ball.rect.center[0]
        y = ball.rect.center[1]
        if x < 0 or x > WIDTH or y < 0 or y > HEIGHT:
            self.shooting_balls.remove(ball)

    def handle_shoot(self, shooting_ball):
        for ball in self.ball_generator.balls:
            if shooting_ball.rect.colliderect(ball.rect):
                chain = self.collect_chain(ball, shooting_ball.color)
                if len(chain) > 1:
                    chain += self.check_for_bonus(chain)
                    self.score_manager.add_score(10 * len(chain))
                    self.ball_generator.destroy(chain)
                    if self.charged_ball.color not in \
                            self.ball_generator.get_available_colors() and \
                            len(self.ball_generator.balls) != 0:
                        self.charged_ball = self.recharge()
                else:
                    ball_index = self.ball_generator.balls.index(ball)
                    self.ball_generator.insert(ball_index, shooting_ball)
                self.shooting_balls.remove(shooting_ball)
                break

    def check_for_bonus(self, chain):
        for ball in chain:
            if ball.bonus is not None:
                if ball.bonus is Bonus.Bomb:
                    return self.bonus_manager.handle_bomb_bonus(chain)
                elif ball.bonus is Bonus.Speed:
                    self.speed = True
                    self.bonus_manager.start_bonus(ball.bonus)
                else:
                    self.bonus_manager.start_bonus(ball.bonus)
        return []

    def collect_chain(self, ball, color):
        ball_index = self.ball_generator.balls.index(ball)
        ball_color = ball.color

        left_half = self.collect_half_chain(ball_index - 1, -1,
                                            color)
        right_half = self.collect_half_chain(ball_index + 1, 1,
                                             color)

        if ball_color == color:
            chain = left_half + [self.ball_generator.balls[ball_index]] + \
                    right_half
            chain.sort(key=lambda ball: ball.pos_in_path)

            return chain

        return right_half

    def collect_half_chain(self, i, delta, color):
        half_chain = []
        while len(self.ball_generator.balls) > i >= 0 and \
                self.ball_generator.balls[i].color == color:
            half_chain.append(self.ball_generator.balls[i])
            i += delta

        return half_chain

