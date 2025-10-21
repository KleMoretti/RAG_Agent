# Markdown 渲染功能

## 概述

聊天界面现已支持完整的 Markdown 渲染，让 AI 回复更加结构化、易读。

## 功能特性

### ✅ 支持的 Markdown 语法

- **文本格式**：粗体、斜体、删除线
- **标题**：H1 到 H6 六级标题
- **列表**：有序列表、无序列表、任务列表
- **代码**：行内代码、多行代码块（带语言标签）
- **引用**：块引用
- **表格**：完整的表格支持
- **链接**：自动在新标签页打开外部链接
- **分割线**：水平分割线
- **GitHub Flavored Markdown (GFM)**：扩展语法支持

### 🎨 主题适配

- 自动适配亮色/暗色主题
- 使用 CSS 变量确保颜色一致性
- 代码块在暗色模式下有更好的对比度

## 技术实现

### 核心依赖

```json
{
  "react-markdown": "^10.1.0",
  "remark-gfm": "^4.0.1",
  "rehype-raw": "^7.0.0"
}
```

### 组件结构

```
components/chat/
├── MarkdownContent.tsx      # Markdown 渲染核心组件
├── ChatMessage.tsx          # 历史消息（AI 消息使用 Markdown）
├── StreamingMessage.tsx     # 流式消息（实时 Markdown 渲染）
└── index.ts                 # 导出
```

### 使用示例

```typescript
import { MarkdownContent } from '@/components/chat';

// 基础使用
<MarkdownContent content={aiResponse} />

// 带自定义样式
<MarkdownContent 
  content={aiResponse} 
  className="text-sm"
/>
```

## 样式定制

所有 Markdown 样式定义在 `app/globals.css` 中：

```css
/* 基础 prose 样式 */
.prose {
  color: var(--foreground);
  max-width: none;
}

/* 代码块样式 */
.prose pre {
  background-color: var(--muted);
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
}

/* 表格样式 */
.prose table {
  border-collapse: collapse;
  border: 1px solid var(--border);
}
```

## 实际效果

### 示例 1：技术文档

**输入（AI 返回）：**
```markdown
## 设备故障诊断

根据您的描述，可能的原因包括：

1. **温度传感器故障**
   - 检查传感器连接
   - 测试传感器输出电压

2. **冷却系统异常**
   ```python
   # 检查冷却水流量
   if flow_rate < MIN_FLOW:
       trigger_alarm("冷却水流量不足")
   ```

| 参数 | 正常值 | 当前值 | 状态 |
|------|--------|--------|------|
| 温度 | 1500°C | 1850°C | ⚠️ 异常 |
| 压力 | 120MPa | 115MPa | ✅ 正常 |
```

**渲染效果：**
- 标题清晰分层
- 代码块带语法高亮和语言标签
- 表格自动对齐，边框清晰
- 图标符号正常显示

### 示例 2：操作指南

**输入：**
```markdown
### 操作步骤

> ⚠️ **警告**：操作前请确保设备已断电。

按以下顺序操作：

1. 关闭主电源开关
2. 等待 **5 分钟** 冷却
3. 使用 `multimeter` 测试电压：
   ```bash
   voltage_test --device=motor_01
   ```
4. 记录结果到维护日志

---

**注意事项**：
- [ ] 佩戴绝缘手套
- [ ] 使用绝缘工具
- [ ] 双人作业，相互监督
```

**渲染效果：**
- 引用块突出显示警告信息
- 粗体文字加粗显示
- 行内代码带背景色
- 任务列表显示复选框
- 分割线清晰分隔内容

## 最佳实践

### ✅ 推荐

1. **结构化回答**：使用标题组织内容层次
   ```markdown
   ## 主要问题
   ### 问题分析
   ### 解决方案
   ```

2. **突出重点**：使用引用块强调重要信息
   ```markdown
   > ⚠️ **安全提醒**：高温作业请佩戴防护装备
   ```

3. **代码展示**：技术细节用代码块
   ```markdown
   ```python
   def check_temperature():
       return sensor.read()
   ``` # 注意：实际使用时去掉这个注释
   ```

4. **数据对比**：使用表格呈现参数
   ```markdown
   | 设备 | 温度 | 状态 |
   |------|------|------|
   | A | 1500 | 正常 |
   ```

### ❌ 避免

1. **纯文本堆砌**：缺乏结构层次
2. **过度嵌套**：标题层级过深（超过 H4）
3. **表格过宽**：移动端显示困难
4. **代码块无语言标签**：缺少语法提示

## 扩展功能

### 添加语法高亮（可选）

如需更丰富的代码高亮，安装：

```bash
npm install react-syntax-highlighter @types/react-syntax-highlighter
```

修改 `MarkdownContent.tsx`：

```typescript
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

// 在 code 组件中使用
code: ({ className, children }) => {
  const match = /language-(\w+)/.exec(className || '');
  return match ? (
    <SyntaxHighlighter style={oneDark} language={match[1]}>
      {String(children)}
    </SyntaxHighlighter>
  ) : (
    <code className={className}>{children}</code>
  );
}
```

### 自定义主题

在 `globals.css` 中修改 prose 样式：

```css
/* 自定义代码块背景色 */
.prose pre {
  background: linear-gradient(135deg, var(--muted) 0%, var(--accent) 100%);
}

/* 自定义链接颜色 */
.prose a {
  color: var(--chart-1);
}
```

## 调试技巧

### 问题：Markdown 未渲染

**检查清单**：
1. ✅ 依赖已安装：`npm list react-markdown`
2. ✅ 组件正确导入：`import { MarkdownContent } from '@/components/chat'`
3. ✅ 样式已加载：检查浏览器开发者工具中的 `.prose` 类

### 问题：代码块显示异常

**原因**：可能是 CSS 冲突

**解决**：
```css
/* 确保代码块不继承父元素样式 */
.prose pre {
  all: revert;
  background-color: var(--muted);
  /* ... 其他样式 */
}
```

### 问题：表格在移动端溢出

**解决**：已添加滚动容器
```typescript
table: ({ children }) => (
  <div className="overflow-x-auto">
    <table>{children}</table>
  </div>
)
```

## 性能优化

### Lazy Loading

对于长文本，使用虚拟滚动：

```typescript
import { useVirtualizer } from '@tanstack/react-virtual';

// 仅渲染可见区域的消息
const virtualizer = useVirtualizer({
  count: messages.length,
  getScrollElement: () => scrollRef.current,
  estimateSize: () => 100,
});
```

### 记忆化

避免重复渲染相同内容：

```typescript
const MemoizedMarkdown = React.memo(MarkdownContent);
```

## 参考资源

- **完整示例**：`docs/MARKDOWN_EXAMPLES.md`
- **组件源码**：`frontend/components/chat/MarkdownContent.tsx`
- **样式定义**：`frontend/app/globals.css`
- **react-markdown 文档**：https://github.com/remarkjs/react-markdown
- **GFM 规范**：https://github.github.com/gfm/

## 更新日志

### v1.0 (2024)
- ✅ 基础 Markdown 渲染
- ✅ GFM 支持（表格、任务列表）
- ✅ 主题自动适配
- ✅ 代码块语言标签
- ✅ 流式渲染支持

---

**维护者**：Frontend Team  
**最后更新**：2024年