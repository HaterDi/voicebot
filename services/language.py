from azure.ai.language.conversations import ConversationClient, ConversationalAnalysisOptions
from config import settings   # < содержит ключ + endpoint

client = ConversationClient(endpoint=settings.CLU_ENDPOINT,
                            credential=settings.CLU_KEY)

def parse(text: str):
    opt = ConversationalAnalysisOptions(
        query=text,
        project_name="Registration",
        deployment_name="production"
    )
    resp = client.analyze_conversation(opt)
    return resp.prediction.intents[0].category, resp.prediction.entities
