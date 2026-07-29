---
name: legal-imagen
description: 为法考和法律学习内容生成适用于 Midjourney、DALL-E、Stable Diffusion、ComfyUI 等工具的配图 Prompt。用户需要把法律关系、流程、时间线、概念对比或案例转成图片提示词时使用。
---

# 🎨 AI绘图Prompt辅助学习指南

> **重要说明**：本指南用于生成**真实图片**的AI绘图prompt，适用于Midjourney、DALL-E、Stable Diffusion、ComfyUI等AI绘图工具，**不是mermaid代码块或文本图表**。

---

## 一、核心定位

本指南用于生成AI绘图工具的prompt，创建真实图片来辅助理解复杂的法律概念、关系和流程。通过可视化方式降低认知负荷，提升学习效率。

### 适用工具
- **Midjourney**：推荐用于艺术风格场景图
- **DALL-E 3**：推荐用于精确信息图表
- **Stable Diffusion**：推荐用于自定义风格
- **ComfyUI**：推荐用于复杂工作流
- **Ideogram**：推荐用于文字标注

---

## 二、适用场景

### 1. 法律关系图
- **适用内容**：多方当事人之间的权利义务关系
- **典型场景**：
  - 善意取得中的三方关系
  - 代理关系中的授权链条
  - 担保关系中的债权债务结构
  - 继承关系中的亲属网络

### 2. 时间线图
- **适用内容**：诉讼时效、期间计算、程序流程
- **典型场景**：
  - 诉讼时效起算点与中断事由
  - 上诉期间与送达时间节点
  - 刑事诉讼各阶段时限
  - 行政复议与诉讼期限

### 3. 流程图
- **适用内容**：诉讼程序、审批流程、法律适用步骤
- **典型场景**：
  - 民事诉讼一审→二审→执行流程
  - 刑事案件立案→侦查→起诉→审判流程
  - 行政处罚程序
  - 合同成立与生效判断流程

### 4. 对比图
- **适用内容**：易混淆概念的视觉对比
- **典型场景**：
  - 盗窃罪vs抢夺罪vs抢劫罪
  - 民事法律行为vs事实行为
  - 善意取得vs拾得遗失物
  - 表见代理vs无权代理

### 5. 场景图
- **适用内容**：典型案例的场景还原
- **典型场景**：
  - 交通事故责任认定场景
  - 不动产交易流程场景
  - 正当防卫的时间条件场景
  - 紧急避险的利益衡量场景

---

## 三、Prompt生成原则

### 1. 简洁明确
- 只描述核心要素，避免冗余细节
- 使用具体视觉描述，而非抽象概念
- 控制prompt长度在50-150词

### 2. 结构清晰
- **法律关系图**：主体人物+关系箭头+标注文字
- **时间线图**：时间轴+事件节点+期间标注
- **流程图**：步骤框+判断菱形+箭头连接
- **对比图**：并列布局+对比维度+差异高亮
- **场景图**：场景元素+人物动作+关键标注

### 3. 风格统一
推荐三种标准风格：
- **简约扁平风格**：适合关系图、流程图
  - 关键词：flat design, minimal, clean lines, vector style, infographic
- **信息图表风格**：适合时间线、对比图
  - 关键词：infographic, data visualization, modern, professional, chart style
- **教学插图风格**：适合场景还原、案例分析
  - 关键词：educational illustration, textbook style, clear, diagram, annotated

### 4. 中文友好
- 主体、关系、标注均使用中文
- 法律术语保持原样
- 可添加英文辅助说明（可选）

---

## 四、Prompt模板库

### 模板1：法律关系图

**基础结构**：
```
[风格] flat design infographic, clean and minimal
[主体] three people representing [角色A], [角色B], [角色C], arranged in triangle
[关系] arrows connecting them with labels showing [关系类型]
[标注] clear text labels in Chinese: [关键标注]
[颜色] professional color scheme with blue for rights, red for obligations
[质量] high quality, sharp details, educational purpose
```

