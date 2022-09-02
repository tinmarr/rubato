"""
A classic
"""
import random
from rubato import *

size = 1080
radius = size // 40
level = 0

init(name="asteroids", res=(size, size))

main = Scene()

# background
stars = Surface(size, size)
stars.fill(Color.black)
for _ in range(200):
    pos = random.randint(0, size), random.randint(0, size)
    stars.draw_point(pos, Color.white)


# component to remove gameobject after number of seconds
class Timer(Component):

    def __init__(self, secs: float):
        super().__init__()
        self.time = Time.sec_to_milli(secs)
        self.started = False

    def update(self):
        if not self.started:
            self.time += Time.now()
            self.started = True

        if Time.now() >= self.time:
            main.remove(self.gameobj)


# explosion particle
expl = Surface(radius // 2, radius // 2)
expl.draw_rect((0, 0), expl.get_size_raw(), Color.debug, 3)


def make_part(angle: float):
    return Particle(
        expl.clone(),
        pos=Particle.circle_shape(radius * 0.75)(angle),
        velocity=Particle.circle_direction()(angle) * random.randint(50, 100),
        rotation=random.randint(0, 360),
    )


# explosion system
expl_sys = wrap([ParticleSystem(new_particle=make_part, mode=ParticleSystemMode.BURST), Timer(5)])


# component to move things that are out of bounds
class BoundsChecker(Component):

    def update(self):
        if self.gameobj.pos.x < -radius:
            self.gameobj.pos.x = Display.right + radius
        elif self.gameobj.pos.x > Display.right + radius:
            self.gameobj.pos.x = -radius
        if self.gameobj.pos.y < -radius:
            self.gameobj.pos.y = Display.bottom + radius
        elif self.gameobj.pos.y > Display.bottom + radius:
            self.gameobj.pos.y = -radius


# asteroid generator
def make_asteroid():
    sides = random.randint(5, 8)

    t = random.randint(0, size)
    topbottom = random.randint(0, 1)
    side = random.randint(0, 1)
    if topbottom:
        pos = t, side * size + (radius if side else -radius)
    else:
        pos = side * size + (radius if side else -radius), t

    direction = (-Display.center.dir_to(pos)).rotate(random.randint(-45, 45))

    main.add(
        wrap(
            [
                Polygon(
                    [
                        Vector.from_radial(random.randint(int(radius * .7), int(radius * 0.95)), i * 360 / sides)
                        for i in range(sides)
                    ],
                    debug=True,
                ),
                RigidBody(velocity=direction * 100, ang_vel=random.randint(-30, 30)),
                BoundsChecker(),
            ],
            "asteroid",
            pos,
            random.randint(0, 360),
        )
    )


Time.schedule(ScheduledTask(1000, make_asteroid, 1000))


class PlayerController(Component):

    def setup(self):
        self.speed = 250
        self.steer = 25

        self.velocity = Vector()

    def update(self):
        if Input.controller_button(Input.controllers - 1, 0) or Input.key_pressed("j"):
            shoot()

    def fixed_update(self):
        dx = Input.controller_axis(Input.controllers - 1, 0) or \
            (-1 if Input.key_pressed("a") else (1 if Input.key_pressed("d") else 0))
        dy = Input.controller_axis(Input.controllers - 1, 1) or \
            (-1 if Input.key_pressed("w") else (1 if Input.key_pressed("s") else 0))
        target = Vector(dx, dy)

        d_vel = target * self.speed
        steering = Vector.clamp_magnitude(d_vel - self.velocity, self.steer)

        self.velocity = Vector.clamp_magnitude(self.velocity + steering, self.speed)

        self.gameobj.pos += self.velocity * Time.fixed_delta

        if target != (0, 0):
            self.gameobj.rotation = self.velocity.angle


full = [
    Vector.from_radial(radius, 0),
    Vector.from_radial(radius, 125),
    Vector.from_radial(radius // 4, 180),
    Vector.from_radial(radius, -125),
]
right = [full[0], full[1], full[2]]
left = [full[0], full[2], full[3]]
player_spr = Raster(radius * 2, radius * 2)
player_spr.draw_poly([v + radius for v in full], Color.debug, 2, aa=True)

main.add(
    wrap(
        [
            PlayerController(),
            Polygon(right, trigger=True),
            Polygon(left, trigger=True),
            player_spr,
            BoundsChecker(),
        ],
        "player",
        Display.center,
    )
)

last_shoot = 0
interval = 200


def bullet_collide(man: Manifold):
    if man.shape_b.gameobj.name == "asteroid":
        local_expl = expl_sys.clone()
        local_expl.pos = man.shape_b.gameobj.pos.clone()
        local_expl.rotation = random.randint(0, 360)
        local_expl_sys = local_expl.get(ParticleSystem)
        if isinstance(man.shape_b, Polygon):
            local_expl_sys.spread = 360 / len(man.shape_b.verts)
        local_expl_sys.start()
        main.remove(man.shape_b.gameobj)
        main.remove(man.shape_a.gameobj)
        main.add(local_expl)


def shoot():
    global last_shoot
    if Time.now() - last_shoot < interval:
        return
    last_shoot = Time.now()
    main.add(
        wrap(
            [
                Circle(radius // 5, Color.debug, trigger=True, on_collide=bullet_collide),
                RigidBody(
                    velocity=player_spr.gameobj.get(PlayerController).velocity + Vector.from_radial(
                        500,
                        player_spr.gameobj.rotation,
                    )
                ),
                BoundsChecker(),
                Timer(0.75),
            ],
            "bullet",
            player_spr.gameobj.pos + full[0].rotate(player_spr.gameobj.rotation),
            player_spr.gameobj.rotation,
        )
    )


def new_draw():
    Draw.surface(stars, Display.center)


Game.draw = new_draw

begin()