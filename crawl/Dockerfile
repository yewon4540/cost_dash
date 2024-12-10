FROM ubuntu:24.04

# WORKDIR /home
WORKDIR /home/crawl

#COPY import_data.py /home
#COPY data.csv /home
#COPY download /home
# COPY . /home
COPY . /home/crawl

# 기본 환경 설치
RUN apt update \
    && apt install -y --no-install-recommends apt-utils
RUN rm -rf /var/lib/apt/lists/*

RUN apt update && apt upgrade -y
RUN apt install -y cron
RUN apt install -y python3-full
RUN apt install -y python3-pip
RUN apt install -y wget unzip curl

RUN python3 -m venv /home/crawl/.venv
# RUN python3 -m venv /home/.venv

RUN /home/crawl/.venv/bin/pip --no-cache-dir install --upgrade setuptools wheel --break-system-packages
# sudo 설치
RUN apt install -y sudo

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
RUN sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'

RUN apt update

RUN apt install -y google-chrome-stable

RUN apt install -y libglib2.0-0 libnss3 libfontconfig1

# 크롬 드라이버설치
RUN LATEST=$(wget -q -O - https://chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget https://chromedriver.storage.googleapis.com/$LATEST/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm chromedriver_linux64.zip

COPY ./crontabfile /etc/cron.d/
RUN chmod 777 /etc/cron.d/crontabfile
RUN echo >> /etc/cron.d/crontabfile
RUN crontab /etc/cron.d/crontabfile

# COPY requirements.txt /home
# RUN /home/.venv/bin/pip install -r /home/requirements.txt
COPY requirements.txt /home/crawl
RUN /home/crawl/.venv/bin/pip install -r /home/crawl/requirements.txt

# cron 트리거 설정
RUN echo "#!/bin/bash\n\
service cron start\n\
tail -f /dev/null" > /cron_start.sh

# 실행 권한 ㄱㄱ
RUN chmod +x /cron_start.sh

CMD ["/cron_start.sh"]
