import pymupdf

from services.text_splitter import clean_pdf_text

PAPER_ID = "96a453e6-9e85-4aef-9545-75487b7aa4dc"
PDF_PATH = f"uploads/{PAPER_ID}.pdf"

# 1. 提取 PDF 第3页
with pymupdf.open(PDF_PATH) as doc:
    original_text = doc[2].get_text("text")

# 2. 清洗文本
cleaned_text = clean_pdf_text(original_text)

# 3. 对比清洗前后
print("原始文本长度：", len(original_text))
print("清洗后长度：", len(cleaned_text))

print("\n===== 断词修复检查 =====")
print("原始文本包含 asymptoti-：", "asymptoti-" in original_text)
print("清洗后包含 asymptotically：", "asymptotically" in cleaned_text)

print("\n===== 连字修复检查 =====")
print("清洗后包含 difficulties：", "difficulties" in cleaned_text)

# 4. 检查公式是否仍然存在
print("\n===== 公式检查 =====")

formula_1 = "y = F(x, {Wi}) + x."
formula_2 = "y = F(x, {Wi}) + Wsx."

print("公式（1）保留：", formula_1 in cleaned_text)
print("公式（2）保留：", formula_2 in cleaned_text)

# 5. 输出公式附近的上下文
pos = cleaned_text.find("y = F(x")

if pos != -1:
    print("\n===== 公式附近文本 =====")
    print(cleaned_text[max(0, pos - 150):pos + 500])