**示例 - 善意取得三方关系**：
```
Midjourney Prompt:
flat design infographic showing three people in a triangular relationship, 
minimal style, clean lines. Person A (original owner) at top, 
Person B (unauthorized seller) at left, Person C (good faith buyer) at right. 
Arrows connecting them with Chinese text labels: "委托保管" from A to B, 
"无权转让" from B to C, "追偿关系" from A to C. 
Professional color scheme: blue arrows for legal rights, 
red dashed arrow for unauthorized transfer, yellow highlight box around Person C. 
Educational diagram style, high quality, sharp details, white background --ar 16:9
```

**DALL-E 3 Prompt**：
```
Create a flat design infographic showing the three-party relationship in good faith acquisition. 
Three people arranged in a triangle: 
- Top: "甲 (原所有权人)" in blue
- Left: "乙 (无权处分人)" in red  
- Right: "丙 (善意第三人)" in green

Arrows connecting them with labels:
- 甲→乙: "委托保管" (blue solid arrow)
- 乙→丙: "无权转让" (red dashed arrow)
- 甲→丙: "追偿关系" (yellow arrow)

Clean, minimal style with professional color scheme. 
Educational diagram on white background. High quality infographic.
```

---

### 模板2：时间线图

**基础结构**：
```
[风格] horizontal timeline infographic, clean and modern
[时间轴] timeline from left to right with clear markers
[节点] T0, T1, T2, T3 marked with dots and labels
[区间] colored segments showing different periods
[标注] Chinese text for events and legal effects
[颜色] gradient from past to present, highlight key moments
```

**示例 - 诉讼时效计算**：
```
Midjourney Prompt:
horizontal timeline infographic showing statute of limitations calculation, 
clean modern style. Timeline from left to right with 4 key points: 
T0 (权利受损), T1 (提起诉讼), T2 (诉讼终结), T3 (时效届满). 
Colored segments: 3-year period in blue, interruption period in red. 
Chinese text labels: "时效起算", "时效中断", "重新起算", "抗辩权产生". 
Professional infographic style, white background, clear annotations, 
educational purpose --ar 21:9
```

**DALL-E 3 Prompt**：
```
Create a horizontal timeline infographic for statute of limitations calculation.

Timeline with 4 key time points from left to right:
- T0: "权利人知道权利受损" (时效起算) - green dot
- T1: "权利人提起诉讼" (时效中断) - red dot
- T2: "诉讼终结" (重新起算) - yellow dot
- T3: "时效届满" (抗辩权产生) - blue dot

Colored segments:
- T0 to T3: 3年普通诉讼时效 (blue bar)
- T1 to T2: 中断期间不计入 (red dashed bar)

Annotations: 中断事由、中止事由、最长保护期20年
Clean, modern infographic style on white background. Professional educational diagram.
```

---

### 模板3：流程图

**基础结构**：
```
[风格] flowchart diagram, clean lines, professional
[结构] linear flow with decision diamonds
[步骤] rectangular boxes for steps, diamonds for decisions
[分支] arrows showing yes/no paths
[标注] Chinese text for conditions and outcomes
[颜色] consistent color coding for different paths
```

**示例 - 合同效力判断流程**：
```
Midjourney Prompt:
flowchart diagram showing contract validity determination process, 
clean professional style. Starting from top: 
"合同是否成立?" in diamond shape, branching to 
"是否生效?" and "效力状态判定". 
Three outcome boxes: "有效合同" (green), "无效合同" (red), 
"可撤销合同" (yellow), "效力待定合同" (orange). 
Arrows with Chinese labels: "成立且符合生效要件", "违反效力要件", 
"存在欺诈胁迫". Professional flowchart style, white background, 
educational diagram --ar 9:16
```

**DALL-E 3 Prompt**：
```
Create a flowchart for contract validity determination.

Flow from top to bottom:
1. Diamond: "合同是否成立?" (要约+承诺)
   - Yes → continue
   - No → stop

2. Diamond: "是否符合生效要件?"
   - Yes → "有效合同" (green box)
   - No → continue checking

3. Decision branches:
   - 违法/违背公序良俗 → "无效合同" (red box)
   - 欺诈/胁迫/重大误解/显失公平 → "可撤销合同" (yellow box)
   - 无权处分/无权代理 → "效力待定合同" (orange box)

Clean flowchart style with professional color coding. White background. Educational diagram.
```

---

### 模板4：对比图

