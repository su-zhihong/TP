// ============================================================
// 初始化知识图谱数据：食物、营养素、运动与减脂关系
// 包含 30+ 种食物、10 种营养素、5 种运动类型
// ============================================================

// ---- 创建营养素 ----
CREATE (p:Nutrient {name: '蛋白质', unit: 'g', daily_reference: 60});
CREATE (c:Nutrient {name: '碳水化合物', unit: 'g', daily_reference: 250});
CREATE (f:Nutrient {name: '脂肪', unit: 'g', daily_reference: 65});
CREATE (fib:Nutrient {name: '膳食纤维', unit: 'g', daily_reference: 25});
CREATE (vitc:Nutrient {name: '维生素C', unit: 'mg', daily_reference: 100});
CREATE (vitb:Nutrient {name: '维生素B族', unit: 'mg', daily_reference: 10});
CREATE (ca:Nutrient {name: '钙', unit: 'mg', daily_reference: 800});
CREATE (fe:Nutrient {name: '铁', unit: 'mg', daily_reference: 15});
CREATE (k:Nutrient {name: '钾', unit: 'mg', daily_reference: 2000});
CREATE (mg:Nutrient {name: '镁', unit: 'mg', daily_reference: 350});

// ---- 创建减脂阶段 ----
CREATE (s1:FatLossStage {name: '启动期', description: '开始减脂，减少热量摄入'});
CREATE (s2:FatLossStage {name: '快速减脂期', description: '持续热量缺口，体重明显下降'});
CREATE (s3:FatLossStage {name: '平台期', description: '体重下降减缓，需调整饮食和运动'});
CREATE (s4:FatLossStage {name: '塑形期', description: '接近目标体重，加强运动塑形'});
CREATE (s5:FatLossStage {name: '维持期', description: '达到目标体重，维持健康生活习惯'});

// ---- 创建运动类型 ----
CREATE (e1:Exercise {name: '跑步', type: '有氧', calories_per_hour: 600, description: '中等强度跑步'});
CREATE (e2:Exercise {name: '游泳', type: '有氧', calories_per_hour: 500, description: '全身有氧运动'});
CREATE (e3:Exercise {name: '骑行', type: '有氧', calories_per_hour: 450, description: '户外/室内骑行'});
CREATE (e4:Exercise {name: '力量训练', type: '力量', calories_per_hour: 350, description: '器械或自重训练'});
CREATE (e5:Exercise {name: 'HIIT', type: '高强度间歇', calories_per_hour: 700, description: '高强度间歇训练'});

// ---- 创建食物（30+种） ----
// 高蛋白肉类
CREATE (f1:Food {name: '鸡胸肉', category: '肉类', calories_per_100g: 165, protein: 31, carbs: 0, fat: 3.6, fiber: 0});
CREATE (f2:Food {name: '瘦牛肉', category: '肉类', calories_per_100g: 250, protein: 26, carbs: 0, fat: 15, fiber: 0});
CREATE (f3:Food {name: '猪里脊', category: '肉类', calories_per_100g: 210, protein: 25, carbs: 0, fat: 11, fiber: 0});
CREATE (f4:Food {name: '三文鱼', category: '海鲜', calories_per_100g: 208, protein: 20, carbs: 0, fat: 13, fiber: 0});
CREATE (f5:Food {name: '虾仁', category: '海鲜', calories_per_100g: 99, protein: 24, carbs: 0, fat: 0.3, fiber: 0});
CREATE (f6:Food {name: '鱼肉（鲈鱼）', category: '海鲜', calories_per_100g: 105, protein: 19, carbs: 0, fat: 3, fiber: 0});
CREATE (f7:Food {name: '鸭胸肉', category: '肉类', calories_per_100g: 140, protein: 24, carbs: 0, fat: 5, fiber: 0});
CREATE (f8:Food {name: '鸡腿肉（去皮）', category: '肉类', calories_per_100g: 180, protein: 26, carbs: 0, fat: 8, fiber: 0});

