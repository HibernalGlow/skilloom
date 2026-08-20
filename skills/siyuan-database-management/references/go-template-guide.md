# Go Template Guide

Rules and proven templates for SiYuan Attribute View `template` columns. Read the three iron rules before writing any comparison or arithmetic.

## Iron rules

1. **Float comparisons.** Every SiYuan number is `float64`. Compare with `gt .实际完成 0.0`; writing the integer `0` raises `incompatible types for comparison` and fails parsing.
2. **Unpack rollup slices.** A rollup column enters the template context as a list (e.g. `[120]`). Index the list with `index .实际完成 0` to get the plain number; otherwise it renders the bracketed string `[120]` and arithmetic breaks.
3. **Guard division by zero.** Always validate the denominator before dividing: `if gt $target 0.0`.

## Rollup slice safe-read

Check the slice length and extract the first item only when one is present:

```gotemplate
.action{$done := 0.0}
.action{if gt (len .实际完成) 0}
    .action{$done = index .实际完成 0}
.action{end}
```

## Conditional effective calculation

The effective count is the actual count when it is non-zero, else the total question count when the check-in is done, else `0`:

```gotemplate
.action{ if gt .实际完成 0.0 }
    .action{ .实际完成 }
.action{ else if .打卡完成 }
    .action{ .总题量 }
.action{ else }
    0
.action{ end }
```

## Visual progress bar

Renders a filled bar with the percentage overlaid and the `done / target` figure on the right:

```gotemplate
<!-- Visual Progress Bar -->
.action{$done := 0.0}
.action{if gt (len .实际完成) 0}
    .action{$done = index .实际完成 0}
.action{end}
.action{$target := 1.0}
.action{if .计划题量}
    .action{$target = .计划题量}
.action{end}
.action{$pct := 0.0}
.action{if gt $target 0.0}
    .action{$pct = mulf (divf $done $target) 100.0}
.action{end}
<span style="background-color: rgba(175,184,193,0.2); width: 100%; display: inline-block; height: 16px; border-radius: 6px; align-self: center; overflow: hidden; position: relative; font-family: 霞鹜文楷屏幕阅读版, sans-serif;">
    <span style="text-align: right; font-size: 11px; width: .action{$pct}%; background-color: rgba(57,197,187,0.85); display: inline-block; height: inherit; vertical-align: top; color: white; padding-right: 5px; line-height: 15px;">.action{printf "%.1f" $pct}%</span>
    <span style="position: absolute; right: 5px; top: 0; bottom: 0; color: #555; font-size: 10px; display: flex; align-items: center;">.action{$done} / .action{$target}</span>
</span>
```