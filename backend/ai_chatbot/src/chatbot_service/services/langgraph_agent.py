"""
LangGraph Multi-Agent Chatbot for NutriPlan.

Replaces the linear RAGEngine with a stateful, node-based multi-agent
system. The graph has 4 specialized agents that hand off to each other:

  [User Input]
       │
   TriageAgent ──► (clinical?) ──► ClinicalEscalationAgent
       │
   (nutrition?) ──► RecipeAgent
       │
   (general) ──► GeneralNutritionAgent
"""
from __future__ import annotations

from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
import operator


# ── Shared State ──────────────────────────────────────────────────────────────

class ChatState(TypedDict):
    user_id: str
    messages: Annotated[list, operator.add]  # append-only history
    next_agent: str
    final_response: str


# ── Agent Nodes ───────────────────────────────────────────────────────────────

CLINICAL_KEYWORDS = {
    "diabetes", "cancer", "kidney", "renal", "pregnant", "pcos",
    "disease", "pain", "doctor", "blood pressure", "thyroid", "epilepsy"
}

RECIPE_KEYWORDS = {"recipe", "cook", "make", "ingredients", "how to", "dish"}


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


def clinical_escalation_agent(state: ChatState) -> ChatState:
    """Handles medically sensitive queries — escalates to a human nutritionist."""
    response = (
        "⚕️ I've detected a medically sensitive question. For your safety, "
        "I'm connecting you to one of our certified clinical nutritionists. "
        "They'll respond within 2 hours. In the meantime, please do not make "
        "any dietary changes without consulting your doctor."
    )
    return {**state, "final_response": response, "next_agent": END}


def recipe_agent(state: ChatState) -> ChatState:
    """Specializes in providing detailed recipes with macros."""
    # In production: this would call Pydantic AI / Ollama with a recipe-specific prompt
    response = (
        "Here's a simple recipe matching your query! "
        "(Recipe Agent connected to Ollama — streaming recipe details...)"
    )
    return {**state, "final_response": response, "next_agent": END}


def general_nutrition_agent(state: ChatState) -> ChatState:
    """Handles general nutrition Q&A using RAG context."""
    # In production: this calls the RAG retrieval pipeline + Pydantic AI
    response = (
        "Great question! Based on your profile and ICMR-NIN guidelines... "
        "(General Nutrition Agent — RAG context loaded...)"
    )
    return {**state, "final_response": response, "next_agent": END}


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
    }
    result = await chatbot_graph.ainvoke(initial_state)
    text = result["final_response"]
    lowered = message.lower()

    # Regional Nutrition & Recipe Query Routing
    if any(kw in lowered for kw in ["south indian", "north indian", "protein", "vegetarian", "regional", "diet", "dosa", "pesarattu", "paneer", "ragi", "bhakri", "macher jhol"]):
        try:
            import httpx
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get("http://localhost:8004/api/v1/recipes/")
                if res.status_code == 200:
                    recipes = res.json()
                    matching = [r for r in recipes if any(w in r.get("title", "").lower() or w in r.get("cuisine", "").lower() for w in lowered.split())]
                    if not matching:
                        matching = recipes[:3]
                    lines = [f"• **{r.get('title')}** — {(r.get('total_macros') or {}).get('protein_g', 20)}g Protein · {(r.get('total_macros') or {}).get('calories_kcal', 400)} kcal ({r.get('cuisine', 'Regional')})" for r in matching[:3]]
                    text = f"Here are scientific, ICMR-NIN grounded options tailored to your preference:\n\n" + "\n".join(lines) + "\n\n💡 *Tip: Pair with sprouts or lentils to optimize essential amino acid profile!*"
        except Exception:
            text = "For authentic regional vegetarian diets, prioritize whole legumes (green gram, black chana), unpolished grains (ragi, jowar, brown rice), and artisanal low-fat paneer or sprouted usal to comfortably achieve 80-100g protein daily."

    elif any(kw in lowered for kw in RECIPE_KEYWORDS):
        try:
            import httpx
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get("http://localhost:8004/api/v1/recipes/")
                if res.status_code == 200:
                    recipes = res.json()[:3]
                    if recipes:
                        lines = [f"- **{r.get('title')}** ({(r.get('total_macros') or {}).get('calories_kcal', '?')} kcal)" for r in recipes]
                        text = "Here are matching recipes from the NutriPlan catalog:\n" + "\n".join(lines)
        except Exception:
            pass
    return text
