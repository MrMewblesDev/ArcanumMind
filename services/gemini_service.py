from google import genai
from google.genai.errors import APIError as GeminiAPIError

from typing import AsyncGenerator

import logging

log = logging.getLogger(__name__)

async def initialize_gemini(GEMINI_API_KEY: str, GEMINI_MODEL: str):
    """Initialize the Gemini API client.

    Raises:
        ConfigError: If the configuration is invalid.
        GeminiAPIError: If the Gemini API cannot be initialized.
    """
    
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        log.info("Gemini API configured successfully.")
        return client, GEMINI_MODEL
    except GeminiAPIError as e:
        raise GeminiAPIError(f"Failed to configure Gemini API: {e}")
    
async def ask_gemini(prompt: list | str, gemini_client: genai.Client, gemini_model: str) -> AsyncGenerator[str, None]:
    """Send a prompt to the Gemini API and return the response from the specified model.

    This function will send the given prompt to the Gemini API and then
    yield each chunk of text received from the AI model.

    Args:
        prompt (list | str): The prompt to send to the Gemini API.
        client (genai.Client): The Gemini API client to use.
        model (str): The AI model to use for generating text.

    Yields:
        str: The final response from the Gemini API.
    """
    try:
        # Send the prompt to the Gemini API and get a stream of text chunks
        response_stream = await gemini_client.aio.models.generate_content_stream(
            model=gemini_model,
            contents=prompt,
        )

        # Yield each chunk of text received from the Gemini API
        async for chunk in response_stream:
            if chunk.text:
                # Yield the text chunk
                yield chunk.text
    except (Exception, GeminiAPIError) as e:
        log.error("Failed steaming response from Gemini API: %s", e, exc_info=True)
        raise


