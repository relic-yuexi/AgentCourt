from typing import List, Dict, Any, Tuple
import re
import json
from LLM.deli_client import search_law
import uuid
import logging


class Agent:
    def __init__(
        self,
        id: int,
        name: str,
        role: str,
        description: str,
        llm: Any,
        db: Any,
        log_think=False,
    ):
        self.id = id
        self.name = name
        self.role = role
        self.description = description
        self.llm = llm
        self.db = db
        self.log_think = log_think

        self.logger = logging.getLogger(__name__)

    def __str__(self):
        return f"{self.name} ({self.role})"

    # --- Plan Phase --- #

    def plan(self, history_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        if self.log_think:
            self.logger.info(f"Agent ({self.role}) starting planning phase")
        history_context = self.prepare_history_context(history_list)
        plans = self._get_plan(history_context)
        if self.log_think:
            self.logger.info(f"Agent ({self.role}) generated plans: {plans}")
        queries = self._prepare_queries(plans, history_context)
        if self.log_think:
            self.logger.info(f"Agent ({self.role}) prepared queries: {queries}")

        return {"plans": plans, "queries": queries}

    def _get_plan(self, history_context: str) -> Dict[str, bool]:
        instruction = f"You are a {self.role}. {self.description}\n\n"
        prompt = "Based on the court history, analyze whether information from the experience, case, or legal database is needed. Return a JSON string with three key-value pairs for experience, case, and legal, with values being true or false."
        response = self.llm.generate(
            instruction=instruction, prompt=prompt + "\n\n" + history_context
        )
        return self._extract_plans(self.extract_response(response))

    def _prepare_queries(
        self, plans: Dict[str, bool], history_context: str
    ) -> Dict[str, str]:
        queries = {}
        if plans["experience"]:
            queries["experience"] = self._prepare_experience_query(history_context)
        if plans["case"]:
            queries["case"] = self._prepare_case_query(history_context)
        if plans["legal"]:
            queries["legal"] = self._prepare_legal_query(history_context)
        return queries

    def _prepare_experience_query(self, history_context: str) -> str:
        instruction = f"You are a {self.role}. {self.description}\n\n"
        prompt = """
        Based on the court history, analyze what kind of experience information is needed.
        Identify the key points and formulate a query to retrieve relevant experiences that can improve logic.
        Provide a JSON string containing query statement.
        like 
        {{
            'query':'劳动争议 处理方法 具体步骤'
        }}
        """
        response = self.llm.generate(
            instruction=instruction, prompt=prompt + "\n\n" + history_context
        )
        return self.extract_response(response)

    def _prepare_case_query(self, history_context: str) -> str:
        instruction = f"You are a {self.role}. {self.description}\n\n"
        prompt = """
        Based on the court history, analyze what kind of case information is needed.
        Identify the key points and formulate a query to retrieve relevant case precedents that can improve agility.
        Provide a JSON string containing query keywords.
        like 
        {{
            'query':'劳动合同纠纷 判决 分析'
        }}
        """
        response = self.llm.generate(
            instruction=instruction, prompt=prompt + "\n\n" + history_context
        )
        return self.extract_response(response)

    def _prepare_legal_query(self, history_context: str) -> str:
        instruction = f"You are a {self.role}. {self.description}\n\n"
        prompt = """
        Based on the court history, analyze what kind of legal information is needed.
        Identify the relevant laws or regulations, such as Civil Law, Labor Law, Family Law, or Labor Dispute, and formulate a query to retrieve relevant legal references that can improve professionalism.
        Provide a JSON string containing query keywords.
        like 
        {{
            'query':'侵权人行为 法律条文'
        }}
        """
        response = self.llm.generate(
            instruction=instruction, prompt=prompt + "\n\n" + history_context
        )
        return self.extract_response(response)

    # --- Do Phase --- #

    def execute(
        self, plan: Dict[str, Any], history_list: List[Dict[str, str]], prompt: str
    ) -> str:
        if not plan:
            context = self.prepare_history_context(history_list)
        else:
            context = self._prepare_context(plan, history_list)
        return self.speak(context, prompt)

    def speak(self, context: str, prompt: str) -> str:
        instruction = f"You are a {self.role}. {self.description}\n\n"
        full_prompt = f"{context}\n\n{prompt}"
        return self.llm.generate(instruction=instruction, prompt=full_prompt)

    def _prepare_context(
        self, plan: Dict[str, Any], history_list: List[Dict[str, str]]
    ) -> str:
        context = ""
        queries = plan["queries"]

        if "experience" in queries:
            experience_context = self.db.query_experience_metadatas(
                queries["experience"], n_results=3
            )
            context += (
                f"\n遵循下面的经验，以增强回复的逻辑严密性:\n{experience_context}\n"
            )

        if "case" in queries:
            case_context = self.db.query_case_metadatas(queries["case"], n_results=3)
            context += f"\nCase Context:\n{case_context}\n"

        if "legal" in queries:
            legal_context = self.db.query_legal(queries["legal"], n_results=3)
            context += f"\nLaw Context:\n{legal_context}\n"

        if self.log_think:
            self.logger.info(f"Agent ({self.role})\n\n{context}")

        history_context = self.prepare_history_context(history_list)
        context += "\nCommunication History:\n" + history_context + "\n"

        return context

    # --- Reflect Phase --- #

    def reflect(self, history_list: List[Dict[str, str]]):

        history_context = self.prepare_history_context(history_list)

        case_content = self.prepare_case_content(history_context)

        # Legal knowledge base reflection
        legal_reflection = self._reflect_on_legal_knowledge(history_context)
        if self.log_think:
            self.logger.info(f"Agent ({self.role})\n\n{legal_reflection}")

        # Experience reflection
        experience_reflection = self._reflect_on_experience(
            case_content, history_context
        )
        if self.log_think:
            self.logger.info(f"Agent ({self.role})\n\n{experience_reflection}")

        # Case reflection
        case_reflection = self._reflect_on_case(case_content, history_context)
        if self.log_think:
            self.logger.info(f"Agent ({self.role})\n\n{case_reflection}")

        return {
            "legal_reflection": legal_reflection,
            "experience_reflection": experience_reflection,
            "case_reflection": case_reflection,
        }

    def _reflect_on_legal_knowledge(self, history_context: str) -> Dict[str, Any]:
        # Determine if legal reference is needed
        need_legal = self._need_legal_reference(history_context)

        if need_legal:
            query = self._prepare_legal_query(history_context)
            laws = search_law(query)

            processed_laws = []
            for law in laws[:3]:  # Limit to 3 laws
                law_id = str(uuid.uuid4())
                processed_law = self._process_law(law)
                self.add_to_legal(
                    law_id, processed_law["content"], processed_law["metadata"]
                )
                processed_laws.append(processed_law)

            return {"needed_reference": True, "query": query, "laws": processed_laws}
        else:
            return {"needed_reference": False}

    def _need_legal_reference(self, history_context: str) -> bool:
        instruction = (
            f"You are a {self.role}. {self.description}\n\n"
            "Review the provided court case history and evaluate its thoroughness and professionalism. "
            "Determine if referencing specific legal statutes or regulations would enhance the quality of the response. "
            "Return 'true' if additional legal references are needed, otherwise return 'false'."
        )
        prompt = (
            "Court Case History:\n\n"
            + history_context
            + "\n\nIs additional legal reference needed? Output true unless it is absolutely unnecessary. Provide only a simple 'true' or 'false' answer."
        )
        response = self.llm.generate(instruction=instruction, prompt=prompt)

        cleaned_response = response.strip().lower()

        # 检查响应是否包含 'true' 或 'false'
        if "true" in cleaned_response:
            return True
        elif "false" in cleaned_response:
            return False
        else:
            return False

    def _process_law(self, law: dict) -> Dict[str, Any]:

        law_content = (
            law["lawsName"] + " " + law["articleTag"] + " " + law["articleContent"]
        )

        return {
            "content": law_content,
            "metadata": {"lawName": law["lawsName"], "articleTag": law["articleTag"]},
        }

    def _reflect_on_experience(
        self, case_content: str, history_context: str
    ) -> Dict[str, Any]:

        experience = self._generate_experience_summary(case_content, history_context)

        experience_entry = {
            "id": str(uuid.uuid4()),
            "content": experience["context"],  # 这里面放的应该是案件相关的描述
            "metadata": {
                "context": experience["content"],  # 这里面放的应该是案件相关的指导用
                "focusPoints": experience["focus_points"],
                "guidelines": experience["guidelines"],
            },
        }

        # Add to experience database
        self.add_to_experience(
            experience_entry["id"],
            experience_entry["content"],
            experience_entry["metadata"],
        )

        return experience_entry

    def _generate_experience_summary(
        self, case_content: str, history_context: str
    ) -> Dict[str, Any]:
        instruction = f"你是{self.role}。{self.description}\n\n"

        prompt = f"""
        根据以下案例内容和对话历史，生成一个逻辑上连贯的经验总结。请确保回复内容逻辑严密，并能有效指导类似案件的处理。

        案例内容: {case_content}
        对话历史: {history_context}

        请在回复中提供以下内容：
        1. 一个简要的案件背景描述，包括案件的主要争议点和各方立场，不要出现真实人名。
        2. 一个专注于逻辑连贯性的经验描述（内容），包括在处理此类案件时应重点关注的问题和策略。
        3. 有助于逻辑连贯性的3-5个关键点，具体说明如何在实际处理中应用这些关键点。
        4. 保持逻辑连贯性的3-5个指南，提供在处理类似案件时需要特别注意的事项和建议。

        将你的回复格式化为以下结构的JSON对象：
        {{
            "context": "简要背景...",
            "content": "专注于逻辑连贯性的经验描述...",
            "focus_points": "关键点1, 关键点2, 关键点3",
            "guidelines": "指南1, 指南2, 指南3"
        }}
        """

        response = self.llm.generate(instruction, prompt)

        data = self.extract_response(response)

        # 将列表转换为字符串
        return self.ensure_ex_string_fields(data)
        # if data and isinstance(data, dict):
        #    for key, value in data.items():
        #        if isinstance(value, list):
        #           data[key] = ", ".join(value)
        # return data

    def _reflect_on_case(
        self, case_content: str, history_context: str
    ) -> Dict[str, Any]:

        case_summary = self._generate_case_summary(case_content, history_context)

        case_entry = {
            "id": str(uuid.uuid4()),
            "content": case_summary["content"],
            "metadata": {
                "caseType": case_summary["case_type"],
                "keywords": case_summary["keywords"],
                "quick_reaction_points": case_summary["quick_reaction_points"],
                "response_directions": case_summary["response_directions"],
            },
        }

        # Add to case database
        self.add_to_case(
            case_entry["id"], case_entry["content"], case_entry["metadata"]
        )

        return case_entry

    def _generate_case_summary(
        self, case_content: str, history_context: str
    ) -> Dict[str, Any]:
        instruction = f"你是一个{self.role}，擅长快速分析案例并提供敏捷的回应。{self.description}\n\n"

        prompt = f"""
        根据以下案例内容和对话历史，生成一个简洁的案例摘要，以提高在类似情况下回应的敏捷性。请确保回复内容能够帮助快速理解案情并迅速制定回应策略。

        案例内容: {case_content}
        对话历史: {history_context}

        请在回复中提供以下内容：
        1. 案例名称及背景：给出一个凝练的案例名称，并简要描述案件的背景，包括主要争议点和各方立场，不要使用真实人名。
        2. 案件类型：说明这是什么类型的案件（如劳动争议、合同纠纷等）。
        3. 关键词：提供3-5个能够快速捕捉案件本质的关键词。
        4. 快速反应点：列出3-5个对于快速理解和处理此类案件至关重要的要点。
        5. 回应方向：提供3-5个可能的回应方向或角度，以便快速制定回应策略。

        将你的回复格式化为以下结构的JSON对象：
        {{
            "content": "案例名称及背景：...",
            "case_type": "案件类型...",
            "keywords": "关键词1, 关键词2, 关键词3",
            "quick_reaction_points": "要点1, 要点2, 要点3",
            "response_directions": "方向1, 方向2, 方向3"
        }}

        注意：内容应该简洁明了，便于快速识别核心问题和制定回应策略。重点放在能够提高思维敏捷性的信息上,注意格式是上面描述的json。
        """

        response = self.llm.generate(instruction, prompt)

        data = self.extract_response(response)

        # 确保是字符串
        return self.ensure_case_string_fields(data)
        # if data and isinstance(data, dict):
        #    for key, value in data.items():
        #        if isinstance(value, list):
        #            data[key] = ", ".join(value)
        # return data

    # --- Helper Methods --- #

    def extract_json_from_txt(self, response: str) -> Any:
        pattern = r"\{.*?\}"
        match = re.search(pattern, response, re.DOTALL)
        json_str = match.group()

        data = json.loads(json_str)
        return data

    def extract_response(self, response: str) -> Any:
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            try:
                cleaned_json_str = re.sub(r"[\x00-\x1F\x7F]", "", json_match.group())
                return json.loads(cleaned_json_str, strict=False)
            except json.JSONDecodeError:
                pass
        return response.strip()

    def _extract_plans(self, plans_str: str) -> Dict[str, bool]:
        try:
            plans = plans_str if isinstance(plans_str, dict) else json.loads(plans_str)
            return {
                "experience": plans.get("experience", False),
                "case": plans.get("case", False),
                "legal": plans.get("legal", False),
            }
        except json.JSONDecodeError:
            return {"experience": False, "case": False, "legal": False}

    def add_to_experience(
        self, id: str, document: str, metadata: Dict[str, Any] = None
    ):
        self.db.add_to_experience(id, document, metadata)

    def add_to_case(self, id: str, document: str, metadata: Dict[str, Any] = None):
        self.db.add_to_case(id, document, metadata)

    def add_to_legal(self, id: str, document: str, metadata: Dict[str, Any] = None):
        self.db.add_to_legal(id, document, metadata)

    def prepare_history_context(self, history_list: List[Dict[str, str]]) -> str:
        formatted_history = []
        for entry in history_list:
            role = entry["role"]
            name = entry["name"]
            content = entry["content"].replace("\n", "\n  ")
            formatted_entry = f"{role} ({name}):\n  {content}"
            formatted_history.append(formatted_entry)
        return "\n\n".join(formatted_history)

    def prepare_case_content(self, history_context: str) -> str:
        instruction = f"你是一个专业的法官。擅长总结案件情况。\n\n"

        prompt = "请根据法庭历史，用三句话总结案件情况。"

        response = self.llm.generate(
            instruction=instruction, prompt=prompt + "\n\n" + history_context
        )

        return response
    
    # 可选项：可以采用打分的方式进行反思
    def _evaluate_response(self, case_content: str, response: str) -> Dict[str, int]:
        instruction = ""
        prompt = f"""
        请根据案件情况对以下回答进行评估，从思维敏捷性、知识专业性和逻辑严密性三个角度给出1到5的评分：
        案件内容：
        {case_content}
        回答内容：
        {response}
        
        请按以下格式输出评分结果：
        {{
            "agility": 评分,
            "professionalism": 评分,
            "logic": 评分
        }}
        """

        evaluation_result = self.llm.generate(instruction, prompt)
        return json.loads(evaluation_result)

    def ensure_ex_string_fields(self, data):
        """
        确保 data 中的特定字段是字符串。
        """
        fields_to_check = {
            "context": str,
            "content": str,
            "focus_points": lambda x: ", ".join(x) if isinstance(x, list) else x,
            "guidelines": lambda x: ", ".join(x) if isinstance(x, list) else x,
        }

        for field, validator in fields_to_check.items():
            if field in data:
                if callable(validator):
                    data[field] = validator(data[field])
                elif not isinstance(data[field], validator):
                    raise ValueError(f"{field} must be a {validator.__name__}")

        return data

    def ensure_case_string_fields(self, data):
        """
        确保 data 中的特定字段是字符串。
        """
        fields_to_check = [
            "content",
            "case_type",
            "keywords",
            "quick_reaction_points",
            "response_directions",
        ]

        for field in fields_to_check:
            if field in data:
                if isinstance(data[field], list):
                    data[field] = ", ".join(data[field])
                elif not isinstance(data[field], str):
                    raise ValueError(f"{field} must be a list or a string")

        return data
