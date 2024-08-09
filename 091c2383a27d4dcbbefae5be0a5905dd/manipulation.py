from PIL import ImageDraw
from PIL import Image as PILImage
from io import BytesIO
import random
import numpy as np
import cv2

COLOURS = [
    cv2.COLOR_BGR2GRAY, cv2.COLOR_RGB2BGR, cv2.COLOR_RGB2BGRA,
    cv2.COLOR_RGB2HSV, cv2.COLOR_RGB2LUV, cv2.COLOR_RGB2HLS,
    cv2.COLOR_RGB2XYZ, cv2.COLOR_RGBA2GRAY, cv2.COLOR_RGB2YUV
]

def randomize():
    return random.randint(0, 255)

def manipulate(content):
    choice = random.choice(1, 2)
    if choice == 1:
        image = cv2.imdecode(np.frombuffer(content, np.uint8), cv2.IMREAD_UNCHANGED)
        colour = cv2.cvtColor(image, random.choice(COLOURS))
        orb = cv2.ORB_create()
        keypoints = orb.detect(colour, None)
        DOT_Layer = np.zeros_like(image, dtype=np.uint8)
        for keypoint in keypoints:
            x, y = keypoint.pt
            color = (randomize(), randomize(), randomize(), random.randint(1, 45))
            cv2.circle(DOT_Layer, (int(x), int(y)), 3, color, -1)
        result = cv2.addWeighted(image, 1, DOT_Layer, random.uniform(0.05, 4), 0)
        _, buffer = cv2.imencode(".png", result)
        return buffer.tobytes()
    elif choice == 2:
        image = PILImage.open(BytesIO(content)).convert("RGBA")
        width, height = image.size
        dotSize = random.uniform(0.25, 3)
        dotColor = (randomize(), randomize(), randomize(), random.randint(1, 35))
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        dot = PILImage.new("RGBA", image.size, (0, 0, 0, 0))
        dotDraw = ImageDraw.Draw(dot)
        dotDraw.ellipse((x - dotSize, y - dotSize, x + dotSize, y + dotSize), fill=dotColor)
        modimage = PILImage.alpha_composite(image, dot)
        imgBytes = BytesIO()
        modimage.save(imgBytes, format="PNG")
        return imgBytes.getvalue()
