"""Entry point shim.

The implementation lives in :mod:`app.main`. This file exists so that the documented
``python bot.py`` command, the Dockerfile and the systemd units keep working; the
packaged ``dip-bot`` console script calls the same function.
"""

from app.main import main

if __name__ == "__main__":
    main()
