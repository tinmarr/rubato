from rubato import check_types
from rubato.utils import Vector


class Camera:
    """
    Cameras handle general visual transformations on all sprites drawn in the current scene.

    :param pos: The coordinates of the Camera
    :param zoom: The initial zoom of the Camera as a number
    """
    def __init__(self, pos: Vector = Vector(), zoom: int = 1, z_index: int = 0):
        check_types(Camera.__init__, locals())
        self.pos = pos
        self.zoom = zoom
        self.z_index = 0

    def transform(self, point: Vector) -> Vector:
        """
        Translates a given set of coordinates by the camera's.

        :param point: The point to be transformed
        :return: A new offset point in the form of a 2D tuple
        """
        check_types(Camera.transform, locals())
        return point.offset(self.pos).to_tuple()
