- **司法三段论**{: style="color: var(--b3-font-color10);"}中法律规范、法律事实与案件裁判如何对应？ #法考/理论法/法理学/法适用/司法三段论# #闪卡/优先级/P1#
    ```mermaid
    flowchart LR
        N[法律规范] --> P1[①]
        F[法律事实] --> P2[②]
        P1 --> R[③]
        P2 --> R
        classDef known fill:#e8f1ff,stroke:#2563eb,color:#0f172a;
        classDef recall fill:#fff3bf,stroke:#d97706,color:#7c2d12,stroke-dasharray:5 3;
        class N,F known;
        class P1,P2,R recall;
    ```
    - **完整对应**{: style="background-color: var(--b3-font-background11);"}：
        ```mermaid
        flowchart LR
            N[法律规范] --> P1[大前提]
            F[法律事实] --> P2[小前提]
            P1 --> R[案件裁判：结论]
            P2 --> R
            classDef known fill:#e8f1ff,stroke:#2563eb,color:#0f172a;
            classDef answer fill:#e6fcf5,stroke:#059669,color:#064e3b;
            class N,F known;
            class P1,P2,R answer;
        ```
{: custom-dm-source-key="beisong-2026-mafeng-kd15-fa-shiyong" custom-dm-card-id="fc-theory-judicial-syllogism-visual-recall-v1" custom-dm-card-schema="1" custom-dm-card-kind="basic" custom-dm-card-renderer="list" custom-qb-note-topic-id="theory-law-application-judicial-syllogism"}

```yaml
report:
  candidates: 1
  accepted: 1
  rejected: 0
  rejection_reasons: {}
```
原笔记：[[示例/司法三段论]] · 协议：DAMO 闪卡 schema 1
