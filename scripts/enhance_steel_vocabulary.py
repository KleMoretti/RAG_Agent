#!/usr/bin/env python3
"""
钢铁行业专业词汇增强脚本

为Agent添加钢铁行业专业词汇，提升专业术语理解和回答质量
"""

import asyncio
from datetime import datetime
from src.api.db import get_db
from src.prompt_management.service import PromptService
from src.prompt_management.schemas import SystemPromptCreate, SystemPromptUpdate, SystemPromptResponse

# 钢铁行业专业词汇库
STEEL_VOCABULARY = {
    "steel_grades": {
        "zh": [
            "Q235", "Q345", "Q420", "Q460", "Q500", "Q550", "Q620", "Q690",
            "20#", "45#", "65Mn", "T8", "T10", "T12",
            "304", "316", "316L", "321", "347", "310S",
            "SUS304", "SUS316", "SUS316L", "SUS321", "SUS347",
            "A36", "A572", "A992", "A500", "A501",
            "S235", "S275", "S355", "S420", "S460",
            "P235", "P265", "P295", "P355", "P420"
        ],
        "en": [
            "Q235", "Q345", "Q420", "Q460", "Q500", "Q550", "Q620", "Q690",
            "20#", "45#", "65Mn", "T8", "T10", "T12",
            "304", "316", "316L", "321", "347", "310S",
            "SUS304", "SUS316", "SUS316L", "SUS321", "SUS347",
            "A36", "A572", "A992", "A500", "A501",
            "S235", "S275", "S355", "S420", "S460",
            "P235", "P265", "P295", "P355", "P420"
        ]
    },
    "steel_types": {
        "zh": [
            "碳素钢", "合金钢", "不锈钢", "工具钢", "弹簧钢", "轴承钢",
            "结构钢", "耐热钢", "耐腐蚀钢", "电工钢", "硅钢",
            "热轧钢", "冷轧钢", "镀锌钢", "镀铝钢", "彩涂钢",
            "低碳钢", "中碳钢", "高碳钢", "低合金钢", "高合金钢"
        ],
        "en": [
            "Carbon Steel", "Alloy Steel", "Stainless Steel", "Tool Steel", 
            "Spring Steel", "Bearing Steel", "Structural Steel", "Heat Resistant Steel",
            "Corrosion Resistant Steel", "Electrical Steel", "Silicon Steel",
            "Hot Rolled Steel", "Cold Rolled Steel", "Galvanized Steel", 
            "Aluminized Steel", "Color Coated Steel", "Low Carbon Steel",
            "Medium Carbon Steel", "High Carbon Steel", "Low Alloy Steel", "High Alloy Steel"
        ]
    },
    "alloy_elements": {
        "zh": [
            "碳", "硅", "锰", "磷", "硫", "铬", "镍", "钼", "钒", "钛",
            "钨", "钴", "铜", "铝", "硼", "氮", "铌", "锆", "稀土",
            "C", "Si", "Mn", "P", "S", "Cr", "Ni", "Mo", "V", "Ti",
            "W", "Co", "Cu", "Al", "B", "N", "Nb", "Zr", "RE"
        ],
        "en": [
            "Carbon", "Silicon", "Manganese", "Phosphorus", "Sulfur", 
            "Chromium", "Nickel", "Molybdenum", "Vanadium", "Titanium",
            "Tungsten", "Cobalt", "Copper", "Aluminum", "Boron", 
            "Nitrogen", "Niobium", "Zirconium", "Rare Earth",
            "C", "Si", "Mn", "P", "S", "Cr", "Ni", "Mo", "V", "Ti",
            "W", "Co", "Cu", "Al", "B", "N", "Nb", "Zr", "RE"
        ]
    },
    "material_properties": {
        "zh": [
            "抗拉强度", "屈服强度", "延伸率", "断面收缩率", "冲击韧性",
            "硬度", "疲劳强度", "蠕变强度", "耐腐蚀性", "耐热性",
            "焊接性", "切削性", "冷加工性", "热处理性", "磁性",
            "σb", "Rm", "σs", "ReL", "ReH", "δ", "A", "ψ", "Z",
            "Akv", "KV", "HB", "HRC", "HV"
        ],
        "en": [
            "Tensile Strength", "Yield Strength", "Elongation", "Reduction of Area",
            "Impact Toughness", "Hardness", "Fatigue Strength", "Creep Strength",
            "Corrosion Resistance", "Heat Resistance", "Weldability", "Machinability",
            "Cold Workability", "Heat Treatability", "Magnetic Properties",
            "σb", "Rm", "σs", "ReL", "ReH", "δ", "A", "ψ", "Z",
            "Akv", "KV", "HB", "HRC", "HV"
        ]
    },
    "processes": {
        "zh": [
            "炼钢", "连铸", "热轧", "冷轧", "退火", "正火", "淬火", "回火",
            "调质", "渗碳", "渗氮", "表面处理", "镀层", "涂层", "酸洗",
            "抛丸", "矫直", "切割", "焊接", "成型", "转炉炼钢", "电炉炼钢",
            "连续铸造", "热轧制", "冷轧制", "完全退火", "球化退火"
        ],
        "en": [
            "Steelmaking", "Continuous Casting", "Hot Rolling", "Cold Rolling",
            "Annealing", "Normalizing", "Quenching", "Tempering", "Quenching and Tempering",
            "Carburizing", "Nitriding", "Surface Treatment", "Coating", "Painting",
            "Pickling", "Shot Blasting", "Straightening", "Cutting", "Welding", "Forming",
            "BOF Steelmaking", "EAF Steelmaking", "Continuous Casting", "Hot Rolling", "Cold Rolling",
            "Full Annealing", "Spheroidizing Annealing"
        ]
    },
    "equipment": {
        "zh": [
            "转炉", "电炉", "连铸机", "热轧机", "冷轧机", "退火炉",
            "淬火炉", "回火炉", "矫直机", "切割机", "焊接机", "镀锌线",
            "彩涂线", "酸洗线", "抛丸机", "检测设备", "包装设备",
            "LD转炉", "BOF", "电弧炉", "EAF", "连铸设备", "热轧设备", "冷轧设备"
        ],
        "en": [
            "Converter", "Electric Furnace", "Continuous Caster", "Hot Rolling Mill",
            "Cold Rolling Mill", "Annealing Furnace", "Quenching Furnace", "Tempering Furnace",
            "Straightening Machine", "Cutting Machine", "Welding Machine", "Galvanizing Line",
            "Color Coating Line", "Pickling Line", "Shot Blasting Machine", "Testing Equipment",
            "Packaging Equipment", "LD Converter", "BOF", "Electric Arc Furnace", "EAF",
            "Continuous Casting Equipment", "Hot Rolling Equipment", "Cold Rolling Equipment"
        ]
    },
    "applications": {
        "zh": [
            "建筑结构", "桥梁工程", "汽车制造", "船舶建造", "压力容器",
            "管道工程", "机械制造", "家电制造", "食品工业", "化工设备",
            "电力设备", "轨道交通", "航空航天", "海洋工程", "新能源",
            "建筑用钢", "桥梁用钢", "汽车用钢", "船舶用钢", "容器用钢"
        ],
        "en": [
            "Building Structure", "Bridge Engineering", "Automotive Manufacturing",
            "Shipbuilding", "Pressure Vessel", "Pipeline Engineering", "Machinery Manufacturing",
            "Home Appliance Manufacturing", "Food Industry", "Chemical Equipment",
            "Power Equipment", "Rail Transit", "Aerospace", "Marine Engineering", "New Energy",
            "Building Steel", "Bridge Steel", "Automotive Steel", "Ship Steel", "Container Steel"
        ]
    },
    "standards": {
        "zh": [
            "GB/T", "GB", "YB", "JB", "HG", "SH", "SY", "TB", "JT",
            "ASTM", "AISI", "SAE", "JIS", "DIN", "EN", "ISO", "API", "ASME", "AWS"
        ],
        "en": [
            "GB/T", "GB", "YB", "JB", "HG", "SH", "SY", "TB", "JT",
            "ASTM", "AISI", "SAE", "JIS", "DIN", "EN", "ISO", "API", "ASME", "AWS"
        ]
    }
}

