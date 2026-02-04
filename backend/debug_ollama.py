import asyncio
import ollama
import json

async def test_ollama():
    client = ollama.AsyncClient(host='http://10.11.200.109:11434')
    
    print("Fetching models...")
    try:
        models = await client.list()
        print("Models response structure:", type(models))
        # print(json.dumps(models, indent=2, default=str)) # Might be too large
        if 'models' in models:
            for m in models['models']:
                # Handle object or dict
                name = m.model if hasattr(m, 'model') else m.get('name') or m.get('model')
                print(f" - {name}")
    except Exception as e:
        print(f"Error listing models: {e}")

    model_name = "deepseek-ocr:latest"
    image_path = r"g:\\_era\\vllm-ocr\\backend\\sample-images\\test-ocr.PNG"
    
    print(f"\nTesting model {model_name} with image {image_path}...")
    
    prompts = [
        "Extract all text from this image. Output as Markdown."
    ]

    for p in prompts:
        print(f"\n--- Testing prompt: '{p}' ---")
        try:
            response = await client.generate(
                model=model_name,
                prompt=p,
                images=[image_path]
            )
            print("Response length:", len(response.response))
            print("Eval count:", response.eval_count if hasattr(response, 'eval_count') else 'N/A')
            print("Generated Text Preview:", response.response[:200].replace('\n', ' '))
            if len(response.response) > 0:
                 print("Full Response:\n", response.response)
        except Exception as e:
            print(f"Error generating with prompt '{p}': {e}")

if __name__ == "__main__":
    asyncio.run(test_ollama())
