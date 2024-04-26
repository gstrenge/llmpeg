# llmpeg
[![Ubuntu](https://github.com/gstrenge/llmpeg/actions/workflows/ubuntu.yml/badge.svg)](https://github.com/gstrenge/llmpeg/actions/workflows/ubuntu.yml)
[![macOS](https://github.com/gstrenge/llmpeg/actions/workflows/macos.yml/badge.svg)](https://github.com/gstrenge/llmpeg/actions/workflows/macos.yml)
[![Windows](https://github.com/gstrenge/llmpeg/actions/workflows/windows.yml/badge.svg)](https://github.com/gstrenge/llmpeg/actions/workflows/windows.yml) (Windows works fine, just a windows specific test is failing for poor reason, working on updating the test!)

Let's be honest, who really knows how to use [`ffmpeg`](https://github.com/FFmpeg/FFmpeg). Its that tool that is so helpful but not needed enough to justify learning all of its inner workings. The days of scrolling through stackoverflow are over, with `llmpeg`. This CLI tool interfaces with an OpenAI LLM (and has support for other LLM API providers) to convert your plain text commands into OS/platform specific ffmpeg commands. 

`llmpeg` is a powerful wrapper around [the popular multimedia library `ffmpeg`](https://github.com/FFmpeg/FFmpeg), designed to simplify video and audio processing for users who are not familiar with the intricacies of [`ffmpeg`](https://github.com/FFmpeg/FFmpeg) commands. By leveraging language model technology, `llmpeg` allows users to describe their multimedia processing tasks in natural language, and the tool generates and executes the appropriate [`ffmpeg`](https://github.com/FFmpeg/FFmpeg) commands automatically.

![](imgs/shell-tools.gif)

## Features

- **Ease of Use**: Simplify multimedia command generation using natural language inputs.
- **Powerful**: Leverage the full power of [`ffmpeg`](https://github.com/FFmpeg/FFmpeg) without the need to learn its complex options.
- **Flexible**: Suitable for a wide range of multimedia tasks from simple conversions to complex processing workflows.
- **Extensible**: LLM Interface allows for other LLM providers (i.e. Amazon Bedrock, Anthropic, etc.) to work as drop-in replacement for OpenAI LLM
- **Conversational**: Supports back-and-forth conversation with the LLM to fix mistakes or clarify misunderstandings
- **Contextual Awareness**: `llmpeg` is provided context on your OS, OS version, [`ffmpeg`](https://github.com/FFmpeg/FFmpeg) version, and [`ffmpeg`](https://github.com/FFmpeg/FFmpeg) executable path to ensure commands are tailored for your platform.

![](imgs/conversation.gif)

## Installation
This was developed on a linux system, but should have valid support on both Windows and MacOS. Automated tests and CI are going to be added soon to validate this behavior.

### OpenAI
This tool leverages your own LLM API access. In the case of using OpenAI (the default setup), you must ensure that you have your `OPENAI_API_KEY` environment variable properly set. You also must install `openai` with pip:

```
pip install openai
```

### Install from Source

```
git clone https://github.com/gstrenge/llmpeg.git
cd llmpeg
python3 -m pip install .
```

## Usage
Simply run `llmpeg "with your instructions in quotes"`. See examples below for more.

For more detailed information, run `llmpeg -h`:
```
usage: llmpeg [-h] [--backend {openai}] [--openai_model OPENAI_MODEL] instructions

Convert your instructions into an ffmpeg command.

positional arguments:
  instructions          A string containing instructions about the desired ffmpeg use

optional arguments:
  -h, --help            show this help message and exit
  --backend {openai}    The backend LLM API provider to use. Defaults to 'openai'.
  --openai_model OPENAI_MODEL
                        The OpenAI LLM Model that you would like to use.

```
### OpenAI
By default, `openai_model` is set to `gpt-3.5-turbo-0125`, which as of today, as the strongest model that can be used with a free developer account with $5 of free credit. If you have a developer account and are willing to pay for credits, you can change this to one of the `gpt-4` models for better performance and more accurate command generation.

## Examples
Simple file conversion and downscaling:
```
llmpeg "convert the file screencapture.webm to screencapture.mp4, but downscale from 1080p to 720p"

Output Command: /usr/bin/ffmpeg -i screencapture.webm -vf scale=1280:720 screencapture.mp4
```

Wildcards to select multiple files and using shell tools:
```
llmpeg "convert all mp4 files in the ~/Desktop/filming/sept_22_2023 folder into mov files with the same name, and store them in a new folder called ~/Desktop/filming/sept_22_2023/movs"

Output Command: mkdir -p ~/Desktop/filming/sept_22_2023/movs && for file in ~/Desktop/filming/sept_22_2023/*.mp4; do ffmpeg -i "$file" -c:v copy -c:a copy "~/Desktop/filming/sept_22_2023/movs/$(basename "$file" .mp4).mov"; done
```

## Contributions

Contributions to llmpeg are welcome! Here's how you can contribute:

- Issues: Submit issues for bugs, enhancements, or features.
- Pull Requests: Submit PRs for bug fixes or enhancements.

## License

`llmpeg` is licensed under the MIT License. See the LICENSE file for more details.
