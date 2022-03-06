# gamechain
This project is to test my hypothesis that the Bitcoin Cash (BCH) blockchain and mempool with zero-confirmation transaction times can make a reasonable, open, non-proprietary game event system for non-realtime multi-player game participation.

It is a companion protocol to [GameChain Lobby](https://github.com/devalbo/gamechain-lobby).

### What is a Game?
If you think of a game as a set of initial conditions and a series of validated transformations at the direction of participants (with some mechanism for randomness when appropriate), it becomes possible to abstract the back and forth as a series of messages. Games themselves can consists of two major components: client/user-interface and rules/validation engine. As long as you have the game as a complete specification of rules/protocols, gameplay can occur on-chain or off-chain (but still have moves be signed/authenticated by participants). Additionally, as long as clients can use these protocols, which clients people use become irrelevant to the game/blockchain itself as long as they validate according to the same sets of rules. Finally, games can resolve themselves the way they would off the blockchain - using observable behavior and conventions.

## Scope
Typical games involve players taking turns making decisions. In theory, this back and forth can occur in messages encoded as blockchain transactions. With the proper abstraction, most classic games could be codified this way.

The use of this protocol is driven by the Game being played. These are some common interactions which should be common to most (if not all) games. The important things to publish on-chain so that they can be seen/recorded/agreed as fair are: game decisions during a turn, assessed outcomes of those game decisions, turn hand-off between players, resolving the game (win/loss/draw)and being able to disagree about the outcome (e.g. bug in rules, invalid play, flip the table, etc.). 

While games might be able to be encoded as Script, I think it's more important to enable games without requiring a centralized protocol (which means they could be Script-based... they just don't *have* to be). Admittedly this is hand-waving at this point. Coming up with a game initialization/play mechanism and implementing a range of games to do that in a range of use cases is the point of this project. 


### There's a lot to do yet...
There are a lot of details to work out and conventions/protocols to support all types of games would be very important, but I am optimistic. One thing to note is that games that use randomness should be possible, but I'm starting as simply as possible. Many games have more than two players, which should also be possible, but I will start with only two players to keep communication simple while testing this hypothesis.

## Assumptions
This system works by using mempools and 0-conf to notify clients about transaction relevant to protocols used for game discovery and play. We will start with some basic assumptions.
* A Player is denoted by a BCH address. This BCH address is that Player's PlayerId.
* A Player uses their private key to sign/authenticate messages they transmit.
* A Player who wishes to start a game is called the Initiator.
* A Game is defined as: a set of initial conditions, rules that define valid actions players can take, how the game state changes based on those actions, transitions between Player turns, when the game ends, and what the outcome of the game is.
* A Game has a GameLobby identifier BCH address.  
* A Match is an instance of a Game. A concluded Match consists of initial conditions, at least one Player, and a series of Player-induced actions.

##Protocol
####BCH Transaction addressing scheme
 The first occurring P2PKH UTXO in a GameChain transaction is the address of the message sender. Addresses of intended recipients are the remainig P2PKH UTXO(s). The OP_RETURN code is the GameChain message.
 
####Message Format
Gamechain messages are preceded by a version byte and a message code byte. During development, the version byte will be set to 1. Message codes are as follows.

| Message Code<br/>Hex Value | Name    | Description |
|:--------------------------:| --------| ----------- | 
| 0x01                       | **STT** | Setting the Table. Initiator broadcasts the game's starting conditions. This includes the player addresses, public keys, inital player order, and game-specific information. |
| 0x02                       | **STC** | Setting the Table - Continuation. Initiator continues broadcasting the game's starting conditions from a previous STT or STC message. |
| 0x03                       | **TMT** | Taking My Turn. Player indicates their move using the game-specific protocol. |
| 0x04                       | **WIN** | I Win. Player claims they win with the move executed using the game-specific protocol. |
| 0x05                       | **LUZ** | I Lose. Player loses. There may be a move they take that is the last move they will execute. |
| 0x06                       | **DRW** | We Draw. Player broadcasts that the game is ending in a tie using the move executed using the game-specific protocol. |
| 0x07                       | **CCD** | I Concede. Player accepts losing and indicates they will be taking no more turns. |
| 0x08                       | **ACC** | I Accept Outcome. Player indicates they accept the proffered outcome. They may express a sentiment. |
| 0x09                       | **DIS** | I Dispute Outcome. Player indicates they do accept the proffered outcome. They may express a sentiment and indicate the basis for their dispute. |
| 0x0A                       | **PTD** | Propose to Draw. Player broadcasts that they would like to end the game in a tie. |
| 0x0B                       | **ATD** | Agree to Draw. Player responds that they are willing to end the game in a tie. |
| 0x0C                       | **DTD** | Disagree to Draw. Player responds that they are not willing to end the game in a tie. |


