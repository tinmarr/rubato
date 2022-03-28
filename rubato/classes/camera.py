"""
The Camera is what handles where things are drawn. A camera can zoom, pan
around, and also travel along the z-index. Items only render if their z-index
is less than that of the camera's.
"""
from rubato.utils import Vector, Display, Math


class Camera:
    """
    The camera class.

    Attributes:
        pos (Vector): The current position of the camera.
        zoom (int): The current zoom of the camera.
        z_index (int): The current z_index of the camera.
    """

    def __init__(self, pos: Vector = Vector(), zoom: float = 1, z_index: int = 100):
        """
        Initializes a camera.

        Args:
            pos: The starting position of the camera. Defaults to Vector().
            zoom: The starting zoom of the camera. Defaults to 1.
            z_index: The starting z_index of the camera. Defaults to 100.
        """
        self.pos = pos
        self._zoom = zoom
        self.z_index = z_index

    @property
    def zoom(self) -> float:
        return self._zoom

    @zoom.setter
    def zoom(self, new: float):
        self._zoom = Math.clamp(new, 0.01, Math.INF)

    def transform(self, point: Vector) -> Vector:
        """
        Converts world space coordinates into screen space coordinates
        according to the camera.

        Args:
            point: The point in world space coordinates.

        Returns:
            Vector: The translated coordinates,
                where the first item is the x-coordinate and the second item
                is the y-coordinate. The coordinates are returned with the
                same type that is given.
        """
        center = Vector(*Display.renderer.logical_size) / 2
        return (point - self.pos - center) * self.zoom + center

    def scale(self, dimension):
        return dimension * self.zoom
