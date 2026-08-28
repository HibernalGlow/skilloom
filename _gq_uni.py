# -*- coding: utf-8 -*-
"""Universal mechanical fixer for 20-整理 files (middle-template -> gates-friendly)."""
import io, re, sys

def C(n): return '{: style="color: var(--b3-font-color%d);"}' % n

IAL = re.compile(r"\{:\s*[^}\n]*\}")
PNCT = re.compile(r"[，。；：、,.!?！？（）()《》\[\]{} \t]")
STYLED_SPAN = re.compile(r"\*\*[^*\n]+\*\*\{:\s*style=\"[^\"]*\"\}")

def plain_of(raw):
    p = IAL.sub("", raw)
    p = re.sub(r"</?(?:u|em|strong|span)\b[^>]*>", "", p)
    p = p.replace("**", "").replace("~~", "").replace("==", "").replace("`", "")
    return PNCT.sub("", p)

def raw_span(body, frag):
    mapping = []
    raw = body
    i = 0
    while i < len(raw):
        m = IAL.match(raw, i)
        if m:
            i = m.end(); continue
        ch = raw[i]
        if ch in "*~=`":
            i += 1; continue
        if ch == "<":
            m2 = re.match(r"</?(?:u|em|strong|span)\b[^>]*>", raw[i:])
            if m2:
                i += m2.end(); continue
        if PNCT.match(ch):
            i += 1; continue
        mapping.append((i, ch))
        i += 1
    plain = "".join(c for _, c in mapping)
    p0 = plain.find(frag)
    if p0 < 0:
        return None
    s = mapping[p0][0]
    e = mapping[p0 + len(frag) - 1][0] + 1
    # round to include full styled spans
    for m in STYLED_SPAN.finditer(body):
        if m.start() < e and m.end() > s:
            s = min(s, m.start()); e = max(e, m.end())
    return s, e

def restrike(line):
    m = re.match(r"^(- ❌ ([A-D])项) ~~(.*)~~$", line.rstrip())
    if not m:
        return line
    prefix, body = m.group(1), m.group(3)
    plain = plain_of(body)
    if len(plain) < 8:
        return line
    last = max(plain.rfind("，"), plain.rfind(","), plain.rfind("；"), plain.rfind(";"))
    frag = None
    if last >= int(len(plain) * 0.25) and last <= int(len(plain) * 0.85):
        frag = plain[last + 1:]
    if frag is None or len(frag) < 2:
        frag = plain[int(len(plain) * 0.45):]
    span = raw_span(body, frag)
    if span is None:
        return line
    s, e = span
    return "%s %s~~%s~~%s" % (prefix, body[:s], body[s:e], body[e:])

def split_name_subjects(text):
    pat = re.compile(r"\*\*([^*\n]{1,2})([甲乙丙丁戊])\*\*(\{:\s*style=\"[^\"]*\"\})")
    def repl(m):
        return m.group(1) + "**" + m.group(2) + "**" + m.group(3)
    return pat.sub(repl, text)

def style_bare(text, term, color):
    pat = re.compile(r"(?<!\*)" + re.escape(term) + r"(?!\*)")
    lines = text.split("\n")
    out, in_fence, in_question = [], False, True
    for line in lines:
        if line.startswith("##### "):
            in_question = True
        elif line.strip() == '{: custom-qb-section="solution"}':
            in_question = False
        if line.strip().startswith(("```", "> ```")):
            in_fence = not in_fence
        if not in_question and not in_fence and not line.startswith("|"):
            line = pat.sub(lambda m: "**%s**%s" % (term, C(color)), line)
        out.append(line)
    return "\n".join(out)

def fix_conclusion_families(text):
    # 结论 line: add <u>正解</u> + code around answer letter
    pat = re.compile(r"^-\s+⚖️\s+\*\*结论\*\*\{:[^}]*\}：==当选==\s+\*\*([A-Z]+)\*\*。$", re.M)
    def repl(m):
        return m.group(0).replace("==当选== **" + m.group(1) + "**。", "<u>正解</u>==当选== `" + m.group(1) + "`。")
    return pat.sub(repl, text)

def remove_rule_map(text):
    lines = text.split("\n")
    out = []
    i = 0
    removed = 0
    in_section = False
    while i < len(lines):
        l = lines[i]
        if re.match(r"^###### 规则地图\s*$", l):
            in_section = True
            i += 1; removed += 1
            continue
        if in_section:
            if l.startswith("> ") or re.match(r"^#{1,6} ", l) or re.match(r"^- [✅❌] ", l) or re.match(r"^- [A-D]项 ", l):
                in_section = False
                out.append(l); i += 1; continue
            if l.strip() == "":
                j = i
                while j < len(lines) and lines[j].strip() == "":
                    j += 1
                if j < len(lines) and (lines[j].startswith("> ") or re.match(r"^#{1,6} ", lines[j]) or re.match(r"^- [✅❌] ", lines[j])):
                    i = j; in_section = False
                    continue
                i += 1; removed += 1; continue
            i += 1; removed += 1; continue
        out.append(l)
        i += 1
    return "\n".join(out), removed

def process(path):
    t = open(path, encoding="utf-8").read()
    t, rem = remove_rule_map(t)
    t = split_name_subjects(t)
    lines = t.split("\n")
    lines = [restrike(l) for l in lines]
    t = "\n".join(lines)
    for term, color in [("法院", 11), ("人民法院", 11), ("第三人", 11), ("相对人", 11),
                        ("有效", 8), ("无效", 13), ("成立", 8), ("不成立", 13),
                        ("允许", 8), ("禁止", 13)]:
        t = style_bare(t, term, color)
    t = fix_conclusion_families(t)
    open(path, "w", encoding="utf-8", newline="\n").write(t)
    print("processed %s (removed %d)" % (path.split("/")[-1], rem))

if __name__ == "__main__":
    for p in sys.argv[1:]:
        process(p)