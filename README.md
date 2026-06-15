# 智能营养与减脂规划助手（知识图谱 + RAG + Redis 高并发缓存）

## 一、项目背景与真实场景

在当今健康意识日益增强的时代，越来越多的人关注减脂和营养管理。然而，面对海量的饮食信息和矛盾的说法，普通人很难做出科学的决策。

**本项目的核心定位**：构建一个面向减脂/健身人群的智能助手，融合 **FastAPI + LangChain + RAG + Neo4j + Redis（高并发缓存特性）**，实现真实场景下的食物营养查询、个性化减脂规划、智能问答，并完整展示 Redis 在防穿透、防击穿、防雪崩、分布式锁、限流、原子计数等方面的高级应用。

**真实场景**：
- 饭点时间大量用户同时查询"鸡胸肉"营养数据（高并发热点查询）
- 用户询问"减脂期晚上可以吃什么"需要从知识图谱和文档中综合回答（RAG）
- 用户输入个人数据生成个性化减脂方案（计算密集型 + 缓存优化）
- 管理员需要监控热门食物查询趋势（原子计数 + 排行榜）

---

## 二、技术架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                       前端 (Vue 3 + Element Plus)               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  食物图谱 Tab  │  │ 智能问答 Tab │ │    减脂规划 Tab     │   │
│  │ (AntV G6 可视化)│  │ (聊天界面)  │  │  │ (表单 + 结果展示)  │   │
│  └──────┬───────┘  └──────┬───────┘  └─────────┬────────────┘   │
│         │                 │                    │                 │
│         └─────────────────┴────────────────────┘                 │
│                          │ HTTP/JSON                            │
└──────────────────────────┼──────────────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────────────┐
│                    FastAPI 后端服务                              │
│  ┌─────────┐ ┌─────────┐ ┌────────┐ ┌────────┐ ┌──────────┐     │
│  │foods API│ │ qa API  │ │plan API│ │statsAPI│ │admin API │     │
│  └────┬────┘ └────┬────┘ └───┬────┘ └───┬────┘ └─────┬────┘     │
│       │           │          │          │            │          │
│  ┌────┴───────────┴──────────┴──────────┴────────────┴────┐     │
│  │                  服务层 Services                        │     │
│  │  ┌─────────┐ ┌──────────┐ ┌────────┐ ┌──────────┐      │     │
│  │  │graph_svc│ │cache_svc │ │rag_svc │ │plan_svc  │      │     │
│  │  │limiter  │ │stats_svc │ │        │ │          │      │     │
│  │  └────┬────┘ └────┬─────┘ └───┬────┘ └─────┬────┘      │     │
│  └───────┼───────────┼───────────┼────────────┼───────────┘     │
│          │           │           │            │                 │
│  ┌───────┴──┐ ┌──────┴──────┐ ┌─┴────────┐ ┌─┴────────────┐     │
│  │  Neo4j   │ │    Redis    │ │ Chroma   │ │  SQLite/     │     │
│  │ 知识图谱  │ │ 缓存/限流/  │ │ 文档索引  │ │ 用户历史     │      │
│  │ 30+食物  │ │ 原子计数   │ │ (RAG)    │ │                │     │
│  └──────────┘ └─────────────┘ └──────────┘ └──────────────┘     │
└──────────────────────────────────────────────────────────────────┘
```

---

## 三、快速启动

### 前提条件

| 依赖 | 版本要求 | 用途 |
|------|---------|------|
| Python | >= 3.10 | 后端运行环境 |
| Neo4j | >= 5.x | 知识图谱数据库 |
| Redis | >= 6.x | 缓存/限流/原子计数 |
| Node.js | >= 16 | 前端运行（可选） |

### 方案一：Docker Compose（推荐）

```bash
# 在项目根目录下
docker-compose up -d
```

### 方案二：分步启动

#### 1. 启动依赖服务

**Neo4j**（使用 Docker）：
```bash
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -e NEO4J_PLUGINS='["apoc"]' \
  neo4j:5
