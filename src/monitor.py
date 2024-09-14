import logging
import sys
import pyautogui as pag
from pyscreeze import Box
from setting import Setting

logger = logging.getLogger(__name__)


class Monitor:
    """A class that holds different aliases of locateOnScreen(image)."""

    def __init__(self, setting: Setting):
        """Initialize setting.

        :param setting: general setting node
        :type setting: Setting
        """
        self.setting = setting
        self.image_dir = self.setting.image_dir

    def _locate_image(self, image: str, confidence: float, multiple=False):
        """Locate image on screen using pyautogui, handling single or multiple searches.

        :param image: base name of the image
        :param confidence: matching confidence for locateOnScreen
        :param multiple: whether to locate all occurrences or just the first
        :return: image box(es), None if not found
        """
        file_path = f"{self.image_dir}/{image}.png"
        if multiple:
            return pag.locateAllOnScreen(file_path, confidence=confidence)
        return pag.locateOnScreen(file_path, confidence=confidence)

    def is_fish_species_matched(self, species: str) -> Box | None:
        return self._locate_image(species, 0.9)

    def is_fish_marked(self):
        return self._locate_image("mark", 0.7)

    def is_fish_yellow_marked(self):
        return self._locate_image("trophy", 0.7)

    def is_fish_hooked(self):
        return self._locate_image("get", 0.9)

    def is_fish_captured(self):
        return self._locate_image("keep", 0.9)

    def _is_rainbow_line_0or5m(self):
        return self._locate_image("5m", self.setting.retrieval_detect_confidence) or self._locate_image("0m", self.setting.retrieval_detect_confidence)

    def _is_spool_full(self):
        return self._locate_image("wheel", self.setting.retrieval_detect_confidence)

    def is_tackle_ready(self):
        return self._locate_image("ready", 0.6)

    def is_tackle_broken(self):
        return self._locate_image("broke", 0.6)

    def is_lure_broken(self):
        return self._locate_image("lure_is_broken", 0.7)

    def is_moving_in_bottom_layer(self):
        return self._locate_image("movement", 0.7)

    def is_disconnected(self):
        return self._locate_image("disconnected", 0.9)

    def is_line_at_end(self):
        return self._locate_image("spooling", 0.98)

    def is_ticket_expired(self):
        return self._locate_image("ticket", 0.9)

    def is_operation_failed(self):
        return self._locate_image("warning", 0.8)

    def is_operation_success(self):
        return self._locate_image("ok", 0.8)

    def get_quit_position(self):
        return self._locate_image("quit", 0.8)

    def get_yes_position(self):
        return self._locate_image("yes", 0.8)

    def get_make_position(self):
        return self._locate_image("make", 0.9)

    def get_exit_icon_position(self):
        return self._locate_image("exit", 0.8)

    def get_confirm_exit_icon_position(self):
        return self._locate_image("confirm_exit", 0.8)

    def is_harvest_success(self):
        return self._locate_image("harvest_confirm", 0.8)

    def get_food_position(self, food: str) -> Box | None:
        return self._locate_image(food, 0.8)

    def get_ticket_position(self, duration: int) -> Box | None:
        return self._locate_image(f"ticket_{duration}", 0.95)

    def get_scrollbar_position(self):
        return self._locate_image("scrollbar", 0.97)

    def get_100wear_position(self):
        return self._locate_image("100wear", 0.98)

    def get_favorite_item_positions(self):
        return self._locate_image("favorite", 0.95, multiple=True)

    def is_energy_high(self) -> bool:
        pos = self._get_energy_icon_position()
        if not pos:
            return False
        x, y = int(pos.x), int(pos.y)
        last_point = int(19 + 152 * self.setting.energy_threshold) - 1
        return pag.pixel(x + 19, y) == pag.pixel(x + last_point, y)

    def is_hunger_low(self) -> bool:
        pos = self._get_food_icon_position()
        if not pos:
            return False
        x, y = int(pos.x), int(pos.y)
        last_point = int(18 + 152 * 0.5) - 1
        return pag.pixel(x + 18, y) != pag.pixel(x + last_point, y)

    def is_comfort_low(self) -> bool:
        pos = self._get_comfort_icon_position()
        if not pos:
            return False
        x, y = int(pos.x), int(pos.y)
        last_point = int(18 + 152 * 0.51) - 1
        return pag.pixel(x + 18, y) != pag.pixel(x + last_point, y)

    def _get_energy_icon_position(self):
        return self._get_icon_position("energy")

    def _get_food_icon_position(self):
        return self._get_icon_position("food")

    def _get_comfort_icon_position(self):
        return self._get_icon_position("comfort")

    def _get_icon_position(self, icon_name):
        """Get the icon position and return its center if found."""
        box = self._locate_image(icon_name, 0.8)
        return pag.center(box) if box else None

    def get_float_camera_region(self) -> tuple[int, int, int, int]:
        """Return the region for float camera based on the window size."""
        x, y = self.setting.window_controller.get_game_rect()[:2]
        size_map = {
            "2560x1440": (1198, 1192),
            "1920x1080": (878, 832),
            "1600x900": (718, 652),
        }
        offsets = size_map.get(self.setting.window_size)
        if not offsets:
            logger.error("Invalid window size")
            sys.exit()
        x_offset, y_offset = offsets
        return (x + x_offset, y + y_offset, 164, 164)
