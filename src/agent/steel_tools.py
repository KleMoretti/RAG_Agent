# -*- coding: utf-8 -*-
"""
钢铁领域专用Agent工具集

提供钢种查询、工艺计算、设备诊断、成本分析等钢铁行业专业工具
"""

from typing import Dict, Any, List, Optional, Union
import math
from .tools import Tool


class SteelGradeQueryTool(Tool):
    """
    钢种性能查询工具
    
    查询常见钢种的化学成分、力学性能、应用场景等信息
    """
    
    # 钢种数据库
    STEEL_DATABASE = {
        "Q235": {
            "name": "Q235普通碳素结构钢",
            "chemical_composition": {
                "C": "≤0.22%",
                "Si": "≤0.35%",
                "Mn": "0.30-0.65%",
                "S": "≤0.050%",
                "P": "≤0.045%"
            },
            "mechanical_properties": {
                "抗拉强度": "375-500 MPa",
                "屈服强度": "≥235 MPa",
                "延伸率": "≥26%",
                "冲击韧性": "≥27 J (20℃)"
            },
            "applications": ["建筑结构", "桥梁", "车辆", "船舶", "一般机械零件"],
            "weldability": "良好",
            "standard": "GB/T 700-2006"
        },
        "Q345": {
            "name": "Q345低合金高强度结构钢",
            "chemical_composition": {
                "C": "≤0.20%",
                "Si": "≤0.55%",
                "Mn": "1.00-1.60%",
                "S": "≤0.035%",
                "P": "≤0.035%"
            },
            "mechanical_properties": {
                "抗拉强度": "470-630 MPa",
                "屈服强度": "≥345 MPa",
                "延伸率": "≥21%",
                "冲击韧性": "≥34 J (-20℃)"
            },
            "applications": ["大型桥梁", "压力容器", "高层建筑", "重型机械"],
            "weldability": "良好",
            "standard": "GB/T 1591-2008"
        },
        "304": {
            "name": "304奥氏体不锈钢",
            "chemical_composition": {
                "C": "≤0.08%",
                "Si": "≤1.00%",
                "Mn": "≤2.00%",
                "Cr": "18.0-20.0%",
                "Ni": "8.0-10.5%"
            },
            "mechanical_properties": {
                "抗拉强度": "≥520 MPa",
                "屈服强度": "≥205 MPa",
                "延伸率": "≥40%",
                "硬度": "≤200 HB"
            },
            "applications": ["食品设备", "化工容器", "医疗器械", "装饰材料", "家电"],
            "corrosion_resistance": "优良",
            "weldability": "优良",
            "standard": "GB/T 3280-2015"
        },
        "45": {
            "name": "45#中碳结构钢",
            "chemical_composition": {
                "C": "0.42-0.50%",
                "Si": "0.17-0.37%",
                "Mn": "0.50-0.80%",
                "S": "≤0.035%",
                "P": "≤0.035%"
            },
            "mechanical_properties": {
                "抗拉强度": "≥600 MPa (调质后)",
                "屈服强度": "≥355 MPa",
                "延伸率": "≥16%",
                "硬度": "170-217 HB (退火)"
            },
            "applications": ["轴类零件", "齿轮", "连杆", "螺栓", "机械零件"],
            "heat_treatment": "调质、正火、淬火",
            "machinability": "良好",
            "standard": "GB/T 699-2015"
        },
        "316L": {
            "name": "316L超低碳奥氏体不锈钢",
            "chemical_composition": {
                "C": "≤0.03%",
                "Si": "≤1.00%",
                "Mn": "≤2.00%",
                "Cr": "16.0-18.0%",
                "Ni": "10.0-14.0%",
                "Mo": "2.0-3.0%"
            },
            "mechanical_properties": {
                "抗拉强度": "≥480 MPa",
                "屈服强度": "≥177 MPa",
                "延伸率": "≥40%",
                "硬度": "≤200 HB"
            },
            "applications": ["海洋工程", "化工设备", "医药设备", "造纸机械", "核电设备"],
            "corrosion_resistance": "极优（耐海水、耐氯离子）",
            "weldability": "优良",
            "standard": "GB/T 3280-2015"
        }
    }
    
    def __init__(self):
        super().__init__(
            name="steel_grade_query",
            description="查询钢种的化学成分、力学性能、应用场景等详细信息。支持Q235、Q345、304、316L、45#等常见钢种"
        )
    
    def run(self, steel_grade: str) -> Dict[str, Any]:
        """查询钢种信息"""
        steel_grade = steel_grade.strip().upper().replace("#", "")
        
        if steel_grade in self.STEEL_DATABASE:
            return {
                "success": True,
                "steel_grade": steel_grade,
                "data": self.STEEL_DATABASE[steel_grade]
            }
        
        for key in self.STEEL_DATABASE.keys():
            if key.upper() == steel_grade or key.replace("#", "") == steel_grade:
                return {
                    "success": True,
                    "steel_grade": key,
                    "data": self.STEEL_DATABASE[key]
                }
        
        available_grades = list(self.STEEL_DATABASE.keys())
        return {
            "success": False,
            "error": f"未找到钢种 '{steel_grade}' 的信息",
            "suggestion": f"可用钢种: {', '.join(available_grades)}"
        }


