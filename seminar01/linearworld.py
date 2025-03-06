
# Constants used for left/right actions
LEFT = -1
RIGHT = 1

# Implementation of linear world
class LinearWorld:
    def __init__(self, length):
        # Store length of world
        self.length = length
        
        # Initialize state of world in the middle
        self.pos = length // 2
    
    def step(self, action):
        """
        Perform an action (going left or right)
        """
        # Compute new state
        if self.pos == 0:
            self.pos += 1
        elif self.pos == self.length - 1:
            self.pos -= 1
        elif action == LEFT:
            self.pos -= 1
        elif action == RIGHT:
            self.pos += 1
        else:
            raise Exception('Invalid action!')

        # Compute reward
        if self.pos == 0:
            reward = 1
        elif self.pos == self.length - 1:
            reward = 1
        else:
            reward = 0

        # Return state and reward
        return self.pos, reward

    def reset(self):
        """
        Reset the position to the middle
        """
        self.pos = self.length // 2

    def showWorld(self):
        """
        Print a representation of the linear world
        """
        # Start with an empty string
        text = ''
        
        # Add "_" for every empty spot, "X" for the player
        for i in range(self.length):
            if i == self.pos:
                text = text + 'X '
            else:
                text = text + '_ '
        print(text)

    def __str__(self):
        # (!) Advanced concept:
        # Custom string-conversion (used e.g. by `print()`)
        
        # Start with an empty string
        text = ''
        
        # Add "_" for every empty spot, "X" for the player
        for i in range(self.length):
            if i == self.pos:
                text = text + 'X '
            else:
                text = text + '_ '
        return text


# Short test function
def testLinearWorld():
    # Initialize a new linearworld
    lw = LinearWorld(9)
    totalRewards = 0
    print(lw)
    
    # Take a few steps to the right
    for i in range(7):
        (pos, reward) = lw.step(RIGHT)
        totalRewards += reward
        print(lw)
        print(pos, reward, totalRewards)

# This code is only run if the module is run directly,
# not if it is imported from a different file
if __name__ == '__main__':
    testLinearWorld()



