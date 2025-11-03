/**
 * 钢铁生产工艺流程模板数据
 * 基于行业标准流程定义，支持多种工艺路线
 */

import type { ProcessNode, ProcessEdge } from "@/lib/types/workflow";

/**
 * 工艺流程模板接口
 */
export interface ProcessTemplate {
    id: string;
    name: string;
    description: string;
    applicability: string;
    co2Range: { min: number; max: number }; // 吨钢碳排放范围
    nodes: ProcessNode[];
    edges: ProcessEdge[];
}

/**
 * 将JSON节点转换为可视化流程节点
 */
function convertToFlowNodes(jsonNodes: any[], templateId: string): ProcessNode[] {
    const nodeTypes: Record<string, ProcessNode["type"]> = {
        raw_prep: "material",
        coking: "process",
        agglomeration: "process",
        smelting: "process",
        refining: "process",
        secondary_refine: "process",
        casting: "process",
        rolling: "process",
        equipment: "equipment",
        vacuum_refine: "process",
        alloy_addition: "process",
        reheat: "process",
        casting_rolling: "process",
        reduction: "process",
        reduction_smelt: "process",
        downstream: "process",
    };

    return jsonNodes.map((node, index) => {
        const parameters = [];
        
        // 提取关键参数
        if (node.temp_range_C) {
            if (Array.isArray(node.temp_range_C)) {
                parameters.push({
                    name: "温度范围",
                    standardValue: `${node.temp_range_C[0]}-${node.temp_range_C[1]}`,
                    unit: "℃",
                });
            } else if (typeof node.temp_range_C === "object") {
                Object.entries(node.temp_range_C).forEach(([key, value]) => {
                    if (Array.isArray(value)) {
                        parameters.push({
                            name: key,
                            standardValue: `${value[0]}-${value[1]}`,
                            unit: "℃",
                        });
                    }
                });
            }
        }

        if (node.residence_time) {
            parameters.push({
                name: "停留时间",
                standardValue: node.residence_time,
                unit: "",
            });
        }

        if (node.key_parameters) {
            Object.entries(node.key_parameters).forEach(([key, value]) => {
                if (typeof value === "string" || typeof value === "number") {
                    parameters.push({
                        name: key.replace(/_/g, " "),
                        standardValue: value,
                        unit: "",
                    });
                }
            });
        }

        // 能耗信息
        if (node.energy_estimate) {
            Object.entries(node.energy_estimate).forEach(([key, value]) => {
                parameters.push({
                    name: `能耗-${key}`,
                    standardValue: value as string | number,
                    unit: "",
                });
            });
        }

        if (node.material_loss_pct) {
            parameters.push({
                name: "物料损失",
                standardValue: node.material_loss_pct,
                unit: "%",
            });
        }

        return {
            id: `${templateId}-${node.id}`,
            name: node.name,
            type: nodeTypes[node.type] || "process",
            description: node.inputs?.map((i: any) => i.material || i.gas).join(", ") || "",
            position: {
                x: 200 + index * 250,
                y: 250,
            },
            status: "normal" as const,
            parameters,
        };
    });
}

/**
 * 生成流程连线
 */
function generateEdges(nodes: ProcessNode[]): ProcessEdge[] {
    const edges: ProcessEdge[] = [];
    
    for (let i = 0; i < nodes.length - 1; i++) {
        edges.push({
            id: `edge-${i}`,
            source: nodes[i].id,
            target: nodes[i + 1].id,
            label: "物料流",
            type: "material",
        });
    }
    
    return edges;
}

/**
 * 1. 高炉—转炉（BF→BOF）长流程
 */
