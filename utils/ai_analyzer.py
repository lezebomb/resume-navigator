"""
========================================
AI 分析模块
========================================
功能:
  1. 调用 Google Gemini API 进行简历 vs JD 深度诊断
  2. 构建专业的诊断 Prompt（6大维度）
  3. 返回结构化的诊断结果
========================================
"""

from google import genai
import json
import re


def get_client(api_key):
    """根据传入的 API Key 创建 Gemini 客户端"""
    return genai.Client(api_key=api_key)


def analyze_resume(resume_text, jd_text, industry_insights, api_key):
    """
    调用 Gemini AI 对简历进行深度诊断分析。
    
    参数:
        resume_text (str): 从简历中提取的文字内容
        jd_text (str): 用户粘贴的目标岗位 JD
        industry_insights (str): 全网搜索提炼的行业情报（Markdown 格式）
        api_key (str): Gemini API Key
    
    返回:
        dict: 结构化的诊断结果，包含各维度评分和建议
    """
    
    # ============================================================
    # 构建专业的诊断 Prompt（核心中的核心！）
    # ============================================================
    prompt = f"""
你是一位顶级的 ATS（Applicant Tracking System，自动简历追踪系统）专家和资深 HR 顾问。
你深谙2026年各大公司最新的 ATS 算法逻辑和 HR 筛选习惯。

现在请你对以下简历进行深度诊断，对比目标岗位 JD，从6个维度进行分析。

## 目标岗位 JD（招聘要求）：
{jd_text}

## 真实全网行业情报（作为你的严苛评审依据）：
{industry_insights}

## 求职者简历内容：
{resume_text}

## 请严格按照以下 JSON 格式输出诊断结果（不要输出任何其他内容）：

{{
    "overall_score": 75,
    "overall_comment": "对简历整体的一句话总结评价",
    
    "hard_skills": {{
        "score": 70,
        "matched": ["JD中要求的且简历中已有的硬技能列表"],
        "missing": ["JD中要求的但简历中缺失的硬技能列表"],
        "suggestion": "针对硬技能缺失的具体改进建议"
    }},
    
    "soft_skills": {{
        "score": 80,
        "matched": [{{"jd_skill": "JD要求的软技能", "resume_evidence": "简历中对应的表述"}}],
        "missing": ["JD中要求但简历中完全没有体现的软技能"],
        "suggestion": "针对软技能的改进建议"
    }},
    
    "quantification": {{
        "score": 60,
        "good_examples": ["简历中已经有量化数据的好句子"],
        "needs_improvement": [{{"original": "简历中缺乏数据的原句", "improved": "使用'动作+数字化成果'句式改写后的建议"}}],
        "suggestion": "关于量化指标的总体建议"
    }},
    
    "anti_cheating": {{
        "score": 90,
        "issues": ["检测到的关键词堆砌或不自然用法"],
        "suggestion": "如何将关键词自然融入项目经历的建议"
    }},
    
    "keyword_density": {{
        "score": 75,
        "high_frequency_jd_keywords": ["JD中出现频率最高的关键词"],
        "resume_keyword_coverage": "简历对JD核心关键词的覆盖率描述",
        "suggestion": "如何提升关键词覆盖的建议"
    }},
    
    "expansion_suggestions": {{
        "certificates": ["推荐考取的高含金量证书及原因"],
        "experiences": ["建议补充的经历或项目"],
        "skills_to_learn": ["建议学习的技能及原因"],
        "suggestion": "拓展建议的总体说明"
    }}
}}

## 评分标准：
- 90-100：优秀，基本可以直接通过 ATS 筛选
- 75-89：良好，有一些可优化的地方
- 60-74：一般，需要较多修改
- 0-59：较差，建议大幅重写

## 注意事项：
1. 硬技能匹配必须检查工具名、编程语言、框架、平台等专业术语的字面匹配
2. 软技能分析要能识别语义相似的表达（如"跨部门沟通"≈"团队协作"）
3. 量化指标检查要关注是否有百分比、金额、时间、人数等数字
4. 反作弊检测要看是否在简历末尾堆砌了大量不相关的关键词
5. 拓展建议要结合具体的 JD 岗位来推荐，不要泛泛而谈
6. 所有建议必须具体可操作，不要说空话
7. 必须将求职者的简历与上述《真实全网行业情报》进行对比！如果简历中缺失了情报里标为【必须】的硬技能，或者踩中了【致命淘汰红线】，必须在评分上予以重罚，并在 suggestion 中明确指出是根据行业真实面经得出的结论。
"""

    try:
        # 调用 Gemini API
        client = get_client(api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        
        # 提取返回的文本
        result_text = response.text or ""
        
        # 尝试从返回文本中提取 JSON
        json_match = re.search(r'\{[\s\S]*\}', result_text)
        if json_match:
            result_dict = json.loads(json_match.group())
            return {"success": True, "data": result_dict}
        else:
            return {"success": False, "error": "AI 返回的内容格式异常，请重试。", "raw": result_text}
    
    except Exception as e:
        return {"success": False, "error": f"AI 调用失败: {str(e)}"}


def generate_improved_resume(resume_text, jd_text, api_key):
    """
    调用 AI 生成优化后的简历文本。
    
    参数:
        resume_text (str): 原始简历文本
        jd_text (str): 目标岗位 JD
        api_key (str): Gemini API Key
    
    返回:
        dict: {"success": True, "improved_text": "优化后文本"} 或错误
    """
    
    prompt = f"""你是一位顶级简历优化专家。请根据目标岗位 JD，对以下简历进行深度优化改写。

优化要求：
1. 保留所有真实信息：不要编造经历、公司名称或数据，只能对已有内容进行润色
2. 结构优化：按"个人信息→求职意向→教育背景→工作经历→项目经历→专业技能→自我评价"排列
3. 用词优化：将"参与""负责"等弱动词替换为"主导""设计""推动"等强动词
4. 量化表达：在合理范围内补充量化描述
5. 关键词植入：自然地融入 JD 中的核心关键词，不要堆砌
6. ATS 友好：使用标准标题名称
7. 每段经历使用 STAR 法则重写
8. 语言风格要像真人写的，降低AI痕迹，用自然、专业的中文表达

目标岗位 JD：
{jd_text}

原始简历内容：
{resume_text}

【严格输出格式要求】：
- 直接输出优化后的简历纯文本内容
- 禁止使用任何 Markdown 符号：不要使用 **（加粗）、##（标题）、###、- （列表）、*（星号）等
- 标题直接写文字即可（如：个人信息、教育背景、工作经历），不要加任何符号前缀
- 列表项使用中文序号（1.、2.、3.）或直接分行书写
- 不要输出解释性文字，只输出简历本身
- 所有内容用纯文本格式，适合直接复制到 Word 文档中
- 风格要像真人手写的专业简历，不要有AI化的模板痕迹
"""

    try:
        client = get_client(api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        
        improved_text = response.text or ""
        return {"success": True, "improved_text": improved_text}
    
    except Exception as e:
        return {"success": False, "error": f"AI 调用失败: {str(e)}"}

