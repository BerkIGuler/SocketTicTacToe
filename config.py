from types import SimpleNamespace
import random


player_config = SimpleNamespace(
    port=6006,
    ip="127.0.0.1"
)

admin_config = SimpleNamespace(
    port=6006,
    ip="127.0.0.1"
)

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
    return random.choice(player_names)


def update_args(args, **kwargs):
    for key in kwargs:
        setattr(args, key, kwargs[key])


if __name__ == "__main__":
    update_args(player_config, **{"new": "new_val"})
    print(sample_name())
