# Mysteel 数据爬虫 - 统一 CLI 指南

> **v2.0 版本** - 统一命令行工具，修复日期选择和材料定位问题

---

## 📚 目录

- [快速开始](#快速开始)
- [命令参考](#命令参考)
- [使用场景](#使用场景)
- [故障排查](#故障排查)
- [自动化部署](#自动化部署)
- [最佳实践](#最佳实践)

---

## 快速开始

### 1. 安装依赖

```bash
pip install selenium webdriver-manager pandas
```

**注意**: 需要安装 Google Chrome 浏览器

### 2. 测试连接

```bash
python scripts/mysteel_cli.py test
```

### 3. 开始爬取

```bash
# 爬取单个材料
python scripts/mysteel_cli.py crawl --material 螺纹 --days 7 --save-db

# 批量爬取多个材料
python scripts/mysteel_cli.py batch --save-db -y
```

### 4. 查看帮助

```bash
python scripts/mysteel_cli.py --help
python scripts/mysteel_cli.py crawl --help
python scripts/mysteel_cli.py batch --help
```

---

## 命令参考

### 可用命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `crawl` | 爬取单个材料 | `python scripts/mysteel_cli.py crawl --material 螺纹` |
| `batch` | 批量爬取多个材料 | `python scripts/mysteel_cli.py batch --save-db -y` |
| `test` | 测试网站连接 | `python scripts/mysteel_cli.py test` |
| `diagnose` | 诊断网站结构 | `python scripts/mysteel_cli.py diagnose` |
| `list` | 列出支持的材料 | `python scripts/mysteel_cli.py list` |

### `crawl` - 爬取单个材料

```bash
python scripts/mysteel_cli.py crawl [OPTIONS]
```

**参数**:

| 参数 | 说明 | 默认值 |
|-----|------|-------|
| `--material` | 材料类型 | 螺纹 |
| `--start-date` | 开始日期 (YYYY-MM-DD) | 30天前 |
| `--end-date` | 结束日期 (YYYY-MM-DD) | 今天 |
| `--days` | 爬取最近N天 | 30 |
| `--output` | CSV输出路径 | - |
| `--save-db` | 保存到数据库 | False |
| `--show-browser` | 显示浏览器 | False |
| `--quiet` | 安静模式 | False |

**示例**:

```bash
# 爬取螺纹钢最近7天
python scripts/mysteel_cli.py crawl --material 螺纹 --days 7 --save-db

# 爬取铁矿石指定日期范围
python scripts/mysteel_cli.py crawl --material 铁矿石 \
    --start-date 2025-01-01 --end-date 2025-01-31 --save-db

# 显示浏览器（调试用）
python scripts/mysteel_cli.py crawl --material 热卷 --show-browser
```

### `batch` - 批量爬取多个材料

```bash
python scripts/mysteel_cli.py batch [OPTIONS]
```

**参数**:

| 参数 | 说明 | 默认值 |
|-----|------|-------|
| `--materials` | 材料列表（逗号分隔） | 螺纹,铁矿石,焦炭,热卷 |
| `--start-date` | 开始日期 | 7天前 |
| `--end-date` | 结束日期 | 今天 |
| `--days` | 爬取最近N天 | 7 |
| `--output-dir` | CSV输出目录 | - |
| `--save-db` | 保存到数据库 | False |
| `--delay` | 延迟时间（秒） | 5 |
| `--show-browser` | 显示浏览器 | False |
| `-y, --yes` | 跳过确认 | False |

**示例**:

```bash
# 批量爬取默认材料
python scripts/mysteel_cli.py batch --save-db -y

# 批量爬取指定材料
python scripts/mysteel_cli.py batch \
    --materials "螺纹,铁矿石,焦炭" \
    --days 30 \
    --save-db \
    -y
```

### `test` - 测试连接

```bash
python scripts/mysteel_cli.py test [--show-browser]
```

测试网站连接和基本功能是否正常。

### `diagnose` - 诊断网站结构

```bash
python scripts/mysteel_cli.py diagnose
```

诊断网站结构，查找材料按钮，帮助排查问题。

### `list` - 列出支持的材料

```bash
python scripts/mysteel_cli.py list
```

输出所有支持的材料类型：

```
材料名称       英文ID            分类              说明
----------------------------------------------------------------------
螺纹         LUOWEN          product         螺纹钢
热卷         REJUAN          product         热轧卷板
冷卷         LENGJUAN        product         冷轧卷板
中厚板        ZHONGHOUBAN     product         中厚板
铁矿石        TEKUANGSHI      raw_material    铁矿石
焦炭         JIAOTA          raw_material    焦炭
```

---

## 使用场景

### 场景1：首次使用

```bash
# 1. 测试连接（显示浏览器，观察过程）
python scripts/mysteel_cli.py test --show-browser

# 2. 爬取小范围数据测试
python scripts/mysteel_cli.py crawl --material 螺纹 --days 3 --show-browser

# 3. 验证成功后批量爬取
python scripts/mysteel_cli.py batch --days 7 --save-db -y
```

### 场景2：每日例行更新

```bash
# 爬取昨天的数据
python scripts/mysteel_cli.py batch --days 1 --save-db -y
```

### 场景3：历史数据补全

```bash
# 爬取2025年1月所有数据
python scripts/mysteel_cli.py batch \
    --start-date 2025-01-01 \
    --end-date 2025-01-31 \
    --materials "螺纹,铁矿石,焦炭,热卷" \
    --save-db \
    --delay 10 \
    -y
```

### 场景4：导出CSV用于分析

```bash
# 批量导出最近30天数据
python scripts/mysteel_cli.py batch \
    --days 30 \
    --output-dir data/mysteel_export \
    -y
```

### 场景5：调试和排查问题

```bash
# 显示浏览器，观察爬取过程
python scripts/mysteel_cli.py crawl --material 螺纹 --show-browser

# 诊断网站结构
python scripts/mysteel_cli.py diagnose
```

---

## 故障排查

### 问题1：日期选择失败

**症状**:
```
❌ 输入日期失败 (start): Message: no such element
```

**解决方案**:
```bash
# 1. 查看日期选择器截图
ls date_picker_error_*.png

# 2. 使用显示浏览器模式调试
python scripts/mysteel_cli.py crawl --material 螺纹 --show-browser

# 3. 运行诊断
python scripts/mysteel_cli.py diagnose
```

### 问题2：材料按钮找不到

**症状**:
```
❌ 未找到材料按钮: TEKUANGSHI
```

**解决方案**:
```bash
# 1. 列出支持的材料
python scripts/mysteel_cli.py list

# 2. 诊断网站结构
python scripts/mysteel_cli.py diagnose
```

### 问题3：网络连接问题

**症状**:
```
ERROR: handshake failed; net_error -107
WinError 10013 访问套接字失败
```

**解决方案**:
1. 关闭防火墙/VPN 后重试
2. 检查系统代理设置: `netsh winhttp show proxy`
3. 运行测试: `python scripts/mysteel_cli.py test`

### 问题4：ChromeDriver 版本不匹配

**症状**:
```
selenium.common.exceptions.SessionNotCreatedException
```

**解决方案**:
```bash
pip install --upgrade webdriver-manager selenium
```

### 问题5：数据为空

**解决方案**:
1. 检查日期范围是否合理（不能超过当前日期）
2. 尝试不同的材料类型
3. 手动访问网站验证：https://index.mysteel.com/

### 问题6：爬取被封IP

**解决方案**:
1. 增加延迟时间：`--delay 10`（每次请求间隔10秒）
2. 降低爬取频率（每天一次而非每小时）
3. 考虑使用官方 API 接口

---

## 自动化部署

### Windows 任务计划程序

**创建批处理脚本** (`mysteel_daily.bat`):
```batch
@echo off
cd /d D:\@Python\@PyCharm\RAG_Agent
call .venv\Scripts\activate
python scripts\mysteel_cli.py batch --days 1 --save-db -y
```

**配置任务计划程序**:
```cmd
schtasks /create /tn "Mysteel每日更新" ^
    /tr "D:\RAG_Agent\mysteel_daily.bat" ^
    /sc daily /st 09:00
```

### Linux Cron 定时任务

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每天9点执行）
0 9 * * * cd /path/to/RAG_Agent && python scripts/mysteel_cli.py batch --days 1 --save-db -y >> /var/log/mysteel_crawl.log 2>&1

# 查看定时任务
crontab -l

# 查看日志
tail -f /var/log/mysteel_crawl.log
```

### Python APScheduler 集成

在 `main.py` 中添加：

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import subprocess
import logging

logger = logging.getLogger(__name__)

def scheduled_mysteel_crawl():
    """每天9点自动爬取昨天的数据"""
    logger.info("🕐 定时任务：开始爬取 Mysteel 数据")
    
    try:
        # 调用 CLI 工具
        result = subprocess.run([
            "python", "scripts/mysteel_cli.py", "batch",
            "--days", "1",
            "--save-db",
            "-y"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ 定时任务完成")
        else:
            logger.error(f"❌ 定时任务失败: {result.stderr}")
            
    except Exception as e:
        logger.error(f"❌ 定时任务异常: {e}")

# 创建调度器
scheduler = BackgroundScheduler()

# 添加定时任务
scheduler.add_job(
    func=scheduled_mysteel_crawl,
    trigger=CronTrigger(hour=9, minute=0),  # 每天9点
    id='daily_mysteel_crawl',
    name='每日Mysteel数据爬取',
    replace_existing=True
)

# 启动调度器
scheduler.start()
logger.info("⏰ Mysteel 定时任务已启动（每天9:00执行）")
```

---

## 最佳实践

### 1. 控制爬取频率

```bash
# ✅ 好的做法：增加延迟
python scripts/mysteel_cli.py batch --delay 10 --save-db -y

# ❌ 不好的做法：过于频繁
python scripts/mysteel_cli.py batch --delay 0  # 容易被封IP
```

### 2. 定期备份数据

```bash
# 导出数据备份
python scripts/mysteel_cli.py batch \
    --days 365 \
    --output-dir backups/mysteel_$(date +%Y%m%d) \
    -y
```

### 3. 监控和日志

```bash
# 记录日志
python scripts/mysteel_cli.py batch --save-db -y >> mysteel_crawl.log 2>&1

# 查看日志
tail -f mysteel_crawl.log
```

### 4. 错误处理

```bash
# 自动重试脚本
#!/bin/bash
MAX_RETRIES=3
for i in $(seq 1 $MAX_RETRIES); do
    echo "尝试 $i/$MAX_RETRIES"
    python scripts/mysteel_cli.py batch --save-db -y && break
    echo "失败，等待10秒后重试..."
    sleep 10
done
```

### 5. 法律合规

⚠️ **重要提示**:

1. ✅ 遵守网站服务条款和 robots.txt
2. ✅ 控制爬取频率（每次间隔 ≥ 5秒）
3. ✅ 仅供研究使用，不得商业转售
4. ✅ 推荐使用 [Mysteel官方API](https://mds.mysteel.com/) 更稳定合规

---

## Python 代码调用

### 示例：基础调用

```python
from scripts.crawl_mysteel_data import MysteelCrawler

crawler = MysteelCrawler(headless=True)
try:
    df = crawler.crawl_price_data(
        material_key="螺纹",
        start_date="2025-01-01",
        end_date="2025-01-31"
    )
    
    print(f"获取 {len(df)} 条数据")
    crawler.save_to_database(df)
    
finally:
    crawler.close()
```

### 示例：批量爬取

```python
from scripts.crawl_mysteel_data import MysteelCrawler, MATERIAL_MAPPING
import time

crawler = MysteelCrawler(headless=True)

try:
    materials = ["螺纹", "铁矿石", "焦炭"]
    
    for material in materials:
        print(f"正在爬取: {MATERIAL_MAPPING[material]['name']}")
        
        df = crawler.crawl_price_data(
            material_key=material,
            start_date="2025-01-01",
            end_date="2025-01-31"
        )
        
        crawler.save_to_database(df)
        time.sleep(5)  # 延迟5秒
        
finally:
    crawler.close()
```

### 示例：错误处理和重试

```python
def crawl_with_retry(material, max_retries=3):
    """带重试的爬取"""
    for attempt in range(max_retries):
        crawler = None
        try:
            crawler = MysteelCrawler(headless=True)
            df = crawler.crawl_price_data(
                material_key=material,
                start_date="2025-01-01",
                end_date="2025-01-31"
            )
            crawler.save_to_database(df)
            print(f"✅ {material} 爬取成功")
            return True
            
        except Exception as e:
            print(f"❌ 第 {attempt + 1} 次尝试失败: {e}")
            if attempt < max_retries - 1:
                time.sleep(10)
            
        finally:
            if crawler:
                crawler.close()
    
    return False
```

---

## 输出格式

### CSV 文件格式

```csv
material_type,category,price,unit,source,price_date,change_rate,change_amount
螺纹钢,product,4250.0,元/吨,Mysteel,2025-01-22,2.3,95.0
螺纹钢,product,4155.0,元/吨,Mysteel,2025-01-21,-0.5,-21.0
```

### 数据库字段

数据自动写入 `market_price_data` 表，字段包括：

- `material_type` - 材料类型
- `category` - 分类（raw_material/product）
- `price` - 价格
- `unit` - 单位（元/吨）
- `source` - 数据来源（Mysteel）
- `price_date` - 价格日期
- `change_rate` - 涨跌幅（%）
- `change_amount` - 涨跌金额
- `volume` - 成交量（吨）
- `created_by` - 创建者ID

---

## 技术细节

### v2.0 核心改进

#### 1. 日期选择器修复

**问题**: 原代码使用 `data-day` 属性定位失败

**解决方案**:
```python
# ❌ 旧方法（失败）
day_xpath = f"//td[@data-day='{date_obj.strftime('%m/%d/%Y')}']"

# ✅ 新方法（成功）
day_xpath = f"//td[contains(@class, 'available') and text()='{day_text}']"
```

**关键改进**:
- 使用 `text()` 直接匹配单元格文本
- 使用 `contains(@class, 'available')` 确保日期可选
- 自动去掉前导0（"02" → "2"）
- 区分开始/结束日期的容器路径（`div[3]` vs `div[4]`）

#### 2. 材料选择修复

**问题**: 铁矿石、焦炭等材料的 ID 无法定位

**解决方案**: 多种方法回退机制
1. 通过 ID 定位（主要方法）
2. 通过文本内容匹配（备用方法）
3. 通过 CSS 选择器遍历（最后尝试）

---

## 相关资源

- **项目文档**: [AGENTS.md](../AGENTS.md) - Market Analysis System 章节
- **快速参考**: [scripts/QUICK_REFERENCE.md](../scripts/QUICK_REFERENCE.md)
- **Mysteel官网**: https://www.mysteel.com/
- **Mysteel数据服务**: https://mds.mysteel.com/
- **原始教程**: https://blog.csdn.net/qq_58602552/article/details/147493285

---

## 更新日志

### v2.0 (2025-10-23)
- ✅ 统一CLI工具
- ✅ 修复日期选择器（使用 text() 和 available class）
- ✅ 修复材料选择（多种方法回退）
- ✅ 添加测试和诊断功能
- ✅ 完善的错误处理和截图
- ✅ 支持批量爬取多个材料

### v1.0 (之前)
- 基本爬虫功能
- 单材料爬取
- 简单错误处理

---

## 获取帮助

如有问题，请：

1. 查看本文档相关章节
2. 运行测试: `python scripts/mysteel_cli.py test`
3. 运行诊断: `python scripts/mysteel_cli.py diagnose`
4. 查看错误截图: `error_screenshot_*.png`

---

**完成！现在你可以使用统一的 CLI 工具进行所有爬虫操作了！** 🎉

