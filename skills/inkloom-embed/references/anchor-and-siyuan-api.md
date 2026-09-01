# 逐知识点锚定 + 思源 API 操作细节

## 锚定原则（讲义/笔记类）

每个场景插到**解释该知识点的具体块**（标题/列表项/表格前）之后——用户 2026-08-30 因"乱插"（专题场景集中堆放）批评过，这是硬标准：

- 同一锚点最多 2 张相关图；第 3 张起上移到上一级节标题后
- 同锚多图**逆序插入**（后插的紧贴锚点，最终阅读顺序 = 场景声明顺序）
- md 插入用 Edit 工具逐个（用户规则禁脚本改内容；死链清理等纯删除可脚本）
- 思源标题可能带 riff 标记词（"3. 顺序监护 亲疏"）——SQL 精确匹配失败时 like 兜底

## HTTP API 配方（GUI 开启时首选；GUI 关闭用 CLI，判壳仍需 HTTP 或文件核实）

```python
import json, urllib.request
def api(endpoint, payload):
    req = urllib.request.Request('http://127.0.0.1:6806/api/'+endpoint,
        data=json.dumps(payload).encode(),
        headers={'Content-Type':'application/json','Authorization':'Token <conf.json 的 apiToken>'})
    return json.loads(urllib.request.urlopen(req, timeout=25).read())

api('block/getChildBlocks', {'id': did})                      # 读结构
api('query/sql', {'stmt': "select ... from blocks where root_id='<did>' and ..."})
api('block/insertBlock', {'dataType':'markdown', 'data':'![...](url)', 'previousID': anchor})
api('block/deleteBlock', {'id': block_id})                    # 清理重复
```

token 在 `D:\1STUDY\SIYUAN\conf\conf.json`。报 tree not found / children 空 = GUI/CLI 双内核冲突 → 改 HTTP API 重试。

## 陷阱实录（2026-08-31 实测）

1. **假壳**：CLI kernel 的 SQL 聚合计数可能陈旧——200 块文档报 7 块，导致场景被误赶去插 md。判壳只用 getChildBlocks。
2. **SQL markdown 列截断长块**：`like '%动画id/%'` 匹配不到（URL 后半段被截），`like '%animation-avif%'`（前段）能命中 → 全库审计拉回后 Python 解析，别信 SQL 直接匹配动画 id。
3. **insertBlock 返回 code 0 但块未插入**：previousID 为 None（锚 id 不在映射表，如 fullmap 后缀位数算错）——思源不报错也不插入。插后 getChildBlocks 复测。
4. **SQL 索引滞后**：新插块查不到，验证走 getChildBlocks。
5. **并行会话撞车**：插入前按场景 id 查重（文档已有该动画的场景则跳过）；出现过三轮叠插同一场景 3 份的事故，需 deleteBlock 清理后按 md 标准位重插。
6. **同名场景跨动画**：`retrial` 同时存在于两个动画的 manifest——拼 URL 时动画 id 必须与场景同源核对，否则 404。
7. **git 提交**：路径限定 add（并行会话在同仓工作）；`客观/动画嵌入数据/_*.json` 被 gitignore，plan 文件不提交。

## 全库死链校验配方

遍历 `客观/**/*.md` 的 `animation-avif/` 引用，对比全部 manifest 场景集合；不存在的即死链（历史成因：场景改名、错拼、旧版场景）。能对上现场景的 Edit 修正，对不上的删行——删行前确认文件不是台账/审计（其正文行可能含 animation-avif 字样但不是图链）。
