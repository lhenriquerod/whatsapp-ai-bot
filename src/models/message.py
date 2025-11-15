"""
Pydantic models for Message entities.
"""
from typing import Optional, Literal, Dict, Any
from pydantic import BaseModel, Field


class MessageCreateRequest(BaseModel):
    """Request model for message creation endpoint"""
    conversation_id: Optional[str] = Field(None, description="Conversation UUID (optional, will be resolved)")
    user_id: str = Field(..., description="User ID (UUID as string)")
    external_contact_id: str = Field(..., description="External contact identifier")
    direction: Literal["inbound", "outbound"] = Field(..., description="Message direction")
    type: str = Field(..., description="Message type (user, assistant, system, etc.)")
    text: str = Field(..., description="Message content")
    timestamp_ts: Optional[int] = Field(None, description="Unix timestamp (seconds)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata (free-form JSON)")


class MessageCreateResponse(BaseModel):
    """Response model for message creation endpoint"""
    message_id: str = Field(..., description="Message UUID")
    conversation_id: str = Field(..., description="Conversation UUID")
