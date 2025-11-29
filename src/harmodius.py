import random
import players
import game

pls = (players.MCTSPlayer(5000), players.MCTSPlayer(5000))
a_game = game.FastGame(len(pls))
a_game.render_state()

while not a_game.is_over():
    options = a_game.get_legal_actions()
    if a_game.is_over():
        break
    a_game.make_move(pls[a_game.active_player].play(a_game, options))
    # a_game.make_move(random.choice(options))

print(f"reward: {a_game.reward()}")
