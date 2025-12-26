from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import Response, StreamingResponse
from chatkit.server import StreamingResult
# Handle both direct execution and module import
try:
    from ...auth.middleware import JWTBearer
    from ...utils.validation import validate_user_id
    from ...auth.jwt import get_user_id_from_token
    from ...services.chatkit_server import ChatKitServer
    from ...services.chatkit_store import ChatKitNeonStore
    from ...todo_agents.chat_agent import create_todo_chat_agent
except ImportError:
    # When running tests or as module, use absolute imports
    from src.auth.middleware import JWTBearer
    from src.utils.validation import validate_user_id
    from src.auth.jwt import get_user_id_from_token
    from src.services.chatkit_server import ChatKitServer
    from src.services.chatkit_store import ChatKitNeonStore
    from src.todo_agents.chat_agent import create_todo_chat_agent


agent, neon_mcp_server = create_todo_chat_agent()
chatkit_store = ChatKitNeonStore[Dict[str, Any]]()
chatkit_server = ChatKitServer(agent=agent, store=chatkit_store, mcp_servers=[neon_mcp_server])

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
    context = {
        "request": request,
        "user_id": validated_user_id
    }
    result = await chatkit_server.process(payload, context)

    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    return Response(content=result.json, media_type="application/json")
    