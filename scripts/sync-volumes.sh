#!/bin/bash
# Arg 1: $SYNC_INTERVAL, default 60 seconds
# Arg 2: $S3_BUCKET_NAME, default s3://mephisto-data
# Arg 3: $LOCAL_DIR, default current directory

SYNC_INTERVAL=${1:-60}
LOCAL_DIR=${2:-.}
S3_BUCKET_NAME=${3:-s3://mephisto-data}
AWS_ACCESS_KEY_ID=${4:-""}
AWS_SECRET_ACCESS_KEY=${5:-""}

trap "echo '[$(date)] Exit syncing script!'; exit;" SIGINT SIGTERM

if [ -z "$AWS_ACCESS_KEY_ID" ]
then
    echo "AWS_ACCESS_KEY_ID not set";
    exit 1;
fi

if [ -z "$AWS_SECRET_ACCESS_KEY" ]
then
    echo "AWS_SECRET_ACCESS_KEY not set";
    exit 1;
fi

export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY

while true; do
    echo "[$(date)] Syncing $LOCAL_DIR to $S3_BUCKET_NAME!"
    aws s3 sync $LOCAL_DIR $S3_BUCKET_NAME

    echo "[$(date)] Sync complete!"
    sleep $SYNC_INTERVAL
done

#  echo when interrupted