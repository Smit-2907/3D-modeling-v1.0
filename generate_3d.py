import requests
import time
import sys

# REPLACE THIS with your free API key from https://www.meshy.ai/
API_KEY = "MSY_YOUR_API_KEY_HERE"

def generate_3d_from_image(image_url):
    print(f"🚀 Sending image to AI: {image_url}")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    
    # 1. Create a task
    payload = {
        "image_url": image_url,
        "enable_pbr": True,
    }
    
    response = requests.post(
        "https://api.meshy.ai/v1/image-to-3d",
        headers=headers,
        json=payload
    )
    
    if response.status_code != 202 and response.status_code != 200:
        print(f"❌ Error: {response.text}")
        return None
        
    task_id = response.json().get("result")
    print(f"✅ Task created! ID: {task_id}")
    
    # 2. Poll for results
    while True:
        print("⏳ AI is thinking... (this takes 1-2 minutes)")
        status_res = requests.get(
            f"https://api.meshy.ai/v1/image-to-3d/{task_id}",
            headers=headers
        )
        
        data = status_res.json()
        status = data.get("status")
        progress = data.get("progress")
        
        if status == "SUCCEEDED":
            model_url = data.get("model_urls").get("glb")
            print(f"✨ SUCCESS! Download your model here: {model_url}")
            return model_url
        elif status == "FAILED":
            print("❌ AI failed to generate the model.")
            break
            
        print(f"📊 Progress: {progress}%")
        time.sleep(10)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_3d.py <IMAGE_URL>")
    else:
        generate_3d_from_image(sys.argv[1])
