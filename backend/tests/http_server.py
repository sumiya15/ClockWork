"""Test-only Uvicorn runner with private stdin shutdown (no shutdown HTTP route)."""
import argparse
import os
import sys
import threading
import uvicorn


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, required=True)
    args = parser.parse_args()
    server = uvicorn.Server(uvicorn.Config('backend.main:app', host='127.0.0.1', port=args.port,
                                          timeout_graceful_shutdown=3, timeout_keep_alive=1))

    def shutdown_on_stdin():
        sys.stdin.readline()
        server.should_exit = True

    threading.Thread(target=shutdown_on_stdin, daemon=True).start()
    server.run()
    # All HTTP work has finished. Close pools explicitly before exiting this
    # test-only subprocess; Windows/Python worker finalizers can otherwise linger.
    from backend.auth import cached_engine
    from backend.database import database_path
    cached_engine(str(database_path())).dispose()
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)
