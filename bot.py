from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import yt_dlp
import os

# Your bot's API token
API_TOKEN = '7863809410:AAHrJ6wi2yVSGAgUe3euLGTTgqSGsjEf9a8'

# Ensure the downloads directory exists
os.makedirs('downloads', exist_ok=True)

# Function to download the YouTube video as MP3
def download_video_as_mp3(url: str, save_path: str) -> tuple:
    try:
        # yt-dlp options to download only the audio as MP3
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
            'ffmpeg_location': 'C:\\ffmpeg\\ffmpeg.exe'  # Replace with the path to your ffmpeg binary
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = os.path.join(save_path, f"{info_dict['title']}.mp3")
            return filename, info_dict['title']  # Return both filename and title
            
    except Exception as e:
        print(f"Error downloading video: {e}")
        return f"Error: {str(e)}", None

# Command handler for /start command
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Send me a YouTube video link, and I will download it as MP3 for you!')

# Function to handle messages (video URL)
async def handle_message(update: Update, context: CallbackContext) -> None:
    video_url = update.message.text
    if 'youtube.com' in video_url or 'youtu.be' in video_url:
        await update.message.reply_text("Processing your request... Please wait.")
        
        # Download the video as MP3
        mp3_file_path, title = download_video_as_mp3(video_url, 'downloads')
        
        if mp3_file_path.startswith("Error"):
            await update.message.reply_text(mp3_file_path)  # Send the error message to the user
        else:
            # Send the MP3 file back to the user with the original title
            with open(mp3_file_path, 'rb') as audio_file:
                await update.message.reply_audio(audio=audio_file, title=title, caption=f"Here is your MP3 file: {title}")
            
            # Optionally, clean up the file after sending
            os.remove(mp3_file_path)
    else:
        await update.message.reply_text("Please send a valid YouTube video URL.")

def main():
    # Initialize the bot with the API token
    application = Application.builder().token(API_TOKEN).build()

    # Add command and message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start polling for updates
    application.run_polling()

if __name__ == '__main__':
    main()
