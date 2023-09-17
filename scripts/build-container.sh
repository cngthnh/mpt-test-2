# #!/bin/bash

REPO_DIR=${1:?"Specify 'REPO_DIR' as argv[1]"}
APP_NAME=${2:?"Specify 'APP_NAME' as argv[2]"}
USER_EMAIL=${3:?"Specify 'USER_EMAIL' as argv[3]"}
USER_NAME=${4:?"Specify 'USER_NAME' as argv[4]"}
HEROKU_API_KEY=${5:?"Specify 'HEROKU_API_KEY' as argv[5]"}
MTURK_TYPE=${6:?"Specify 'MTURK_TYPE' as argv[6]"}
MTURK_NAME=${7:?"Specify 'MTURK_NAME' as argv[7]"}
MTURK_ACCESS_KEY_ID=${8:?"Specify 'MTURK_ACCESS_KEY_ID' as argv[8]"}
MTURK_SECRET_ACCESS_KEY=${9:?"Specify 'MTURK_SECRET_ACCESS_KEY' as argv[9]"}
DOTNETRC=${10:?"Specify 'DOTNETRC' as argv[10]"}

echo "REPO_DIR::: $REPO_DIR"
echo "APP_NAME: $APP_NAME"

cd $REPO_DIR && git pull
cd $REPO_DIR/app

docker exec -t $(docker ps -a -q --filter ancestor="$APP_NAME" --format="{{.ID}}") bash -c 'pkill -SIGINT -f python3 && sleep 5' || true

echo "Wait for 10 seconds for the container to stop"
# wait for 10 seconds for the container to stop
sleep 10

docker exec -t $(docker ps -a -q --filter ancestor="$APP_NAME" --format="{{.ID}}") bash -c 'pkill -SIGINT -f python3 && sleep 5' || true
echo "Send SIGINT to all containers with image tag: $APP_NAME"

echo "Wait for 10 seconds for the container to stop"
# wait for 10 seconds for the container to stop
sleep 10

docker kill -s SIGINT $(docker ps -a -q --filter ancestor="$APP_NAME" --format="{{.ID}}") || true


echo "Stop and remove all containers with image tag: $APP_NAME"
docker rm $(docker stop $(docker ps -q -a --filter ancestor="$APP_NAME" --format="{{.ID}}")) || true

echo "Pulling latest docker image: jayhuynh239/mephisto-uq:latest"
docker pull jayhuynh239/mephisto-uq:latest

docker build -t $APP_NAME \
        --build-arg GIT_USER_EMAIL=$USER_EMAIL \
        --build-arg GIT_USER_NAME=$USER_NAME \
        --build-arg MTURK_TYPE=$MTURK_TYPE \
        --build-arg MTURK_NAME=$MTURK_NAME \
        --build-arg MTURK_ACCESS_KEY_ID=$MTURK_ACCESS_KEY_ID \
        --build-arg MTURK_SECRET_ACCESS_KEY=$MTURK_SECRET_ACCESS_KEY \
        --build-arg DOTNETRC="$DOTNETRC" \
        --build-arg HEROKU_API_KEY=$HEROKU_API_KEY \
        .
