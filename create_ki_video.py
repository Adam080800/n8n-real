import os
import requests
from PIL import Image
import io
import logging
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
HUGGINGFACE_TOKEN = os.getenv("HF_TOKEN")
FINAL_OUTPUT = "/tmp/final_tiktok.mp4"
TEMP_MEDIA_PATH = "/tmp/temp_media"
AUDIO_OUTPUT = "/tmp/voice.mp3"

if not os.path.exists(TEMP_MEDIA_PATH):
    os.makedirs(TEMP_MEDIA_PATH)

def generate_script():
    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct",
            headers={"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"},
            json={"inputs": "Erstelle ein kurzes, motivierendes TikTok-Skript auf Deutsch (max. 50 Wörter)."}
        )
        response.raise_for_status()
        result = response.json()
        return result[0]["generated_text"].strip() if isinstance(result, list) else "Heute ist dein Tag!"
    except Exception as e:
        logging.error(f"Textgenerierung fehlgeschlagen: {e}")
        return "Heute ist dein Tag!"

def generate_voiceover(text):
    try:
        response = requests.post(
            "https://ttsmp3.com/makemp3_new.php",
            data={"msg": text, "lang": "Maxim", "source": "ttsmp3"}
        )
        response.raise_for_status()
        mp3_url = response.json().get("MP3")
        mp3_data = requests.get(mp3_url).content
        with open(AUDIO_OUTPUT, "wb") as f:
            f.write(mp3_data)
    except Exception as e:
        logging.error(f"Voiceover fehlgeschlagen: {e}")

def generate_ki_images(prompt, num_images=2):
    image_paths = []
    try:
        for i in range(num_images):
            response = requests.post(
                "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1",
                headers={"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"},
                json={"inputs": f"A vibrant, motivational scene: {prompt}"}
            )
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content))
            image_path = os.path.join(TEMP_MEDIA_PATH, f"image_{i}.png")
            image.save(image_path)
            image_paths.append(image_path)
        return image_paths
    except Exception as e:
        logging.error(f"Bildgenerierung fehlgeschlagen: {e}")
        return [os.path.join(TEMP_MEDIA_PATH, "default.png")] * num_images

def combine_video_audio(image_paths, text):
    try:
        clips = [ImageClip(img).set_duration(3) for img in image_paths]
        video = concatenate_videoclips(clips, method="compose")
        audio = AudioFileClip(AUDIO_OUTPUT)
        video = video.set_duration(audio.duration)
        txt_clip = TextClip(text, fontsize=50, color='white', bg_color='black')
        txt_clip = txt_clip.set_pos('center').set_duration(audio.duration)
        final = CompositeVideoClip([video, txt_clip]).set_audio(audio)
        final.write_videofile(FINAL_OUTPUT, codec="libx264", audio_codec="aac", bitrate="1000k")
        logging.info(f"Video erstellt: {FINAL_OUTPUT}")
    except Exception as e:
        logging.error(f"Videoerstellung fehlgeschlagen: {e}")

def main():
    text = generate_script()
    logging.info(f"Text: {text}")
    generate_voiceover(text)
    image_paths = generate_ki_images(text)
    combine_video_audio(image_paths, text)

if __name__ == "__main__":
    main()
