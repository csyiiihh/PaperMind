from services.text_splitter import clean_pdf_text

text = """The network has difﬁculties in learning.
It can asymptoti-
cally approximate the residual function.
The ﬂow of information is important."""

result = clean_pdf_text(text)

print("===== 清洗结果 =====")
print(result)

assert "difficulties" in result
assert "asymptotically" in result
assert "flow" in result

print("\n测试通过！")