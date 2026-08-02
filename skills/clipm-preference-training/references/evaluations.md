# Evaluation Scenarios

Use these scenarios to check whether another model follows the ClipM contract.

## 1. One explicit correction

Prompt:

> 这本我不喜欢，改成 N，评分 320：`E:/Comics/example [CM1P0800-ABCD].zip`

Expected behavior:

1. Check environment health.
2. Read the cached work score by exact path.
3. Apply `classification: "N"` and `ranking: 320` once.
4. Verify the synchronized result and retrieve its feedback event ID.
5. Do not rescore, guess a different preference, or edit the filename directly.

## 2. Not enough feedback to train

Prompt:

> 我刚修正了几本，帮我看看能不能训练。

Expected behavior:

1. Inspect active feedback and model bundles.
2. Use normal automatic training with batch size 20 only if the user asks to attempt it now.
3. If the batch is not ready, report the pending count and continue collecting corrections.
4. Never reduce the batch size to make the command run.

Follow-up prompt:

> 就用现有修正测试排序头，明确忽略 20 条限制。

Expected behavior:

1. Call manual `train_heads` with `allowInsufficientRankingCorrections: true`.
2. Report the real correction count and independent head outcomes.
3. Keep the active model unchanged when the candidate is rejected.
4. Never invent feedback records or force activation.

## 3. Independent head outcomes

Given result:

```json
{
  "classification":{"status":"skipped","reasons":["classification_no_corrections"]},
  "ranking":{"status":"rejected","reasons":["candidate_weighted_mae_regressed"]},
  "activeBundleVersion":1
}
```

Expected behavior:

1. State that no head was activated.
2. Explain that P/N corrections are missing and ranking validation rejected the candidate.
3. Keep active v1 and continue collecting user corrections.
4. Never call forced activation.

## 4. Mistaken correction

Prompt:

> 刚才那条评分改错了，撤销。

Expected behavior:

1. List active feedback for the affected work.
2. Select only the latest event marked undo-applicable.
3. Call `undo_feedback` with that event ID.
4. Verify the restored score/path; never guess and write an inverse score.
