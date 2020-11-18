# Text-To-Video

The idea of this project is to be able to _generate_ videos just from text input that includes:

* Images.
* Videos.
* Voice over.
* Music.
---
This is a little fun side project that I plan to work on in my free time over the next few weeks.

# Current status

Given a script (text with a special template), the program will scrap google images for requested images, and use WaveNet TTS to voice over the script.

# Script template

## Image tag
```
[IMAGE: Shonen anime] In anime, shonen in particular, characters will often have incredible powers that will set them aside from the rest of the characters.
```

Your script must always start with an `[IMAGE: keyword count]` tag, the `IMAGE` tells the program what images to search and display till the next `[IMAGE]` tag, the program will then turn the following text into voice over, and display each image for `speech duration/count` seconds.

`keyword` : The keyword that the program will use to search google images

`count` (Optional) : Number of images to be shown in this segment of video. Defaults to 5.

## Voice Tag
```
[IMAGE: strength anime characters]
But some characters, however, [VOICE: J]manage to be heroes in their own way, meaning that they don't actually posses powers.[/VOICE]
they go by sheer strength and will power instead. In this video you will see 10 anime characters who are overpowered without super powers.
```
You can wrap text in `[VOICE: voice_name]` tag, notice there's a closing tag for this one `[/VOICE]`, you can find more info about voice names [here](https://cloud.google.com/text-to-speech/docs/voices).

For simplicity, this program uses `en-US-Wavenet-` voices, and you need to pass the voice name letter to the tag, this will be changed later as more language support is added.

# How to run

Create a virtual environment and run

`pip install -r requirement.txt`

Then you can create a script in `test_script.txt` and run 

`python main.py`

# Important Note
This program uses Google's `Cloud text-to-speech`, so sadly you need to enable their API set up authentication to work and try this program. Check more inforamtion on how to do this [here](https://cloud.google.com/text-to-speech/docs/libraries).



# Example
Uploading on YouTube, Soon!


# TODOs
- [ ] Create a pipeline that handles the text processing for the template with many tags.
- [ ] Add new video tag (from file) to the script template.
- [ ] Add new music tag (from file) to the script template.
- [ ] Add tags for special video effects.
- [ ] Add multiple keyword for image search, comma separated.
- [ ] Add ArgParser to the program instead of using `main.py`.
- [ ] Variable display time for images.
- [ ] Validation and testing.
- [ ] Add other languages support for TTS.
- [ ] Explore more TTS options, and machine learning tools that can help with this project.

# License
[MIT](./LICENSE)