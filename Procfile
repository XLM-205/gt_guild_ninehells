web: cd ./website && gunicorn -c gunicorn_hooks.py --bind=0.0.0.0:$PORT startup:app --workers $(($CORES * 2 + 1)) --threads=$THREADS
