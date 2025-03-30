import base64
import io
from flask import Flask, request, jsonify
from PIL import Image

app = Flask(__name__)

# ---------------
# Load your model here once (optional).
# For illustration, we’ll just hardcode a face shape prediction.
# ---------------
# Example: 
# import torch
# model = torch.load('face_shape_model.pth')
# model.eval()

# ---------------
# Hairstyle recommendations (converted from your JS map to a Python dict).
# ---------------
hairstyle_recommendations = {
    "heart": {
        "male": [
            { "id": 1, "name": "Side-Parted Style", "image": "/images/male/heart/side-parted.jpg" },
            { "id": 2, "name": "Textured Fringe", "image": "/images/male/heart/textured-fringe.jpg" },
            { "id": 3, "name": "Crew Cut", "image": "/images/male/heart/crew-cut.jpg" },
            { "id": 4, "name": "Quiff", "image": "/images/male/heart/quiff.jpg" },
            { "id": 5, "name": "Angular Fringe", "image": "/images/male/heart/angular-fringe.jpg" }
        ],
        "female": [
            { "id": 6, "name": "Long Layers with Side-Swept Bangs", "image": "/images/female/heart/long-layers.jpg" },
            { "id": 7, "name": "Chin-Length Bob", "image": "/images/female/heart/chin-length-bob.jpg" },
            { "id": 8, "name": "Deep Side Part with Loose Waves", "image": "/images/female/heart/deep-side-part.jpg" },
            { "id": 9, "name": "Shoulder-Length Lob", "image": "/images/female/heart/shoulder-length-lob.jpg" },
            { "id": 10, "name": "Side-Swept Pixie Cut", "image": "/images/female/heart/side-swept-pixie.jpg" }
        ]
    },
    "oblong": {
        "male": [
            { "id": 11, "name": "Medium-Length Layered Cut", "image": "/images/male/oblong/medium-layered.jpg" },
            { "id": 12, "name": "Side-Swept Bangs", "image": "/images/male/oblong/side-swept-bangs.jpg" },
            { "id": 13, "name": "Classic Side Part", "image": "/images/male/oblong/classic-side-part.jpg" },
            { "id": 14, "name": "Textured Crop", "image": "/images/male/oblong/textured-crop.jpg" },
            { "id": 15, "name": "Fringe Cut", "image": "/images/male/oblong/fringe-cut.jpg" }
        ],
        "female": [
            { "id": 16, "name": "Shoulder-Length Waves", "image": "/images/female/oblong/shoulder-waves.jpg" },
            { "id": 17, "name": "Soft Curls with Bangs", "image": "/images/female/oblong/soft-curls-bangs.jpg" },
            { "id": 18, "name": "Blunt Bob with Bangs", "image": "/images/female/oblong/blunt-bob-bangs.jpg" },
            { "id": 19, "name": "Layered Lob", "image": "/images/female/oblong/layered-lob.jpg" },
            { "id": 20, "name": "Curtain Bangs with Layers", "image": "/images/female/oblong/curtain-bangs-layers.jpg" }
        ]
    },
    "oval": {
        "male": [
            { "id": 21, "name": "Buzz Cut", "image": "/images/male/oval/buzz-cut.jpg" },
            { "id": 22, "name": "Quiff", "image": "/images/male/oval/quiff.jpg" },
            { "id": 23, "name": "Pompadour", "image": "/images/male/oval/pompadour.jpg" },
            { "id": 24, "name": "Slicked-Back Undercut", "image": "/images/male/oval/slicked-back-undercut.jpg" },
            { "id": 25, "name": "Faux Hawk", "image": "/images/male/oval/faux-hawk.jpg" }
        ],
        "female": [
            { "id": 26, "name": "Pixie Cut", "image": "/images/female/oval/pixie-cut.jpg" },
            { "id": 27, "name": "Long Waves", "image": "/images/female/oval/long-waves.jpg" },
            { "id": 28, "name": "Blunt Bob", "image": "/images/female/oval/blunt-bob.jpg" },
            { "id": 29, "name": "Shag Cut", "image": "/images/female/oval/shag-cut.jpg" },
            { "id": 30, "name": "Curtain Bangs with Layers", "image": "/images/female/oval/curtain-bangs-layers.jpg" }
        ]
    },
    "round": {
        "male": [
            { "id": 31, "name": "Pompadour", "image": "/images/male/round/pompadour.jpg" },
            { "id": 32, "name": "Faux Hawk", "image": "/images/male/round/faux-hawk.jpg" },
            { "id": 33, "name": "Flat Top", "image": "/images/male/round/flat-top.jpg" },
            { "id": 34, "name": "Side Part with Volume", "image": "/images/male/round/side-part-volume.jpg" },
            { "id": 35, "name": "Spiky Hair", "image": "/images/male/round/spiky-hair.jpg" }
        ],
        "female": [
            { "id": 36, "name": "Long, Face-Framing Layers", "image": "/images/female/round/long-layers.jpg" },
            { "id": 37, "name": "Side-Swept Bangs", "image": "/images/female/round/side-swept-bangs.jpg" },
            { "id": 38, "name": "Asymmetrical Bob", "image": "/images/female/round/asymmetrical-bob.jpg" },
            { "id": 39, "name": "High Bun or Ponytail", "image": "/images/female/round/high-bun.jpg" },
            { "id": 40, "name": "Layered Shag Cut", "image": "/images/female/round/layered-shag.jpg" }
        ]
    },
    "square": {
        "male": [
            { "id": 41, "name": "Crew Cut", "image": "/images/male/square/crew-cut.jpg" },
            { "id": 42, "name": "Textured Crop", "image": "/images/male/square/textured-crop.jpg" },
            { "id": 43, "name": "Side-Parted Style", "image": "/images/male/square/side-parted.jpg" },
            { "id": 44, "name": "Quiff", "image": "/images/male/square/quiff.jpg" },
            { "id": 45, "name": "Ivy League Cut", "image": "/images/male/square/ivy-league.jpg" }
        ],
        "female": [
            { "id": 46, "name": "Curtain Bangs", "image": "/images/female/square/curtain-bangs.jpg" },
            { "id": 47, "name": "Italian Bob", "image": "/images/female/square/italian-bob.jpg" },
            { "id": 48, "name": "Feathered Shoulder-Length Cut", "image": "/images/female/square/feathered-shoulder.jpg" },
            { "id": 49, "name": "Side-Swept Bangs with Layers", "image": "/images/female/square/side-swept-bangs-layers.jpg" },
            { "id": 50, "name": "Textured Waves", "image": "/images/female/square/textured-waves.jpg" }
        ]
    }
}

