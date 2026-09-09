"""
LangGraph Multi-Agent Chatbot for NutriPlan.
============================================
A stateful, node-based multi-agent system powered by the production RAGEngine:

  [User Input]
       │
   TriageAgent ──► (clinical?) ──► ClinicalEscalationAgent (dispatches notification)
       │
   (recipe?) ────► RecipeAgent (queries live Recipe DB + macros)
       │
   (general) ────► GeneralNutritionAgent (queries RAGEngine with Live Ollama + context)
"""
from __future__ import annotations

from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
import operator
import httpx

from .rag_engine import rag_engine, CLINICAL_KEYWORDS
from nutriplan_shared.service_registry import RECIPE_URL


# ── Shared State ──────────────────────────────────────────────────────────────

class ChatState(TypedDict):
    user_id: str
    messages: Annotated[list, operator.add]  # append-only history
    next_agent: str
    final_response: str
    response_type: str


RECIPE_KEYWORDS = {"recipe", "cook", "make", "ingredients", "how to", "dish", "meal"}


def triage_agent(state: ChatState) -> ChatState:
    """Routes the user message to the correct specialist agent."""
    last_msg = state["messages"][-1].lower()

    if any(kw in last_msg for kw in CLINICAL_KEYWORDS):
        next_agent = "clinical_escalation"
    elif any(kw in last_msg for kw in RECIPE_KEYWORDS):
        next_agent = "recipe_agent"
    else:
        next_agent = "general_nutrition"

    return {**state, "next_agent": next_agent}


async def clinical_escalation_agent(state: ChatState) -> ChatState:
    """Handles medically sensitive queries — escalates to a human nutritionist via RAG engine."""
    user_id = state.get("user_id", "user_default")
    last_msg = state["messages"][-1]
    res = await rag_engine.trigger_clinical_transfer(user_id, last_msg)
    return {
        **state,
        "final_response": res["message"],
        "response_type": "escalation",
        "next_agent": END
    }


async def recipe_agent(state: ChatState) -> ChatState:
    """Specializes in providing detailed recipes with macros from live recipe service."""
    last_msg = state["messages"][-1].lower()
    user_id = state.get("user_id", "user_default")

    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            res = await client.get(f"{RECIPE_URL}/api/v1/recipes/")
            if res.status_code == 200:
                recipes = res.json()
                matching = [
                    r for r in recipes 
                    if any(w in r.get("title", "").lower() or w in r.get("cuisine", "").lower() for w in last_msg.split())
                ]
                if not matching:
                    matching = recipes[:3]
                
                lines = []
                for r in matching[:3]:
                    macros = r.get("total_macros") or {}
                    cal = macros.get("calories_kcal", 350)
                    pro = macros.get("protein_g", 18)
                    lines.append(f"• **{r.get('title')}** — {cal} kcal | {pro}g protein ({r.get('cuisine', 'Regional')})")
                
                reply = (
                    "Here are curated recipes from the NutriPlan database matching your inquiry:\n\n"
                    + "\n".join(lines) +
                    "\n\n💡 *All items can be logged in 1-click to your Food Diary or added to your Grocery list.*"
                )
                return {**state, "final_response": reply, "response_type": "ai_response", "next_agent": END}
    except Exception:
        pass

    # Fallback to RAG engine
    rag_res = await rag_engine.generate_response(last_msg, user_id)
    return {
        **state,
        "final_response": rag_res["message"],
        "response_type": "ai_response",
        "next_agent": END
    }


async def general_nutrition_agent(state: ChatState) -> ChatState:
    """Handles general nutrition Q&A using full live RAG pipeline."""
    user_id = state.get("user_id", "user_default")
    last_msg = state["messages"][-1]
    rag_res = await rag_engine.generate_response(last_msg, user_id)
    return {
        **state,
        "final_response": rag_res["message"],
        "response_type": rag_res.get("type", "ai_response"),
        "next_agent": END
    }


def route(state: ChatState) -> Literal["clinical_escalation", "recipe_agent", "general_nutrition", "__end__"]:
    return state["next_agent"]


# ── Build the LangGraph ───────────────────────────────────────────────────────

def build_chatbot_graph() -> StateGraph:
    graph = StateGraph(ChatState)

    graph.add_node("triage", triage_agent)
    graph.add_node("clinical_escalation", clinical_escalation_agent)
    graph.add_node("recipe_agent", recipe_agent)
    graph.add_node("general_nutrition", general_nutrition_agent)

    graph.set_entry_point("triage")

    graph.add_conditional_edges(
        "triage",
        route,
        {
            "clinical_escalation": "clinical_escalation",
            "recipe_agent": "recipe_agent",
            "general_nutrition": "general_nutrition",
        }
    )

    graph.add_edge("clinical_escalation", END)
    graph.add_edge("recipe_agent", END)
    graph.add_edge("general_nutrition", END)

    return graph.compile()


# Compiled graph (singleton)
chatbot_graph = build_chatbot_graph()


async def process_chat_message(user_id: str, message: str) -> str:
    initial_state: ChatState = {
        "user_id": user_id,
        "messages": [message],
        "next_agent": "triage",
        "final_response": "",
        "response_type": "ai_response",
    }
    result = await chatbot_graph.ainvoke(initial_state)
    return result["final_response"]
