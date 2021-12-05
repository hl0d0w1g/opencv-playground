#!/bin/sh

tmux new-session -d -s 'DEV'
tmux new-window -t $'DEV':1
tmux send-keys 'htop' C-m
tmux split-window -h 
tmux send-keys 'source venv/bin/activate' C-m 'cd webapp' C-m 'export FLASK_APP=webapp/server.py' C-m 'python3 webapp/server.py' C-m
tmux split-window -v
tmux -2 attach-session -d
