import random
from hatgame import HatGame
from flask import Flask, Response, render_template, request, redirect, abort, url_for, session, jsonify, g
from typing import Dict
import logging
import time

# start flask app
app = Flask(__name__)


# This "needs" to be set properly in production
# it's for cookie signing but we don't handle sensitive info  
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


def mobile_check() -> bool:
    return True if request.user_agent.platform in ["android", "iphone"] else False # type: ignore


@app.before_request
def before_request():
    g.start = time.time()


@app.after_request
def after_request(response):
    # don't want to log refresh 
    if request.path == '/refresh':
        return response
    
    # time for request
    diff = time.time() - g.start

    # log usage data
    logging.info(f"{request.remote_addr} | {request.url} | {request.user_agent.platform} | {response.status_code} | {diff}")
    return response


@app.errorhandler(404)
def page_not_found(e):
    """
    https://flask.palletsprojects.com/en/1.1.x/patterns/errorpages/
    """
    # note that we set the 404 status explicitly
    return render_template(
        '404.html',
        mobile = mobile_check()
        ), 404


@app.errorhandler(500)
def internal_error(e):
    """
    https://flask.palletsprojects.com/en/1.1.x/patterns/errorpages/
    """
    return render_template(
        '500.html',
        mobile = mobile_check()
        ), 500


@app.route('/500')
def page500():
    return render_template(
        '500.html',
        mobile = mobile_check()
        ), 500


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
    link_id = request.args.get('link_id', "")

    session['username'] = username
    session.permanent = True # means the cookie persists after the client has disconnected for 31 days

    # if they haven't entered a username, displayer the landing page
    if username == None:
        return render_template(
            'index.html',
            link_id = link_id,
            mobile = mobile
        )
    
    # if they have entered a username but no room_id then they want to create a game
    if room_id == None:
        # then create a new game
        hatgame = HatGame()
        hatgamehat[hatgame.id] = hatgame # put hatgame in the game hat
        hatgame.add_user(username) # add to the hat
        session['id'] = hatgame.id # required for refresh function 
        # redirect to /<room_id>
        return redirect(
            url_for(
                'game',
                game_id=hatgame.id,
            )
        )

    # if they enter a username and room_id, they want to join a game

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
    
    session['id'] = hatgame.id # required for refresh function 

    # if the username already exists in the game, add them back
    if username in hatgame.get_user_info().keys():
        # skip adding to game
        pass
    else:
        # add the username to the game
        message = hatgame.add_user(username)
        
        if message != "Success":
            # return the index page with an error message
            return render_template(
                'index.html',
                error = message,
                mobile = mobile
            )
        else:
            pass

    # redirect to /game/<room_id>
    return redirect(
        url_for(
            'game',
            game_id=hatgame.id,
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

    # if the instance doesn't exist, refresh their page and return them to home
    if hatgame == None:
        return "1"
    
    # if they have lost their username, don't refresh their page as this will just keep on going
    if username == None:
        return "0"

    change = hatgame.has_changed(username)

    if change == 1:
        hatgame.reset_change(username)
        return "1"
    else:
        return "0"


if __name__ == '__main__':
    # start the flask server
	app.run(port=5000, debug=True)