export const BF_BOF_TEMPLATE: ProcessTemplate = {
    id: "bf-bof",
    name: "高炉—转炉（BF→BOF）长流程",
    description: "传统高炉-转炉一体化流程，适合大规模连续生产",
    applicability: "大型综合钢厂；原料为铁矿石、焦炭；适合百万吨级/年产线；能耗与碳排放较高",
    co2Range: { min: 1.8, max: 2.5 },
    nodes: [
        {
            id: "bf-bof-raw_prep",
            name: "原料准备",
            type: "material",
            description: "铁矿石、炼焦煤、石灰石破碎筛分配料",
            position: { x: 100, y: 250 },
            status: "normal",
            parameters: [
                { name: "铁品位", standardValue: "50-65", unit: "%" },
                { name: "磷含量", standardValue: "≤0.05", unit: "%" },
                { name: "粒度", standardValue: "0-50", unit: "mm" },
                { name: "电耗", standardValue: "10", unit: "kWh/t" },
                { name: "物料损失", standardValue: "2", unit: "%" },
            ],
        },
        {
            id: "bf-bof-coking",
            name: "炼焦（焦炉）",
            type: "process",
            description: "炼焦煤在焦炉中干馏制焦炭",
            position: { x: 350, y: 250 },
            status: "normal",
            parameters: [
                { name: "温度", standardValue: "900-1100", unit: "℃" },
                { name: "炉龄", standardValue: "18-36", unit: "小时" },
                { name: "焦炭收率", standardValue: "60-70", unit: "%" },
                { name: "CRI", standardValue: "<30", unit: "" },
                { name: "燃料耗", standardValue: "2.0", unit: "GJ/t" },
                { name: "物料损失", standardValue: "35", unit: "%" },
            ],
        },
        {
            id: "bf-bof-sintering",
            name: "烧结",
            type: "process",
            description: "铁矿粉、焦粉、石灰石烧结成块矿",
            position: { x: 600, y: 250 },
            status: "normal",
            parameters: [
                { name: "温度", standardValue: "1200-1400", unit: "℃" },
                { name: "单圈时间", standardValue: "60-90", unit: "分钟" },
                { name: "Fe含量", standardValue: "55-60", unit: "%" },
                { name: "碱度", standardValue: "1.8-2.8", unit: "CaO/SiO2" },
                { name: "燃料耗", standardValue: "0.3", unit: "GJ/t" },
                { name: "物料损失", standardValue: "6", unit: "%" },
            ],
        },
        {
            id: "bf-bof-blast_furnace",
            name: "高炉炼铁",
            type: "process",
            description: "烧结矿、焦炭在高炉中还原冶炼成铁水",
            position: { x: 850, y: 250 },
            status: "normal",
            parameters: [
                { name: "温度", standardValue: "1500-2000", unit: "℃" },
                { name: "出铁周期", standardValue: "2-4", unit: "小时" },
                { name: "热风温度", standardValue: "1000", unit: "℃" },
                { name: "焦比", standardValue: "300", unit: "kg/t铁" },
                { name: "煤粉", standardValue: "125", unit: "kg/t铁" },
                { name: "燃料耗", standardValue: "12", unit: "GJ/t" },
                { name: "物料损失", standardValue: "22", unit: "%" },
            ],
        },
        {
            id: "bf-bof-converter",
            name: "转炉炼钢（BOF）",
            type: "process",
            description: "铁水+废钢在转炉中吹氧脱碳炼钢",
            position: { x: 1100, y: 250 },
            status: "normal",
            parameters: [
                { name: "温度", standardValue: "1550-1700", unit: "℃" },
                { name: "炉龄", standardValue: "20-40", unit: "分钟" },
                { name: "终碳", standardValue: "0.02-0.2", unit: "%" },
                { name: "氧气流量", standardValue: "500", unit: "m³/t" },
                { name: "废钢比", standardValue: "10", unit: "%" },
                { name: "氧耗", standardValue: "500", unit: "Nm³/t" },
                { name: "物料损失", standardValue: "5", unit: "%" },
            ],
        },
        {
            id: "bf-bof-secondary_refine",
            name: "炉外精炼（LF/RH）",
            type: "process",
            description: "钢水脱硫脱氧、合金化、真空处理",
            position: { x: 1350, y: 250 },
            status: "normal",
            parameters: [
                { name: "温度", standardValue: "1550-1650", unit: "℃" },
                { name: "时间", standardValue: "20-60", unit: "分钟" },
                { name: "硫含量", standardValue: "<50", unit: "ppm" },
                { name: "氧含量", standardValue: "≤20", unit: "ppm" },
                { name: "电耗", standardValue: "30", unit: "kWh/t" },
                { name: "物料损失", standardValue: "1", unit: "%" },
            ],
        },
        {
            id: "bf-bof-continuous_casting",
            name: "连铸",
            type: "process",
            description: "钢水连续浇铸成板坯/方坯",
            position: { x: 1600, y: 250 },
            status: "normal",
            parameters: [
                { name: "温度", standardValue: "1400-1600", unit: "℃" },
                { name: "铸速", standardValue: "0.6-1.5", unit: "m/min" },
                { name: "冷却水耗", standardValue: "5", unit: "kWh/t" },
                { name: "物料损失", standardValue: "0.5", unit: "%" },
            ],
        },
        {
            id: "bf-bof-rolling",
            name: "轧制与热处理",
            type: "process",
            description: "板坯加热→粗轧→精轧→退火/淬火",
            position: { x: 1850, y: 250 },
            status: "normal",
            parameters: [
                { name: "加热温度", standardValue: "1100-1250", unit: "℃" },
                { name: "终轧温度", standardValue: "850-950", unit: "℃" },
                { name: "氧化铁皮损失", standardValue: "1-3", unit: "%" },
                { name: "厚度公差", standardValue: "±0.1-1", unit: "mm" },
                { name: "燃料耗", standardValue: "3.5", unit: "GJ/t" },
                { name: "电耗", standardValue: "30", unit: "kWh/t" },
                { name: "物料损失", standardValue: "2", unit: "%" },
            ],
        },
    ],
    edges: [
        { id: "e1", source: "bf-bof-raw_prep", target: "bf-bof-coking", label: "炼焦煤", type: "material" },
        { id: "e2", source: "bf-bof-raw_prep", target: "bf-bof-sintering", label: "铁矿粉", type: "material" },
        { id: "e3", source: "bf-bof-coking", target: "bf-bof-sintering", label: "焦粉", type: "material" },
        { id: "e4", source: "bf-bof-sintering", target: "bf-bof-blast_furnace", label: "烧结矿", type: "material" },
        { id: "e5", source: "bf-bof-coking", target: "bf-bof-blast_furnace", label: "焦炭", type: "material" },
        { id: "e6", source: "bf-bof-blast_furnace", target: "bf-bof-converter", label: "铁水", type: "material" },
        { id: "e7", source: "bf-bof-converter", target: "bf-bof-secondary_refine", label: "钢水", type: "material" },
        { id: "e8", source: "bf-bof-secondary_refine", target: "bf-bof-continuous_casting", label: "精炼钢水", type: "material" },
        { id: "e9", source: "bf-bof-continuous_casting", target: "bf-bof-rolling", label: "板坯", type: "material" },
    ],
};

