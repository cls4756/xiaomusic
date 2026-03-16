# XiaoMusic CentOS Docker 部署指南

## 📦 项目已准备好部署

所有无关文件已删除，项目现在包含以下部署文件：

### 新增部署文件

| 文件 | 说明 |
|------|------|
| `docker-compose.yml` | Docker Compose 配置文件 |
| `deploy.sh` | 一键部署脚本 |
| `CentOS_Docker_部署指南.md` | 详细部署指南 |
| `部署步骤总结.md` | 快速部署步骤 |
| `快速部署清单.txt` | 部署检查清单 |

---

## 🚀 快速开始（3 分钟）

### 第 1 步：复制项目到 CentOS

```bash
# 在本地机器上执行
scp -r /path/to/xiaomusic root@your_centos_ip:/opt/xiaomusic
```

### 第 2 步：运行部署脚本

```bash
# SSH 连接到 CentOS
ssh root@your_centos_ip

# 进入项目目录
cd /opt/xiaomusic

# 运行一键部署脚本
bash deploy.sh
```

### 第 3 步：配置小米账号

```bash
# 编辑配置文件
vi /xiaomusic_conf/config.json

# 修改以下字段：
# "account": "your_xiaomi_account@example.com"
# "password": "your_password"
# "hostname": "http://your_centos_ip"

# 保存后重启容器
docker restart xiaomusic
```

### 第 4 步：访问 Web 界面

打开浏览器访问：`http://your_centos_ip:58090`

---

## 📋 部署文件说明

### 1. `docker-compose.yml`
Docker Compose 配置文件，定义了容器的运行参数。

**关键配置**：
- 镜像：`hanxi/xiaomusic:latest`
- 端口：`58090:8090`
- 数据卷：`/xiaomusic_music` 和 `/xiaomusic_conf`
- 健康检查：自动检测容器状态

### 2. `deploy.sh`
一键部署脚本，自动完成以下操作：
- ✅ 检查 Docker 环境
- ✅ 创建数据目录
- ✅ 复制配置文件
- ✅ 拉取 Docker 镜像
- ✅ 启动容器
- ✅ 验证部署

**使用方法**：
```bash
bash deploy.sh
```

### 3. `CentOS_Docker_部署指南.md`
详细的部署指南，包含：
- 前置要求
- 完整的部署步骤
- 常用命令
- 故障排查
- 性能优化
- 备份恢复

### 4. `部署步骤总结.md`
快速参考指南，包含：
- 快速部署方式
- 手动部署步骤
- 配置文件详解
- 验证部署
- 常用命令

### 5. `快速部署清单.txt`
部署检查清单，包含：
- 8 个部署步骤
- 常用命令速查
- 故障排查
- 重要提示

---

## 🔍 部署前检查

### 在 CentOS 上检查

```bash
# 1. 检查 Docker
docker --version
docker-compose --version

# 2. 检查磁盘空间
df -h

# 3. 检查网络连接
ping account.xiaomi.com
```

### 在本地检查

```bash
# 1. 检查项目文件
ls -la xiaomusic/

# 2. 检查 Dockerfile
cat xiaomusic/Dockerfile

# 3. 检查配置示例
cat xiaomusic/config-example.json
```

---

## 📝 部署步骤

### 方式 A：使用一键脚本（推荐）

```bash
# 1. 复制项目
scp -r xiaomusic root@your_centos_ip:/opt/

# 2. 运行脚本
ssh root@your_centos_ip "cd /opt/xiaomusic && bash deploy.sh"

# 3. 配置账号
ssh root@your_centos_ip "vi /xiaomusic_conf/config.json"

# 4. 重启容器
ssh root@your_centos_ip "docker restart xiaomusic"
```

### 方式 B：手动部署

详见 `部署步骤总结.md` 中的"手动部署步骤"部分。

---

## ✅ 验证部署

```bash
# 1. 检查容器状态
docker ps | grep xiaomusic

# 2. 测试 API
curl http://your_centos_ip:58090/getversion

# 3. 查看日志
docker logs xiaomusic | tail -20

# 4. 访问 Web 界面
# 打开浏览器：http://your_centos_ip:58090
```

---

## 🎵 上传音乐

```bash
# 使用 SCP 上传
scp -r /path/to/music/* root@your_centos_ip:/xiaomusic_music/

# 或使用 rsync
rsync -avz /path/to/music/ root@your_centos_ip:/xiaomusic_music/

# 刷新音乐列表
curl -X POST http://your_centos_ip:58090/api/music/refreshlist
```

---

## 🐛 常见问题

### Q1：设备列表为空
**A**：检查小米账号密码是否正确，删除认证文件重新登录
```bash
rm /xiaomusic_conf/.mi.token
docker restart xiaomusic
```

### Q2：无法访问 Web 界面
**A**：检查防火墙是否开放了 58090 端口
```bash
sudo firewall-cmd --permanent --add-port=58090/tcp
sudo firewall-cmd --reload
```

### Q3：容器无法启动
**A**：查看错误日志
```bash
docker logs xiaomusic
```

### Q4：重启后设备列表为空
**A**：确保 `/xiaomusic_conf` 目录已正确挂载
```bash
docker inspect xiaomusic | grep -A 10 "Mounts"
```

---

## 📚 更多信息

- **详细部署指南**：`CentOS_Docker_部署指南.md`
- **快速参考**：`部署步骤总结.md`
- **检查清单**：`快速部署清单.txt`
- **项目 README**：`README.md`

---

## 🎯 部署完成后

1. ✅ 对小爱音箱说话测试
2. ✅ 配置 AI 大模型（可选）
3. ✅ 设置定时任务（可选）
4. ✅ 定期备份配置文件

---

## 💡 提示

- 首次启动需要 30-60 秒完全初始化
- 设备列表加载可能需要 1-2 分钟
- 定期备份 `/xiaomusic_conf` 目录
- 确保 `/xiaomusic_music` 和 `/xiaomusic_conf` 已挂载到宿主机

---

## 🆘 需要帮助？

1. 查看详细部署指南：`CentOS_Docker_部署指南.md`
2. 查看快速参考：`部署步骤总结.md`
3. 查看检查清单：`快速部署清单.txt`
4. 查看项目 Issues：https://github.com/hanxi/xiaomusic/issues

---

**祝部署顺利！** 🎉
