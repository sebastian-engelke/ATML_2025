
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional, Sequence, Union, Iterable

numeric = Union[int, float]
Pos = tuple[int, int]

class GridWorld:
    """
    A generic gridworld class that can be used for different examples
    """
    def __init__(self, height: int = 5, width: int = 5, pos0: tuple[int, int] = (0, 0)):
        """
        Properties other than `height`, `width`, and `pos0` have to be modified after initialization.
        Parameters are not checked!
        """
        # The width and height of the world
        self.width = width
        self.height = height

        # The initial position used by the `reset()` method
        self.pos0 = pos0

        # Start position:
        self.pos: tuple[int, int] = self.pos0
        
        # Possible moves and their labels (must match in number)
        self.moves: list[Pos] = [
            (-1, 0), # Up
            (0, 1),  # Right
            (1, 0),  # Down
            (0, -1)  # Left
        ]
        self.moveLabels = ['↑', '→', '↓', '←']
        
        # Labels for particular positions
        self.positionLabels: dict[Pos, str] = dict()
        
        # Rewards for landing in particular positions (0 else)
        self.rewards: dict[Pos, numeric] = dict()
        
        # Positions that teleport somewhere else in the format
        # `teleportations[(FROM_X, FROM_Y)] = ((TARGET_X, TARGET_Y), REWARD)`
        self.teleportations: dict[Pos, tuple[Pos, numeric]] = dict()
        self.immediateTeleportations: dict[Pos, tuple[Pos, numeric]] = dict()

        # Positions that cannot be moved onto
        self.blockedSquares: list[Pos] = []
        
        # Reward/penalty for attempting an invalid move
        self.invalidActionReward: numeric = 0
        
        # (Small) chance of something super random happening:
        self.randomChance = 0.0

    def step(self, action: int, pos0: Optional[Pos] = None) -> tuple[Pos, numeric]:
        """
        Actually make a step.
        """
        if np.random.uniform() < self.randomChance:
            newPos, reward = self.superRandomStep(action)
        else:
            newPos, reward = self.normalStep(action, pos0)
        self.pos = newPos
        return newPos, reward

    def reset(self):
        """
        Reset the state of the world to `self.pos0`
        """
        self.pos = self.pos0
        return self.pos
    
    def superRandomStep(self, action):
        x = 0
        y = np.random.binomial(self.width - 1, 0.5)
        reward = np.random.chisquare(2 + y) + action - np.random.gumbel(5 + self.pos[0] + self.pos[1])
        reward = max(min(reward, 10), -10)
        pos = (x, y)
        return (pos, reward)

    def normalStep(self, action: int, pos0: Optional[Pos] = None) -> tuple[Pos, numeric]:
        """
        Simulate making a step. Returns new position and reward.
        `pos0` can be used to overwrite the current position.
        (!) This method would not be available in a "real world" example (!)
        """
        # Use current position if `pos0` not specified
        if pos0 is None:
            pos0 = self.pos
        
        # Check if the current position force-teleports
        if pos0 in self.teleportations:
            return self.teleportations[pos0]

        # Compute new position
        move = self.moves[action]
        newPos = (pos0[0] + move[0], pos0[1] + move[1])
        
        # Check if the new position is inside the world and not blocked
        if not self._isValidPosition(newPos):
            return pos0, self.invalidActionReward
        
        # Check if the new position immediately teleports somewhere
        if newPos in self.immediateTeleportations:
            return self.immediateTeleportations[newPos]
        
        # Compute reward, update state
        reward = self.rewards.get(newPos, 0)
        return newPos, reward
    
    
    def _listActions(self) -> list[int]:
        """
        Lists all valid actions in the current position as integers referencing entries in `self.moves`.
        """
        validActions: list[int] = []
        for i, move in enumerate(self.moves):
            newPos = (self.pos[0] + move[0], self.pos[1] + move[1])
            if self._isValidPosition(newPos):
                validActions.append(i)
        return validActions
    
    def _isValidPosition(self, pos):
        """
        "Private" helper function that checks if a position is inside the world and not blocked
        """
        return not (
            pos[0] < 0
            or pos[1] < 0
            or pos[0] >= self.height
            or pos[1] >= self.width
            or pos in self.blockedSquares
        )
        
    def allStates(self):
        """
        Helper function that returns a generator of all possible states of the gridworld
        """
        return ((i, j) for i in range(self.height) for j in range(self.width))

    
    def drawWorld(
            self,
            ax: Optional[plt.Axes] = None,
            title='',
            drawLabels=True,
            drawPos=True,
            drawTeleportations=True,
            drawRewards=True,
            drawBlocked=True,
            policy: dict[Pos, Union[int, Iterable[int]]] = dict(),
            values: Union[dict[Pos, numeric], np.ndarray] = dict(),
            path: Optional[Sequence[Pos]] = None,
        ):
        """
        Draw the gridworld into the axes `ax`, including infos specified by `drawXXX`
        """

        # Prepare axes, empty table
        if ax is None:
            ax = plt.axes()
        ax.set_axis_off()
        tb = matplotlib.table.Table(ax, bbox=[0, 0, 1, 1])
        cellHeight = 1.0 / self.height
        cellWidth = 1.0 / self.width
        
        # Convert value-array to dictionary if necessary
        if isinstance(values, np.ndarray):
            values = {pos: values[pos] for pos in self.allStates()}
        
        # Make list (more precisely: generator) of all squares and iterate over it
        for pos in self.allStates():
            # Prepare the text shown in the current square
            infos = []

            # Add marker of current "player"
            if drawPos and pos == self.pos:
                infos.append('\U0001F600')

            # Add label if the position has a "name"
            if drawLabels and pos in self.positionLabels:
                infos.append(self.positionLabels[pos])

            # If the position teleports to "TARGET", label it "*TARGET"/"**TARGET"
            if drawTeleportations and  pos in self.immediateTeleportations:
                target, reward = self.immediateTeleportations[pos]
                targetLabel = self.positionLabels.get(target, str(target))
                infos.append('**{to} ({reward:+})'.format(to = targetLabel, reward = reward))
            elif drawTeleportations and  pos in self.teleportations:
                target, reward = self.teleportations[pos]
                targetLabel = self.positionLabels.get(target, str(target))
                infos.append('*{to} ({reward:+})'.format(to = targetLabel, reward = reward))


            # If the position has a reward, indicate it
            if drawRewards and pos in self.rewards:
                infos.append('{reward:+}'.format(reward = self.rewards[pos]))
            
            # Add value function
            if pos in values:
                infos.append('{value:.1f}'.format(value = values[pos]))

            # Add arrows for all possible actions (according to policy)
            if pos in policy:
                moveInfo = ''
                policyMoves = policy[pos]
                if isinstance(policyMoves, int):
                    policyMoves = [policyMoves]
                for move in policyMoves:
                    moveInfo += self.moveLabels[move]
                infos.append(moveInfo)

            # Join infos by newlines
            cellText = '\n'.join(infos)

            # Determine background color of current square
            cellColor = 'white'
            if drawBlocked and pos in self.blockedSquares:
                cellColor = 'grey'

            # Add square to plotted table:
            tb.add_cell(pos[0], pos[1], cellWidth, cellHeight, text=cellText, loc='center', facecolor=cellColor)

        # Actually plot the table
        ax.add_table(tb)
        
        # Add title
        ax.set_title(title)

        # Draw path if given
        if path is not None:
            x = [(1/2 + pos[1]) * cellWidth for pos in path]
            y = [1 - (1/2 + pos[0]) * cellHeight for pos in path]
            ax.set_xlim([0,1])
            ax.set_ylim([0,1])
            ax.plot(x, y)
            pass

    def play(self):
        ax = plt.axes()
        totalRewards = 0
        counter = 0
        def onClick(event):
            nonlocal totalRewards
            nonlocal counter
            counter += 1
            # Compute direction of click
            xy0 = np.array(self.posToXy(self.pos))
            xy1 = np.array((event.xdata, event.ydata))
            clickDir = normalizeVector(xy1 - xy0)
            
            # Find matching move
            normalizedMoves = [normalizeVector(move) for move in self.moves]
            scores = [np.dot((move[1], -move[0]), clickDir) for move in normalizedMoves]
            move = np.argmax(scores)
            
            # Make move and re-draw image
            (pos, reward) = self.step(move)
            totalRewards += reward
            print(xy0, ' -> ', xy1, ' ~ ', clickDir, ' : ', move, '   --->   ', pos, ' (Reward: ', reward, ')')
            ax.clear()
            txt = '   -   '.join([
                '#' + str(counter),
                'Action: ' + self.moveLabels[move],
                'State: ' + str(pos),
                'Reward: ' + str(reward),
                'Total: ' + str(totalRewards)
            ])
            self.drawWorld(ax, txt)
            plt.draw()
        self.drawWorld(ax, 'Click the gridworld to play!')
        ax.figure.canvas.mpl_connect('button_press_event', onClick)
        plt.show()
    
    def posToXy(self, pos: tuple[int, int]):
        x = (1/2 + pos[1]) / self.width
        y = 1 - (1/2 + pos[0]) / self.height
        return (x, y)