#### Message/Action: Setting the Table
 The transaction and following Continuation messages contain enough information for a game client to display the game and enable play options as appropriate. The following information is in the OP_RETURN:
 
| Byte Count | Name    | Format/Values | Description |
|:----------:| --------| ----------- | ---- | 
| 1          | Protocol version | Version byte | See protocol description. |
| 1          | **STC** | 0x02 | _Setting the Table_ message code. See above. |
| 32         | Signal Tx ID | <transaction_id> | Transaction ID of the message signaling the game will be played. (ACC message if using GameChain Lobby protocol for set up) |
| 1          | Message data size | Size byte| Number of bytes to read for message data  |
| 1          | Signed Tx ID data size | Size byte | Number of bytes to read for signed transaction ID data |
| 33         | Initiator's public key | <public_key> | Key used by the initiator to sign messages. |
| 1          | STC message follows | Boolean byte | While this is non-zero, append STC messages to this until a message where this byte is zero. | 
| 32         | STC Tx ID | <transaction_id> | Transaction ID of the continuing STC message. Concatenate game start continuation messages in order until STC message follows is not set to have complete game start message. |
| <message_data_size> | Game start conditions | Complete information about how game will start and be played | Depends on game. Information that should be included regardless of game is: player order, player public keys, player addresses | 
| <signed_tx_id_size> | Signed Tx ID | Byte array used to authenticate message from transmitters | Signed version of the transaction ID signaling the game will be played. Prevents spoofing of this message.| 

#### Message/Action: Setting the Table - Continuation
 Continuation messages contain enough information for a game client to display the game and enable play options as appropriate. Message data should be concatenated to previous messages until there are no more messages. The following information is in the OP_RETURN:
 
| Byte Count | Name    | Format/Values | Description |
|:----------:| --------| ----------- | ---- | 
| 1          | Protocol version | Version byte | See protocol description. |
| 1          | **STC** | 0x02 | _Setting the Table - Continuation_ message code. See above. |
| 1          | Message data size | Size byte| Number of bytes to read for message data  |
| 1          | Signed Tx ID data size | Size byte | Number of bytes to read for signed transaction ID data |
| 1          | STC message follows | Boolean byte | While this is non-zero, append STC messages to this until a message where this byte is zero. || 32         | Following STC message Tx ID | <transaction_id> | Transaction ID of the preceding STT or STC message. |
| 32         | STC Tx ID | <transaction_id> | Transaction ID of the continuing STC message. Concatenate game start continuation messages in order until STC message follows is not set to have complete game start message. |
| <message_data_size> | Game start conditions | Complete information about how game will start and be played | Depends on game. Information that should be included regardless of game is: player order, player public keys, player addresses | 
| <signed_tx_id_size> | Signed Tx ID | Byte array used to authenticate message from transmitters | Signed version of the previous STT or STC transaction ID. Prevents spoofing of this message. Uses initiator key from previous **STT** messages.| 


 #### Message/Action: Taking My Turn
 Taking My Turn messages contain enough information for a game client to display the actions of the player and determine which player's turn is next. The following information is in the OP_RETURN:
 
