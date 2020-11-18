import os
from typing import Tuple, List
from PIL import Image
from google_images_download import google_images_download
from .google_crawl import run_search
import requests
from utils.common import mkdir


class ImageGrabber:
    """Responsible to grab and process images from the internet giving a
        keyword.
    Attributes:
        _search_options (str): Options to be passed to the search engine.
        _resize (bool): Whether to resize images after download or not.
        _size (Tuple[int, int]): Size to resize images to.
        images_count (int): number of images downloaded.
        _memory (Dict[str, str]): Mapping between keyword to files paths.
            this is checked before searching for a keyword to avoid multiple
            searches for the same keyword.
    """

    def __init__(
        self,
        search_options: str = "",
        resize: bool = False,
        size: Tuple[int, int] = (1920, 1080),
        to_download: int = 20,
    ):
        """Initialize class variables and gid instance
        Args:
            search_options (str, optional): Search options to pass to the
                downloader, e.g. isz:lt,islt:svga,itp:photo,ic:color,ift:jpg.
            resize (bool, optional): Resizes images after downloading if True.
                Defaults to False.
            size (Tuple[int, int], optional): Resizes images to this size if
                resize is set to True. Defaults to (1920, 1080).
            to_download (int): number of images to download
        """
        self._search_options = search_options
        self._resize = resize
        self._size = size
        self._downloader = google_images_download.googleimagesdownload()
        self.download_folder = os.path.join(os.getcwd(), "downloads")
        self.images_count = 0
        self.to_download = to_download
        self._memory = {}

        # Create downloads folder if it doesn't exist and load local images
        mkdir("downloads")
        self._load_images()

    def _load_images(self) -> None:
        """Tries to load local files first"""
        local_files = {}
        directory = os.path.join(os.getcwd(), "downloads")
        for root, _, files in os.walk(directory):
            # Skip the main folder
            if root == directory:
                continue
            local_files[os.path.basename(root).lower()] = []
            for file in files:
                local_files[os.path.basename(root).lower()].append(
                    os.path.abspath(os.path.join(root, file))
                )
        self._memory = local_files

    def _download_from_url(self, url: str, keyword: str) -> str:
        """Downloads a single image from a url

        Args:
            url (str): url to download
            keyword(str): keyword searched, to create directory.
        Returns:
            str: path to downloaded file
        """
        self.images_count += 1

        # Make keyword directory in downloads if it doesn't exist
        mkdir(f"{self.download_folder}/{keyword}")

        print(f"[INFO] Downloading from URL: {url}")
        print(
            "[INFO] Downloading to: "
            + f"{self.download_folder}/"
            + f"{keyword}/image_{self.images_count}.jpg"
        )

        # Load the image via requests
        res = requests.get(url)
        if res.status_code != 200:
            print(f"[INFO] Skipping downloading image, got status {res.status_code}")
            self.images_count -= 1
            return None

        img_data = res.content

        # Save image to desk
        with open(
            f"{self.download_folder}/{keyword}/image_{self.images_count}.jpg",
            "wb",
        ) as handler:
            handler.write(img_data)

        return f"{self.download_folder}/{keyword}/image_{self.images_count}.jpg"

    def search_image(self, keyword: str) -> List[str]:
        """Searches google images with the keyword given and arguments supplied to instance.
        Does not start a new search if keyword is already searched.

        Args:
            keyword (str): single keyword to search

        Returns:
            List[str]: List of downloaded files paths
        """

        word = keyword.strip()

        # Return images paths if it already exists
        if word.lower() in self._memory:
            return self._memory[word.lower()]

        print(f"[INFO] Downloading images for keyword: {word}")
        # Scrape google images search to get urls of images
        urls = run_search(word, "off", self.to_download, self._search_options)

        # Download the images and add the path to list
        paths = []
        for url in urls:
            path = self._download_from_url(url, word)
            if path is not None:
                paths.append(path)

        # Save keyword and paths to memory
        self._memory[word] = paths

        # Process images
        if self._resize and len(paths) > 0:
            directory = os.path.dirname(os.path.abspath(paths[0]))
            self._resize_images(self._size, directory)

        return paths

    def _resize_images(self, size: Tuple[int, int], directory: str) -> None:
        """resizes all images inside a directory to the given size

        Args:
            size (Tuple[int, int]): a 2-tuple for the desired size
            directory (str): path to directory, relative or absolute
        """

        # Get only files from that directory
        files = [
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
        ]

        for file in files:
            # Create a new black image with specified size as background
            background = Image.new("RGB", size)
            im = Image.open(file)

            # convert image mode to RGB
            if im.mode != "RGB":
                im = im.convert("RGB")

            # Resize image
            # TODO fix this
            wr = size[0] / im.width
            hr = size[1] / im.height

            if wr > hr:
                nw = (im.width) * hr
                im = im.resize((int(nw), size[1]), Image.ANTIALIAS)
            else:
                nh = (im.height) * wr
                im = im.resize((size[0], int(nh)), Image.ANTIALIAS)

            # Add the image to the background centered
            x = (size[0] - im.width) // 2
            y = (size[1] - im.height) // 2
            background.paste(im, (x, y))

            # To avoid saved WEBP images, which don't work with MoviePy.
            if im.format == "WEBP":
                background.save(file + ".jpg", "JPEG")
            else:
                background.save(file, "JPEG")


def main():
    ig = ImageGrabber(resize=True)
    ig.search_image("test")


if __name__ == "__main__":
    main()