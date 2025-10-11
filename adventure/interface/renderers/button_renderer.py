"""Draw the control bar buttons."""

import matplotlib.patches as patches


class ButtonRenderer:
    """Draw buttons and keep their layout in sync with the figure."""

    _STATIC_LABELS = set()

    _SIZE_PRESETS = {
        "small": {
            "w_px": 120,
            "h_px": 32,
            "pad_px": 12,
            "pad_y_px": 16,
            "offset_px": 46,
            "font": 11,
            "title": 12,
        },
        "medium": {
            "w_px": 138,
            "h_px": 36,
            "pad_px": 14,
            "pad_y_px": 22,
            "offset_px": 72,
            "font": 12,
            "title": 13,
        },
        "large": {
            "w_px": 158,
            "h_px": 40,
            "pad_px": 16,
            "pad_y_px": 24,
            "offset_px": 96,
            "font": 13,
            "title": 14,
        },
    }

    def __init__(self, ax_controls, size_hint="medium"):
        self.ax_controls = ax_controls
        self.size_hint = size_hint
        self.buttons = {}
        self._engine = None
        self._resize_cid = None
        self._label_font = 11

    def create_layout(self, engine):
        """Build the current layout inside the controls axes."""
        self._engine = engine
        self.ax_controls.clear()
        self.ax_controls.set_xlim(0, 1)
        self.ax_controls.set_ylim(0, 1)
        self.ax_controls.axis("off")

        if self._resize_cid is None and self.ax_controls.figure:
            self._resize_cid = self.ax_controls.figure.canvas.mpl_connect(
                "resize_event", self._on_resize
            )

        spec = self._SIZE_PRESETS.get(self.size_hint, self._SIZE_PRESETS["medium"])
        self._label_font = spec["font"]

        # Use normalized coordinates so buttons do not overlap after resizing.
        btn_width = 0.235
        btn_height = 0.33
        pad_x = 0.02

        top_buttons = ["pause", "reset", "exit"]
        bottom_buttons = ["speed1", "speed5", "speed10"]
        if engine.show_stats:
            bottom_buttons.append("stats")

        top_total = len(top_buttons) * btn_width + (len(top_buttons) - 1) * pad_x
        bot_total = len(bottom_buttons) * btn_width + (len(bottom_buttons) - 1) * pad_x

        x_top = (1.0 - top_total) / 2.0
        x_bot = (1.0 - bot_total) / 2.0

        y_top = 0.70
        y_bot = 0.18

        self.buttons = {}

        x = x_top
        for name, color in [
            ("pause", "lightgreen"),
            ("reset", "orange"),
            ("exit", "red"),
        ]:
            self._create_button(name, x, y_top, btn_width, btn_height, color)
            x += btn_width + pad_x

        x = x_bot
        for name, color in [
            ("speed1", "lightblue"),
            ("speed5", "orange"),
            ("speed10", "red"),
        ]:
            self._create_button(name, x, y_bot, btn_width, btn_height, color)
            x += btn_width + pad_x

        if engine.show_stats:
            self._create_button("stats", x, y_bot, btn_width, btn_height, "lightgray")

        self.update_button_texts(engine)

    def update_button_texts(self, engine):
        """Refresh button labels for the current engine state."""
        self._engine = engine
        for artist in list(self.ax_controls.texts):
            if artist.get_text() not in self._STATIC_LABELS:
                artist.remove()

        labels = {
            "pause": "PLAY" if engine.paused else "PAUSE",
            "reset": "RESET",
            "exit": "EXIT",
            "speed1": "1x*" if engine.speed_multiplier == 1 else "1x",
            "speed5": "5x*" if engine.speed_multiplier == 5 else "5x",
            "speed10": "10x*" if engine.speed_multiplier == 10 else "10x",
        }
        if "stats" in self.buttons:
            labels["stats"] = "STATS"

        for name, text in labels.items():
            if name in self.buttons:
                self._add_button_text(name, text)

    def get_button_area(self, button_name):
        return self.buttons.get(button_name, {}).get("area")

    def set_final_mode(self, size_hint="large"):
        self.size_hint = size_hint
        if self._engine is not None:
            self.create_layout(self._engine)

    def _create_button(self, name, x, y, w, h, color):
        rect = patches.Rectangle(
            (x, y),
            w,
            h,
            facecolor=color,
            edgecolor="black",
            linewidth=1.6,
            transform=self.ax_controls.transAxes,
            clip_on=False,
        )
        self.ax_controls.add_patch(rect)
        self.buttons[name] = {
            "rect": rect,
            "area": (x, x + w, y, y + h),
            "text_pos": (x + w / 2, y + h / 2),
            "default_color": color,
            "current_text": "",
        }

    def _add_button_text(self, btn_name, text):
        info = self.buttons[btn_name]
        x, y = info["text_pos"]
        fontsize = max(8, self._label_font)
        if btn_name == "exit":
            color = "white"
        elif btn_name == "pause":
            color = "darkgreen"
        elif btn_name == "reset":
            color = "black"
        elif "speed" in btn_name:
            color = "white"
        else:
            color = "black"

        self.ax_controls.text(
            x,
            y,
            text,
            ha="center",
            va="center",
            fontsize=fontsize,
            weight="bold",
            color=color,
            transform=self.ax_controls.transAxes,
        )
        info["current_text"] = text

    def _on_resize(self, _event):
        if self._engine is None:
            return
        self.create_layout(self._engine)
