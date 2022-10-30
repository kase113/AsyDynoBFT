#!/bin/sh


N=$1
f=$2

docker run --rm -itd --name trusted-key \
  -v /home/lzh/workspace/data/keys:/home/keys bft:latest /bin/bash -c "python3 run_trusted_key_gen.py --N $N --f $f"