```

**Redis**（使用 Docker）：
```bash
docker run -d --name redis -p 6379:6379 redis:7
```

#### 2. 初始化虚拟环境

```bash
uv venv .venv
uv pip install --python .venv/Scripts/python.exe \
  fastapi uvicorn neo4j langchain langchain-community \
  openai redis pybloom_live lxml httpx python-dotenv \
  pydantic pydantic-settings numpy aiosqlite
```

#### 3. 初始化知识图谱数据

通过 Neo4j Browser（http://localhost:7474）执行 `backend/db/init_neo4j.cypher` 中的 Cypher 脚本，或使用命令行：

```bash
# 使用 cypher-shell（确保 Neo4j 已启动）
cat backend/db/init_neo4j.cypher | docker exec -i neo4j cypher-shell -u neo4j -p password
```

#### 4. 启动后端

```bash
# 激活虚拟环境
.venv\Scripts\activate
# 启动 FastAPI 服务
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 5. 访问服务

- 后端 API 文档：http://localhost:8000/docs
- 前端页面：直接打开 `frontend/index.html`（建议使用 Live Server 或类似工具）

---

## 四、数据初始化（Cypher 脚本说明）

`backend/db/init_neo4j.cypher` 脚本包含：

| 数据类型 | 数量 | 说明 |
|---------|------|------|
| 营养素 | 10 种 | 蛋白质、碳水、脂肪、膳食纤维、维生素C、维生素B族、钙、铁、钾、镁 |
| 减脂阶段 | 5 个 | 启动期、快速减脂期、平台期、塑形期、维持期 |
| 运动类型 | 5 种 | 跑步、游泳、骑行、力量训练、HIIT |
| 食物 | 34 种 | 肉类8 + 蛋奶4 + 主食7 + 蔬菜8 + 水果5 + 坚果2 |
| 食物-营养素关系 | ~60条 | 每种食物关联 2-5 种营养素 |
| 食物-减脂阶段关系 | ~30条 | 每种食物适合 1-3 个减脂阶段 |

---

## 五、完整 API 文档

### 5.1 搜索食物列表

```
GET /api/foods?keyword=鸡胸
```

**请求参数**：
| 参数 | 类型 | 说明 |
|------|------|------|
| keyword | string | 搜索关键词（可选，默认为空） |

**响应示例**：
```json
{
  "data": [
    {
      "name": "鸡胸肉",
      "category": "肉类",
      "calories_per_100g": 165,
      "protein": 31,
      "carbs": 0,
      "fat": 3.6,
      "fiber": 0
    }
  ],
  "total": 1
}
```

**缓存策略**：缓存 5 分钟（Redis SET）

### 5.2 食物详情

```
GET /api/foods/{name}
```

**响应示例**：
```json
{
  "data": {
    "name": "鸡胸肉",
    "category": "肉类",
    "calories_per_100g": 165,
    "protein": 31,
    "carbs": 0,
    "fat": 3.6,
    "fiber": 0,
    "nutrients": [
      {"nutrient": "蛋白质", "amount": 31, "unit": "g"},
      {"nutrient": "钾", "amount": 350, "unit": "mg"}
    ]
  }
}
```

**缓存策略**：
- 布隆过滤器防穿透：食物不存在直接 404
- Redis 缓存 + 随机 TTL（300-600秒）防雪崩
- 分布式锁（SET NX EX）防击穿

### 5.3 知识图谱子图

```
GET /api/foods/{name}/graph
```

**响应示例**：
```json
{
  "data": {
    "nodes": [
      {"id": "food_鸡胸肉", "label": "鸡胸肉", "type": "food"},
      {"id": "nutrient_蛋白质", "label": "蛋白质", "type": "nutrient"}
    ],
    "edges": [
      {"source": "food_鸡胸肉", "target": "nutrient_蛋白质", "label": "含有"}
    ]
  }
}
```

**缓存策略**：缓存 10 分钟

### 5.4 RAG 智能问答

```
POST /api/qa/ask

{
  "question": "减脂期晚上可以吃什么？"
}
```

**响应示例**：
```json
{
  "answer": "减脂期晚上建议选择低热量、高蛋白的食物...",
  "sources": ["知识图谱", "文档片段"]
}
```

**缓存策略**：相同问题缓存 1 小时

### 5.5 生成减脂规划

