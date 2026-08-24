# ⚡专题六 共同诉讼

## 制度区分

- **共同诉讼**{: style="color: var(--b3-font-color10);"}的两类基本形态如何区分？ #法考/民诉/共同诉讼/制度区分# #闪卡/优先级/P1#
    - **必要共同诉讼**{: style="color: var(--b3-font-color10);"}：诉讼标的是**共同**{: style="background-color: var(--b3-font-background11);"}的。
        - 处理结果：<em>合一审理、合一判决</em>。
    - **普通共同诉讼**{: style="color: var(--b3-font-color12);"}：诉讼标的是<u>同一种类</u>的。
        - 审理方式：可以`合并审理`，也可以分开审理。
    - 对照维度：
        | 制度 | 标的关系 | 审理方式 |
        | --- | --- | --- |
        | 必要共同诉讼 | 共同 | 合一审理、合一判决 |
        | 普通共同诉讼 | 同一种类 | 合并或分开审理 |
{: custom-dm-source-key="example-civil-joint-litigation" custom-dm-card-id="fc-example-joint-litigation-basic-distinction-v1" custom-dm-card-schema="1" custom-dm-card-kind="basic" custom-dm-card-renderer="list" custom-qb-note-topic-id="civil-procedure-joint-litigation-distinction"}

---

## 人数不确定的代表人诉讼

- 人数不确定的代表人诉讼启动步骤是什么？ #法考/民诉/共同诉讼/代表人诉讼/人数不确定# #闪卡/优先级/P1#
    - 程序步骤：
        1. **公告**{: style="color: var(--b3-font-color12); background-color: var(--b3-font-background12);"}案件情况和诉讼请求。
        2. **登记**{: style="color: var(--b3-font-color13);"}权利人。
        3. 由登记的权利人推选代表人；推选不出时，由法院与登记权利人商定。
        ```mermaid
        flowchart LR
            A[人数尚未确定] --> B[公告案件情况]
            B --> C[权利人登记]
            C --> D[推选或商定代表人]
            classDef known fill:#e8f1ff,stroke:#3b6ea8,color:#222;
            classDef answer fill:#e8f5e9,stroke:#4d8b57,color:#222;
            class A known;
            class B,C,D answer;
        ```
    > [!IMPORTANT] 核心边界
    > - <em>起诉时人数尚未确定</em>，不能直接按确定人数规则推选。
    > - ~~跳过公告、登记直接裁判~~不是该程序的启动方式。
{: custom-dm-source-key="example-civil-joint-litigation" custom-dm-card-id="fc-example-joint-litigation-representative-process-v1" custom-dm-card-schema="1" custom-dm-card-kind="basic" custom-dm-card-renderer="list" custom-qb-note-topic-id="civil-procedure-joint-litigation-representative-undetermined"}

## 四类制度区分口诀

- **区分口诀**{: style="color: var(--b3-font-color6);"}：==必要共标的，普通同种类；确定全体推，不定公告登。== #法考/民诉/共同诉讼/区分口诀# #闪卡/优先级/P1#
    - ==必要共标的==：必要共同诉讼，诉讼标的是**共同**{: style="background-color: var(--b3-font-background11);"}的。
    - ==普通同种类==：普通共同诉讼，诉讼标的是<u>同一种类</u>的。
    - ==确定全体推==：人数确定时由全体当事人推选代表人。
    - ==不定公告登==：人数不确定时先公告、登记，再推选或商定代表人。
{: custom-dm-source-key="example-civil-joint-litigation" custom-dm-card-id="fc-example-joint-litigation-mnemonic-v1" custom-dm-card-schema="1" custom-dm-card-kind="mnemonic" custom-dm-card-renderer="list" custom-qb-note-topic-id="civil-procedure-joint-litigation-mnemonic"}

生成报告：候选 3；接受 3；拒绝 0。
原笔记：[[示例/专题六 共同诉讼]] · 协议：DAMO 闪卡 schema 1
