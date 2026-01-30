#!/bin/bash

# Create models folder if not exists
mkdir -p models
cd models

# Function to download and unzip
download_model () {
    url=$1
    zipfile=$(basename "$url")
    folder="${zipfile%.zip}"

    echo "Downloading $folder..."
    wget -c "$url" -O "$zipfile"

    echo "Unzipping $folder..."
    unzip -o "$zipfile" -d .
    rm -f "$zipfile"
}

# English
download_model https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip

# Indian languages
download_model https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip   # Hindi
download_model https://alphacephei.com/vosk/models/vosk-model-te-in-0.4.zip       # Telugu
download_model https://alphacephei.com/vosk/models/vosk-model-ta-0.1.zip          # Tamil
download_model https://alphacephei.com/vosk/models/vosk-model-kn-0.5.zip          # Kannada
download_model https://alphacephei.com/vosk/models/vosk-model-ml-0.4.zip          # Malayalam
download_model https://alphacephei.com/vosk/models/vosk-model-bn-0.1.zip          # Bengali
download_model https://alphacephei.com/vosk/models/vosk-model-gu-0.4.zip          # Gujarati
download_model https://alphacephei.com/vosk/models/vosk-model-pa-0.5.zip          # Punjabi
download_model https://alphacephei.com/vosk/models/vosk-model-mr-0.4.zip          # Marathi
download_model https://alphacephei.com/vosk/models/vosk-model-ur-pk-0.1.zip       # Urdu
download_model https://alphacephei.com/vosk/models/vosk-model-or-0.1.zip          # Odia
download_model https://alphacephei.com/vosk/models/vosk-model-as-0.1.zip          # Assamese

echo "✅ All models downloaded and ready in ./models/"
