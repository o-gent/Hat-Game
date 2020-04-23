import random
from typing import List, Tuple


class HatGame:
    """
    The hat game 
    States

    - Blank new game
    
    - Lobby for users to join

    - Everyone presses ready
    
    - All users enter hat names, then wait for all users to finish
    
    - Round X
        - 
    
    """

    def __init__(self):
        """
        
        """
        self.__main_hat = []
        self.__used_hat = []
        self.__user_info = {}

        self.__user_template = {
            'submitted': [],
            'won': [],
            'points?': 0,
            'lobby_ready': 0,
            'all_names_submitted': 0,
        }
    

    def add_user(self, username: str):
        """
        add a user to the users dictionary with necessary parameters
        """
        if username.strip() == "":
            # the user didn't enter anything 
            pass
        else:
            self.__user_info[username] = self.__user_template
    
    
    def set_user_ready(self, user: str) -> None:
        """
        Set a specific users ready attribute to 1
        """
        self.__user_info[user]['lobby_ready'] = 1


    def all_users(self) -> List[Tuple[str, str]]:
        userReady = [(user, self.__user_info[user]['lobby_ready']) for user in self.__user_info.keys()]
        return userReady
    

    def funcname(self, parameter_list):
        pass


    def put(self, username: str, item: str) -> None:
        """
        Append to the main_hat list
        """
        if item.strip() == "":
            # the user didn't enter anything 
            pass
        else:
            if len(self.__user_info[username]['submitted']) < 5:
                self.__user_info[username]['submitted'].append(item)
                self.__main_hat.append(item)


    def pick(self):
        """
        choose a random entry from the main_hat list then add it to the used_hat list
        """
        # pick an entry

        pass

    
    def end_round(self):
        """
        move used hat to main hat after main hat is empty
        """
        pass

    
    def reset(self):
        """
        delete the object?
        """
        pass

    
    def display_main_hat(self):
        print(self.__main_hat)

    """
    private methods
    """

    pass


if __name__ == "__main__":
    hatgame = HatGame()
    hatgame.display_main_hat()
    hatgame.put("santa")
    hatgame.display_main_hat()
    hatgame.put("big santa")
    hatgame.display_main_hat()
