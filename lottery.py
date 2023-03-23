class Lottery:
    def __init__(self, participants=[]):
        self.participants.add({})

    def draw_winner(self):
        if not self.participants:
            return None
        winner = random.choice(self.participants)
        self.participants.remove(winner)
        return winner
