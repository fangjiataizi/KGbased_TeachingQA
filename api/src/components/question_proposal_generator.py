from typing import Any, Dict, List, Union

from components.base_component import BaseComponent
from driver.neo4j import Neo4jDatabase
from llm.basellm import BaseLLM
import re
from llm.ali_llm import init_message,get_response
from dashscope.api_entities.dashscope_response import Role


class QuestionProposalGenerator(BaseComponent):
    def __init__(
        self,
        llm: BaseLLM,
        database: Neo4jDatabase,
    ) -> None:
        self.llm = llm
        self.database = database

    def get_system_message(self) -> str:
        system = f"""
        你的任务是提出一些可能关于Neo4j数据库内容的问题。尽量使问题各不相同。
每个问题应以新的一行分隔，每行只包含一个问题。
为了做到这一点，你需要仔细阅读数据库的模式。因此，仔细阅读模式非常重要。你可以在下面找到模式。
        Schema: 
        {self.database.schema}
        """
        return system

    def get_database_sample(self) -> str:
        return self.database.query(
            """MATCH (n)
                WITH n
                WHERE rand() < 0.3
                RETURN apoc.map.removeKey(n, 'embedding') AS properties, LABELS(n) as labels
                LIMIT 1"""
        )

    def run(self) -> Dict[str, Union[str, List[Dict[str, Any]]]]:
        messages = init_message(self.get_system_message())
        sample = self.get_database_sample()
        messages.append(
            {
                "role": Role.USER,
                "content": f"""请生成关于数据库内容的2个问题。以下是你在生成问题时可以使用的数据库样本：{sample}""",
            }
        )
        print(messages)
        questionsString = get_response(messages)
        questions = [
            # remove number and dot from the beginning of the question
            re.sub(r"\A\d\.?\s*", "", question)
            for question in questionsString.split("\n")
        ]
        return {
            "output": questions,
        }
        # messages = [{"role": "system", "content": self.get_system_message()}]
        # sample = self.get_database_sample()
        # messages.append(
        #     {
        #         "role": "user",
        #         "content": f"""请生成关于数据库内容的1个问题。以下是你在生成问题时可以使用的数据库样本：{sample}""",
        #     }
        # )
        # print(messages)
        # questionsString = self.llm.generate(messages)
        # questions = [
        #     # remove number and dot from the beginning of the question
        #     re.sub(r"\A\d\.?\s*", "", question)
        #     for question in questionsString.split("\n")
        # ]
        # return {
        #     "output": questions,
        # }
