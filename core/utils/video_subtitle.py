import assemblyai as aai
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from dotenv import load_dotenv
from moviepy.config import change_settings
import os

# Connecting to aai
load_dotenv()
token_aai = os.getenv("TOKEN_ASSEMBLYAI")
aai.settings.api_key = token_aai

# Once you have installed it, ImageMagick will be automatically detected by MoviePy, except on Windows
if os.name == 'nt':
	# Specify your path to I mageMagick - "C:\\Program Files\\ImageMagick_VERSION\\magick.exe"
	IMAGEMAGICK_BINARY = 'C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe'
	change_settings({'IMAGEMAGICK_BINARY': IMAGEMAGICK_BINARY})


class VideoSubtitlerGenerator:
	def __init__(self, audio_path: str, video_path: str, save_file_name: str):
		"""
		:param audio_path: Accepts the path to the audio|video
		:param save_file_name: The name for saving subtitles and videos.
		"""
		self.save_file_name = save_file_name
		subtitles = self.generate_subtitles(audio_path)
		self.subtitles_text = subtitles

		# Saving subtitles to an srt file
		with open(self.save_file_name + '.srt', "w") as file:
			file.write(self.subtitles_text)

		self.generate_video(video_path)

	@staticmethod
	def generate_subtitles(audio_path: str) -> str:
		"""
		:return subtitles: Generated subtitles
		"""

		transcriber = aai.Transcriber().transcribe(audio_path)
		subtitles = transcriber.export_subtitles_srt()

		return subtitles

	def generate_video(self, video_path: str):
		"""Adding subtitles to a video"""
		video = VideoFileClip(video_path, audio=True)
		w, h = video.size

		generator = lambda txt: TextClip(txt, font='Georgia-Regular', fontsize=16, color='black').set_position('center')
		subtitles = SubtitlesClip(self.save_file_name + '.srt', generator)

		result = CompositeVideoClip([video, subtitles.set_position(('center', 'center'))])

		# Save video
		result.write_videofile(
			self.save_file_name + '.mp4', fps=video.fps,
			temp_audiofile="tmp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")


