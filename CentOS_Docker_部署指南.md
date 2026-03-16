# XiaoMusic 在 CentOS 上的 Docker 部署指南

## 前置要求

- CentOS 7.x 或 8.x 或更高版本
- Docker 已安装（版本 20.10+）
- Docker Compose 已安装（版本 1.29+）
- 至少 2GB 可用磁盘空间

---

## 第一步：准备项目文件

### 1. 在本地清理项目

```bash
# 已完成：删除了所有分析文档
# 项目现在只包含必要的源代码和配置文件
```

### 2. 复制项目到 CentOS 服务器

```bash
# 在本地机器上
scp -r /path/to/xiaomusic root@your_centos_ip:/opt/xiaomusic

# 或使用 rsync（更快）
rsync -avz /path/to/xiaomusic/ root@your_centos_ip:/opt/xiaomusic/
```

### 3. 验证文件完整性

```bash
# SSH 连接到 CentOS 服务器
ssh root@your_centos_ip

# 检查项目文件
cd /opt/xiaomusic
ls -la

# 应该看到这些关键文件：
# Dockerfile
# pyproject.toml
# xiaomusic.py
# xiaomusic/ (目录)
# config-example.json
```

---

## 第二步：在 CentOS 上准备环境

### 1. 检查 Docker 和 Docker Compose

```bash
# 检查 Docker 版本
docker --version

# 检查 Docker Compose 版本
docker-compose --version

# 如果未安装，执行以下命令
# CentOS 7
sudo yum install -y docker docker-compose

# CentOS 8+
sudo dnf install -y docker docker-compose

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 验证 Docker 是否运行
sudo docker ps
```

### 2. 创建数据目录

```bash
# 创建音乐和配置目录
sudo mkdir -p /xiaomusic_music
sudo mkdir -p /xiaomusic_conf

# 设置权限（允许容器读写）
sudo chmod -R 755 /xiaomusic_music
sudo chmod -R 755 /xiaomusic_conf

# 如果需要特定用户访问
sudo chown -R 1000:1000 /xiaomusic_music
sudo chown -R 1000:1000 /xiaomusic_conf
```

### 3. 复制配置文件

```bash
# 复制示例配置
cp /opt/xiaomusic/config-example.json /xiaomusic_conf/config.json

# 编辑配置文件
vi /xiaomusic_conf/config.json
```

---

## 第三步：编辑配置文件

### 编辑 `/xiaomusic_conf/config.json`

```json
{
  "account": "your_xiaomi_account@example.com",
  "password": "your_xiaomi_password",
  "mi_did": "你的小爱音箱设备ID",
  "music_path": "music",
  "temp_path": "music/tmp",
  "download_path": "music/download",
  "conf_path": "conf",
  "cache_dir": "music/cache",
  "hostname": "http://your_centos_ip",
  "port": 8090,
  "public_port": 58090,
  "verbose": false,
  "disable_httpauth": true,
  "enable_config_example": true
}
```

**关键配置项**：
- `account` - 小米账号
- `password` - 小米密码
- `mi_did` - 小爱音箱的设备 ID（可以先不填，启动后从 Web 界面获取）
- `hostname` - 服务器 IP 或域名
- `port` - 内部端口（保持 8090）
- `public_port` - 外部访问端口（可改为其他）

---

## 第四步：构建 Docker 镜像

### 本地编译镜像（包含你的所有代码修改）

```bash
# 进入项目目录
cd /opt/xiaomusic

# 构建镜像
docker build -t xiaomusic:latest .

# 验证镜像
docker images | grep xiaomusic

# 查看构建日志（如果需要）
docker build -t xiaomusic:latest . --progress=plain
```

**重要说明**：
- 使用本地 Dockerfile 构建，包含你对代码的所有修改
- 首次构建时间：约 5-10 分钟（取决于网络速度）
- 后续更新代码后，只需重新执行 `docker build` 命令即可

---

## 第五步：创建 Docker Compose 配置

### 使用本地编译的镜像

docker-compose.yml 已经配置为使用本地 Dockerfile 构建镜像。你只需要在 CentOS 上运行：

```bash
# 进入项目目录
cd /opt/xiaomusic

# docker-compose 会自动使用 Dockerfile 构建镜像
docker-compose up -d
```

**docker-compose.yml 配置说明**：

