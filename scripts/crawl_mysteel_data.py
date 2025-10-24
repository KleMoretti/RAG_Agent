"""
Mysteel钢铁价格数据爬虫
基于 Selenium 自动化爬取我的钢铁网价格数据
参考教程: https://blog.csdn.net/qq_58602552/article/details/147493285

使用方法:
    python scripts/crawl_mysteel_data.py --start-date 2025-01-01 --end-date 2025-01-31 --material 螺纹

支持的材料类型:
    - 螺纹 (LUOWEN)
    - 热卷 (REJUAN)
    - 冷卷 (LENGJUAN)
    - 中厚板 (ZHONGHOUBAN)
    - 铁矿石 (TEKUANGSHI)
    - 焦炭 (JIAOTA)
"""
from __future__ import annotations

import argparse
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 添加项目路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.db import get_db
from src.api.models import MarketPriceData

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 材料类型映射
MATERIAL_MAPPING = {
    "螺纹": {"id": "LUOWEN", "name": "螺纹钢", "category": "product"},
    "热卷": {"id": "REJUAN", "name": "热轧卷板", "category": "product"},
    "冷卷": {"id": "LENGJUAN", "name": "冷轧卷板", "category": "product"},
    "中厚板": {"id": "ZHONGHOUBAN", "name": "中厚板", "category": "product"},
    "铁矿石": {"id": "TEKUANGSHI", "name": "铁矿石", "category": "raw_material"},
    "焦炭": {"id": "JIAOTA", "name": "焦炭", "category": "raw_material"},
}


