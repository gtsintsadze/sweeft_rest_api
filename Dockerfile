FROM python:3.9

RUN apt-get update && apt-get -y install cron
RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app/

COPY expired_links_removal_cron /etc/cron.d/expired_links_removal_cron
COPY . /usr/src/app/

RUN pip install --no-cache -r requirements.txt
RUN chmod 0644 /etc/cron.d/expired_links_removal_cron
RUN crontab /etc/cron.d/expired_links_removal_cron
RUN touch /var/log/cron.log

EXPOSE 8088

CMD cron
CMD ["python","app.py"]
