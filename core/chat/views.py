from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
import logging

from restaurants.models import Restaurant
from chat.models import Thread, Message
from chat.serializers import ChatRequestSerializer, ChatResponseSerializer
from chat.knowledge import get_restaurant_knowledge
from chat.agent import create_restaurant_agent

logger = logging.getLogger(__name__)


class ChatAPIView(GenericAPIView):
    """
    Chat endpoint for restaurant queries using RAG.

    POST /api/chat/<restaurant_uid>/
    """
    permission_classes = [AllowAny]
    serializer_class = ChatRequestSerializer

    def post(self, request, restaurant_uid):
        # Validate request data
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        user_message = validated_data['message']
        thread_uid = validated_data.get('thread_uid')

        # Get restaurant
        restaurant = get_object_or_404(Restaurant, uid=restaurant_uid)

        # Get or create thread
        if thread_uid:
            # Continue existing conversation
            thread = get_object_or_404(Thread, uid=thread_uid, restaurant=restaurant)
        else:
            # Create new thread
            thread = Thread.objects.create(
                restaurant=restaurant,
                user=request.user if request.user.is_authenticated else None,
            )

        try:
            # Get knowledge base for this restaurant
            knowledge = get_restaurant_knowledge(str(restaurant.uid))

            # Create agent with name context
            agent = create_restaurant_agent(str(restaurant.uid), restaurant.name, knowledge)

            # Get AI response using rolling summary as context
            ai_response = agent.chat(user_message, rolling_summary=thread.summary)

            # Save message to database
            message_obj = Message.objects.create(
                thread=thread,
                user_message=user_message,
                ai_response=ai_response,
            )

            # Update rolling summary in the thread model
            # This replaces the need for full history queries in future calls
            updated_summary = agent.summarize(
                current_summary=thread.summary,
                user_message=user_message,
                ai_response=ai_response
            )
            thread.summary = updated_summary
            thread.save()

            # Prepare response
            response_data = {
                'thread_uid': thread.uid,
                'ai_response': ai_response,
                'created_at': message_obj.created_at,
            }

            response_serializer = ChatResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the error and return a user-friendly message
            logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)

            return Response(
                {"error": "An error occurred while processing your request. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
