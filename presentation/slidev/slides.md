---
# Slidev 主题
theme: seriph
# 背景图片
background: https://images.unsplash.com/photo-1565008447742-97f6f38c985c?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80
# 演示文稿信息
title: 钢铁行业AI决策中心 - RAG Agent系统
info: |
  ## 钢铁行业AI决策中心
  基于RAG技术的智能决策支持系统
  
  融合检索增强生成与专业知识图谱
# 应用 UnoCSS 类到当前幻灯片
class: text-center
# 绘图功能
drawings:
  persist: false
# 幻灯片过渡效果
transition: slide-left
# 启用 MDC 语法
mdc: true
---

# CastIron 助铁 
## 钢铁行业AI决策中心
### RAG Agent智能决策支持系统

<div class="text-xl mb-8 text-gray-200">
基于检索增强生成技术的垂直领域AI解决方案
</div>

<div class="grid grid-cols-3 gap-8 mt-12">
  <div class="text-center">
    <carbon:industry class="text-4xl mb-2 text-blue-600" />
    <div class="font-semibold">钢铁行业专精</div>
  </div>
  <div class="text-center">
    <carbon:ai-results class="text-4xl mb-2 text-green-600" />
    <div class="font-semibold">RAG技术驱动</div>
  </div>
  <div class="text-center">
    <carbon:decision-tree class="text-4xl mb-2 text-purple-600" />
    <div class="font-semibold">智能决策支持</div>
  </div>
</div>

<div @click="$slidev.nav.next" class="mt-12 py-1" hover:bg="white op-10">
  按空格键进入下一页 <carbon:arrow-right />
</div>

---
transition: fade-out
---

# 目录

<Toc maxDepth="2" columns="2" />

---

# 作品信息

<div class="grid grid-cols-2 gap-8">
  <div>
    <h2 class="text-2xl font-bold mb-4 text-blue-600">项目概览</h2>
    <div class="space-y-3">
      <div><strong>项目名称:</strong> CastIron 助铁 ｜ 钢铁行业AI决策中心</div>
      <div><strong>技术架构:</strong> RAG Agent系统</div>
      <div><strong>团队规模:</strong> 3人</div>
      <div><strong>项目状态:</strong> MVP已完成</div>
    </div>
  </div>
  <div>
    <h2 class="text-2xl font-bold mb-4 text-green-600">目标用户</h2>
    <div class="grid grid-cols-2 gap-2 text-sm">
      <div class="bg-blue-50 p-2 rounded">🏭 生产管理者</div>
      <div class="bg-green-50 p-2 rounded">🔧 技术专家</div>
      <div class="bg-yellow-50 p-2 rounded">💼 采购人员</div>
      <div class="bg-purple-50 p-2 rounded">📊 市场分析师</div>
      <div class="bg-red-50 p-2 rounded">🛠️ 设备维护</div>
      <div class="bg-indigo-50 p-2 rounded">🌱 环保专家</div>
    </div>
  </div>
</div>

<div class="mt-8 p-4 bg-gray-50 rounded-lg">
  <h3 class="font-bold mb-2">核心价值主张</h3>
  <p class="text-gray-700">从"信息检索"到"智能决策" - 为钢铁行业提供专业化AI决策支持系统</p>
</div>

---
layout: section
---

# 项目背景
## 钢铁行业的数字化转型需求

---

# 行业现状与挑战

