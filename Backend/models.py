from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class RoleEnum(str, Enum):
    admin = "admin"
    viewer = "viewer"

class RiskLevelEnum(str, Enum):
    Low = "Low"
    Moderate = "Moderate"
    High = "High"
    Critical = "Critical"

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: RoleEnum = RoleEnum.viewer

class UserInDB(BaseModel):
    id: str = Field(alias="_id")
    name: str
    email: EmailStr
    role: RoleEnum
    createdAt: datetime

class Lake(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    lakeName: str
    latitude: float
    longitude: float
    waterLevel: float
    riskLevel: RiskLevelEnum
    status: str

class EnvironmentData(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    lakeId: str
    temperature: float
    rainfall: float
    waterLevel: float
    glacierMeltRate: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Prediction(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    lakeId: str
    probability: float
    riskLevel: RiskLevelEnum
    recommendation: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Alert(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    lakeId: str
    alertLevel: RiskLevelEnum
    message: str
    status: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)

class FloodHistory(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    lakeId: str
    eventDate: datetime
    severity: str
    affectedArea: float
    description: str
