"""
Starting Template

Once you have learned how to use classes, you can begin your program with this
template.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.starting_template
"""
import math

import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starwars"
SPRITE_SCALING = 0.25

TURN_SPEED = 1
SPEED_CHANGE = 0.125
MAX_SPEED = 5
GRAV_CONST = 1.
STAR_MASS = 1000
SHIP_MASS = 0.1
BULLET_MASS = 0.01
BULLET_TTL = 300
BULLET_START_SPEED = 3


class RealGravitationPhysicsEngine(object):
    def __init__(self, star_sprite: arcade.Sprite, other_objects: arcade.SpriteList):
        self.star_sprite = star_sprite
        self.objects_list = other_objects

    def update(self):
        for obj in self.objects_list:
            r2 = pow(self.star_sprite.center_x - obj.center_x, 2) + pow(self.star_sprite.center_y - obj.center_y, 2)
            r = math.sqrt(r2)
            f = GRAV_CONST * self.star_sprite.mass * obj.mass / r2
            a_x = (self.star_sprite.center_x - obj.center_x) / r * f
            a_y = (self.star_sprite.center_y - obj.center_y) / r * f
            obj.velocity[0] += a_x
            obj.velocity[1] += a_y


class Player(arcade.Sprite):
    turn_left_action: bool = False
    turn_right_action: bool = False
    speedup_action: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bullets_list = arcade.SpriteList()

    @property
    def speed(self):
        return math.sqrt(self.change_x * self.change_x + self.change_y * self.change_y)

    def draw(self):
        super().draw()
        self.bullets_list.draw()

    def update(self):
        if self.turn_left_action:
            self.turn_left(TURN_SPEED)
        if self.turn_right_action:
            self.turn_right(TURN_SPEED)
        if self.speedup_action:
            self.velocity[0] -= math.sin(self.radians) * SPEED_CHANGE
            self.velocity[1] += math.cos(self.radians) * SPEED_CHANGE

        speed = self.speed
        if speed > MAX_SPEED:
            self.velocity[0] = self.velocity[0] / speed * MAX_SPEED
            self.velocity[1] = self.velocity[1] / speed * MAX_SPEED

        self.position = [self.position[0] + self.velocity[0], self.position[1] + self.velocity[1]]

        if self.position[0] > SCREEN_WIDTH:
            self.position[0] -= SCREEN_WIDTH
        if self.position[0] < 0:
            self.position[0] += SCREEN_WIDTH
        if self.position[1] > SCREEN_HEIGHT:
            self.position[1] -= SCREEN_HEIGHT
        if self.position[1] < 0:
            self.position[1] += SCREEN_HEIGHT

        self.bullets_list.update()

    def fire(self) -> 'Bullet':
        bullet = Bullet(filename=':resources:images/space_shooter/laserBlue01.png', scale=SPRITE_SCALING)
        bullet.position = self.position
        bullet.velocity[0] = -math.sin(self.radians) * BULLET_START_SPEED
        bullet.velocity[1] = math.cos(self.radians) * BULLET_START_SPEED
        bullet.velocity[0] += self.velocity[0]
        bullet.velocity[1] += self.velocity[1]
        bullet.mass = BULLET_MASS
        self.bullets_list.append(bullet)
        return bullet


class Bullet(arcade.Sprite):
    updates_count = 0

    def update(self):
        self.angle = math.degrees(math.atan2(self.change_y, self.change_x))
        self.position = [self.position[0] + self.velocity[0], self.position[1] + self.velocity[1]]

        if self.position[0] > SCREEN_WIDTH:
            self.position[0] -= SCREEN_WIDTH
        if self.position[0] < 0:
            self.position[0] += SCREEN_WIDTH
        if self.position[1] > SCREEN_HEIGHT:
            self.position[1] -= SCREEN_HEIGHT
        if self.position[1] < 0:
            self.position[1] += SCREEN_HEIGHT

        self.updates_count += 1
        if self.updates_count > BULLET_TTL:
            self.remove_from_sprite_lists()