// 蛋奶类
CREATE (f9:Food {name: '鸡蛋', category: '蛋类', calories_per_100g: 155, protein: 13, carbs: 1.1, fat: 11, fiber: 0});
CREATE (f10:Food {name: '脱脂牛奶', category: '乳制品', calories_per_100g: 34, protein: 3.4, carbs: 5, fat: 0.1, fiber: 0});
CREATE (f11:Food {name: '希腊酸奶', category: '乳制品', calories_per_100g: 59, protein: 10, carbs: 3.6, fat: 0.7, fiber: 0});
CREATE (f12:Food {name: '豆腐', category: '豆制品', calories_per_100g: 76, protein: 8, carbs: 2, fat: 4, fiber: 0.3});

// 主食类
CREATE (f13:Food {name: '糙米', category: '主食', calories_per_100g: 111, protein: 2.6, carbs: 23, fat: 0.9, fiber: 1.8});
CREATE (f14:Food {name: '燕麦', category: '主食', calories_per_100g: 389, protein: 16.9, carbs: 66, fat: 6.9, fiber: 10.6});
CREATE (f15:Food {name: '红薯', category: '主食', calories_per_100g: 86, protein: 1.6, carbs: 20, fat: 0.1, fiber: 3});
CREATE (f16:Food {name: '全麦面包', category: '主食', calories_per_100g: 247, protein: 13, carbs: 41, fat: 3.4, fiber: 7});
CREATE (f17:Food {name: '藜麦', category: '主食', calories_per_100g: 120, protein: 4.4, carbs: 21, fat: 1.9, fiber: 2.8});
CREATE (f18:Food {name: '荞麦面', category: '主食', calories_per_100g: 110, protein: 4.5, carbs: 21, fat: 0.8, fiber: 2.5});
CREATE (f19:Food {name: '玉米', category: '主食', calories_per_100g: 96, protein: 3.4, carbs: 21, fat: 1.2, fiber: 2.4});

// 蔬菜类
CREATE (f20:Food {name: '西兰花', category: '蔬菜', calories_per_100g: 34, protein: 2.8, carbs: 7, fat: 0.4, fiber: 2.6});
CREATE (f21:Food {name: '菠菜', category: '蔬菜', calories_per_100g: 23, protein: 2.9, carbs: 3.6, fat: 0.4, fiber: 2.2});
CREATE (f22:Food {name: '黄瓜', category: '蔬菜', calories_per_100g: 15, protein: 0.7, carbs: 3.6, fat: 0.1, fiber: 0.5});
CREATE (f23:Food {name: '番茄', category: '蔬菜', calories_per_100g: 18, protein: 0.9, carbs: 3.9, fat: 0.2, fiber: 1.2});
CREATE (f24:Food {name: '生菜', category: '蔬菜', calories_per_100g: 15, protein: 1.4, carbs: 2.9, fat: 0.2, fiber: 1.3});
CREATE (f25:Food {name: '胡萝卜', category: '蔬菜', calories_per_100g: 41, protein: 0.9, carbs: 10, fat: 0.2, fiber: 2.8});
CREATE (f26:Food {name: '芹菜', category: '蔬菜', calories_per_100g: 16, protein: 0.7, carbs: 3, fat: 0.2, fiber: 1.6});
CREATE (f27:Food {name: '紫甘蓝', category: '蔬菜', calories_per_100g: 31, protein: 1.4, carbs: 7, fat: 0.2, fiber: 2.1});

// 水果类
CREATE (f28:Food {name: '苹果', category: '水果', calories_per_100g: 52, protein: 0.3, carbs: 14, fat: 0.2, fiber: 2.4});
CREATE (f29:Food {name: '蓝莓', category: '水果', calories_per_100g: 57, protein: 0.7, carbs: 14, fat: 0.3, fiber: 2.4});
CREATE (f30:Food {name: '牛油果', category: '水果', calories_per_100g: 160, protein: 2, carbs: 8.5, fat: 15, fiber: 6.7});
CREATE (f31:Food {name: '香蕉', category: '水果', calories_per_100g: 89, protein: 1.1, carbs: 23, fat: 0.3, fiber: 2.6});
CREATE (f32:Food {name: '西柚', category: '水果', calories_per_100g: 42, protein: 0.8, carbs: 11, fat: 0.1, fiber: 1.6});

