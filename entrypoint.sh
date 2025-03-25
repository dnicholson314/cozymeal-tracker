#!/bin/sh

# Start cron
echo "Starting cron service..."
cron
touch /var/log/cron.log

# Define cleanup function
cleanup() {
    echo "Received shutdown signal, cleaning up..."
    echo "Stopping cron service..."
    pkill cron

    if [ -n "$child" ]; then
        echo "Stopping gunicorn gracefully..."
        kill -TERM "$child"
        wait "$child"
    fi

    echo "All processes terminated, exiting entrypoint script"
    exit 0
}

# Set up signal handlers for graceful shutdown
trap cleanup 15 2

# Start gunicorn in the background and capture its PID
echo "Starting gunicorn server..."
gunicorn --bind 0.0.0.0:5000 --workers 2 app:app &
child=$!

# Log the main processes
echo "Entrypoint setup complete:"
echo "- Cron service running"
echo "- Gunicorn running with PID: $child"

# Keep the container running
echo "Container is now running. Use docker stop to terminate properly."
tail -f /var/log/cron.log &
wait "$child"
