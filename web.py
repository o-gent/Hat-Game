import random
from hatgame import HatGame
from flask import Flask, Response, render_template, request, redirect, abort, url_for, session


# start flask app
app = Flask(__name__)


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
    lobby_id = request.args.get('lobby_id')

    if username == None:
        # before we have the username
        # they enter the username in this stage
        return render_template(
            'index.html'
        )
    
    if lobby_id == None:
        # then create a new game
        hatgame = HatGame()
        hatgamehat[hatgame.id] = hatgame # put hatgame in the game hat
        hatgame.add_user(username) # add to the hat
        session['username'] = username # add to the session
        # redirect to /<lobby_id>
        return redirect(
            url_for(
                hatgame.id
            )
        )

    else:
        # join the new game if it exists
        # redirect to /<lobby_id>
        hatgame = hatgamehat.get(lobby_id, None)
        # TODO: handle game not existing

        hatgame.add_user(username)

        return redirect(
            url_for(
                'lobby',
                user=username
            )
        )


@app.route('/<game_id>')
def game(game_id):
    """
    Display the game depending on the game_id and state of that game
    """
    hatgame = hatgamehat.get(game_id, None)

    # depending on the game state we display different content here?
    state = hatgame.get_state()

    # functions which map to the states
    states = {
        'lobby': lobby,
        'input': input_stage
    }

    # return the state function output
    return states[state](hatgame)


def lobby(hatgame):
    """
    Lobby page
    Display people and wait for everyone to join
    """

    username = request.args.get('user')
    ready = request.args.get('readyCheck')

    # check if ready parameter exists
    if ready == 1:
        # update that users status
        hatgame.set_user_ready(username)


    user = f"Welcome {username}"

    all_users = hatgame.all_users()

    print(ready)
    
    # check if everyone is ready
    # if hatgame.ready():
    #     # redirect to input
    #     pass
    if False:
        pass

    else:
        # display lobby with users

        return render_template(
            'lobby.html',
            user = user,
            all_users = all_users,
            ready = ''
        )


def input_stage(hatgame):
    """
    user enters names to be put in the hat
    """
 
    input_name = request.args.get('input_name')
    username = request.args.get('username')
    user = f"{username}"

    if input_name == None:
        # diplay the page
        return render_template(
            'input.html', 
            user = user 
        )
    
    else:
        hatgame.put(input_name)
        message = f"{input_name} has been submitted!"
        
        print(message)

        return render_template(
            'input.html',
            user = user,
            message = message
        )


@app.route('/refresh', methods=['POST'])
def refresh():
    """
    check if the game state has changed
    This needs to be pretty fast if run often as every client will load this each interval
    (but that should be faster than reloading the entire page?)
    """
    room_id = request.json.get('id')

    pass


if __name__ == '__main__':
    # start the flask server
	app.run(port=5000, debug=True)