// 坚果种子类
CREATE (f33:Food {name: '杏仁', category: '坚果', calories_per_100g: 579, protein: 21, carbs: 22, fat: 50, fiber: 12.5});
CREATE (f34:Food {name: '核桃', category: '坚果', calories_per_100g: 654, protein: 15, carbs: 14, fat: 65, fiber: 6.7});

// ---- 创建关系：食物→含有→营养素 ----
// 鸡胸肉
MATCH (f:Food {name:'鸡胸肉'}), (n:Nutrient {name:'蛋白质'}) CREATE (f)-[:CONTAINS {amount_per_100g: 31, unit:'g'}]->(n);
MATCH (f:Food {name:'鸡胸肉'}), (n:Nutrient {name:'碳水化合物'}) CREATE (f)-[:CONTAINS {amount_per_100g: 0, unit:'g'}]->(n);
MATCH (f:Food {name:'鸡胸肉'}), (n:Nutrient {name:'脂肪'}) CREATE (f)-[:CONTAINS {amount_per_100g: 3.6, unit:'g'}]->(n);
MATCH (f:Food {name:'鸡胸肉'}), (n:Nutrient {name:'钾'}) CREATE (f)-[:CONTAINS {amount_per_100g: 350, unit:'mg'}]->(n);
MATCH (f:Food {name:'鸡胸肉'}), (n:Nutrient {name:'镁'}) CREATE (f)-[:CONTAINS {amount_per_100g: 28, unit:'mg'}]->(n);

// 三文鱼
MATCH (f:Food {name:'三文鱼'}), (n:Nutrient {name:'蛋白质'}) CREATE (f)-[:CONTAINS {amount_per_100g: 20, unit:'g'}]->(n);
MATCH (f:Food {name:'三文鱼'}), (n:Nutrient {name:'脂肪'}) CREATE (f)-[:CONTAINS {amount_per_100g: 13, unit:'g'}]->(n);
MATCH (f:Food {name:'三文鱼'}), (n:Nutrient {name:'维生素B族'}) CREATE (f)-[:CONTAINS {amount_per_100g: 5.8, unit:'mg'}]->(n);
MATCH (f:Food {name:'三文鱼'}), (n:Nutrient {name:'钙'}) CREATE (f)-[:CONTAINS {amount_per_100g: 15, unit:'mg'}]->(n);

// 鸡蛋
MATCH (f:Food {name:'鸡蛋'}), (n:Nutrient {name:'蛋白质'}) CREATE (f)-[:CONTAINS {amount_per_100g: 13, unit:'g'}]->(n);
MATCH (f:Food {name:'鸡蛋'}), (n:Nutrient {name:'脂肪'}) CREATE (f)-[:CONTAINS {amount_per_100g: 11, unit:'g'}]->(n);
MATCH (f:Food {name:'鸡蛋'}), (n:Nutrient {name:'维生素B族'}) CREATE (f)-[:CONTAINS {amount_per_100g: 0.6, unit:'mg'}]->(n);
MATCH (f:Food {name:'鸡蛋'}), (n:Nutrient {name:'铁'}) CREATE (f)-[:CONTAINS {amount_per_100g: 1.8, unit:'mg'}]->(n);

// 糙米
MATCH (f:Food {name:'糙米'}), (n:Nutrient {name:'碳水化合物'}) CREATE (f)-[:CONTAINS {amount_per_100g: 23, unit:'g'}]->(n);
MATCH (f:Food {name:'糙米'}), (n:Nutrient {name:'蛋白质'}) CREATE (f)-[:CONTAINS {amount_per_100g: 2.6, unit:'g'}]->(n);
MATCH (f:Food {name:'糙米'}), (n:Nutrient {name:'膳食纤维'}) CREATE (f)-[:CONTAINS {amount_per_100g: 1.8, unit:'g'}]->(n);
MATCH (f:Food {name:'糙米'}), (n:Nutrient {name:'镁'}) CREATE (f)-[:CONTAINS {amount_per_100g: 43, unit:'mg'}]->(n);