**基础结构**：
```
[风格] side-by-side comparison infographic, clear layout
[布局] three columns for three concepts
[维度] rows showing different comparison aspects
[内容] concise text in each cell
[高亮] color coding to highlight differences
[标注] key differences emphasized
```

**示例 - 盗窃罪vs抢夺罪vs抢劫罪**：
```
Midjourney Prompt:
side-by-side comparison infographic for three crimes: 盗窃罪, 抢夺罪, 抢劫罪. 
Three columns with clear headers. Comparison rows: 
"行为方式", "暴力程度", "被害人状态", "取财特征". 
Content in Chinese: 盗窃罪 column shows "秘密窃取", "无暴力", "不知情"; 
抢夺罪 column shows "公然夺取", "对物暴力", "可知情但无力反抗"; 
抢劫罪 column shows "暴力压制", "对人暴力", "被强制不能反抗". 
Color coding: blue for 盗窃, yellow for 抢夺, red for 抢劫. 
Professional infographic style, white background, educational purpose --ar 16:9
```

**DALL-E 3 Prompt**：
```
Create a side-by-side comparison infographic for three crimes.

Three columns with headers:
| 盗窃罪 | 抢夺罪 | 抢劫罪 |

Comparison rows:
1. 行为方式:
   - 盗窃罪: 秘密窃取
   - 抢夺罪: 公然夺取
   - 抢劫罪: 暴力压制

2. 暴力程度:
   - 盗窃罪: 无暴力
   - 抢夺罪: 对物暴力
   - 抢劫罪: 对人暴力

3. 被害人状态:
   - 盗窃罪: 不知情
   - 抢夺罪: 可知情但无力反抗
   - 抢劫罪: 被强制不能反抗

4. 取财特征:
   - 盗窃罪: 平和取财
   - 抢夺罪: 乘人不备取财
   - 抢劫罪: 强行取财

Color coding: blue (盗窃), yellow (抢夺), red (抢劫)
Key difference highlight: 暴力对象（物vs人）
Memory tip: 盗无暴，夺对物，抢对人
Professional infographic style on white background.
```

---

### 模板5：场景图

**基础结构**：
```
[风格] educational illustration, realistic but simplified
[场景] specific setting with relevant elements
[人物] characters with clear roles and actions
[动作] key behaviors depicted
[标注] annotations pointing to important details
[颜色] realistic colors with emphasis on key elements
```

**示例 - 正当防卫时间条件场景**：
```
Midjourney Prompt:
educational illustration showing self-defense scenario at night, 
realistic but simplified style. Scene: residential interior at night, 
dark lighting. Two characters: defender (homeowner) holding a bat, 
intruder with knife breaking through door. 
Key moments shown: intruder entering (不法侵害开始), 
defender counterattacking (防卫行为), intruder fleeing (侵害结束). 
Annotations in Chinese: "正在进行", "防卫时机适当", "适时停止". 
Yellow highlight on defender's action, red warning on excessive force. 
Educational illustration style, clear composition, annotated diagram --ar 16:9
```

**DALL-E 3 Prompt**：
```
Create an educational illustration for self-defense time conditions.

Scene: Night time, inside a residential home, dark atmosphere.

Characters and actions:
1. Intruder (侵害人): Breaking through the door with a knife
   - Label: "不法侵害开始"
   - Time: "正在进行"

2. Defender (防卫人): Homeowner holding a baseball bat, counterattacking
   - Label: "防卫行为"
   - Condition: "防卫时机适当"

3. Outcome: Intruder fleeing
   - Label: "侵害结束"
   - Note: "防卫应适时停止"

Annotations:
- Time condition: 不法侵害"正在进行"
- Limit condition: 防卫不能明显超过必要限度
- Special defense: 对严重暴力犯罪可无限防卫

Educational illustration style. Realistic but simplified. Clear composition with annotations.
```

---

## 五、输出格式规范

### 标准输出格式

使用 Callout 提示块包裹，提供多个AI工具的prompt：

```markdown
> [!TIP] 🎨 可视化辅助 - AI绘图Prompt
>
> **Midjourney**:
> ```
> [完整prompt]
> ```
>
> **DALL-E 3**:
> ```
> [完整prompt]
> ```
>
> **使用建议**: [具体建议]
```

### 嵌入位置