def create_vocabulary_enhanced_prompts():
    """创建包含钢铁专业词汇的增强prompt模板"""
    
    # 获取数据库连接
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        service = PromptService(db)
        
        # 获取所有Agent
        agents = service.list_agents()
        
        for agent in agents:
            print(f"正在为 {agent.display_name} 增强专业词汇...")
            
            # 为每个Agent创建增强的prompt
            for language in ["zh-CN", "en-US"]:
                lang_code = "zh" if language == "zh-CN" else "en"
                
                # 构建包含专业词汇的prompt
                enhanced_prompt = build_enhanced_prompt(agent.agent_type, language, lang_code)
                
                # 创建新的prompt
                prompt_data = SystemPromptCreate(
                    agent_id=agent.id,
                    name=f"钢铁专业词汇增强-{language}",
                    content=enhanced_prompt,
                    language=language,
                    status="active",
                    is_default=False,
                    variables={
                        "steel_vocabulary": STEEL_VOCABULARY,
                        "last_updated": datetime.now().isoformat()
                    },
                    meta_data={
                        "vocabulary_enhanced": True,
                        "steel_terms_count": sum(len(terms[lang_code]) for terms in STEEL_VOCABULARY.values()),
                        "categories": list(STEEL_VOCABULARY.keys())
                    }
                )
                
                try:
                    new_prompt = service.create_prompt(prompt_data, created_by=1)
                    print(f"✅ 成功为 {agent.display_name} ({language}) 创建增强prompt (ID: {new_prompt.id})")
                except Exception as e:
                    print(f"❌ 为 {agent.display_name} ({language}) 创建prompt失败: {e}")
        
        print(f"\n🎉 钢铁专业词汇增强完成！")
        
    except Exception as e:
        print(f"❌ 增强专业词汇时出错: {e}")
        raise
    finally:
        db.close()