/**
 * 2. 废钢电炉（EAF）短流程
 */
export const EAF_TEMPLATE: ProcessTemplate = {
    id: "eaf",
    name: "废钢电炉（EAF）短流程",
    description: "以废钢为主的电弧炉炼钢流程，适合弹性生产与较低排放",
    applicability: "中小型钢厂、mini-mill；适合废钢丰富区域；低对焦炭依赖",
    co2Range: { min: 0.3, max: 0.9 },
    nodes: [
        {
            id: "eaf-scrap_prep",
            name: "废钢回收与准备",
            type: "material",
            description: "废钢剪切、配级、除杂",
            position: { x: 100, y: 250 },
            status: "normal",
            parameters: [
                { name: "粒度", standardValue: "≤300", unit: "mm" },
                { name: "铜含量限制", standardValue: "视钢种", unit: "" },
                { name: "准备时间", standardValue: "30-120", unit: "分钟" },
                { name: "电耗", standardValue: "5", unit: "kWh/t" },
                { name: "物料损失", standardValue: "3", unit: "%" },
            ],
        },
        {
            id: "eaf-eaf_melt",
            name: "电弧炉熔炼（EAF）",
            type: "process",
            description: "废钢电弧熔化+吹氧脱碳",
            position: { x: 400, y: 250 },
            status: "normal",
            parameters: [
                { name: "温度", standardValue: "1550-1650", unit: "℃" },
                { name: "炉龄", standardValue: "30-90", unit: "分钟" },
                { name: "出钢温度", standardValue: "1600", unit: "℃" },
                { name: "电耗", standardValue: "400-600", unit: "kWh/t" },
                { name: "物料损失", standardValue: "10", unit: "%" },
            ],
        },
        {
            id: "eaf-secondary_refine",
            name: "炉外精炼（LF/VD）",
            type: "process",
            description: "钢水脱硫脱氧、合金化、真空处理",
            position: { x: 700, y: 250 },
            status: "normal",
            parameters: [
                { name: "温度", standardValue: "1500-1650", unit: "℃" },
                { name: "时间", standardValue: "20-60", unit: "分钟" },
                { name: "硫含量", standardValue: "<50", unit: "ppm" },
                { name: "氧含量", standardValue: "<20", unit: "ppm" },
                { name: "电耗", standardValue: "20", unit: "kWh/t" },
                { name: "物料损失", standardValue: "1", unit: "%" },
            ],
        },
        {
            id: "eaf-casting_rolling",
            name: "连铸→轧制→热/冷处理",
            type: "process",
            description: "精钢水→板坯→热/冷轧→退火",
            position: { x: 1000, y: 250 },
            status: "normal",
            parameters: [
                { name: "铸造温度", standardValue: "1400-1560", unit: "℃" },
                { name: "铸速", standardValue: "0.6-1.2", unit: "m/min" },
                { name: "热轧加热", standardValue: "1100-1250", unit: "℃" },
                { name: "电耗", standardValue: "30", unit: "kWh/t" },
                { name: "燃料耗", standardValue: "2.5", unit: "GJ/t" },
                { name: "物料损失", standardValue: "2", unit: "%" },
            ],
        },
    ],
    edges: [
        { id: "e1", source: "eaf-scrap_prep", target: "eaf-eaf_melt", label: "废钢", type: "material" },
        { id: "e2", source: "eaf-eaf_melt", target: "eaf-secondary_refine", label: "粗钢水", type: "material" },
        { id: "e3", source: "eaf-secondary_refine", target: "eaf-casting_rolling", label: "精钢水", type: "material" },
    ],
};

