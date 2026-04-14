"""
SiloPrompts CLI — start the web interface from the command line
"""

import argparse


def main():
    parser = argparse.ArgumentParser(
        prog='siloprompts',
        description='SiloPrompts — Personal AI Prompt Database'
    )
    parser.add_argument('--port', type=int, default=5000, help='Port to listen on (default: 5000)')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--prompts', default=None, help='Prompts directory path')
    parser.add_argument('--open', action='store_true', help='Open browser on start')
    parser.add_argument('--version', action='store_true', help='Show version and exit')
    args = parser.parse_args()

    from siloprompts import __version__

    if args.version:
        print(f'siloprompts {__version__}')
        return

    from siloprompts.web import create_app
    app = create_app(prompts_dir=args.prompts)

    if args.open:
        import webbrowser
        import threading
        threading.Timer(1.0, lambda: webbrowser.open(f'http://localhost:{args.port}')).start()

    import logging
    logging.getLogger('werkzeug').setLevel(logging.WARNING)

    print(f'SiloPrompts v{__version__}')
    print(f'Prompts: {app.prompts_dir}')
    print(f'Listening on http://{args.host}:{args.port}')
    app.run(host=args.host, port=args.port)


if __name__ == '__main__':
    main()
