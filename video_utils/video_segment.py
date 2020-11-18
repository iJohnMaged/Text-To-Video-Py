import random
from typing import List, Dict
from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    VideoClip,
    concatenate_videoclips,
    concatenate_audioclips,
)
from audio_utils.audio import WaveNetTTS
from images_utils.image_grabber import ImageGrabber


class VideoSegment:
    """This class represents and handles a single video segment, which
    includes audio, images. Input text is split into different segments
    every [IMAGE] tag.

    Attributes:
        text (str): Raw input text for this segment
        voiceover_text (List[Dict]): List of Dict of this format (voice name,
        text to be voiced over).
        image_keyword (str): Keyword for images to be scraped for this segment.
        segment_number (int): number of segment in the entire video.
        images_number (int): number of images to be displayed in this segment
    """

    def __init__(
        self,
        text: str,
        voiceover_text: List[Dict],
        image_keyword: str,
        segment_number: int,
        images_number: int = 5,
    ):
        self.segment_number = segment_number
        self.text = text
        self.voiceover_text = voiceover_text
        self.image_keyword = image_keyword
        self.images_number = images_number

    def generate_segment(self, tts: WaveNetTTS, gid: ImageGrabber) -> VideoClip:
        """Generates a video segment by searching the images, combining them
        and adding TTS voice over.

        Args:
            tts (WaveNetTTS): TTS object
            gid (ImageGrabber): Image search/grabber object

        Returns:
            VideoClip: complete video clip combined from images/TTS.
        """

        print(f"[INFO] Generating video segment #{self.segment_number}")
        image_clips = []
        audio_clips = []

        # Total duration of segment in seconds
        segment_duration = 0

        # Start by first generating TTS audio file
        for idx, voiceover in enumerate(self.voiceover_text):
            audio_file, duration = tts.generate_tts(
                voiceover["text"],
                f"video-segment{self.segment_number}-{idx+1}.mp3",
                voiceover["voice"],
            )
            # Add audio duration to the segment duration
            segment_duration += duration
            audio_clips.append(AudioFileClip(audio_file))

        # Image duration is total duration / number of images, this could be
        # changed to be random period of times between 0 and segment_duration
        image_duration = segment_duration / self.images_number
        images = gid.search_image(self.image_keyword)
        # Randomly select the images, this needs to be checked for number of
        # images downloaded.
        random_images = random.sample(images, self.images_number)

        # Create the image clips and produce final video
        for video_image in random_images:
            image_clips.append(ImageClip(video_image, duration=image_duration))

        audio_clip = concatenate_audioclips(audio_clips)
        final_clip = concatenate_videoclips(image_clips, method="compose")
        final_clip.fps = 24
        final_clip = final_clip.set_audio(audio_clip)
        return final_clip
