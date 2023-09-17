#!/bin/bash
APP_NAME=${1:-temp-app}
S3_BUCKET_NAME=${2:-s3://mephisto-data}

mephisto_data_root="/mephisto/data"

echo "[$(date)] Syncing $mephisto_data_root to $S3_BUCKET_NAME/data-v2/$APP_NAME!"
aws s3 sync $mephisto_data_root $S3_BUCKET_NAME/data-v2/$APP_NAME

echo "[$(date)] Sync complete!"