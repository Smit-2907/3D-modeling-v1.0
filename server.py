import os
import time
import shutil
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from gradio_client import Client, handle_file

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# THE AI BRAIN: Stability AI's High-Resolution 3D Sculptor
GRADIO_SPACE = "stabilityai/stable-fast-3d" 
client = None

# Ensure the models directory exists
MODELS_DIR = os.path.join(os.getcwd(), "models")
if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR)

def get_client():
    global client
    if client is None:
        print(f"--- [AI PROCESSOR CONNECTING] ---")
        print(f"Target Model: {GRADIO_SPACE}")
        try:
            # We connect to a high-perf remote model to keep your local machine fast
            client = Client(GRADIO_SPACE)
            print(f"Status: AI ENGINE IS ONLINE")
        except Exception as e:
            print(f"Status: ERROR (AI SLEEPING): {str(e)}")
            return None
    return client

@app.route('/generate', methods=['POST'])
def generate():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    image = request.files['image']
    temp_name = f"input_{int(time.time())}.jpg"
    image.save(temp_name)
    
    print(f"--- [NEW TASK RECEIVED] ---")
    print(f"Local Image: {temp_name}")
    
    try:
        c = get_client()
        if not c: return jsonify({"error": "AI Connection Failed"}), 500

        print(f"[PROCESSOR] Sculpting 3D geometry from pixels...")
        
        try:
            # Stage 1: Send to Stability AI Cloud Processor
            result = c.predict(input_image=handle_file(temp_name), api_name="/predict")
        except:
            # Fallback for different API versions
            result = c.predict(handle_file(temp_name))

        # Handle the resulting 3D Model file
        glb_path = None
        if isinstance(result, str) and result.endswith('.glb'):
            glb_path = result
        elif isinstance(result, (list, tuple)) and len(result) > 0:
            for item in result:
                if isinstance(item, str) and item.endswith('.glb'):
                    glb_path = item
                    break
        
        if not glb_path:
             return jsonify({"error": "AI process failed - No GLB generated"}), 500

        preview_name = "latest_preview.glb"
        shutil.copy(glb_path, preview_name)
        
        if os.path.exists(temp_name): os.remove(temp_name)
        
        print(f"[COMPLETED] 3D Model built. Exporting to GLB...")
        return send_file(preview_name, as_attachment=True)

    except Exception as e:
        print(f"[STALLED] AI Engine Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/save', methods=['POST'])
def save_model():
    data = request.json
    item_name = data.get('name', 'new_model').replace(' ', '_').lower()
    
    if not os.path.exists("latest_preview.glb"):
        return jsonify({"error": "No model found"}), 400

    final_path = os.path.join(MODELS_DIR, f"{item_name}.glb")
    shutil.copy("latest_preview.glb", final_path)
    
    print(f"[STORAGE] Item '{item_name}' permanently saved to menu library.")
    return jsonify({"success": True, "path": final_path})

if __name__ == "__main__":
    print("=======================================")
    print("   AURA AI 3D PROCESSOR: ONLINE        ")
    print("   Listening at: http://localhost:5000 ")
    print("=======================================")
    app.run(host='0.0.0.0', port=5000, debug=False)
