import json
import os
import random
import logging
import argparse
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from tqdm import trange

from EMDB.db import db
from LLM.offlinellm import OfflineLLM
from LLM.apillm import APILLM
from agent import Agent

console = Console()


class CourtSimulation:
    def __init__(self, config_path, case_data, log_level, log_think=False):
        """
        初始化法庭模拟类
        :param config_path: 配置文件路径
        :param case_data: 案例数据（可以是单个文件路径或包含多个案例的目录路径）
        :param log_level: 日志级别
        """
        self.setup_logging(log_level)
        self.config = self.load_json(config_path)
        self.case_data = self.load_case_data(case_data)
        if self.config["llm_type"] == "offline":
            self.llm = OfflineLLM(self.config["model_path"])
        elif self.config["llm_type"] == "apillm":
            self.llm = APILLM(
                api_key=self.config["api_key"],
                api_secret=self.config.get("api_secret", None),
                platform=self.config["model_platform"],
                model=self.config["model_type"],
            )

        self.judge = self.create_agent(self.config["judge"], log_think=log_think)
        self.lawyers = [
            self.create_agent(lawyer, log_think=log_think)
            for lawyer in self.config["lawyers"]
        ]
        self.role_colors = {
            "书记员": "cyan",
            "审判长": "yellow",
            "原告律师": "green",
            "被告律师": "red",
        }

    @staticmethod
    def setup_logging(log_level):
        """
        设置日志配置
        :param log_level: 日志级别
        """
        logging.basicConfig(
            level=log_level,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(rich_tracebacks=True)],
        )

    @staticmethod
    def load_json(file_path):
        """
        加载JSON文件
        :param file_path: 文件路径
        :return: JSON数据
        """
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def load_case_data(case_path):
        """
        加载案例数据
        :param case_path: 案例文件路径或目录路径
        :return: 包含所有案例数据的列表
        """
        cases = []
        with open(case_path, "r", encoding="utf-8") as file:
            for line in file:
                case = json.loads(line)
                cases.append(case)
        return cases

    def create_agent(self, role_config, log_think=False):
        """
        创建角色代理
        :param role_config: 角色配置
        :return: Agent实例
        """
        return Agent(
            id=role_config["id"],
            name=role_config["name"],
            role=role_config.get("role", None),
            description=role_config["description"],
            llm=self.llm,
            db=db(role_config["name"]),
            log_think=log_think,
        )

    def add_to_history(self, role, name, content):
        """
        添加对话到历史记录
        :param role: 说话角色
        :param name: 说话人名字
        :param content: 对话内容
        """
        self.global_history.append({"role": role, "name": name, "content": content})
        color = self.role_colors.get(role, "white")
        console.print(
            Panel(content, title=f"{role} ({name})", border_style=color, expand=False)
        )

    def initialize_court(self):
        """
        初始化法庭
        """
        self.global_history = []
        court_rules = self.config["stenographer"]["court_rules"]
        self.add_to_history("书记员", self.config["stenographer"]["name"], court_rules)
        self.add_to_history(
            "审判长",
            self.judge.name,
            "现在开庭。",
        )
    # 法庭前确认各种事项的例子，可以根据自己需要，采用大模型结合合适的prompt来模拟，此处仅为简化示例
    def confirm_rights_and_obligations(self):
        """
        确认诉讼权利义务
        """
        self.add_to_history(
            "审判长",
            self.judge.name,
            "各方对对方出庭人员有无异议？",
        )
        self.add_to_history(
            "原告律师",
            self.plaintiff.name,
            "无异议",
        )
        self.add_to_history(
            "被告律师",
            self.defendant.name,
            "无异议",
        )
        self.add_to_history(
            "审判长",
            self.judge.name,
            "经核对，到庭当事人及诉讼代理人身份均符合法律规定，可以参加本案的庭审诉讼活动。有关当事人诉讼权利和义务的规定，已于庭前以书面通知形式告知双方当事人。当事人对诉讼权利义务的内容是否清楚？",
        )
        self.add_to_history(
            "原告律师",
            self.plaintiff.name,
            "清楚",
        )
        self.add_to_history(
            "被告律师",
            self.defendant.name,
            "清楚",
        )
        self.add_to_history(
            "审判长",
            self.judge.name,
            "根据民事诉讼法的规定，如双方当事人认为审判人员或书记员是本案当事人、诉讼代理人的近亲属或与本案有直接利害关系或其他关系，可能影响公正审判的，可以提出事实和理由申请回避。当事人是否需要申请回避？",
        )
        self.add_to_history(
            "原告律师",
            self.plaintiff.name,
            "不申请",
        )
        self.add_to_history(
            "被告律师",
            self.defendant.name,
            "不申请",
        )

    def initial_statements(self, case):
        """
        初始陈述
        :param case: 当前案例数据
        """
        self.add_to_history(
            "审判长",
            self.judge.name,
            "首先由原告陈述诉讼请求、事实和理由。",
        )
        self.add_to_history(
            "原告律师", self.plaintiff.name, case["plaintiff_statement"]
        )
        self.add_to_history(
            "审判长",
            self.judge.name,
            "请被告进行答辩。",
        )
        self.add_to_history(
            "被告律师", self.defendant.name, case["defendant_statement"]
        )

    def judge_initial_question(self):
        """
        法官初始提问
        """
        content = self.judge.execute(
            None,
            history_list=self.global_history,
            prompt="根据原告律师、被告律师的陈述，总结双方律师应该针对什么问题进行辩论，你的总结应该在符合现实的基础上，尽量简洁有效。",
        )
        self.add_to_history("审判长", self.judge.name, content)

    def debate_rounds(self, rounds):
        """
        辩论环节
        :param rounds: 辩论轮数
        """
        for i in trange(rounds, desc="Debate Rounds"):
            logging.info(f"Starting debate round {i+1}")
            for role, agent in [
                ("原告律师", self.plaintiff),
                ("被告律师", self.defendant),
            ]:
                p_q = agent.plan(self.global_history)
                content = agent.execute(
                    p_q,
                    self.global_history,
                    prompt=f"根据经验、法条、案例以及法庭对话记录，开始你的辩论。如果你引用了context中的法条库，请把引用的部分说出来。注意：1、当前为法庭辩论环节，而非法庭调查环节。2、你是{role}",
                )
                self.add_to_history(role, agent.name, content)

    def final_judgment(self):
        """
        最终判决
        """
        content = self.judge.speak(
            self.global_history, prompt="法官请做出判决：(你的判决应该符合现实情况。)"
        )
        self.add_to_history("审判长", self.judge.name, content)

    def reflect_and_summary(self):
        """
        反思和总结
        """
        self.plaintiff.reflect(self.global_history)
        self.defendant.reflect(self.global_history)

    def assign_roles(self):
        """
        随机分配角色
        """
        roles = ["plaintiff", "defendant"]
        # random.shuffle(self.lawyers)
        self.plaintiff = self.lawyers[0]
        self.defendant = self.lawyers[1]
        self.plaintiff.role = roles[0]
        self.defendant.role = roles[1]

    def save_progress(self, index):
        """
        记录运行状态
        :param index: 当前案例索引
        """
        progress = {"current_case_index": index}
        with open("progress.json", "w") as f:
            json.dump(progress, f)

    def load_progress(self):
        """
        加载运行状态
        :return: 运行状态字典或None
        """
        if os.path.exists("progress.json"):
            with open("progress.json", "r") as f:
                return json.load(f)
        return None

    def run_simulation(self):
        """
        运行整个法庭模拟过程
        """
        progress = self.load_progress()
        start_index = progress["current_case_index"] if progress else 0

        case_data_to_run = self.case_data[:62]
        for index in range(start_index, len(case_data_to_run)):
            case = case_data_to_run[index]
            console.print(f"\n开始模拟案例 {index + 1}", style="bold")
            console.print("除审判员的其他人员入场", style="bold")
            self.assign_roles()  # 随机分配角色
            self.initialize_court()
            self.confirm_rights_and_obligations()
            self.initial_statements(case)
            self.judge_initial_question()

            rounds = random.randint(3, 5)
            self.debate_rounds(rounds)
            self.save_progress(index)  # 记录当前进度

            self.final_judgment()
            self.reflect_and_summary()
            console.print(f"案例 {index + 1} 庭审结束", style="bold")
            self.save_court_log(
                f"test_result/ours/1/court_session_test_case_{index + 1}.json"
            )

    def save_court_log(self, file_path):
        """
        保存法庭日志
        :param file_path: 保存文件路径
        """
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.global_history, f, ensure_ascii=False, indent=2)
        logging.info(f"Court session log saved to {file_path}")


def parse_arguments():
    """
    解析命令行参数
    :return: 解析后的参数
    """
    parser = argparse.ArgumentParser(description="Run a simulated court session.")
    parser.add_argument(
        "--config",
        default="example_role_config.json",
        help="Path to the role configuration file",
    )
    parser.add_argument(
        "--case",
        default="data/validation.jsonl",
        help="Path to the case data file in JSONL format",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level",
    )
    parser.add_argument(
        "--log_think", action="store_true", help="Log the agent think step"
    )
    return parser.parse_args()


def main():
    """
    主函数
    """
    args = parse_arguments()
    simulation = CourtSimulation(args.config, args.case, args.log_level, args.log_think)
    simulation.run_simulation()


if __name__ == "__main__":
    main()
