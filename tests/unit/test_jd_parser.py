from __future__ import annotations

import unittest

from backend.services.jd.parser import parse_job_description


class JobDescriptionParserTests(unittest.TestCase):
    def test_extracts_core_fields(self) -> None:
        jd_text = """
        公司：某消费互联网公司
        岗位：数据分析师
        工作地点：上海
        任职要求：
        1. 本科及以上学历，3年以上数据分析经验
        2. 熟悉 Python、SQL、Excel、Power BI
        3. 具备良好的沟通与团队协作能力
        4. 有电商行业经验优先
        """

        jd = parse_job_description(jd_text)

        self.assertEqual(jd.company_name, "某消费互联网公司")
        self.assertEqual(jd.role_title, "数据分析师")
        self.assertEqual(jd.location, "上海")
        self.assertEqual(jd.education_requirement, "本科")
        self.assertEqual(jd.years_experience, "3")
        self.assertIn("python", jd.hard_skills)
        self.assertIn("sql", jd.hard_skills)
        self.assertIn("communication", jd.soft_skills)


if __name__ == "__main__":
    unittest.main()
