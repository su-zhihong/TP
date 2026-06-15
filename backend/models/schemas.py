"""
Pydantic 数据模型定义。
"""
from pydantic import BaseModel, Field
from typing import Optional, List


# ---- 食物 ----

class FoodItem(BaseModel):
    name: str
    category: str = ""
    calories_per_100g: float = 0
    protein: float = 0
    carbs: float = 0
    fat: float = 0
    fiber: float = 0

class FoodDetail(FoodItem):
    nutrients: List[dict] = []

class FoodGraph(BaseModel):
    nodes: list = []
    edges: list = []


# ---- 问答 ----

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str
    sources: List[str] = []


# ---- 减脂规划 ----

class PlanRequest(BaseModel):
    age: int = Field(..., ge=10, le=100, description="年龄")
    gender: str = Field(..., pattern="^(male|female)$", description="性别 male/female")
    height: float = Field(..., ge=100, le=250, description="身高 cm")
    weight: float = Field(..., ge=30, le=300, description="体重 kg")
    activity_level: str = Field(
        ..., pattern="^(sedentary|light|moderate|active|very_active)$",
        description="活动水平: sedentary/light/moderate/active/very_active"
    )
    goal: str = Field(
        ..., pattern="^(lose|maintain|gain)$",
        description="减脂目标: lose/maintain/gain"
    )

class PlanMeal(BaseModel):
    meal_type: str  # breakfast, lunch, dinner, snack
    foods: List[FoodItem] = []
    total_calories: float = 0
    total_protein: float = 0
    total_carbs: float = 0
    total_fat: float = 0

class PlanResponse(BaseModel):
    bmr: float
    tdee: float
    daily_calories: float
    daily_protein: float
    daily_carbs: float
    daily_fat: float
    meals: List[PlanMeal] = []


# ---- 热门排行榜 ----

class HotFoodItem(BaseModel):
    name: str
    query_count: int

class HotFoodsResponse(BaseModel):
    foods: List[HotFoodItem] = []


# ---- 刷新缓存 ----

class RefreshCacheResponse(BaseModel):
    message: str
    success: bool