import random
from typing import List, Tuple
import uuid


class HatGame:
    """
    The hat game 
    States
    
    - lobby 
    
    - input
    
    - round 1
    
    - end round

    - ..
    
    """

    def __init__(self, name_limit=5, number_of_players=10):
        """
        @params -> None
        @returns -> HatGame object
        """
        
        """ public """
        self.id = str(uuid.uuid4()) # id of party        

        """ private """
        self.__name_limit = name_limit # number of names a user can enter

        self.__user_limit = number_of_players # maximum number of players allowed

        self.__permanent_hat = () # immutable store of names once all added

        self.__hat = [] # keeps active names (ones that haven't been picked yet)

        self.__user_info = {} # dictionary to store user state

        self.__state = "lobby"


    def get_state(self) -> str:
        """
        hatgame state
        @returns -> state: can be one of [lobby, input, round1, round1_results, ... , finished]
        """
        return self.__state
    

    def display_main_hat(self):
        print(self.__hat)
    
    def get_user_info(self):
        return self.__user_info
    
    
    """
    lobby state
    """

    def add_user(self, username: str) -> None:
        """
        [state required: lobby] 
        add a user to the users dictionary with necessary parameters
        @params -> username: the username of the player to be added
        @raises -> Exception
        """
        self.__check_state("lobby")

        # check if we have enough game slots
        if len(self.__user_info.keys()) < self.__user_limit:
            pass
        else:
            raise Exception("Too many users already in the game")
        
        # username checks
        if username.strip() == "":
            raise Exception("The user didn't enter anything")
        else:
            # Register the name to the game
            self.__user_info[username] =  {
                'submitted': [],
                'won': [],
                'points?': 0,
                'lobby_ready': 0,
                'all_names_submitted': 0,
            }

    
    
    def set_user_ready(self, username: str) -> None:
        """
        [state required: lobby] 
        Set a specific users ready attribute to 1
        @params -> username: the username of the player for the state to be changed
        @raises -> Exception
        """
        self.__check_state("lobby")

        # check user exists
        if self.__user_info.get(username, None) == None:
            raise Exception("User doesn't exist")

        # set the user to ready
        self.__user_info[username]['lobby_ready'] = 1


    def all_users(self) -> List[Tuple[str, str]]:
        """
        Get all usernames present and whether they are ready to proceed from the lobby
        @returns -> list of tuples in format [(username, 0 or 1), ..]
        """
        userReady = [(username, self.__user_info[username]['lobby_ready']) for username in self.__user_info.keys()]
        return userReady

    
    def change_state_to_input(self) -> None:
        """
        [state required: lobby] 
        change from lobby state to input state if everyone is ready
        @returns -> list of tuples in format [(username, 0 or 1), ..]
        @raises -> Exception
        """
        self.__check_state("lobby")

        # get a list of user states in [0,1,0,0, ...]
        ready_states = [self.__user_info[username]['lobby_ready'] for username in self.__user_info.keys()]
        # [1] * number of players
        expected = [1]*len(self.__user_info.keys())

        if ready_states == expected:
            self.__state = "input"
        else:
            raise Exception("Not everyone is ready!")


    """
    input state
    """

    def put(self, username: str, item: str) -> None:
        """
        [state required: input] 
        Append to the main_hat list if they have spare slots
        """
        self.__check_state("input")

        if item.strip() == "":
            # the user didn't enter anything 
            raise Exception("User didn't enter anything")
        else:
            pass

        if len(self.__user_info[username]['submitted']) < self.__name_limit + 1:
            # add item to user list
            self.__user_info[username]['submitted'].append(item)
            # add item to hat
            self.__hat.append(item)
        else:
            # the user has entered all their slots
            print(item)
            raise Exception("Too many items added")

    
    def users_input_ready(self):
        """
        [state required: input]
        Check if all users are ready, if they are move items to permanent hat and change the state
        """
        self.__check_state("input")

        # get a list of how many items each user has submitted in form [1,0,4,5, ...]
        ready_states = [len(self.__user_info[username]['submitted']) for username in self.__user_info.keys()]
        # [max number of possible items] * number of players
        expected = [self.__name_limit]*len(self.__user_info.keys())

        # check if everyone has the expected number
        if ready_states == expected:
            self.__state = "round1"
            # move all items from temp hat to permanent
            self.__permanent_hat = (item for item in self.__hat)
            # empty hat
            self.__hat = []
        else:
            raise Exception("Not everyone is ready!")


    """
    Round state
    """

    def pick(self):
        """
        choose a random entry from the main_hat list then add it to the used_hat list
        """
        # pick an entry

        pass


    """
    Round end state
    """

    def end_round(self):
        """
        move used hat to main hat after main hat is empty
        """
        pass

    
    """
    Game end state
    """

    def reset(self):
        """
        delete the object?
        """
        pass


    """
    private methods
    """

    def __check_state(self, state_required: str) -> None:
        """
        if not in expected state, raise
        @params -> state_required:
        @raises -> Exception
        """
        if self.get_state() == state_required:
            pass
        else:
            raise Exception(f"Not in the {state_required} state")


if __name__ == "__main__":
    # Start the lobby
    hatgame = HatGame()

    # Add players
    players = [
        "Player1",
        "Player2",
        "Player3"
    ]

    for player in players:
        hatgame.add_user(player)
    
    for player in players:
        hatgame.set_user_ready(player)
    
    hatgame.change_state_to_input()

    items = [
        "a",
        "b",
        "c", 
        "d",
        "e"
    ]

    player = "Player1"
    for item in items:
        print(f"{item}, {player}")
        hatgame.put(player, player + item)
    
    player = "Player2"
    for item in items:
        print(f"{item}, {player}")
        hatgame.put(player, player + item)
    
    player = "Player3"
    for item in items:
        print(f"{item}, {player}")
        hatgame.put(player, player + item)
    
    hatgame.users_input_ready()

    print(hatgame.get_state())

