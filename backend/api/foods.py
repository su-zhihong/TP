"""
食物相关 API 接口。
"""
import json
from fastapi import APIRouter, HTTPException
from backend.models.schemas import FoodDetail, FoodGraph, FoodItem
from backend.services.graph_service import search_foods as neo4j_search, get_food_detail, get_food_graph as neo4j_graph
from backend.services.cache_service import get_food_with_fallback, get_cached_or_fetch
from backend.services.stats_service import record_food_query

router = APIRouter(prefix="/api/foods", tags=["食物"])


# 内置食物数据（当 Neo4j 不可用时的 fallback）
BUILTIN_FOODS = [
    {"name": "鸡胸肉", "category": "肉类", "calories_per_100g": 165, "protein": 31, "carbs": 0, "fat": 3.6, "fiber": 0},
    {"name": "瘦牛肉", "category": "肉类", "calories_per_100g": 250, "protein": 26, "carbs": 0, "fat": 15, "fiber": 0},
    {"name": "猪里脊", "category": "肉类", "calories_per_100g": 210, "protein": 25, "carbs": 0, "fat": 11, "fiber": 0},
    {"name": "三文鱼", "category": "海鲜", "calories_per_100g": 208, "protein": 20, "carbs": 0, "fat": 13, "fiber": 0},
    {"name": "虾仁", "category": "海鲜", "calories_per_100g": 99, "protein": 24, "carbs": 0, "fat": 0.3, "fiber": 0},
    {"name": "鸡蛋", "category": "蛋类", "calories_per_100g": 155, "protein": 13, "carbs": 1.1, "fat": 11, "fiber": 0},
    {"name": "脱脂牛奶", "category": "乳制品", "calories_per_100g": 34, "protein": 3.4, "carbs": 5, "fat": 0.1, "fiber": 0},
    {"name": "希腊酸奶", "category": "乳制品", "calories_per_100g": 59, "protein": 10, "carbs": 3.6, "fat": 0.7, "fiber": 0},
    {"name": "豆腐", "category": "豆制品", "calories_per_100g": 76, "protein": 8, "carbs": 2, "fat": 4, "fiber": 0.3},
    {"name": "糙米", "category": "主食", "calories_per_100g": 111, "protein": 2.6, "carbs": 23, "fat": 0.9, "fiber": 1.8},
    {"name": "燕麦", "category": "主食", "calories_per_100g": 389, "protein": 16.9, "carbs": 66, "fat": 6.9, "fiber": 10.6},
    {"name": "红薯", "category": "主食", "calories_per_100g": 86, "protein": 1.6, "carbs": 20, "fat": 0.1, "fiber": 3},
    {"name": "全麦面包", "category": "主食", "calories_per_100g": 247, "protein": 13, "carbs": 41, "fat": 3.4, "fiber": 7},
    {"name": "藜麦", "category": "主食", "calories_per_100g": 120, "protein": 4.4, "carbs": 21, "fat": 1.9, "fiber": 2.8},
    {"name": "荞麦面", "category": "主食", "calories_per_100g": 110, "protein": 4.5, "carbs": 21, "fat": 0.8, "fiber": 2.5},
    {"name": "玉米", "category": "主食", "calories_per_100g": 96, "protein": 3.4, "carbs": 21, "fat": 1.2, "fiber": 2.4},
    {"name": "西兰花", "category": "蔬菜", "calories_per_100g": 34, "protein": 2.8, "carbs": 7, "fat": 0.4, "fiber": 2.6},
    {"name": "菠菜", "category": "蔬菜", "calories_per_100g": 23, "protein": 2.9, "carbs": 3.6, "fat": 0.4, "fiber": 2.2},
    {"name": "黄瓜", "category": "蔬菜", "calories_per_100g": 15, "protein": 0.7, "carbs": 3.6, "fat": 0.1, "fiber": 0.5},
    {"name": "番茄", "category": "蔬菜", "calories_per_100g": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2, "fiber": 1.2},
    {"name": "胡萝卜", "category": "蔬菜", "calories_per_100g": 41, "protein": 0.9, "carbs": 10, "fat": 0.2, "fiber": 2.8},
    {"name": "苹果", "category": "水果", "calories_per_100g": 52, "protein": 0.3, "carbs": 14, "fat": 0.2, "fiber": 2.4},
    {"name": "蓝莓", "category": "水果", "calories_per_100g": 57, "protein": 0.7, "carbs": 14, "fat": 0.3, "fiber": 2.4},
    {"name": "牛油果", "category": "水果", "calories_per_100g": 160, "protein": 2, "carbs": 8.5, "fat": 15, "fiber": 6.7},
    {"name": "香蕉", "category": "水果", "calories_per_100g": 89, "protein": 1.1, "carbs": 23, "fat": 0.3, "fiber": 2.6},
    {"name": "西柚", "category": "水果", "calories_per_100g": 42, "protein": 0.8, "carbs": 11, "fat": 0.1, "fiber": 1.6},
    {"name": "杏仁", "category": "坚果", "calories_per_100g": 579, "protein": 21, "carbs": 22, "fat": 50, "fiber": 12.5},
    {"name": "核桃", "category": "坚果", "calories_per_100g": 654, "protein": 15, "carbs": 14, "fat": 65, "fiber": 6.7},
]


