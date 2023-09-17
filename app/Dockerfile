FROM jayhuynh239/mephisto-uq:latest

ARG GIT_USER_EMAIL
ARG GIT_USER_NAME

ARG MTURK_TYPE
ARG MTURK_NAME
ARG MTURK_ACCESS_KEY_ID
ARG MTURK_SECRET_ACCESS_KEY

ARG DOTNETRC

SHELL ["/bin/bash", "-c"]

# Set working directory to /app
WORKDIR /mephisto/app

RUN mephisto metrics install

# Clear the content of /app
RUN rm -rf ./*

# Copy your application code to /app
COPY . .

RUN git config --global user.email "$GIT_USER_EMAIL"
RUN git config --global user.name "$GIT_USER_NAME"
RUN git config --global --add safe.directory '*'

RUN echo -e "$DOTNETRC" > /root/.netrc

RUN mephisto register "$MTURK_TYPE" name="$MTURK_NAME" access_key_id="$MTURK_ACCESS_KEY_ID" secret_access_key="$MTURK_SECRET_ACCESS_KEY"

WORKDIR webapp
RUN ./link_mephisto_task.sh
WORKDIR ..

CMD yes '\n' | yes 'y\n' | python3 deploy.py