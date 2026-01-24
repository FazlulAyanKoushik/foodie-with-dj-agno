from typing import List, Optional
from decouple import config
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.knowledge import Knowledge
from agno.models.message import Message


class RestaurantAgent:
    """
    AI agent for handling restaurant-related queries with RAG.
    """

    def __init__(self, restaurant_uid: str, knowledge: Knowledge):
        """
        Initialize the restaurant agent.

        Args:
            restaurant_uid: Unique identifier for the restaurant
            knowledge: Knowledge base instance for this restaurant
        """
        self.restaurant_uid = restaurant_uid
        self.knowledge = knowledge

        # Initialize OpenAI model
        openai_api_key = config("OPENAI_API_KEY")
        self.model = OpenAIChat(
            id="gpt-4o-mini",
            api_key=openai_api_key,
        )

        # Create Agno agent with knowledge base and memory
        self.agent = Agent(
            name="Restaurant Assistant",
            model=self.model,
            knowledge=knowledge,
            # Enable RAG features
            search_knowledge=True,
            add_knowledge_to_context=True,
            description="A helpful assistant that provides restaurant details, menu items, and handles dietary queries.",
            instructions=[
                "You are a professional restaurant assistant.",
                "Your PRIMARY RESOURCE is the knowledge base. ALWAYS search it first for restaurant information. ",
                "USE the 'CONVERSATION HISTORY SUMMARY' (provided in context) to remember user names, preferences, and previous parts of this conversation.",
                "When asked about the restaurant's website, social media, or contact details, use the `search_knowledge_base` tool.",
                "Provide detailed menu descriptions and prices from the knowledge base.",
                "Handle allergy queries by suggesting safe items based on the provided ingredient lists.",
                "Maintain a helpful, friendly, and professional tone.",
            ],
            markdown=True,
        )

    def chat(self, message: str, rolling_summary: Optional[str] = None) -> str:
        """
        Process a user message and return the AI response.

        Args:
            message: User's message
            rolling_summary: Concise summary of the previous conversation
        """
        # Inject rolling summary as additional context for the model
        if rolling_summary:
            self.agent.additional_context = f"CONVERSATION HISTORY SUMMARY: {rolling_summary}"

        # Get response from agent
        response = self.agent.run(message)

        # Extract content from response
        if hasattr(response, 'content'):
            return response.content
        return str(response)

    def summarize(self, current_summary: Optional[str], user_message: str, ai_response: str) -> str:
        """
        Generate an updated rolling summary of the conversation.
        This is an O(1) operation regarding history length.
        """
        summary_agent = Agent(
            model=self.model,
            instructions=[
                "You are a conversation summarizer.",
                "Your task is to update a rolling summary based on a previous summary and the latest turn.",
                "Maintain key facts, USER NAMES, user preferences, and important context.",
                "NEVER omit the user's name if it was mentioned in the history or latest turn.",
                "Keep the summary concise but highly informative.",
                "Output ONLY the new summary text.",
            ]
        )

        prompt = f"""
Existing Summary: {current_summary or 'No previous context.'}

Latest Turn:
User: {user_message}
AI: {ai_response}

Please provide an updated, concise version of the summary that includes the latest turn.
"""
        response = summary_agent.run(prompt)

        if hasattr(response, 'content'):
            return response.content.strip()
        return str(response).strip()


def create_restaurant_agent(restaurant_uid: str, knowledge: Knowledge) -> RestaurantAgent:
    """
    Factory function to create a restaurant agent.

    Args:
        restaurant_uid: Unique identifier for the restaurant
        knowledge: Knowledge base instance

    Returns:
        Configured RestaurantAgent instance
    """
    return RestaurantAgent(restaurant_uid, knowledge)
