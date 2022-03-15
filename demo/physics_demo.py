"""Physics Demo... basically a ball pit"""
import os
import sys

sys.path.insert(0, os.path.abspath("../"))
# pylint: disable=wrong-import-position
from random import randint
import rubato as rb
from rubato import Game, Vector, Color

num_balls = 50
rb.init({
    "name": "Physics Demo",
    "fps_cap": 60,
    "window_size": Vector(600, 600),
    "resolution": Vector(600, 600),
})

main_scene = rb.Scene()
Game.scenes.add(main_scene, "main")
rb.Game.scenes.set("main")

top = rb.Sprite({
    "pos": Vector(Game.resolution.x / 2, -Game.resolution.x / 20)
}).add(
    rb.Rectangle({
        "width":Game.resolution.x,
        "height":Game.resolution.y/6,
        "debug":
        False,
        "color":
        Color.maroon,
    })
)

bottom = rb.Sprite({
    "pos":
    Vector(Game.resolution.x / 2, Game.resolution.y + Game.resolution.x / 20)
}).add(
    rb.Rectangle({
        "width":Game.resolution.x,
        "height":Game.resolution.y/6,
        "debug":
        False,
        "color":
        Color.maroon,
    })
)

left = rb.Sprite({
    "pos": Vector(-Game.resolution.x / 20, Game.resolution.y / 2)
}).add(
    rb.Rectangle({
        "width":Game.resolution.x/6,
        "height":Game.resolution.y,
        "debug":
        False,
        "color":
        Color.maroon,
    })
)

right = rb.Sprite({
    "pos":
    Vector(Game.resolution.x + Game.resolution.x / 20, Game.resolution.y / 2)
}).add(
    rb.Rectangle({
        "width":Game.resolution.x/6,
        "height":Game.resolution.y,
        "debug":
        False,
        "color":
        Color.maroon,
    })
)

balls = []
for i in range(num_balls):
    ball = rb.Sprite({
        "pos":
        Vector(randint(100, Game.resolution.y - 100),
               randint(100, Game.resolution.y - 100))
    }).add(
        rb.Circle({
            "radius": Game.resolution.x / 30,
            "color": Color.random
        })
    ).add(
        rb.RigidBody({
            "bounciness": 0.75,
            "gravity": Vector(0, Game.resolution.x / 30)
        })
    )
    balls.append(ball)

player = rb.Sprite({
    "pos": rb.Vector(50, 50),
})

player_rb = rb.RigidBody({
    "mass": 10,
    "bounciness": 0.1,
    "max_speed": Vector(50, 1000),
    "gravity": Vector()
})
player.add(player_rb)

player_hitbox = rb.Polygon({
    "verts":
    rb.Polygon.generate_polygon(5, Game.resolution.x / 20),
    "color":
    Color.blue,
    "rotation":
    180,
})
player.add(player_hitbox)


def custom_update():
    if rb.Input.is_pressed("w"):
        player_rb.velocity.y -= Game.resolution.x * (1 / 12)
    elif rb.Input.is_pressed("s"):
        player_rb.velocity.y += Game.resolution.x * (1 / 12)
    if rb.Input.is_pressed("a"):
        player_rb.velocity.x -= Game.resolution.x * (1 / 12)
    elif rb.Input.is_pressed("d"):
        player_rb.velocity.x += Game.resolution.x * (1 / 12)

    #print(f"fps: {rb.Time.clock.get_fps()}")


main_scene.add(balls)
main_scene.add([top, bottom, left, right, player])
main_scene.update = custom_update

rb.begin()