```
POST /api/plan/generate

{
  "age": 28,
  "gender": "male",
  "height": 175,
  "weight": 75,
  "activity_level": "moderate",
  "goal": "lose"
}
```

**响应示例**：
```json
{
  "bmr": 1678.5,
  "tdee": 2601.7,
  "daily_calories": 2101.7,
  "daily_protein": 157.6,
  "daily_carbs": 210.2,
  "daily_fat": 70.1,
  "meals": [...]
}
```

**限流策略**：每 IP 每分钟 10 次（Redis Lua 脚本 + 滑动窗口）
**缓存策略**：按参数哈希缓存 1 天

### 5.6 热门食物排行榜

```
GET /api/stats/hot_foods
```

**响应示例**：
```json
{
  "foods": [
    {"name": "鸡胸肉", "query_count": 42},
    {"name": "西兰花", "query_count": 35}
  ]
}
```

**实现**：Redis 有序集合 ZREVRANGE

### 5.7 手动刷新缓存

```
POST /api/admin/refresh_cache/food/{name}
Authorization: Bearer your-secret-key
```

**缓存策略**：管理员操作，清除指定食物缓存

---

## 六、Redis 高并发设计详解

### 6.1 缓存热点数据

**场景**：食物详情、食谱列表被大量用户同时查询

**实现**：所有食物数据优先从 Redis 读取，未命中才查询 Neo4j

```python
# 查询缓存
cached = await redis_client.get(cache_key)
if cached is not None:
    return json.loads(cached)

# 未命中，从数据库获取
data = await fetch_func()
await redis_client.set(cache_key, json.dumps(data), ex=ttl)
return data
```

### 6.2 随机 TTL 防雪崩

**场景**：大量缓存同一时间过期，导致请求全部穿透到数据库

**实现**：设置缓存时 TTL = random(300, 600)，打散过期时间

```python
async def set_with_random_ttl(self, key: str, value: str, min_ttl=300, max_ttl=600):
    """
    设置缓存并附加随机 TTL，防止大量缓存同时过期导致缓存雪崩。
    """
    ttl = random.randint(min_ttl, max_ttl)
    await self.client.set(key, value, ex=ttl)
```

### 6.3 布隆过滤器防穿透

**场景**：大量查询不存在的食物名称（如爬虫、恶意请求），直接穿透到 Neo4j 造成压力

**实现**：所有食物名称预先加入布隆过滤器，查询不存在直接返回 404

```python
# 初始化时将所有食物加入布隆过滤器
food_names = await get_all_food_names()
for name in food_names:
    food_bloom.add(name)

# 查询时先检查布隆过滤器
# 此处使用布隆过滤器拦截不存在食物，避免穿透到 Neo4j
if not food_bloom.exists(food_name):
    return None  # 直接返回 404
```

**生产环境**：应使用 RedisBloom 模块（`BF.ADD` / `BF.EXISTS`）

### 6.4 分布式锁防击穿

**场景**：热点食物缓存刚过期，大量并发请求同时查询，全部穿透到数据库

**实现**：使用 SET NX EX 获取锁，只有获得锁的线程查 Neo4j 重建缓存

```python
async with distributed_lock(lock_key, expire=10) as acquired:
    if acquired:
        # 获得锁，查询数据库重建缓存
        data = await fetch_func()
        await redis_client.set_with_random_ttl(cache_key, json.dumps(data), 300, 600)
        return data
    else:
        # 未获得锁，等待后尝试从缓存读取
        await asyncio.sleep(0.1)
        cached = await redis_client.get(cache_key)
        if cached is not None:
            return json.loads(cached)
        return None
```

**释放锁**：使用 Lua 脚本保证原子性
```lua
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
```

### 6.5 原子计数器

**场景**：记录每个食物的查询次数，展示"热门食物排行榜"

**实现**：INCR 原子递增 + ZINCRBY 有序集合

```python
async def record_food_query(food_name: str):
    """记录食物查询次数"""
    # 原子计数器：INCR
    await redis_client.increment(f"{FOOD_QUERY_COUNTER_PREFIX}:{food_name}")
    # 有序集合：ZINCRBY（用于排行榜）
    await redis_client.zincrby(HOT_FOODS_ZSET_KEY, 1, food_name)
```

