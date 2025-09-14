import os

class ScoreManager:
    def __init__(self, filename="high_score.txt"):
        self.filename = filename
        self.high_score = self.load_high_score()
    
    def load_high_score(self):
        """Load the high score from file"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as file:
                    return int(file.read().strip())
            else:
                return 0
        except (FileNotFoundError, ValueError):
            # If file doesn't exist or contains invalid data, return 0
            return 0
    
    def save_high_score(self, score):
        """Save the high score to file if it's a new record"""
        if score > self.high_score:
            self.high_score = score
            try:
                with open(self.filename, 'w') as file:
                    file.write(str(score))
                return True  # New high score achieved
            except IOError:
                print("Could not save high score to file")
                return False
        return False  # Not a new high score
    
    def get_high_score(self):
        """Return the current high score"""
        return self.high_score
    
    def is_new_high_score(self, score):
        """Check if the given score is a new high score"""
        return score > self.high_score