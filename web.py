import random
from hatgame import HatGame
from flask import Flask, Response, render_template, request, redirect, abort, url_for


# start flask app
app = Flask(__name__)


hatgame = HatGame()


@app.route('/')
def index():
    """
    Main page
    
    Ask their name and they join a lobby

    """

    username = request.args.get('username')

    if username == None:
        # before we have the username
        # they enter the username in this stage
        return render_template(
            'index.html'
        )
    
    
    else:
        # Now we have a username input
        
        # add the username to our game
        # if its a valid username display the lobby
        hatgame.add_user(username)

        # else display index with an error
        
        return redirect(
            url_for(
                'lobby',
                user=username
            )
        )


@app.route('/lobby')
def lobby():
    """
    Lobby page
    Display people in lobby and have ready up button    
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


@app.route('/input')
def input_func():
    """
    GET /input?hello=1
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


if __name__ == '__main__':
    # start the flask server
	app.run(port=5000, debug=True)