```yaml
version: '3.8'

services:
  xiaomusic:
    # 使用本地 Dockerfile 构建镜像
    build:
      context: .
      dockerfile: Dockerfile
    
    image: xiaomusic:latest
    container_name: xiaomusic
    restart: unless-stopped
    
    ports:
      - "58090:8090"
    
    volumes:
      - /xiaomusic_music:/app/music
      - /xiaomusic_conf:/app/conf
      - /etc/localtime:/etc/localtime:ro
    
    environment:
      - TZ=Asia/Shanghai
    
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8090/getversion"]
      interval: 60s
      timeout: 10s
      retries: 3
      start_period: 60s
    
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**关键点**：
- `build` 部分指定使用本地 Dockerfile 构建
- 首次运行 `docker-compose up -d` 时会自动构建镜像
- 后续更新代码后，运行 `docker-compose up -d --build` 重新构建

---

## 第六步：启动容器

### 使用 Docker Compose 启动（推荐）

```bash
# 进入项目目录
cd /opt/xiaomusic

# 启动容器（首次会自动构建镜像）
docker-compose up -d

# 查看构建和启动日志
docker-compose logs -f xiaomusic

# 等待容器完全启动（约 30-60 秒）
```

### 更新代码后重新构建

```bash
# 如果修改了代码，重新构建镜像并启动
docker-compose up -d --build

# 查看构建日志
docker-compose logs -f xiaomusic
```

---

## 第七步：验证部署

### 1. 检查容器状态

```bash
# 查看容器是否运行
docker ps | grep xiaomusic

# 应该看到类似输出：
# CONTAINER ID   IMAGE                    STATUS
# abc123def456   hanxi/xiaomusic:latest   Up 2 minutes
```

### 2. 查看启动日志

```bash
# 查看最近的日志
docker logs xiaomusic | tail -50

# 实时查看日志
docker logs -f xiaomusic

# 查看认证相关日志
docker logs xiaomusic | grep -E "登录|login|auth"
```

### 3. 测试 API

```bash
# 获取版本信息
curl http://localhost:58090/getversion

# 获取设备列表
curl http://localhost:58090/getsetting?need_device_list=true | jq '.device_list'

# 应该返回设备列表（如果已配置）
```

### 4. 访问 Web 界面

```
http://your_centos_ip:58090
```

在浏览器中打开上面的地址，应该能看到 XiaoMusic 的 Web 界面。

---

## 第八步：初始配置

### 1. 首次登录

1. 打开 Web 界面：`http://your_centos_ip:58090`
2. 点击"设置"
3. 输入小米账号和密码
4. 点击"保存"
5. 等待设备列表加载

### 2. 获取设备 ID

```bash
# 如果 Web 界面显示了设备，记下设备 ID
# 或通过 API 获取
curl http://localhost:58090/getsetting?need_device_list=true | jq '.device_list[0].miotDID'
```

### 3. 更新配置文件

```bash
# 编辑配置文件，填入设备 ID
vi /xiaomusic_conf/config.json

# 修改 mi_did 字段
"mi_did": "981195288"

# 保存后重启容器
docker restart xiaomusic
```

---

## 第九步：上传音乐文件

### 方法 1：使用 SCP 上传

```bash
# 在本地机器上
scp -r /path/to/music/* root@your_centos_ip:/xiaomusic_music/

# 或使用 rsync
rsync -avz /path/to/music/ root@your_centos_ip:/xiaomusic_music/
```

### 方法 2：使用 Web 界面上传

1. 打开 Web 界面
2. 点击"上传"
3. 选择音乐文件
4. 等待上传完成

### 方法 3：直接复制到目录

```bash
# SSH 到服务器
ssh root@your_centos_ip

# 复制音乐文件
cp -r /path/to/music/* /xiaomusic_music/

# 刷新音乐列表
curl -X POST http://localhost:58090/api/music/refreshlist
```

---

## 常用命令

### 容器管理

```bash
# 启动容器
docker-compose up -d

# 停止容器
docker-compose down

# 重启容器
docker restart xiaomusic

# 查看容器日志
docker logs -f xiaomusic

# 进入容器
docker exec -it xiaomusic bash

# 查看容器资源使用
docker stats xiaomusic
```

### 配置管理

