FROM python:3.12-slim
WORKDIR /code

RUN apt-get update && apt-get install -y cron curl procps

COPY . /code

RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x /code/cron-task.sh
RUN echo "0 * * * * /code/cron-task.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/cozymeal-cron
RUN chmod 0644 /etc/cron.d/cozymeal-cron
RUN crontab /etc/cron.d/cozymeal-cron
RUN touch /var/log/cron.log

EXPOSE 5000

# Make entrypoint script executable
RUN chmod +x /code/entrypoint.sh

# Use entrypoint script for proper process management
ENTRYPOINT ["/code/entrypoint.sh"]
