"""
RAG 智能问答 API 接口。
"""
from fastapi import APIRouter
from backend.models.schemas import QuestionRequest, AnswerResponse
from backend.services.rag_service import ask_question

router = APIRouter(prefix="/api/qa", tags=["智能问答"])


@router.post("/ask", response_model=AnswerResponse)
async def ask_question_api(req: QuestionRequest):
    """
    RAG 智能问答。
    从 Neo4j 检索相关实体 + 文档片段 + LLM 组合回答。
    缓存策略：相同问题缓存 1 小时。
    """
    answer = await ask_question(req.question)
    return AnswerResponse(answer=answer, sources=["知识图谱", "文档片段"])