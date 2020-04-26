import random
from typing import List, Tuple, Dict, Callable
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

    def __init__(self, number_of_players=10):
        """
        @params -> None
        @returns -> HatGame object
        """
        
        """ public """
        self.id = str(uuid.uuid4()) # id of party        

        """ private """
        self.__name_limit = int(25/number_of_players) # number of names a user can enter

        self.__user_limit = number_of_players # maximum number of players allowed

        self.__permanent_hat = () # immutable store of names once all added

        self.__hat = [] # keeps active names (ones that haven't been picked yet)

        self.__user_info = {} # dictionary to store user state

        self.__state = "lobby"

        self.__change = 0 # updated to 1 everytime a function runs

        self.__current_player = None

        self.__current_item = None


    # TODO: we get errors here even though it's valid code
    def attempt(func: Callable):
        """
        Error handles any function
        Function must not return something normally
        """
        def inner(self, *args, **kwargs) -> str:
            try:
                result = func(self, *args, **kwargs)
                if result == None:
                    self.set_change()
                    return "Success"
                else:
                    self.set_change()
                    return result

            except Exception as e:
                # function failed
                return e.args[0]
        return inner


    def get_state(self) -> str:
        """
        hatgame state
        @returns -> state: can be one of [lobby, input, round1, round1_results, ... , finished]
        """
        return self.__state
    

    def get_user_info(self):
        return self.__user_info
    

    def all_users(self) -> Dict[str, str]:
        """
        INFORMATION FUNCTION
        Get all usernames present and whether they are ready to proceed from the lobby
        @returns -> list of tuples in format [(username, 0 or 1), ..]
        """
        userReady = {username: self.__user_info[username]['lobby_ready'] for username in self.__user_info.keys()}
        return userReady
    

    def user_finished(self, username: str) -> bool:
        """
        INFORMATION FUNCTION
        if the user has submitted all thier names, return true, else false
        """
        if len(self.__user_info[username]['submitted']) == self.__name_limit:
            return True
        else:
            return False
    

    def user_input_left(self, username: str) -> int:
        """
        INFORMATION FUNCTION
        """
        return self.__name_limit - len(self.__user_info[username]['submitted'])
    

    def current_player(self):
        """
        INFORMATION FUNCTION
        """
        return self.__current_player
    
    
    def current_item(self):
        """
        INFORMATION FUNCTION
        """
        return self.__current_item
    

    def all_players_except(self, username: str) -> List[str]:
        """
        INFORMATION FUNCTION
        """
        players = list(self.__user_info.keys())
        players.remove(username)
        return players


    """
    Change management 
    """
    
    def has_changed(self, username):
        return self.__user_info[username]['change']
    
    
    def reset_change(self, username):
        self.__user_info[username]['change'] = 0

    
    def set_change(self):
        # need to go through all users and set change
        for username in self.__user_info.keys():
            self.__user_info[username]['change'] = 1

    
    """
    lobby state
    """

    @attempt
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
                'lobby_ready': "❌",
                'change': 0,
                'chosen': []
            }

    
    @attempt
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
        self.__user_info[username]['lobby_ready'] = "✔"

    
    @attempt
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
        expected = ["✔"]*len(self.__user_info.keys())

        if ready_states == expected:
            self.__state = "input"
            self.__name_limit = int(25/len(expected)) # number of names a user can enter
            if self.__name_limit > 6:
                self.__name_limit = 6
        else:
            raise Exception("Not everyone is ready!")


    """
    input state
    """

    @attempt
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

        if len(self.__user_info[username]['submitted']) < self.__name_limit:
            # add item to user list
            self.__user_info[username]['submitted'].append(item)
            # add item to hat
            self.__hat.append(item)
        else:
            raise Exception("Too many items added")

    
    @attempt
    def users_input_ready(self) -> None:
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
            self.__state = "1"
            # move all items from temp hat to permanent
            self.__permanent_hat = (item for item in self.__hat)
            self.__users_to_go = list(self.__user_info.keys())
        else:
            raise Exception("Not everyone is ready!")


    """
    Round state
    """

    @attempt
    def pick(self):
        """
        [state required: round number]
        pick a user then 
        choose a random entry from the main_hat list then add it to the used_hat list
        """
        # enure we are in a round state
        if self.get_state() in ['1', '2', '3']:
            state = self.get_state()
        self.__check_state(state)


        # if been through users, refresh list
        if len(self.__users_to_go) == 0:
            self.__users_to_go = list(self.__user_info.keys())

        # pick user
        try:
            print(self.__users_to_go)
            user = self.__users_to_go.pop(random.randint(0,len(self.__users_to_go)-1))
            self.__current_player = user
        except:
            raise Exception("User picking didn't work")

        # give them a random item
        try:
            print(self.__hat)
            item = self.__hat.pop(random.randint(0,len(self.__hat)-1))
            self.__current_item = item
        except:
            raise Exception("Item picking didn't work")


    @attempt
    def choose(self, username, picked_username):
        """
        [state required: round number]
        """
        # enure we are in a round state
        if self.get_state() in ['1', '2', '3']:
            state = self.get_state()
        self.__check_state(state)

        # check it's the correct player choosing
        
        # add picked_username to username chosen

        # add item to picked_username won

        pass


    @attempt
    def change_round(self):
        """
        [state required: round number]
        if all users have gone
        1 -> 2 -> 3 -> end
        """
        # enure we are in a round state
        if self.get_state() in ['1', '2', '3']:
            state = self.get_state()
        self.__check_state(state)

        # if the hat is empty, change state
        if len(self.__hat) == 0:
            state = self.get_state()
            if state == "1":
                self.end_round()
                self.__state = "2"
            elif state == "2":
                self.end_round()
                self.__state = "3"
            elif state == "3":
                self.end_round()
                self.__state = "end"
            else:
                pass
        else:
            raise Exception("Round hasn't ended yet")

    
    @attempt
    def end_round(self):
        """
        move used hat to main hat after main hat is empty
        """
        # copy permanent hat to hat
        print(self.__hat)
        print(self.__permanent_hat)
        self.__hat = list(self.__permanent_hat)
        print(self.__permanent_hat)


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
        "e",
        "f"
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
    
    # change to round 1
    hatgame.users_input_ready()


    print(hatgame.pick())
    print(hatgame.change_round())
    print(hatgame.current_player())
    print(hatgame.current_item())
    print(hatgame.get_state())