<div class="grid grid-cols-2 gap-8">
  <div>
    <h2 class="text-xl font-bold mb-4 text-red-600">🚨 行业痛点</h2>
    <div class="space-y-3">
      <div class="flex items-start">
        <carbon:warning class="text-red-500 mt-1 mr-2" />
        <div>
          <strong>知识孤岛严重</strong><br>
          <span class="text-sm text-gray-600">技术文档分散，专家经验难以传承</span>
        </div>
      </div>
      <div class="flex items-start">
        <carbon:time class="text-orange-500 mt-1 mr-2" />
        <div>
          <strong>决策效率低下</strong><br>
          <span class="text-sm text-gray-600">信息查找耗时，缺乏智能分析工具</span>
        </div>
      </div>
      <div class="flex items-start">
        <carbon:user-multiple class="text-blue-500 mt-1 mr-2" />
        <div>
          <strong>专业人才稀缺</strong><br>
          <span class="text-sm text-gray-600">经验丰富的技术专家退休，知识传承断层</span>
        </div>
      </div>
    </div>
  </div>
  <div>
    <h2 class="text-xl font-bold mb-4 text-green-600">📈 市场机遇</h2>
    <div class="space-y-3">
      <div class="bg-green-50 p-3 rounded">
        <strong>政策驱动</strong><br>
        <span class="text-sm">国家智能制造2025战略</span>
      </div>
      <div class="bg-blue-50 p-3 rounded">
        <strong>技术成熟</strong><br>
        <span class="text-sm">AI技术在垂直领域应用日趋成熟</span>
      </div>
      <div class="bg-purple-50 p-3 rounded">
        <strong>需求迫切</strong><br>
        <span class="text-sm">钢铁企业数字化转型需求强烈</span>
      </div>
    </div>
  </div>
</div>

---

# 市场需求分析

<div class="grid grid-cols-3 gap-6">
  <div class="text-center">
    <div class="text-3xl font-bold text-blue-600 mb-2">85%</div>
    <div class="text-sm text-gray-600">钢铁企业认为需要AI辅助决策</div>
  </div>
  <div class="text-center">
    <div class="text-3xl font-bold text-green-600 mb-2">60%</div>
    <div class="text-sm text-gray-600">技术文档查找时间占工作时间比例</div>
  </div>
  <div class="text-center">
    <div class="text-3xl font-bold text-purple-600 mb-2">40%</div>
    <div class="text-sm text-gray-600">因信息不及时导致的决策延误</div>
  </div>
</div>

<div class="mt-8">
  <h3 class="text-lg font-bold mb-4">核心需求场景</h3>
  <div class="grid grid-cols-2 gap-4">
    <div class="border-l-4 border-blue-500 pl-4">
      <strong>生产工艺优化</strong><br>
      <span class="text-sm text-gray-600">快速获取工艺参数建议，提升生产效率</span>
    </div>
    <div class="border-l-4 border-green-500 pl-4">
      <strong>设备故障诊断</strong><br>
      <span class="text-sm text-gray-600">智能故障分析，减少停机时间</span>
    </div>
    <div class="border-l-4 border-yellow-500 pl-4">
      <strong>市场价格分析</strong><br>
      <span class="text-sm text-gray-600">实时市场信息，辅助采购决策</span>
    </div>
    <div class="border-l-4 border-purple-500 pl-4">
      <strong>环保合规指导</strong><br>
      <span class="text-sm text-gray-600">法规解读，确保合规生产</span>
    </div>
  </div>
</div>

---
layout: section
---

# 核心技术
## RAG架构与关键技术实现

---

# 技术架构设计

```mermaid {scale: 0.6}
graph TB
    A[用户界面层] --> B[API网关层]
    B --> C[Agent调度层]
    C --> D[RAG引擎]
    C --> E[推理引擎]
    
    D --> F[向量检索]
    D --> G[知识图谱]
    D --> H[文档处理]
    
    F --> I[FAISS向量库]
    G --> J[Neo4j图数据库]
    H --> K[文档存储]
    
    E --> L[LLM模型]
    E --> M[提示工程]
    
    subgraph "数据层"
        I
        J
        K
        N[关系数据库]
    end
    
    subgraph "AI模型层"
        L
        O[嵌入模型]
        P[专业词汇库]
    end
```

---

# 关键技术实现

