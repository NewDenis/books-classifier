#!/bin/bash

set -e
set -x

python ./scripts/prepare_data.py --out-path ./data

s3cmd \
    --access_key $AWS_ACCESS_KEY_ID \
    --secret_key $AWS_SECRET_ACCESS_KEY \
    --host https://storage.yandexcloud.net \
    --region ru-central1 \
    --host-bucket "%(bucket)s.storage.yandexcloud.net" \
    -q \
    put ./data/datasets/raw/*.pqt s3://books-raw-data/prepared/
