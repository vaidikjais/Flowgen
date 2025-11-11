"""
Example Python client for Flowgen API.
Demonstrates how to programmatically generate diagrams.
"""
import base64
import requests
from pathlib import Path


class DiagramClient:
    """Simple client for diagram generation API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize client with base URL."""
        self.base_url = base_url.rstrip("/")
    
    def generate_diagram(
        self,
        prompt: str,
        format: str = "svg",
        layout: str = "dot",
        save_to: str = None
    ) -> bytes:
        """
        Generate a diagram from a natural language prompt.
        
        Args:
            prompt: Natural language description
            format: Output format ("svg" or "png")
            layout: Layout engine ("dot", "neato", "fdp", "sfdp", "twopi", "circo")
            save_to: Optional file path to save the diagram
            
        Returns:
            Diagram image as bytes
        """
        url = f"{self.base_url}/api/diagram/generate"
        
        payload = {
            "prompt": prompt,
            "format": format,
            "layout": layout
        }
        
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        image_bytes = response.content
        
        if save_to:
            Path(save_to).write_bytes(image_bytes)
            print(f"✓ Diagram saved to: {save_to}")
        
        return image_bytes
    
    def preview_dot(
        self,
        dot_code: str,
        format: str = "svg",
        layout: str = "dot",
        save_to: str = None
    ) -> bytes:
        """
        Preview a diagram from DOT code.
        
        Args:
            dot_code: Graphviz DOT code
            format: Output format ("svg" or "png")
            layout: Layout engine
            save_to: Optional file path to save the diagram
            
        Returns:
            Diagram image as bytes
        """
        url = f"{self.base_url}/api/diagram/preview"
        
        payload = {
            "dot": dot_code,
            "format": format,
            "layout": layout
        }
        
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        image_bytes = response.content
        
        if save_to:
            Path(save_to).write_bytes(image_bytes)
            print(f"✓ Diagram saved to: {save_to}")
        
        return image_bytes
    
    def generate_with_metadata(
        self,
        prompt: str,
        format: str = "svg",
        layout: str = "dot"
    ) -> dict:
        """
        Generate diagram and get both DOT code and image as base64.
        
        Args:
            prompt: Natural language description
            format: Output format
            layout: Layout engine
            
        Returns:
            Dictionary with diagram_dot, image_base64, and format
        """
        url = f"{self.base_url}/api/diagram/generate"
        
        payload = {
            "prompt": prompt,
            "format": format,
            "layout": layout
        }
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        return response.json()
    
    def health_check(self) -> dict:
        """Check API health."""
        url = f"{self.base_url}/api/health"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()


def main():
    """Example usage of the DiagramClient."""
    
    # Initialize client
    client = DiagramClient()
    
    # Check if API is healthy
    print("Checking API health...")
    health = client.health_check()
    print(f"✓ API Status: {health['status']} (v{health['version']})")
    print()
    
    # Example 1: Generate a flowchart
    print("Example 1: Generating flowchart...")
    client.generate_diagram(
        prompt="Draw a flowchart for user login with username/password validation, showing success and error paths",
        format="svg",
        layout="dot",
        save_to="example_flowchart.svg"
    )
    print()
    
    # Example 2: Generate a network diagram
    print("Example 2: Generating network diagram...")
    client.generate_diagram(
        prompt="Create a network topology diagram showing internet, router, firewall, DMZ with web server, and internal network with app and database servers",
        format="png",
        layout="dot",
        save_to="example_network.png"
    )
    print()
    
    # Example 3: Preview existing DOT code
    print("Example 3: Previewing custom DOT code...")
    dot_code = """
    digraph custom {
        rankdir=LR;
        node [shape=box, style=rounded];
        
        A [label="Start"];
        B [label="Process"];
        C [label="End"];
        
        A -> B [label="input"];
        B -> C [label="output"];
    }
    """
    client.preview_dot(
        dot_code=dot_code,
        format="svg",
        layout="dot",
        save_to="example_custom.svg"
    )
    print()
    
    # Example 4: Get metadata with diagram
    print("Example 4: Getting diagram with metadata...")
    result = client.generate_with_metadata(
        prompt="Simple state machine with states: idle, running, paused, stopped",
        format="svg",
        layout="dot"
    )
    print(f"✓ Received DOT code ({len(result['diagram_dot'])} chars)")
    print(f"✓ Received image ({len(result['image_base64'])} base64 chars)")
    
    # Optionally save the base64 image
    image_data = base64.b64decode(result['image_base64'])
    Path("example_metadata.svg").write_bytes(image_data)
    print("✓ Saved to: example_metadata.svg")
    print()
    
    print("=" * 50)
    print("All examples completed successfully! 🎉")
    print("=" * 50)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API. Is the server running?")
        print("   Start with: uvicorn app.main:app --reload")
    except requests.exceptions.HTTPError as e:
        print(f"❌ API Error: {e}")
        print("   Check your OpenAI API key and server logs")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

