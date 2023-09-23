FROM jayhuynh239/mephisto-uq:latest

ARG GIT_USER_EMAIL
ARG GIT_USER_NAME

ARG MTURK_TYPE
ARG MTURK_NAME
ARG MTURK_ACCESS_KEY_ID
ARG MTURK_SECRET_ACCESS_KEY

ARG DOTNETRC
ARG PROLIFIC_API_KEY
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY

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
RUN mephisto register prolific name=prolific api_key="$PROLIFIC_API_KEY"

RUN aws configure --profile mpt set aws_access_key_id $AWS_ACCESS_KEY_ID
RUN aws configure --profile mpt set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
RUN aws configure --profile mpt set region ap-southeast-2
RUN aws configure --profile mpt set output json

RUN aws s3 cp --profile mpt s3://mephisto-data/ec2/fallback.json /mephisto/mephisto/abstractions/architects/ec2/servers/fallback.json
RUN aws s3 cp --profile mpt s3://mephisto-data/ec2/mephisto-server-key.pem /mephisto/mephisto/abstractions/architects/ec2/keypairs/mephisto-server-key.pem
RUN chmod 400 /mephisto/mephisto/abstractions/architects/ec2/keypairs/mephisto-server-key.pem

WORKDIR webapp
RUN ./link_mephisto_task.sh
WORKDIR ..

CMD yes '\n' | yes 'y\n' | python3 deploy.py