/**
 * 3. 直接还原（DRI）→ 电炉（DRI+EAF）
 */
export const DRI_EAF_TEMPLATE: ProcessTemplate = {
    id: "dri-eaf",
    name: "直接还原（DRI）→ 电炉",
    description: "气基直接还原制DRI或HBI，结合EAF炼钢，适合低碳路线",
    applicability: "天然气/氢气资源充足或追求低碳产品的场景；合金与特种钢可控性好",
    co2Range: { min: 0.4, max: 1.0 },
    nodes: [
        {
            id: "dri-pellet",
            name: "球团/精矿制备",
            type: "material",
            description: "精矿粉制备高品位球团",
            position: { x: 100, y: 250 },
            status: "normal",
            parameters: [
                { name: "温度", standardValue: "1200-1350", unit: "℃" },
                { name: "Fe含量", standardValue: "≥65", unit: "%" },
                { name: "落下强度", standardValue: "高", unit: "" },
                { name: "燃料耗", standardValue: "0.4", unit: "GJ/t" },
                { name: "电耗", standardValue: "20", unit: "kWh/t" },
                { name: "物料损失", standardValue: "8", unit: "%" },
            ],
        },
        {
            id: "dri-reduction",
            name: "DRI直接还原",
            type: "process",
            description: "球团在竖炉/旋转炉中气基还原",
            position: { x: 400, y: 250 },
            status: "normal",
            parameters: [
                { name: "温度", standardValue: "800-1000", unit: "℃" },
                { name: "时间", standardValue: "1-2", unit: "小时" },
                { name: "金属化率", standardValue: "92-95", unit: "%" },
                { name: "气耗", standardValue: "1000", unit: "m³/t" },
                { name: "电耗", standardValue: "40", unit: "kWh/t" },
                { name: "物料损失", standardValue: "5", unit: "%" },
            ],
        },
        {
            id: "dri-eaf",
            name: "电弧炉熔化（含DRI）",
            type: "process",
            description: "DRI/HBI+废钢电弧熔化",
            position: { x: 700, y: 250 },
            status: "normal",
            parameters: [
                { name: "温度", standardValue: "1550-1650", unit: "℃" },
                { name: "时间", standardValue: "30-90", unit: "分钟" },
                { name: "DRI配比", standardValue: "0-100", unit: "%" },
                { name: "电耗", standardValue: "450-650", unit: "kWh/t" },
                { name: "物料损失", standardValue: "8", unit: "%" },
            ],
        },
        {
            id: "dri-downstream",
            name: "精炼→连铸→轧制",
            type: "process",
            description: "精炼钢水→板坯→成品钢材",
            position: { x: 1000, y: 250 },
            status: "normal",
            parameters: [
                { name: "精炼温度", standardValue: "1500-1650", unit: "℃" },
                { name: "铸造温度", standardValue: "1400-1560", unit: "℃" },
                { name: "氧含量", standardValue: "<20", unit: "ppm" },
                { name: "电耗", standardValue: "40", unit: "kWh/t" },
                { name: "燃料耗", standardValue: "1.5", unit: "GJ/t" },
                { name: "物料损失", standardValue: "2", unit: "%" },
            ],
        },
    ],
    edges: [
        { id: "e1", source: "dri-pellet", target: "dri-reduction", label: "球团", type: "material" },
        { id: "e2", source: "dri-reduction", target: "dri-eaf", label: "DRI/HBI", type: "material" },
        { id: "e3", source: "dri-eaf", target: "dri-downstream", label: "钢水", type: "material" },
    ],
};

