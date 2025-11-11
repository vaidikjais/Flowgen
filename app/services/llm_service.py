"""
LLM Service - Business Logic for LLM Interactions

Handles LLM API calls for generating Graphviz DOT code from natural language,
including retry logic, token tracking, and error handling.
"""
import re
import time
import asyncio
from typing import Optional, Tuple
from datetime import datetime, timezone

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
        """Initialize the LLM service."""
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.base_url = settings.OPENAI_BASE_URL
        
        # Initialize OpenAI client if API key is available
        if self.api_key:
            try:
                import openai
                self.client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
                self._use_openai = True
                logger.info(f"Initialized OpenAI client with model: {self.model}")
            except ImportError:
                logger.warning(
                    "openai package not installed. "
                    "Install with: pip install openai"
                )
                self._use_openai = False
        else:
            self._use_openai = False
            logger.warning("No OpenAI API key set. Using fallback mock implementation.")
    
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
        
        if not self._use_openai or not self.api_key:
            dot_code = self._fallback_mock(prompt)
            latency_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
            return dot_code, None, latency_ms
        
        # Try with retries and exponential backoff
        for attempt in range(max_retries):
            try:
                response, tokens_used = await self._call_openai_async(prompt, max_tokens)
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
    
    async def _call_openai_async(
        self,
        prompt: str,
        max_tokens: int
    ) -> Tuple[str, Optional[int]]:
        """
        Call OpenAI API asynchronously.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens for response
            
        Returns:
            Tuple of (response_text, tokens_used)
        """
        try:
            # Run OpenAI call in executor to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.3,  # Lower temperature for deterministic output
                    timeout=30
                )
            )
            
            content = response.choices[0].message.content
            if not content:
                raise LLMError("Empty response from LLM")
            
            # Extract token usage
            tokens_used = getattr(response.usage, 'total_tokens', None) if hasattr(response, 'usage') else None
            
            return content, tokens_used
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise LLMError(f"OpenAI API call failed: {str(e)}")
    
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

