from typing import Tuple


class player:
    def __init__(self, location: Tuple[int, int], direction: str | None):
        self.location = location
        self.direction = direction

    def move_player(self, obstacles) -> bool:
        """Changes player coordinates depending on current direction."""
        result = None
        if self.direction == "Up" and self.location[0] > 0:
            result = (self.location[0] - 1, self.location[1])
        elif self.direction == "Down" and self.location[0] < 40:
            result = (self.location[0] + 1, self.location[1])
        elif self.direction == "Left" and self.location[1] > 0:
            result = (self.location[0], self.location[1] - 1)
        elif self.direction == "Right" and self.location[1] < 40:
            result = (self.location[0], self.location[1] + 1)
        if result != None and result not in obstacles:
            self.location = result
            return True
        self.location = self.location
        return False
