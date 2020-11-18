"""The main class for the project.
This module turns given text to a video with images grabbed from google search
as well as audio from google tts.
"""

import os

from moviepy.editor import (
    concatenate_videoclips,
)

from images_utils.image_grabber import ImageGrabber
from text_utils.text_processor import TextProcessor
from audio_utils.audio import WaveNetTTS

from utils.common import mkdir


class TextToVideo:
    def __init__(self, text: str, output: str):
        """This class processes the images and audio then generates the required vidoe

        Args:
            text (str): Text to turn into images/audio
            output (str): Output file name
        """
        self.text = text
        self.output = output
        self._gid = ImageGrabber(
            search_options="ift:jpg",
            resize=True,
        )
        self._text_processor = TextProcessor(self.text)
        self._wnTTS = WaveNetTTS()
        self._output_folder = "output"
        self._video_clips = []
        mkdir(os.path.join(os.getcwd(), self._output_folder))

    def generate_video(self) -> None:
        """Generates the video clips/segments to be concatenated on save"""

        video_segments = self._text_processor.video_segments
        for segment in video_segments:
            final_clip = segment.generate_segment(self._wnTTS, self._gid)
            self._video_clips.append(final_clip)

    def save_video(self, fps: int = 24) -> None:
        """Saves the processed video

        Args:
            fps (int, optional): Desired video FPS. Defaults to 24.
        """

        if len(self._video_clips) == 0:
            raise VideoElementsNotProcessed

        final_video = concatenate_videoclips(self._video_clips, method="compose")
        final_video.fps = 24
        final_video.write_videofile(f"{self._output_folder}/{self.output}")


class VideoElementsNotProcessed(Exception):
    pass