class ProcessParameterTool(Tool):
    """工艺参数计算工具"""
    
    def __init__(self):
        super().__init__(
            name="process_parameter_calculator",
            description="计算钢铁生产工艺参数，如热轧温度、轧制力、冷却速度、热处理时间等"
        )
    
    def run(self, process_type: str, **params) -> Dict[str, Any]:
        """计算工艺参数"""
        process_type = process_type.lower().strip()
        
        if process_type == "hot_rolling":
            return self._calculate_hot_rolling(**params)
        elif process_type == "heat_treatment":
            return self._calculate_heat_treatment(**params)
        elif process_type == "cooling":
            return self._calculate_cooling(**params)
        else:
            return {
                "success": False,
                "error": f"不支持的工艺类型: {process_type}",
                "supported_types": ["hot_rolling", "heat_treatment", "cooling"]
            }
    
    def _calculate_hot_rolling(
        self,
        steel_grade: str = "Q235",
        thickness_initial: float = 200.0,
        thickness_final: float = 10.0,
        width: float = 1500.0,
        **kwargs
    ) -> Dict[str, Any]:
        """计算热轧参数"""
        total_reduction = ((thickness_initial - thickness_final) / thickness_initial) * 100
        deformation_resistance = 100
        contact_length = math.sqrt((thickness_initial - thickness_final) * 500)
        rolling_force = 1.15 * deformation_resistance * contact_length * width / 1000
        
        temp_ranges = {
            "Q235": {"start": 1150, "finish": 850},
            "Q345": {"start": 1100, "finish": 820},
            "304": {"start": 1150, "finish": 900},
            "45": {"start": 1180, "finish": 880}
        }
        temp_range = temp_ranges.get(steel_grade.upper(), {"start": 1100, "finish": 850})
        passes = max(3, int(total_reduction / 15))
        
        return {
            "success": True,
            "process": "热轧",
            "parameters": {
                "总压下率": f"{total_reduction:.1f}%",
                "估算轧制力": f"{rolling_force:.0f} kN",
                "推荐开轧温度": f"{temp_range['start']}°C",
                "推荐终轧温度": f"{temp_range['finish']}°C",
                "建议轧制道次": passes,
                "每道次平均压下率": f"{total_reduction / passes:.1f}%"
            }
        }
    
    def _calculate_heat_treatment(
        self,
        steel_grade: str = "45",
        treatment_type: str = "quenching",
        thickness: float = 20.0,
        **kwargs
    ) -> Dict[str, Any]:
        """计算热处理参数"""
        holding_time = thickness * 1.2
        
        treatment_params = {
            "quenching": {
                "45": {"temp": 840, "medium": "油", "hardness": "45-55 HRC"},
                "Q345": {"temp": 870, "medium": "水", "hardness": "35-45 HRC"}
            },
            "tempering": {
                "45": {"temp": 550, "medium": "空气", "hardness": "25-35 HRC"}
            }
        }
        
        params = treatment_params.get(treatment_type, {}).get(steel_grade.upper())
        if not params:
            return {
                "success": False,
                "error": f"不支持钢种 {steel_grade} 的 {treatment_type} 工艺"
            }
        
        return {
            "success": True,
            "process": f"热处理-{treatment_type}",
            "parameters": {
                "加热温度": f"{params['temp']}±10°C",
                "保温时间": f"{holding_time:.0f}分钟",
                "冷却介质": params['medium'],
                "预期硬度": params['hardness']
            }
        }
    
    def _calculate_cooling(
        self,
        initial_temp: float = 900.0,
        target_temp: float = 500.0,
        cooling_rate: float = 15.0,
        **kwargs
    ) -> Dict[str, Any]:
        """计算冷却参数"""
        temp_diff = initial_temp - target_temp
        cooling_time = temp_diff / cooling_rate
        
        if cooling_rate > 50:
            cooling_method = "水冷（急冷）"
            risk_level = "高"
        elif cooling_rate > 20:
            cooling_method = "油冷"
            risk_level = "中"
        else:
            cooling_method = "空冷"
            risk_level = "低"
        
        return {
            "success": True,
            "process": "冷却计算",
            "parameters": {
                "温度区间": f"{initial_temp}°C → {target_temp}°C",
                "冷却速度": f"{cooling_rate}°C/s",
                "估算冷却时间": f"{cooling_time:.1f}秒",
                "推荐冷却方式": cooling_method,
                "风险等级": risk_level
            }
        }