@app.route('/api/analyze', methods=['POST'])
def analyze_image():
    """
    Endpoint to receive base64 image data + gender,
    run face shape prediction, and return
    recommended hairstyles.
    """
    data = request.get_json()
    image_data = data.get("image", "")
    gender = data.get("gender", "")

    if not image_data or not gender:
        return jsonify({"error": "Invalid data received"}), 400

    try:
        # 1) Decode the base64 image (remove the "data:image/jpeg;base64," part first).
        base64_str = image_data.split(",")[1]
        decoded_bytes = base64.b64decode(base64_str)

        # 2) Convert the bytes to a PIL image.
        pil_image = Image.open(io.BytesIO(decoded_bytes))

        # 3) Run your face-shape classification model.
        #    For demonstration, we’ll hardcode a result.
        #    Replace this with model inference code:
        # face_shape = predict_face_shape(pil_image, model)
        face_shape = "oval"  # Hardcoded example

        # 4) Get hairstyles from the map based on face_shape + gender.
        #    Make sure you handle potential errors if face_shape is not recognized.
        if face_shape in hairstyle_recommendations:
            recommended = hairstyle_recommendations[face_shape][gender]
        else:
            recommended = []

        # 5) Return result to frontend.
        return jsonify({
            "result": face_shape,
            "hairstyles": recommended
        }), 200

    except Exception as e:
        print("Error analyzing image:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
