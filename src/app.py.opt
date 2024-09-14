import logging
import os
import shlex
import signal
import smtplib
import sys
from argparse import ArgumentParser
from pathlib import Path
from socket import gaierror

import pyautogui as pag
from dotenv import load_dotenv
from prettytable import PrettyTable
from pynput import keyboard

import script
from player import Player
from setting import COMMON_CONFIGS, SPECIAL_CONFIGS, Setting

logger = logging.getLogger(__name__)

ASCII_LOGO = """
██████╗ ███████╗██╗  ██╗███████╗
██╔══██╗██╔════╝██║  ██║██╔════╝
██████╔╝█████╗  ███████║███████╗
██╔══██╗██╔══╝  ╚════██║╚════██║
██║  ██║██║          ██║███████║
╚═╝  ╚═╝╚═╝          ╚═╝╚══════╝"""

class App:
    def __init__(self):
        """Merge args into setting node."""
        self.pid = None
        self.player = None
        self.setting = Setting()

        # Combine parsing and validation to avoid redundant checks
        self.parse_and_verify_args()

        if self.args.email and self.setting.SMTP_validation_enabled:
            self._validate_smtp_connection()
        if self.setting.image_verification_enabled:
            self._verify_image_file_integrity()

        # all checks passed, merge settings
        args_attributes = COMMON_ARGS + SPECIAL_ARGS
        self.setting.merge_args(self.args, args_attributes)

        # update number of fishes to catch
        self.setting.fishes_to_catch = max(0, self.setting.keepnet_limit - self.setting.fishes_in_keepnet)

        print(ASCII_LOGO)
        print("https://github.com/dereklee0310/RussianFishing4Script")

    def parse_and_verify_args(self):
        """Combine argument parsing and validation to avoid redundant processing."""
        parser = ArgumentParser(description="Start the script for Russian Fishing 4")

        # Adding common arguments
        for arg_help, common_arg in zip(HELP, COMMON_ARGS):
            parser.add_argument(f"-{arg_help[0]}", f"--{common_arg[0]}", action="store_true", help=arg_help[1])

        # Mutually exclusive groups for release and retrieval strategies
        release_strategy = parser.add_mutually_exclusive_group()
        release_strategy.add_argument("-a", "--all", action="store_true", help="Keep all captured fishes, default")
        release_strategy.add_argument("-m", "--marked", action="store_true", help="Keep only marked fishes")

        retrieval_detection_strategy = parser.add_mutually_exclusive_group()
        retrieval_detection_strategy.add_argument("-d", "--default-spool", action="store_true", help="Use default spool")
        retrieval_detection_strategy.add_argument("-R", "--rainbow-line", action="store_true", help="Use rainbow line")

        # Other arguments
        parser.add_argument("-p", "--pid", metavar="PID", type=int, help="Profile ID")
        parser.add_argument("-n", "--fishes_in_keepnet", metavar="FISH_COUNT", type=int, default=0, help="Fish count")
        parser.add_argument("-t", "--boat-ticket-duration", metavar="DURATION", type=int, choices=[1, 2, 3, 5], help="Boat ticket duration")

        argv = self.setting.default_arguments
        self.args = parser.parse_args(shlex.split(argv) + sys.argv[1:])

        # Verify args
        if not (0 <= self.args.fishes_in_keepnet < self.setting.keepnet_limit):
            logger.error("Invalid number of fishes in keepnet")
            sys.exit()

        if self.args.pid and not self._is_pid_valid(str(self.args.pid)):
            logger.error("Invalid profile id")
            sys.exit()
        self.pid = self.args.pid

    def _validate_smtp_connection(self):
        """Validate email configuration in .env."""
        load_dotenv()
        email, password, smtp_server_name = map(os.getenv, ["EMAIL", "PASSWORD", "SMTP_SERVER"])

        if not smtp_server_name:
            logger.error("SMTP_SERVER not specified")
            sys.exit()

        try:
            with smtplib.SMTP_SSL(smtp_server_name, 465) as smtp_server:
                smtp_server.login(email, password)
        except smtplib.SMTPAuthenticationError:
            logger.error("Email/password incorrect")
            sys.exit()
        except (TimeoutError, gaierror):
            logger.error("Invalid SMTP Server or timeout")
            sys.exit()

    def _verify_image_file_integrity(self):
        """Verify static/{language} file integrity by comparing against static/en."""
        logger.info("Verifying file integrity...")
        image_dir = self.setting.image_dir

        if image_dir == "../static/en/":
            logger.info("Integrity check passed")
            return

        try:
            complete_filenames = set(os.listdir("../static/en/"))
            current_filenames = set(os.listdir(image_dir))
        except FileNotFoundError:
            logger.error("Directory %s not found", image_dir)
            sys.exit()

        missing_filenames = complete_filenames - current_filenames
        if missing_filenames:
            logger.error("Missing images detected")
            print(f"Refer to: https://shorturl.at/2AzUI")
            print(PrettyTable(header=False, align="l", title="Missing images", rows=[(f,) for f in missing_filenames]))
            sys.exit()

        logger.info("Integrity check passed")

    def _is_pid_valid(self, pid):
        """Validate profile ID."""
        return pid.isdigit() and 0 <= int(pid) < len(self.setting.profile_names)

    def on_release(self, key):
        """Handle keyboard key release event."""
        if key == keyboard.KeyCode.from_char(self.setting.quitting_shortcut):
            logger.info("Shutting down...")
            os.kill(os.getpid(), signal.CTRL_C_EVENT)
            sys.exit()


if __name__ == "__main__":
    app = App()
    if app.pid is None:
        app.display_available_profiles()
        app.ask_for_pid()
    app.create_player()
    app.display_args()
    app.display_user_configs()

    if app.setting.confirmation_enabled:
        script.ask_for_confirmation("Do you want to continue with the settings above")
    app.setting.window_controller.activate_game_window()

    if app.setting.quitting_shortcut != "Ctrl-C":
        listener = keyboard.Listener(on_release=app.on_release)
        listener.start()

    try:
        app.player.start_fishing()
    except KeyboardInterrupt:
        pass

    pag.keyUp("shift")
    print(app.player.gen_result("Terminated by user"))
    if app.setting.plotting_enabled:
        app.plot_and_save()
