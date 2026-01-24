"""
Serializers for chat API endpoints.
"""
from rest_framework import serializers
from chat.models import Thread, Message


class ChatRequestSerializer(serializers.Serializer):
    """
    Serializer for incoming chat requests.
    """
    message = serializers.CharField(
        required=True,
        allow_blank=False,
        help_text="User's message"
    )
    thread_uid = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text="Optional thread UID for continuing conversation"
    )


class ChatResponseSerializer(serializers.Serializer):
    """
    Serializer for chat API responses.
    """
    thread_uid = serializers.UUIDField(
        help_text="Thread identifier for conversation continuity"
    )
    ai_response = serializers.CharField(
        help_text="AI assistant's response"
    )
    created_at = serializers.DateTimeField(
        help_text="Timestamp of the response"
    )


class ThreadSerializer(serializers.ModelSerializer):
    """
    Serializer for Thread model.
    """
    class Meta:
        model = Thread
        fields = ['uid', 'restaurant', 'user', 'summary', 'created_at', 'updated_at']
        read_only_fields = ['uid', 'created_at', 'updated_at']


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model.
    """
    class Meta:
        model = Message
        fields = ['uid', 'thread', 'user_message', 'ai_response', 'created_at']
        read_only_fields = ['uid', 'created_at']
