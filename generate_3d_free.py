import sys
import os
from gradio_client import Client, handle_file

def generate_3d_free(image_path):
    print(f"🚀 Connecting to Free AI Space (LGM)...")
    
    # We are using a public space that provides High-Quality 3D models for free
    client = Client("ashawkey/LGM")
    
    print(f"⌛ Processing your image: {image_path}")
    print("   (This can take 30-60 seconds depending on the queue)")
    
    try:
        # LGM takes an image and converts it to a .glb
        result = client.predict(
            input_image=handle_file(image_path),
            api_name="/process"
        )
        
        # The result includes the GLB file path
        # In this specific space, the output is often a list [image, video, glb]
        glb_path = result[2] 
        
        # Move the file to your folder
        output_name = "baked_food_model.glb"
        os.rename(glb_path, output_name)
        
        print(f"✨ SUCCESS! Your free model is saved as: {output_name}")
        return output_name

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nTIP: Make sure you have the library installed: pip install gradio_client")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_3d_free.py <LOCAL_IMAGE_PATH>")
    else:
        generate_3d_free(sys.argv[1])
