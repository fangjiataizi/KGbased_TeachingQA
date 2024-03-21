from typing import Any, Awaitable, Callable, Dict, List

from components.base_component import BaseComponent
from llm.basellm import BaseLLM
from llm.ali_llm import init_message,get_response
from dashscope.api_entities.dashscope_response import Role

system = f"""
你是一个助手，帮助生成基于给定信息的、易于理解的文本回答。最新的提示包含了信息，你需要根据这些信息生成人类可读的回应。让答案听起来像是对问题的回应，不要提及你是基于给定信息得出结果的。不要添加任何在最新提示中没有明确提供的额外信息。我再重复一遍，不要添加任何未明确给出的信息。请尽可能让答案简洁，且不要超过50个词。
"""
system = f"""
你是一个教学设计专家，你需要根据用户的问题来帮助用户进行教学设计，你给出的教学设计一定是要与用户问题相关，并且必须至少需要包括：教学内容、学习目标、教学活动设计、总结四个部分。
"""


def remove_large_lists(d: Dict[str, Any]) -> Dict[str, Any]:
    """
    The idea is to remove all properties that have large lists (embeddings) or text as values
    """
    LIST_CUTOFF = 56
    CHARACTER_CUTOFF = 5000
    # iterate over all key-value pairs in the dictionary
    for key, value in d.items():
        # if the value is a list and has more than list cutoff elements
        if isinstance(value, list) and len(value) > LIST_CUTOFF:
            d[key] = None
        # if the value is a string and has more than list cutoff elements
        if isinstance(value, str) and len(value) > CHARACTER_CUTOFF:
            d[key] = d[key][:CHARACTER_CUTOFF]
        # if the value is a dictionary
        elif isinstance(value, dict):
            # recurse into the nested dictionary
            remove_large_lists(d[key])
    return d


class SummarizeCypherResult(BaseComponent):
    llm: BaseLLM
    exclude_embeddings: bool

    def __init__(self, llm: BaseLLM, exclude_embeddings: bool = True) -> None:
        self.llm = llm
        self.exclude_embeddings = exclude_embeddings

    def generate_user_prompt(self, question: str, results: List[Dict[str, str]]) -> str:
        return f"""
        用户的问题是： {question}
        请基于下面这些结果来回答这个问题：
        {[remove_large_lists(el) for el in  results] if self.exclude_embeddings else results}
        """

    def run(
        self,
        question: str,
        results: List[Dict[str, Any]],
    ) -> Dict[str, str]:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": self.generate_user_prompt(question, results)},
        ]

        output = self.llm.generate(messages)
        return output

    async def run_async(
        self,
        question: str,
        results: List[Dict[str, Any]],
        callback: Callable[[str], Awaitable[Any]] = None,
    ) -> Dict[str, str]:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": self.generate_user_prompt(question, results)},
        ]
        # output = await self.llm.generateStreaming(messages, onTokenCallback=callback)
        output=get_response(messages)
        return "".join(output)
