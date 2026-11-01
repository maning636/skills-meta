# -*- coding: utf-8 -*-
import io

P = r"D:\研究\库体系\03-库体系总图.md"
t = io.open(P, encoding="utf-8").read()
old = "（HumanLayer 3 个已全部移除；heygen hyperframes 5 个与制图类 5 个已于 2026-10-31 移除）"
new = "（HumanLayer 3 个已全部移除；第三方 hyperframes 5 个与制图类 5 个已于 2026-10-31 移除）"
assert old in t
io.open(P, "w", encoding="utf-8", newline="\n").write(t.replace(old, new, 1))
print("OK 03")
