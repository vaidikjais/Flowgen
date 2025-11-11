"""
LLM Service - Business Logic for LLM Interactions

Handles LLM API calls for generating Graphviz DOT code from natural language,
including retry logic, token tracking, and error handling.
Uses LangChain for provider abstraction (OpenAI, NVIDIA NIM).
"""
import re
import asyncio
from typing import Optional, Tuple
from datetime import datetime, timezone

from langchain_core.messages import HumanMessage, SystemMessage

from app.core.config import settings
from app.core.exceptions import LLMError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LLMService:
    """Service class for LLM interactions to generate DOT code."""
    
    SYSTEM_PROMPT = """You are a specialized assistant that converts natural-language descriptions into Graphviz DOT code.

RULES:
1. Output ONLY the DOT code, optionally wrapped in triple backticks with "dot" language tag
2. Do NOT include any explanation, commentary, or text outside the code
3. Use 'digraph' for directed graphs (flowcharts, processes, hierarchies)
4. Use 'graph' for undirected graphs (relationships, networks)
5. Use short, safe node IDs (alphanumeric, no spaces)
6. Add meaningful labels to nodes and edges
7. Choose appropriate Graphviz layout: dot (hierarchical), neato (spring), fdp (force), circo (circular), etc.
8. Keep the graph concise and readable

EXAMPLE INPUT: "Draw a flowchart for user login with username/password validation"
EXAMPLE OUTPUT:
```dot
digraph login {
    rankdir=TB;
    node [shape=box, style=rounded];
    
    start [label="Start"];
    input [label="Enter Username\\nand Password"];
    validate [label="Validate Credentials"];
    success [label="Login Success", shape=ellipse, style=filled, fillcolor=lightgreen];
    error [label="Login Failed", shape=ellipse, style=filled, fillcolor=lightcoral];
    
    start -> input;
    input -> validate;
    validate -> success [label="Valid"];
    validate -> error [label="Invalid"];
}
```

Now generate DOT code based on the user's request."""
    
    def __init__(self):
        """Initialize the LLM service with LangChain."""
        self.provider = settings.LLM_PROVIDER
        self.llm = None
        self._use_llm = False
        
        # Initialize LLM based on provider
        if self.provider == "openai" and settings.OPENAI_API_KEY and settings.OPENAI_MODEL:
            try:
                from langchain_openai import ChatOpenAI
                init_params = {
                    "api_key": settings.OPENAI_API_KEY,
                    "model": settings.OPENAI_MODEL,
                    "temperature": 0.3,
                    "max_tokens": settings.MAX_TOKENS,
                    "timeout": 30
                }
                if settings.OPENAI_BASE_URL:
                    init_params["base_url"] = settings.OPENAI_BASE_URL
                
                self.llm = ChatOpenAI(**init_params)
                self._use_llm = True
                logger.info(f"Initialized LangChain with OpenAI: {settings.OPENAI_MODEL}")
            except ImportError as e:
                logger.warning(
                    f"Failed to import langchain_openai: {e}. "
                    "Install with: pip install langchain-openai"
                )
        
        elif self.provider == "nvidia" and settings.NVIDIA_API_KEY and settings.NVIDIA_MODEL:
            try:
                from langchain_nvidia_ai_endpoints import ChatNVIDIA
                init_params = {
                    "api_key": settings.NVIDIA_API_KEY,
                    "model": settings.NVIDIA_MODEL,
                    "temperature": 0.3,
                    "max_tokens": settings.MAX_TOKENS,
                    "timeout": 30
                }
                if settings.NVIDIA_BASE_URL:
                    init_params["base_url"] = settings.NVIDIA_BASE_URL
                
                self.llm = ChatNVIDIA(**init_params)
                self._use_llm = True
                logger.info(f"Initialized LangChain with NVIDIA NIM: {settings.NVIDIA_MODEL}")
            except ImportError as e:
                logger.warning(
                    f"Failed to import langchain_nvidia_ai_endpoints: {e}. "
                    "Install with: pip install langchain-nvidia-ai-endpoints"
                )
        
        elif self.provider == "gemini" and settings.GOOGLE_API_KEY and settings.GEMINI_MODEL:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                self.llm = ChatGoogleGenerativeAI(
                    google_api_key=settings.GOOGLE_API_KEY,
                    model=settings.GEMINI_MODEL,
                    temperature=0.3,
                    max_tokens=settings.MAX_TOKENS,
                    timeout=30
                )
                self._use_llm = True
                logger.info(f"Initialized LangChain with Google Gemini: {settings.GEMINI_MODEL}")
            except ImportError as e:
                logger.warning(
                    f"Failed to import langchain_google_genai: {e}. "
                    "Install with: pip install langchain-google-genai"
                )
        
        if not self._use_llm:
            logger.warning(
                f"No valid configuration for provider '{self.provider}'. Using fallback mock implementation."
            )
    
    async def generate_dot_code(
        self,
        prompt: str,
        max_tokens: int = 1024,
        max_retries: int = 3
    ) -> Tuple[str, Optional[int], int]:
        """
        Generate Graphviz DOT code from a natural language prompt.
        
        Args:
            prompt: Natural language description of the diagram
            max_tokens: Maximum tokens for LLM response
            max_retries: Number of retry attempts on transient errors
            
        Returns:
            Tuple of (dot_code, tokens_used, latency_ms)
            
        Raises:
            LLMError: If LLM call fails after retries
        """
        start_time = datetime.now(timezone.utc)
        
        if not self._use_llm:
            dot_code = self._fallback_mock(prompt)
            latency_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
            return dot_code, None, latency_ms
        
        # Try with retries and exponential backoff
        for attempt in range(max_retries):
            try:
                response, tokens_used = await self._call_llm_async(prompt, max_tokens)
                dot_code = self._extract_dot(response)
                latency_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
                
                logger.info(
                    f"Successfully generated DOT code "
                    f"(tokens: {tokens_used}, latency: {latency_ms}ms)"
                )
                
                return dot_code, tokens_used, latency_ms
                
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.warning(
                        f"LLM call failed (attempt {attempt + 1}/{max_retries}): {e}. "
                        f"Retrying in {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    latency_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
                    logger.error(f"LLM call failed after {max_retries} attempts: {e}")
                    raise LLMError(
                        f"Failed to generate DOT code after {max_retries} attempts",
                        detail=str(e)
                    )
    
    async def _call_llm_async(
        self,
        prompt: str,
        max_tokens: int
    ) -> Tuple[str, Optional[int]]:
        """
        Call LLM API asynchronously via LangChain.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens for response
            
        Returns:
            Tuple of (response_text, tokens_used)
        """
        try:
            # Prepare messages
            messages = [
                SystemMessage(content=self.SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ]
            
            # Call LLM using LangChain's async invoke
            response = await self.llm.ainvoke(messages)
            
            content = response.content
            if not content:
                raise LLMError("Empty response from LLM")
            
            # Extract token usage from response metadata
            tokens_used = None
            if hasattr(response, 'response_metadata'):
                usage = response.response_metadata.get('token_usage', {})
                tokens_used = usage.get('total_tokens')
            
            return content, tokens_used
            
        except Exception as e:
            logger.error(f"LLM API error ({self.provider}): {e}")
            raise LLMError(f"LLM API call failed: {str(e)}")
    
    def _extract_dot(self, llm_response: str) -> str:
        """
        Extract clean DOT code from LLM response.
        
        Handles triple-backtick code fences and removes markdown formatting.
        
        Args:
            llm_response: Raw response from LLM
            
        Returns:
            Clean DOT code
            
        Raises:
            LLMError: If no valid DOT code found
        """
        # Try to extract from code fence first (```dot or ```graphviz or just ```)
        code_fence_pattern = r"```(?:dot|graphviz)?\s*\n(.*?)\n```"
        match = re.search(code_fence_pattern, llm_response, re.DOTALL)
        
        if match:
            dot_code = match.group(1).strip()
        else:
            # No code fence, use the entire response
            dot_code = llm_response.strip()
        
        # Basic validation: should contain 'graph' or 'digraph'
        if not re.search(r'\b(di)?graph\b', dot_code, re.IGNORECASE):
            raise LLMError(
                "Invalid DOT code: must contain 'graph' or 'digraph' declaration"
            )
        
        return dot_code
    
    def _fallback_mock(self, prompt: str) -> str:
        """
        Fallback mock implementation when OpenAI API is not available.
        
        Returns a simple example DOT graph based on prompt keywords.
        
        Args:
            prompt: User prompt (used to customize output slightly)
            
        Returns:
            Simple DOT graph
        """
        logger.info("Using fallback mock DOT generation")
        
        # Create a simple graph based on prompt keywords
        is_directed = any(
            word in prompt.lower() 
            for word in ["flow", "process", "step", "sequence", "hierarchy"]
        )
        
        if is_directed:
            return """digraph example {
    rankdir=TB;
    node [shape=box, style=rounded];
    
    start [label="Start", shape=ellipse];
    step1 [label="Process Step"];
    step2 [label="Decision", shape=diamond];
    end [label="End", shape=ellipse];
    
    start -> step1;
    step1 -> step2;
    step2 -> end [label="Complete"];
}"""
        else:
            return """graph example {
    node [shape=circle];
    
    A [label="Node A"];
    B [label="Node B"];
    C [label="Node C"];
    D [label="Node D"];
    
    A -- B;
    B -- C;
    C -- D;
    D -- A;
    A -- C;
}"""

