import io
from flask import Flask, request, send_file, jsonify
import psycopg2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

from image_processing.load_and_resize import load_and_resize

app = Flask(__name__)

# Replace with your PostgreSQL connection URI
db_uri = "postgresql://apple@localhost/challenge2"

def fetch_data_from_db(depth_min, depth_max):
    conn = psycopg2.connect(db_uri)
    cur = conn.cursor()
    cur.execute('''
    SELECT pixels FROM images WHERE depth BETWEEN %s AND %s
    ''', (depth_min, depth_max))
    rows = cur.fetchall()
    conn.close()

    images = [np.frombuffer(row[0], dtype=np.uint8) for row in rows]
    return images

@app.route('/images', methods=['GET'])
def get_images():
    try:

                # Load and resize images, then store in database
        image_csv_path = 'data.csv'  # Replace with your CSV file path
        processed_images = load_and_resize(image_csv_path)
        store_in_db(processed_images)
        
        depth_min = int(request.args.get('depth_min', 0))
        depth_max = int(request.args.get('depth_max', 200))
        filtered_frames = fetch_data_from_db(depth_min, depth_max)

        color_mapped_frames_list = []
        color_map = plt.get_cmap('gist_rainbow')

        for img_frame in filtered_frames:
            img_frame = img_frame.reshape(1, -1)  # Reshape each frame to the original shape
            color_mapped_frame = color_map(img_frame)
            color_mapped_frame = (color_mapped_frame[:, :, :3] * 255).astype(np.uint8)  # Convert to uint8 RGB values
            color_mapped_frames_list.append(color_mapped_frame)

        # Concatenate frames into a single image
        concatenated_frames = np.concatenate(color_mapped_frames_list, axis=0)

        # Create PIL image from numpy array
        pil_img = Image.fromarray(concatenated_frames)

        # Create an in-memory stream for image to send
        img_io = io.BytesIO()
        pil_img.save(img_io, format='PNG')
        img_io.seek(0)

        # Send the image file as a response
        return send_file(img_io, mimetype='image/png')

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def store_in_db(processed_images):
    conn = psycopg2.connect(db_uri)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS images (
        depth INTEGER PRIMARY KEY,
        pixels BYTEA
    )
    ''')
    conn.commit()

    for image in processed_images:
        pixels_bytes = image['pixels'].tobytes()

        cur.execute('''
        INSERT INTO images (depth, pixels) VALUES (%s, %s)
        ON CONFLICT (depth) DO NOTHING
        ''', (image['depth'], psycopg2.Binary(pixels_bytes)))

    conn.commit()
    cur.close()
    conn.close()
