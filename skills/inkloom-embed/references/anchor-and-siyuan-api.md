# 锚定原则与思源 API 操作细节

## 逐知识点锚定（讲义/笔记类）

- 每个场景插到**解释该知识点的具体块**（标题/列表项/表格前）之后；禁止把一个专题的场景集中堆在同一位置（用户 2026-08-30 严厉批评过"乱插"）
- 同一锚点最多 2 张相关图；第 3 张起上移到上一级节标题后
- 思源标题可能带 riff 标记词（如"3. 顺序监护 亲疏"）——SQL content 精确匹配失败时用 like 兜底
- 同锚多图逆序插入（后插的紧贴锚点，最终阅读顺序 = 场景声明顺序）

## HTTP API 配方（GUI 开启时首选）

```python
import json, urllib.request
def api(endpoint, payload):
    req = urllib.request.Request('http://127.0.0.1:6806/api/'+endpoint,
        data=json.dumps(payload).encode(),
        headers={'Content-Type':'application/json','Authorization':'Token <conf.json 的 apiToken>'})
    return json.loads(urllib.request.urlopen(req, timeout=25).read())

# 读结构
api('block/getChildBlocks', {'id': did})
api('query/sql', {'stmt': "select ... from blocks where root_id='<did>' and ..."})

# 插入（previousID = 锚块完整 id）
api('block/insertBlock', {'dataType':'markdown', 'data':'![...](url)', 'previousID': anchor})

# 删除重复块
api('block/deleteBlock', {'id': block_id})
```

## 陷阱实录（2026-08-31）

1. **SQL markdown 列截断长块**：`like '%动画id/%'` 匹配不到（URL 后半段被截），`like '%animation-avif%'`（前段）能命中 → 全库审计拉回后 Python 正则解析，别信 SQL 直接匹配动画 id
2. **insertBlock code 0 但块未出现**：previousID 传了 None（锚 id 不在 fullmap）——思源不报错但也不插入。必须插后 getChildBlocks 复测
3. **fullmap 后缀位数**：块 id 如 `20260316215220-2bms3zw` 的 [-12:] 是 `5220-2bms3zw` 而非 `15220-2bms3zw`——用完整 id 作键最稳
4. **CLI 假壳**：GUI 关闭时 CLI kernel 的 SQL 聚合计数可能陈旧（实测 200 块文档报 7 块）→ 判壳只用 getChildBlocks
5. **并行会话撞车**：插入前按场景 id 查重（同文档 markdown 已含该动画的场景跳过）；历史上出现过三轮叠插同一场景 3 份，需 deleteBlock 清理后按 md 标准位重插
6. **git 提交**：路径限定 add（防扫入并行会话文件）；.gitignore 可能忽略 动画嵌入数据/_*.json（plan 文件别指望提交）
