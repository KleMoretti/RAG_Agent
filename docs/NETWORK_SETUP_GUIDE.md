
## 问题描述

当其他电脑访问系统时出现 `Missing or invalid authorization header` 错误，这通常是由于网络配置和CORS设置问题导致的。

## 解决方案

### 1. 后端CORS配置修复

已修复 `main.py` 中的CORS配置：

```python
# 修复前（有问题）
allow_origins=["http://localhost:3000", "*"]  # 与 allow_credentials=True 冲突

# 修复后（正确）
cors_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000", 
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]
# 自动添加本地网络IP
```

### 2. 前端Token存储修复

修复了 `frontend/lib/api/client.ts` 中的token获取逻辑：

```typescript
// 修复前（错误）
token = parsedData.state?.token || null;

// 修复后（正确）
token = parsedData.token || null;
```

### 3. 网络访问配置

#### 方法一：使用本地IP地址

1. **获取服务器IP地址**：
   ```bash
   # Windows
   ipconfig
   
   # Linux/Mac
   ifconfig
   ```

2. **修改前端配置**：
   在 `frontend/.env.local` 中添加：
   ```env
   NEXT_PUBLIC_API_URL=http://YOUR_SERVER_IP:8000
   ```

3. **重启服务**：
   ```bash
   python start_system.py
   ```

#### 方法二：配置防火墙

**Windows防火墙**：
1. 打开"Windows Defender防火墙"
2. 点击"高级设置"
3. 选择"入站规则" → "新建规则"
4. 选择"端口" → "TCP" → "特定本地端口" → 输入"8000,3000"
5. 允许连接

**Linux防火墙**：
```bash
# Ubuntu/Debian
sudo ufw allow 8000
sudo ufw allow 3000

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --reload
```

### 4. 测试认证流程

运行诊断脚本：

```bash
python test_auth_flow.py
```

该脚本会测试：
- 后端健康检查
- CORS配置
- 登录流程
- Token验证
- 认证端点访问

### 5. 浏览器调试

在浏览器开发者工具中检查：

1. **Network标签**：
   - 查看请求是否发送到正确的URL
   - 检查Authorization头是否存在
   - 查看CORS预检请求

2. **Console标签**：
   - 查看JavaScript错误
   - 检查localStorage中的token

3. **Application标签**：
   - 检查localStorage中的用户数据
   - 验证token格式

### 6. 常见问题排查

#### 问题1：CORS错误
```
Access to fetch at 'http://server:8000/api/auth/me' from origin 'http://client:3000' 
has been blocked by CORS policy
```

**解决方案**：
- 确保服务器IP在CORS允许列表中
- 检查防火墙设置
- 验证端口是否正确

#### 问题2：Token未传递
```
Missing or invalid authorization header
```

**解决方案**：
- 检查localStorage中是否有token
- 验证token格式是否正确
- 确认API客户端配置

#### 问题3：网络连接失败
```
Failed to fetch
```

**解决方案**：
- 检查网络连接
- 验证服务器IP和端口
- 确认服务正在运行

### 7. 生产环境配置

对于生产环境，建议：

1. **使用HTTPS**：
   ```python
   # 在main.py中配置
   cors_origins = [
       "https://yourdomain.com",
       "https://www.yourdomain.com",
   ]
   ```

2. **限制CORS来源**：
   ```python
   # 只允许特定域名
   cors_origins = [
       "https://yourdomain.com",
   ]
   ```

3. **环境变量配置**：
   ```env
   # .env
   CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```

### 8. 快速验证步骤

1. **启动服务**：
   ```bash
   python start_system.py
   ```

2. **运行测试**：
   ```bash
   python test_auth_flow.py
   ```

3. **访问调试端点**：
   ```
   http://YOUR_SERVER_IP:8000/api/debug/auth
   ```

4. **检查前端**：
   ```
   http://YOUR_SERVER_IP:3000
   ```

## 总结

通过以上修复和配置，应该能够解决跨电脑访问时的认证问题。主要修复点：

1. ✅ 修复了CORS配置冲突
2. ✅ 修复了前端token存储逻辑
3. ✅ 添加了自动网络IP检测
4. ✅ 提供了完整的诊断工具
5. ✅ 创建了详细的配置指南

如果问题仍然存在，请运行 `python test_auth_flow.py` 并查看详细的错误信息。
