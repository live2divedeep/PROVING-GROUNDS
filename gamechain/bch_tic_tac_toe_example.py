
from bitcash import PrivateKeyTestnet

PRIVATE_KEY = "cTnSxeMZyzQgBpdsxGDujpZj75KawM2JgN5S4ppEHbG75az7CUGn"

my_key = PrivateKeyTestnet(PRIVATE_KEY)

print(my_key.get_transactions())

print(my_key.get_balance())


import datetime
from secrets import PLAYER1_PRIVATE_KEY, PLAYER2_PRIVATE_KEY
from games import GAMESHELF_ID_TIC_TAC_TOE

player1_key = PrivateKeyTestnet(PLAYER1_PRIVATE_KEY)
player2_key = PrivateKeyTestnet(PLAYER2_PRIVATE_KEY)

lfg_tx = create_looking_for_game_transaction(GAMESHELF_ID_TIC_TAC_TOE, "TicTacToe @ %s" % datetime.datetime.now(), "I go first; I am X")
lfg_tx_id = player1_key.send(lfg_tx)

p2_lfg_tx = wait_for_lfg(player2_key, GAMESHELF_ID_TIC_TAC_TOE)
p2_wtp_tx = create_willing_to_play_transaction(p2_lfg_tx)
player2_key.send(p2_wtp_tx)

p1_wtp_tx = wait_for_wtp(player1_key, lfg_tx_id)
iaccept_tx = create_iaccept_transaction(p1_wtp_tx)
player1_key.send(iaccept_tx)

# players create/send/wait for moves
