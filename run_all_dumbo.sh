#!/bin/sh

# -------------------------------8节点--------------------------------------

# 1. 运行dumbo，batchsize从1000到6000

i=1
while [ "$i" -lt 7 ]; do
  # batchsize=1000*i
  batchsize=$((1000 * i * 8))
  sh ./run_socket_network_start.sh dumbo 8 2 $batchsize 2 0
  while true; do
    echo "---- 开始扫描容器运行情况，dumbo，N=8 f=2 B=$batchsize K=2  ----"
    # 2.2 判断容器数量，如果不是8个，退出
    if [ $(docker ps -a | grep "bft" | wc -l) -eq 0 ]; then
      echo "---- 成功运行dumbo，N=8 f=2 B=$batchsize K=2  ----"
      break
    else
      sleep 10
      if [ $(docker ps -a | grep "bft" | wc -l) -lt 5 ]; then
        echo "---- 成功运行dumbo，N=8 f=2 B=$batchsize K=2 ----"
        docker rm -f $(docker ps -a | grep "bft:latest" | awk '{print $1}')
        break
      fi
    fi
  done
  i=$((i + 1))
done

#i=1
#while [ "$i" -lt 7 ]; do
#  # batchsize=1000*i
#  batchsize=$((1000 * i * 16))
#  sh ./run_socket_network_start.sh dumbo 16 4 $batchsize 2 0
#  while true; do
#    echo "---- 开始扫描容器运行情况，dumbo，N=16 f=4 B=$batchsize K=2 ----"
#    # 2.2 判断容器数量，如果不是8个，退出
#    if [ $(docker ps -a | grep "bft" | wc -l) -eq 0 ]; then
#      echo "---- 成功运行dumbo，N=16 f=4 B=$batchsize K=2 ----"
#      break
#    else
#      sleep 30
#      if [ $(docker ps -a | grep "bft" | wc -l) -lt 9 ]; then
#        echo "---- 成功运行dumbo，N=16 f=4 B=$batchsize K=2 ----"
#        docker rm -f $(docker ps -a | grep "bft:latest" | awk '{print $1}')
#        break
#      fi
#    fi
#  done
#  i=$((i + 1))
#done
#
#i=1
#while [ "$i" -lt 7 ]; do
#  # batchsize=1000*i
#  batchsize=$((1000 * i * 32))
#  sh ./run_socket_network_start.sh dumbo 32 8 $batchsize 2 0
#  while true; do
#    echo "---- 开始扫描容器运行情况，dumbo，N=32 f=8 B=$batchsize K=2 ----"
#    # 2.2 判断容器数量，如果不是8个，退出
#    if [ $(docker ps -a | grep "bft" | wc -l) -eq 0 ]; then
#      echo "---- 成功运行dumbo，N=32 f=8 B=$batchsize K=2 ----"
#      break
#    else
#      sleep 30
#      if [ $(docker ps -a | grep "bft" | wc -l) -lt 20 ]; then
#        echo "---- 成功运行dumbo，N=32 f=8 B=$batchsize K=2 ----"
#        docker rm -f $(docker ps -a | grep "bft:latest" | awk '{print $1}')
#        break
#      fi
#    fi
#  done
#  i=$((i + 1))
#done

echo "---- 所有任务运行完毕 ----"