async def _search_foods_with_fallback(keyword: str) -> list:
    """搜索食物：优先从 Neo4j 查询，失败时使用内置数据 fallback。"""
    try:
        results = await neo4j_search(keyword)
        if results:
            return [dict(r) for r in results]
    except Exception:
        pass
    
    keyword_lower = keyword.lower() if keyword else ""
    matched = []
    for food in BUILTIN_FOODS:
        if keyword_lower in food["name"].lower() or keyword_lower in food["category"].lower() or keyword_lower == "":
            matched.append(food)
    return matched[:20]


async def _get_food_detail_with_fallback(name: str) -> dict:
    """获取食物详情：优先从 Neo4j 查询，失败时使用内置数据 fallback。"""
    try:
        result = await get_food_detail(name)
        if result:
            return result
    except Exception:
        pass
    
    for food in BUILTIN_FOODS:
        if food["name"] == name:
            return {**food, "nutrients": []}
    return None


# 内置图谱数据（当 Neo4j 不可用时的 fallback）
# 包含常见食物→营养素、食物→减脂阶段、运动→食物的关系
BUILTIN_GRAPH_DATA = {
    "鸡胸肉": {
        "nodes": [
            {"id": "food_鸡胸肉", "label": "鸡胸肉", "type": "food", "category": "肉类", "calories": 165},
            {"id": "nutrient_蛋白质", "label": "蛋白质", "type": "nutrient", "unit": "g"},
            {"id": "nutrient_脂肪", "label": "脂肪", "type": "nutrient", "unit": "g"},
            {"id": "nutrient_钾", "label": "钾", "type": "nutrient", "unit": "mg"},
            {"id": "nutrient_镁", "label": "镁", "type": "nutrient", "unit": "mg"},
            {"id": "stage_启动期", "label": "启动期", "type": "stage", "description": "开始减脂，减少热量摄入"},
            {"id": "stage_快速减脂期", "label": "快速减脂期", "type": "stage", "description": "持续热量缺口"},
            {"id": "stage_塑形期", "label": "塑形期", "type": "stage", "description": "接近目标体重"},
            {"id": "exercise_跑步", "label": "跑步", "type": "exercise", "calories_per_hour": 600},
            {"id": "exercise_力量训练", "label": "力量训练", "type": "exercise", "calories_per_hour": 350},
        ],
        "edges": [
            {"source": "food_鸡胸肉", "target": "nutrient_蛋白质", "label": "含有", "amount": 31, "unit": "g"},
            {"source": "food_鸡胸肉", "target": "nutrient_脂肪", "label": "含有", "amount": 3.6, "unit": "g"},
            {"source": "food_鸡胸肉", "target": "nutrient_钾", "label": "含有", "amount": 350, "unit": "mg"},
            {"source": "food_鸡胸肉", "target": "nutrient_镁", "label": "含有", "amount": 28, "unit": "mg"},
            {"source": "food_鸡胸肉", "target": "stage_启动期", "label": "适合"},
            {"source": "food_鸡胸肉", "target": "stage_快速减脂期", "label": "适合"},
            {"source": "food_鸡胸肉", "target": "stage_塑形期", "label": "适合"},
            {"source": "exercise_跑步", "target": "food_鸡胸肉", "label": "消耗"},
            {"source": "exercise_力量训练", "target": "food_鸡胸肉", "label": "消耗"},
        ]
    },
    "三文鱼": {
        "nodes": [
            {"id": "food_三文鱼", "label": "三文鱼", "type": "food", "category": "海鲜", "calories": 208},
            {"id": "nutrient_蛋白质", "label": "蛋白质", "type": "nutrient", "unit": "g"},
            {"id": "nutrient_脂肪", "label": "脂肪", "type": "nutrient", "unit": "g"},
            {"id": "nutrient_维生素B族", "label": "维生素B族", "type": "nutrient", "unit": "mg"},
            {"id": "nutrient_钙", "label": "钙", "type": "nutrient", "unit": "mg"},
            {"id": "stage_快速减脂期", "label": "快速减脂期", "type": "stage"},
            {"id": "stage_塑形期", "label": "塑形期", "type": "stage"},
            {"id": "exercise_游泳", "label": "游泳", "type": "exercise", "calories_per_hour": 500},
        ],
        "edges": [
            {"source": "food_三文鱼", "target": "nutrient_蛋白质", "label": "含有", "amount": 20, "unit": "g"},
            {"source": "food_三文鱼", "target": "nutrient_脂肪", "label": "含有", "amount": 13, "unit": "g"},
            {"source": "food_三文鱼", "target": "nutrient_维生素B族", "label": "含有", "amount": 5.8, "unit": "mg"},
            {"source": "food_三文鱼", "target": "nutrient_钙", "label": "含有", "amount": 15, "unit": "mg"},
            {"source": "food_三文鱼", "target": "stage_快速减脂期", "label": "适合"},
            {"source": "food_三文鱼", "target": "stage_塑形期", "label": "适合"},
            {"source": "exercise_游泳", "target": "food_三文鱼", "label": "消耗"},
        ]
    },
    "鸡蛋": {
        "nodes": [
            {"id": "food_鸡蛋", "label": "鸡蛋", "type": "food", "category": "蛋类", "calories": 155},
            {"id": "nutrient_蛋白质", "label": "蛋白质", "type": "nutrient", "unit": "g"},
            {"id": "nutrient_脂肪", "label": "脂肪", "type": "nutrient", "unit": "g"},
            {"id": "nutrient_维生素B族", "label": "维生素B族", "type": "nutrient", "unit": "mg"},
            {"id": "nutrient_铁", "label": "铁", "type": "nutrient", "unit": "mg"},
            {"id": "stage_启动期", "label": "启动期", "type": "stage"},
            {"id": "stage_快速减脂期", "label": "快速减脂期", "type": "stage"},
            {"id": "stage_塑形期", "label": "塑形期", "type": "stage"},
            {"id": "exercise_力量训练", "label": "力量训练", "type": "exercise", "calories_per_hour": 350},
        ],
        "edges": [
            {"source": "food_鸡蛋", "target": "nutrient_蛋白质", "label": "含有", "amount": 13, "unit": "g"},
            {"source": "food_鸡蛋", "target": "nutrient_脂肪", "label": "含有", "amount": 11, "unit": "g"},
            {"source": "food_鸡蛋", "target": "nutrient_维生素B族", "label": "含有", "amount": 0.6, "unit": "mg"},
            {"source": "food_鸡蛋", "target": "nutrient_铁", "label": "含有", "amount": 1.8, "unit": "mg"},
            {"source": "food_鸡蛋", "target": "stage_启动期", "label": "适合"},
            {"source": "food_鸡蛋", "target": "stage_快速减脂期", "label": "适合"},
            {"source": "food_鸡蛋", "target": "stage_塑形期", "label": "适合"},
            {"source": "exercise_力量训练", "target": "food_鸡蛋", "label": "消耗"},
        ]
    },
    "糙米": {
        "nodes": [
            {"id": "food_糙米", "label": "糙米", "type": "food", "category": "主食", "calories": 111},
            {"id": "nutrient_碳水化合物", "label": "碳水化合物", "type": "nutrient", "unit": "g"},
            {"id": "nutrient_膳食纤维", "label": "膳食纤维", "type": "nutrient", "unit": "g"},
            {"id": "nutrient_镁", "label": "镁", "type": "nutrient", "unit": "mg"},
            {"id": "stage_启动期", "label": "启动期", "type": "stage"},
            {"id": "stage_快速减脂期", "label": "快速减脂期", "type": "stage"},
            {"id": "stage_维持期", "label": "维持期", "type": "stage"},
            {"id": "exercise_骑行", "label": "骑行", "type": "exercise", "calories_per_hour": 450},
        ],
        "edges": [
            {"source": "food_糙米", "target": "nutrient_碳水化合物", "label": "含有", "amount": 23, "unit": "g"},
            {"source": "food_糙米", "target": "nutrient_膳食纤维", "label": "含有", "amount": 1.8, "unit": "g"},
            {"source": "food_糙米", "target": "nutrient_镁", "label": "含有", "amount": 43, "unit": "mg"},
            {"source": "food_糙米", "target": "stage_启动期", "label": "适合"},
            {"source": "food_糙米", "target": "stage_快速减脂期", "label": "适合"},
            {"source": "food_糙米", "target": "stage_维持期", "label": "适合"},
            {"source": "exercise_骑行", "target": "food_糙米", "label": "消耗"},
        ]
    },
    "西兰花": {
        "nodes": [
            {"id": "food_西兰花", "label": "西兰花", "type": "food", "category": "蔬菜", "calories": 34},
            {"id": "nutrient_膳食纤维", "label": "膳食纤维", "type": "nutrient", "unit": "g"},
            {"id": "nutrient_维生素C", "label": "维生素C", "type": "nutrient", "unit": "mg"},
            {"id": "nutrient_钙", "label": "钙", "type": "nutrient", "unit": "mg"},
            {"id": "nutrient_钾", "label": "钾", "type": "nutrient", "unit": "mg"},
            {"id": "stage_启动期", "label": "启动期", "type": "stage"},
            {"id": "stage_快速减脂期", "label": "快速减脂期", "type": "stage"},
            {"id": "stage_平台期", "label": "平台期", "type": "stage"},
            {"id": "stage_塑形期", "label": "塑形期", "type": "stage"},
            {"id": "exercise_跑步", "label": "跑步", "type": "exercise", "calories_per_hour": 600},
        ],
        "edges": [
            {"source": "food_西兰花", "target": "nutrient_膳食纤维", "label": "含有", "amount": 2.6, "unit": "g"},
            {"source": "food_西兰花", "target": "nutrient_维生素C", "label": "含有", "amount": 89, "unit": "mg"},
            {"source": "food_西兰花", "target": "nutrient_钙", "label": "含有", "amount": 47, "unit": "mg"},
            {"source": "food_西兰花", "target": "nutrient_钾", "label": "含有", "amount": 316, "unit": "mg"},
            {"source": "food_西兰花", "target": "stage_启动期", "label": "适合"},
            {"source": "food_西兰花", "target": "stage_快速减脂期", "label": "适合"},
            {"source": "food_西兰花", "target": "stage_平台期", "label": "适合"},
            {"source": "food_西兰花", "target": "stage_塑形期", "label": "适合"},
            {"source": "exercise_跑步", "target": "food_西兰花", "label": "消耗"},
        ]
    },
    "牛油果": {
        "nodes": [
            {"id": "food_牛油果", "label": "牛油果", "type": "food", "category": "水果", "calories": 160},
            {"id": "nutrient_脂肪", "label": "脂肪", "type": "nutrient", "unit": "g"},
            {"id": "nutrient_膳食纤维", "label": "膳食纤维", "type": "nutrient", "unit": "g"},
            {"id": "nutrient_钾", "label": "钾", "type": "nutrient", "unit": "mg"},
            {"id": "stage_塑形期", "label": "塑形期", "type": "stage"},
            {"id": "stage_维持期", "label": "维持期", "type": "stage"},
            {"id": "exercise_游泳", "label": "游泳", "type": "exercise", "calories_per_hour": 500},
        ],
        "edges": [
            {"source": "food_牛油果", "target": "nutrient_脂肪", "label": "含有", "amount": 15, "unit": "g"},
            {"source": "food_牛油果", "target": "nutrient_膳食纤维", "label": "含有", "amount": 6.7, "unit": "g"},
            {"source": "food_牛油果", "target": "nutrient_钾", "label": "含有", "amount": 485, "unit": "mg"},
            {"source": "food_牛油果", "target": "stage_塑形期", "label": "适合"},
            {"source": "food_牛油果", "target": "stage_维持期", "label": "适合"},
            {"source": "exercise_游泳", "target": "food_牛油果", "label": "消耗"},
        ]
    },
    "燕麦": {
        "nodes": [
            {"id": "food_燕麦", "label": "燕麦", "type": "food", "category": "主食", "calories": 389},
            {"id": "nutrient_碳水化合物", "label": "碳水化合物", "type": "nutrient", "unit": "g"},
            {"id": "nutrient_膳食纤维", "label": "膳食纤维", "type": "nutrient", "unit": "g"},
            {"id": "nutrient_蛋白质", "label": "蛋白质", "type": "nutrient", "unit": "g"},
            {"id": "stage_启动期", "label": "启动期", "type": "stage"},
            {"id": "stage_快速减脂期", "label": "快速减脂期", "type": "stage"},
            {"id": "exercise_骑行", "label": "骑行", "type": "exercise", "calories_per_hour": 450},
        ],
        "edges": [
            {"source": "food_燕麦", "target": "nutrient_碳水化合物", "label": "含有", "amount": 66, "unit": "g"},
            {"source": "food_燕麦", "target": "nutrient_膳食纤维", "label": "含有", "amount": 10.6, "unit": "g"},
            {"source": "food_燕麦", "target": "nutrient_蛋白质", "label": "含有", "amount": 16.9, "unit": "g"},
            {"source": "food_燕麦", "target": "stage_启动期", "label": "适合"},
            {"source": "food_燕麦", "target": "stage_快速减脂期", "label": "适合"},
            {"source": "exercise_骑行", "target": "food_燕麦", "label": "消耗"},
        ]
    },
    "虾仁": {
        "nodes": [
            {"id": "food_虾仁", "label": "虾仁", "type": "food", "category": "海鲜", "calories": 99},
            {"id": "nutrient_蛋白质", "label": "蛋白质", "type": "nutrient", "unit": "g"},
            {"id": "nutrient_钙", "label": "钙", "type": "nutrient", "unit": "mg"},
            {"id": "nutrient_镁", "label": "镁", "type": "nutrient", "unit": "mg"},
            {"id": "stage_启动期", "label": "启动期", "type": "stage"},
            {"id": "stage_快速减脂期", "label": "快速减脂期", "type": "stage"},
            {"id": "exercise_HIIT", "label": "HIIT", "type": "exercise", "calories_per_hour": 700},
        ],
        "edges": [
            {"source": "food_虾仁", "target": "nutrient_蛋白质", "label": "含有", "amount": 24, "unit": "g"},
            {"source": "food_虾仁", "target": "nutrient_钙", "label": "含有", "amount": 120, "unit": "mg"},
            {"source": "food_虾仁", "target": "nutrient_镁", "label": "含有", "amount": 43, "unit": "mg"},
            {"source": "food_虾仁", "target": "stage_启动期", "label": "适合"},
            {"source": "food_虾仁", "target": "stage_快速减脂期", "label": "适合"},
            {"source": "exercise_HIIT", "target": "food_虾仁", "label": "消耗"},
        ]
    },
}


