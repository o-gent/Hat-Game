import random
from hatgame import HatGame
from flask import Flask, Response, render_template, request, redirect, abort, url_for, session, jsonify
from typing import Dict
import logging
import time

# start flask app
app = Flask(__name__)


from logging.handlers import RotatingFileHandler
file_handler = RotatingFileHandler('python.log', maxBytes=1024 * 1024 * 100, backupCount=20)
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)


# This needs to be set properly in production
app.secret_key = b'not a secret'


# SETUP logging 
logging.basicConfig(
	format='%(asctime)s - %(levelname)s - %(message)s',
	datefmt='%H:%M:%S',
	level = logging.INFO,
	handlers=[
		logging.FileHandler(f"logs/{time.strftime('%Y%m%d-%H%M%S')}.log"),
		logging.StreamHandler()
	]
)


# we store hatgame instances here
hatgamehat: Dict[str, HatGame] = {}

instructions = {
    '1': "Describe the item in with any words except for words in the item",
    '2': 'Describe the item in one word and only one word',
    '3': 'Act out the item!'
}


def mobile_check():
    mobile = False
    mobile_devices = ["android", "iphone"]
    if request.user_agent.platform in mobile_devices:
        mobile = True
    return mobile


@app.after_request
def after_request(response):
    # don't want to log refresh 
    if request.path == '/refresh':
        return response
    # log usage data
    logging.info(f"{request.remote_addr} | {request.url} | {request.user_agent.platform} | {response.status_code}")
    return response


@app.route('/')
def index():
    """
    Main page

    Join a lobby
    or
    Create a lobby

    """
    mobile = mobile_check()
    
    username = request.args.get('username')
    room_id = request.args.get('room_id')
    session['username'] = username
    link_id = request.args.get('link_id', "")

    if username == None:
        # before we have the username
        # they enter the username in this stage
        return render_template(
            'index.html',
            link_id = link_id,
            mobile = mobile
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
                game_id=hatgame.id,
                mobile = mobile
            )
        )

    # join the new game if it exists
    hatgame = hatgamehat.get(room_id, None)

    # handle game not existing
    if hatgame == None:
        # return the index page with an error message
        return render_template(
            'index.html',
            error = "That game doesn't exist",
            mobile = mobile
        )

    if hatgame.add_user(username) != "Success":
        # return the index pagge with an error message
        return render_template(
            'index.html',
            error = "Enter a username!",
            mobile = mobile
        )

    session['id'] = hatgame.id

    # redirect to /game/<room_id>
    return redirect(
        url_for(
            'game',
            game_id=hatgame.id,
            mobile = mobile
        )
    )


@app.route('/game/<game_id>', methods=['GET', 'POST'])
def game(game_id):
    """
    Display the game depending on the game_id and state of that game
    """
    mobile = mobile_check()

    hatgame = hatgamehat.get(game_id, None)

    # handle game not existing
    if hatgame == None:
        # return the index page with an error message
        return render_template(
            'index.html',
            error = "This game doesn't exist",
            mobile = mobile
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
    mobile = mobile_check()

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
        ready = '',
        mobile = mobile
    )


def input_stage(hatgame):
    """
    user enters names to be put in the hat
    """
    mobile = mobile_check()
 
    input_name = request.args.get('input_name')
    username = session['username']

    ready = hatgame.users_input_ready()

    if input_name == None:
        # diplay the page
        return render_template(
            'input.html', 
            user = username,
            ready = ready,
            mobile = mobile
        )
    
    else:
        message = hatgame.put(username,input_name)

        return render_template(
            'input.html',
            user = username,
            message = message,
            ready = ready,
            user_finished = hatgame.user_finished(username),
            items_left = hatgame.user_input_left(username),
            mobile = mobile
        )


def round_(hatgame):

    mobile = mobile_check()

    # get any arguments for page
    round_winner_name = request.args.get('round_winner_name') # only for choose state
    username = session['username']
    
    # start of the round
    if hatgame.current_player() == None:
        hatgame.pick()

    current_player = hatgame.current_player()
    current_item = hatgame.current_item()
    
    # if we have a round winner input, choose and pick
    if round_winner_name != None:
        # user has chosen a player who got the item right
        # check if the current player is the user
        if hatgame.current_player() == username:
            hatgame.choose(username, round_winner_name)
            
            hatgame.change_round()
            # pick new item and player
            hatgame.pick()
            # set all user state to display round result
            hatgame.set_round_winner(round_winner_name)
    
    # check if there has been a round winner since last state change
    round_winner_name = hatgame.is_round_winner(username)
    # if round winner is zero, we haven't had a round winner
    if round_winner_name != 0:
        hatgame.set_not_round_winner(username)

        return render_template(
            'round_winner.html',
            round_winner_name = round_winner_name,
            round_number = hatgame.get_state(),
            mobile = mobile
        )
    
    # if the round has changed, show the round change page
    if hatgame.get_state() != hatgame.previous_state(username):
        round_instruction = instructions[hatgame.get_state()]
        hatgame.set_previous_state(username)
        return render_template(
            'round_change.html',
            round_number = hatgame.get_state(),
            instructions = round_instruction,
            scores = hatgame.scores(),
            mobile = mobile
        )
    hatgame.set_previous_state(username)

    # if it's the turn of the user loading the page, show them the turn page
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
            mobile = mobile
        )
    
    # If it's not the views turn, show them the participant page
    return render_template(
        'round.html',
        round_number = hatgame.get_state(),
        username = username,
        user_turn = hatgame.current_player(),
        mobile = mobile
    )

def end(hatgame):
    # display results
    # delete the hatgame instance after ten minutes
    mobile = mobile_check()

    return render_template(
        'end.html',
        scores = hatgame.scores(),
        bias = hatgame.bias(),
        winner = hatgame.winner(),
        mobile = mobile
    )


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