/**
 * 4. COREX / FINEX（熔融还原）
 */
export const COREX_TEMPLATE: ProcessTemplate = {
    id: "corex-finex",
    name: "COREX / FINEX 熔融还原",
    description: "熔融还原-熔融处理流程，减少焦炭依赖，可产铁水或热金属",
    applicability: "希望替代/补充高炉产能、减少焦炭依赖的中大型厂",
    co2Range: { min: 1.2, max: 2.0 },
    nodes: [
        {
            id: "corex-feed",
            name: "块矿/球团制备",
            type: "material",
            description: "块矿/球团破碎筛分混合",
            position: { x: 100, y: 250 },
            status: "normal",
            parameters: [
                { name: "Fe品位", standardValue: "≥60", unit: "%" },
                { name: "电耗", standardValue: "30", unit: "kWh/t" },
                { name: "物料损失", standardValue: "5", unit: "%" },
            ],
        },
        {
            id: "corex-reduction",
            name: "熔融还原反应器",
            type: "process",
            description: "COREX/FINEX模块熔融还原",
            position: { x: 400, y: 250 },
            status: "normal",
            parameters: [
                { name: "温度", standardValue: "1400-1700", unit: "℃" },
                { name: "产品", standardValue: "液态铁/热金属", unit: "" },
                { name: "副产煤气", standardValue: "高（可回收）", unit: "m³/t" },
                { name: "燃料耗", standardValue: "8", unit: "GJ/t" },
                { name: "电耗", standardValue: "60", unit: "kWh/t" },
                { name: "物料损失", standardValue: "10", unit: "%" },
            ],
        },
        {
            id: "corex-downstream",
            name: "炼钢→精炼→连铸→轧制",
            type: "process",
            description: "热金属→转炉/EAF→精炼→板坯→成品",
            position: { x: 700, y: 250 },
            status: "normal",
            parameters: [
                { name: "温度", standardValue: "1500-1700", unit: "℃" },
                { name: "电耗", standardValue: "40", unit: "kWh/t" },
                { name: "物料损失", standardValue: "3", unit: "%" },
            ],
        },
    ],
    edges: [
        { id: "e1", source: "corex-feed", target: "corex-reduction", label: "矿料", type: "material" },
        { id: "e2", source: "corex-reduction", target: "corex-downstream", label: "液态铁", type: "material" },
    ],
};

