import sys
from time import sleep
import pygame
from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien


class AlienInvasion:

    def __init__(self):
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.screen_width,self.settings.screen_height))
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")

        self.stats = GameStats(self)
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.sb = Scoreboard(self)

        self.__create__fleet()
        self.play__button = Button(self,"Play")

    def __create__fleet(self):
        alien = Alien(self)
        alien_width,alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2*alien_width)
        number_alien_x = available_space_x // (2*alien_width)

        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height -
                             (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_width)
        for row_number in range(number_rows):
            for alien_number in range(number_alien_x):
                self.__create__aliens(alien_number,row_number)

    def __create__aliens(self,alien_number,row_number):
        alien = Alien(self)
        alien_width,alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien_height * row_number
        self.aliens.add(alien)

    def __check__aliens__bottom(self):
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self.__ship__hit()
                break

    def __check_fleet__edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self.__change__fleet__direction()
                break

    def __change__fleet__direction(self):
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def __check__keydown__events(self,event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            self.sb.write_highest_score()
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self.__fire__bullet()

    def __check__keyup__events(self,event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def __fire__bullet(self):
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)


    def __check__play__button(self,mouse_pos):
        button_clicked = self.play__button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            self.settings.initialize_dynamic_settings()
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()

            pygame.mouse.set_visible(False)

    def __check__events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.sb.write_highest_score()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self.__check__keydown__events(event)
            elif event.type == pygame.KEYUP:
                self.__check__keyup__events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self.__check__play__button(mouse_pos)

    def __update__bullets(self):
        self.bullets.update()
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self.__check__bullet__alilen__collsions()

    def __check__bullet__alilen__collsions(self):
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
                self.sb.prep_score()
                self.sb.check_high_score()

        if not self.aliens:
            self.bullets.empty()
            self.__create__fleet()
            self.settings.increase_speed()
            self.stats.level += 1
            self.sb.prep_level()

    def __update__aliens(self):
        self.__check_fleet__edges()
        self.aliens.update()

        if pygame.sprite.spritecollideany(self.ship,self.aliens):
            self.__ship__hit()

        self.__check__aliens__bottom()

    def __ship__hit(self):
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            self.aliens.empty()
            self.bullets.empty()
            self.__create__fleet()
            self.ship.center_ship()

            sleep(0.5)
        else:

            #self.__play_end_music()
            self.stats.game_active = False
            pygame.mouse.set_visible(True)
            self.__play_end_music()

    def __update__screen(self):
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        self.sb.show_score()

        if not self.stats.game_active:
            self.play__button.draw_button()

        pygame.display.flip()

    def __play_music(self):
        pygame.mixer.music.load("music/1.ogg")
        pygame.mixer.music.set_volume(1)
        pygame.mixer.music.play(-1)

    def __play_end_music(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.load("music/3.ogg")
        pygame.mixer.music.set_volume(1)
        pygame.mixer.music.play()
        sleep(4.0)
        self.__play_music()

    def run_game(self):
        self.__play_music()

        while True:

            self.__check__events()

            if self.stats.game_active:
                self.ship.update()
                self.__update__bullets()
                self.__update__aliens()

            self.__update__screen()


if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()