def build_enhanced_prompt(agent_type: str, language: str, lang_code: str) -> str:
    """构建包含钢铁专业词汇的增强prompt"""
    
    # 基础prompt模板
    base_prompts = {
        "zh-CN": {
            "general": """你是一个专业的AI助手，具备广泛的知识基础和问题解决能力。
请根据用户的问题提供准确、有用的回答。

核心能力：
- 多领域知识问答
- 文档分析与总结
- 数据解读与建议
- 工作流程优化

请保持回答的专业性和准确性。""",
            
            "process": """你是钢铁生产工艺专家，深度了解炼钢、轧钢等各个生产环节。
请基于专业知识为用户提供工艺优化和技术改进建议。

专业领域：
- 工艺流程分析
- 生产参数优化
- 技术改进建议
- 工艺故障诊断

请确保建议的可操作性和安全性。""",
            
            "equipment": """你是设备维护和故障诊断专家，具备丰富的设备管理经验。
请帮助用户快速定位问题并提供解决方案。

专业能力：
- 故障快速诊断
- 预防性维护建议
- 设备性能分析
- 维修方案制定

请优先考虑安全因素，提供详细的操作指导。""",
            
            "market": """你是市场分析专家，专注于钢铁行业的市场情报和趋势分析。
请为用户提供专业的市场洞察和决策支持。

分析领域：
- 价格趋势分析
- 供需关系评估
- 竞争情报分析
- 投资决策建议

请基于数据提供客观、准确的分析结论。""",
            
            "quality": """你是质量顾问，专注于质量控制和参数优化。
请为用户提供专业的质量管理和标准制定建议。

专业能力：
- 质量控制
- 参数优化
- 质量检测
- 标准制定

请确保建议的实用性和准确性。""",
            
            "environment": """你是节能专家，帮助您优化能源使用和降低成本。
请为用户提供专业的节能和环保建议。

专业能力：
- 能源分析
- 节能优化
- 成本控制
- 环保建议

请确保建议的经济性和环保性。"""
        },
        "en-US": {
            "general": """You are a professional AI assistant with extensive knowledge and problem-solving capabilities.
Please provide accurate and helpful responses based on user questions.

Core Capabilities:
- Multi-domain Q&A
- Document analysis and summarization
- Data interpretation and recommendations
- Workflow optimization

Please maintain professionalism and accuracy in your responses.""",
            
            "process": """You are a steel production process expert with deep understanding of steelmaking, rolling, and other production processes.
Please provide process optimization and technical improvement suggestions based on professional knowledge.

Expertise Areas:
- Process flow analysis
- Production parameter optimization
- Technical improvement recommendations
- Process fault diagnosis

Please ensure suggestions are actionable and safe.""",
            
            "equipment": """You are an equipment maintenance and fault diagnosis expert with extensive equipment management experience.
Please help users quickly identify problems and provide solutions.

Professional Capabilities:
- Rapid fault diagnosis
- Preventive maintenance recommendations
- Equipment performance analysis
- Repair plan development

Please prioritize safety factors and provide detailed operational guidance.""",
            
            "market": """You are a market analysis expert focused on steel industry market intelligence and trend analysis.
Please provide professional market insights and decision support for users.

Analysis Areas:
- Price trend analysis
- Supply and demand assessment
- Competitive intelligence analysis
- Investment decision recommendations

Please provide objective and accurate analytical conclusions based on data.""",
            
            "quality": """You are a quality consultant specializing in quality control and parameter optimization.
Please provide professional quality management and standard development recommendations.

Professional Capabilities:
- Quality control
- Parameter optimization
- Quality testing
- Standard development

Please ensure recommendations are practical and accurate.""",
            
            "environment": """You are an energy efficiency expert helping optimize energy usage and reduce costs.
Please provide professional energy saving and environmental recommendations.

Professional Capabilities:
- Energy analysis
- Energy saving optimization
- Cost control
- Environmental recommendations

Please ensure recommendations are economical and environmentally friendly."""
        }
    }
    
    # 获取基础prompt
    base_prompt = base_prompts[language].get(agent_type, base_prompts[language]["general"])
    
    # 构建专业词汇部分
    vocabulary_section = build_vocabulary_section(language, lang_code)
    
    # 组合最终prompt
    enhanced_prompt = f"""{base_prompt}

=== 钢铁行业专业词汇库 ===
{vocabulary_section}

=== 使用指导 ===
在回答问题时，请：
1. 优先使用上述专业词汇和术语
2. 确保术语使用的准确性和一致性
3. 根据用户的技术水平调整术语解释的详细程度
4. 提供中英文对照时，优先使用上述标准术语
5. 对于复杂概念，提供通俗易懂的解释

请基于以上专业词汇库，为用户提供更专业、准确的钢铁行业相关回答。"""
    
    return enhanced_prompt

