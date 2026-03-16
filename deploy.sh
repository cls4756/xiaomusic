#!/bin/bash

# XiaoMusic CentOS Docker 一键部署脚本
# 使用方法：bash deploy.sh

set -e

echo "=========================================="
echo "XiaoMusic CentOS Docker 部署脚本"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}错误：此脚本需要 root 权限运行${NC}"
    echo "请使用 sudo bash deploy.sh"
    exit 1
fi

# 第一步：检查 Docker
echo -e "${YELLOW}[1/8] 检查 Docker 环境...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误：Docker 未安装${NC}"
    echo "请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}错误：Docker Compose 未安装${NC}"
    echo "请先安装 Docker Compose"
    exit 1
fi

echo -e "${GREEN}✓ Docker 版本: $(docker --version)${NC}"
echo -e "${GREEN}✓ Docker Compose 版本: $(docker-compose --version)${NC}"
echo ""

# 第二步：创建数据目录
echo -e "${YELLOW}[2/8] 创建数据目录...${NC}"
mkdir -p /xiaomusic_music
mkdir -p /xiaomusic_conf
chmod -R 755 /xiaomusic_music
chmod -R 755 /xiaomusic_conf
echo -e "${GREEN}✓ 数据目录创建完成${NC}"
echo ""

# 第三步：复制配置文件
echo -e "${YELLOW}[3/8] 配置文件...${NC}"
if [ ! -f /xiaomusic_conf/config.json ]; then
    if [ -f ./config-example.json ]; then
        cp ./config-example.json /xiaomusic_conf/config.json
        echo -e "${GREEN}✓ 配置文件已复制${NC}"
        echo -e "${YELLOW}⚠ 请编辑 /xiaomusic_conf/config.json 填入小米账号密码${NC}"
    else
        echo -e "${RED}错误：找不到 config-example.json${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ 配置文件已存在${NC}"
fi
echo ""

# 第四步：拉取镜像
echo -e "${YELLOW}[4/8] 拉取 Docker 镜像...${NC}"
docker pull hanxi/xiaomusic:latest
echo -e "${GREEN}✓ 镜像拉取完成${NC}"
echo ""

# 第五步：检查 docker-compose.yml
echo -e "${YELLOW}[5/8] 检查 docker-compose.yml...${NC}"
if [ ! -f ./docker-compose.yml ]; then
    echo -e "${RED}错误：找不到 docker-compose.yml${NC}"
    exit 1
fi
echo -e "${GREEN}✓ docker-compose.yml 存在${NC}"
echo ""

# 第六步：启动容器
echo -e "${YELLOW}[6/8] 启动容器...${NC}"
docker-compose up -d
echo -e "${GREEN}✓ 容器已启动${NC}"
echo ""

# 第七步：等待容器启动
echo -e "${YELLOW}[7/8] 等待容器完全启动...${NC}"
sleep 10
for i in {1..30}; do
    if docker exec xiaomusic curl -s http://localhost:8090/getversion > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 容器已就绪${NC}"
        break
    fi
    echo "等待中... ($i/30)"
    sleep 2
done
echo ""

# 第八步：验证部署
echo -e "${YELLOW}[8/8] 验证部署...${NC}"
echo ""
echo -e "${GREEN}========== 部署完成 ==========${NC}"
echo ""
echo "容器状态："
docker ps | grep xiaomusic
echo ""
echo "访问地址："
echo -e "${GREEN}http://$(hostname -I | awk '{print $1}'):58090${NC}"
echo ""
echo "后续步骤："
echo "1. 编辑配置文件："
echo "   vi /xiaomusic_conf/config.json"
echo ""
echo "2. 填入小米账号和密码，然后重启容器："
echo "   docker restart xiaomusic"
echo ""
echo "3. 查看日志："
echo "   docker logs -f xiaomusic"
echo ""
echo "4. 上传音乐文件到 /xiaomusic_music 目录"
echo ""
echo "5. 在 Web 界面刷新音乐列表"
echo ""
echo -e "${GREEN}========== 部署完成 ==========${NC}"