class EquipmentDiagnosisTool(Tool):
    """设备故障诊断工具"""
    
    FAULT_DATABASE = {
        "轧机": {
            "异常振动": {
                "possible_causes": ["轴承磨损或损坏", "轧辊不平衡", "传动系统松动"],
                "diagnostic_steps": ["检查振动频率", "检查轴承温度", "检查轧辊跳动量"],
                "solutions": ["更换磨损轴承", "重新平衡轧辊", "紧固松动部件"],
                "urgency": "高"
            },
            "温度过高": {
                "possible_causes": ["轴承润滑不良", "冷却系统故障", "轧制负荷过大"],
                "diagnostic_steps": ["检查润滑油量", "检查冷却水流量", "监测轧制力"],
                "solutions": ["补充润滑油", "修复冷却系统", "降低轧制负荷"],
                "urgency": "中"
            }
        },
        "加热炉": {
            "温度不均": {
                "possible_causes": ["烧嘴堵塞", "空燃比不当", "炉压控制失调"],
                "diagnostic_steps": ["检查各烧嘴火焰", "测量空燃比", "检查炉压表"],
                "solutions": ["清理烧嘴", "调整空燃比", "修复炉压控制"],
                "urgency": "中"
            }
        }
    }
    
    def __init__(self):
        super().__init__(
            name="equipment_diagnosis",
            description="根据设备症状诊断故障原因，提供维修建议"
        )
    
    def run(self, equipment_type: str, symptom: str, **additional_info) -> Dict[str, Any]:
        """诊断设备故障"""
        equipment_type = equipment_type.strip()
        symptom = symptom.strip()
        
        equipment_data = None
        for eq_name in self.FAULT_DATABASE.keys():
            if eq_name in equipment_type or equipment_type in eq_name:
                equipment_data = self.FAULT_DATABASE[eq_name]
                equipment_type = eq_name
                break
        
        if not equipment_data:
            return {
                "success": False,
                "error": f"不支持的设备类型: {equipment_type}",
                "supported_equipment": list(self.FAULT_DATABASE.keys())
            }
        
        fault_info = None
        for symptom_key in equipment_data.keys():
            if symptom_key in symptom or symptom in symptom_key:
                fault_info = equipment_data[symptom_key]
                symptom = symptom_key
                break
        
        if not fault_info:
            return {
                "success": False,
                "error": f"{equipment_type}不支持的故障症状: {symptom}",
                "supported_symptoms": list(equipment_data.keys())
            }
        
        result = {
            "success": True,
            "equipment": equipment_type,
            "symptom": symptom,
            "urgency": fault_info["urgency"],
            "possible_causes": fault_info["possible_causes"],
            "diagnostic_procedure": fault_info["diagnostic_steps"],
            "recommended_solutions": fault_info["solutions"]
        }
        
        if fault_info["urgency"] == "高":
            result["warning"] = "⚠️ 此故障紧急程度高，建议立即停机检修"
        
        return result


