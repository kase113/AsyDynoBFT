#!/bin/sh

# -------------------------------8节点--------------------------------------

# 1. 运行hbbft_shard_new，batchsize从1000到6000

i=1
while [ "$i" -lt 7 ]; do
  # batchsize=1000*i
  batchsize=$((1000 * i))
  sh ./run_socket_network_start_new.sh hbbft_shard_new 8 1 $batchsize 2 2
  while true; do
    echo "---- 开始扫描容器运行情况，hbbft_shard_new，N=8 f=1 B=$batchsize K=2 MR=2 ----"
    # 2.2 判断容器数量，如果不是8个，退出
    if [ $(docker ps -a | grep "bft" | wc -l) -eq 0 ]; then
      echo "---- 成功运行hbbft_shard_new，N=8 f=1 B=$batchsize K=2 MR=2 ----"
      break
    else
      sleep 10
      if [ $(docker ps -a | grep "bft" | wc -l) -lt 6 ]; then
        echo "---- 成功运行hbbft_shard_new，N=8 f=1 B=$batchsize K=2 ----"
        docker rm -f $(docker ps -a | grep "bft:latest" | awk '{print $1}')
        break
      fi
    fi
  done
  i=$((i + 1))
done

i=1
while [ "$i" -lt 7 ]; do
  # batchsize=1000*i
  batchsize=$((1000 * i))
  sh ./run_socket_network_start_new.sh hbbft_shard_new 16 1 $batchsize 2 4
  while true; do
    echo "---- 开始扫描容器运行情况，hbbft_shard_new，N=16 f=1 B=$batchsize K=2 MR=4 ----"
    # 2.2 判断容器数量，如果不是8个，退出
    if [ $(docker ps -a | grep "bft" | wc -l) -eq 0 ]; then
      echo "---- 成功运行hbbft_shard_new，N=16 f=1 B=$batchsize K=2 MR=4 ----"
      break
    else
      sleep 30
      if [ $(docker ps -a | grep "bft" | wc -l) -lt 14 ]; then
        echo "---- 成功运行hbbft_shard_new，N=16 f=1 B=$batchsize K=2 MR=4 ----"
        docker rm -f $(docker ps -a | grep "bft:latest" | awk '{print $1}')
        break
      fi
    fi
  done
  i=$((i + 1))
done

i=1
while [ "$i" -lt 7 ]; do
  # batchsize=1000*i
  batchsize=$((1000 * i))
  sh ./run_socket_network_start_new.sh hbbft_shard_new 32 1 $batchsize 2 8
  while true; do
    echo "---- 开始扫描容器运行情况，hbbft_shard_new，N=32 f=1 B=$batchsize K=2 MR=8 ----"
    # 2.2 判断容器数量，如果不是8个，退出
    if [ $(docker ps -a | grep "bft" | wc -l) -eq 0 ]; then
      echo "---- 成功运行hbbft_shard_new，N=32 f=1 B=$batchsize K=2 MR=2 ----"
      break
    else
      sleep 60
      if [ $(docker ps -a | grep "bft" | wc -l) -lt 30 ]; then
        echo "---- 成功运行hbbft_shard_new，N=32 f=1 B=$batchsize K=2 MR=8 ----"
        docker rm -f $(docker ps -a | grep "bft:latest" | awk '{print $1}')
        break
      fi
    fi
  done
  i=$((i + 1))
done

i=1
while [ "$i" -lt 7 ]; do
  # batchsize=1000*i
  batchsize=$((1000 * i))
  sh ./run_socket_network_start_new.sh hbbft_shard_new 36 1 $batchsize 2 9
  while true; do
    echo "---- 开始扫描容器运行情况，hbbft_shard_new，N=36 f=1 B=$batchsize K=2 MR=9 ----"
    # 2.2 判断容器数量，如果不是8个，退出
    if [ $(docker ps -a | grep "bft" | wc -l) -eq 0 ]; then
      echo "---- 成功运行hbbft_shard_new，N=32 f=4 B=$batchsize K=2 MR=2 ----"
      break
    else
      sleep 60
      if [ $(docker ps -a | grep "bft" | wc -l) -lt 34 ]; then
        echo "---- 成功运行hbbft_shard_new，N=36 f=1 B=$batchsize K=2 MR=9 ----"
        docker rm -f $(docker ps -a | grep "bft:latest" | awk '{print $1}')
        break
      fi
    fi
  done
  i=$((i + 1))
done

i=1
while [ "$i" -lt 7 ]; do
  # batchsize=1000*i
  batchsize=$((1000 * i))
  sh ./run_socket_network_start_new.sh hbbft_shard_new 40 1 $batchsize 2 10
  while true; do
    echo "---- 开始扫描容器运行情况，hbbft_shard_new，N=40 f=1 B=$batchsize K=2 MR=10 ----"
    # 2.2 判断容器数量，如果不是8个，退出
    if [ $(docker ps -a | grep "bft" | wc -l) -eq 0 ]; then
      echo "---- 成功运行hbbft_shard_new，N=40 f=4 B=$batchsize K=2 MR=2 ----"
      break
    else
      sleep 60
      if [ $(docker ps -a | grep "bft" | wc -l) -lt 38 ]; then
        echo "---- 成功运行hbbft_shard_new，N=40 f=1 B=$batchsize K=2 MR=10 ----"
        docker rm -f $(docker ps -a | grep "bft:latest" | awk '{print $1}')
        break
      fi
    fi
  done
  i=$((i + 1))
done

echo "---- 所有任务运行完毕 ----"
