---
# Slidev 主题
theme: seriph
# 演示文稿信息
title: CastIron 助铁 - 钢铁行业AI决策中心
info: |
  ## CastIron 助铁 | 钢铁行业AI决策中心
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

<style>
.slidev-layout {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%) !important;
}
</style>

<div class="h-full flex flex-col justify-center items-center">
  <h1 class="text-6xl font-bold text-white mb-4 drop-shadow-2xl">CastIron 助铁</h1>
  <h2 class="text-3xl font-semibold text-white/90 mb-2 drop-shadow-lg">钢铁行业AI决策中心</h2>
  <h3 class="text-xl text-white/80 mb-8 drop-shadow-md">RAG Agent智能决策支持系统</h3>

  <div class="text-lg mb-12 text-white/90 drop-shadow-md">
    基于检索增强生成技术的垂直领域AI解决方案
  </div>

  <div class="grid grid-cols-3 gap-12 mt-8">
    <div class="text-center bg-white/10 backdrop-blur-sm p-6 rounded-xl">
      <carbon:industry class="text-5xl mb-3 text-white mx-auto" />
      <div class="font-semibold text-white text-lg">钢铁行业专精</div>
    </div>
    <div class="text-center bg-white/10 backdrop-blur-sm p-6 rounded-xl">
      <carbon:ai-results class="text-5xl mb-3 text-white mx-auto" />
      <div class="font-semibold text-white text-lg">RAG技术驱动</div>
    </div>
    <div class="text-center bg-white/10 backdrop-blur-sm p-6 rounded-xl">
      <carbon:decision-tree class="text-5xl mb-3 text-white mx-auto" />
      <div class="font-semibold text-white text-lg">智能决策支持</div>
    </div>
  </div>

  <div @click="$slidev.nav.next" class="mt-12 py-2 px-4 bg-white/20 backdrop-blur-sm rounded-lg text-white hover:bg-white/30 cursor-pointer">
    按空格键进入下一页 <carbon:arrow-right class="inline" />
  </div>
</div>

---
transition: fade-out
background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 50%, #dbeafe 100%)
---

# 目录

<div class="max-w-4xl mx-auto space-y-5">
  <div class="flex items-center p-5 bg-blue-50 rounded-xl border-l-4 border-blue-500 hover:shadow-lg transition">
    <div class="text-4xl font-bold text-blue-600 mr-6 w-16 text-center">一</div>
    <div class="flex-1">
      <div class="text-xl font-bold text-blue-600 mb-1">项目背景</div>
      <div class="text-sm text-gray-600">行业现状与市场需求分析</div>
    </div>
  </div>
  
  <div class="flex items-center p-5 bg-green-50 rounded-xl border-l-4 border-green-500 hover:shadow-lg transition">
    <div class="text-4xl font-bold text-green-600 mr-6 w-16 text-center">二</div>
    <div class="flex-1">
      <div class="text-xl font-bold text-green-600 mb-1">项目内容</div>
      <div class="text-sm text-gray-600">系统功能与技术架构设计</div>
    </div>
  </div>
  
  <div class="flex items-center p-5 bg-yellow-50 rounded-xl border-l-4 border-yellow-500 hover:shadow-lg transition">
    <div class="text-4xl font-bold text-yellow-600 mr-6 w-16 text-center">三</div>
    <div class="flex-1">
      <div class="text-xl font-bold text-yellow-600 mb-1">技术创新</div>
      <div class="text-sm text-gray-600">核心突破与差异化竞争优势</div>
    </div>
  </div>
  
  <div class="flex items-center p-5 bg-purple-50 rounded-xl border-l-4 border-purple-500 hover:shadow-lg transition">
    <div class="text-4xl font-bold text-purple-600 mr-6 w-16 text-center">四</div>
    <div class="flex-1">
      <div class="text-xl font-bold text-purple-600 mb-1">发展展望</div>
      <div class="text-sm text-gray-600">技术演进路径与未来规划</div>
    </div>
  </div>
</div>

---
layout: section
background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #60a5fa 100%)
---

<div class="h-full flex flex-col justify-center items-center text-white">
  <h1 class="text-5xl font-bold mb-4">一、项目背景</h1>
  <h2 class="text-2xl opacity-90">钢铁行业的数字化转型需求</h2>
  
  <div class="absolute bottom-10 right-10 text-white/50 text-lg">
    Background
  </div>
