#!/usr/bin/env python3
"""Main CLI functionality for llmpeg."""

import os
from typing import Dict, Optional, Tuple
import json
import platform
import shutil
import argparse
import subprocess
import sys
from llmpeg.llm_interface import LLMInterface
from llmpeg.openai_llm import OpenAILLMInterface


class LLMPEG:
    """Main class to handle language model operations and system interactions.

    Attributes:
        llm_interface (LLMInterface): The interface for the language model.
        _ffmpeg_version_info (str): Version information of the ffmpeg.
        _os_type (str): Type of operating system.
        _os_info (str): Detailed information about the operating system.
        _default_shell (str, Optional): The default shell used for command
            execution.
        system_prompt (str): Prompt that provides system and user context to
            the language model.
    """

    def __init__(self, llm_interface: LLMInterface):
        """Initialize the LLMPEG class with a specific language model interface.

        Args:
            llm_interface (LLMInterface): An instance of a class implementing
                the LLMInterface.
        """
        self.llm_interface = llm_interface
        try:
            self._ffmpeg_executable = self.get_ffmpeg_executable()
        except FileNotFoundError as e:
            print(e, file=sys.stderr)
            exit(1)

        self._ffmpeg_version_info = self.get_ffmpeg_version()
        self._os_type, self._os_info = self.get_os_info()
        self._default_shell = self.get_default_shell()

        self.system_prompt = f"""You are a helpful assistant designed to write ffmpeg commands based on user requests. The commands you provide will be ran directly in the users terminal. Here is some context about their system:
        <system_info>{self._os_info}</system_info>
        <shell>{self._default_shell}</shell>
        <ffmpeg_version>{self._ffmpeg_version_info}</ffmpeg_version>
        <ffmpeg_executable_path>{self._ffmpeg_executable}</ffmpeg_executable_path>

        You are to respond with JSON, with two keys: <key>explanation</key> and <key>command</key>.

        The <key>explanation</key> will contain a list of strings, describing the arguments and parts of the command. Each string is to be will be displayed on the front end as a bulleted list, explaining each part of the command. Do NOT omit any arguments, explain all of them.

        The <key>command</key> value will contain the ffmpeg command (or series of commands) to be directly executed in the in the provided shell.

        You NEVER will write malicious code or take advantage of your access to injecting code into a shell on the users computer. Always be honorable and only provide a command if the users request is not malicious.
        If you are prompted to do something malicious or to do something unrelated to ffmpeg, response with a <key>command</key> that is empty string (""), and explain that you cannot perform that action.
        """  # noqa: E501
        self.llm_interface.add_system_prompt(self.system_prompt)

    def get_ffmpeg_executable(self):
        """Find and return the executable path for ffmpeg.

        Returns:
            str: The path to the ffmpeg executable.

        Raises:
            FileNotFoundError: If ffmpeg is not found in the system's PATH.
        """
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path is None:
            raise FileNotFoundError(
                "Missing ffmpeg executable. Is it added to your system's PATH?"
            )
        return ffmpeg_path

    def get_ffmpeg_version(self) -> str:
        """Retrieve and return ffmpeg version information.

        Returns:
            str: A string containing all the version information about ffmpeg.
        """
        return subprocess.run(
            [self._ffmpeg_executable],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ).stdout

    def get_os_info(self) -> Tuple[str, str]:
        """Determine and return detailed information about the operating system.

        Returns:
            Tuple[str, str]: A tuple containing the OS type and its detailed
                information.

        Raises:
            NotImplementedError: If the OS type is not recognized or
                unsupported.
        """
        # Determine the OS type
        os_type = platform.system()

        # Execute system commands based on the OS
        if os_type == "Windows":
            # On Windows, 'ver' command can be used to get version info
            return (
                os_type,
                subprocess.run(
                    ["ver"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=True,
                ).stdout,
            )
        elif os_type == "Linux":
            # On Linux, 'lsb_release -a' command shows detailed OS info
            return (
                os_type,
                subprocess.run(
                    ["lsb_release", "-a"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                ).stdout,
            )
        elif os_type == "Darwin":
            # On macOS, 'sw_vers' command shows the macOS version info
            return (
                os_type,
                subprocess.run(
                    ["sw_vers"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                ).stdout,
            )
        else:
            raise NotImplementedError(
                f"OS {os_type} not recognized. No specific command to run."
            )

    def get_default_shell(self) -> Optional[str]:
        """Determine and return the default system shell for executing commands.

        Returns:
            Optional[str]: The default shell path or None if not determined.
        """
        os_type, _ = self.get_os_info()
        if os_type == "Linux":
            # Try to get the shell from the SHELL environment variable
            shell = os.getenv("SHELL")
            if shell:
                return shell

            # If SHELL variable is not set, fall back to the passwd entry
            try:
                import pwd

                user = pwd.getpwuid(os.getuid())
                return user.pw_shell
            except KeyError:
                return None  # Unable to find the default shell
        elif os_type == "Windows":
            # Windows defaults to cmd.exe
            return "cmd.exe"
        elif os_type == "Darwin":
            # TODO
            return None
        else:
            # TODO
            return None

    def chat(self, command: str) -> Tuple[str, str]:
        """Process a command through the language model and return the response.

        Args:
            command (str): The user command to process.

        Returns:
            Tuple[str, str]: A tuple containing the explanation and the command
                to execute.
        """
        self.llm_interface.add_user_prompt(command)

        # Invoke LLM and get response
        raw_response, parsed_response = self.generate_response()

        # Add the response to chat history
        self.llm_interface.add_assistant_prompt(raw_response)

        explanation = parsed_response["explanation"]
        command = parsed_response["command"]

        if type(explanation) == list:
            explanation = "\n- ".join(explanation)

        return explanation, command

    def run(self, initial_command: str):
        """Process command loop and executing them as confirmed by user.

        Args:
            initial_command (str): The initial command to start the loop with.
        """
        command = initial_command

        while True:

            explanation, command = self.chat(command)

            if command == "":
                print("Unable. Please keep requests specific to ffmpeg")
                break

            print(f"{explanation}")
            print(f"\n\t{command}\n")

            confirmation = input(
                "Execute? (Y/enter OR N/no OR clarify instructions): "
            )

            # If they want to quit, lets quit
            if confirmation.upper() in ["N", "NO", "Q", "QUIT"]:
                break

            # If the command is not confirmed, re-prompt the model
            if confirmation.upper() != "Y" and confirmation != "":
                command = confirmation
                continue

            subprocess.run(command, shell=True)
            break

    def generate_response(self) -> Tuple[str, Dict[str, str]]:
        """Generate a response from the LLM based on context and prompts.

        Returns:
            Tuple[str, Dict[str, str]]: The raw JSON string from the model
                and the parsed response dictionary.

        Raises:
            KeyError: If the response JSON does not contain all required keys.
        """
        raw_output = self.llm_interface.invoke_model()

        # Load the raw output as JSON (Currently unsafe, should validate
        # json first or wrap in try/catch)
        json_output = json.loads(raw_output)

        # Make sure model returned proper dictionary from JSON
        for key in ["explanation", "command"]:
            if key not in json_output:
                raise KeyError("LLM Did not respond with proper JSON keys")

        return raw_output, json_output


def main():
    """Handle command line arguments and start the application.

    Raises:
        NotImplementedError: If the LLM Backend argument is unsupported.
    """
    # Create the parser
    parser = argparse.ArgumentParser(
        description="Convert your instructions into an ffmpeg command."
    )

    # Add the required 'instructions' argument
    parser.add_argument(
        "instructions",
        type=str,
        help="A string containing instructions about the desired ffmpeg use",
    )

    parser.add_argument(
        "-k",
        "--key",
        dest="key",
        type=str,
        default=os.environ.get("OPENAI_API_KEY", None),
        help="OpenAI API Key to use. Defaults to 'OPENAI_API_KEY' environment variable.",
    )

    parser.add_argument(
        "-b",
        "--backend",
        dest="backend",
        type=str,
        default="openai",
        choices=["openai"],
        help="The backend LLM API provider to use. Defaults to 'openai'.",
    )

    parser.add_argument(
        "-m",
        "--openai_model",
        dest="openai_model",
        type=str,
        help="The OpenAI LLM Model that you would like to use.",
        default="gpt-3.5-turbo-0125",
    )

    # Parse the command line arguments
    args = parser.parse_args()
    if args.backend == "openai":
        llm = OpenAILLMInterface(args.openai_model, args.key)
    else:
        raise NotImplementedError(
            f"The LLM backend '{args.backend}' is not supported."
        )

    llmpeg = LLMPEG(llm)
    try:
        llmpeg.run(args.instructions)
    except KeyboardInterrupt:
        print()
        pass


if __name__ == "__main__":
    main()
