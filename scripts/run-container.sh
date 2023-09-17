APP_NAME=${1:?"Specify 'APP_NAME' as argv[1]"}
HEROKU_API_KEY=${2:?"Specify 'HEROKU_API_KEY' as argv[2]"}
APP_ENV=${3:?"Specify 'APP_ENV' as argv[3]"}
M_TURK_PREVIEW_URL_PREFIX=${4:?"Specify 'M_TURK_PREVIEW_URL_PREFIX' as argv[4]"}
AWS_ACCESS_KEY_ID=${5:?"Specify 'AWS_ACCESS_KEY_ID' as argv[5]"}
AWS_SECRET_ACCESS_KEY=${6:?"Specify 'AWS_SECRET_ACCESS_KEY' as argv[6]"}



docker run -d --rm --init -v $APP_NAME-volume:/mephisto/data \
    --net mephistonginx_mephisto-net \
    --name $APP_NAME \
    -e HEROKU_API_KEY=$HEROKU_API_KEY \
    -e APP_ENV=$APP_ENV \
    -e APP_NAME=$APP_NAME \
    -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    $APP_NAME;

container_id=$(docker ps -q --filter ancestor=$APP_NAME --format="{{.ID}}");

echo "Running container $APP_NAME with id: $container_id";

if [ -z "$container_id" ]
then
    echo "Container $APP_NAME failed to start";
    exit 1;
fi

mkdir -p ~/logs/$APP_NAME/;

echo "Streaming logs from container $container_id to file ~/logs/$APP_NAME/$container_id-$(date +%s).log";
nohup docker logs -f $container_id > ~/logs/$APP_NAME/$container_id-$(date +%s).log &

echo "Waiting for MTurk preview URL: ";
timeout 1800 \
    sh -c "while ! docker logs -f $container_id| grep -q '$M_TURK_PREVIEW_URL_PREFIX'; \
            do sleep 1; done";


echo "MTurk preview URL: ";
docker logs $container_id;