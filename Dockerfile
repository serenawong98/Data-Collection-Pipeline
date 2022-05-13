# FROM python:3.9 
# RUN apt-get update

# #install system depend

# RUN apt-get install -y software-properties-common

# #Download and install Fire
# RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys A6DCF7707EBC211F
# RUN apt-add-repository "deb http://ppa.launchpad.net/ubuntu-mozilla-security/ppa/ubuntu bionic main" -y
# RUN apt-get update -y
# RUN apt-get install firefox -y


# # Download and install geckodriver
# RUN GECKODRIVER_VERSION=$(curl https://github.com/mozilla/geckodriver/releases | grep -Eo 'v0+.[0-9]+.[0-9]+' | head -1) && \
#     wget https://github.com/mozilla/geckodriver/releases/download/"$GECKODRIVER_VERSION"/geckodriver-"$GECKODRIVER_VERSION"-macos-aarch64.tar.gz && \
#     tar -xvzf geckodriver* && \
#     chmod +x geckodriver && \
#     mv geckodriver /usr/local/bin
#  ENV DISPLAY=:99


# #Install depend and cop files
# COPY . .
# RUN pip install -r requirements.txt
# CMD ["python3", "scrapper_class.py"]





# FOR LINUX ON AMD64 ARCH
FROM --platform=linux/amd64 python:3.9 
RUN apt-get update
#install system depend
RUN apt-get install -y software-properties-common
#Download and install Fire
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys A6DCF7707EBC211F
RUN apt-add-repository "deb http://ppa.launchpad.net/ubuntu-mozilla-security/ppa/ubuntu bionic main" -y
RUN apt-get update -y
RUN apt-get install firefox -y
# Download and install geckodriver
RUN GECKODRIVER_VERSION=$(curl https://github.com/mozilla/geckodriver/releases | grep -Eo 'v0+.[0-9]+.[0-9]+' | head -1) && \
    wget https://github.com/mozilla/geckodriver/releases/download/"$GECKODRIVER_VERSION"/geckodriver-"$GECKODRIVER_VERSION"-linux64.tar.gz && \
    tar -xvzf geckodriver-"$GECKODRIVER_VERSION"-linux64.tar.gz && \
    chmod +x geckodriver && \
    mv geckodriver /usr/local/bin
ENV DISPLAY=:99
#Install depend and cop files
COPY . .
RUN pip install -r requirements.txt
CMD ["python3", "scrapper_class.py"]





# # FOR CHROME
# FROM --platform=linux/amd64 python:3.9-slim-buster
# RUN  apt-get update \
#   && apt-get install -y wget \
#   && apt-get install -y gnupg \
#   && apt-get install -y curl
# RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
# RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
# RUN apt-get -y update
# RUN apt-get install -y google-chrome-stable
# RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
# RUN apt-get install -yqq unzip
# RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/
# COPY . .
# RUN pip install -r requirements.txt
# CMD ["python", "scrapper_class.py"]