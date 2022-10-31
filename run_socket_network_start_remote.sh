#!/bin/sh

# 1.获取输入参数
P=$1
N=$2
f=$3
B=$4
K=$5
MR=$6
per=0
hosts1=$7
hosts2=$8
beginNum=$9
endNum=${10}
echo "---- 当前运行协议输入参数为：P=$P, N=$N, f=$f, B=$B, K=$K, MR=$MR per=$per----"
IMAGE_NAME="bft"
IMAGE_TAG="latest"

if [ $beginNum -eq 0 ]; then
  rm -rf hosts.config
  touch hosts.config
  i=$beginNum
  while [ "$i" -lt $((endNum + 1)) ]; do
    echo $i $hosts1 $hosts1 $((20000 + $((100 * $i)))) >>hosts.config
    echo "---- 写入第【$i】个节点的hosts.config文件：$i $hosts1 $hosts1 $((20000 + $((100 * $i)))) ----"
    i=$((i + 1))
  done
  while [ "$i" -lt $N ]; do
    echo $i $hosts2 $hosts2 $((20000 + $((100 * $i)))) >>hosts.config
    echo "---- 写入第【$i】个节点的hosts.config文件：$i $hosts2 $hosts2 $((20000 + $((100 * $i)))) ----"
    i=$((i + 1))
  done
  # 3.4.远程拷贝密钥到其他服务器
  scp /home/lzh/workspace/project/dumbo_1029/hosts.config root@172.22.110.18:/home/lzh/workspace/project/dumbo_1029/hosts.config
fi

# 2.构建基础镜像（若多台服务器，则需要推送到其他服务器）
docker stop $(docker ps -a | grep "$IMAGE_NAME:$IMAGE_TAG" | awk '{print $1}')
docker rm $(docker ps -a | grep "$IMAGE_NAME:$IMAGE_TAG" | awk '{print $1}')
docker rmi $(docker images | grep "$IMAGE_NAME:$IMAGE_TAG" | awk '{print $1}')
echo "---- 开始构建镜像 $IMAGE_NAME:$IMAGE_TAG ----"
docker build -t $IMAGE_NAME:$IMAGE_TAG .
echo "---- 成功构建镜像 $IMAGE_NAME:$IMAGE_TAG ----"

if [ $beginNum -eq 0 ]; then
  # 3.启动一个镜像作为可信第三方，生成公私钥（若是多台服务器，则需要远程发送到其他服务器）
  rm -rf /home/lzh/workspace/data/keys
  mkdir -p /home/lzh/workspace/data/keys
  # 3.1.通过if判断key-gen网桥是否存在，若存在则删除
  if [ "$(docker network ls | grep "key-network")" ]; then
    docker network rm key-network
  fi
  # 3.2.创建key-gen网桥
  docker network create -d bridge --subnet 172.140.0.0/16 key-network
  echo "---- 成功创建key-gen网桥 ----"
  # 3.3.启动key-gen容器
  docker run --rm -itd --name trusted-key --network=key-network -v /home/lzh/workspace/data/keys:/home/keys $IMAGE_NAME:$IMAGE_TAG /bin/bash -c "python3 run_trusted_key_gen.py --N $N --f $f"
  echo "---- 启动key-gen容器，生成密钥 ----"
  # 3.4.远程拷贝密钥到其他服务器
  scp -r /home/lzh/workspace/data/keys root@172.22.110.18:/home/lzh/workspace/data
fi

# 5.启动N个容器，i为容器编号，j为网桥编号
echo "---- 开始循环启动容器 ----"
mkdir -p /home/lzh/workspace/data/logs/$IMAGE_NAME/$P/$N-$f-$B-$K

i=$beginNum
while [ "$i" -lt $((endNum + 1)) ]; do

  if [ $MR -eq 0 ]; then
    docker run --cpus=2 -m 4096m --rm -itd --name $IMAGE_NAME-$i --net=host \
      -v /home/lzh/workspace/data/keys:/home/keys \
      -v /home/lzh/workspace/data/logs/$IMAGE_NAME/$P/$N-$f-$B-$K:/home/log \
      $IMAGE_NAME:$IMAGE_TAG /bin/bash -c "nohup python3 run_socket_node_new.py --sid 'sidA' --id $i --N $N --f $f --B $B --K $K --P $P > /home/log/$IMAGE_NAME-$i.out"
    echo "---- 成功启动第【$i】个容器 ----"
  else
    shard_index=$((i / ($N / MR)))
    echo "---- 第【$i】个容器属于第【$shard_index】个分片，MR=$MR ----"
    docker run --cpus=2 -m 4096m --rm -itd --name $IMAGE_NAME-$i --net=host \
      -v /home/lzh/workspace/data/keys:/home/keys \
      -v /home/lzh/workspace/data/logs/$IMAGE_NAME/$P/$N-$f-$B-$K:/home/log \
      $IMAGE_NAME:$IMAGE_TAG /bin/bash -c "nohup python3 run_socket_node_new.py --sid 'sidA' --id $i --N $N --f $f --B $B --K $K --P $P --R $shard_index --MR $MR  --per $per > /home/log/$IMAGE_NAME-$i.out"
    echo "---- 成功启动第【$i】个容器 ----"
  fi
  i=$((i + 1))
done
