"""
RAG 智能问答服务。
从 Neo4j 检索相关实体 + 文档片段检索 + LLM 组合回答。
"""
import json
import os
from typing import List, Optional
from backend.core.config import settings
from backend.core.redis_client import redis_client
from backend.services.cache_service import get_cached_or_fetch
from backend.db.neo4j_client import neo4j_client

# 文档片段目录
DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs_chunks")


def _load_docs() -> List[dict]:
    """加载文档片段（简单的txt文件读取，生产环境使用向量数据库）"""
    chunks = []
    if not os.path.exists(DOCS_DIR):
        return chunks
    for filename in os.listdir(DOCS_DIR):
        if filename.endswith(".txt"):
            filepath = os.path.join(DOCS_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                # 按空行分割为片段
                parts = [p.strip() for p in content.split("\n\n") if p.strip()]
                for part in parts:
                    chunks.append({"source": filename, "content": part})
    return chunks


async def _search_neo4j_for_qa(question: str) -> str:
    """从 Neo4j 中检索与问题相关的知识"""
    # 尝试从问题中提取食物名称
    cypher = """
    MATCH (f:Food)
    WHERE $question CONTAINS f.name
    OPTIONAL MATCH (f)-[r:CONTAINS]->(n:Nutrient)
    RETURN f.name AS food, f.calories_per_100g AS calories,
           COLLECT({nutrient: n.name, amount: r.amount_per_100g, unit: r.unit}) AS nutrients
    LIMIT 5
    """
    try:
        results = await neo4j_client.run(cypher, question=question)
        if not results:
            # 尝试模糊匹配
            cypher2 = """
            MATCH (f:Food)
            RETURN f.name AS food, f.calories_per_100g AS calories,
                   f.protein AS protein, f.carbs AS carbs, f.fat AS fat,
                   [] AS nutrients
            LIMIT 5
            """
            results = await neo4j_client.run(cypher2)
        
        if results:
            lines = []
            for r in results:
                line = f"- {r['food']}: {r['calories']} kcal/100g"
                if r.get('nutrients'):
                    nut_str = ", ".join([f"{n['nutrient']}: {n['amount']}{n['unit']}" for n in r['nutrients'] if n['nutrient']])
                    if nut_str:
                        line += f" ({nut_str})"
                lines.append(line)
            return "\n".join(lines)
    except Exception:
        pass
    return ""


async def ask_question(question: str) -> str:
    """
    RAG 问答主流程。
    使用相同问题哈希作为缓存 key，相同问题 1 小时内直接返回缓存。
    """
    cache_key = f"qa:{hash(question)}"
    
    # 检查缓存
    cached = await redis_client.get(cache_key)
    if cached is not None:
        return cached

    # 1. 从 Neo4j 检索知识
    kg_context = await _search_neo4j_for_qa(question)
    
    # 2. 从文档片段检索
    docs = _load_docs()
    doc_context = ""
    for doc in docs:
        # 简单关键词匹配
        keywords = question.replace("？", "").replace("?", "").split()
        if any(kw in doc['content'] for kw in keywords if len(kw) > 1):
            doc_context += f"\n[{doc['source']}]: {doc['content'][:300]}"
    
    # 3. 构建 Prompt
    prompt = f"""你是一个专业的营养与减脂顾问。请基于以下信息回答用户的问题。

用户问题：{question}

知识图谱中的食物数据：
{kg_context if kg_context else "（暂无相关食物数据）"}

健康知识文档：
{doc_context if doc_context else "（暂无相关文档）"}

请提供专业、准确的回答。如果信息不足，请说明并给出一般性建议。
回答使用中文。
"""
    
    # 4. 调用 LLM
    answer = await _call_llm(prompt)
    
    # 缓存 1 小时
    if answer:
        await redis_client.set(cache_key, answer, ex=3600)
    
    return answer


async def _call_llm(prompt: str) -> str:
    """
    调用 LLM（支持 DeepSeek / OpenAI / Ollama）。
    当 LLM_API_KEY/LLM_BASE_URL 配置后，自动调用对应 API。
    失败时降级为 Mock 响应。
    """
    # 检查是否有 API Key 配置
    api_key = settings.LLM_API_KEY
    base_url = settings.LLM_BASE_URL
    model = settings.LLM_MODEL
    
    if api_key and api_key != "ollama" and base_url:
        try:
            from openai import AsyncOpenAI
            
            # DeepSeek 使用 OpenAI 兼容接口
            client = AsyncOpenAI(
                api_key=api_key,
                base_url=base_url
            )
            
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "你是一个专业的营养与减脂顾问。请基于提供的知识图谱食物数据和健康知识文档，用中文回答用户关于饮食、营养、减脂运动的问题。回答要专业准确，有数据支撑，语气亲切友好。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM API 调用失败，降级至 Mock 响应: {e}")
    elif base_url and "localhost" in base_url:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(
                api_key="ollama",
                base_url=base_url
            )
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "你是一个专业的营养与减脂顾问。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Ollama 调用失败: {e}")
    
    # Mock 响应：基于关键词简单规则
    return _mock_llm_response(prompt)


def _mock_llm_response(prompt: str) -> str:
    """Mock LLM 响应（当没有 API Key 时使用）"""
    q = prompt.split("用户问题：")[1].split("\n")[0] if "用户问题：" in prompt else ""
    
    if "晚上" in q and "吃" in q:
        return "减脂期晚上建议选择低热量、高蛋白的食物，如鸡胸肉沙拉、清蒸鱼、豆腐蔬菜汤等。避免高碳水和油腻食物，晚餐最好在睡前3小时完成。每餐控制在300-400大卡为宜。"
    elif "鸡胸肉" in q and "鱼" in q:
        return "鸡胸肉和鱼肉都是减脂期的优质蛋白来源。鸡胸肉（165kcal/100g，31g蛋白质）脂肪含量极低，适合增肌减脂；鱼肉（如三文鱼208kcal/100g）富含omega-3脂肪酸，对心血管健康更有利。建议两者交替食用。"
    elif "碳水" in q or "主食" in q:
        return "减脂期建议选择低GI的复合碳水，如糙米、燕麦、红薯、藜麦等。避免精制碳水（白米、白面）。每餐主食控制在拳头大小（约100-150g熟重），搭配足量蔬菜和蛋白质。"
    elif "蛋白" in q:
        return "减脂期蛋白质摄入推荐每天每公斤体重1.6-2.2g。优质蛋白来源：鸡胸肉（31g/100g）、鸡蛋（13g/100g）、三文鱼（20g/100g）、豆腐（8g/100g）、希腊酸奶（10g/100g）。建议每餐均匀分布蛋白质摄入。"
    elif "运动" in q or "锻炼" in q:
        return "减脂期建议有氧运动与力量训练结合。有氧（跑步、游泳等）直接消耗热量，力量训练提高基础代谢。推荐每周3-4次有氧（每次30-45分钟）+ 2-3次力量训练。HIIT（高强度间歇训练）燃脂效率最高，但需根据个人体能循序渐进。"
    else:
        return "减脂的核心原理是创造热量缺口（摄入 < 消耗）。建议：1）控制每日总热量，计算BMR和TDEE；2）保证足量蛋白质（1.6-2.2g/kg体重）；3）选择复合碳水和优质脂肪；4）规律运动（有氧+力量）；5）充足睡眠和水分。具体方案需根据个人情况调整，建议咨询专业营养师。"