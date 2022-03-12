# Twitter Youtube Uploader Bot 

With this code, you can automate the process of reuploading your (or someone else's) videos from Twitter to your YouTube channel.

All you need is the Twitter and YouTube API access and you are good to go - the code will take of everything from downloading the videos, to naming them after the tweets and putting them in corresponding folders, and then uploading them to YouTube with title, description, and tags taken care of (to a certain extent, feel free to tweak it as you'd like, there is a lot of refinement that can be done depending on your workflow).
## Installation

After downloading the project, you can create a virtual environment to keep your native Python packages clean (more about that in [the official Python docs](https://docs.python.org/3/library/venv.html).

requirements.txt file is attached, so that should get you covered.

## Quick Start Guide
There are currently 2 code files there, one for Python and one for Jupyter, which I find much easier to use when working with APIs. In the Jupyter Notebook, you'll see 4 blocks of code, all to an extent separated by logic:
1. Importing all the libraries needed.
2. Everything to do with authentication and parameters (related to both Twitter and Youtube). Technically, you don't even need to know what's in blocks 3 and 4, as everything besides the actual code logic can be controlled from here.
3. All Twitter logic of authenticating on Twitter, finding the desired timeline, going over the number of tweets that you've specified in the 2nd block, and checking if they have any videos. If they do, then you check the bitrate to download the highest quality one, create an "output" folder, and use the API to download the video and the thumbnail, renaming them from something random to the text body of the tweet (up to a certain number of characters).
4. All Youtube logic of finding the video and image that you've saved in the previous blogs, modifying them to meet the YouTube standards, getting the date and time into the right format, uploading the media, and so on.



## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[Apache](https://choosealicense.com/licenses/apache-2.0/)
