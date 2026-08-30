# Damophus 出题输入与 ID 契约

## 可接受的输入

出题至少需要一份题目内容资料和一份个性化信号。资料可以是：

- 含 `custom-qb-*` IAL 的题库 Markdown，提供题干、选项、答案、解析和考点。
- 题目目录/题目索引导出，至少能把题目 ID 映射到科目、分类和考点。
- 现行法条、课程讲义、原题解析或用户明确指定的权威材料，作为新题规则依据。

个性化信号可以是：

```json
{
  "questionId": "civil-gold-objective-2020-2-1-14",
  "topicIds": ["civil-security-flow-clause"],
  "subject": "civil",
  "attempts": 3,
  "objectiveCorrect": 1,
  "latestRating": "again",
  "lastAnsweredAt": "2026-08-30T10:00:00Z",
  "bookmark": {
    "tags": ["易混淆", "重点"],
    "note": "容易把流押条款和抵押合同效力混在一起"
  }
}
```

字段名称不是强制的；CSV、JSON、表格或自然语言记录都可以先映射到同一语义。只含 Riff `revlog.csv` 的记录通常只有 `card_id`、评分和时间，必须另有卡片到题目/考点的映射；不能把 `card_id` 当作 `custom-qb-id`。

## 个性化信号的边界

- `Again`、答错、重复答错、`Hard`、长用时、主观题低分用于排序和题目蓝图。
- 收藏标签和备注用于发现用户关注的陷阱、相邻概念和表达偏好。
- 统计值不进入题目 IAL，不写入题干、选项或解析，不改变原有复习阈值。
- 资料之间发生题目 ID、答案或考点冲突时停止该题，并报告冲突来源。

## ID 规则

### 变式题

从原题稳定 ID 派生，不使用显示序号：

```text
{subject}-damophus-variant-{source-question-id}-v{variant}
```

例如：

```text
civil-damophus-variant-civil-gold-objective-2020-2-1-14-v01
```

同一源题同一变式号只能对应一个题目。变式号发生变化表示新题，不覆盖原题。

### 弱点驱动的新题

没有唯一源题时，使用目标叶考点和稳定批次键：

```text
{subject}-damophus-target-{topic-id}-{batch-key}-v{variant}
```

`batch-key` 由用户指定，或由生成日期加短 ASCII 标识组成；不要用随机 UUID 作为唯一依据，否则无法稳定去重。ID 必须只含小写 ASCII 字母、数字和连字符。

### 考点

优先复用现有 `custom-qb-note-topic-id` 对应的叶子 ID。没有合适叶子时，创建一个普通考点提供块：

```md
### 流押条款的效力与抵押权实现
{: custom-qb-note-topic-id="civil-security-flow-clause" custom-qb-note-topic-parent-id="civil-security"}
```

只有确认父考点存在且该 ID 确实是更细考点时才写 `custom-qb-note-topic-parent-id`。题目始终使用：

```md
{: custom-qb-question-topic-ids="civil-security-flow-clause"}
```

新输出不得使用 `custom-qb-topic-ids`、`custom-qb-role` 或把普通笔记的 `custom-qb-note-topic-id` 写到题目 IAL。

## 输出元数据

允许写入描述题目静态身份的属性：

```text
custom-qb-id
custom-qb-type
custom-qb-answer              # 主观题不写
custom-qb-question-topic-ids
custom-qb-source="damophus-generated"
custom-qb-subject
custom-qb-category
custom-qb-collection
```

禁止写入：尝试次数、正确率、Again/Hard 状态、复习时间、Riff 卡片 ID、设备 ID、数据库行 ID 和生成时的临时权重。
