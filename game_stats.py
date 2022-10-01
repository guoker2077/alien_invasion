class GameStats:

    def __init__(self,ai_game):
        self.settings = ai_game.settings
        self.reset_stats()
        self.game_active = False

        with open("highest_score.txt","r") as f:
            str_score = f.read()
            self.high_score = int(str_score)

    def reset_stats(self):
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1