"""Global Fixtures needed in multiple tests"""
import pytest
import rubato
import sdl2
import sdl2.ext


@pytest.fixture(scope="module")
def sdl():
    """Initialize SDL2"""
    sdl2.SDL_ClearError()
    ret = sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO | sdl2.SDL_INIT_TIMER)
    assert sdl2.SDL_GetError() == b""
    assert ret == 0
    yield
    sdl2.SDL_Quit()


@pytest.fixture(scope="module")
def rub():
    rubato.init({"hidden": True})
    yield
    sdl2.sdlttf.TTF_Quit()
    sdl2.SDL_Quit()
