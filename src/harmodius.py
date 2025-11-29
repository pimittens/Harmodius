import random

import game

a_game = game.FastGame(4)
a_game.render_state()

while not a_game.is_over():
    options = a_game.get_legal_actions()
    if a_game.is_over():
        break
    while True:
        for i in range(len(options)):
            print(f"{i+1} - {options[i]}")
        choice = input("select from the above options: ")
        if choice == "print":
            a_game.render_state()
            continue
        if not choice.isdigit():
            print("invalid choice")
            continue
        choice = int(choice)
        if choice in list(range(1, len(options) + 1)):
            break
        print("invalid choice")
    a_game.make_move(options[choice - 1])
    #a_game.make_move(random.choice(options))

print(f"reward: {a_game.reward()}")
