"""This module processes custom text input used to generate videos.
So far the only tag supported is: [IMAGE: <IMAGE KEYWORD>]
"""

import re
from typing import List, Dict
from video_utils.video_segment import VideoSegment


class TextProcessor:

    TextTemplateRe = {
        "image": r"\[IMAGE: (.+?)(\d*?)]",
        "split_image": r"\[IMAGE: .+?\d*?]",
        "search_voice": r"\[VOICE: (.+?)](.+?)\[\/VOICE]",
        "split_voice": r"\[VOICE: .+?](.+?)\[\/VOICE]",
    }

    def __init__(self, text: str):
        """
        Args:
            text (str): Text to be processed
        """
        self.text = text
        self.video_segments = []
        self.sentences = []
        print("[INFO] Processing text...")
        self._process_text_for_images()
        print("[INFO] Processed text..")

    def _process_text_for_images(self) -> None:
        """processes and formats text
        Eventually, this function will set `self.sentences` to be an array of
        2-tuples: Tuple[sentence, images_keyword]. Then each pair, sentence
        will be used for voice over and images_keyword will be used for image
        search over this segment.
        """
        matches = re.finditer(
            TextProcessor.TextTemplateRe["image"], self.text, re.DOTALL
        )

        groups = []
        for _, match in enumerate(matches):
            try:
                images_number = int(match.group(2))
            except:
                images_number = 5
            groups.append((match.group(1), images_number))

        i = 0
        for sentence in re.split(
            TextProcessor.TextTemplateRe["split_image"],
            self.text,
            re.DOTALL,
        ):
            if len(sentence) > 0:
                self.video_segments.append(
                    VideoSegment(
                        sentence.strip(),
                        self._process_voices(sentence.strip()),
                        groups[i][0],
                        i + 1,
                        groups[i][1],
                    )
                )
                self.sentences.append((sentence.strip(), groups[i][0]))
                i += 1

    def _process_voices(self, text) -> List[Dict]:
        """Extracts [VOICE] tags from video and sets every group of text to the
        the correct voice.

        Args:
            text (str): Text to be processed

        Returns:
            List[Dict]: List of Dict of this format {"voice": str, "text": str}
            Where voice is the voice name and text is the text to be voiced
            over.
        """
        # TODO do this, but better.
        # Split all text on voice tags and sets everything to "default"
        voiceover_segment = []
        for sentence in re.split(
            TextProcessor.TextTemplateRe["split_voice"], text, re.DOTALL | re.MULTILINE
        ):
            if len(sentence.strip()) > 0:
                voiceover_segment.append({"voice": "DEFAULT", "text": sentence.strip()})

        # Iterate again but this time set the text to the correct voice in tag.
        for sentence in re.finditer(
            TextProcessor.TextTemplateRe["search_voice"], text, re.DOTALL | re.MULTILINE
        ):
            for idx, t in enumerate(voiceover_segment):
                if t["text"] == sentence.group(2).strip():
                    voiceover_segment[idx]["voice"] = sentence.group(1)

        return voiceover_segment