/**
 * 5. 真空/特殊精炼路线（高端钢种）
 */
export const VACUUM_SPECIAL_TEMPLATE: ProcessTemplate = {
    id: "vacuum-special",
    name: "真空/特殊精炼路线",
    description: "用于高端合金、不锈钢或特殊规格钢的精密炉外处理路线",
    applicability: "高端市场/特种钢厂；产能相对小，要求成分与夹杂物严格控制",
    co2Range: { min: 0.5, max: 2.5 },
    nodes: [
        {
            id: "vacuum-melt",
            name: "初次熔炼（BF/BOF/EAF）",
            type: "process",
            description: "初级钢水熔炼",
            position: { x: 100, y: 250 },
            status: "normal",
            parameters: [
                { name: "温度", standardValue: "1500-1650", unit: "℃" },
                { name: "电耗", standardValue: "20", unit: "kWh/t" },
                { name: "物料损失", standardValue: "2", unit: "%" },
            ],
        },
        {
            id: "vacuum-degassing",
            name: "真空脱气（VD/VOD）",
            type: "process",
            description: "真空炉脱气、降低O/H/N含量",
            position: { x: 400, y: 250 },
            status: "normal",
            parameters: [
                { name: "温度", standardValue: "1400-1650", unit: "℃" },
                { name: "时间", standardValue: "15-60", unit: "分钟" },
                { name: "氧含量", standardValue: "<10", unit: "ppm" },
                { name: "氢含量", standardValue: "<1-2", unit: "ppm" },
                { name: "氮含量", standardValue: "≤20", unit: "ppm" },
                { name: "电耗", standardValue: "30", unit: "kWh/t" },
                { name: "真空泵耗", standardValue: "5", unit: "kWhr/t" },
                { name: "物料损失", standardValue: "0.5", unit: "%" },
            ],
        },
        {
            id: "vacuum-alloy",
            name: "精确合金添加",
            type: "process",
            description: "微量元素精密控制（V, Nb, Ti, Al等）",
            position: { x: 700, y: 250 },
            status: "normal",
            parameters: [
                { name: "温度", standardValue: "1400-1600", unit: "℃" },
                { name: "时间", standardValue: "几分钟-几十分钟", unit: "" },
                { name: "合金精度", standardValue: "±10-50", unit: "ppm" },
                { name: "电耗", standardValue: "5", unit: "kWh/t" },
                { name: "物料损失", standardValue: "0.2", unit: "%" },
            ],
        },
    ],
    edges: [
        { id: "e1", source: "vacuum-melt", target: "vacuum-degassing", label: "粗钢水", type: "material" },
        { id: "e2", source: "vacuum-degassing", target: "vacuum-alloy", label: "脱气钢水", type: "material" },
    ],
};

/**
 * 6. 连铸—热轧一体线（CC–HSM）
 */
