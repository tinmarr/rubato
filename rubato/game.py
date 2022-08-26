"""
An abstraction surrounding the main game loop in rubato.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
import sdl2, sdl2.sdlttf
import sys

from . import Time, Display, Debug, Radio, Events, Font, PrintError, Camera, IdError, Draw, InitError, Input

if TYPE_CHECKING:
    from . import Scene


# THIS IS A STATIC CLASS
class Game:
    """
    A static class controlling rubato game flow.
    """
    RUNNING = 1
    STOPPED = 2
    PAUSED = 3

    debug: bool = False
    """Whether to use debug-mode."""
    show_fps: bool = False
    """Whether to show fps."""
    debug_font: Font
    """What font to draw debug text in."""

    state: int = STOPPED
    """
    The state of the game. The game states are::

        Game.RUNNING
        Game.STOPPED
        Game.PAUSED
    """

    _initialized = False

    _scenes: dict[str, Scene] = {}
    _scene_id: int = 0
    _current: str = ""

    def __init__(self) -> None:
        raise InitError(self)

    @classmethod
    @property
    def current(cls) -> Scene | None:  # test: skip
        """
        The current scene. (getonly)

        Returns:
            The current scene.
        """
        return cls._scenes.get(cls._current)

    @classmethod
    def set_scene(cls, scene_id: str):  # test: skip
        """
        Changes the current scene. Takes effect on the next frame.

        Args:
            scene_id: The id of the new scene.
        """
        cls._current = scene_id

    @classmethod
    def _add(cls, scene: Scene, name: str | None) -> str:  # test: skip
        """
        Add a scene to the game. Also set the current scene if this is the first added scene.

        Args:
            scene: The scene to add.
            name: The name of the scene. If None, a unique name is generated.

        Raises:
            IdError: The given scene id is already used.
        """
        if name is None:
            name = "scene" + str(cls._scene_id)  # pylint: disable=protected-access

        if name in cls._scenes:
            raise IdError(f"A scene with name '{name}' has already been added.")

        if not cls._scenes:
            cls.set_scene(name)

        cls._scenes[name] = scene
        cls._scene_id += 1

        return name

    @classmethod
    @property
    def camera(cls) -> Camera | None:  # test: skip
        """
        A shortcut getter allowing easy access to the current camera.
        This is a get-only property.

        Note:
            Returns a pointer to the current camera object.
            This is so you can access/change the current camera properties faster, but you'd still need to
            use :func:`Game.current.camera <rubato.struct.scene.Scene.camera>` to access the camera directly.

        Returns:
            Camera: The current scene's camera
        """
        return cls.current.camera if cls.current else None  # pylint: disable=using-constant-test

    @classmethod
    def quit(cls):
        """Quit the game and close the python process."""
        Radio.broadcast(Events.EXIT)
        cls.state = cls.STOPPED
        sys.stdout.flush()
        sdl2.sdlttf.TTF_Quit()
        sdl2.SDL_Quit()
        sys.exit(0)

    @classmethod
    def start(cls) -> None:
        """
        Starts the main game loop. Called automatically by :meth:`rubato.begin`.
        """
        cls.state = cls.RUNNING
        try:
            cls.loop()
        except KeyboardInterrupt:
            cls.quit()
        except PrintError as e:
            sys.stdout.flush()
            raise e
        except (Exception,) as e:
            sys.stdout.flush()
            raise type(e)(
                str(e) + "\nRubato Error-ed. Was it our fault? Issue tracker: "
                "https://github.com/rubatopy/rubato/issues"
            ).with_traceback(sys.exc_info()[2])
        finally:
            sys.stdout.flush()

    @classmethod
    def loop(cls):
        """
        Rubato's main game loop. Called automatically by :meth:`rubato.Game.start`.
        """
        while True:
            # start timing the update loop
            Time._frame_start = Time.now()  # pylint: disable= protected-access

            if cls.state == cls.STOPPED:
                sdl2.SDL_PushEvent(sdl2.SDL_Event(sdl2.SDL_QUIT))

            # Pump SDL events
            sdl2.SDL_PumpEvents()

            # Event handling
            if Radio.handle():
                cls.quit()

            # Register controllers
            Input.update_controllers()

            # process delayed calls
            Time.process_calls()

            cls.update()

            curr = cls.current
            if curr:  # pylint: disable=using-constant-test
                if cls.state == Game.PAUSED:
                    # process user set pause update
                    curr._paused_update()  # pylint: disable=protected-access
                else:
                    # normal update
                    curr._update()  # pylint: disable=protected-access

                    # fixed update
                    Time.physics_counter += Time.delta_time

                    while Time.physics_counter >= Time.fixed_delta:
                        curr._fixed_update()  # pylint: disable=protected-access
                        Time.physics_counter -= Time.fixed_delta

                curr._draw()  # pylint: disable=protected-access
            else:
                Draw.clear()

            cls.draw()

            Draw.dump()

            if cls.show_fps:
                Debug.draw_fps(cls.debug_font)

            # update renderers
            Display.renderer.present()

            # use delay to cap the fps if need be
            if Time.capped:
                delay = Time.normal_delta - (1000 * Time.delta_time)
                if delay > 0:
                    sdl2.SDL_Delay(int(delay))

            # don't allow updates to occur more than once in a millisecond
            # this will likely never occur but is a failsafe
            while Time.now() == Time.frame_start:  # pylint: disable= comparison-with-callable
                sdl2.SDL_Delay(1)

            # clock the time the update call took
            Time.delta_time = (Time.now() - Time.frame_start) / 1000  # pylint: disable=comparison-with-callable

    @staticmethod
    def update():  # test: skip
        """An overrideable method for updating the game. Called once per frame, before the current scene updates."""
        pass

    @staticmethod
    def draw():  # test: skip
        """An overrideable method for drawing the game. Called once per frame, after the current scene draws."""
        pass