def normalizeVector(v):
    return v / np.linalg.norm(v)




# The functions below can be used for testing,
# they are not meant to be useful for anything else.

def _example2():
    gw = GridWorld(5, 6)
    A_POS = (0, 1)
    A_PRIME_POS = (4, 1)
    B_POS = (0, 3)
    B_PRIME_POS = (2, 3)
    gw.positionLabels[A_POS] = 'A'
    gw.teleportations[A_PRIME_POS] = (A_POS, 10)
    gw.positionLabels[B_POS] = 'B'
    gw.teleportations[B_PRIME_POS] = (B_POS, 5)
    gw.invalidActionReward = -1
    
    gw.blockedSquares.append((1, 1))
    gw.blockedSquares.append((1, 2))
    
    gw.play()

def _example1():
    # Example illustrating all the cool features
    gw = GridWorld(5, 6)
    A_POS = (0, 1)
    A_PRIME_POS = (4, 1)
    B_POS = (0, 3)
    B_PRIME_POS = (2, 3)
    gw.positionLabels[A_POS] = 'A'
    gw.teleportations[A_PRIME_POS] = (A_POS, 10)
    gw.positionLabels[B_POS] = 'B'
    gw.teleportations[B_PRIME_POS] = (B_POS, 5)
    
    gw.blockedSquares.append((1, 1))
    gw.blockedSquares.append((1, 2))
    
    policy = dict()
    policy[(0,0)] = [0, 1]
    policy[(2,3)] = [0, 1, 2, 3]
    policy[(3,4)] = []
    policy[(4,4)] = 3
    policy[(0,1)] = 3
    
    ax = plt.subplot(1,2,1)
    gw.drawWorld(ax, policy=policy)
    
    path = []
    path.append(gw.pos)
    gw.step(2)
    path.append(gw.pos)
    gw.step(1)
    path.append(gw.pos)
    gw.step(2)
    path.append(gw.pos)
    gw.step(1)
    path.append(gw.pos)
    gw.step(1)
    path.append(gw.pos)
    # path = [(0,0), (1,1)]
    ax = plt.subplot(1,2,2)
    gw.drawWorld(ax, path = path)
    plt.show()


if __name__ == '__main__':
    _example2()
    # _example1()

