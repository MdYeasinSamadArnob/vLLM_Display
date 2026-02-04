import asyncio
import ollama
import os

async def test_prompts():
    client = ollama.AsyncClient(host='http://10.11.200.109:11434')
    
    image_path = r"g:\\_era\\vllm-ocr\\backend\\sample-images\\test-ocr.PNG"
    if not os.path.exists(image_path):
        print(f"ERROR: Image not found at {image_path}")
        return

    print(f"Image size: {os.path.getsize(image_path)} bytes")

    # 1. Sanity check with text-only model
    print("\n--- Sanity Check: llama3.2:3b (Text only) ---")
    try:
        response = await client.generate(
            model="llama3.2:3b",
            prompt="Say hello.",
        )
        print("Llama response:", response.response)
    except Exception as e:
        print(f"Llama failed: {e}")

    # 2. Test deepseek-ocr
    model_name = "deepseek-ocr:latest"
    # model_name = "qwen3-vl:8b" # Trying alternative model
    print(f"\n--- Testing {model_name} ---")
    
    # Force unload to reset state
    print("  > Unloading model...")
    try:
        await client.generate(model=model_name, prompt="", keep_alive=0)
    except:
        pass

    prompts = [
        "Extract all text from this image.",
    ]

    for p in prompts:
        print(f"\nPrompt: '{p}'")
        try:
            # Try streaming to see if it starts generating garbage immediately
            print("  > Streaming response with num_ctx=4096...")
            async for part in await client.generate(
                model=model_name,
                prompt=p,
                images=[image_path],
                stream=True,
                options={
                    "num_ctx": 4096,
                    "temperature": 0.1
                }
            ):
                print(part['response'], end='', flush=True)
            print("\n  > Done.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_prompts())
