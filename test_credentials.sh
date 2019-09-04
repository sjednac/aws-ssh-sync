#!/usr/bin/env bash
# https://stackoverflow.com/a/44850245/1535738

mkdir -p ~/.aws

cat >> ~/.aws/credentials << EOL
[testprofile]
aws_access_key_id = AKIAIO5FODNN7EXAMPLE
aws_secret_access_key = ABCDEF+c2L7yXeGvUyrPgYsDnWRRC1AYEXAMPLE
EOL
