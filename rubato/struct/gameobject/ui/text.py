"""A text component."""
from __future__ import annotations
from typing import Literal
import sdl2, sdl2.ext

from .. import Component
from .... import Display, Vector, VectorLike, Color, Font, Draw, Camera


class Text(Component):
    """
    A text component subclass. Add this to game objects or UI elements to give them text.

    Args:
        text: The text to display. Defaults to "".
        font: The font to use. Defaults to Font().
        justify: The justification of the text. Defaults to "left".
        anchor: The anchor of the text. The zero vector means it is centered. x component is whether to shift left,
            none, or right (-1, 0, 1). y component is whether to shift top, none, or bottom (-1, 0, 1).
            Defaults to Vector(0, 0).
        width: The width of the text. Defaults to 0.
        offset: The offset of the text from the game object. Defaults to Vector(0, 0).
        rot_offset: The rotation offset of the text from the game object. Defaults to 0.
        z_index: The z index of the text. Defaults to 0.
    """

    def __init__(
        self,
        text: str = "",
        font: Font = Font(),
        justify: Literal["left", "center", "right"] = "left",
        anchor: VectorLike = (0, 0),
        width: int = 0,
        offset: VectorLike = (0, 0),
        rot_offset: float = 0,
        z_index: int = 0
    ):
        super().__init__(offset=offset, rot_offset=rot_offset, z_index=z_index)
        self._text: str = text
        self.font_object: Font = font
        self.anchor: Vector = Vector.create(anchor)
        """
        The anchor vector of the text.

        This controls the position of the text relative to the game object. Is a vector where the x value
        controls the x anchor and the y value controls the y anchor. The values for each can be either -1, 0 or 1. This
        offset the text around the game object center.

        Example:
            An anchor of ``Vector(0, 0)`` will center the text on the game object. An anchor of ``Vector(1, 1)`` will
            move the text so that it's top left corner is at the game object's center.

        Warning:
            Previously was called align.
        """
        self._justify: str = justify
        self._width: int = width

        if not self.font_object:
            self.font_object = Font()

        self.generate_surface()

    @property
    def text(self) -> str:
        """The text of the Text."""
        return self._text

    @text.setter
    def text(self, new: str):
        self._text = new
        self.generate_surface()

    @property
    def justify(self) -> str:
        """
        The justification of the text.

        Can be one of: ``"left"``, ``"center"``, ``"right"``.
        """
        return self._justify

    @justify.setter
    def justify(self, new: str):
        if new in ["left", "center", "right"]:
            self._justify = new
            self.generate_surface()
        else:
            raise ValueError(f"Justification {new} is not left, center or right.")

    @property
    def width(self) -> int:
        """The maximum width of the text. Will automatically wrap the text. Use -1 to disable wrapping."""
        return self._width

    @width.setter
    def width(self, new: int):
        self._width = new
        self.generate_surface()

    @property
    def font_size(self) -> int:
        """
        The font size.

        Warning:
            Don't set this too high or font smoothing may misbehave on some systems.
        """
        return self.font_object.size

    @font_size.setter
    def font_size(self, size: int):
        self.font_object.size = size
        self.generate_surface()

    @property
    def font_color(self) -> Color:
        """The font color."""
        return self.font_object.color

    @font_color.setter
    def font_color(self, color: Color):
        self.font_object.color = color
        self.generate_surface()

    def add_style(self, style: str):
        """Add a style to the font (bold, italic, underline, strikethrough, normal)."""
        self.font_object.add_style(style)
        self.generate_surface()

    def remove_style(self, style: str):
        """Remove a style from a font."""
        self.font_object.remove_style(style)
        self.generate_surface()

    def generate_surface(self):
        """(Re)generates the surface of the text."""
        self._tx = sdl2.ext.Texture(
            Display.renderer, self.font_object.generate_surface(
                self._text,
                self._justify,
                self._width,
            )
        )

    def draw(self, camera: Camera):
        if self.hidden:
            return

        Draw.queue_texture(
            self._tx,
            camera.transform(self.gameobj.pos + (self.anchor - 1) * Vector(*self._tx.size) / 2) + self.offset,
            self.true_z(),
            angle=int((self.gameobj.rotation if self.gameobj else 0) + self.rot_offset),
        )

    def delete(self):
        """Deletes the text component."""
        self._tx.destroy()
        self.font_object._font.close()  # pylint: disable=protected-access
        self._tx = None
        self.font_object = None

    def clone(self) -> Text:
        """Clones the text component."""
        return Text(
            text=self._text,
            font=self.font_object.clone(),
            anchor=self.anchor.clone(),
            justify=self._justify,
            width=self._width,
            offset=self.offset.clone(),
            rot_offset=self.rot_offset,
            z_index=self.z_index,
        )
