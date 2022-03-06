import gc_message
import gamechain_lobby
import json


def initialize_game(initiator_key, JSON_FILE, table_addr, game_id,
                    p1_addr, p1_public_key,
                    p2_addr, p2_public_key,
                    challenger_game_conditions) -> str:
    init_game_conditions = {
        "gameAddr": game_id,
        "players": [
            {
                "addr": p1_addr,
                "key": p1_public_key.hex()
            },
            {
                "addr": p2_addr,
                "key": p2_public_key.hex()
            }
        ],
        "setup": challenger_game_conditions
    }
    init_game_conditions_str_bytes = json.dumps(init_game_conditions).encode()

    gcl_client = gamechain_lobby.GameChainLobbyClient(initiator_key, JSON_FILE)
    txid = gcl_client.send_gc_message(table_addr, init_game_conditions_str_bytes)
    return f"bitcoincash-gc:{txid}"


def start_playing(init_game_msg, player_key, JSON_FILE):
    bch_init_txid = init_game_msg.split("bitcoincash-gc:")[1]
    # find game tx
    # extract game_id
    # get initial conditions
    # start listening to table address
    # find all turns that have happened until now (query table address for all transactions, put in order)
    # find out who has taken most recent turn
    # when it's player's turn, make a valid move
    return None