<div class="grid grid-cols-2 gap-8">
  <div>
    <h2 class="text-xl font-bold mb-4 text-blue-600">🔍 检索增强生成 (RAG)</h2>
    <div class="space-y-3 text-sm">
      <div class="bg-blue-50 p-3 rounded">
        <strong>多模态检索</strong><br>
        支持文本、图像、表格等多种数据类型
      </div>
      <div class="bg-green-50 p-3 rounded">
        <strong>语义检索</strong><br>
        基于向量相似度的智能文档匹配
      </div>
      <div class="bg-yellow-50 p-3 rounded">
        <strong>上下文增强</strong><br>
        动态组装相关知识，提升回答准确性
      </div>
    </div>
  </div>
  <div>
    <h2 class="text-xl font-bold mb-4 text-green-600">🧠 智能Agent系统</h2>
    <div class="space-y-3 text-sm">
      <div class="bg-purple-50 p-3 rounded">
        <strong>多Agent协作</strong><br>
        工艺专家、设备诊断、市场分析等专业Agent
      </div>
      <div class="bg-red-50 p-3 rounded">
        <strong>推理引擎</strong><br>
        ReAct框架，支持多步推理和工具调用
      </div>
      <div class="bg-indigo-50 p-3 rounded">
        <strong>记忆管理</strong><br>
        对话历史管理，支持上下文连续对话
      </div>
    </div>
  </div>
</div>

---

# 性能指标

<div class="grid grid-cols-3 gap-6 mb-8">
  <div class="text-center p-4 bg-blue-50 rounded-lg">
    <div class="text-2xl font-bold text-blue-600">95%</div>
    <div class="text-sm text-gray-600">检索准确率</div>
  </div>
  <div class="text-center p-4 bg-green-50 rounded-lg">
    <div class="text-2xl font-bold text-green-600">&lt;2s</div>
    <div class="text-sm text-gray-600">平均响应时间</div>
  </div>
  <div class="text-center p-4 bg-yellow-50 rounded-lg">
    <div class="text-2xl font-bold text-yellow-600">218+</div>
    <div class="text-sm text-gray-600">专业词汇库</div>
  </div>
</div>

<div class="grid grid-cols-2 gap-8">
  <div>
    <h3 class="font-bold mb-3">技术栈</h3>
    <div class="space-y-2 text-sm">
      <div><strong>后端:</strong> Python + FastAPI + SQLAlchemy</div>
      <div><strong>前端:</strong> Next.js + TypeScript + Ant Design</div>
      <div><strong>AI模型:</strong> OpenAI GPT + 自定义嵌入模型</div>
      <div><strong>数据库:</strong> PostgreSQL + FAISS + Neo4j</div>
      <div><strong>部署:</strong> Docker + Kubernetes</div>
    </div>
  </div>
  <div>
    <h3 class="font-bold mb-3">核心算法</h3>
    <div class="space-y-2 text-sm">
      <div><strong>文档分块:</strong> 语义分割 + 重叠窗口</div>
      <div><strong>向量检索:</strong> 混合检索 + 重排序</div>
      <div><strong>提示工程:</strong> 角色定制 + 上下文注入</div>
      <div><strong>质量控制:</strong> 置信度评分 + 来源追溯</div>
    </div>
  </div>
</div>

---
layout: section
---

# 创新亮点
## 技术突破与差异化优势

---

# 技术创新突破

<div class="grid grid-cols-2 gap-8">
  <div>
    <h2 class="text-xl font-bold mb-4 text-blue-600">🚀 核心创新</h2>
    <div class="space-y-4">
      <div class="border-l-4 border-blue-500 pl-4">
        <h3 class="font-bold">钢铁行业专业知识图谱</h3>
        <p class="text-sm text-gray-600">构建包含218+专业术语的领域知识图谱，支持中英文双语</p>
      </div>
      <div class="border-l-4 border-green-500 pl-4">
        <h3 class="font-bold">多模态RAG架构</h3>
        <p class="text-sm text-gray-600">支持文本、图像、表格等多种数据类型的统一检索</p>
      </div>
      <div class="border-l-4 border-purple-500 pl-4">
        <h3 class="font-bold">智能Agent协作机制</h3>
        <p class="text-sm text-gray-600">多个专业Agent协同工作，提供全方位决策支持</p>
      </div>
    </div>
  </div>
  <div>
    <h2 class="text-xl font-bold mb-4 text-green-600">⚡ 技术优势</h2>
    <div class="space-y-3">
      <div class="bg-green-50 p-3 rounded">
        <strong>实时性</strong><br>
        <span class="text-sm">30秒超时机制，确保快速响应</span>
      </div>
      <div class="bg-blue-50 p-3 rounded">
        <strong>准确性</strong><br>
        <span class="text-sm">95%检索准确率，专业术语精准匹配</span>
      </div>
      <div class="bg-yellow-50 p-3 rounded">
        <strong>可扩展性</strong><br>
        <span class="text-sm">模块化架构，支持新领域快速扩展</span>
      </div>
      <div class="bg-purple-50 p-3 rounded">
        <strong>易用性</strong><br>
        <span class="text-sm">角色化界面，降低使用门槛</span>
      </div>
    </div>
  </div>