- 放置在对应知识点的末尾
- 与正文用空行分隔
- 可选添加说明文字："下图辅助理解xxx关系："

---

## 六、使用建议

### 1. 工具选择

| 内容类型 | 推荐工具 | 理由 |
| :--- | :--- | :--- |
| 法律关系图 | DALL-E 3 | 文字标注更准确 |
| 时间线图 | DALL-E 3 | 信息图表处理更好 |
| 流程图 | DALL-E 3 | 流程结构清晰 |
| 对比图 | DALL-E 3 | 并列对比准确 |
| 场景图 | Midjourney | 艺术感更强，场景更真实 |

### 2. 适用判断
- ✅ 复杂的多方关系
- ✅ 抽象的时间流程
- ✅ 易混淆的概念对比
- ✅ 典型案例的场景还原
- ❌ 简单的单方行为
- ❌ 纯文字的法条列举
- ❌ 已经有清晰图表的内容

### 3. 生成策略
- **聚焦核心**：只可视化关键结构和关系
- **忠于原文**：不添加原文未提及的信息
- **辅助定位**：图片是辅助工具，不替代文字说明
- **迭代优化**：根据生成效果调整prompt

### 4. 质量控制
- Prompt长度控制在50-150词
- 主体数量控制在3-5个
- 关系线条控制在5-8条
- 标注信息控制在3-5个关键点

---

## 七、高级技巧

### 1. Midjourney专用技巧

**参数说明**：
- `--ar 16:9`：宽屏比例，适合横向关系图
- `--ar 9:16`：竖屏比例，适合纵向流程图
- `--ar 1:1`：正方形，适合对比图
- `--style raw`：更写实风格
- `--v 6`：使用V6版本（更准确）

**负面提示**：
```
--no photorealistic, 3D render, complex details, shadows, gradients
```

**风格预设**：
```
flat design, vector illustration, infographic style, clean lines, 
minimal, professional, educational diagram, white background
```

### 2. DALL-E 3专用技巧

**结构化描述**：
- 使用明确的列表格式
- 分点描述每个元素
- 明确颜色编码
- 添加尺寸建议

**文字处理**：
- 中文文字需要明确说明
- 可以要求"Chinese text labels"
- 重要文字用引号标注

**质量提升**：
```
Create a [type] infographic/diagram/illustration.
[详细描述]
Professional, clean, educational style. High quality. White background.
```

### 3. Stable Diffusion专用技巧

**模型推荐**：
- `sd3-medium`：通用高质量
- `sdxl`：高分辨率
- `flat-2d-animated`：扁平风格

**提示词权重**：
```
(flat design:1.3), (infographic:1.2), (clean lines:1.2), 
[其他描述词], (complex:0.8), (realistic:0.5)
```

**负面提示**：
```
negative prompt: photorealistic, 3D, shadows, gradients, 
complex details, noise, blur, low quality
```

### 4. 颜色编码系统

**法律关系颜色**：
- **蓝色系**：权利关系、合法行为
  - Midjourney: `blue arrows, blue boxes`
  - DALL-E: "blue for rights"
- **红色系**：义务关系、违法行为
  - Midjourney: `red arrows, red boxes`
  - DALL-E: "red for obligations"
- **黄色系**：争议焦点、关键条件
  - Midjourney: `yellow highlight, yellow boxes`
  - DALL-E: "yellow for key points"
- **绿色系**：成功状态、有效行为
  - Midjourney: `green checkmark, green boxes`
  - DALL-E: "green for valid/success"
- **灰色系**：次要信息、背景说明
  - Midjourney: `gray, muted colors`
  - DALL-E: "gray for secondary info"

### 5. 构图技巧

**三角形构图**（三方关系）：
```
three people arranged in triangle, Person A at top, 
Person B at bottom left, Person C at bottom right
```

**线性构图**（流程图）：
```
flowchart from top to bottom, sequential layout, 
clear progression from start to end
```

**并列构图**（对比图）：
```
side-by-side layout, three columns, equal spacing, 
parallel comparison structure
```

**放射构图**（多方关系）：
```
central element with radiating connections, 
hub-and-spoke layout, multiple branches
```

---

## 八、常见错误与修正

