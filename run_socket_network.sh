#!/bin/sh

# 1.获取输入参数
P=$1
N=$2
f=$3
B=$4
K=$5
MR=$6
per=$7
beginNum=$8
endNum=$9

echo "---- 当前运行协议输入参数为：P=$P, N=$N, f=$f, B=$B, K=$K, MR=$MR per=$per----"
IMAGE_NAME="bft"
IMAGE_TAG="latest"

echo "---- 开始循环启动容器 ----"
mkdir -p /home/lzh/workspace/data/logs/$IMAGE_NAME/$P/$N-$f-$B-$K

i=$beginNum
while [ "$i" -lt $((endNum + 1)) ]; do

  if [ $MR -eq 0 ]; then
    docker run --cpus=2 -m 4096m --rm -itd --name $IMAGE_NAME-$i --net=host \
      -v /home/lzh/workspace/project/dumbo_1029/hosts.config:/home/hosts.config \
      -v /home/lzh/workspace/data/keys:/home/keys \
      -v /home/lzh/workspace/data/logs/$IMAGE_NAME/$P/$N-$f-$B-$K:/home/log \
      $IMAGE_NAME:$IMAGE_TAG /bin/bash -c "nohup python3 run_socket_node_new.py --sid 'sidA' --id $i --N $N --f $f --B $B --K $K --P $P > /home/log/$IMAGE_NAME-$i.out"
    echo "---- 成功启动第【$i】个容器 ----"
  else
    shard_index=$((i / ($N / MR)))
    echo "---- 第【$i】个容器属于第【$shard_index】个分片，MR=$MR ----"
    docker run --cpus=2 -m 4096m --rm -itd --name $IMAGE_NAME-$i --net=host \
      -v /home/lzh/workspace/project/dumbo_1029/hosts.config:/home/hosts.config \
      -v /home/lzh/workspace/data/keys:/home/keys \
      -v /home/lzh/workspace/data/logs/$IMAGE_NAME/$P/$N-$f-$B-$K:/home/log \
      $IMAGE_NAME:$IMAGE_TAG /bin/bash -c "nohup python3 run_socket_node_new.py --sid 'sidA' --id $i --N $N --f $f --B $B --K $K --P $P --R $shard_index --MR $MR  --per $per > /home/log/$IMAGE_NAME-$i.out"
    echo "---- 成功启动第【$i】个容器 ----"
  fi
  i=$((i + 1))
done
