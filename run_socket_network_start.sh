#!/bin/sh

# 1.获取输入参数
P=$1
N=$2
f=$3
B=$4
K=$5
MR=$6
echo "---- 当前运行协议输入参数为：P=$P, N=$N, f=$f, B=$B, K=$K, MR=$MR ----"
IMAGE_NAME="bft"
IMAGE_TAG="latest"

# 5.根据网桥生成 hosts.config 文件，每四个节点为一组，每组节点共享一个网桥
# 5.1.删除旧的hosts.config文件
rm -rf hosts.config
touch hosts.config
# 5.2.生成新的hosts.config文件，最后一位ip从k=10开始
i=0
k=10
while [ "$i" -lt $N ]; do
  j=$((i / 256))
  echo $i 172.10$j.0.$k 172.10$j.0.$k $((10000 + $((100 * $i)))) >>hosts.config
  echo "---- 写入第【$i】个节点的hosts.config文件：$i 172.10$j.0.$k 172.10$j.0.$k $((10000 + $((100 * $i)))) ----"
  i=$((i + 1))
  k=$((k + 1))
done

# 2.构建基础镜像（若多台服务器，则需要推送到其他服务器）
docker stop $(docker ps -a | grep "$IMAGE_NAME:$IMAGE_TAG" | awk '{print $7}')
docker rm $(docker ps -a | grep "$IMAGE_NAME:$IMAGE_TAG" | awk '{print $8}')
docker rmi $(docker images | grep "$IMAGE_NAME:$IMAGE_TAG" | awk '{print $9}')
echo "---- 开始构建镜像 $IMAGE_NAME:$IMAGE_TAG ----"
docker build -t $IMAGE_NAME:$IMAGE_TAG .
echo "---- 成功构建镜像 $IMAGE_NAME:$IMAGE_TAG ----"

# 3.启动一个镜像作为可信第三方，生成公私钥（若是多台服务器，则需要远程发送到其他服务器）
rm -rf /home/lzh/keys
mkdir -p /home/lzh/keys
# 3.1.通过if判断key-gen网桥是否存在，若存在则删除
if [ "$(docker network ls | grep "key-network")" ]; then
  docker network rm key-network
fi
# 3.2.创建key-gen网桥
docker network create -d bridge --subnet 172.140.0.0/16 key-network
echo "---- 成功创建key-gen网桥 ----"
# 3.3.启动key-gen容器
docker run --rm -itd --name trusted-key --network=key-network -v /home/lzh/bft/keys:/home/keys $IMAGE_NAME:$IMAGE_TAG /bin/bash -c "python3 run_trusted_key_gen.py --N $N --f $f"
echo "---- 启动key-gen容器，生成密钥 ----"
# 3.4.远程拷贝密钥到其他服务器
#scp -r  /root/.ssh/id_rsa /home/lzh/keys root@172.22.110.137:/home/lzh/keys

# 4.创建网桥，根据节点数量N，每四个容器为一组，每组容器共享一个网桥，例如，N=4，则创建一个网桥，N=5，则创建两个网桥
# 4.1.计算需要创建的网桥数量
bridge_num=$((N / 256))
if [ $((N % 256)) -ne 0 ]; then
  bridge_num=$((bridge_num + 1))
fi
echo "---- 网桥数量为：$bridge_num ----"
# 4.2.创建网桥
i=0
while [ "$i" -lt $bridge_num ]; do
  if [ "$(docker network ls | grep "bft-network-$i")" ]; then
    docker network rm bft-network-$i
  fi
  docker network create -d bridge --subnet 172.10$i.0.0/16 bft-network-$i
  echo "---- 成功创建第【$i】个网桥：bft-network-$i ----"
  i=$((i + 1))
done

# 5.启动N个容器，i为容器编号，j为网桥编号
echo "---- 开始循环启动容器 ----"
i=0
k=10
mkdir -p /home/lzh/logs/$IMAGE_NAME/$P/$N-$f-$B-$K
while [ "$i" -lt $N ]; do
  # 5.1.计算容器属于哪个网桥
  bridge_index=$((i / 256))
  echo "---- 正在启动第【$i】个容器，容器名称【$IMAGE_NAME-$i】，容器IP【172.10$bridge_index.0.$k:$((10000 + $((100 * $i))))】 ----"

  if [ $MR -eq 0 ]; then
    docker run --rm -itd --name $IMAGE_NAME-$i --network=bft-network-$bridge_index --ip 172.10$bridge_index.0.$k \
      -p $((10000 + $((100 * $i)))):$((10000 + $((100 * $i)))) \
      -v /home/lzh/keys:/home/keys \
      -v /home/lzh/logs/$IMAGE_NAME/$P/$N-$f-$B-$K:/home/log \
      $IMAGE_NAME:$IMAGE_TAG /bin/bash -c "nohup python3 run_socket_node_new.py --sid 'sidA' --id $i --N $N --f $f --B $B --K $K --P $P > /home/log/$IMAGE_NAME-$i.out"
    echo "---- 成功启动第【$i】个容器 ----"
    #    # 5.3.将当前容器和其他网桥连接起来，并且绑定ip
    #    j=0
    #    echo "---- 开始循环连接其他网桥 ----"
    #    echo "---- 网桥数量为【$bridge_num】，当前容器属于第【$bridge_index】个网桥 ----"
    #    while [ "$j" -lt $bridge_num ]; do
    #      if [ "$j" -ne "$bridge_index" ]; then
    #        echo "---- 正在连接第【$j】个网桥 ----"
    #        docker network connect --ip 172.10$j.0.$k bft-network-$j $IMAGE_NAME-$i
    #        echo "---- 成功将第【$i】个容器 $IMAGE_NAME-$i 连接到第【$j】个网桥 bft-network-$j ----"
    #      fi
    #      j=$((j + 1))
    #    done
  else
    shard_index=$((i / ($N / MR)))
    echo "---- 第【$i】个容器属于第【$shard_index】个分片，MR=$MR ----"
    docker run --rm -itd --name $IMAGE_NAME-$i --network=bft-network-$bridge_index --ip 172.10$bridge_index.0.$k \
      -p $((10000 + $((100 * $i)))):$((10000 + $((100 * $i)))) \
      -v /home/lzh/keys:/home/keys \
      -v /home/lzh/logs/$IMAGE_NAME/$P/$N-$f-$B-$K:/home/log \
      $IMAGE_NAME:$IMAGE_TAG /bin/bash -c "nohup python3 run_socket_node_new.py --sid 'sidA' --id $i --N $N --f $f --B $B --K $K --P $P --R $shard_index --MR $MR> /home/log/$IMAGE_NAME-$i.out"
    echo "---- 成功启动第【$i】个容器 ----"
    #    # 5.3.将当前容器和其他网桥连接起来，并且绑定ip
    #    j=0
    #    echo "---- 开始循环连接其他网桥 ----"
    #    echo "---- 网桥数量为【$bridge_num】，当前容器属于第【$bridge_index】个网桥 ----"
    #    while [ "$j" -lt $bridge_num ]; do
    #      if [ "$j" -ne "$bridge_index" ]; then
    #        echo "---- 正在连接第【$j】个网桥 ----"
    #        docker network connect --ip 172.10$j.0.$k bft-network-$j $IMAGE_NAME-$i
    #        echo "---- 成功将第【$i】个容器 $IMAGE_NAME-$i 连接到第【$j】个网桥 bft-network-$j ----"
    #      fi
    #      j=$((j + 1))
    #    done
  fi
  i=$((i + 1))
  k=$((k + 1))
done
