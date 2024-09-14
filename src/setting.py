"""
Module for SettingHandler class, not used yet.
"""

import configparser
import logging
import pathlib
from argparse import Namespace

from windowcontroller import WindowController

logger = logging.getLogger(__name__)

# -------------------- attribute name - column name - type ------------------- #
GENERAL_CONFIGS = (
    ("language", "Language", str),
    ("window_size", "Window size", str),
    ("default_arguments", "Default arguments", str),
    ("confirmation_enabled", "Enable confirmation", bool),
    ("SMTP_validation_enabled", "Enable SMTP validation", bool),
    ("image_verification_enabled", "Enable image verification", bool),
    ("coffee_limit", "Coffee limit", int),
    ("keepnet_limit", "Keepnet limit", int),
    ("keep_fish_delay", "Keep fish delay", float),
    ("energy_threshold", "Energy threshold", float),
    ("retrieval_detect_confidence", "Retrieve detect confidence", float),
    ("alcohol_drinking_delay", "Alcohol drinking delay", float),
    ("alcohol_drinking_quantity", "Alcohol drinking quantity", int),
    ("lure_broken_action", "Lure broken action", str),
    ("keepnet_full_action", "Keep net full action", str),
    ("alarm_sound_file", "Alarm sound file", str),
    ("unmarked_release_whitelist", "Unmarked release whitelist", str),
)

# ----------------------- config name - attribute name ----------------------- #
SHORTCUTS = (
    ("tea", "tea_shortcut"),
    ("carrot", "carrot_shortcut"),
    ("coffee", "coffee_shortcut"),
    ("shovel_spoon", "shovel_spoon_shortcut"),
    ("alcohol", "alcohol_shortcut"),
    ("bottom_rods", "bottom_rods_shortcuts"),
    ("quit", "quitting_shortcut"),
)

# -------------------- attribute name - column name - type ------------------- #
COMMON_CONFIGS = (
    ("fishing_strategy", "Fishing strategy", str),
    ("cast_power_level", "Cast power level", float),
    ("cast_delay", "Cast delay", float),
    ("post_acceleration_enabled", "Enable post-acceleration", str),
)

SPECIAL_CONFIGS = {
    "spin": (),
    "spin_with_pause": (
        ("retrieval_duration", "Retrieval duration", float),
        ("retrieval_delay", "Retrieval delay", float),
        ("pre_acceleration_enabled", "Enable pre-acceleration", bool),
    ),
    "bottom": (("check_delay", "Check delay", float),
        ("min_deviation", "Min deviation", float),
        ("max_deviation", "Max deviation", float),
    ),
    "marine": (
        ("sink_timeout", "Sink timeout", float),
        ("pirk_duration", "Pirk duration", float),
        ("pirk_delay", "Pirk delay", float),
        ("pirk_timeout", "Pirk timeout", float),
        ("tighten_duration", "Tighten duration", float),
        ("fish_hooked_delay", "Fish hooked delay", float),
    ),
    "float": (
        ("float_confidence", "Float confidence", float),
        ("check_delay", "Check delay", float),
        ("pull_delay", "Pull delay", float),
        ("drifting_timeout", "Drifting timeout", float),
    ),
    "wakey_rig": (
        ("sink_timeout", "Sink timeout", float),
        ("pirk_duration", "Pirk duration", float),
        ("pirk_delay", "Pirk delay", float),
        ("pirk_timeout", "Pirk timeout", float),
        ("tighten_duration", "Tighten duration", float),
        ("fish_hooked_delay", "Fish hooked delay", float),
    ),
}


class Setting:
    """Universal setting node."""

    def __init__(self):
        """Initialize attributes and merge the configs."""
        self.window_controller = WindowController()
        self.config = configparser.ConfigParser()
        self.config.read(pathlib.Path(__file__).resolve().parents[1] / "config.ini")

        self.profile_names = ["edit configuration file"]
        for section in self.config.sections():
            section_obj = self.config[section]
            if "fishing_strategy" in section_obj:  # Replace has_option() with 'in'
                self.profile_names.append(section)

        # args should be handled and merged in caller module first
        self._merge_general_configs()
        self._merge_shortcuts()

        # generate path of the image directory
        parent_dir = pathlib.Path(__file__).resolve().parents[1]
        self.image_dir = parent_dir / "static" / self.language

    def _merge_general_configs(self) -> None:
        """Merge general configs from config.ini."""
        if "game" not in self.config:
            logger.error("Section 'game' not found in config file")
            return

        section = self.config["game"]

        for attribute_name, _, var_type in GENERAL_CONFIGS:
            if attribute_name in section:  # Check if the key exists
                if var_type == bool:
                    attribute_value = section.get(attribute_name) == "True"
                else:
                    attribute_value = var_type(section.get(attribute_name))
                setattr(self, attribute_name, attribute_value)
            else:
                logger.warning(f"Key '{attribute_name}' not found in section 'game'")

        # Handle whitelist correctly
        if hasattr(self, "unmarked_release_whitelist"):
            self.unmarked_release_whitelist = [
                key.strip() for key in self.unmarked_release_whitelist.split(",")
            ]
        else:
            self.unmarked_release_whitelist = []

    def _merge_shortcuts(self) -> None:
        """Merge shortcuts from config.ini."""
        if "shortcut" not in self.config:
            logger.error("Section 'shortcut' not found in config file")
            return

        section = self.config["shortcut"]

        for config, attribute_name in SHORTCUTS:
            setattr(self, attribute_name, section.get(config, fallback=None))  # Provide fallback

        if hasattr(self, "bottom_rods_shortcuts"):
            self.bottom_rods_shortcuts = [
                key.strip() for key in self.bottom_rods_shortcuts.split(",")
            ]
        else:
            self.bottom_rods_shortcuts = []

    def merge_args(self, args: Namespace, args_map: tuple[tuple]) -> None:
        """Merge command line arguments from caller module.

        :param args: parsed command line arguments
        :type args: Namespace
        :param args_attributes: flag name - attribute name - column name mapping
        :type args_attributes: tuple[tuple]
        """
        for arg_name, attribute_name, _ in args_map:
            setattr(self, attribute_name, getattr(args, arg_name))

    def merge_user_configs(self, pid: int):
        """Merge the chosen user profile using pid.

        After a profile id and args is given, this method should be invoked by app.py
        to merge the profile section in config.ini into this object.

        :param pid: user profile id
        :type pid: int
        """
        section = self.config[self.profile_names[pid]]

        for attribute_name, _, var_type in COMMON_CONFIGS:
            # Provide a fallback if the key is missing from the section
            if var_type == bool:
                attribute_value = section.get(attribute_name, fallback="False") == "True"
            else:
                attribute_value = var_type(section.get(attribute_name, fallback=None))
            setattr(self, attribute_name, attribute_value)

        special_configs = SPECIAL_CONFIGS.get(self.fishing_strategy, [])
        for attribute_name, _, var_type in special_configs:
            if var_type == bool:
                attribute_value = section.get(attribute_name, fallback="False") == "True"
            else:
                attribute_value = var_type(section.get(attribute_name, fallback=None))
            setattr(self, attribute_name, attribute_value)


