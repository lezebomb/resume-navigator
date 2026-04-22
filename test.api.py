from openai import OpenAI
import os

API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
BASE_URL = os.getenv("OPENAI_BASE_URL", "").strip()
MODEL = os.getenv("OPENAI_MODEL", "").strip() or "gpt-4o-mini"

if not API_KEY:
    print("❌ 请先设置环境变量 OPENAI_API_KEY")
else:
    try:
        client = OpenAI(api_key=API_KEY, base_url=BASE_URL) if BASE_URL else OpenAI(api_key=API_KEY)
        print("正在连接模型，请稍候...\n")

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": "你好！如果你收到这条消息，请简短回复：模型连接成功，可以开始分析简历。"},
            ],
        )

        reply = response.choices[0].message.content if response.choices else ""
        print("✅ AI 回复：", reply)
    except Exception as e:
        print(f"\n❌ 连接失败: {e}")
