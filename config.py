from types import SimpleNamespace

player_config = SimpleNamespace(
    port=8888,
    ip="127.0.0.1"
)

admin_config = SimpleNamespace(
    port=8888,
    ip="127.0.0.1"
)


def update_args(args, **kwargs):
    for key in kwargs:
        setattr(args, key, kwargs[key])


if __name__ == "__main__":
    update_args(player_config, **{"new": "new_val"})

