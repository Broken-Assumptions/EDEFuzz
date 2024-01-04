FROM --platform=linux/amd64 ubuntu:20.04

ENV TZ=Australia/Melbourne \
    DEBIAN_FRONTEND=noninteractive

# Install common dependencies
RUN apt-get -y update && \
    apt-get -y install sudo \ 
    tzdata \
    git \
    python3.10 \
    python3-pip \
    unzip \
    wget \
    curl \
    firefox \
    firefox-geckodriver

RUN apt-get install -y libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1

# Reference: https://gist.github.com/varyonic/dea40abcf3dd891d204ef235c6e8dd79

# Set up the Chrome PPA
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list

# Update the package list and install chrome
RUN apt-get update -y
RUN apt-get install -y google-chrome-stable

# Set up Chromedriver Environment variables
ENV CHROMEDRIVER_DIR /chromedriver
RUN mkdir $CHROMEDRIVER_DIR

# Download and install latest Chromedriver
RUN CHROMEDRIVER_VERSION=$(curl -sS https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE) && \
    wget -q --continue -P $CHROMEDRIVER_DIR https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip
#    wget -q --continue -P $CHROMEDRIVER_DIR https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip
RUN unzip $CHROMEDRIVER_DIR/chromedriver* -d $CHROMEDRIVER_DIR

# Download and install Chromedriver
# RUN wget -q --continue -P $CHROMEDRIVER_DIR "http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
# RUN unzip $CHROMEDRIVER_DIR/chromedriver* -d $CHROMEDRIVER_DIR

# Put Chromedriver into the PATH
ENV PATH $CHROMEDRIVER_DIR:$PATH

RUN python3 -m pip install --upgrade pip
RUN pip install selenium
RUN pip install selenium-wire

RUN pip install mysql-connector-python


# Add a new user ubuntu, pass: ubuntu
RUN groupadd ubuntu && \
    useradd -rm -d /home/ubuntu -s /bin/bash -g ubuntu -G sudo -u 1000 ubuntu -p "$(openssl passwd -1 ubuntu)"

RUN mv $CHROMEDRIVER_DIR/chromedriver-linux64/* $CHROMEDRIVER_DIR

RUN chown ubuntu:ubuntu $CHROMEDRIVER_DIR
RUN chown ubuntu:ubuntu $CHROMEDRIVER_DIR/chromedriver

# Use ubuntu as the default username
USER ubuntu
WORKDIR /home/ubuntu

# Set up environment variables
ENV WORKDIR="/home/ubuntu"
ENV EDEFUZZ_PATH="${WORKDIR}/edefuzz"
ENV EDEFUZZ_LOG="${WORKDIR}/edefuzz/log"
RUN mkdir $EDEFUZZ_PATH
RUN mkdir $EDEFUZZ_LOG


# Copy file from the host folder where Dockerfile is stored
COPY --chown=ubuntu:ubuntu ./ $EDEFUZZ_PATH/