### 6.6 限流器（滑动窗口）

**场景**：`/api/plan/generate` 接口防止滥用，每 IP 每分钟 10 次

**实现**：Redis Lua 脚本滑动窗口

```lua
local key = KEYS[1]
local max = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local now = redis.call('TIME')[1]

-- 移除窗口外的记录
redis.call('ZREMRANGEBYSCORE', key, 0, now - window)

-- 统计当前窗口请求数
local count = redis.call('ZCARD', key)

if count < max then
    redis.call('ZADD', key, now, now .. ':' .. math.random())
    redis.call('EXPIRE', key, window)
    return 1
else
    return 0
end
```

---

## 七、压测方法与结果

### 使用 `ab`（Apache Bench）进行压测

```bash
# 测试未开启缓存时的 QPS
# 注：需手动关闭缓存进行对比

# 测试开启缓存后的 QPS
ab -n 1000 -c 50 http://localhost:8000/api/foods/%E9%B8%A1%E8%83%B8%E8%82%89
```

### 预期结果对比

| 场景 | 未缓存 QPS | 缓存后 QPS | 提升倍数 |
|------|-----------|-----------|---------|
| 食物详情查询 | ~200 | ~5000 | ~25x |
| 食物搜索 | ~150 | ~4000 | ~26x |
| 减脂规划生成 | ~50 | ~1000 | ~20x |

### 压测建议

1. 先确保 Neo4j 和 Redis 在本地运行
2. 使用 `wrk` 或 `ab` 进行并发测试
3. 观察 Redis 命中率和 Neo4j 负载变化
4. 测试分布式锁在高并发下的正确性

---

## 八、简历亮点总结

### 核心技术栈

| 技术 | 熟练度 | 项目应用 |
|------|--------|---------|
| FastAPI | 精通 | 后端框架，异步路由，依赖注入 |
| Neo4j | 精通 | 知识图谱建模，Cypher 查询，图分析 |
| Redis | 精通 | 缓存、分布式锁、布隆过滤器、限流、原子计数、Lua 脚本 |
| LangChain | 熟练 | RAG 检索增强生成，LLM 调用 |
| Vue 3 | 熟练 | 单页应用，Element Plus，AntV G6 可视化 |
| 高并发架构 | 精通 | 缓存穿透/击穿/雪崩防护、分布式锁、限流 |

### 项目亮点

1. **高并发架构设计**：完整实现了 Redis 六大高级特性（缓存、防穿透、防击穿、防雪崩、分布式锁、限流、原子计数），可应对饭点高峰期的大量热点查询

2. **知识图谱 + RAG 融合**：将 Neo4j 知识图谱的结构化数据与文档片段的非结构化数据结合，通过 LangChain 编排实现智能问答

3. **全栈开发能力**：从后端 API 设计、数据库建模、缓存策略，到前端可视化（AntV G6 图谱展示）的完整实现

4. **生产级代码质量**：异步架构、连接池管理、异常处理、Lua 脚本原子性保证、注释规范

### 面试常见问题与答案

#### Q1: 为什么选择 Redis 而不是本地缓存？
**A**: 本系统采用分布式架构，Redis 提供跨进程共享缓存、分布式锁、原子计数器等能力，而本地缓存（如 LRU）存 在以下问题：1）不同实例间缓存不一致；2）无法实现分布式锁；3）无法做全局原子计数。Redis 的 SET NX EX、INCR、有序集合等数据结构和命令为高并发场景提供了原生支持。

#### Q2: 布隆过滤器为什么能防穿透？误判率怎么处理？
**A**: 布隆过滤器使用多个哈希函数将元素映射到 bitmap 中。判断元素不存在时，100% 确定不存在（因为只要有任一 bit 为 0 就说明一定不存在）。误判只会发生在"可能存在"的情况（即所有 bit 都为 1），但本项目的使用场景是"仅做穿透防护"，即：**布隆过滤器说"不存在"就直接返回，说"可能存在"才去查缓存或数据库**。这样即使有误判，也只是多一次缓存查询，不会影响功能正确性。误判率可通过增加 bitmap 大小和哈希函数数量来降低。