```bash
# 编辑配置
vi /xiaomusic_conf/config.json

# 重启容器使配置生效
docker restart xiaomusic

# 备份配置
cp /xiaomusic_conf/config.json /xiaomusic_conf/config.json.backup
```

### 日志查看

```bash
# 查看最近 100 行日志
docker logs xiaomusic | tail -100

# 查看特定时间的日志
docker logs xiaomusic --since 2026-03-16T10:00:00

# 查看 AI 相关日志
docker logs xiaomusic | grep -E "\[AI分析\]|\[AI智能解析\]"

# 查看认证相关日志
docker logs xiaomusic | grep -E "登录|auth|token"
```

---

## 故障排查

### 问题 1：容器无法启动

```bash
# 查看错误日志
docker logs xiaomusic

# 检查端口是否被占用
sudo netstat -tlnp | grep 58090

# 检查目录权限
ls -la /xiaomusic_conf/
ls -la /xiaomusic_music/
```

### 问题 2：设备列表为空

```bash
# 检查配置文件
cat /xiaomusic_conf/config.json | jq '.account, .password, .mi_did'

# 检查认证文件
ls -la /xiaomusic_conf/.mi.token

# 查看认证日志
docker logs xiaomusic | grep -i "login\|auth"

# 删除认证文件重新登录
rm /xiaomusic_conf/.mi.token
docker restart xiaomusic
```

### 问题 3：无法访问 Web 界面

```bash
# 检查防火墙
sudo firewall-cmd --list-all

# 开放端口
sudo firewall-cmd --permanent --add-port=58090/tcp
sudo firewall-cmd --reload

# 或使用 iptables
sudo iptables -A INPUT -p tcp --dport 58090 -j ACCEPT
```

### 问题 4：音乐无法播放

```bash
# 检查音乐文件权限
ls -la /xiaomusic_music/

# 刷新音乐列表
curl -X POST http://localhost:58090/api/music/refreshlist

# 查看音乐库日志
docker logs xiaomusic | grep -i "music\|library"
```

---

## 性能优化

### 1. 增加容器资源限制

```yaml
# 在 docker-compose.yml 中添加
services:
  xiaomusic:
    # ... 其他配置
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### 2. 启用日志轮转

```yaml
# 已在 docker-compose.yml 中配置
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### 3. 定期清理

```bash
# 清理未使用的镜像
docker image prune -a

# 清理未使用的容器
docker container prune

# 清理未使用的卷
docker volume prune
```

---

## 备份和恢复

### 备份配置和数据

```bash
# 备份配置
tar -czf xiaomusic_conf_backup.tar.gz /xiaomusic_conf/

# 备份音乐
tar -czf xiaomusic_music_backup.tar.gz /xiaomusic_music/

# 上传到安全位置
scp xiaomusic_*_backup.tar.gz backup_server:/backup/
```

### 恢复配置和数据

```bash
# 恢复配置
tar -xzf xiaomusic_conf_backup.tar.gz -C /

# 恢复音乐
tar -xzf xiaomusic_music_backup.tar.gz -C /

# 重启容器
docker restart xiaomusic
```

---

## 更新升级

### 更新代码后重新构建

```bash
# 1. 更新本地代码（git pull 或手动修改）
cd /opt/xiaomusic
git pull origin main

# 2. 重新构建镜像
docker-compose up -d --build

# 3. 验证更新
docker logs xiaomusic | grep -i "version"
```

### 完整的更新流程

```bash
# 停止旧容器
docker-compose down

# 更新代码
git pull origin main

# 重新构建并启动
docker-compose up -d --build

# 查看日志
docker-compose logs -f xiaomusic
```

---

## 总结

完整的部署流程：

1. ✅ 复制项目文件到 CentOS
2. ✅ 创建数据目录
3. ✅ 编辑配置文件
4. ✅ 构建或拉取 Docker 镜像
5. ✅ 创建 docker-compose.yml
6. ✅ 启动容器
7. ✅ 验证部署
8. ✅ 初始配置
9. ✅ 上传音乐文件

现在你的 XiaoMusic 应该已经在 CentOS 上成功运行了！

---

## 获取帮助

如果遇到问题，可以：

1. 查看日志：`docker logs xiaomusic`
2. 检查配置：`cat /xiaomusic_conf/config.json`
3. 测试 API：`curl http://localhost:58090/getversion`
4. 查看 GitHub Issues：https://github.com/hanxi/xiaomusic/issues
