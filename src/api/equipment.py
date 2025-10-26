"""Equipment Monitoring API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.api.db import get_db
from src.api.models import User, Equipment, SensorData, FaultPrediction, MLModel
from src.api.auth import get_current_user
from src.ml.fault_detector import FaultDetector

router = APIRouter(prefix="/api/equipment", tags=["equipment"])


# Request/Response Models
class SensorDataCreate(BaseModel):
    """传感器数据创建模型"""
    equipment_id: int
    temperature: float
    pressure: float
    vibration: float
    humidity: float
    recorded_at: Optional[datetime] = None
    is_faulty: Optional[bool] = None


class SensorDataResponse(BaseModel):
    """传感器数据响应模型"""
    id: int
    equipment_id: int
    temperature: float
    pressure: float
    vibration: float
    humidity: float
    recorded_at: datetime
    is_faulty: Optional[bool]
    created_at: datetime

    class Config:
        from_attributes = True


class PredictRequest(BaseModel):
    """预测请求模型"""
    temperature: float = Field(..., description="温度")
    pressure: float = Field(..., description="压力")
    vibration: float = Field(..., description="振动")
    humidity: float = Field(..., description="湿度")
    equipment_type: Optional[str] = None
    location: Optional[str] = None


class PredictResponse(BaseModel):
    """预测响应模型"""
    fault_probability: float
    is_faulty: bool
    confidence: float
    model_version: str


class EquipmentResponse(BaseModel):
    """设备响应模型"""
    id: int
    equipment_type: str
    location: str
    description: Optional[str]
    is_active: bool
    installation_date: Optional[datetime]
    last_maintenance: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class FaultPredictionResponse(BaseModel):
    """故障预测响应模型"""
    id: int
    equipment_id: int
    fault_probability: float
    predicted_fault_type: Optional[str]
    model_version: str
    confidence: Optional[float]
    predicted_at: datetime
    is_confirmed: bool

    class Config:
        from_attributes = True


# Singleton fault detector instance
_fault_detector: Optional[FaultDetector] = None


def get_fault_detector() -> FaultDetector:
    """获取故障检测器单例"""
    global _fault_detector
    if _fault_detector is None:
        _fault_detector = FaultDetector()
        # 尝试加载最新的模型
        from pathlib import Path
        model_dir = Path("data/ml_models")
        if model_dir.exists():
            models = sorted(model_dir.glob("fault_detector_*.pkl"))
            if models:
                _fault_detector.load_model(models[-1])
                print(f"✅ 已加载模型: {models[-1]}")
    return _fault_detector


@router.post("/sensor-data", response_model=SensorDataResponse)
def create_sensor_data(
    data: SensorDataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建传感器数据"""
    equipment = db.query(Equipment).filter(Equipment.id == data.equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="设备不存在")
    
    sensor_data = SensorData(
        equipment_id=data.equipment_id,
        temperature=data.temperature,
        pressure=data.pressure,
        vibration=data.vibration,
        humidity=data.humidity,
        recorded_at=data.recorded_at or datetime.utcnow(),
        is_faulty=data.is_faulty,
    )
    
    db.add(sensor_data)
    db.commit()
    db.refresh(sensor_data)
    
    return sensor_data


@router.get("/sensor-data", response_model=List[SensorDataResponse])
def get_sensor_data(
    equipment_id: Optional[int] = Query(None, description="设备ID"),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取传感器数据列表"""
    query = db.query(SensorData)
    
    if equipment_id:
        query = query.filter(SensorData.equipment_id == equipment_id)
    
    query = query.order_by(SensorData.recorded_at.desc())
    sensor_data = query.offset(offset).limit(limit).all()
    
    return sensor_data


@router.post("/predict", response_model=PredictResponse)
def predict_fault(
    request: PredictRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """预测设备故障"""
    try:
        detector = get_fault_detector()
        
        predict_data = {
            "temperature": request.temperature,
            "pressure": request.pressure,
            "vibration": request.vibration,
            "humidity": request.humidity,
        }
        
        if request.equipment_type:
            predict_data["equipment_type"] = request.equipment_type
        if request.location:
            predict_data["location"] = request.location
        
        result = detector.predict(predict_data)
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"预测失败: {str(e)}")


@router.post("/predict-batch", response_model=List[Dict[str, Any]])
def predict_fault_batch(
    requests: List[PredictRequest],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """批量预测设备故障"""
    try:
        detector = get_fault_detector()
        
        predict_data_list = []
        for req in requests:
            predict_data = {
                "temperature": req.temperature,
                "pressure": req.pressure,
                "vibration": req.vibration,
                "humidity": req.humidity,
            }
            if req.equipment_type:
                predict_data["equipment_type"] = req.equipment_type
            if req.location:
                predict_data["location"] = req.location
            predict_data_list.append(predict_data)
        
        results = detector.batch_predict(predict_data_list)
        
        return results
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"批量预测失败: {str(e)}")


@router.get("/equipment", response_model=List[EquipmentResponse])
def get_equipment(
    equipment_type: Optional[str] = Query(None, description="设备类型"),
    location: Optional[str] = Query(None, description="位置"),
    is_active: Optional[bool] = Query(None, description="是否激活"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取设备列表"""
    query = db.query(Equipment)
    
    if equipment_type:
        query = query.filter(Equipment.equipment_type == equipment_type)
    if location:
        query = query.filter(Equipment.location == location)
    if is_active is not None:
        query = query.filter(Equipment.is_active == is_active)
    
    equipment_list = query.all()
    return equipment_list


@router.get("/fault-predictions", response_model=List[FaultPredictionResponse])
def get_fault_predictions(
    equipment_id: Optional[int] = Query(None, description="设备ID"),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取故障预测列表"""
    query = db.query(FaultPrediction)
    
    if equipment_id:
        query = query.filter(FaultPrediction.equipment_id == equipment_id)
    
    query = query.order_by(FaultPrediction.predicted_at.desc())
    predictions = query.offset(offset).limit(limit).all()
    
    return predictions


@router.get("/stats")
def get_equipment_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取设备统计信息"""
    total_equipment = db.query(Equipment).count()
    active_equipment = db.query(Equipment).filter(Equipment.is_active == True).count()
    total_sensor_data = db.query(SensorData).count()
    faulty_count = db.query(SensorData).filter(SensorData.is_faulty == True).count()
    
    return {
        "total_equipment": total_equipment,
        "active_equipment": active_equipment,
        "total_sensor_data": total_sensor_data,
        "faulty_count": faulty_count,
        "faulty_rate": (faulty_count / total_sensor_data * 100) if total_sensor_data > 0 else 0,
    }
