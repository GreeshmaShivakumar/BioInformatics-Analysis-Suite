import httpx
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GROK_API_KEY = os.getenv("GROK_API_KEY", "")
GROK_API_URL = "https://api.x.ai/v1/responses"

BIOINFORMATICS_CONTEXT = """You are a helpful bioinformatics assistant. You help users understand:
- Genomic sequence analysis results
- GC content and nucleotide composition
- FASTA and FASTQ file formats
- DNA/RNA biology concepts
- How to interpret analysis results

Be concise, scientific but accessible. When users ask about their specific results, reference the provided context."""


async def chat_with_grok(user_message: str, analysis_context: Optional[Dict[str, Any]] = None) -> str:
    """
    Send a message to Grok API and get a response.
    
    Args:
        user_message: The user's question or message
        analysis_context: Optional context from recent analysis (results, sequences, etc.)
    
    Returns:
        The chatbot's response text
    """
    
    if not GROK_API_KEY:
        return "Error: GROK_API_KEY not configured. Please set the GROK_API_KEY environment variable in backend/.env file."
    
    # Build system message with context
    system_message = BIOINFORMATICS_CONTEXT
    if analysis_context:
        context_str = "\n\nUser's recent analysis context:\n"
        if "filename" in analysis_context:
            context_str += f"- File: {analysis_context['filename']}\n"
        if "average_gc_content" in analysis_context:
            context_str += f"- Average GC Content: {analysis_context['average_gc_content']:.2f}%\n"
        if "total_sequences" in analysis_context:
            context_str += f"- Total Sequences: {analysis_context['total_sequences']}\n"
        if "average_length" in analysis_context:
            context_str += f"- Average Sequence Length: {analysis_context['average_length']:.0f} bp\n"
        if "nucleotide_composition" in analysis_context:
            comp = analysis_context["nucleotide_composition"]
            context_str += f"- Nucleotide Composition: A={comp.get('A', 0)}, T={comp.get('T', 0)}, G={comp.get('G', 0)}, C={comp.get('C', 0)}\n"
        
        system_message += context_str
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                GROK_API_URL,
                headers={
                    "Authorization": f"Bearer {GROK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "grok-4.3",
                    "input": [
                        {
                            "role": "system",
                            "content": system_message
                        },
                        {
                            "role": "user",
                            "content": user_message
                        }
                    ]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                # Handle Grok API response format
                if "result" in data:
                    return data["result"].get("output", str(data["result"]))
                elif "choices" in data:
                    return data["choices"][0]["message"]["content"]
                else:
                    return str(data)
            elif response.status_code == 401:
                return "Error: Invalid or expired API key. Please check your GROK_API_KEY in backend/.env"
            elif response.status_code == 400:
                try:
                    error_detail = response.json().get("error", "Unknown error")
                except:
                    error_detail = response.text
                return f"Error: Bad request from Grok API: {error_detail}. Please verify your API key is valid."
            else:
                try:
                    error_body = response.json()
                except:
                    error_body = response.text
                return f"Error: Grok API returned status {response.status_code}: {error_body}"
    
    except httpx.TimeoutException:
        return "Error: Request to Grok API timed out. Please try again."
    except Exception as e:
        return f"Error communicating with Grok API: {str(e)}"
