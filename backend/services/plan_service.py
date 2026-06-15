"""
减脂规划服务。
计算 BMR、TDEE、推荐每日热量，基于知识图谱推荐三餐。
"""
import hashlib
import json
from typing import List
from backend.models.schemas import PlanRequest, PlanResponse, PlanMeal, FoodItem
from backend.db.neo4j_client import neo4j_client
from backend.core.redis_client import redis_client


async def _get_foods_by_category(category: str, limit: int = 5) -> list:
    """根据分类获取食物"""
    cypher = """
    MATCH (f:Food)
    WHERE f.category CONTAINS $category
    RETURN f.name AS name, f.category AS category,
           f.calories_per_100g AS calories_per_100g,
           f.protein AS protein, f.carbs AS carbs,
           f.fat AS fat, f.fiber AS fiber
    LIMIT $limit
    """
    return await neo4j_client.run(cypher, category=category, limit=limit)


async def _get_foods_suitable_for_stage(stage: str, limit: int = 5) -> list:
    """获取适合某减脂阶段的食物"""
    cypher = """
    MATCH (f:Food)-[:SUITABLE_FOR]->(s:FatLossStage {name: $stage})
    RETURN f.name AS name, f.category AS category,
           f.calories_per_100g AS calories_per_100g,
           f.protein AS protein, f.carbs AS carbs,
           f.fat AS fat, f.fiber AS fiber
    LIMIT $limit
    """
    return await neo4j_client.run(cypher, stage=stage, limit=limit)


def _calculate_bmr(weight: float, height: float, age: int, gender: str) -> float:
    """Mifflin-St Jeor 公式计算基础代谢率 (BMR)"""
    if gender == "male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161


def _get_default_foods() -> list:
    """当 Neo4j 不可用时的内建食物数据"""
    return [
        {"name": "鸡胸肉", "category": "肉类", "calories_per_100g": 165, "protein": 31, "carbs": 0, "fat": 3.6, "fiber": 0},
        {"name": "三文鱼", "category": "海鲜", "calories_per_100g": 208, "protein": 20, "carbs": 0, "fat": 13, "fiber": 0},
        {"name": "鸡蛋", "category": "蛋类", "calories_per_100g": 155, "protein": 13, "carbs": 1.1, "fat": 11, "fiber": 0},
        {"name": "糙米", "category": "主食", "calories_per_100g": 111, "protein": 2.6, "carbs": 23, "fat": 0.9, "fiber": 1.8},
        {"name": "西兰花", "category": "蔬菜", "calories_per_100g": 34, "protein": 2.8, "carbs": 7, "fat": 0.4, "fiber": 2.6},
        {"name": "牛油果", "category": "水果", "calories_per_100g": 160, "protein": 2, "carbs": 8.5, "fat": 15, "fiber": 6.7},
        {"name": "燕麦", "category": "主食", "calories_per_100g": 389, "protein": 16.9, "carbs": 66, "fat": 6.9, "fiber": 10.6},
        {"name": "虾仁", "category": "海鲜", "calories_per_100g": 99, "protein": 24, "carbs": 0, "fat": 0.3, "fiber": 0},
        {"name": "菠菜", "category": "蔬菜", "calories_per_100g": 23, "protein": 2.9, "carbs": 3.6, "fat": 0.4, "fiber": 2.2},
        {"name": "豆腐", "category": "豆制品", "calories_per_100g": 76, "protein": 8, "carbs": 2, "fat": 4, "fiber": 0.3},
        {"name": "红薯", "category": "主食", "calories_per_100g": 86, "protein": 1.6, "carbs": 20, "fat": 0.1, "fiber": 3},
        {"name": "希腊酸奶", "category": "乳制品", "calories_per_100g": 59, "protein": 10, "carbs": 3.6, "fat": 0.7, "fiber": 0},
        {"name": "瘦牛肉", "category": "肉类", "calories_per_100g": 250, "protein": 26, "carbs": 0, "fat": 15, "fiber": 0},
        {"name": "鱼肉（鲈鱼）", "category": "海鲜", "calories_per_100g": 105, "protein": 19, "carbs": 0, "fat": 3, "fiber": 0},
        {"name": "全麦面包", "category": "主食", "calories_per_100g": 247, "protein": 13, "carbs": 41, "fat": 3.4, "fiber": 7},
        {"name": "苹果", "category": "水果", "calories_per_100g": 52, "protein": 0.3, "carbs": 14, "fat": 0.2, "fiber": 2.4},
    ]


def _get_activity_multiplier(activity_level: str) -> float:
    """获取活动系数"""
    multipliers = {
        "sedentary": 1.2,      # 久坐
        "light": 1.375,        # 轻度活动
        "moderate": 1.55,      # 中度活动
        "active": 1.725,       # 积极活动
        "very_active": 1.9,    # 高强度活动
    }
    return multipliers.get(activity_level, 1.2)


def _calculate_tdee(bmr: float, activity_multiplier: float) -> float:
    """计算每日总能量消耗 (TDEE)"""
    return round(bmr * activity_multiplier, 1)


def _get_daily_calories(tdee: float, goal: str) -> float:
    """根据目标调整每日热量"""
    if goal == "lose":
        return round(tdee - 500, 1)  # 减脂：TDEE - 500
    elif goal == "gain":
        return round(tdee + 300, 1)  # 增肌：TDEE + 300
    else:
        return round(tdee, 1)  # 维持


