import sys
import os
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import Response, StreamingResponse
from chatkit.server import StreamingResult

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.auth.middleware import JWTBearer
from src.utils.validation import validate_user_id
from src.auth.jwt import get_user_id_from_token
from src.services.chatkit_server import ChatKitServer
from src.services.chatkit_store import ChatKitNeonStore
from src.todo_agents.chat_agent import create_todo_chat_agent
from src.todo_agents.context import UserContext


agent, _ = create_todo_chat_agent()
chatkit_store = ChatKitNeonStore()
chatkit_server = ChatKitServer(agent=agent, store=chatkit_store)

router = APIRouter(prefix="/api", tags=["chat"])
security = JWTBearer()


@router.post("/chat", response_class=Response)
async def chat(
    request: Request,
    token: str = Depends(security)
):
    """Send a message to the AI chatbot and receive a response."""

    # Extract user ID from token
    user_id = get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )

    # Validate user_id
    validated_user_id = validate_user_id(user_id)

    # Get the raw payload from the request body
    payload = await request.body()

    # Process the payload using the ChatKitServer instance
    # Pass the validated user_id in the context
    context = UserContext(
        user_id=validated_user_id
    )
    result = await chatkit_server.process(payload, context)

    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    return Response(content=result.json, media_type="application/json")
    