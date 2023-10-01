#!/bin/bash

APP_NAME=${1:?"Specify 'APP_NAME' as argv[1]"}
HEROKU_API_KEY=${2:?"Specify 'HEROKU_API_KEY' as argv[2]"}
APP_ENV=${3:?"Specify 'APP_ENV' as argv[3]"}
M_TURK_PREVIEW_URL_PREFIX=${4:?"Specify 'M_TURK_PREVIEW_URL_PREFIX' as argv[4]"}
AWS_ACCESS_KEY_ID=${5:?"Specify 'AWS_ACCESS_KEY_ID' as argv[5]"}
AWS_SECRET_ACCESS_KEY=${6:?"Specify 'AWS_SECRET_ACCESS_KEY' as argv[6]"}

LOG_TIME=(date +%s)

mkdir -p ~/app-data/$APP_NAME-$LOG_TIME

docker run -d --rm --init -v ~/app-data/$APP_NAME-$LOG_TIME:/mephisto/data \
    --net mephistonginx_mephisto-net \
    --name $APP_NAME \
    -e APP_ENV=$APP_ENV \
    -e APP_NAME=$APP_NAME \
    $APP_NAME;

container_id=$(docker ps -q --filter ancestor=$APP_NAME --format="{{.ID}}");

echo "Running container $APP_NAME with id: $container_id";

if [ -z "$container_id" ]
then
    echo "Container $APP_NAME failed to start";
    exit 1;
fi

mkdir -p ~/logs/$APP_NAME/;

LOG_FILE="$HOME/logs/$APP_NAME/$container_id-$LOG_TIME.log";
echo "Streaming logs from container $container_id to file $LOG_FILE";
DOCKER_LOGS=$(docker inspect --format='{{.LogPath}}' $container_id);
sudo ln "$DOCKER_LOGS" "$LOG_FILE";
sudo chmod 777 "$LOG_FILE";

echo "Waiting for confirmation from providers: ";

timeout 1800 \
    sh -c "while ! grep '$M_TURK_PREVIEW_URL_PREFIX' '$LOG_FILE'; \
            do sleep 1; done";


echo "Matched confirmation: ";
grep $M_TURK_PREVIEW_URL_PREFIX $LOG_FILE;
docker logs $container_id;