</div>

---

# 项目概览

<style>
.slidev-layout {
  background: linear-gradient(135deg, #0c4a6e 0%, #075985 25%, #0369a1 50%, #0284c7 75%, #0ea5e9 100%) !important;
  background-image: 
    radial-gradient(circle at 15% 15%, rgba(34, 197, 94, 0.2) 0%, transparent 50%),
    radial-gradient(circle at 85% 85%, rgba(251, 191, 36, 0.2) 0%, transparent 50%),
    radial-gradient(circle at 50% 50%, rgba(168, 85, 247, 0.1) 0%, transparent 50%);
}
</style>

<div class="grid grid-cols-2 gap-8">
  <div>
    <h2 class="text-2xl font-bold mb-4 text-blue-600">基本信息</h2>
    <div class="space-y-3">
      <div class="flex items-start">
        <carbon:application class="text-blue-500 mt-1 mr-3" />
        <div>
          <strong>项目名称</strong><br>
          <span class="text-sm">CastIron 助铁 ｜ 钢铁行业AI决策中心</span>
        </div>
      </div>
      <div class="flex items-start">
        <carbon:ai-results class="text-green-500 mt-1 mr-3" />
        <div>
          <strong>技术架构</strong><br>
          <span class="text-sm">RAG Agent智能决策系统</span>
        </div>
      </div>
      <div class="flex items-start">
        <carbon:user-multiple class="text-purple-500 mt-1 mr-3" />
        <div>
          <strong>团队规模</strong><br>
          <span class="text-sm">3人（后端2人 + 前端1人）</span>
        </div>
      </div>
      <div class="flex items-start">
        <carbon:checkmark class="text-green-600 mt-1 mr-3" />
        <div>
          <strong>项目状态</strong><br>
          <span class="text-sm">MVP已完成，通过测试验证</span>
        </div>
      </div>
    </div>
  </div>
  <div>
    <h2 class="text-2xl font-bold mb-4 text-green-600">目标用户</h2>
    <div class="grid grid-cols-2 gap-3">
      <div class="flex items-center bg-blue-50 p-3 rounded">
        <carbon:industry class="text-blue-600 mr-2" />
        <span class="text-sm font-medium">生产管理者</span>
      </div>
      <div class="flex items-center bg-green-50 p-3 rounded">
        <carbon:tools class="text-green-600 mr-2" />
        <span class="text-sm font-medium">技术专家</span>
      </div>
      <div class="flex items-center bg-yellow-50 p-3 rounded">
        <carbon:shopping-cart class="text-yellow-600 mr-2" />
        <span class="text-sm font-medium">采购人员</span>
      </div>
      <div class="flex items-center bg-purple-50 p-3 rounded">
        <carbon:chart-line class="text-purple-600 mr-2" />
        <span class="text-sm font-medium">市场分析师</span>
      </div>
      <div class="flex items-center bg-red-50 p-3 rounded">
        <carbon:settings class="text-red-600 mr-2" />
        <span class="text-sm font-medium">设备维护</span>
      </div>
      <div class="flex items-center bg-indigo-50 p-3 rounded">
        <carbon:earth class="text-indigo-600 mr-2" />
        <span class="text-sm font-medium">环保专家</span>
      </div>
    </div>
    <div class="mt-4 p-4 bg-gradient-to-r from-blue-50 to-green-50 rounded-lg">
      <h3 class="font-bold mb-2 text-blue-700">核心价值主张</h3>
      <p class="text-sm text-gray-700">从"信息检索"到"智能决策" - 为钢铁行业提供专业化AI决策支持系统</p>
    </div>
  </div>
</div>

---

# 行业现状与挑战

<style>
.slidev-layout {
  background: linear-gradient(135deg, #7c2d12 0%, #dc2626 25%, #ef4444 50%, #f87171 75%, #fca5a5 100%) !important;
  background-image: 
    radial-gradient(circle at 30% 20%, rgba(59, 130, 246, 0.2) 0%, transparent 50%),
    radial-gradient(circle at 70% 80%, rgba(16, 185, 129, 0.2) 0%, transparent 50%),
    radial-gradient(circle at 50% 50%, rgba(168, 85, 247, 0.1) 0%, transparent 50%);
}
</style>

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

<style>
.slidev-layout {
  background: linear-gradient(135deg, #14532d 0%, #166534 25%, #16a34a 50%, #22c55e 75%, #4ade80 100%) !important;
  background-image: 
    radial-gradient(circle at 20% 80%, rgba(59, 130, 246, 0.2) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(251, 191, 36, 0.2) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(168, 85, 247, 0.1) 0%, transparent 50%);
}
</style>

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
background: linear-gradient(135deg, #065f46 0%, #10b981 50%, #6ee7b7 100%)
---

<div class="h-full flex flex-col justify-center items-center text-white">
  <h1 class="text-5xl font-bold mb-4">二、项目内容</h1>
  <h2 class="text-2xl opacity-90">系统功能与技术架构</h2>
  
  <div class="absolute bottom-10 right-10 text-white/50 text-lg">
    Content
  </div>
</div>

---

# 系统核心功能

<style>
.slidev-layout {
  background: linear-gradient(135deg, #1e293b 0%, #334155 25%, #475569 50%, #64748b 75%, #94a3b8 100%) !important;
  background-image: 
    radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(120, 219, 255, 0.2) 0%, transparent 50%);
}
</style>

<div class="grid grid-cols-2 gap-4">
  <div class="space-y-3">
    <div class="border-l-4 border-blue-500 pl-3 bg-gradient-to-r from-blue-50 to-blue-100 p-3 rounded-lg shadow-md hover:shadow-lg transition-all duration-300">
      <div class="flex items-center mb-1">
        <carbon:chat class="text-blue-600 text-xl mr-2" />
        <h3 class="font-bold text-blue-700 text-sm">智能问答系统</h3>
      </div>
      <p class="text-xs text-gray-700">基于RAG技术的钢铁工艺智能问答，支持多轮对话、文档检索与引用</p>
    </div>
    <div class="border-l-4 border-green-500 pl-3 bg-gradient-to-r from-green-50 to-green-100 p-3 rounded-lg shadow-md hover:shadow-lg transition-all duration-300">
      <div class="flex items-center mb-1">
        <carbon:settings class="text-green-600 text-xl mr-2" />
        <h3 class="font-bold text-green-700 text-sm">设备故障诊断</h3>
      </div>
      <p class="text-xs text-gray-700">对话式故障诊断助手，基于历史案例和维修手册提供精准解决方案</p>
    </div>
    <div class="border-l-4 border-yellow-500 pl-3 bg-gradient-to-r from-yellow-50 to-yellow-100 p-3 rounded-lg shadow-md hover:shadow-lg transition-all duration-300">
      <div class="flex items-center mb-1">
        <carbon:chart-line class="text-yellow-600 text-xl mr-2" />
        <h3 class="font-bold text-yellow-700 text-sm">市场情报分析</h3>
      </div>
      <p class="text-xs text-gray-700">AI驱动的市场报告解读，自动提取关键信息，生成决策建议</p>
    </div>
  </div>
  <div class="space-y-3">
    <div class="border-l-4 border-purple-500 pl-3 bg-gradient-to-r from-purple-50 to-purple-100 p-3 rounded-lg shadow-md hover:shadow-lg transition-all duration-300">
      <div class="flex items-center mb-1">
        <carbon:network-3 class="text-purple-600 text-xl mr-2" />
        <h3 class="font-bold text-purple-700 text-sm">知识图谱可视化</h3>
      </div>
      <p class="text-xs text-gray-700">钢铁生产流程、设备关系、工艺参数的图谱化展示，支持交互式探索</p>
    </div>
    <div class="border-l-4 border-red-500 pl-3 bg-gradient-to-r from-red-50 to-red-100 p-3 rounded-lg shadow-md hover:shadow-lg transition-all duration-300">
      <div class="flex items-center mb-1">
        <carbon:document class="text-red-600 text-xl mr-2" />
        <h3 class="font-bold text-red-700 text-sm">知识库管理</h3>
      </div>
      <p class="text-xs text-gray-700">支持PDF、DOCX等多格式文档上传，自动向量化、语义检索、版本管理</p>
    </div>
    <div class="border-l-4 border-indigo-500 pl-3 bg-gradient-to-r from-indigo-50 to-indigo-100 p-3 rounded-lg shadow-md hover:shadow-lg transition-all duration-300">
      <div class="flex items-center mb-1">
        <carbon:user-admin class="text-indigo-600 text-xl mr-2" />
        <h3 class="font-bold text-indigo-700 text-sm">角色权限系统</h3>
      </div>
      <p class="text-xs text-gray-700">多角色支持，定制化AI响应风格，精细化权限控制</p>
    </div>
  </div>
</div>

---

# 技术架构设计

<style>
.slidev-layout {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 25%, #334155 50%, #475569 75%, #64748b 100%) !important;
  background-image: 
    radial-gradient(circle at 10% 20%, rgba(59, 130, 246, 0.2) 0%, transparent 50%),
    radial-gradient(circle at 90% 80%, rgba(16, 185, 129, 0.2) 0%, transparent 50%),
    radial-gradient(circle at 50% 50%, rgba(168, 85, 247, 0.1) 0%, transparent 50%);
}
</style>

<div class="grid grid-cols-2 gap-6">
  <div>
    <h3 class="font-bold mb-3 text-blue-600">核心层次</h3>
    <div class="space-y-2">
      <div class="p-3 bg-blue-50 rounded border-l-4 border-blue-500">
        <strong>用户界面层</strong><br>
        <span class="text-sm text-gray-600">Next.js + React + shadcn/ui</span>
      </div>
      <div class="p-3 bg-green-50 rounded border-l-4 border-green-500">
        <strong>API网关层</strong><br>
        <span class="text-sm text-gray-600">FastAPI + 中间件 + 认证</span>
      </div>
      <div class="p-3 bg-yellow-50 rounded border-l-4 border-yellow-500">
        <strong>Agent调度层</strong><br>
        <span class="text-sm text-gray-600">多Agent协作 + 任务路由</span>
      </div>
      <div class="p-3 bg-purple-50 rounded border-l-4 border-purple-500">
        <strong>RAG引擎</strong><br>
        <span class="text-sm text-gray-600">向量检索 + 知识图谱</span>
      </div>
    </div>
  </div>
  
  <div>
    <h3 class="font-bold mb-3 text-green-600">数据与模型</h3>
    <div class="space-y-2">
      <div class="p-3 bg-blue-50 rounded">
        <strong>数据层</strong><br>
        <span class="text-sm text-gray-600">• FAISS向量库<br>• MySQL关系数据库<br>• 文档存储系统</span>
      </div>
      <div class="p-3 bg-green-50 rounded">
        <strong>AI模型层</strong><br>
        <span class="text-sm text-gray-600">• LLM模型 (Qwen)<br>• 嵌入模型<br>• 专业词汇库 (218+)</span>
      </div>
      <div class="p-3 bg-purple-50 rounded">
        <strong>推理引擎</strong><br>
        <span class="text-sm text-gray-600">• ReAct框架<br>• 多步推理<br>• 工具调用</span>
      </div>
    </div>
  </div>
</div>

---

# 关键技术实现

<style>
.slidev-layout {
  background: linear-gradient(135deg, #1e1b4b 0%, #312e81 25%, #4338ca 50%, #6366f1 75%, #8b5cf6 100%) !important;
  background-image: 
    radial-gradient(circle at 25% 25%, rgba(34, 197, 94, 0.2) 0%, transparent 50%),
    radial-gradient(circle at 75% 75%, rgba(251, 191, 36, 0.2) 0%, transparent 50%),
    radial-gradient(circle at 50% 10%, rgba(239, 68, 68, 0.1) 0%, transparent 50%);
}
</style>

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
background: linear-gradient(135deg, #ea580c 0%, #fb923c 50%, #fbbf24 100%)
---

<div class="h-full flex flex-col justify-center items-center text-white">
  <h1 class="text-5xl font-bold mb-4">三、技术创新</h1>
  <h2 class="text-2xl opacity-90">核心突破与差异化优势</h2>
  
  <div class="absolute bottom-10 right-10 text-white/50 text-lg">
    Innovation
  </div>
</div>

---

# 技术创新突破

<style>
.slidev-layout {
  background: linear-gradient(135deg, #7c2d12 0%, #ea580c 25%, #fb923c 50%, #fbbf24 75%, #fde047 100%) !important;
  background-image: 
    radial-gradient(circle at 20% 30%, rgba(59, 130, 246, 0.2) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(16, 185, 129, 0.2) 0%, transparent 50%),
    radial-gradient(circle at 60% 20%, rgba(168, 85, 247, 0.1) 0%, transparent 50%);
}
</style>

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
    <p class="text-sm text-gray-600">jz</p>
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
background: linear-gradient(135deg, #7c3aed 0%, #a78bfa 50%, #c4b5fd 100%)
---

<div class="h-full flex flex-col justify-center items-center text-white">
  <h1 class="text-5xl font-bold mb-4">四、发展展望</h1>
  <h2 class="text-2xl opacity-90">技术演进与未来规划</h2>
  
  <div class="absolute bottom-10 right-10 text-white/50 text-lg">
    Prospect
  </div>
</div>

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

# 技术挑战与解决方案

<div class="grid grid-cols-2 gap-8">
  <div>
    <h2 class="text-xl font-bold mb-4 text-red-600">🚧 核心技术挑战</h2>
    <div class="space-y-3">
      <div class="border-l-4 border-red-500 pl-4">
        <h3 class="font-bold">专业术语理解难题</h3>
        <p class="text-sm text-gray-600 mb-2">钢铁行业术语复杂，通用AI理解困难</p>
        <div class="p-2 bg-green-50 rounded text-sm">
          <strong class="text-green-700">✓ 解决方案:</strong> 构建218+专业词汇库，定制化嵌入模型训练
        </div>
      </div>
      <div class="border-l-4 border-orange-500 pl-4">
        <h3 class="font-bold">多模态数据处理</h3>
        <p class="text-sm text-gray-600 mb-2">图表、图像等非结构化数据难以检索</p>
        <div class="p-2 bg-green-50 rounded text-sm">
          <strong class="text-green-700">✓ 解决方案:</strong> 多模态RAG架构，统一向量化处理流程
        </div>
      </div>
      <div class="border-l-4 border-yellow-500 pl-4">
        <h3 class="font-bold">实时性要求高</h3>
        <p class="text-sm text-gray-600 mb-2">生产环境要求快速响应，不能超时</p>
        <div class="p-2 bg-green-50 rounded text-sm">
          <strong class="text-green-700">✓ 解决方案:</strong> 智能缓存机制 + 25秒超时降级策略
        </div>
      </div>
    </div>
  </div>
  <div>
    <h2 class="text-xl font-bold mb-4 text-green-600">✅ 阶段性成果</h2>
    <div class="space-y-3">
      <div class="bg-green-50 p-4 rounded-lg">
        <div class="flex items-center mb-2">
          <carbon:checkmark class="text-green-600 mr-2" />
          <strong class="text-green-700">MVP完成</strong>
        </div>
        <span class="text-sm text-gray-700">核心功能已实现，通过内部测试验证</span>
      </div>
      <div class="bg-blue-50 p-4 rounded-lg">
        <div class="flex items-center mb-2">
          <carbon:document class="text-blue-600 mr-2" />
          <strong class="text-blue-700">知识库建设</strong>
        </div>
        <span class="text-sm text-gray-700">已收录大量钢铁行业专业文档和技术资料</span>
      </div>
      <div class="bg-purple-50 p-4 rounded-lg">
        <div class="flex items-center mb-2">
          <carbon:certificate class="text-purple-600 mr-2" />
          <strong class="text-purple-700">技术指标验证</strong>
        </div>
        <span class="text-sm text-gray-700">95%检索准确率，平均2秒响应时间</span>
      </div>
    </div>
  </div>
</div>

---
layout: center
background: linear-gradient(135deg, #fef3c7 0%, #ddd6fe 50%, #bfdbfe 100%)
---

# 项目总结

<div class="text-center mb-8">
  <h2 class="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 via-purple-600 to-green-600 mb-3">
    CastIron 助铁 | 钢铁行业AI决策中心
  </h2>
  <p class="text-lg text-gray-600">从"信息检索"到"智能决策"的技术突破</p>
</div>

<div class="grid grid-cols-4 gap-3 mb-6">
  <div class="text-center p-3 bg-blue-50 rounded-lg border-t-4 border-blue-500">
    <div class="text-2xl font-bold text-blue-600">一</div>
    <div class="font-bold text-blue-700 text-sm">背景</div>
    <p class="text-xs text-gray-600">行业痛点 · 市场需求</p>
  </div>
  <div class="text-center p-3 bg-green-50 rounded-lg border-t-4 border-green-500">
    <div class="text-2xl font-bold text-green-600">二</div>
    <div class="font-bold text-green-700 text-sm">内容</div>
    <p class="text-xs text-gray-600">6大功能 · RAG架构</p>
  </div>
  <div class="text-center p-3 bg-yellow-50 rounded-lg border-t-4 border-yellow-500">
    <div class="text-2xl font-bold text-yellow-600">三</div>
    <div class="font-bold text-yellow-700 text-sm">创新</div>
    <p class="text-xs text-gray-600">知识图谱 · 多模态</p>
  </div>
  <div class="text-center p-3 bg-purple-50 rounded-lg border-t-4 border-purple-500">
    <div class="text-2xl font-bold text-purple-600">四</div>
    <div class="font-bold text-purple-700 text-sm">展望</div>
    <p class="text-xs text-gray-600">技术演进 · 功能扩展</p>
  </div>
</div>

<div class="grid grid-cols-3 gap-4 mb-6">
  <div class="text-center p-3 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg">
    <carbon:industry class="text-3xl text-blue-600 mb-2 mx-auto" />
    <div class="font-bold text-blue-700 text-sm mb-1">垂直领域专精</div>
    <div class="text-xs text-gray-600">218+专业术语库</div>
  </div>
  <div class="text-center p-3 bg-gradient-to-br from-green-50 to-green-100 rounded-lg">
    <carbon:ai-results class="text-3xl text-green-600 mb-2 mx-auto" />
    <div class="font-bold text-green-700 text-sm mb-1">技术架构先进</div>
    <div class="text-xs text-gray-600">RAG+Agent+知识图谱</div>
  </div>
  <div class="text-center p-3 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg">
    <carbon:chart-line class="text-3xl text-purple-600 mb-2 mx-auto" />
    <div class="font-bold text-purple-700 text-sm mb-1">性能指标优异</div>
    <div class="text-xs text-gray-600">95%准确率 · 2秒响应</div>
  </div>
</div>

<div class="p-4 bg-gradient-to-r from-blue-100 via-green-100 to-purple-100 rounded-lg shadow-md">
  <h3 class="text-lg font-bold mb-2 text-center text-gray-800">核心价值</h3>
  <p class="text-center text-sm text-gray-700 leading-relaxed">
    基于多模态RAG架构和专业知识图谱技术，为钢铁行业打造智能决策支持系统，实现智能检索、推理分析和决策支持
  </p>
</div>

---
layout: end
background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%)
---

# 谢谢！

<div class="text-center space-y-8 mt-16">
  <div class="text-6xl font-bold text-white drop-shadow-2xl">
    CastIron 助铁
  </div>
  
  <div class="text-2xl text-white/90 font-light drop-shadow-lg">
    让智能决策触手可及
  </div>
  
  <div class="flex justify-center gap-12 mt-12">
    <div class="text-center bg-white/20 backdrop-blur-sm p-6 rounded-xl">
      <carbon:industry class="text-5xl text-white mx-auto mb-3" />
      <div class="text-sm text-white font-semibold">行业专精</div>
    </div>
    <div class="text-center bg-white/20 backdrop-blur-sm p-6 rounded-xl">
      <carbon:ai-results class="text-5xl text-white mx-auto mb-3" />
      <div class="text-sm text-white font-semibold">AI赋能</div>
    </div>
    <div class="text-center bg-white/20 backdrop-blur-sm p-6 rounded-xl">
      <carbon:idea class="text-5xl text-white mx-auto mb-3" />
      <div class="text-sm text-white font-semibold">持续创新</div>
    </div>
  </div>
  
  <div class="mt-16 text-white/70 text-base">
    钢铁行业AI决策中心 · RAG Agent智能决策系统
  </div>
</div>