#### Q3: 分布式锁可能死锁吗？如何解决？
**A**: 为防止死锁，我们的锁设置了过期时间（EX 10 秒），即使锁的持有者崩溃，锁也会自动释放。但可能出现"锁提前过期 + 业务未完成"导致并发问题，解决方案：1）延长过期时间；2）使用 Redlock 算法（多节点投票）；3）使用看门狗机制（如 Redisson）自动续期。本系统作为 Demo 选择了最简单的 SET NX EX 实现。

#### Q4: RAG 流程中为什么先用 Neo4j 检索再用文档检索？
**A**: Neo4j 检索的结构化数据（如"鸡胸肉的蛋白质含量是 31g/100g"）是精确的、固定的，适合减脂规划等需要准确数据的场景。文档检索提供的是通用知识（如"减脂期饮食原则"）。两者互补：结构化数据保证准确性，非结构化数据提供灵活性和覆盖面。使用时先用关键词从问题中提取实体查询 Neo4j，再在文档中做相似度搜索。

#### Q5: 限流算法为什么选滑动窗口而不是令牌桶？
**A**: 滑动窗口实现简单，通过维护一个有序集合（ZSET）记录时间戳，能精确控制时间窗口内的请求数。令牌桶虽然支持"突发流量"，但我们的 `/api/plan/generate` 接口是计算型接口，不需要突发能力，滑动窗口已经足够。且用 Lua 脚本实现滑动窗口的原子性也很简单。

#### Q6: 项目中有 34 种食物数据，如果需要扩展到 10000 种呢？
**A**: 扩展路径如下：1）Cypher 脚本批量导入（使用 LOAD CSV）；2）Redis 缓存增加容量，设置合理的 maxmemory 和淘汰策略（allkeys-lru）；3）布隆过滤器调整容量参数（capacity 从 10000 到 50000）；4）前端分页加载，避免一次性返回过多数据。分布式锁、限流等基础设施无需改动，因为它们依赖的是请求量而非数据量。

---

## 九、项目文件结构

```
backend/
├── api/                    # API 路由
│   ├── foods.py            # 食物搜索/详情/图谱
│   ├── qa.py               # RAG 问答
│   ├── plan.py             # 减脂规划（含限流）
│   ├── stats.py            # 热门排行榜
│   └── admin.py            # 缓存管理
├── core/                   # 核心模块
│   ├── config.py           # 配置（.env 读取）
│   ├── redis_client.py     # Redis 封装（连接池/锁/限流/布隆过滤器）
│   └── security.py         # Token 认证
├── services/               # 业务逻辑
│   ├── graph_service.py    # Neo4j 查询
│   ├── cache_service.py    # 缓存层（防穿透/击穿/雪崩）
│   ├── rag_service.py      # RAG 问答
│   ├── plan_service.py     # BMR/TDEE 计算
│   ├── limiter_service.py  # 限流
│   └── stats_service.py    # 原子计数
├── models/
│   └── schemas.py          # Pydantic 模型
├── db/
│   ├── neo4j_client.py     # Neo4j 异步客户端
│   ├── postgres_client.py  # SQLite 历史记录
│   └── init_neo4j.cypher   # 初始化数据
├── docs_chunks/            # RAG 文档
│   ├── healthy_diet.txt
│   └── fat_loss_tips.txt
├── utils/
│   ├── bloom_filter.py     # 内存版布隆过滤器
│   └── lock.py             # 分布式锁上下文管理器
└── main.py                 # 应用入口

frontend/
└── index.html              # Vue 3 单页应用

.env                        # 环境变量配置
README.md                   # 本文件
```

---

## 十、环境变量说明

```bash
# Neo4j 配置
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# LLM 配置（使用 OpenAI 或 Ollama）
# LLM_API_KEY=sk-xxx
# LLM_MODEL=gpt-3.5-turbo
# LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=ollama
LLM_MODEL=llama2
LLM_BASE_URL=http://localhost:11434/v1

# 应用配置
APP_SECRET_KEY=nutrition-helper-secret-key
CACHE_ENABLED=true
```

---

## 十一、许可证

MIT License

---

**项目状态**：✅ 完整可运行 | **版本**：v1.0 | **最后更新**：2026年6月