export const CC_HSM_TEMPLATE: ProcessTemplate = {
    id: "cc-hsm",
    name: "连铸—热轧一体线（CC–HSM）",
    description: "连铸直轧/连退火一体化，提高板带产线效率与质量",
    applicability: "板带材大产线，追求高产能与高表面质量",
    co2Range: { min: 0.4, max: 1.2 },
    nodes: [
        {
            id: "cc-hsm-cast",
            name: "连铸（板坯）",
            type: "process",
            description: "精炼钢水连续浇铸成热连铸板坯",
            position: { x: 100, y: 250 },
            status: "normal",
            parameters: [
                { name: "温度", standardValue: "1400-1600", unit: "℃" },
                { name: "铸速", standardValue: "0.7-1.2", unit: "m/min" },
                { name: "表面缺陷率", standardValue: "低", unit: "" },
                { name: "冷却水耗", standardValue: "5", unit: "kWh/t" },
                { name: "物料损失", standardValue: "0.5", unit: "%" },
            ],
        },
        {
            id: "cc-hsm-reheat",
            name: "再加热炉",
            type: "equipment",
            description: "板坯再加热至再结晶温度",
            position: { x: 400, y: 250 },
            status: "normal",
            parameters: [
                { name: "温度", standardValue: "1100-1250", unit: "℃" },
                { name: "加热温度", standardValue: "1150", unit: "℃" },
                { name: "温度均匀性", standardValue: "±10", unit: "℃" },
                { name: "燃料耗", standardValue: "3.5", unit: "GJ/t" },
                { name: "物料损失", standardValue: "1", unit: "%" },
            ],
        },
        {
            id: "cc-hsm-rolling",
            name: "热轧机组（粗轧→精轧）",
            type: "process",
            description: "再热板坯→粗轧→中轧→精轧→在线热处理",
            position: { x: 700, y: 250 },
            status: "normal",
            parameters: [
                { name: "粗轧温度", standardValue: "1000-1200", unit: "℃" },
                { name: "精轧温度", standardValue: "800-1000", unit: "℃" },
                { name: "终厚度", standardValue: "按规格", unit: "mm" },
                { name: "卷取温度", standardValue: "控制组织", unit: "℃" },
                { name: "电耗", standardValue: "40", unit: "kWh/t" },
                { name: "物料损失", standardValue: "1.5", unit: "%" },
            ],
        },
    ],
    edges: [
        { id: "e1", source: "cc-hsm-cast", target: "cc-hsm-reheat", label: "热连铸板坯", type: "material" },
        { id: "e2", source: "cc-hsm-reheat", target: "cc-hsm-rolling", label: "再热板坯", type: "material" },
    ],
};

/**
 * 所有工艺流程模板
 */
export const PROCESS_TEMPLATES: ProcessTemplate[] = [
    BF_BOF_TEMPLATE,
    EAF_TEMPLATE,
    DRI_EAF_TEMPLATE,
    COREX_TEMPLATE,
    VACUUM_SPECIAL_TEMPLATE,
    CC_HSM_TEMPLATE,
];

/**
 * 获取默认工艺流程（BF-BOF）
 */
export function getDefaultTemplate(): ProcessTemplate {
    return BF_BOF_TEMPLATE;
}

/**
 * 根据ID获取工艺流程模板
 */
export function getTemplateById(id: string): ProcessTemplate | undefined {
    return PROCESS_TEMPLATES.find((t) => t.id === id);
}

/**
 * 工艺节点颜色映射（用于流程图显示）
 */
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

/**
 * 节点状态颜色映射
 */
export const STATUS_COLORS = {
    normal: "border-green-500 bg-green-50 dark:bg-green-950",
    warning: "border-yellow-500 bg-yellow-50 dark:bg-yellow-950 animate-pulse",
    error: "border-red-500 bg-red-50 dark:bg-red-950 animate-pulse",
    optimizing: "border-blue-500 bg-blue-50 dark:bg-blue-950",
};

