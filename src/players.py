import math
import random
import time

import game


def print_options(options, board):
    print(f"player {board.active_player}'s move:")
    if board.phase == game.Phase.Attack:
        for i in range(len(options)):
            if len(options[i]) == 0:
                print(f"{i + 1} - yield")
            elif len(options[i]) == 1:
                print(f"{i + 1} - play the card {next(iter(options[i]))}")
            else:
                print(f"{i + 1} - play the following cards: ", end='')
                for card in options[i]:
                    print(f"{card.name} ", end='')
                print()
    elif board.phase == game.Phase.Discard:
        for i in range(len(options)):
            if len(options[i]) == 1:
                print(f"{i + 1} - discard the card {next(iter(options[i]))}")
            else:
                print(f"{i + 1} - discard the following cards: ", end='')
                for card in options[i]:
                    print(f"{card.name} ", end='')
                print()
    elif board.phase == game.Phase.JokerChoosePlayer:
        for i in range(len(options)):
            print(f"{i + 1} - choose player {options[i]} to go next")


class HumanPlayer():
    def play(self, board, options):
        if len(options) == 1:
            return options[0]
        while True:
            print_options(options, board)
            choice = input("select from the above options: ")
            if choice == "print":
                board.render_state()
                continue
            if not choice.isdigit():
                print("invalid choice")
                continue
            choice = int(choice)
            if choice in list(range(1, len(options) + 1)):
                break
            print("invalid choice")
        return options[choice - 1]


class MCTSPlayer():
    def __init__(self, numSims):
        self.numSims = numSims

    def play(self, board, options):
        if len(options) == 1:
            return options[0]
        return mcts(board, self.numSims)


class Node:
    def __init__(self, state, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.points = 0

    def is_terminal_node(self):
        return self.state.is_over()

    def is_fully_expanded(self):
        return len(self.children) == len(self.state.get_legal_actions())

    def best_child(self, exploration_weight=1.41):
        choices_weights = [
            (child.points / child.visits) + exploration_weight * math.sqrt(
                math.log(self.visits) / child.visits
            )
            for child in self.children
        ]
        return self.children[choices_weights.index(max(choices_weights))]

    def most_visited_child(self):
        visits = [child.visits for child in self.children]
        return self.children[visits.index(max(visits))]

    def expand(self):
        tried = [child.move for child in self.children]
        options = self.state.get_legal_actions()
        for move in options:
            if move not in tried:
                next_state = self.state.clone_state()
                next_state.make_move(move)
                child_node = Node(next_state, self, move)
                self.children.append(child_node)
                return child_node

    def backpropagate(self, result):
        self.visits += 1
        self.points += result
        if self.parent:
            self.parent.backpropagate(result)


def mcts(root_state, num_sims):
    startTime = time.time()
    root = Node(root_state.clone_state())
    for _ in range(num_sims):
        node = root
        # selection
        while node.is_fully_expanded() and node.children:
            node = node.best_child()
        # expansion
        if not node.is_terminal_node():
            node = node.expand()
        # simulation
        result = rollout(node.state)
        # backpropagation
        node.backpropagate(result)
    print("mcts results:")
    for node in root.children:
        print(
            f"Move: {node.move}, visits:{node.visits}, score: {node.points / node.visits}")
    print(f"time elapsed: {time.time() - startTime} seconds")
    return root.most_visited_child().move


def rollout(state):
    current_state = state.clone_state()
    while not current_state.is_over():
        possible_moves = current_state.get_legal_actions()
        if current_state.is_over():
            break
        move = random.choice(possible_moves)
        current_state.make_move(move)
    return current_state.reward()