class MysteelCrawler:
    """Mysteel数据爬虫"""
    
    def __init__(self, headless: bool = True, driver_path: str | None = None):
        """
        初始化爬虫
        
        Args:
            headless: 是否使用无头模式
            
        """
        self.base_url = "https://index.mysteel.com/xpic/detail.html?tabName=pugang"
        self.driver = self._init_driver(headless, driver_path)
    
    @staticmethod
    def _align_to_week_boundary(date_str: str, is_start: bool = True) -> str:
        """
        将日期对齐到周边界（按周查询必须：周一-周日）
        
        Args:
            date_str: 输入日期字符串 (YYYY-MM-DD)
            is_start: True=对齐到周一(周起始), False=对齐到周日(周结束)
        
        Returns:
            对齐后的日期字符串 (YYYY-MM-DD)
        """
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        weekday = date_obj.weekday()  # 0=周一, 1=周二, ..., 6=周日
        
        if is_start:
            # 对齐到周一（往前推）
            if weekday == 0:  # 已经是周一
                aligned_date = date_obj
            else:
                days_to_monday = weekday  # 往前推到周一
                aligned_date = date_obj - timedelta(days=days_to_monday)
        else:
            # 对齐到周日（往后推）
            if weekday == 6:  # 已经是周日
                aligned_date = date_obj
            else:
                days_to_sunday = 6 - weekday  # 往后推到周日
                aligned_date = date_obj + timedelta(days=days_to_sunday)
        
        return aligned_date.strftime("%Y-%m-%d")
        
    def _init_driver(self, headless: bool, driver_path: str | None):
        """初始化浏览器驱动"""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument("--headless=new")  # 使用新版无头模式
            chrome_options.add_argument("--disable-gpu")
        
        # 基础配置
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # 网络和SSL配置
        chrome_options.add_argument("--ignore-certificate-errors")  # 忽略SSL证书错误
        chrome_options.add_argument("--ignore-ssl-errors")
        chrome_options.add_argument("--disable-web-security")
        
        # 性能优化
        chrome_options.add_argument("--disable-software-rasterizer")  # 禁用软件光栅化
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--log-level=3")  # 仅显示严重错误
        
        # User-Agent
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # 实验性功能
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        try:
            if driver_path:
                service = Service(driver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                # 使用 webdriver-manager 自动管理驱动
                from webdriver_manager.chrome import ChromeDriverManager
                driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=chrome_options
                )
            
            logger.info("✅ 浏览器驱动初始化成功")
            return driver
            
        except Exception as e:
            logger.error(f"❌ 浏览器驱动初始化失败: {e}")
            logger.info("提示：请安装 webdriver-manager: pip install webdriver-manager")
            raise
    
    def crawl_price_data(
        self,
        material_key: str,
        start_date: str,
        end_date: str,
        max_retries: int = 3
    ) -> pd.DataFrame:
        """
        爬取价格数据
        
        Args:
            material_key: 材料类型（如"螺纹"、"铁矿石"）
            start_date: 开始日期（YYYY-MM-DD）
            end_date: 结束日期（YYYY-MM-DD）
            max_retries: 最大重试次数
            
        Returns:
            DataFrame包含价格数据
        """
        if material_key not in MATERIAL_MAPPING:
            raise ValueError(f"不支持的材料类型: {material_key}")
        
        material_info = MATERIAL_MAPPING[material_key]
        logger.info(f"🔍 开始爬取 {material_info['name']} 数据 ({start_date} ~ {end_date})")
        
        for attempt in range(max_retries):
            try:
                # 1. 打开网站（带重试）
                logger.info(f"📡 正在连接网站... (尝试 {attempt + 1}/{max_retries})")
                self.driver.get(self.base_url)
                time.sleep(3)
                logger.info("✅ 网站加载完成")
                break  # 成功则跳出重试循环
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"⚠️ 连接失败，{5}秒后重试... 错误: {e}")
                    time.sleep(5)
                else:
                    raise Exception(f"网站连接失败（已重试{max_retries}次）: {e}")
        
        try:
            
            # 2. 点击右侧展开按钮
            self._click_expand_button()
            
            # 3. 选择材料类型
            self._select_material(material_info["id"], material_info["name"])
            
            # 4. 切换到"按日查询"
            self._switch_to_weekly_query()
            
            # 5. 输入日期范围
            self._input_date_range(start_date, end_date)
            
            # 6. 等待数据加载
            time.sleep(5)
            
            # 7. 提取数据
            data = self._extract_data()
            
            # 8. 数据处理
            df = self._process_data(data, material_info)
            
            logger.info(f"✅ 成功爬取 {len(df)} 条数据")
            return df
            
        except Exception as e:
            logger.error(f"❌ 爬取失败: {e}")
            # 保存错误截图
            screenshot_path = f"error_screenshot_{int(time.time())}.png"
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"已保存错误截图: {screenshot_path}")
            raise
    
    def _click_expand_button(self):
        """点击右侧展开按钮"""
        try:
            expand_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "img.addBtn[src*='icon.png']"))
            )
            expand_btn.click()
            time.sleep(1)
            logger.info("✅ 点击展开按钮")
        except TimeoutException:
            logger.warning("⚠️ 展开按钮未找到，可能已展开")
    
    def _select_material(self, material_id: str, material_name: str):
        """选择材料类型"""
        try:
            # 方法1：通过ID查找
            try:
                material_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.ID, material_id))
                )
                material_btn.click()
                time.sleep(2)
                logger.info(f"✅ 选择材料: {material_name} (通过ID)")
                return
            except TimeoutException:
                logger.warning(f"⚠️ 通过ID未找到按钮: {material_id}，尝试其他方法...")
            
            # 方法2：通过文本内容查找（关键词匹配）
            keyword = material_name[:2]  # 取前两个字符，如"螺纹"、"铁矿"、"焦炭"
            all_elements = self.driver.find_elements(By.CSS_SELECTOR, "button, a, li, div[onclick]")
            
            for element in all_elements:
                try:
                    if keyword in element.text:
                        element.click()
                        time.sleep(2)
                        logger.info(f"✅ 选择材料: {material_name} (通过文本匹配)")
                        return
                except:
                    continue
            
            # 如果所有方法都失败
            raise Exception(f"未找到材料按钮: {material_id} ('{material_name}')")
            
        except TimeoutException:
            raise Exception(f"未找到材料按钮: {material_id}")
    
    def _switch_to_weekly_query(self):
        """切换到"按周查询"模式"""
        try:
            # 按周查询按钮（通过文本匹配）
            weekly_query_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '按周查询')]"))
            )
            weekly_query_btn.click()
            time.sleep(1)
            
            # 等待按周查询容器变为可见（dome2）
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "dome2"))
            )
            logger.info("✅ 切换到按周查询模式，容器已可见")
        except TimeoutException:
            raise Exception("未找到'按周查询'按钮或容器未显示")
    
    def _input_date_range(self, start_date: str, end_date: str):
        """输入日期范围（自动对齐到周边界）"""
        # 🔧 修复：按周查询必须对齐到周边界（周一-周日）
        aligned_start = self._align_to_week_boundary(start_date, is_start=True)
        aligned_end = self._align_to_week_boundary(end_date, is_start=False)
        
        if aligned_start != start_date or aligned_end != end_date:
            logger.info(f"📅 日期对齐: {start_date} → {aligned_start} (周一)")
            logger.info(f"📅 日期对齐: {end_date} → {aligned_end} (周日)")
        
        # 输入开始日期
        self._input_date("start", aligned_start)
        
        # 关键修复：选择完开始日期后，等待日历完全关闭
        time.sleep(2)
        logger.info("⏳ 等待开始日期日历关闭...")
        
        # 输入结束日期
        self._input_date("end", aligned_end)
        
        # 点击查询按钮（周查询的图片按钮）
        query_btn_found = False
        
        # 方法1：通过name属性定位周查询按钮
        try:
            query_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "img[name='week']"))
            )
            query_btn.click()
            time.sleep(3)  # 等待数据加载
            logger.info("✅ 点击查询按钮 (通过name='week')")
            query_btn_found = True
        except TimeoutException:
            logger.warning("⚠️ 方法1失败：img[name='week']未找到")
        
        # 方法2：通过class定位
        if not query_btn_found:
            try:
                query_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "img.tabSearchBtn"))
                )
                query_btn.click()
                time.sleep(3)
                logger.info("✅ 点击查询按钮 (通过class='tabSearchBtn')")
                query_btn_found = True
            except TimeoutException:
                logger.warning("⚠️ 方法2失败：tabSearchBtn未找到")
        
        # 方法3：通过XPath组合条件
        if not query_btn_found:
            try:
                query_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//img[@name='week' and @class='tabSearchBtn']"))
                )
                query_btn.click()
                time.sleep(3)
                logger.info("✅ 点击查询按钮 (通过XPath组合)")
                query_btn_found = True
            except TimeoutException:
                logger.warning("⚠️ 方法3失败：XPath组合未找到")
        
        if not query_btn_found:
            logger.warning("⚠️ 未找到查询按钮，等待数据自动加载")
            time.sleep(5)  # 给数据加载留足时间
    
    def _input_date(self, date_type: str, date_str: str):
        """
        输入日期（改进版：优先使用JavaScript填充，更可靠）
        
        Args:
            date_type: "start" 或 "end"
            date_str: 日期字符串（YYYY-MM-DD）
        """
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            
            # 确定输入框 ID
            input_id = "startWeek" if date_type == "start" else "endWeek"
            
            # 等待输入框可点击
            date_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, input_id))
            )
            
            logger.info(f"📅 开始填充{date_type}日期: {date_str}")
            
            # ==================== 方法1: JavaScript 直接填充（推荐，最可靠） ====================
            try:
                # 点击输入框以激活
                date_input.click()
                time.sleep(1)
                
                # 使用 JavaScript 直接设置值并触发所有可能的事件
                self.driver.execute_script("""
                    const input = arguments[0];
                    const value = arguments[1];
                    
                    // 设置值
                    input.value = value;
                    
                    // 触发所有可能的事件
                    ['input', 'change', 'blur', 'keyup', 'keydown'].forEach(eventType => {
                        const event = new Event(eventType, { 
                            bubbles: true, 
                            cancelable: true 
                        });
                        input.dispatchEvent(event);
                    });
                    
                    // 如果有 jQuery 绑定的事件
                    if (typeof jQuery !== 'undefined') {
                        jQuery(input).trigger('change');
                        jQuery(input).trigger('input');
                    }
                    
                    // 确保焦点离开（触发验证）
                    input.blur();
                """, date_input, date_str)
                
                time.sleep(1)
                
                # 验证是否成功
                input_value = date_input.get_attribute('value')
                if input_value and (input_value == date_str or date_str in input_value):
                    logger.info(f"✅ JavaScript填充成功：{date_type}输入框值 = {input_value}")
                    return  # 成功，直接返回
                else:
                    logger.warning(f"⚠️ JavaScript填充后值不匹配：期望 {date_str}, 实际 {input_value}")
            
            except Exception as e:
                logger.warning(f"⚠️ JavaScript填充方法失败: {e}")
            
            # ==================== 方法2: 传统日历选择器方法（备用） ====================
            try:
                # 点击输入框打开日历
                date_input.click()
                time.sleep(2)
                logger.info("🖱️ 点击输入框，等待日历弹出...")
                
                # 动态查找日历容器（不使用硬编码路径）
                calendar_found = False
                year_select = None
                month_select = None
                
                # 尝试多种定位方式
                for attempt in range(3):
                    try:
                        # 方式1: 查找可见的年份选择器
                        year_selects = self.driver.find_elements(By.XPATH, "//select[contains(@class, 'yearselect') or @aria-label='Year']")
                        for sel in year_selects:
                            if sel.is_displayed():
                                year_select = sel
                                # 找到对应的月份选择器
                                parent = sel.find_element(By.XPATH, "../..")
                                month_selects = parent.find_elements(By.TAG_NAME, "select")
                                if len(month_selects) >= 2:
                                    month_select = month_selects[0]
                                    calendar_found = True
                                    logger.info("✅ 找到日历选择器（方式1：yearselect class）")
                                    break
                        
                        if not calendar_found:
                            # 方式2: 遍历所有 div 查找包含年份选择器的容器
                            for div_index in range(1, 15):
                                try:
                                    xpath_year = f"/html/body/div[{div_index}]//select"
                                    selects = self.driver.find_elements(By.XPATH, xpath_year)
                                    if len(selects) >= 2 and selects[0].is_displayed():
                                        # 检查是否真的是日期选择器（包含年份选项）
                                        options = selects[1].find_elements(By.TAG_NAME, "option")
                                        if options and any("202" in opt.get_attribute("value") or "" for opt in options[:3]):
                                            month_select = selects[0]
                                            year_select = selects[1]
                                            calendar_found = True
                                            logger.info(f"✅ 找到日历选择器（方式2：div[{div_index}]）")
                                            break
                                except:
                                    continue
                        
                        if calendar_found:
                            break
                        
                        time.sleep(1)
                    
                    except Exception as e:
                        logger.warning(f"查找日历容器失败（尝试 {attempt + 1}/3）: {e}")
                        time.sleep(1)
                
                if not calendar_found:
                    raise Exception("无法找到日历选择器")
                
                # 选择年份
                year_dropdown = Select(year_select)
                year_dropdown.select_by_value(str(date_obj.year))
                time.sleep(0.8)
                logger.info(f"  ✅ 选择年份: {date_obj.year}")
                
                # 选择月份（月份从0开始）
                month_dropdown = Select(month_select)
                month_dropdown.select_by_value(str(date_obj.month - 1))
                time.sleep(0.8)
                logger.info(f"  ✅ 选择月份: {date_obj.month}")
                
                # 选择日期
                day_text = str(date_obj.day)
                
                # 尝试多种日期选择方法
                day_selected = False
                
                # 尝试1: available class + text
                try:
                    day_xpath = f"//td[contains(@class, 'available') and text()='{day_text}']"
                    day_element = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, day_xpath))
                    )
                    self.driver.execute_script("arguments[0].click();", day_element)
                    day_selected = True
                    logger.info(f"  ✅ 选择日期: {day_text} (available class)")
                except:
                    pass
                
                # 尝试2: 仅 text 匹配
                if not day_selected:
                    try:
                        day_cells = self.driver.find_elements(By.XPATH, f"//td[text()='{day_text}']")
                        for cell in day_cells:
                            if cell.is_displayed() and "old" not in cell.get_attribute("class"):
                                self.driver.execute_script("arguments[0].click();", cell)
                                day_selected = True
                                logger.info(f"  ✅ 选择日期: {day_text} (text匹配)")
                                break
                    except:
                        pass
                
                if not day_selected:
                    raise Exception(f"无法选择日期 {day_text}")
                
                time.sleep(1)
                
                # 验证日期是否填入成功
                input_value = date_input.get_attribute('value')
                if input_value and (input_value == date_str or date_str in input_value):
                    logger.info(f"✅ 日历选择成功：{date_type}输入框值 = {input_value}")
                    return  # 成功，直接返回
                else:
                    logger.warning(f"⚠️ 日历选择后值不匹配：期望 {date_str}, 实际 {input_value}")
                    # 再次尝试 JavaScript 填充
                    self.driver.execute_script("""
                        arguments[0].value = arguments[1];
                        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                    """, date_input, date_str)
                    time.sleep(0.5)
            
            except Exception as e:
                logger.warning(f"⚠️ 传统日历选择方法失败: {e}")
            
            # ==================== 最终验证 ====================
            input_value = date_input.get_attribute('value')
            if not input_value:
                logger.error(f"❌ 所有方法都失败：{date_type}输入框仍为空")
                # 保存截图用于调试
                screenshot_path = f"date_input_failed_{date_type}_{int(time.time())}.png"
                self.driver.save_screenshot(screenshot_path)
                logger.error(f"已保存失败截图: {screenshot_path}")
                raise Exception(f"无法填充{date_type}日期：所有方法都失败")
            else:
                logger.info(f"✅ 最终验证成功：{date_type}输入框值 = {input_value}")
        
        except Exception as e:
            logger.error(f"❌ 输入日期失败 ({date_type}): {e}")
            raise
    
    def _extract_data(self) -> list[dict]:
        """提取页面数据（修复：使用detailTab而非dataTable）"""
        try:
            # 🔧 修复1：表格class为detailTab（不是dataTable）
            # 🔧 修复2：增加超时时间到30秒
            table = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "detailTab"))
            )
            logger.info("✅ 找到 detailTab 表格")
            
            # 提取表格数据（detailTab 结构不同）
            tbody = table.find_element(By.TAG_NAME, "tbody")
            rows = tbody.find_elements(By.TAG_NAME, "tr")
            data = []
            
            logger.info(f"📊 找到 {len(rows)} 行数据")
            
            for idx, row in enumerate(rows):
                try:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    
                    # 跳过分类标题行（colspan=10的行）
                    if len(cols) == 1 or cols[0].get_attribute("colspan"):
                        logger.debug(f"跳过分类标题行: {cols[0].text}")
                        continue
                    
                    if len(cols) >= 4:
                        # detailTab 格式：品种名称 | 本日 | 昨日 | 日环比 | 上周 | 周环比 | ...
                        # 我们需要：日期、价格、涨跌幅
                        variety_name = cols[0].text.strip()
                        today_price = cols[1].text.strip()
                        daily_change = cols[3].text.strip()  # 日环比
                        
                        # 清理数据（移除颜色标签、百分号）
                        daily_change = daily_change.replace("%", "").replace("+", "")
                        
                        data.append({
                            "variety": variety_name,  # 品种名称
                            "date": datetime.now().strftime("%Y-%m-%d"),  # 使用当前日期
                            "price": today_price,
                            "change_rate": daily_change,
                            "change_amount": "",  # detailTab没有涨跌金额
                        })
                        
                        logger.debug(f"提取数据 {idx+1}: {variety_name} = {today_price} ({daily_change}%)")
                        
                except (IndexError, ValueError, AttributeError) as e:
                    logger.warning(f"⚠️ 跳过无效行 {idx+1}: {e}")
                    continue
            
            logger.info(f"✅ 成功提取 {len(data)} 条数据")
            return data
            
        except TimeoutException:
            logger.error("❌ 数据表格加载超时 (30秒)")
            # 保存截图用于调试
            try:
                screenshot_path = f"table_timeout_{int(time.time())}.png"
                self.driver.save_screenshot(screenshot_path)
                logger.info(f"已保存超时截图: {screenshot_path}")
            except:
                pass
            return []
        except Exception as e:
            logger.error(f"❌ 提取数据时出错: {e}")
            return []
    
    def _process_data(self, data: list[dict], material_info: dict) -> pd.DataFrame:
        """处理数据为标准格式"""
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        
        # 数据清洗
        df["material_type"] = material_info["name"]
        df["category"] = material_info["category"]
        df["source"] = "Mysteel"
        df["unit"] = "元/吨"
        
        # 转换价格
        df["price"] = df["price"].str.replace(",", "").astype(float)
        
        # 转换涨跌幅（移除百分号和加号）
        df["change_rate"] = (
            df["change_rate"]
            .str.replace("%", "")
            .str.replace("+", "")
            .replace("", "0")  # 空值替换为0
            .astype(float)
        )
        
        # 处理涨跌金额（detailTab没有此字段，设为0或None）
        if "change_amount" in df.columns and df["change_amount"].notna().any():
            df["change_amount"] = (
                df["change_amount"]
                .str.replace("+", "")
                .replace("", "0")
                .astype(float)
            )
        else:
            df["change_amount"] = 0.0
        
        # 转换日期
        df["price_date"] = pd.to_datetime(df["date"])
        df = df.drop(columns=["date"])
        
        # 删除品种列（如果存在）
        if "variety" in df.columns:
            df = df.drop(columns=["variety"])
        
        return df
    
    def save_to_csv(self, df: pd.DataFrame, output_path: str):
        """保存数据到CSV"""
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        logger.info(f"✅ 数据已保存到: {output_path}")
    
    def save_to_database(self, df: pd.DataFrame, user_id: int = 1):
        """保存数据到数据库"""
        db = next(get_db())
        
        try:
            success_count = 0
            for _, row in df.iterrows():
                price_data = MarketPriceData(
                    material_type=row["material_type"],
                    category=row["category"],
                    price=row["price"],
                    unit=row["unit"],
                    source=row["source"],
                    price_date=row["price_date"],
                    change_rate=row["change_rate"],
                    change_amount=row["change_amount"],
                    created_by=user_id,
                )
                db.add(price_data)
                success_count += 1
            
            db.commit()
            logger.info(f"✅ 成功写入数据库: {success_count} 条记录")
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 数据库写入失败: {e}")
            raise
        finally:
            db.close()
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("✅ 浏览器已关闭")
            except Exception as e:
                logger.warning(f"⚠️ 关闭浏览器时出现警告（可忽略）: {e}")
                # 强制终止 Chrome 进程（Windows）
                try:
                    import os
                    os.system("taskkill /F /IM chrome.exe /T >nul 2>&1")
                    os.system("taskkill /F /IM chromedriver.exe /T >nul 2>&1")
                except:
                    pass


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Mysteel钢铁价格数据爬虫")
    parser.add_argument(
        "--material",
        type=str,
        default="螺纹",
        choices=list(MATERIAL_MAPPING.keys()),
        help="材料类型",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
        help="开始日期（YYYY-MM-DD）",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        default=datetime.now().strftime("%Y-%m-%d"),
        help="结束日期（YYYY-MM-DD）",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="输出CSV文件路径（可选）",
    )
    parser.add_argument(
        "--save-db",
        action="store_true",
        help="是否保存到数据库",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="是否使用无头模式（默认True）",
    )
    parser.add_argument(
        "--driver-path",
        type=str,
        default=None,
        help="ChromeDriver路径（可选）",
    )
    
    args = parser.parse_args()
    
    crawler = None
    try:
        # 初始化爬虫
        crawler = MysteelCrawler(headless=args.headless, driver_path=args.driver_path)
        
        # 爬取数据
        df = crawler.crawl_price_data(
            material_key=args.material,
            start_date=args.start_date,
            end_date=args.end_date
        )
        
        if df.empty:
            logger.warning("⚠️ 未获取到任何数据")
            return
        
        # 保存到CSV
        if args.output:
            crawler.save_to_csv(df, args.output)
        else:
            default_output = f"mysteel_{args.material}_{args.start_date}_{args.end_date}.csv"
            crawler.save_to_csv(df, default_output)
        
        # 保存到数据库
        if args.save_db:
            crawler.save_to_database(df)
        
        logger.info("🎉 爬虫任务完成！")
        
    except KeyboardInterrupt:
        logger.warning("⚠️ 用户中断任务")
    except Exception as e:
        logger.error(f"❌ 任务失败: {e}")
    finally:
        if crawler:
            crawler.close()


if __name__ == "__main__":
    main()