class Explosion(arcade.Sprite):
    """ This class creates an explosion animation """

    def __init__(self, texture_list):
        super().__init__()

        # Start at the first frame
        self.current_texture = 0
        self.textures = texture_list

    def update(self):

        # Update to the next frame of the animation. If we are at the end
        # of our frames, then delete this sprite.
        self.current_texture += 1
        if self.current_texture < len(self.textures):
            self.set_texture(self.current_texture)
        else:
            self.remove_from_sprite_lists()


class MyGame(arcade.Window):
    """
    Main application class.

    NOTE: Go ahead and delete the methods you don't need.
    If you do need a method, delete the 'pass' and replace it
    with your own code. Don't leave 'pass' in this program.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.BLACK_LEATHER_JACKET)

        self.player_list: arcade.SpriteList = None
        self.explosions_list: arcade.SpriteList = None
        self.gravity_list: arcade.SpriteList = None

        self.player_sprite: Player = None
        self.star_sprite: arcade.Sprite = None

        self.explosion_texture_list = arcade.load_spritesheet(file_name=":resources:images/spritesheets/explosion.png",
                                                              sprite_width=256,
                                                              sprite_height=256,
                                                              columns=16,
                                                              count=60)

        self.physics: RealGravitationPhysicsEngine = None

        self.game_over: bool = False
        # If you have sprite lists, you should create them here,
        # and set them to None

    def setup(self):
        # Create your sprites and sprite lists here
        self.player_list = arcade.SpriteList()
        self.explosions_list = arcade.SpriteList()
        self.gravity_list = arcade.SpriteList()

        self.player_sprite = Player(filename=':resources:images/space_shooter/playerShip1_green.png',
                                    scale=SPRITE_SCALING,
                                    center_x=50,
                                    center_y=50)
        self.player_sprite.mass = SHIP_MASS
        self.player_list.append(self.player_sprite)

        self.star_sprite = arcade.Sprite(filename=':resources:images/pinball/bumper.png',
                                         center_x=SCREEN_WIDTH / 2,
                                         center_y=SCREEN_HEIGHT / 2,
                                         scale=1.)
        self.star_sprite.mass = STAR_MASS

        self.gravity_list.append(self.player_sprite)
        self.physics = RealGravitationPhysicsEngine(star_sprite=self.star_sprite, other_objects=self.gravity_list)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()
        self.star_sprite.draw()
        self.player_list.draw()
        self.explosions_list.draw()
        for pl in self.player_list:
            pl.bullets_list.draw()

        # Call draw() on all your sprite lists below

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        self.explosions_list.update()

        if not self.game_over:
            self.physics.update()

            self.player_list.update()

            if arcade.check_for_collision(self.player_sprite, self.star_sprite):
                self.game_over = True
                explosion = Explosion(texture_list=self.explosion_texture_list)
                explosion.center_x = self.player_sprite.center_x
                explosion.center_y = self.player_sprite.center_y
                explosion.update()
                self.explosions_list.append(explosion)

                self.player_sprite.remove_from_sprite_lists()

            bullet_hit_list = arcade.check_for_collision_with_list(self.star_sprite, self.player_sprite.bullets_list)
            for blt in bullet_hit_list:
                explosion = Explosion(texture_list=self.explosion_texture_list)
                explosion.center_x = blt.center_x
                explosion.center_y = blt.center_y
                explosion.update()
                self.explosions_list.append(explosion)
                blt.remove_from_sprite_lists()

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        http://arcade.academy/arcade.key.html
        """
        if key == arcade.key.LEFT:
            self.player_sprite.turn_left_action = True
        if key == arcade.key.RIGHT:
            self.player_sprite.turn_right_action = True
        if key == arcade.key.UP:
            self.player_sprite.speedup_action = True
        if key == arcade.key.DOWN:
            bullet = self.player_sprite.fire()
            # self.gravity_list.append(bullet)


    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        if key == arcade.key.LEFT:
            self.player_sprite.turn_left_action = False
        if key == arcade.key.RIGHT:
            self.player_sprite.turn_right_action = False
        if key == arcade.key.UP:
            self.player_sprite.speedup_action = False

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        pass

    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        pass


def main():
    """ Main method """
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