// 西兰花
MATCH (f:Food {name:'西兰花'}), (n:Nutrient {name:'膳食纤维'}) CREATE (f)-[:CONTAINS {amount_per_100g: 2.6, unit:'g'}]->(n);
MATCH (f:Food {name:'西兰花'}), (n:Nutrient {name:'维生素C'}) CREATE (f)-[:CONTAINS {amount_per_100g: 89, unit:'mg'}]->(n);
MATCH (f:Food {name:'西兰花'}), (n:Nutrient {name:'钙'}) CREATE (f)-[:CONTAINS {amount_per_100g: 47, unit:'mg'}]->(n);
MATCH (f:Food {name:'西兰花'}), (n:Nutrient {name:'钾'}) CREATE (f)-[:CONTAINS {amount_per_100g: 316, unit:'mg'}]->(n);

// 菠菜
MATCH (f:Food {name:'菠菜'}), (n:Nutrient {name:'膳食纤维'}) CREATE (f)-[:CONTAINS {amount_per_100g: 2.2, unit:'g'}]->(n);
MATCH (f:Food {name:'菠菜'}), (n:Nutrient {name:'维生素C'}) CREATE (f)-[:CONTAINS {amount_per_100g: 28, unit:'mg'}]->(n);
MATCH (f:Food {name:'菠菜'}), (n:Nutrient {name:'铁'}) CREATE (f)-[:CONTAINS {amount_per_100g: 2.7, unit:'mg'}]->(n);
MATCH (f:Food {name:'菠菜'}), (n:Nutrient {name:'钙'}) CREATE (f)-[:CONTAINS {amount_per_100g: 99, unit:'mg'}]->(n);

// 牛油果
MATCH (f:Food {name:'牛油果'}), (n:Nutrient {name:'脂肪'}) CREATE (f)-[:CONTAINS {amount_per_100g: 15, unit:'g'}]->(n);
MATCH (f:Food {name:'牛油果'}), (n:Nutrient {name:'膳食纤维'}) CREATE (f)-[:CONTAINS {amount_per_100g: 6.7, unit:'g'}]->(n);
MATCH (f:Food {name:'牛油果'}), (n:Nutrient {name:'钾'}) CREATE (f)-[:CONTAINS {amount_per_100g: 485, unit:'mg'}]->(n);

// 燕麦
MATCH (f:Food {name:'燕麦'}), (n:Nutrient {name:'碳水化合物'}) CREATE (f)-[:CONTAINS {amount_per_100g: 66, unit:'g'}]->(n);
MATCH (f:Food {name:'燕麦'}), (n:Nutrient {name:'膳食纤维'}) CREATE (f)-[:CONTAINS {amount_per_100g: 10.6, unit:'g'}]->(n);
MATCH (f:Food {name:'燕麦'}), (n:Nutrient {name:'蛋白质'}) CREATE (f)-[:CONTAINS {amount_per_100g: 16.9, unit:'g'}]->(n);

// 红薯
MATCH (f:Food {name:'红薯'}), (n:Nutrient {name:'碳水化合物'}) CREATE (f)-[:CONTAINS {amount_per_100g: 20, unit:'g'}]->(n);
MATCH (f:Food {name:'红薯'}), (n:Nutrient {name:'膳食纤维'}) CREATE (f)-[:CONTAINS {amount_per_100g: 3, unit:'g'}]->(n);
MATCH (f:Food {name:'红薯'}), (n:Nutrient {name:'维生素C'}) CREATE (f)-[:CONTAINS {amount_per_100g: 2.4, unit:'mg'}]->(n);

