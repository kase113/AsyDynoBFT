#!/bin/sh


IMAGE_NAME="bft"
IMAGE_TAG="latest"
# 2.构建基础镜像（若多台服务器，则需要推送到其他服务器）
docker stop $(docker ps -a | grep "$IMAGE_NAME:$IMAGE_TAG" | awk '{print $1}')
docker rm $(docker ps -a | grep "$IMAGE_NAME:$IMAGE_TAG" | awk '{print $1}')
docker rmi $(docker images | grep "$IMAGE_NAME:$IMAGE_TAG" | awk '{print $1}')
echo "---- 开始构建镜像 $IMAGE_NAME:$IMAGE_TAG ----"
docker build -t $IMAGE_NAME:$IMAGE_TAG .
echo "---- 成功构建镜像 $IMAGE_NAME:$IMAGE_TAG ----"