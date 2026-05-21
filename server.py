{\rtf1\ansi\ansicpg1252\cocoartf2869
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 from flask import Flask, request, send_from_directory, jsonify\
import os\
from PIL import Image\
from datetime import datetime\
\
app = Flask(__name__)\
\
# Configuration\
UPLOAD_FOLDER = 'collected_images'\
LOG_FILE = 'metadata_log.txt'\
\
# Ensure the upload folder exists\
os.makedirs(UPLOAD_FOLDER, exist_ok=True)\
\
@app.route('/')\
def index():\
    # This serves your frontend HTML file\
    return send_from_directory('.', 'index.html')\
\
@app.route('/upload', methods=['POST'])\
def upload_file():\
    if 'file' not in request.files:\
        return jsonify(\{'status': 'error', 'message': 'No file part'\}), 400\
    \
    file = request.files['file']\
    \
    if file.filename == '':\
        return jsonify(\{'status': 'error', 'message': 'No selected file'\}), 400\
\
    if file:\
        # Save the image\
        filename = os.path.basename(file.filename)\
        filepath = os.path.join(UPLOAD_FOLDER, filename)\
        \
        try:\
            file.save(filepath)\
            \
            # Extract Metadata (EXIF)\
            metadata_log = []\
            try:\
                with Image.open(filepath) as img:\
                    metadata_log.append(f"Filename: \{filename\}")\
                    metadata_log.append(f"Size: \{img.size[0]\}x\{img.size[1]\}")\
                    \
                    # Try to get EXIF data (GPS, Date, etc.)\
                    if hasattr(img, '_getexif'):\
                        exif = img._getexif()\
                        if exif:\
                            for tag_id in exif:\
                                value = exif.get(tag_id)\
                                metadata_log.append(f"Tag \{tag_id\}: \{value\}")\
            except Exception as e:\
                metadata_log.append(f"Metadata Error: \{str(e)\}")\
\
            # Append to log file\
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")\
            with open(LOG_FILE, 'a') as f:\
                f.write(f"\\n--- Upload at \{timestamp\} ---\\n")\
                for line in metadata_log:\
                    f.write(line + "\\n")\
            \
            return jsonify(\{\
                'status': 'success', \
                'message': f'Image saved to \{UPLOAD_FOLDER\}',\
                'filename': filename,\
                'log_file': LOG_FILE\
            \})\
\
        except Exception as e:\
            return jsonify(\{'status': 'error', 'message': str(e)\}), 500\
\
if __name__ == '__main__':\
    # Run the app (debug=True for development)\
    app.run(debug=True, host='0.0.0.0')\
}