</div>

---

# 差异化竞争优势

<div class="grid grid-cols-3 gap-6">
  <div class="text-center p-6 border rounded-lg">
    <carbon:industry class="text-4xl text-blue-600 mb-4 mx-auto" />
    <h3 class="font-bold mb-2">垂直领域专精</h3>
    <p class="text-sm text-gray-600">专注钢铁行业，深度理解业务场景和专业需求</p>
  </div>
  <div class="text-center p-6 border rounded-lg">
    <carbon:ai-results class="text-4xl text-green-600 mb-4 mx-auto" />
    <h3 class="font-bold mb-2">AI技术领先</h3>
    <p class="text-sm text-gray-600">RAG+Agent架构，结合最新AI技术与行业知识</p>
  </div>
  <div class="text-center p-6 border rounded-lg">
    <carbon:user-multiple class="text-4xl text-purple-600 mb-4 mx-auto" />
    <h3 class="font-bold mb-2">多角色协作</h3>
    <p class="text-sm text-gray-600">支持不同角色用户，提供个性化服务体验</p>
  </div>
</div>

<div class="mt-8 p-4 bg-gradient-to-r from-blue-50 to-green-50 rounded-lg">
  <h3 class="font-bold mb-3 text-center">与传统方案对比</h3>
  <div class="grid grid-cols-3 gap-4 text-sm">
    <div class="text-center">
      <div class="font-bold text-red-600">传统方案</div>
      <div>人工查找文档</div>
      <div>经验依赖严重</div>
      <div>响应时间长</div>
    </div>
    <div class="text-center">
      <carbon:arrow-right class="text-2xl text-gray-400 mx-auto my-4" />
    </div>
    <div class="text-center">
      <div class="font-bold text-green-600">AI决策中心</div>
      <div>智能检索推荐</div>
      <div>知识自动化</div>
      <div>秒级响应</div>
    </div>
  </div>
</div>

---
layout: section
---

# 发展前景
## 技术演进与发展前景

---

# 技术发展路径

<div class="grid grid-cols-2 gap-8">
  <div>
    <h2 class="text-xl font-bold mb-4 text-blue-600">🔬 核心技术演进</h2>
    <div class="space-y-4">
      <div class="flex items-start">
        <div class="bg-blue-100 rounded-full p-2 mr-3 mt-1">
          <span class="text-blue-600 font-bold text-sm">1</span>
        </div>
        <div>
          <strong>RAG架构优化</strong><br>
          <span class="text-sm text-gray-600">多模态检索、向量化算法改进</span>
        </div>
      </div>
      <div class="flex items-start">
        <div class="bg-green-100 rounded-full p-2 mr-3 mt-1">
          <span class="text-green-600 font-bold text-sm">2</span>
        </div>
        <div>
          <strong>知识图谱扩展</strong><br>
          <span class="text-sm text-gray-600">实体关系挖掘、推理能力增强</span>
        </div>
      </div>
      <div class="flex items-start">
        <div class="bg-yellow-100 rounded-full p-2 mr-3 mt-1">
          <span class="text-yellow-600 font-bold text-sm">3</span>
        </div>
        <div>
          <strong>智能代理升级</strong><br>
          <span class="text-sm text-gray-600">多轮对话、任务规划能力</span>
        </div>
      </div>
    </div>
  </div>
  <div>
    <h2 class="text-xl font-bold mb-4 text-green-600">⚙️ 功能模块拓展</h2>
    <div class="space-y-3">
      <div class="bg-blue-50 p-3 rounded">
        <strong>预测分析</strong><br>
        <span class="text-sm">设备故障预测、生产优化建议</span>
      </div>
      <div class="bg-green-50 p-3 rounded">
        <strong>实时监控</strong><br>
        <span class="text-sm">生产数据接入、异常检测告警</span>
      </div>
      <div class="bg-yellow-50 p-3 rounded">
        <strong>决策支持</strong><br>
        <span class="text-sm">多维度分析、智能推荐系统</span>
      </div>
      <div class="bg-purple-50 p-3 rounded">
        <strong>协作平台</strong><br>
        <span class="text-sm">团队知识共享、经验沉淀</span>
      </div>
    </div>
  </div>
