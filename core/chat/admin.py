from django.contrib import admin
from chat.models import Thread, Message

# Register your models here.
# register Thread and message model
@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'uid', 'restaurant', 'user', 'summary_short'
    )

    def summary_short(self, obj):
        """Display first 10 characters of summary"""
        if obj.summary:
            return obj.summary[:10] + ('...' if len(obj.summary) > 10 else '')
        return '-'
    summary_short.short_description = 'Summary'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'thread', 'user_message_short', 'ai_response_short'
    )

    def user_message_short(self, obj):
        """Display first 10 characters of user message"""
        if obj.user_message:
            return obj.user_message[:10] + ('...' if len(obj.user_message) > 10 else '')
        return '-'
    user_message_short.short_description = 'User Message'

    def ai_response_short(self, obj):
        """Display first 10 characters of AI response"""
        if obj.ai_response:
            return obj.ai_response[:10] + ('...' if len(obj.ai_response) > 10 else '')
        return '-'
    ai_response_short.short_description = 'AI Response'


