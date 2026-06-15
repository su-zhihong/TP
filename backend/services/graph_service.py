"""
Neo4j 图数据库查询服务。
"""
from typing import Optional, List
from backend.db.neo4j_client import neo4j_client


async def search_foods(keyword: str) -> list:
    """搜索食物列表"""
    cypher = """
    MATCH (f:Food)
    WHERE f.name CONTAINS $keyword
    RETURN f.name AS name, f.category AS category, 
           f.calories_per_100g AS calories_per_100g,
           f.protein AS protein, f.carbs AS carbs, 
           f.fat AS fat, f.fiber AS fiber
    LIMIT 20
    """
    results = await neo4j_client.run(cypher, keyword=keyword)
    return results


async def get_food_detail(name: str) -> Optional[dict]:
    """获取食物详情（含营养素关联）"""
    cypher = """
    MATCH (f:Food {name: $name})
    OPTIONAL MATCH (f)-[r:CONTAINS]->(n:Nutrient)
    RETURN f.name AS name, f.category AS category,
           f.calories_per_100g AS calories_per_100g,
           f.protein AS protein, f.carbs AS carbs,
           f.fat AS fat, f.fiber AS fiber,
           COLLECT({
               nutrient: n.name,
               amount: r.amount_per_100g,
               unit: r.unit
           }) AS nutrients
    """
    results = await neo4j_client.run(cypher, name=name)
    return results[0] if results else None


async def get_food_graph(name: str) -> dict:
    """获取知识图谱子图（食物及其关联的营养素、减脂阶段）"""
    cypher = """
    MATCH (f:Food {name: $name})
    OPTIONAL MATCH (f)-[r1:CONTAINS]->(n:Nutrient)
    OPTIONAL MATCH (f)-[r2:SUITABLE_FOR]->(s:FatLossStage)
    OPTIONAL MATCH (f)<-[r3:BURNS]-(e:Exercise)
    RETURN f, COLLECT(DISTINCT {type: 'nutrient', node: n, rel: r1}) AS nutrients,
           COLLECT(DISTINCT {type: 'stage', node: s, rel: r2}) AS stages,
           COLLECT(DISTINCT {type: 'exercise', node: e, rel: r3}) AS exercises
    """
    results = await neo4j_client.run(cypher, name=name)
    if not results or not results[0].get('f'):
        return {"nodes": [], "edges": []}

    record = results[0]
    food = record['f']
    nodes = []
    edges = []

    # 添加食物节点
    food_id = f"food_{food['name']}"
    nodes.append({
        "id": food_id,
        "label": food['name'],
        "type": "food",
        "category": food.get('category', ''),
        "calories": food.get('calories_per_100g', 0)
    })

    # 添加营养素节点和边
    for item in record.get('nutrients', []):
        n = item['node']
        rel = item['rel']
        if n:
            nut_id = f"nutrient_{n['name']}"
            nodes.append({
                "id": nut_id,
                "label": n['name'],
                "type": "nutrient",
                "unit": n.get('unit', '')
            })
            edges.append({
                "source": food_id,
                "target": nut_id,
                "label": "含有",
                "amount": rel.get('amount_per_100g', 0),
                "unit": rel.get('unit', 'g')
            })

    # 添加减脂阶段节点和边
    for item in record.get('stages', []):
        s = item['node']
        if s:
            stage_id = f"stage_{s['name']}"
            nodes.append({
                "id": stage_id,
                "label": s['name'],
                "type": "stage",
                "description": s.get('description', '')
            })
            edges.append({
                "source": food_id,
                "target": stage_id,
                "label": "适合"
            })

    # 添加运动节点和边
    for item in record.get('exercises', []):
        e = item['node']
        if e:
            ex_id = f"exercise_{e['name']}"
            nodes.append({
                "id": ex_id,
                "label": e['name'],
                "type": "exercise",
                "calories_per_hour": e.get('calories_per_hour', 0)
            })
            edges.append({
                "source": ex_id,
                "target": food_id,
                "label": "消耗"
            })

    return {"nodes": nodes, "edges": edges}


async def get_all_food_names() -> List[str]:
    """获取所有食物名称列表，用于初始化布隆过滤器"""
    cypher = """
    MATCH (f:Food)
    RETURN f.name AS name
    """
    results = await neo4j_client.run(cypher)
    return [r['name'] for r in results]