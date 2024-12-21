import assemblyai as aai
from assemblyai import settings
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from dotenv import load_dotenv
from moviepy.config import change_settings
import os
import re
from uuid import uuid4
import srt_equalizer

from .settings import tmp_dir, font_path

# Connecting to aai
load_dotenv()
token_aai = os.getenv("TOKEN_ASSEMBLYAI")
aai.settings.api_key = token_aai

# Once you have installed it, ImageMagick will be automatically detected by MoviePy, except on Windows
if os.name == 'nt':
	# Specify your path to ImageMagick - "C:\\Program Files\\ImageMagick_VERSION\\magick.exe"
	IMAGEMAGICK_BINARY = 'C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe'
	change_settings({'IMAGEMAGICK_BINARY': IMAGEMAGICK_BINARY})
else:
	IMAGEMAGICK_BINARY = input('specify the path to ImageMagick: ')
	change_settings({'IMAGEMAGICK_BINARY': IMAGEMAGICK_BINARY})


class VideoSubtitleGenerator:
	def __init__(self, audio_path: str, video_path: str, output_file_name: str | None = None, target_chars: int = 1):
		"""
		:param audio_path: Accepts the path to the audio|video file
		:param video_path:  Accepts the path to the video file
		:param output_file_name: The name for saving subtitles and videos. By default, it takes = video_path
		:param target_chars: If the word is longer than the specified number of characters, then the whole word is used
		"""
		self.output_file_name = output_file_name
		self.tmp_file = str(tmp_dir / str(uuid4()))

		subtitles = self.generate_subtitles(audio_path)
		self.subtitles_text = subtitles
		self.edit_subtitles(subtitles)
		self.generate_video(video_path)

	def edit_subtitles(self, subtitles: str):
		# Saving subtitles to a srt
		with open(self.tmp_file + '.srt', 'w', encoding='utf-8') as temp_srt:
			temp_srt.write(subtitles)
		srt_equalizer.equalize_srt_file(self.tmp_file + '.srt', self.tmp_file + '.srt', 1)
		processed_lines = []
		with open(self.tmp_file + '.srt', 'r+', encoding='utf-8') as temp_srt:
			for line in temp_srt.readlines():
				if re.match(r'\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}', line):
					# If the line matches the timestamp format, add it to the list without any changes
					processed_lines.append(line)
					continue
				# Otherwise, remove punctuation marks from the text and add the processed line to the list
				processed_lines.append(re.sub(r'[^\w\s]', '', line))

			temp_srt.seek(0)  # Move the file pointer to the beginning of the file
			temp_srt.truncate(0)  # Clear the file content
			# Rewrite the file with the processed lines
			temp_srt.write(''.join(processed_lines))

	@staticmethod
	def generate_subtitles(audio_path: str) -> str:
		"""
		:return subtitles: Generated subtitles
		"""

		transcriber = aai.Transcriber(max_workers=10).transcribe(audio_path)
		subtitles = transcriber.export_subtitles_srt()

		return subtitles

	def generate_video(self, video_path: str):
		"""Adding subtitles to a video"""
		video = VideoFileClip(video_path, audio=True)

		generator = lambda txt: TextClip(
			txt,
			font=font_path,
			fontsize=100,
			color='yellow',
			stroke_color="yellow",
			stroke_width=5,
		)
		subtitles = SubtitlesClip(self.tmp_file + '.srt', generator)

		result = CompositeVideoClip([video, subtitles.set_position(('center', 'center'))])

		# Save video
		result.write_videofile(
			self.output_file_name + '.mp4', fps=video.fps,
			temp_audiofile=self.tmp_file + '.m4a', remove_temp=True, codec="libx264", audio_codec="aac")