// 虾仁
MATCH (f:Food {name:'虾仁'}), (n:Nutrient {name:'蛋白质'}) CREATE (f)-[:CONTAINS {amount_per_100g: 24, unit:'g'}]->(n);
MATCH (f:Food {name:'虾仁'}), (n:Nutrient {name:'钙'}) CREATE (f)-[:CONTAINS {amount_per_100g: 120, unit:'mg'}]->(n);
MATCH (f:Food {name:'虾仁'}), (n:Nutrient {name:'镁'}) CREATE (f)-[:CONTAINS {amount_per_100g: 43, unit:'mg'}]->(n);

// 全麦面包
MATCH (f:Food {name:'全麦面包'}), (n:Nutrient {name:'碳水化合物'}) CREATE (f)-[:CONTAINS {amount_per_100g: 41, unit:'g'}]->(n);
MATCH (f:Food {name:'全麦面包'}), (n:Nutrient {name:'膳食纤维'}) CREATE (f)-[:CONTAINS {amount_per_100g: 7, unit:'g'}]->(n);
MATCH (f:Food {name:'全麦面包'}), (n:Nutrient {name:'蛋白质'}) CREATE (f)-[:CONTAINS {amount_per_100g: 13, unit:'g'}]->(n);

// 苹果
MATCH (f:Food {name:'苹果'}), (n:Nutrient {name:'碳水化合物'}) CREATE (f)-[:CONTAINS {amount_per_100g: 14, unit:'g'}]->(n);
MATCH (f:Food {name:'苹果'}), (n:Nutrient {name:'膳食纤维'}) CREATE (f)-[:CONTAINS {amount_per_100g: 2.4, unit:'g'}]->(n);
MATCH (f:Food {name:'苹果'}), (n:Nutrient {name:'维生素C'}) CREATE (f)-[:CONTAINS {amount_per_100g: 4.6, unit:'mg'}]->(n);

// 蓝莓
MATCH (f:Food {name:'蓝莓'}), (n:Nutrient {name:'维生素C'}) CREATE (f)-[:CONTAINS {amount_per_100g: 9.7, unit:'mg'}]->(n);
MATCH (f:Food {name:'蓝莓'}), (n:Nutrient {name:'膳食纤维'}) CREATE (f)-[:CONTAINS {amount_per_100g: 2.4, unit:'g'}]->(n);

// 香蕉
MATCH (f:Food {name:'香蕉'}), (n:Nutrient {name:'碳水化合物'}) CREATE (f)-[:CONTAINS {amount_per_100g: 23, unit:'g'}]->(n);
MATCH (f:Food {name:'香蕉'}), (n:Nutrient {name:'钾'}) CREATE (f)-[:CONTAINS {amount_per_100g: 358, unit:'mg'}]->(n);

// 豆腐
MATCH (f:Food {name:'豆腐'}), (n:Nutrient {name:'蛋白质'}) CREATE (f)-[:CONTAINS {amount_per_100g: 8, unit:'g'}]->(n);
MATCH (f:Food {name:'豆腐'}), (n:Nutrient {name:'钙'}) CREATE (f)-[:CONTAINS {amount_per_100g: 350, unit:'mg'}]->(n);

// 瘦牛肉
MATCH (f:Food {name:'瘦牛肉'}), (n:Nutrient {name:'蛋白质'}) CREATE (f)-[:CONTAINS {amount_per_100g: 26, unit:'g'}]->(n);
MATCH (f:Food {name:'瘦牛肉'}), (n:Nutrient {name:'铁'}) CREATE (f)-[:CONTAINS {amount_per_100g: 2.6, unit:'mg'}]->(n);
MATCH (f:Food {name:'瘦牛肉'}), (n:Nutrient {name:'维生素B族'}) CREATE (f)-[:CONTAINS {amount_per_100g: 3.5, unit:'mg'}]->(n);