def build_vocabulary_section(language: str, lang_code: str) -> str:
    """构建专业词汇部分"""
    
    if language == "zh-CN":
        section = """以下是钢铁行业核心专业词汇，请熟练掌握并在回答中准确使用：

【钢种牌号】
{steel_grades}

【钢材类型】
{steel_types}

【合金元素】
{alloy_elements}

【材料性能】
{material_properties}

【工艺流程】
{processes}

【设备名称】
{equipment}

【应用领域】
{applications}

【标准规范】
{standards}""".format(
            steel_grades="、".join(STEEL_VOCABULARY["steel_grades"][lang_code]),
            steel_types="、".join(STEEL_VOCABULARY["steel_types"][lang_code]),
            alloy_elements="、".join(STEEL_VOCABULARY["alloy_elements"][lang_code]),
            material_properties="、".join(STEEL_VOCABULARY["material_properties"][lang_code]),
            processes="、".join(STEEL_VOCABULARY["processes"][lang_code]),
            equipment="、".join(STEEL_VOCABULARY["equipment"][lang_code]),
            applications="、".join(STEEL_VOCABULARY["applications"][lang_code]),
            standards="、".join(STEEL_VOCABULARY["standards"][lang_code])
        )
    else:
        section = """Below are the core professional vocabulary for the steel industry. Please master these terms and use them accurately in your responses:

【Steel Grades】
{steel_grades}

【Steel Types】
{steel_types}

【Alloy Elements】
{alloy_elements}

【Material Properties】
{material_properties}

【Processes】
{processes}

【Equipment】
{equipment}

【Applications】
{applications}

【Standards】
{standards}""".format(
            steel_grades=", ".join(STEEL_VOCABULARY["steel_grades"][lang_code]),
            steel_types=", ".join(STEEL_VOCABULARY["steel_types"][lang_code]),
            alloy_elements=", ".join(STEEL_VOCABULARY["alloy_elements"][lang_code]),
            material_properties=", ".join(STEEL_VOCABULARY["material_properties"][lang_code]),
            processes=", ".join(STEEL_VOCABULARY["processes"][lang_code]),
            equipment=", ".join(STEEL_VOCABULARY["equipment"][lang_code]),
            applications=", ".join(STEEL_VOCABULARY["applications"][lang_code]),
            standards=", ".join(STEEL_VOCABULARY["standards"][lang_code])
        )
    
    return section

# 移除更新现有prompt的功能，只创建新的增强prompt

if __name__ == "__main__":
    print("🚀 开始钢铁行业专业词汇增强...")
    print("=" * 50)
    
    # 创建新的增强prompt
    create_vocabulary_enhanced_prompts()
    
    print("\n" + "=" * 50)
    print("✅ 钢铁行业专业词汇增强完成！")
    print("\n📋 增强内容包括：")
    print(f"- 钢种牌号: {len(STEEL_VOCABULARY['steel_grades']['zh'])} 个")
    print(f"- 钢材类型: {len(STEEL_VOCABULARY['steel_types']['zh'])} 个")
    print(f"- 合金元素: {len(STEEL_VOCABULARY['alloy_elements']['zh'])} 个")
    print(f"- 材料性能: {len(STEEL_VOCABULARY['material_properties']['zh'])} 个")
    print(f"- 工艺流程: {len(STEEL_VOCABULARY['processes']['zh'])} 个")
    print(f"- 设备名称: {len(STEEL_VOCABULARY['equipment']['zh'])} 个")
    print(f"- 应用领域: {len(STEEL_VOCABULARY['applications']['zh'])} 个")
    print(f"- 标准规范: {len(STEEL_VOCABULARY['standards']['zh'])} 个")
    print(f"\n总计: {sum(len(terms['zh']) for terms in STEEL_VOCABULARY.values())} 个专业术语")
    print("\n💡 使用说明:")
    print("1. 在聊天界面选择对应的专业Agent（如工艺专家、设备诊断等）")
    print("2. 询问钢铁行业相关问题，Agent会使用专业术语回答")
    print("3. 可以通过Admin面板查看和编辑prompt模板")
