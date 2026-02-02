#!/usr/bin/env bash


# find process
# kill it
# pull from github
# run the bot

# ----- vars ----
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_MAIN="bot_main.py"
SCRIPT_VENV=".venv"
LOG_FILE="app.log"
PID_FILE="app.pid"

cd "$SCRIPT_DIR"

# ----- find & kill process -----
if [[ -f "$PID_FILE" ]]; then
    OLD_PID = "$(cat "$PID_FILE")"
    if kill -0 "$OLD_PID" 2>/dev/null; then
        kill "$OLD_PID" 
        sleep 2
    fi
fi

# ----- pull from github -----
git fetch origin
git reset --hard -- origin/master

# ----- updating requirements -----
"$SCRIPT_VENV/bin/pip" install -r requirements.txt

# ----- run the bot -----
nohup "$SCRIPT_VENV/bin/python" "$SCRIPT_MAIN" > "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"