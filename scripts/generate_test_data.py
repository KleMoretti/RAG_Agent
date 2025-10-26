"""生成设备故障监控测试数据."""

import pandas as pd
import numpy as np
import argparse


def generate_fault_data(n_samples=1000, output_file="equipment_fault_data.csv"):
    """生成设备故障监控测试数据
    
    Args:
        n_samples: 样本数量
        output_file: 输出文件名
    """
    np.random.seed(42)
    
    equipment_types = ["Turbine", "Compressor", "Pump"]
    locations = ["Atlanta", "Chicago", "San Francisco", "New York", "Houston"]
    
    data = []
    
    for i in range(n_samples):
        equipment_type = np.random.choice(equipment_types)
        location = np.random.choice(locations)
        
        # 生成传感器数据（正常设备）
        if equipment_type == "Turbine":
            temp_mean, temp_std = 70, 10
            pressure_mean, pressure_std = 40, 10
            vibration_mean, vibration_std = 1.5, 0.5
            humidity_mean, humidity_std = 50, 10
        elif equipment_type == "Compressor":
            temp_mean, temp_std = 65, 10
            pressure_mean, pressure_std = 50, 15
            vibration_mean, vibration_std = 2.0, 0.8
            humidity_mean, humidity_std = 45, 10
        else:  # Pump
            temp_mean, temp_std = 60, 10
            pressure_mean, pressure_std = 35, 10
            vibration_mean, vibration_std = 1.0, 0.3
            humidity_mean, humidity_std = 55, 10
        
        # 决定是否故障（15%的故障率）
        is_faulty = np.random.random() < 0.15
        
        if is_faulty:
            # 故障设备：参数偏离正常值
            temperature = np.random.normal(temp_mean + 20, temp_std)
            pressure = np.random.normal(pressure_mean + 15, pressure_std)
            vibration = np.random.normal(vibration_mean + 2.0, vibration_std)
            humidity = np.random.normal(humidity_mean, humidity_std)
        else:
            # 正常设备
            temperature = np.random.normal(temp_mean, temp_std)
            pressure = np.random.normal(pressure_mean, pressure_std)
            vibration = np.random.normal(vibration_mean, vibration_std)
            humidity = np.random.normal(humidity_mean, humidity_std)
        
        data.append({
            "temperature": round(temperature, 2),
            "pressure": round(pressure, 2),
            "vibration": round(vibration, 4),
            "humidity": round(humidity, 4),
            "equipment_type": equipment_type,
            "location": location,
            "faulty": 1 if is_faulty else 0,
        })
    
    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    print(f"✅ 已生成测试数据: {output_file}")
    print(f"   样本数: {len(df)}")
    print(f"   故障样本: {df['faulty'].sum()} ({df['faulty'].sum()/len(df)*100:.1f}%)")
    print(f"   设备类型: {df['equipment_type'].value_counts().to_dict()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成设备故障监控测试数据")
    parser.add_argument("--n-samples", type=int, default=1000, help="样本数量")
    parser.add_argument("--output", type=str, default="equipment_fault_data.csv", help="输出文件名")
    args = parser.parse_args()
    
    generate_fault_data(n_samples=args.n_samples, output_file=args.output)
