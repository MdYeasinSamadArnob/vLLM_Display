import asyncio
import ollama

async def test_minimal():
    client = ollama.AsyncClient(host='http://10.11.200.109:11434')
    
    # List models
    try:
        models = await client.list()
        print("Available models:")
        for m in models['models']:
            print(f" - {m.model}")
    except Exception as e:
        print(f"Error listing models: {e}")

    model = "qwen3-vl:8b"
    image_path = r"g:\_era\vllm-ocr\backend\sample-images\test-ocr.PNG"
    
    prompts = [
        "Convert this image to HTML.",
    ]
    
    for p in prompts:
        print(f"\nPrompt: {p}")
        try:
            # Try chat instead of generate
            response = await client.chat(
                model=model,
                messages=[{
                    'role': 'user',
                    'content': p,
                    'images': [image_path]
                }],
                options={"num_ctx": 4096, "temperature": 0.6} # Increased temperature
            )
            content = response['message']['content']
            print(f"Response Length: {len(content)}")
            print(f"Preview: {content[:100]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_minimal())
