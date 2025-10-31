"""Fault Detection Machine Learning Model."""

import json
import pickle
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)

from config.settings import get_settings

cfg = get_settings()


class FaultDetector:
    """设备故障检测器"""

    def __init__(self, model_dir: Path | None = None):
        """初始化故障检测器"""
        # 新的ML目录结构：data/ml/models/
        project_root = Path(cfg.data_dir).parent 
        self.model_dir = model_dir or project_root / "ml" / "models"
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        self.model: RandomForestClassifier | None = None
        self.feature_columns = ["temperature", "pressure", "vibration", "humidity"]
        # 注意：CSV中的列名是 "equipment" 而不是 "equipment_type"
        self.categorical_columns = ["equipment", "location"]
        self.model_version = "1.0.0"
        self.equipment_type_mapping: Dict[str, int] = {}
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """准备特征数据"""
        X = df.copy()
        
        # 对分类特征进行编码
        for col in self.categorical_columns:
            if col in X.columns:
                if not self.equipment_type_mapping and col == "equipment":
                    unique_types = X[col].unique()
                    self.equipment_type_mapping = {eq_type: idx for idx, eq_type in enumerate(unique_types)}
                    print(f"📋 设备类型映射: {self.equipment_type_mapping}")
                
                X[col] = X[col].astype("category").cat.codes
                X[col] = X[col].clip(lower=0)
        
        feature_cols = self.feature_columns + [
            col for col in self.categorical_columns if col in X.columns
        ]
        return X[feature_cols]
    
    def train(
        self,
        data_path: str | Path,
        test_size: float = 0.2,
        n_estimators: int = 100,
        max_depth: int = 10,
        random_state: int = 42,
    ) -> Dict[str, Any]:
        """训练故障检测模型"""
        print(f"📖 加载训练数据: {data_path}")
        df = pd.read_csv(data_path)
        print(f"✅ 加载完成: {len(df)} 条记录")
        
        # 分析设备类型分布
        equipment_col = 'equipment' if 'equipment' in df.columns else 'equipment_type'
        if equipment_col in df.columns:
            print(f"\n📋 设备类型分布:")
            for eq_type in df[equipment_col].unique():
                eq_data = df[df[equipment_col] == eq_type]
                faulty_count = eq_data['faulty'].sum()
                total = len(eq_data)
                print(f"   {eq_type}: {total} 个样本, 故障: {faulty_count} ({faulty_count/total*100:.1f}%)")
        
        # 准备特征
        X = self.prepare_features(df)
        y = df["faulty"].values
        
        print(f"\n📊 特征维度: {X.shape}")
        print(f"📊 故障样本: {sum(y)} ({sum(y)/len(y)*100:.1f}%)")
        
        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        print(f"\n🔄 开始训练随机森林模型...")
        print(f"   参数: n_estimators={n_estimators}, max_depth={max_depth}")
        
        # 训练模型
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            class_weight="balanced",
            n_jobs=-1,
        )
        
        self.model.fit(X_train, y_train)
        
        # 评估模型
        print("📈 评估模型性能...")
        y_pred = self.model.predict(X_test)
        
        metrics = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred, zero_division=0)),
            "recall": float(recall_score(y_test, y_pred, zero_division=0)),
            "f1_score": float(f1_score(y_test, y_pred, zero_division=0)),
        }
        
        print(f"\n📊 模型性能:")
        print(f"   准确率: {metrics['accuracy']:.4f}")
        print(f"   精确率: {metrics['precision']:.4f}")
        print(f"   召回率: {metrics['recall']:.4f}")
        print(f"   F1分数: {metrics['f1_score']:.4f}")
        
        # 特征重要性
        feature_importance = dict(
            zip(X.columns, [float(imp) for imp in self.model.feature_importances_])
        )
        metrics["feature_importance"] = feature_importance
        
        print(f"\n🔍 特征重要性:")
        for feature, importance in sorted(feature_importance.items(), key=lambda x: x[1], reverse=True):
            print(f"   {feature}: {importance:.4f}")
        
        # 交叉验证
        print("\n🔄 交叉验证...")
        cv_scores = cross_val_score(self.model, X_train, y_train, cv=5, scoring="f1")
        metrics["cv_mean"] = float(cv_scores.mean())
        metrics["cv_std"] = float(cv_scores.std())
        print(f"   CV F1均值: {metrics['cv_mean']:.4f} (±{metrics['cv_std']:.4f})")
        
        # 保存模型
        model_path = self._save_model(metrics)
        print(f"\n💾 模型已保存: {model_path}")
        
        return {
            "model_version": self.model_version,
            "metrics": metrics,
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "model_path": str(model_path),
            "trained_at": datetime.utcnow().isoformat(),
            "equipment_types": list(self.equipment_type_mapping.keys()) if self.equipment_type_mapping else [],
        }
    
    def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """预测故障概率"""
        if self.model is None:
            raise ValueError("模型未加载，请先调用 load_model() 或 train()")
        
        df = pd.DataFrame([data])
        X = self.prepare_features(df)
        
        probability = self.model.predict_proba(X)[0]
        prediction = self.model.predict(X)[0]
        
        fault_probability = float(probability[1])
        
        return {
            "fault_probability": fault_probability,
            "is_faulty": bool(prediction),
            "confidence": float(max(probability)),
            "model_version": self.model_version,
        }
    
    def batch_predict(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量预测故障概率"""
        if self.model is None:
            raise ValueError("模型未加载，请先调用 load_model() 或 train()")
        
        df = pd.DataFrame(data_list)
        X = self.prepare_features(df)
        
        probabilities = self.model.predict_proba(X)
        predictions = self.model.predict(X)
        
        results = []
        for prob, pred in zip(probabilities, predictions):
            results.append({
                "fault_probability": float(prob[1]),
                "is_faulty": bool(pred),
                "confidence": float(max(prob)),
                "model_version": self.model_version,
            })
        
        return results
    
    def _save_model(self, metrics: Dict[str, Any]) -> Path:
        """保存模型到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_name = f"fault_detector_{timestamp}.pkl"
        model_path = self.model_dir / model_name
        
        with open(model_path, "wb") as f:
            pickle.dump(self.model, f)
        
        metadata = {
            "model_version": self.model_version,
            "model_path": str(model_path),
            "trained_at": datetime.utcnow().isoformat(),
            "metrics": metrics,
            "feature_columns": self.feature_columns,
            "categorical_columns": self.categorical_columns,
            "equipment_type_mapping": self.equipment_type_mapping,
        }
        
        metadata_path = self.model_dir / f"{model_name}.metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return model_path
    
    def load_model(self, model_path: str | Path) -> None:
        """加载模型"""
        with open(model_path, "rb") as f:
            self.model = pickle.load(f)
        
        metadata_path = Path(str(model_path) + ".metadata.json")
        if metadata_path.exists():
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
                self.model_version = metadata.get("model_version", "1.0.0")
                self.feature_columns = metadata.get("feature_columns", self.feature_columns)
                self.categorical_columns = metadata.get("categorical_columns", self.categorical_columns)
                self.equipment_type_mapping = metadata.get("equipment_type_mapping", {})
                print(f"✅ 已加载设备类型映射: {self.equipment_type_mapping}")
