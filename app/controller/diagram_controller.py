"""
Diagram Controller - API Endpoints for Diagram Operations

Handles diagram generation, preview, history, and CRUD operations.
"""
import base64
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.services.diagram_service import DiagramService
from app.services.render_service import RenderService
from app.schemas.diagram_schema import (
    GenerateDiagramRequest,
    PreviewDiagramRequest,
    DiagramResponse,
    DiagramOut,
    DiagramDetailOut,
    DiagramListResponse
)
from app.schemas.common_schema import PaginationParams
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/diagram", tags=["Diagrams"])


def get_diagram_service(db: AsyncSession = Depends(get_session)) -> DiagramService:
    """Dependency injection for diagram service."""
    return DiagramService(db)


@router.post("/generate", tags=["Diagrams"])
async def generate_diagram(
    request_data: GenerateDiagramRequest,
    http_request: Request,
    service: DiagramService = Depends(get_diagram_service)
):
    """
    Generate a diagram from a natural language prompt.
    
    This endpoint:
    1. Sends the prompt to the LLM to generate Graphviz DOT code
    2. Validates the generated DOT code
    3. Renders the DOT to the requested format (SVG or PNG)
    4. Saves to database for caching and history
    5. Returns the image directly or as JSON (based on Accept header)
    
    Returns:
        - Image response (image/svg+xml or image/png) by default
        - JSON response with base64-encoded image if Accept: application/json
    """
    logger.info(
        f"Generate diagram request: format={request_data.format}, "
        f"layout={request_data.layout}, prompt='{request_data.prompt[:50]}...'"
    )
    
    try:
        # Generate diagram
        image_bytes, dot_code, diagram_id = await service.generate_diagram(
            prompt=request_data.prompt,
            format=request_data.format,
            layout=request_data.layout or "dot",
            user_id=request_data.user_id,
            save_to_db=True
        )
        
        # Return response based on Accept header
        accept_header = http_request.headers.get("accept", "")
        
        if "application/json" in accept_header:
            # Return JSON with base64-encoded image
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            return DiagramResponse(
                diagram_dot=dot_code,
                image_base64=image_base64,
                format=request_data.format,
                diagram_id=diagram_id
            )
        else:
            # Return image directly
            mime_type = RenderService.get_format_mime_type(request_data.format)
            return Response(
                content=image_bytes,
                media_type=mime_type
            )
            
    except Exception as e:
        logger.error(f"Diagram generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate diagram: {str(e)}"
        )


@router.post("/preview", tags=["Diagrams"])
async def preview_diagram(
    request_data: PreviewDiagramRequest,
    http_request: Request,
    service: DiagramService = Depends(get_diagram_service)
):
    """
    Preview/render a diagram from Graphviz DOT code directly (no LLM call).
    
    Useful for WYSIWYG editing or when you already have DOT code.
    
    Returns:
        - Image response (image/svg+xml or image/png) by default
        - JSON response with base64-encoded image if Accept: application/json
    """
    logger.info(f"Preview diagram request: format={request_data.format}, layout={request_data.layout}")
    
    try:
        # Preview diagram (no LLM, no DB save)
        image_bytes = await service.preview_diagram(
            dot_code=request_data.dot,
            format=request_data.format,
            layout=request_data.layout or "dot"
        )
        
        # Return response based on Accept header
        accept_header = http_request.headers.get("accept", "")
        
        if "application/json" in accept_header:
            # Return JSON with base64-encoded image
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            return DiagramResponse(
                diagram_dot=request_data.dot,
                image_base64=image_base64,
                format=request_data.format,
                diagram_id=None
            )
        else:
            # Return image directly
            mime_type = RenderService.get_format_mime_type(request_data.format)
            return Response(
                content=image_bytes,
                media_type=mime_type
            )
            
    except Exception as e:
        logger.error(f"Diagram preview failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to preview diagram: {str(e)}"
        )


@router.get("/history", response_model=DiagramListResponse, tags=["Diagrams"])
async def get_diagram_history(
    limit: int = Query(50, ge=1, le=200, description="Items per page"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    service: DiagramService = Depends(get_diagram_service)
):
    """
    Get diagram generation history with pagination.
    
    Returns a paginated list of previously generated diagrams.
    """
    logger.debug(f"Get history: limit={limit}, offset={offset}, user_id={user_id}")
    
    try:
        diagrams, total = await service.get_diagram_history(
            limit=limit,
            offset=offset,
            user_id=user_id
        )
        
        return DiagramListResponse(
            total=total,
            limit=limit,
            offset=offset,
            items=[DiagramOut.model_validate(d) for d in diagrams]
        )
        
    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve diagram history: {str(e)}"
        )


@router.get("/{diagram_id}", response_model=DiagramDetailOut, tags=["Diagrams"])
async def get_diagram(
    diagram_id: UUID,
    service: DiagramService = Depends(get_diagram_service)
):
    """
    Get a specific diagram by ID.
    
    Returns the full diagram including DOT code and stored image data.
    """
    logger.debug(f"Get diagram: {diagram_id}")
    
    try:
        diagram = await service.get_diagram_by_id(str(diagram_id))
        
        if not diagram:
            raise HTTPException(
                status_code=404,
                detail=f"Diagram not found: {diagram_id}"
            )
        
        return DiagramDetailOut.model_validate(diagram)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get diagram: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve diagram: {str(e)}"
        )


@router.delete("/{diagram_id}", tags=["Diagrams"])
async def delete_diagram(
    diagram_id: UUID,
    service: DiagramService = Depends(get_diagram_service)
):
    """
    Delete a diagram.
    
    Returns a success message if deleted, 404 if not found.
    """
    logger.info(f"Delete diagram: {diagram_id}")
    
    try:
        deleted = await service.delete_diagram(str(diagram_id))
        
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Diagram not found: {diagram_id}"
            )
        
        return {"message": "Diagram deleted successfully", "id": str(diagram_id)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete diagram: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete diagram: {str(e)}"
        )