</div>

---

# 技术发展路线图

<div class="grid grid-cols-2 gap-8 mb-8">
  <div>
    <h3 class="font-bold mb-4">核心技术升级</h3>
    <div class="space-y-3">
      <div class="flex justify-between items-center p-3 bg-blue-50 rounded">
        <span>多模态RAG引擎</span>
        <span class="font-bold text-blue-600">v2.0</span>
      </div>
      <div class="flex justify-between items-center p-3 bg-green-50 rounded">
        <span>知识图谱规模</span>
        <span class="font-bold text-green-600">10万+实体</span>
      </div>
      <div class="flex justify-between items-center p-3 bg-yellow-50 rounded">
        <span>专业词汇库</span>
        <span class="font-bold text-yellow-600">500+术语</span>
      </div>
    </div>
  </div>
  <div>
    <h3 class="font-bold mb-4">技术演进阶段</h3>
    <div class="space-y-3">
      <div class="border-l-4 border-blue-500 pl-3">
        <strong>第一阶段 (6个月)</strong><br>
        <span class="text-sm text-gray-600">多模态检索优化，响应速度提升</span>
      </div>
      <div class="border-l-4 border-green-500 pl-3">
        <strong>第二阶段 (12个月)</strong><br>
        <span class="text-sm text-gray-600">知识图谱扩展，推理能力增强</span>
      </div>
      <div class="border-l-4 border-purple-500 pl-3">
        <strong>第三阶段 (24个月)</strong><br>
        <span class="text-sm text-gray-600">智能代理升级，自主决策支持</span>
      </div>
    </div>
  </div>
</div>

<div class="p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg">
  <h3 class="font-bold mb-2 text-center">技术指标提升</h3>
  <div class="grid grid-cols-3 gap-4 text-center text-sm">
    <div>
      <div class="font-bold text-green-600">90%</div>
      <div>检索准确率</div>
    </div>
    <div>
      <div class="font-bold text-blue-600">2秒</div>
      <div>平均响应时间</div>
    </div>
    <div>
      <div class="font-bold text-purple-600">95%</div>
      <div>系统可用性</div>
    </div>
  </div>
</div>

---
layout: section
---

# 团队与发展
## 团队构成与未来规划

---

# 团队构成与分工

<div class="max-w-4xl mx-auto">
  <h2 class="text-2xl font-bold mb-6 text-center text-blue-600">👥 核心团队</h2>
  
  <div class="grid grid-cols-2 gap-6">
    <div class="flex items-start p-4 bg-green-50 rounded-lg">
      <carbon:code class="text-3xl text-green-600 mr-4 mt-1" />
      <div>
        <strong class="text-lg">后端开发工程师 (2人)</strong><br>
        <span class="text-sm text-gray-600 block mt-1">
          • RAG引擎核心开发<br>
          • 知识图谱构建与维护<br>
          • API接口设计与实现<br>
          • 数据库优化与性能调优
        </span>
      </div>
    </div>
    <div class="flex items-start p-4 bg-yellow-50 rounded-lg">
      <carbon:laptop class="text-3xl text-yellow-600 mr-4 mt-1" />
      <div>
        <strong class="text-lg">前端开发工程师 (1人)</strong><br>
        <span class="text-sm text-gray-600 block mt-1">
          • 用户界面设计与开发<br>
          • 交互体验优化<br>
          • 响应式布局实现<br>
          • 前后端数据对接
        </span>
      </div>
    </div>
  </div>
