"use client";

import * as React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

interface AgentTooltipProps {
  agent: {
    id: string;
    name: string;
    icon: LucideIcon;
    color: string;
    description: string;
  };
  isVisible: boolean;
  position: { x: number; y: number };
  className?: string;
}

// 扩展的 Agent 功能描述
const agentDetails: Record<string, {
  fullDescription: string;
  capabilities: string[];
  useCases: string[];
  tags: string[];
}> = {
  general: {
    fullDescription: "全能型 AI 助手，具备广泛的知识基础和问题解决能力，可以协助处理各类日常工作和技术咨询。",
    capabilities: [
      "多领域知识问答",
      "文档分析与总结", 
      "数据解读与建议",
      "工作流程优化"
    ],
    useCases: [
      "日常工作咨询",
      "技术问题解答",
      "文档处理",
      "决策支持"
    ],
    tags: ["通用", "多功能", "智能问答"]
  },
  process: {
    fullDescription: "专业的钢铁生产工艺专家，深度了解炼钢、轧钢等各个生产环节，提供工艺优化和技术改进建议。",
    capabilities: [
      "工艺流程分析",
      "生产参数优化",
      "技术改进建议",
      "工艺故障诊断"
    ],
    useCases: [
      "生产工艺咨询",
      "参数调优",
      "工艺改进",
      "技术升级"
    ],
    tags: ["工艺", "生产", "技术优化"]
  },
  equipment: {
    fullDescription: "设备维护和故障诊断专家，具备丰富的设备管理经验，能够快速定位问题并提供解决方案。",
    capabilities: [
      "故障快速诊断",
      "预防性维护建议",
      "设备性能分析",
      "维修方案制定"
    ],
    useCases: [
      "设备故障排查",
      "维护计划制定",
      "性能监控",
      "备件管理"
    ],
    tags: ["设备", "维护", "故障诊断"]
  },
  market: {
    fullDescription: "钢铁市场分析专家，实时跟踪市场动态，提供价格趋势分析和投资决策支持。",
    capabilities: [
      "市场趋势分析",
      "价格预测建模",
      "供需关系评估",
      "投资风险分析"
    ],
    useCases: [
      "价格走势分析",
      "采购决策支持",
      "市场调研",
      "投资规划"
    ],
    tags: ["市场", "分析", "价格预测"]
  },
  quality: {
    fullDescription: "质量控制专家，专注于产品质量管理和改进，确保产品符合行业标准和客户要求。",
    capabilities: [
      "质量标准制定",
      "检测流程优化",
      "质量问题分析",
      "改进措施建议"
    ],
    useCases: [
      "质量体系建设",
      "检测方案设计",
      "质量问题解决",
      "标准化管理"
    ],
    tags: ["质量", "标准", "检测"]
  },
  energy: {
    fullDescription: "节能减排专家，专注于能源效率优化和环保技术应用，帮助企业降低能耗和运营成本。",
    capabilities: [
      "能耗分析诊断",
      "节能方案设计",
      "环保技术咨询",
      "成本效益评估"
    ],
    useCases: [
      "能耗优化",
      "节能改造",
      "环保合规",
      "成本控制"
    ],
    tags: ["节能", "环保", "成本优化"]
  }
};

export function AgentTooltip({ agent, isVisible, position, className }: AgentTooltipProps) {
  const details = agentDetails[agent.id];
  const Icon = agent.icon;

  if (!details) return null;

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 8, x: -8 }}
          animate={{ opacity: 1, scale: 1, y: 0, x: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 8, x: -8 }}
          transition={{ 
            duration: 0.05, 
            ease: [0.25, 0.46, 0.45, 0.94], // 快速非线性缓动函数
            opacity: { duration: 0.05 },
            scale: { duration: 0.05 },
          }}
          className={cn(
            "fixed z-50 pointer-events-auto",
            className
          )}
          style={{
            left: position.x,
            top: position.y,
          }}
          onMouseEnter={() => {
            // 当鼠标进入悬浮窗口时，保持显示状态
          }}
        >
          <Card className="w-80 shadow-xl border border-border bg-card backdrop-blur-md ring-1 ring-border/20">
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-3">
                <div className={cn(
                  "p-2 rounded-lg",
                  // 将 text-color 转换为对应的 bg-color
                  agent.color.replace('text-', 'bg-').replace('-600', '-100')
                )}>
                  <Icon className={cn("size-5", agent.color)} />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-card-foreground">{agent.name}</h3>
                  <p className="text-sm text-muted-foreground font-normal">
                    {agent.description}
                  </p>
                </div>
              </CardTitle>
            </CardHeader>
            
            <CardContent className="space-y-4">
              {/* 详细描述 */}
              <div>
                <p className="text-sm text-card-foreground leading-relaxed">
                  {details.fullDescription}
                </p>
              </div>

              <Separator />

              {/* 核心能力 */}
              <div>
                <h4 className="text-sm font-medium mb-2 text-card-foreground">核心能力</h4>
                <div className="grid grid-cols-1 gap-1">
                  {details.capabilities.map((capability, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-primary flex-shrink-0" />
                      <span className="text-xs text-muted-foreground">{capability}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* 应用场景 */}
              <div>
                <h4 className="text-sm font-medium mb-2 text-card-foreground">应用场景</h4>
                <div className="flex flex-wrap gap-1">
                  {details.useCases.map((useCase, index) => (
                    <Badge 
                      key={index} 
                      variant="secondary" 
                      className="text-xs px-2 py-1"
                    >
                      {useCase}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* 标签 */}
              <div>
                <div className="flex flex-wrap gap-1">
                  {details.tags.map((tag, index) => (
                    <Badge 
                      key={index} 
                      className={cn(
                        "text-xs px-2 py-1",
                        // 背景色：将 text-color-600 转换为 bg-color-100
                        agent.color.replace('text-', 'bg-').replace('-600', '-100'),
                        // 文字色：将 text-color-600 转换为 text-color-700
                        agent.color.replace('-600', '-700')
                      )}
                    >
                      {tag}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </AnimatePresence>
  );
}