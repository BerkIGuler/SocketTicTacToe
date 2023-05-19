from types import SimpleNamespace
import random

# players and admins comm configs
player_config = SimpleNamespace(
    port=6006,
    ip="127.0.0.1"
)

admin_config = SimpleNamespace(
    port=6006,
    ip="127.0.0.1"
)

# list to assign random names to players
player_names = [
    "Liam",
    "Noah",
    "Oliver",
    "James",
    "Elijah",
    "William",
    "Henry",
    "Lucas",
    "Benjamin",
    "Theodore",
    "Mateo",
    "Levi",
    "Sebastian",
    "Daniel",
    "Jack",
    "Michael",
    "Alexander",
    "Owen",
    "Asher",
    "Samuel",
    "Ethan",
    "Leo"
]


def sample_name():
    """samples a random name from a list of names"""
    return random.choice(player_names)


def update_args(args, **kwargs):
    """"Updates a namespace object with given kwargs"""
    for key in kwargs:
        setattr(args, key, kwargs[key])
