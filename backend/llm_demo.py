from services.llm_service import generate_answer


question = "请用两句话解释什么是残差连接。"

print("用户问题：")
print(question)

print("\nDeepSeek 回答：")

answer = generate_answer(question)

print(answer)