DataClean Mobile
================

Run the app with `streamlit run app.py`.

Users can register with a unique username (3-32 letters, numbers, or underscores)
and a password between 8 and 128 characters, then log in with those credentials.
Passwords are stored as salted scrypt hashes in a local SQLite database. By
default the database is `users.db` beside `app.py`; set `DATACLEAN_AUTH_DB` to
use another database path.