// 鱼肉（鲈鱼）
MATCH (f:Food {name:'鱼肉（鲈鱼）'}), (n:Nutrient {name:'蛋白质'}) CREATE (f)-[:CONTAINS {amount_per_100g: 19, unit:'g'}]->(n);
MATCH (f:Food {name:'鱼肉（鲈鱼）'}), (n:Nutrient {name:'维生素B族'}) CREATE (f)-[:CONTAINS {amount_per_100g: 1.2, unit:'mg'}]->(n);

// 猪里脊
MATCH (f:Food {name:'猪里脊'}), (n:Nutrient {name:'蛋白质'}) CREATE (f)-[:CONTAINS {amount_per_100g: 25, unit:'g'}]->(n);
MATCH (f:Food {name:'猪里脊'}), (n:Nutrient {name:'维生素B族'}) CREATE (f)-[:CONTAINS {amount_per_100g: 4.2, unit:'mg'}]->(n);

// ---- 创建关系：食物→适合→减脂阶段 ----
MATCH (f:Food {name:'鸡胸肉'}), (s:FatLossStage {name:'启动期'}) CREATE (f)-[:SUITABLE_FOR]->(s);
MATCH (f:Food {name:'鸡胸肉'}), (s:FatLossStage {name:'快速减脂期'}) CREATE (f)-[:SUITABLE_FOR]->(s);
MATCH (f:Food {name:'鸡胸肉'}), (s:FatLossStage {name:'塑形期'}) CREATE (f)-[:SUITABLE_FOR]->(s);

MATCH (f:Food {name:'三文鱼'}), (s:FatLossStage {name:'快速减脂期'}) CREATE (f)-[:SUITABLE_FOR]->(s);
MATCH (f:Food {name:'三文鱼'}), (s:FatLossStage {name:'塑形期'}) CREATE (f)-[:SUITABLE_FOR]->(s);

MATCH (f:Food {name:'糙米'}), (s:FatLossStage {name:'启动期'}) CREATE (f)-[:SUITABLE_FOR]->(s);
MATCH (f:Food {name:'糙米'}), (s:FatLossStage {name:'快速减脂期'}) CREATE (f)-[:SUITABLE_FOR]->(s);
MATCH (f:Food {name:'糙米'}), (s:FatLossStage {name:'维持期'}) CREATE (f)-[:SUITABLE_FOR]->(s);

MATCH (f:Food {name:'西兰花'}), (s:FatLossStage {name:'启动期'}) CREATE (f)-[:SUITABLE_FOR]->(s);
MATCH (f:Food {name:'西兰花'}), (s:FatLossStage {name:'快速减脂期'}) CREATE (f)-[:SUITABLE_FOR]->(s);
MATCH (f:Food {name:'西兰花'}), (s:FatLossStage {name:'平台期'}) CREATE (f)-[:SUITABLE_FOR]->(s);
MATCH (f:Food {name:'西兰花'}), (s:FatLossStage {name:'塑形期'}) CREATE (f)-[:SUITABLE_FOR]->(s);

MATCH (f:Food {name:'红薯'}), (s:FatLossStage {name:'快速减脂期'}) CREATE (f)-[:SUITABLE_FOR]->(s);
MATCH (f:Food {name:'红薯'}), (s:FatLossStage {name:'塑形期'}) CREATE (f)-[:SUITABLE_FOR]->(s);

MATCH (f:Food {name:'鸡蛋'}), (s:FatLossStage {name:'启动期'}) CREATE (f)-[:SUITABLE_FOR]->(s);
MATCH (f:Food {name:'鸡蛋'}), (s:FatLossStage {name:'快速减脂期'}) CREATE (f)-[:SUITABLE_FOR]->(s);
MATCH (f:Food {name:'鸡蛋'}), (s:FatLossStage {name:'塑形期'}) CREATE (f)-[:SUITABLE_FOR]->(s);

MATCH (f:Food {name:'燕麦'}), (s:FatLossStage {name:'启动期'}) CREATE (f)-[:SUITABLE_FOR]->(s);
MATCH (f:Food {name:'燕麦'}), (s:FatLossStage {name:'快速减脂期'}) CREATE (f)-[:SUITABLE_FOR]->(s);

