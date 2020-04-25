import random
from hatgame import HatGame
from flask import Flask, Response, render_template, request, redirect, abort, url_for, session, jsonify


# start flask app
app = Flask(__name__)

# This needs to be set properly in production
app.secret_key = b'not a secret'


# we store hatgame instances here
hatgamehat = {}


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

    if username == None:
        # before we have the username
        # they enter the username in this stage
        return render_template(
            'index.html'
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


@app.route('/game/<game_id>')
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
        'round1': round1,
        'round2': round2,
        'round3': round3,
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
            ready = ready
        )


def round1(hatgame):
    return render_template(
        'round.html'
    )

def round2():
    pass

def round3():
    pass

def end():
    pass


@app.route('/refresh')
def refresh():
    """
    check if the game state has changed
    This needs to be pretty fast if run often as every client will load this each interval
    (but that should be faster than reloading the entire page?)
    """
    game_id = session['id']

    hatgame = hatgamehat[game_id]

    change = hatgame.has_changed()

    if change == 1:
        hatgame.reset_change()
        return "1"
    else:
        return "0"


if __name__ == '__main__':
    # start the flask server
	app.run(port=5000, debug=True)