| 错误类型 | ❌ 错误示范 | ✅ 正确做法 |
| :--- | :--- | :--- |
| 过于抽象 | "show legal relationship" | "three people with arrows connecting them, labeled '委托', '转让'" |
| 信息过载 | 描述所有细节和例外 | 只描述核心结构和关键点 |
| 风格混乱 | 混用多种风格关键词 | 统一使用"flat design, infographic" |
| 缺少标注 | 只有图形没有文字 | 明确要求"Chinese text labels" |
| 比例不当 | 默认比例 | 根据内容类型设置`--ar`参数 |
| 脱离原文 | 添加原文未提及的内容 | 严格基于原文信息生成 |

---

## 九、快速参考卡

### Midjourney 快速模板

```
[类型] infographic, flat design, clean lines
[主体] [具体描述]
[关系] [连接方式]
[标注] Chinese text labels: [关键文字]
[颜色] professional color scheme
[质量] educational diagram, white background
[比例] --ar [根据内容选择]
```

### DALL-E 3 快速模板

```
Create a [类型] infographic/diagram.

[详细分点描述]

Professional, clean style. White background. Educational purpose.
```

---

## 十、实际应用示例

### 示例1：善意取得构成要件

**知识点**：善意取得的四个构成要件

**生成的Prompt**：

> [!TIP] 🎨 可视化辅助 - 善意取得构成要件
>
> **Midjourney**:
> ```
> flat design infographic showing good faith acquisition requirements, 
> four key elements arranged in a 2x2 grid. Each element in a colored box: 
> 1. "善意" (good faith) in blue, 
> 2. "合理价格" (reasonable price) in green, 
> 3. "已交付" (delivered) in yellow, 
> 4. "已登记" (registered) in orange. 
> Chinese text labels, clean layout, professional infographic style, 
> white background, educational diagram --ar 1:1
> ```
>
> **DALL-E 3**:
> ```
> Create a grid infographic showing the four requirements for good faith acquisition.
>
> 2x2 grid layout with four boxes:
> 1. "善意" (good faith) - blue box
>    - 说明: 受让人不知情
> 2. "合理价格" (reasonable price) - green box
>    - 说明: 以合理对价转让
> 3. "已交付" (delivered) - yellow box
>    - 说明: 动产已交付
> 4. "已登记" (registered) - orange box
>    - 说明: 不动产已登记
>
> Clean, professional infographic style. White background. Educational diagram.
> ```
>
> **使用建议**: 使用DALL-E 3生成，文字标注更准确

---

### 示例2：犯罪构成四要件

**知识点**：犯罪构成的四个要件

**生成的Prompt**：

> [!TIP] 🎨 可视化辅助 - 犯罪构成四要件
>
> **Midjourney**:
> ```
> circular diagram showing four elements of crime constitution, 
> arranged in a circle with center label "犯罪构成". 
> Four segments: "犯罪客体" (object) in blue, 
> "犯罪客观方面" (objective aspect) in green, 
> "犯罪主体" (subject) in yellow, 
> "犯罪主观方面" (subjective aspect) in red. 
> Arrows showing interconnections between elements. 
> Chinese text labels, clean infographic style, 
> white background, educational diagram --ar 1:1
> ```
>
> **DALL-E 3**:
> ```
> Create a circular diagram showing the four elements of crime constitution.
>
> Circular layout with center label "犯罪构成":
> - Top: "犯罪客体" (blue segment)
>   - 说明: 刑法保护的法益
> - Right: "犯罪客观方面" (green segment)
>   - 说明: 危害行为+危害结果
> - Bottom: "犯罪主体" (yellow segment)
>   - 说明: 实施犯罪的人
> - Left: "犯罪主观方面" (red segment)
>   - 说明: 故意或过失
>
> Arrows connecting all four elements to show their relationships.
> Professional infographic style. White background. Educational diagram.
> ```
>
> **使用建议**: 使用DALL-E 3生成，圆形布局更直观

---

## 十一、版本说明

- **版本**：v2.0
- **更新日期**：2026-05-17
- **重要说明**：本指南专门用于生成**真实图片**，适用于AI绘图工具
- **适用场景**：法考学习、法律概念可视化
- **配合工具**：可配合 marknote.md 使用，作为可视化增强模块
- **关键区别**：生成的是真实图片文件，不是mermaid代码块或文本图表
