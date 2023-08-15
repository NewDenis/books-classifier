#!/bin/bash

set -e
set -x

mkdir ./data
mkdir ./data/datasets
mkdir ./data/datasets/raw

s3cmd \
    --access_key $AWS_ACCESS_KEY_ID \
    --secret_key $AWS_SECRET_ACCESS_KEY \
    --host https://storage.yandexcloud.net \
    --region ru-central1 \
    --host-bucket "%(bucket)s.storage.yandexcloud.net" \
    -q \
    sync s3://books-raw-data/prepared/ ./data/datasets/raw/

python ./scripts/train_and_save.py --data-path ./data
