import random
from hatgame import HatGame
from flask import Flask, Response, render_template, request, redirect, abort, url_for, session, jsonify
from typing import Dict
import logging
from flask.logging import default_handler

# start flask app
app = Flask(__name__)

# web domain
#app.config['SERVER_NAME'] = "127.0.0.1:5000"

# This needs to be set properly in production
app.secret_key = b'not a secret'

""" # set up flask logging
class RequestFormatter(logging.Formatter):
    def format(self, record):
        try:
            record.url = request.url
            record.remote_addr = request.remote_addr
        except:
            record.url = None
            record.remote_addr = None

        return super().format(record)

formatter = RequestFormatter(
    '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
    '%(levelname)s in %(module)s: %(message)s'
)

default_handler.setFormatter(formatter)

logging.basicConfig(filename='app_log.log',level=logging.INFO)
logging.FileHandler('app_log.log', mode='a')

root = logging.getLogger()
root.addHandler(default_handler) """



# we store hatgame instances here
hatgamehat: Dict[str, HatGame] = {}

instructions = {
    '1': "Describe the item in with any words except for words in the item",
    '2': 'Describe the item in one word and only one word',
    '3': 'Act out the item!'
}


@app.route('/')
def index():
    """
    Main page

    Join a lobby
    or
    Create a lobby

    """

    username = request.args.get('username')
    room_id = request.args.get('room_id')
    session['username'] = username
    link_id = request.args.get('link_id', "")

    if username == None:
        # before we have the username
        # they enter the username in this stage
        return render_template(
            'index.html',
            link_id = link_id
        )
    
    if room_id == None:
        # then create a new game
        hatgame = HatGame()
        hatgamehat[hatgame.id] = hatgame # put hatgame in the game hat
        hatgame.add_user(username) # add to the hat
        session['id'] = hatgame.id
        # redirect to /<room_id>
        return redirect(
            url_for(
                'game',
                game_id=hatgame.id
            )
        )

    # join the new game if it exists
    hatgame = hatgamehat.get(room_id, None)

    # handle game not existing
    if hatgame == None:
        # return the index page with an error message
        return render_template(
            'index.html',
            error = "That game doesn't exist"
        )

    if hatgame.add_user(username) != "Success":
        # return the index pagge with an error message
        return render_template(
            'index.html',
            error = "Enter a username!"
        )

    session['id'] = hatgame.id

    # redirect to /game/<room_id>
    return redirect(
        url_for(
            'game',
            game_id=hatgame.id
        )
    )


@app.route('/game/<game_id>', methods=['GET', 'POST'])
def game(game_id):
    """
    Display the game depending on the game_id and state of that game
    """
    hatgame = hatgamehat.get(game_id, None)

    # handle game not existing
    if hatgame == None:
        # return the index page with an error message
        return render_template(
            'index.html',
            error = "This game doesn't exist"
        )

    # depending on the game state we display different content here?
    state = hatgame.get_state()

    # functions which map to the states
    states = {
        'lobby': lobby,
        'input': input_stage,
        '1': round_,
        '2': round_,
        '3': round_,
        'end': end
    }

    # return the state function output
    return states[state](hatgame)


def lobby(hatgame):
    """
    Lobby page
    Display people and wait for everyone to join
    """

    username = session['username']
    ready = request.args.get('readyCheck')

    if ready == "✔":
        message = hatgame.set_user_ready(username) # update that users status

    all_users = hatgame.all_users()
    
    message = hatgame.change_state_to_input()
    
    # display lobby with users
    return render_template(
        'lobby.html',
        username = session['username'],
        all_users = all_users,
        room_id = hatgame.id,
        ready = ''
    )


def input_stage(hatgame):
    """
    user enters names to be put in the hat
    """
 
    input_name = request.args.get('input_name')
    username = session['username']

    ready = hatgame.users_input_ready()

    if input_name == None:
        # diplay the page
        return render_template(
            'input.html', 
            user = username,
            ready = ready
        )
    
    else:
        message = hatgame.put(username,input_name)

        return render_template(
            'input.html',
            user = username,
            message = message,
            ready = ready,
            user_finished = hatgame.user_finished(username),
            items_left = hatgame.user_input_left(username)
        )


def round_(hatgame):
    # round number
    # round instruction
    # user turn -> who is playing
    # if user turn
    #   item picked
    #   round instruction
    #   list of users

    round_winner_name = request.args.get('round_winner_name') # only for choose state
    username = session['username']
    

    hatgame.change_round() # if hat is empty change state
    
    # if the round has changed, show the round change page
    if hatgame.get_state() != hatgame.previous_state(username):
        round_instruction = instructions[hatgame.get_state()]
        hatgame.set_previous_state(username)
        return render_template(
            'round_change.html',
            round = hatgame.get_state(),
            state = hatgame.get_state(),
            instructions = round_instruction
        )
    hatgame.set_previous_state(username)


    current_player = hatgame.current_player()
    current_item = hatgame.current_item()

    if current_player == None:
        # start of the round
        hatgame.pick()
        current_player = hatgame.current_player()
        current_item = hatgame.current_item()


    if round_winner_name != None:
        # user has chosen a player who got the item right
        # check if the current player is the user
        if hatgame.current_player() == username:
            hatgame.choose(username, round_winner_name)
            # pick new item and player
            hatgame.pick()
            # set all user state to display round result
            hatgame.set_round_winner(round_winner_name)

        else:
            # it's not that players turn to choose
            pass
    
    # check if there has been a round winner since last state change
    round_winner_name = hatgame.is_round_winner(username)
    # if round winner is zero, we haven't had a round winner
    if round_winner_name != 0:
        hatgame.set_not_round_winner(username)
        return render_template(
            'round_winner.html',
            round_winner_name = round_winner_name,
            round_number = hatgame.get_state()
        )

    if hatgame.current_player() == username:
        # display the picker screen
        users = hatgame.all_players_except(username)
        round_instruction = instructions[hatgame.get_state()]
        return render_template(
            'round.html',
            round_number = hatgame.get_state(),
            username = username,
            user_turn = hatgame.current_player(),
            item = hatgame.current_item(),
            users = users,
            instructions = round_instruction,
        )
    
    return render_template(
        'round.html',
        round_number = hatgame.get_state(),
        username = username,
        user_turn = hatgame.current_player()
    )

def end():
    # display results
    # delete the hatgame instance
    pass


@app.route('/refresh')
def refresh():
    """
    check if the game state has changed
    This needs to be pretty fast if run often as every client will load this each interval
    (but that should be faster than reloading the entire page?)
    """
    game_id = session.get('id', None)
    username = session.get('username', None)

    hatgame = hatgamehat.get(game_id, None)

    # if the instance doesn't exits, refresh their page
    if hatgame == None:
        return "1"

    change = hatgame.has_changed(username)

    if change == 1:
        hatgame.reset_change(username)
        return "1"
    else:
        return "0"


if __name__ == '__main__':
    # start the flask server
	app.run(port=5000, debug=True)