class MaterialCostCalculatorTool(Tool):
    """生产成本计算工具"""
    
    MATERIAL_PRICES = {
        "铁矿石": {"price": 850, "unit": "元/吨"},
        "焦炭": {"price": 2400, "unit": "元/吨"},
        "废钢": {"price": 2600, "unit": "元/吨"},
        "电力": {"price": 0.65, "unit": "元/kWh"}
    }
    
    def __init__(self):
        super().__init__(
            name="material_cost_calculator",
            description="计算钢铁生产成本，包括原材料成本、能源成本等"
        )
    
    def run(
        self,
        calculation_type: str = "blast_furnace",
        output_tons: float = 1.0,
        custom_prices: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """计算生产成本"""
        if calculation_type == "blast_furnace":
            return self._calculate_blast_furnace_cost(output_tons, custom_prices)
        elif calculation_type == "eaf":
            return self._calculate_eaf_cost(output_tons, custom_prices)
        else:
            return {
                "success": False,
                "error": f"不支持的计算类型: {calculation_type}",
                "supported_types": ["blast_furnace", "eaf"]
            }
    
    def _calculate_blast_furnace_cost(
        self,
        output_tons: float,
        custom_prices: Optional[Dict]
    ) -> Dict[str, Any]:
        """计算高炉炼铁成本"""
        iron_ore_consumption = 1.6
        coke_consumption = 0.35
        
        prices = self.MATERIAL_PRICES.copy()
        if custom_prices:
            prices.update(custom_prices)
        
        iron_ore_cost = iron_ore_consumption * prices["铁矿石"]["price"] * output_tons
        coke_cost = coke_consumption * prices["焦炭"]["price"] * output_tons
        power_cost = 50 * prices["电力"]["price"] * output_tons
        
        total_cost = iron_ore_cost + coke_cost + power_cost
        
        return {
            "success": True,
            "process": "高炉炼铁",
            "output": f"{output_tons} 吨铁水",
            "cost_breakdown": {
                "铁矿石": f"{iron_ore_cost:.2f} 元",
                "焦炭": f"{coke_cost:.2f} 元",
                "电力": f"{power_cost:.2f} 元"
            },
            "summary": {
                "总成本": f"{total_cost:.2f} 元",
                "吨铁成本": f"{total_cost / output_tons:.2f} 元/吨"
            }
        }
    
    def _calculate_eaf_cost(
        self,
        output_tons: float,
        custom_prices: Optional[Dict]
    ) -> Dict[str, Any]:
        """计算电炉炼钢成本"""
        scrap_consumption = 1.08
        power_consumption = 450
        
        prices = self.MATERIAL_PRICES.copy()
        if custom_prices:
            prices.update(custom_prices)
        
        scrap_cost = scrap_consumption * prices["废钢"]["price"] * output_tons
        power_cost = power_consumption * prices["电力"]["price"] * output_tons
        electrode_cost = 30 * output_tons
        
        total_cost = scrap_cost + power_cost + electrode_cost
        
        return {
            "success": True,
            "process": "电炉炼钢",
            "output": f"{output_tons} 吨钢水",
            "cost_breakdown": {
                "废钢": f"{scrap_cost:.2f} 元",
                "电力": f"{power_cost:.2f} 元",
                "电极": f"{electrode_cost:.2f} 元"
            },
            "summary": {
                "总成本": f"{total_cost:.2f} 元",
                "吨钢成本": f"{total_cost / output_tons:.2f} 元/吨"
            }
        }


class StandardQueryTool(Tool):
    """标准规范查询工具"""
    
    STANDARDS_DATABASE = {
        "GB/T 700-2006": {
            "title": "碳素结构钢",
            "scope": "规定了碳素结构钢的牌号、尺寸、外形、技术要求等",
            "steel_grades": ["Q195", "Q215", "Q235", "Q275"],
            "key_requirements": [
                "化学成分符合表1规定",
                "力学性能符合表2规定",
                "低温冲击试验（需方要求时）",
                "表面质量：不得有裂纹、结疤、折叠"
            ]
        },
        "GB/T 1591-2008": {
            "title": "低合金高强度结构钢",
            "scope": "规定了低合金高强度结构钢的分类、牌号、尺寸、技术要求等",
            "steel_grades": ["Q345", "Q390", "Q420", "Q460", "Q500", "Q550"],
            "key_requirements": [
                "化学成分：C、Si、Mn、P、S及合金元素含量",
                "力学性能：屈服强度、抗拉强度、延伸率、冲击韧性",
                "质量等级：A、B、C、D、E（冲击温度要求不同）",
                "交货状态：热轧、正火、正火轧制等"
            ]
        },
        "GB/T 3280-2015": {
            "title": "不锈钢冷轧钢板和钢带",
            "scope": "规定了不锈钢冷轧钢板和钢带的分类、牌号、尺寸、技术要求等",
            "steel_grades": ["304", "304L", "316", "316L", "321", "310S"],
            "key_requirements": [
                "化学成分符合GB/T 20878规定",
                "力学性能：屈服强度、抗拉强度、延伸率、硬度",
                "表面质量：2B、BA、NO.1等表面状态",
                "耐腐蚀性能要求"
            ]
        },
        "GB/T 699-2015": {
            "title": "优质碳素结构钢",
            "scope": "规定了优质碳素结构钢的牌号、化学成分、技术要求等",
            "steel_grades": ["08", "10", "15", "20", "25", "30", "35", "40", "45", "50"],
            "key_requirements": [
                "化学成分：碳、硅、锰、磷、硫含量严格控制",
                "交货状态：热轧、锻制、冷拉",
                "可进行热处理：退火、正火、淬火、回火",
                "用途：制造机械零件、齿轮、轴类等"
            ]
        }
    }
    
    def __init__(self):
        super().__init__(
            name="standard_query",
            description="查询钢铁行业标准规范，如GB/T 700、GB/T 1591等国家标准信息"
        )
    
    def run(self, standard_number: str) -> Dict[str, Any]:
        """查询标准信息"""
        standard_number = standard_number.strip().upper()
        
        # 精确匹配
        if standard_number in self.STANDARDS_DATABASE:
            return {
                "success": True,
                "standard_number": standard_number,
                "data": self.STANDARDS_DATABASE[standard_number]
            }
        
        # 模糊匹配（不包含年份）
        for key in self.STANDARDS_DATABASE.keys():
            if key.startswith(standard_number) or standard_number in key:
                return {
                    "success": True,
                    "standard_number": key,
                    "data": self.STANDARDS_DATABASE[key],
                    "note": f"已自动匹配到标准: {key}"
                }
        
        return {
            "success": False,
            "error": f"未找到标准: {standard_number}",
            "available_standards": list(self.STANDARDS_DATABASE.keys())
        }


class KnowledgeGraphQueryTool(Tool):
    """知识图谱查询工具"""
    
    def __init__(self):
        super().__init__(
            name="knowledge_graph_query",
            description="查询钢铁知识图谱，探索钢种、工艺、设备之间的关系。支持查询：实体属性、关系路径、相似实体"
        )
    
    def run(self, query_type: str, entity_name: str, **kwargs) -> Dict[str, Any]:
        """查询知识图谱"""
        query_type = query_type.lower().strip()
        
        if query_type == "properties":
            return self._query_properties(entity_name)
        elif query_type == "relationships":
            return self._query_relationships(entity_name)
        elif query_type == "similar":
            return self._query_similar(entity_name)
        else:
            return {
                "success": False,
                "error": f"不支持的查询类型: {query_type}",
                "supported_types": ["properties", "relationships", "similar"]
            }
    
    def _query_properties(self, entity_name: str) -> Dict[str, Any]:
        """查询实体属性"""
        mock_entities = {
            "Q235": {
                "type": "钢种",
                "category": "碳素结构钢",
                "standard": "GB/T 700-2006",
                "yield_strength": "235 MPa",
                "applications": ["建筑", "桥梁", "车辆"],
                "weldability": "良好"
            },
            "热轧": {
                "type": "工艺",
                "category": "轧制工艺",
                "temperature_range": "850-1150°C",
                "equipment": ["加热炉", "热轧机", "卷取机"],
                "products": ["热轧板", "热轧卷", "型钢"]
            },
            "转炉": {
                "type": "设备",
                "category": "炼钢设备",
                "capacity": "100-350吨",
                "process": "氧气顶吹转炉炼钢",
                "raw_materials": ["铁水", "废钢", "石灰"]
            }
        }
        
        if entity_name in mock_entities:
            return {
                "success": True,
                "entity": entity_name,
                "properties": mock_entities[entity_name]
            }
        else:
            return {
                "success": False,
                "error": f"知识图谱中未找到实体: {entity_name}"
            }
    
    def _query_relationships(self, entity_name: str) -> Dict[str, Any]:
        """查询实体关系"""
        mock_relationships = {
            "Q235": [
                {"relation": "属于", "target": "碳素结构钢", "type": "分类"},
                {"relation": "用于生产", "target": "建筑结构件", "type": "应用"},
                {"relation": "可通过", "target": "热轧工艺", "type": "加工"},
                {"relation": "符合标准", "target": "GB/T 700-2006", "type": "标准"}
            ],
            "热轧": [
                {"relation": "需要设备", "target": "热轧机", "type": "设备"},
                {"relation": "前道工序", "target": "加热", "type": "工艺流程"},
                {"relation": "后道工序", "target": "冷却", "type": "工艺流程"},
                {"relation": "生产产品", "target": "热轧板", "type": "产品"}
            ]
        }
        
        if entity_name in mock_relationships:
            relationships = mock_relationships[entity_name]
            return {
                "success": True,
                "entity": entity_name,
                "relationship_count": len(relationships),
                "relationships": relationships
            }
        else:
            return {
                "success": False,
                "error": f"未找到实体 {entity_name} 的关系信息"
            }
    
    def _query_similar(self, entity_name: str) -> Dict[str, Any]:
        """查询相似实体"""
        mock_similar = {
            "Q235": [
                {"entity": "Q215", "similarity": 0.92, "reason": "同属碳素结构钢，性能接近"},
                {"entity": "Q275", "similarity": 0.88, "reason": "同类钢种，强度稍高"},
                {"entity": "A36", "similarity": 0.85, "reason": "美标对应钢种"}
            ],
            "304": [
                {"entity": "304L", "similarity": 0.95, "reason": "超低碳版本，焊接性能更好"},
                {"entity": "321", "similarity": 0.82, "reason": "同属奥氏体不锈钢"},
                {"entity": "316", "similarity": 0.78, "reason": "添加钼，耐腐蚀性更强"}
            ]
        }
        
        if entity_name in mock_similar:
            return {
                "success": True,
                "entity": entity_name,
                "similar_entities": mock_similar[entity_name]
            }
        else:
            return {
                "success": False,
                "error": f"未找到与 {entity_name} 相似的实体"
            }


class QualityAnalysisTool(Tool):
    """质量分析工具"""
    
    def __init__(self):
        super().__init__(
            name="quality_analysis",
            description="分析钢材质量缺陷，诊断原因并提供改进措施。支持的缺陷类型：表面缺陷、尺寸偏差、性能不达标"
        )
    
    def run(self, defect_type: str, description: str, **params) -> Dict[str, Any]:
        """分析质量问题"""
        defect_type = defect_type.lower().strip()
        
        if defect_type == "surface":
            return self._analyze_surface_defect(description, params)
        elif defect_type == "dimension":
            return self._analyze_dimension_defect(description, params)
        elif defect_type == "performance":
            return self._analyze_performance_defect(description, params)
        else:
            return {
                "success": False,
                "error": f"不支持的缺陷类型: {defect_type}",
                "supported_types": ["surface", "dimension", "performance"]
            }
    
    def _analyze_surface_defect(self, description: str, params: Dict) -> Dict[str, Any]:
        """分析表面缺陷"""
        defect_causes = {
            "裂纹": {
                "possible_causes": [
                    "冷却速度过快",
                    "钢中氢含量过高",
                    "热加工温度不当",
                    "成分偏析严重"
                ],
                "solutions": [
                    "控制冷却速度，采用缓冷或分级冷却",
                    "加强脱氢处理，控制钢液中氢含量",
                    "优化加热温度和轧制温度",
                    "改善连铸工艺，减少偏析"
                ]
            },
            "麻点": {
                "possible_causes": [
                    "钢液氧化严重",
                    "保护渣质量差",
                    "连铸结晶器漏钢"
                ],
                "solutions": [
                    "加强钢液脱氧，使用优质脱氧剂",
                    "改善保护渣性能",
                    "检查结晶器，防止漏钢"
                ]
            },
            "划伤": {
                "possible_causes": [
                    "导卫装置磨损",
                    "辊道有异物",
                    "吊运过程碰撞"
                ],
                "solutions": [
                    "定期检查和更换导卫",
                    "清理辊道，保持清洁",
                    "改进吊运方式，使用防护垫"
                ]
            }
        }
        
        matched_defect = None
        for defect_name, info in defect_causes.items():
            if defect_name in description:
                matched_defect = defect_name
                break
        
        if matched_defect:
            return {
                "success": True,
                "defect_type": "表面缺陷",
                "defect_name": matched_defect,
                "analysis": defect_causes[matched_defect],
                "severity": "根据缺陷尺寸和深度确定"
            }
        else:
            return {
                "success": True,
                "defect_type": "表面缺陷",
                "description": description,
                "general_advice": "建议详细检查缺陷形态、位置、分布",
                "common_surface_defects": list(defect_causes.keys())
            }
    
    def _analyze_dimension_defect(self, description: str, params: Dict) -> Dict[str, Any]:
        """分析尺寸偏差"""
        thickness_deviation = params.get("thickness_deviation", 0)
        width_deviation = params.get("width_deviation", 0)
        
        issues = []
        
        if abs(thickness_deviation) > 0.1:
            issues.append({
                "item": "厚度偏差",
                "value": f"{thickness_deviation:+.2f} mm",
                "causes": ["轧辊磨损", "AGC系统故障", "来料厚度波动"],
                "solutions": ["更换或修磨轧辊", "校准AGC系统", "控制来料质量"]
            })
        
        if abs(width_deviation) > 5:
            issues.append({
                "item": "宽度偏差",
                "value": f"{width_deviation:+.1f} mm",
                "causes": ["侧导板调整不当", "轧制温度不均"],
                "solutions": ["调整侧导板位置", "均匀加热"]
            })
        
        if not issues:
            return {
                "success": True,
                "result": "尺寸偏差在合格范围内",
                "thickness_deviation": f"{thickness_deviation:+.2f} mm",
                "width_deviation": f"{width_deviation:+.1f} mm"
            }
        
        return {
            "success": True,
            "defect_type": "尺寸偏差",
            "issues": issues
        }
    
    def _analyze_performance_defect(self, description: str, params: Dict) -> Dict[str, Any]:
        """分析性能不达标"""
        tensile_strength = params.get("tensile_strength")
        required_tensile = params.get("required_tensile", 400)
        
        issues = []
        
        if tensile_strength and tensile_strength < required_tensile:
            issues.append({
                "property": "抗拉强度",
                "measured": f"{tensile_strength} MPa",
                "required": f"{required_tensile} MPa",
                "possible_causes": [
                    "化学成分不达标（C、Mn含量低）",
                    "轧制温度过高",
                    "冷却速度过慢"
                ],
                "solutions": [
                    "调整配料，控制化学成分",
                    "降低终轧温度",
                    "加快冷却速度"
                ]
            })
        
        if not issues:
            return {
                "success": True,
                "result": "力学性能符合要求",
                "measured_values": params
            }
        
        return {
            "success": True,
            "defect_type": "性能不达标",
            "issues": issues
        }


def register_steel_tools(agent) -> int:
    """
    将所有钢铁工具注册到Agent
    
    Args:
        agent: RAGAgent或BaseAgent实例
    
    Returns:
        注册的工具数量
    """
    tools = [
        SteelGradeQueryTool(),
        ProcessParameterTool(),
        EquipmentDiagnosisTool(),
        MaterialCostCalculatorTool(),
        StandardQueryTool(),
        KnowledgeGraphQueryTool(),
        QualityAnalysisTool()
    ]
    
    for tool in tools:
        agent.add_tool(tool)
    
    return len(tools)

