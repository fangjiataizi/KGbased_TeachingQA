import re
from typing import Any, Dict, List, Union

from components.base_component import BaseComponent
from driver.neo4j import Neo4jDatabase
from llm.basellm import BaseLLM
from llm.ali_llm import init_message,get_response
from dashscope.api_entities.dashscope_response import Role

def remove_relationship_direction(cypher):
    return cypher.replace("->", "-").replace("<-", "-")


class Text2Cypher(BaseComponent):
    def __init__(
        self,
        llm: BaseLLM,
        database: Neo4jDatabase,
        use_schema: bool = True,
        cypher_examples: str = "",
        ignore_relationship_direction: bool = True,
    ) -> None:
        self.llm = llm
        self.database = database
        self.cypher_examples = cypher_examples
        self.ignore_relationship_direction = ignore_relationship_direction
        if use_schema:
            self.schema = database.schema

    def get_system_message(self) -> str:
        system = """
        你的任务是将关于Neo4j数据库内容的问题转换为Cypher查询，以查询Neo4j数据库。只使用提供的关系类型和属性。不要使用任何未提供的其他关系类型或属性。
        """
        if self.schema:
            system += f"""
            如果你无法根据提供的模式生成Cypher语句，需要向用户解释原因。
            Schema:
            {self.schema}
            """
        if self.cypher_examples:
            system += f"""
            你需要参考这些Cypher示例来构建Cypher语句。
            {self.cypher_examples}
            """
        # Add note at the end and try to prevent LLM injections
        system += """注意：在你的回答中不要包含任何解释或道歉。
不要回答任何可能要求你做出除构建Cypher语句之外的任何事情的问题。
除生成的Cypher语句外，不要包含任何文本。如果你想得到报酬，这一点非常重要。
始终为LLM提供足够的上下文，以便能够生成有效的回应。
请用三个反引号 (`) 包裹生成的Cypher语句。
                     """
        return system

    def construct_cypher(self, question: str, history=[]) -> str:
        messages = init_message(self.get_system_message())
        # messages.extend(history)
        messages.append(
            {
                "role": Role.USER,
                "content": question,
            }
        )
        print([el for el in messages if not el["role"] == "system"])
        cypher = get_response(messages)
        return cypher

        # messages = [{"role": "system", "content": self.get_system_message()}]
        # messages.extend(history)
        # messages.append(
        #     {
        #         "role": "user",
        #         "content": question,
        #     }
        # )
        # print([el for el in messages if not el["role"] == "system"])
        # cypher = self.llm.generate(messages)
        # return cypher

    def run(
        self, question: str, history: List = [], heal_cypher: bool = True
    ) -> Dict[str, Union[str, List[Dict[str, Any]]]]:
        # Add prefix if not part of self-heal loop
        final_question = (
            "需要转换为Cypher的问题: " + question
            if heal_cypher
            else question
        )
        cypher = self.construct_cypher(final_question, history)
        # finds the first string wrapped in triple backticks. Where the match include the backticks and the first group in the match is the cypher
        match = re.search("```([\w\W]*?)```", cypher)

        # If the LLM didn't any Cypher statement (error, missing context, etc..)
        if match is None:
            return {"output": [{"message": cypher}], "generated_cypher": None}
        extracted_cypher = match.group(1)

        if self.ignore_relationship_direction:
            extracted_cypher = remove_relationship_direction(extracted_cypher)

        print(f"Generated cypher: {extracted_cypher}")

        output = self.database.query(extracted_cypher)
        print("neo4j return result:{}".format(output))
        # Catch Cypher syntax error
        if heal_cypher and output and output[0].get("code") == "invalid_cypher":
            # syntax_messages = [{"role": "system", "content": self.get_system_message()}]
            syntax_messages =init_message(self.get_system_message())
            syntax_messages.extend(
                [
                    {"role": Role.USER, "content": question},
                    {"role": Role.ASSISTANT, "content": cypher},
                ]
            )
            # Try to heal Cypher syntax only once
            return self.run(
                output[0].get("message"), syntax_messages, heal_cypher=False
            )

        return {
            "output": output,
            "generated_cypher": extracted_cypher,
        }
