import argparse

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--path', '-p', type=str, default='./')
arg_parser.add_argument('--server', '-s', action='store_true', default=False)
arg_parser.add_argument('--client', '-c', action='store_true', default=False)
arg_parser.add_argument('--reset', '-r', action='store_true', default=False)
arg_parser.add_argument('--name', '-n', type=str, default='worker')
arg_parser.add_argument('--db-host', type=str, default='localhost')
arg_parser.add_argument('--db-user', type=str, default='root')
arg_parser.add_argument('--db-pass', type=str, default='1234')
args, _ = arg_parser.parse_known_args()
print(f"[Args] Running from {args.path} (specify with --path/-p)")
print(f"[Args] Server={args.server} Client={args.client} (specify with --server/--client)")