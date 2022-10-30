#!/bin/sh

N=$1
hosts1=$2
hosts2=$3
hosts3=$4
hosts4=$5
hosts5=$6
hosts6=$7
hosts1endNum=$8
hosts2endNum=$9
hosts3endNum=${10}
hosts4endNum=${11}
hosts5endNum=${12}


rm -rf hosts.config
touch hosts.config

i=0
# hosts1
while [ "$i" -lt $((hosts1endNum + 1)) ]; do
  echo $i $hosts1 $hosts1 $((20000 + $((100 * $i)))) >>hosts.config
  echo "---- 写入第【$i】个节点的hosts.config文件：$i $hosts1 $hosts1 $((20000 + $((100 * $i)))) ----"
  i=$((i + 1))
done
# hosts2
if [ $hosts2endNum -ne 0 ]; then
  while [ "$i" -lt $((hosts2endNum + 1)) ]; do
    echo $i $hosts2 $hosts2 $((20000 + $((100 * $i)))) >>hosts.config
    echo "---- 写入第【$i】个节点的hosts.config文件：$i $hosts2 $hosts2 $((20000 + $((100 * $i)))) ----"
    i=$((i + 1))
  done
fi
# hosts3
if [ $hosts3endNum -ne 0 ]; then
  while [ "$i" -lt $((hosts3endNum + 1)) ]; do
    echo $i $hosts3 $hosts3 $((20000 + $((100 * $i)))) >>hosts.config
    echo "---- 写入第【$i】个节点的hosts.config文件：$i $hosts3 $hosts3 $((20000 + $((100 * $i)))) ----"
    i=$((i + 1))
  done
fi
# hosts4
if [ $hosts4endNum -ne 0 ]; then
  while [ "$i" -lt $((hosts4endNum + 1)) ]; do
    echo $i $hosts4 $hosts4 $((20000 + $((100 * $i)))) >>hosts.config
    echo "---- 写入第【$i】个节点的hosts.config文件：$i $hosts4 $hosts4 $((20000 + $((100 * $i)))) ----"
    i=$((i + 1))
  done
fi
# hosts5
if [ $hosts5endNum -ne 0 ]; then
  while [ "$i" -lt $((hosts5endNum + 1)) ]; do
    echo $i $hosts5 $hosts5 $((20000 + $((100 * $i)))) >>hosts.config
    echo "---- 写入第【$i】个节点的hosts.config文件：$i $hosts5 $hosts5 $((20000 + $((100 * $i)))) ----"
    i=$((i + 1))
  done
fi
# hosts6
while [ "$i" -lt $N ]; do
  echo $i $hosts6 $hosts6 $((20000 + $((100 * $i)))) >>hosts.config
  echo "---- 写入第【$i】个节点的hosts.config文件：$i $hosts6 $hosts6 $((20000 + $((100 * $i)))) ----"
  i=$((i + 1))
done
