"""
Pydantic models for Conversation entities.
"""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ConversationUpsertRequest(BaseModel):
    """Request model for conversation upsert endpoint"""
    user_id: str = Field(..., description="User ID (UUID as string)")
    external_contact_id: str = Field(..., description="External contact identifier (e.g., WhatsApp ID)")
    contact_name: Optional[str] = Field(None, description="Contact display name")
    source: str = Field(..., description="Message source (e.g., 'whatsapp', 'simulacao')")
    status: str = Field(default="open", description="Conversation status")
    started_at_ts: Optional[int] = Field(None, description="Unix timestamp (seconds) when conversation started")


class ConversationUpsertResponse(BaseModel):
    """Response model for conversation upsert endpoint"""
    conversation_id: str = Field(..., description="Conversation UUID")
    created: bool = Field(..., description="Whether the conversation was newly created")