async def _get_food_graph_with_fallback(name: str) -> dict:
    """
    获取知识图谱子图：优先从 Neo4j 查询，失败时使用内置图谱数据 fallback。
    """
    try:
        result = await neo4j_graph(name)
        if result and result.get("nodes"):
            return result
    except Exception:
        pass
    
    # Fallback: 使用内置图谱数据
    if name in BUILTIN_GRAPH_DATA:
        return BUILTIN_GRAPH_DATA[name]
    
    # 通用图谱：对没有预设图谱的食物生成简化图谱
    for food in BUILTIN_FOODS:
        if food["name"] == name:
            nodes = [
                {"id": f"food_{name}", "label": name, "type": "food", "category": food["category"], "calories": food["calories_per_100g"]},
                {"id": "nutrient_蛋白质", "label": "蛋白质", "type": "nutrient", "unit": "g"},
                {"id": "nutrient_碳水化合物", "label": "碳水化合物", "type": "nutrient", "unit": "g"},
                {"id": "nutrient_脂肪", "label": "脂肪", "type": "nutrient", "unit": "g"},
                {"id": "exercise_跑步", "label": "跑步", "type": "exercise", "calories_per_hour": 600},
            ]
            edges = [
                {"source": f"food_{name}", "target": "nutrient_蛋白质", "label": "含有", "amount": food["protein"], "unit": "g"},
                {"source": f"food_{name}", "target": "nutrient_碳水化合物", "label": "含有", "amount": food["carbs"], "unit": "g"},
                {"source": f"food_{name}", "target": "nutrient_脂肪", "label": "含有", "amount": food["fat"], "unit": "g"},
                {"source": "exercise_跑步", "target": f"food_{name}", "label": "消耗"},
            ]
            return {"nodes": nodes, "edges": edges}
    
    return {"nodes": [], "edges": []}


