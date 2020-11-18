from TextToVideo import TextToVideo


def main():
    with open("test_script.txt", "r") as f:
        text = f.read()
    text = text.replace("\n", " ")
    ttv = TextToVideo(text, "anime.mp4")
    ttv.generate_video()
    ttv.save_video()


if __name__ == "__main__":
    main()