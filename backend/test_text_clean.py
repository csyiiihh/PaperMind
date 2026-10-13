from services.text_splitter import remove_references

text = """
5. Conclusion

We present a residual learning framework.

References

[1] Author A. Paper A.
[2] Author B. Paper B.
"""

result = remove_references(text)

print("清洗后的文本：")
print(result)

print("\n是否包含 References：", "References" in result)