@router.get("")
async def search_foods_api(keyword: str = ""):
    """
    搜索食物列表。
    缓存策略：缓存 5 分钟。
    """
    async def fetch():
        return await _search_foods_with_fallback(keyword)

    cache_key = f"food_search:{keyword}"
    data = await get_cached_or_fetch(cache_key, fetch, ttl=300)
    
    if data is None:
        data = []
    
    return {"data": data, "total": len(data)}


@router.get("/{name}")
async def get_food_detail_api(name: str):
    """
    获取食物详情（含营养素）。
    缓存策略：强缓存 + 防击穿 + 随机 TTL。
    """
    async def fetch():
        return await _get_food_detail_with_fallback(name)

    data = await get_food_with_fallback(
        name,
        fetch,
        cache_key_prefix="food_detail",
        min_ttl=300,
        max_ttl=600
    )
    
    if data is None:
        raise HTTPException(status_code=404, detail=f"食物 '{name}' 不存在")
    
    # 记录查询次数（原子计数）
    await record_food_query(name)
    
    return {"data": data}


@router.get("/{name}/graph")
async def get_food_graph_api(name: str):
    """
    获取知识图谱子图（nodes + edges）。
    缓存策略：缓存 10 分钟。
    """
    async def fetch():
        return await _get_food_graph_with_fallback(name)

    cache_key = f"food_graph:{name}"
    data = await get_cached_or_fetch(cache_key, fetch, ttl=600)
    
    return {"data": data}