import openai
import os
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

def resize_image(image_file, max_width=500, max_height=500):
    """Resize the image to reduce its size before encoding."""
    try:
        image = Image.open(image_file)
        print("Original image size:", image.size)
        
        if image.mode != "RGB":
            print("Converting image to RGB mode.")
            image = image.convert("RGB")
        
        image.thumbnail((max_width, max_height))
        print(f"Resized image size: {image.size}")
        
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=85)  # Lower quality for smaller size
        buffer.seek(0)
        return buffer
    except Exception as e:
        print(f"Error resizing image: {e}")
        raise ValueError(f"Error resizing image: {e}")

def encode_image_base64(image_file):
    """Encode the resized image to Base64 string."""
    print("Resizing and encoding image to Base64...")
    resized_image = resize_image(image_file)
    encoded_image = base64.b64encode(resized_image.read()).decode("utf-8")
    print(f"Base64-encoded image size: {len(encoded_image)} characters.")
    return encoded_image

@app.route('/api/openai', methods=['POST'])
def openai_request():
    print("Received a request at /api/openai")
    data = request.form
    user_text = data.get("text")
    images = request.files.getlist("images")  # Get all uploaded images

    print(f"User text: {user_text}")
    print(f"Number of images received: {len(images)}")

    if not user_text and not images:
        print("No input provided. Returning error response.")
        return jsonify({"error": "No input provided. Please submit text or images."}), 400

    try:
        # Encode all images to Base64
        image_payload = []
        for image_file in images:
            base64_image = encode_image_base64(image_file)
            image_payload.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
            })
            print(f"Encoded image size: {len(base64_image)} characters.")

        # Build the message payload
        content_payload = [{"type": "text", "text": user_text}] if user_text else []
        content_payload.extend(image_payload)

        messages = [{"role": "user", "content": content_payload}]
        print(f"Final messages sent to OpenAI: {messages}")

        # Send request to OpenAI
        print("Sending request to OpenAI API...")
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages
        )
        print("Response received from OpenAI API.")

        ai_response = response.choices[0].message['content']
        print(f"AI response: {ai_response}")

        return jsonify({"result": ai_response})
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Starting Flask server on port 5000...")
    app.run(port=5000)
