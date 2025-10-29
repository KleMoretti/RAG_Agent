/**
 * 钢铁生产工艺流程数据
 */

import type { ProcessNode, ProcessEdge } from "@/lib/types/workflow";

// 钢铁生产主要工艺节点
export const STEEL_PROCESS_NODES: ProcessNode[] = [
    {
        id: "raw-materials",
        name: "原料准备",
        type: "material",
        description: "铁矿石、焦炭、石灰石等原料的储存和配料",
        position: { x: 100, y: 250 },
        status: "normal",
        parameters: [
            { name: "铁矿石品位", standardValue: "60-65", unit: "%" },
            { name: "焦炭固定碳", standardValue: "≥85", unit: "%" },
        ],
    },
    {
        id: "blast-furnace",
        name: "高炉炼铁",
        type: "process",
        description: "通过高炉将铁矿石还原成生铁",
        position: { x: 350, y: 250 },
        status: "normal",
        parameters: [
            { name: "炉温", standardValue: "1500-1600", unit: "℃" },
            { name: "生铁含碳量", standardValue: "3.5-4.5", unit: "%" },
            { name: "日产量", standardValue: "5000", unit: "吨" },
        ],
    },
    {
        id: "converter",
        name: "转炉炼钢",
        type: "process",
        description: "通过转炉将生铁转化为钢水，降低碳含量",
        position: { x: 600, y: 250 },
        status: "normal",
        parameters: [
            { name: "冶炼温度", standardValue: "1600-1650", unit: "℃" },
            { name: "氧气流量", standardValue: "600-800", unit: "m³/min" },
            { name: "钢水含碳量", standardValue: "0.15-0.20", unit: "%" },
        ],
    },
    {
        id: "refining",
        name: "精炼处理",
        type: "process",
        description: "去除钢水中的杂质，调整化学成分",
        position: { x: 850, y: 150 },
        status: "normal",
        parameters: [
            { name: "处理时间", standardValue: "20-30", unit: "分钟" },
            { name: "真空度", standardValue: "≤67", unit: "Pa" },
            { name: "脱硫率", standardValue: "≥85", unit: "%" },
        ],
    },
    {
        id: "continuous-casting",
        name: "连续铸造",
        type: "process",
        description: "将钢水连续浇铸成板坯、方坯或圆坯",
        position: { x: 850, y: 350 },
        status: "normal",
        parameters: [
            { name: "拉速", standardValue: "0.8-1.2", unit: "m/min" },
            { name: "结晶器温度", standardValue: "1450-1500", unit: "℃" },
            { name: "二冷水量", standardValue: "2.5-3.5", unit: "L/kg" },
        ],
    },
    {
        id: "heating-furnace",
        name: "加热炉",
        type: "equipment",
        description: "将板坯加热到轧制温度",
        position: { x: 1100, y: 250 },
        status: "normal",
        parameters: [
            { name: "出炉温度", standardValue: "1150-1250", unit: "℃" },
            { name: "加热时间", standardValue: "120-180", unit: "分钟" },
        ],
    },
    {
        id: "hot-rolling",
        name: "热轧",
        type: "process",
        description: "在高温下将板坯轧制成钢板",
        position: { x: 1350, y: 250 },
        status: "normal",
        parameters: [
            { name: "轧制温度", standardValue: "850-950", unit: "℃" },
            { name: "轧制力", standardValue: "30000-50000", unit: "kN" },
            { name: "厚度", standardValue: "2.0-20.0", unit: "mm" },
        ],
    },
    {
        id: "cold-rolling",
        name: "冷轧",
        type: "process",
        description: "在常温下轧制，获得更薄更光滑的钢板",
        position: { x: 1600, y: 150 },
        status: "normal",
        parameters: [
            { name: "轧制速度", standardValue: "400-800", unit: "m/min" },
            { name: "轧制力", standardValue: "15000-25000", unit: "kN" },
            { name: "厚度", standardValue: "0.3-3.0", unit: "mm" },
        ],
    },
    {
        id: "annealing",
        name: "退火处理",
        type: "process",
        description: "热处理以改善钢材的机械性能",
        position: { x: 1600, y: 350 },
        status: "normal",
        parameters: [
            { name: "退火温度", standardValue: "650-750", unit: "℃" },
            { name: "保温时间", standardValue: "4-8", unit: "小时" },
        ],
    },
    {
        id: "quality-inspection",
        name: "质量检验",
        type: "inspection",
        description: "对成品进行机械性能和表面质量检验",
        position: { x: 1850, y: 250 },
        status: "normal",
        parameters: [
            { name: "抗拉强度", standardValue: "≥370", unit: "MPa" },
            { name: "屈服强度", standardValue: "≥235", unit: "MPa" },
            { name: "延伸率", standardValue: "≥26", unit: "%" },
        ],
    },
    {
        id: "finished-product",
        name: "成品入库",
        type: "material",
        description: "合格产品包装入库",
        position: { x: 2100, y: 250 },
        status: "normal",
        parameters: [],
    },
];

// 工艺流程连线
export const STEEL_PROCESS_EDGES: ProcessEdge[] = [
    { id: "e1", source: "raw-materials", target: "blast-furnace", label: "铁矿石", type: "material" },
    { id: "e2", source: "blast-furnace", target: "converter", label: "生铁", type: "material" },
    { id: "e3", source: "converter", target: "refining", label: "钢水", type: "material" },
    { id: "e4", source: "converter", target: "continuous-casting", label: "钢水", type: "material" },
    { id: "e5", source: "refining", target: "continuous-casting", label: "精炼后钢水", type: "material" },
    { id: "e6", source: "continuous-casting", target: "heating-furnace", label: "板坯", type: "material" },
    { id: "e7", source: "heating-furnace", target: "hot-rolling", label: "加热板坯", type: "material" },
    { id: "e8", source: "hot-rolling", target: "cold-rolling", label: "热轧钢板", type: "material" },
    { id: "e9", source: "hot-rolling", target: "annealing", label: "热轧钢板", type: "material" },
    { id: "e10", source: "cold-rolling", target: "quality-inspection", label: "冷轧钢板", type: "material" },
    { id: "e11", source: "annealing", target: "quality-inspection", label: "退火钢板", type: "material" },
    { id: "e12", source: "quality-inspection", target: "finished-product", label: "合格产品", type: "material" },
];

// 工艺节点颜色映射
export const NODE_COLORS = {
    process: {
        bg: "bg-blue-50 dark:bg-blue-950",
        border: "border-blue-500",
        text: "text-blue-700 dark:text-blue-300",
    },
    equipment: {
        bg: "bg-purple-50 dark:bg-purple-950",
        border: "border-purple-500",
        text: "text-purple-700 dark:text-purple-300",
    },
    inspection: {
        bg: "bg-green-50 dark:bg-green-950",
        border: "border-green-500",
        text: "text-green-700 dark:text-green-300",
    },
    material: {
        bg: "bg-amber-50 dark:bg-amber-950",
        border: "border-amber-500",
        text: "text-amber-700 dark:text-amber-300",
    },
};

// 节点状态颜色
export const STATUS_COLORS = {
    normal: "border-green-500 bg-green-50 dark:bg-green-950",
    warning: "border-yellow-500 bg-yellow-50 dark:bg-yellow-950 animate-pulse",
    error: "border-red-500 bg-red-50 dark:bg-red-950 animate-pulse",
    optimizing: "border-blue-500 bg-blue-50 dark:bg-blue-950",
};

