from argparse import ArgumentParser


def parse_port():
    """return port parsed from cli"""
    parser = ArgumentParser(
        description="Parses port number for tic-tac-toe server"
    )

    parser.add_argument("port",
                        help="port number for tic-tac-toe server")

    args = parser.parse_args()
    return args.port
