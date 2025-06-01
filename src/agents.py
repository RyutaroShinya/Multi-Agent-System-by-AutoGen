#======================================
# ライブラリ
#======================================
import os
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from dotenv import load_dotenv
from docx import Document

#======================================
# 環境変数の読み込み
#======================================
load_dotenv()

#======================================
# Azure OpenAI LLMの設定
#======================================
llm_config = {
    "config_list": [
        {
            "model": os.getenv("DEPLOYMENT_NAME"),
            "api_type": "azure",
            "api_key": os.getenv("API_KEY"),
            "base_url": os.getenv("API_ENDPOINT"),
            "api_version": os.getenv("API_VERSION"),
        }
    ]
}

#======================================
# UserProxyAgent
#======================================
user_proxy = UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    code_execution_config={"use_docker": False},
    max_consecutive_auto_reply=0,
    )

#======================================
# Agentの取得
#======================================
def get_agent_names(selected_agents):
    """User, オーケストレーターを除いたエージェント名リストを返す"""
    return [name for name in selected_agents if name not in ("オーケストレーター", "User")]

#======================================
# PDFファイルを読み込み
#======================================
def start_group_chat(pdf_path, selected_agents):
    """グループチャットを開始"""
    # PDFファイルからテキスト抽出
    doc = Document(pdf_path)
    user_message = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    groupchat = create_groupchat(selected_agents)
    manager = GroupChatManager(groupchat=groupchat)
    user_proxy.initiate_chat(manager, message=user_message)

#======================================
# オーケストレーター Agent
# 必要に応じてシステムプロンプトを変更してください。
#======================================
def generate_summary_system_message(selected_agents):
    """オーケストレーター用システムメッセージ生成"""
    agent_list_str = "、".join(get_agent_names(selected_agents))
    return (
        "あなたは議論のオーケストレーターです。"
        "会話の最初にUserのインプット情報を要約し、最初に発言すべきエージェントを指名してください。"
        f"今回の参加エージェントは: {agent_list_str} です。"
        "各エージェントの意見が出揃ったら、最後にユーザーに向けて提案をまとめてください。"
        f"他エージェントとの連携は、{agent_list_str}の名称の中から使ってください。"
    )

#======================================
# Agent
# 必要に応じてシステムプロンプトを変更してください。
#======================================
def generate_agent_system_message(agent_type, selected_agents):
    """各エージェント用システムメッセージ生成"""
    agent_list_str = "、".join(get_agent_names(selected_agents))
    return (
        f"あなたは{agent_type}の専門家です。"
        "自分の観点でレビューした後、他エージェントへ0回、もしくは1回意見を求めてください。"
        "直前の会話で他のエージェントから意見を求められた場合は、その意見の内容を加味して発言をしてください。"
        f"自分の専門分野（{agent_type}）以外の内容についてはコメントしないでください。"
        f"他エージェントとの連携は、{agent_list_str}の名称の中から使ってください。"
    )

#======================================
# グループチャット
# ここでエージェント名も変更してください。
#======================================
def create_groupchat(selected_agents):
    """選択されたエージェントでグループチャットを生成"""
    agent_map = {
        "オーケストレーター": lambda: AssistantAgent(
            name="オーケストレーター",
            system_message=generate_summary_system_message(selected_agents),
            llm_config=llm_config
        ),
        "エージェントA": lambda: AssistantAgent(
            name="エージェントA",
            system_message=generate_agent_system_message("エージェントA", selected_agents),
            llm_config=llm_config
        ),
        "エージェントB": lambda: AssistantAgent(
            name="エージェントB",
            system_message=generate_agent_system_message("エージェントB", selected_agents),
            llm_config=llm_config
        ),
        "エージェントC": lambda: AssistantAgent(
            name="エージェントC",
            system_message=generate_agent_system_message("エージェントC", selected_agents),
            llm_config=llm_config
        ),
        "エージェントD": lambda: AssistantAgent(
            name="エージェントD",
            system_message=generate_agent_system_message("エージェントD", selected_agents),
            llm_config=llm_config
        ),
        "エージェントE": lambda: AssistantAgent(
            name="エージェントE",
            system_message=generate_agent_system_message("エージェントE", selected_agents),
            llm_config=llm_config
        ),
        "エージェントF": lambda: AssistantAgent(
            name="エージェントF",
            system_message=generate_agent_system_message("エージェントF", selected_agents),
            llm_config=llm_config
        ),
        "User": lambda: user_proxy,
    }
    agents = [agent_map[name]() for name in selected_agents if name in agent_map]
#======================================
# 会話の最大回数の設定
# max_round=10で、最大10回までの会話を設定する
#======================================
    return GroupChat(agents=agents, messages=[], max_round=10)