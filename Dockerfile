FROM alpine:3.15

RUN apk update
RUN apk upgrade
RUN apk add --update --no-cache bash build-base gcc musl-dev python3-dev curl libc6-compat
RUN apk add --no-cache gcc g++ py-pip mysql-dev linux-headers libffi-dev openssl-dev

SHELL ["/bin/bash", "-c"]

# INSTALL REQUIRED PACKAGES
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

RUN apk add --update --no-cache git
RUN apk add --no-cache aws-cli

# Install node and npm
RUN apk add --update nodejs npm
RUN npm install -g npm && \
    npm update -g npm && \
    npm install -g yarn heroku


# ec2 architect requires `ssh-keygen` util, so we need to install it.
# Firstly, remove `yarn` repo as it causes error that stops building a container. Error:
# (Error: The repository 'https://dl.yarnpkg.com/debian stable InRelease' is not signed)
# RUN rm /etc/apt/sources.list.d/yarn.list
# RUN apk update
# RUN apk install keychain -y

COPY . /mephisto
RUN mkdir ~/.mephisto

# Create the main Mephisto data directory
RUN mkdir -p /mephisto/data

SHELL ["/bin/bash", "-c"]
# Write the mephisto config file manually for now to avoid prompt.
# For bash-style string $ expansion for newlines,
# we need to switch the shell to bash:
RUN echo $'core: \n  main_data_directory: /mephisto/data' >> ~/.mephisto/config.yml

WORKDIR /mephisto
RUN pip3 install -e .

RUN yarn install
RUN yarn build-all
RUN mephisto metrics install

CMD bash -c "sleep infinity"