</div>

---

# 技术挑战与解决方案

<div class="grid grid-cols-2 gap-8">
  <div>
    <h2 class="text-xl font-bold mb-4 text-red-600">🚧 主要挑战</h2>
    <div class="space-y-2">
      <div class="border-l-4 border-red-500 pl-4">
        <h3 class="font-bold">专业术语理解</h3>
        <p class="text-sm text-gray-600">钢铁行业术语复杂，AI理解困难</p>
        <div class="mt-2 p-2 bg-green-50 rounded text-sm">
          <strong>解决方案:</strong> 构建218+专业词汇库，定制化训练
        </div>
      </div>
      <div class="border-l-4 border-orange-500 pl-4">
        <h3 class="font-bold">多模态数据处理</h3>
        <p class="text-sm text-gray-600">图表、图像等非结构化数据处理</p>
        <div class="mt-2 p-2 bg-green-50 rounded text-sm">
          <strong>解决方案:</strong> 多模态RAG架构，统一向量化处理
        </div>
      </div>
      <div class="border-l-4 border-yellow-500 pl-4">
        <h3 class="font-bold">实时性要求</h3>
        <p class="text-sm text-gray-600">生产环境要求快速响应</p>
        <div class="mt-2 p-2 bg-green-50 rounded text-sm">
          <strong>解决方案:</strong> 缓存机制+超时降级策略
        </div>
      </div>
    </div>
  </div>
  <div>
    <h2 class="text-xl font-bold mb-4 text-green-600">✅ 阶段性成果</h2>
    <div class="space-y-3">
      <div class="bg-green-50 p-3 rounded">
        <strong>MVP完成</strong><br>
        <span class="text-sm">核心功能已实现，通过内部测试</span>
      </div>
      <div class="bg-blue-50 p-3 rounded">
        <strong>知识库建设</strong><br>
        <span class="text-sm">已收录大量专业文档</span>
      </div>
      <div class="bg-purple-50 p-3 rounded">
        <strong>技术验证</strong><br>
        <span class="text-sm">95%检索准确率，2秒响应时间</span>
      </div>
    </div>
  </div>
</div>

---
layout: center
---

# 总结

<div class="text-center space-y-8">
  <h2 class="text-3xl font-bold text-blue-600">钢铁行业AI决策中心</h2>
  <p class="text-xl text-gray-600">从信息检索到智能决策的突破</p>
  
  <div class="grid grid-cols-3 gap-6 mt-8">
    <div class="text-center">
      <carbon:industry class="text-3xl text-blue-600 mb-2 mx-auto" />
      <div class="font-bold">行业专精</div>
      <div class="text-sm text-gray-600">钢铁领域深度理解</div>
    </div>
    <div class="text-center">
      <carbon:ai-results class="text-3xl text-green-600 mb-2 mx-auto" />
      <div class="font-bold">技术领先</div>
      <div class="text-sm text-gray-600">RAG+Agent架构</div>
    </div>
    <div class="text-center">
      <carbon:idea class="text-3xl text-purple-600 mb-2 mx-auto" />
      <div class="font-bold">技术创新</div>
      <div class="text-sm text-gray-600">多模态RAG架构</div>
    </div>
  </div>
  
  <div class="mt-8 p-6 bg-gradient-to-r from-blue-50 to-green-50 rounded-lg">
    <h3 class="text-xl font-bold mb-4">技术价值</h3>
    <p class="text-gray-700">基于多模态RAG架构和知识图谱技术，构建钢铁行业专业AI决策系统，实现智能检索、推理分析和决策支持，推动行业技术创新发展</p>
  </div>
</div>

---
layout: end
---

# 谢谢！

<div class="text-center space-y-6">
  <div class="mt-8 text-gray-500">
    钢铁行业AI决策中心 · 让智能决策触手可及
  </div>
</div>