| Byte Count | Name    | Format/Values | Description |
|:----------:| --------| ----------- | ---- | 
| 1          | Protocol version | Version byte | See protocol description. |
| 1          | **TMT** | 0x03 | _Taking My Turn_ message code. See above. |
| 32         | Prevous Tx ID | <transaction_id> | Transaction ID of the preceding TMT message (or STT/STC message if it's the first turn). |
| 1          | Message data size | Size byte| Number of bytes to read for message data  |
| 1          | Signed Tx ID data size | Size byte | Number of bytes to read for signed transaction ID data |
| <message_data_size> | Game turn operations | Complete information about the player's turn| Depends on game. | 
| <signed_tx_id> | Signed Tx ID | Byte array used to authenticate message from transmitters | Signed version of the previous TMT/STT/STC transaction ID. Prevents spoofing of this message.| 


#### Message/Action: I Win
I Win messages contain enough information for a game client to convince other players the sending player has won using a game-specific protocol. The following information is in the OP_RETURN:
 
| Byte Count | Name    | Format/Values | Description |
|:----------:| --------| ----------- | ---- | 
| 1          | Protocol version | Version byte | See protocol description. |
| 1          | **WIN** | 0x04 | _I Win_ message code. See above. |
| 32         | Prevous Tx ID | <transaction_id> | Transaction ID of the preceding TMT message. |
| 1          | Message data size | Size byte| Number of bytes to read for message data  |
| 1          | Signed Tx ID data size | Size byte | Number of bytes to read for signed transaction ID data |
| <message_data_size> | Winning move | Complete information about the player's turn that results in a win| Depends on game. | 
| <signed_tx_id> | Signed Tx ID | Byte array used to authenticate message from transmitters | Signed version of the previous TMT transaction ID. Prevents spoofing of this message.| 


#### Message/Action: I Lose
I Lose messages can contain last game-turn information using a game-specific protocol. The following information is in the OP_RETURN:
 
| Byte Count | Name    | Format/Values | Description |
|:----------:| --------| ----------- | ---- | 
| 1          | Protocol version | Version byte | See protocol description. |
| 1          | **LUZ** | 0x05 | _I Lose_ message code. See above. |
| 32         | Prevous Tx ID | <transaction_id> | Transaction ID of the preceding TMT message. |
| 1          | Message data size | Size byte| Number of bytes to read for message data  |
| 1          | Signed Tx ID data size | Size byte | Number of bytes to read for signed transaction ID data |
| <message_data_size> | Losing move | Optional. Complete information about the player's turn that results in a loss | Depends on game. | 
| <signed_tx_id> | Signed Tx ID | Byte array used to authenticate message from transmitters | Signed version of the previous TMT transaction ID. Prevents spoofing of this message.| 


#### Message/Action: We Draw
We Draw messages contain last game-turn information using a game-specific protocol and indicate the game ends in a tie. The following information is in the OP_RETURN:
 
| Byte Count | Name    | Format/Values | Description |
|:----------:| --------| ----------- | ---- | 
| 1          | Protocol version | Version byte | See protocol description. |
| 1          | **DRW** | 0x06 | _We Draw_ message code. See above. |
| 32         | Prevous Tx ID | <transaction_id> | Transaction ID of the preceding TMT message. |
| 1          | Message data size | Size byte| Number of bytes to read for message data  |
| 1          | Signed Tx ID data size | Size byte | Number of bytes to read for signed transaction ID data |
| <message_data_size> | Ending move | Complete information about the player's turn that results in a draw | Depends on game. | 
| <signed_tx_id> | Signed Tx ID | Byte array used to authenticate message from transmitters | Signed version of the previous TMT transaction ID. Prevents spoofing of this message.| 


#### Message/Action: I Concede
I Concede messages indicate sender accepts losing and will be taking no more turns. The following information is in the OP_RETURN:
 
| Byte Count | Name    | Format/Values | Description |
|:----------:| --------| ----------- | ---- | 
| 1          | Protocol version | Version byte | See protocol description. |
| 1          | **CCD** | 0x07 | _I Concede_ message code. See above. |
| 32         | Prevous Tx ID | <transaction_id> | Transaction ID of the preceding TMT message. |
| 1          | Message data size | Size byte| Number of bytes to read for message data  |
| 1          | Signed Tx ID data size | Size byte | Number of bytes to read for signed transaction ID data |
| <message_data_size> | Game concession details| Final message | Any color sender wishes to provide on the concession | 
| <signed_tx_id> | Signed Tx ID | Byte array used to authenticate message from transmitters | Signed version of the previous TMT transaction ID. Prevents spoofing of this message.| 


#### Message/Action: I Accept Outcome
I Accept Outcome messages indicate sender accepts proferred outcome. They may express a sentiment. The following information is in the OP_RETURN:
 
| Byte Count | Name    | Format/Values | Description |
|:----------:| --------| ----------- | ---- | 
| 1          | Protocol version | Version byte | See protocol description. |
| 1          | **ACC** | 0x08 | _I Accept_ message code. See above. |
| 32         | Prevous Tx ID | <transaction_id> | Transaction ID of the preceding TMT message. |
| 1          | Message data size | Size byte| Number of bytes to read for message data  |
| 1          | Signed Tx ID data size | Size byte | Number of bytes to read for signed transaction ID data |
| <message_data_size> | Game outcome details| Final message | Any color sender wishes to provide on the outcome | 
| <signed_tx_id> | Signed Tx ID | Byte array used to authenticate message from transmitters | Signed version of the previous WIN/LUZ/DRW/CCD transaction ID. Prevents spoofing of this message.| 


#### Message/Action: I Dispute Outcome
I Dispute Outcome messages indicate sender disagrees with proferred outcome. They may express a sentiment. The following information is in the OP_RETURN:
 
| Byte Count | Name    | Format/Values | Description |
|:----------:| --------| ----------- | ---- | 
| 1          | Protocol version | Version byte | See protocol description. |
| 1          | **DIS** | 0x09 | _I Accept_ message code. See above. |
| 32         | Prevous Tx ID | <transaction_id> | Transaction ID of the preceding TMT message. |
| 1          | Message data size | Size byte| Number of bytes to read for message data  |
| 1          | Signed Tx ID data size | Size byte | Number of bytes to read for signed transaction ID data |
| <message_data_size> | Game dispute details| Final message | Any color sender wishes to provide on the dispute | 
| <signed_tx_id> | Signed Tx ID | Byte array used to authenticate message from transmitters | Signed version of the previous WIN/LUZ/DRW/CCD transaction ID. Prevents spoofing of this message.| 

 
 #### Message/Action: Propose to Draw
Propose to Draw messages indicate sender would like to end the game in a draw. They may express a sentiment. The following information is in the OP_RETURN:
 
| Byte Count | Name    | Format/Values | Description |
|:----------:| --------| ----------- | ---- | 
| 1          | Protocol version | Version byte | See protocol description. |
| 1          | **PTD** | 0x0A | _Propose to Draw_ message code. See above. |
| 32         | Prevous Tx ID | <transaction_id> | Transaction ID of the preceding TMT message. |
| 1          | Message data size | Size byte| Number of bytes to read for message data  |
| 1          | Signed Tx ID data size | Size byte | Number of bytes to read for signed transaction ID data |
| <message_data_size> | Propose to Draw message | Freeform | Any color sender wishes to provide on the draw proposal| 
| <signed_tx_id> | Signed Tx ID | Byte array used to authenticate message from transmitters | Signed version of the previous TMT transaction ID. Prevents spoofing of this message.| 
 
 #### Message/Action: Agree to Draw
Agree to Draw messages indicate sender accepts ending game in a draw. They may express a sentiment. The following information is in the OP_RETURN:
 
| Byte Count | Name    | Format/Values | Description |
|:----------:| --------| ----------- | ---- | 
| 1          | Protocol version | Version byte | See protocol description. |
| 1          | **ATD** | 0x0B | _Agree to Draw_ message code. See above. |
| 32         | Prevous Tx ID | <transaction_id> | Transaction ID of the preceding PTD message. |
| 1          | Message data size | Size byte| Number of bytes to read for message data  |
| 1          | Signed Tx ID data size | Size byte | Number of bytes to read for signed transaction ID data |
| <message_data_size> | Accept to Draw message | Freeform | Any color sender wishes to provide on the draw acceptance | 
| <signed_tx_id> | Signed Tx ID | Byte array used to authenticate message from transmitters | Signed version of the previous PTD transaction ID. Prevents spoofing of this message.| 
 
 #### Message/Action: Disagree to Draw
 Propose to Draw messages indicate sender would like to end the game in a draw. They may express a sentiment. The following information is in the OP_RETURN:
 
| Byte Count | Name    | Format/Values | Description |
|:----------:| --------| ----------- | ---- | 
| 1          | Protocol version | Version byte | See protocol description. |
| 1          | **DTD** | 0x0C | _Disagree to Draw_ message code. See above. |
| 32         | Prevous Tx ID | <transaction_id> | Transaction ID of the preceding PTD message. |
| 1          | Message data size | Size byte| Number of bytes to read for message data  |
| 1          | Signed Tx ID data size | Size byte | Number of bytes to read for signed transaction ID data |
| <message_data_size> | Disagree to Draw message | Freeform | Any color sender wishes to provide on the draw rejection | 
| <signed_tx_id> | Signed Tx ID | Byte array used to authenticate message from transmitters | Signed version of the previous PTD transaction ID. Prevents spoofing of this message.| 

 