MATCH (f:Food {name:'希腊酸奶'}), (s:FatLossStage {name:'快速减脂期'}) CREATE (f)-[:SUITABLE_FOR]->(s);
MATCH (f:Food {name:'希腊酸奶'}), (s:FatLossStage {name:'塑形期'}) CREATE (f)-[:SUITABLE_FOR]->(s);

MATCH (f:Food {name:'牛油果'}), (s:FatLossStage {name:'塑形期'}) CREATE (f)-[:SUITABLE_FOR]->(s);
MATCH (f:Food {name:'牛油果'}), (s:FatLossStage {name:'维持期'}) CREATE (f)-[:SUITABLE_FOR]->(s);

MATCH (f:Food {name:'虾仁'}), (s:FatLossStage {name:'启动期'}) CREATE (f)-[:SUITABLE_FOR]->(s);
MATCH (f:Food {name:'虾仁'}), (s:FatLossStage {name:'快速减脂期'}) CREATE (f)-[:SUITABLE_FOR]->(s);

MATCH (f:Food {name:'菠菜'}), (s:FatLossStage {name:'启动期'}) CREATE (f)-[:SUITABLE_FOR]->(s);
MATCH (f:Food {name:'菠菜'}), (s:FatLossStage {name:'快速减脂期'}) CREATE (f)-[:SUITABLE_FOR]->(s);

MATCH (f:Food {name:'豆腐'}), (s:FatLossStage {name:'快速减脂期'}) CREATE (f)-[:SUITABLE_FOR]->(s);
MATCH (f:Food {name:'豆腐'}), (s:FatLossStage {name:'塑形期'}) CREATE (f)-[:SUITABLE_FOR]->(s);

MATCH (f:Food {name:'鱼肉（鲈鱼）'}), (s:FatLossStage {name:'快速减脂期'}) CREATE (f)-[:SUITABLE_FOR]->(s);
MATCH (f:Food {name:'鱼肉（鲈鱼）'}), (s:FatLossStage {name:'塑形期'}) CREATE (f)-[:SUITABLE_FOR]->(s);

// ---- 创建关系：运动→消耗→热量范围 ----
MATCH (e:Exercise {name:'跑步'}), (n:Nutrient {name:'碳水化合物'}) CREATE (e)-[:BURNS {min_cal: 400, max_cal: 800}]->(n);
MATCH (e:Exercise {name:'跑步'}), (n:Nutrient {name:'脂肪'}) CREATE (e)-[:BURNS {min_cal: 400, max_cal: 800}]->(n);
MATCH (e:Exercise {name:'HIIT'}), (n:Nutrient {name:'碳水化合物'}) CREATE (e)-[:BURNS {min_cal: 500, max_cal: 900}]->(n);
MATCH (e:Exercise {name:'HIIT'}), (n:Nutrient {name:'脂肪'}) CREATE (e)-[:BURNS {min_cal: 500, max_cal: 900}]->(n);
MATCH (e:Exercise {name:'游泳'}), (n:Nutrient {name:'碳水化合物'}) CREATE (e)-[:BURNS {min_cal: 350, max_cal: 650}]->(n);
MATCH (e:Exercise {name:'力量训练'}), (n:Nutrient {name:'蛋白质'}) CREATE (e)-[:BURNS {min_cal: 250, max_cal: 450}]->(n);
MATCH (e:Exercise {name:'骑行'}), (n:Nutrient {name:'碳水化合物'}) CREATE (e)-[:BURNS {min_cal: 300, max_cal: 600}]->(n);

// ---- 创建索引 ----
CREATE INDEX food_name_idx IF NOT EXISTS FOR (f:Food) ON (f.name);
CREATE INDEX nutrient_name_idx IF NOT EXISTS FOR (n:Nutrient) ON (n.name);
CREATE INDEX exercise_name_idx IF NOT EXISTS FOR (e:Exercise) ON (e.name);
CREATE INDEX stage_name_idx IF NOT EXISTS FOR (s:FatLossStage) ON (s.name);