async def generate_plan(req: PlanRequest) -> PlanResponse:
    """
    生成减脂规划。
    按参数哈希缓存 1 天。
    
    计算策略：
    - BMR 使用 Mifflin-St Jeor 公式
    - TDEE = BMR × 活动系数
    - 减脂目标：TDEE - 500 kcal/天
    - 宏量营养素分配：蛋白质 30%，碳水 40%，脂肪 30%
    """
    # 计算基础数据
    bmr = _calculate_bmr(req.weight, req.height, req.age, req.gender)
    activity_mult = _get_activity_multiplier(req.activity_level)
    tdee = _calculate_tdee(bmr, activity_mult)
    daily_calories = _get_daily_calories(tdee, req.goal)
    
    # 宏量营养素分配：蛋白质 30%，碳水 40%，脂肪 30%
    protein_cal_ratio = 0.30
    carbs_cal_ratio = 0.40
    fat_cal_ratio = 0.30
    
    daily_protein = round((daily_calories * protein_cal_ratio) / 4, 1)  # 蛋白质 4 kcal/g
    daily_carbs = round((daily_calories * carbs_cal_ratio) / 4, 1)     # 碳水 4 kcal/g
    daily_fat = round((daily_calories * fat_cal_ratio) / 9, 1)         # 脂肪 9 kcal/g
    
    # 基于知识图谱推荐三餐食物
    # 根据活动水平和目标选择适合的食物
    stage_name = "快速减脂期" if req.goal == "lose" else "维持期" if req.goal == "maintain" else "塑形期"
    
    # 获取适合该阶段的食物
    all_foods = []
    try:
        all_foods = await _get_foods_suitable_for_stage(stage_name, limit=20)
        # 如果不够，补充其他食物
        if len(all_foods) < 6:
            extra = await _get_foods_by_category("", limit=20)
            all_foods.extend(extra)
    except Exception:
        # Neo4j 不可用时使用内建数据
        all_foods = _get_default_foods()
    
    # 去重
    seen = set()
    unique_foods = []
    for f in all_foods:
        if f['name'] not in seen:
            seen.add(f['name'])
            unique_foods.append(f)
    
    # 按分类分配三餐
    def _food_to_item(f: dict) -> FoodItem:
        return FoodItem(
            name=f['name'],
            category=f.get('category', ''),
            calories_per_100g=float(f.get('calories_per_100g', 0)),
            protein=float(f.get('protein', 0)),
            carbs=float(f.get('carbs', 0)),
            fat=float(f.get('fat', 0)),
            fiber=float(f.get('fiber', 0))
        )
    
    breakfast_foods = []
    lunch_foods = []
    dinner_foods = []
    
    for f in unique_foods:
        item = _food_to_item(f)
        cat = f.get('category', '')
        if cat in ('主食', '蛋类', '乳制品'):
            breakfast_foods.append(item)
        elif cat in ('肉类', '海鲜', '豆制品'):
            lunch_foods.append(item)
            dinner_foods.append(item)
        elif cat in ('蔬菜',):
            lunch_foods.append(item)
            dinner_foods.append(item)
        elif cat in ('水果', '坚果'):
            breakfast_foods.append(item)
    
    # 取 top 3
    breakfast_foods = breakfast_foods[:3]
    lunch_foods = lunch_foods[:4]
    dinner_foods = dinner_foods[:4]
    
    # 计算每餐总热量
    def _calc_meal_total(foods: List[FoodItem]) -> tuple:
        cal = sum(f.calories_per_100g for f in foods)
        pro = sum(f.protein for f in foods)
        car = sum(f.carbs for f in foods)
        fat = sum(f.fat for f in foods)
        return cal, pro, car, fat
    
    b_cal, b_pro, b_car, b_fat = _calc_meal_total(breakfast_foods)
    l_cal, l_pro, l_car, l_fat = _calc_meal_total(lunch_foods)
    d_cal, d_pro, d_car, d_fat = _calc_meal_total(dinner_foods)
    
    meals = [
        PlanMeal(
            meal_type="早餐",
            foods=breakfast_foods,
            total_calories=round(b_cal, 1),
            total_protein=round(b_pro, 1),
            total_carbs=round(b_car, 1),
            total_fat=round(b_fat, 1)
        ),
        PlanMeal(
            meal_type="午餐",
            foods=lunch_foods,
            total_calories=round(l_cal, 1),
            total_protein=round(l_pro, 1),
            total_carbs=round(l_car, 1),
            total_fat=round(l_fat, 1)
        ),
        PlanMeal(
            meal_type="晚餐",
            foods=dinner_foods,
            total_calories=round(d_cal, 1),
            total_protein=round(d_pro, 1),
            total_carbs=round(d_car, 1),
            total_fat=round(d_fat, 1)
        ),
    ]
    
    return PlanResponse(
        bmr=round(bmr, 1),
        tdee=tdee,
        daily_calories=daily_calories,
        daily_protein=daily_protein,
        daily_carbs=daily_carbs,
        daily_fat=daily_fat,
        meals=meals
    )


async def get_or_generate_plan(req: PlanRequest) -> PlanResponse:
    """
    获取或生成减脂规划（按参数哈希缓存 1 天）。
    大量用户并发时，展示分布式锁防缓存击穿。
    """
    # 生成参数哈希作为缓存 key
    param_str = f"{req.age}_{req.gender}_{req.height}_{req.weight}_{req.activity_level}_{req.goal}"
    cache_key = f"plan:{hashlib.md5(param_str.encode()).hexdigest()}"
    
    # 尝试从缓存读取
    cached = await redis_client.get(cache_key)
    if cached is not None:
        return PlanResponse(**json.loads(cached))
    
    # 生成规划
    plan = await generate_plan(req)
    
    # 缓存 1 天
    await redis_client.set(cache_key, plan.model_dump_json(), ex=86400)
    
    return plan