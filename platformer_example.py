import pygame
import the_brain as ch4d

# Global constants

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

LOWER_BORDER = 50
LOWER_BORDER_LIMIT = SCREEN_HEIGHT - LOWER_BORDER


class Player(pygame.sprite.Sprite):
    """
    This class represents the bar at the bottom that the player controls.
    """

    # -- Methods
    def __init__(self):
        """ Constructor function """

        # Call the parent's constructor
        super().__init__()

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        width = 40
        height = 60
        self.image = pygame.Surface([width, height])
        self.image.fill(RED)

        # Set a referance to the image rect.
        self.rect = self.image.get_rect()

        # Set speed vector of player
        self.change_x = 0
        self.change_y = 0

        # List of sprites we can bump against
        self.level = None

    def update(self):
        """ Move the player. """
        # Gravity
        self.calc_grav()

        # Move left/right
        self.rect.x += self.change_x

        # See if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            # If we are moving right,
            # set our right side to the left side of the item we hit
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                # Otherwise if we are moving left, do the opposite.
                self.rect.left = block.rect.right

        # Move up/down
        self.rect.y += self.change_y

        # Check and see if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:

            # Reset our position based on the top/bottom of the object.
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom

            # Stop our vertical movement
            self.change_y = 0

            if isinstance(block, MovingPlatform):
                self.rect.x += block.change_x

    def calc_grav(self):
        """ Calculate effect of gravity. """
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += .35

        # See if we are on the ground.
        if self.rect.y >= SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height

    def jump(self):
        """ Called when user hits 'jump' button. """

        # move down a bit and see if there is a platform below us.
        # Move down 2 pixels because it doesn't work well if we only move down
        # 1 when working with a platform moving down.
        self.rect.y += 2
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 2

        # If it is ok to jump, set our speed upwards
        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.change_y = -10

    # Player-controlled movement:
    def go_left(self):
        """ Called when the user hits the left arrow. """
        self.change_x = -6

    def go_right(self):
        """ Called when the user hits the right arrow. """
        self.change_x = 6

    def stop(self):
        """ Called when the user lets off the keyboard. """
        self.change_x = 0


class Platform(pygame.sprite.Sprite):
    """ Platform the user can jump on """

    def __init__(self, width, height):
        """ Platform constructor. Assumes constructed with user passing in
            an array of 5 numbers like what's defined at the top of this code.
            """
        super().__init__()

        self.image = pygame.Surface([width, height])
        self.image.fill(GREEN)

        self.rect = self.image.get_rect()


class MovingPlatform(Platform):
    """ This is a fancier platform that can actually move. """
    change_x = 0
    change_y = 0

    boundary_top = 0
    boundary_bottom = 0
    boundary_left = 0
    boundary_right = 0

    player = None

    level = None

    def update(self):
        """ Move the platform.
            If the player is in the way, it will shove the player
            out of the way. This does NOT handle what happens if a
            platform shoves a player into another object. Make sure
            moving platforms have clearance to push the player around
            or add code to handle what happens if they don't. """

        # Move left/right
        self.rect.x += self.change_x

        # See if we hit the player
        hit = pygame.sprite.collide_rect(self, self.player)
        if hit:
            # We did hit the player. Shove the player around and
            # assume he/she won't hit anything else.

            # If we are moving right, set our right side
            # to the left side of the item we hit
            if self.change_x < 0:
                self.player.rect.right = self.rect.left
            else:
                # Otherwise if we are moving left, do the opposite.
                self.player.rect.left = self.rect.right

        # Move up/down
        self.rect.y += self.change_y

        # Check and see if we the player
        hit = pygame.sprite.collide_rect(self, self.player)
        if hit:
            # We did hit the player. Shove the player around and
            # assume he/she won't hit anything else.

            # Reset our position based on the top/bottom of the object.
            if self.change_y < 0:
                self.player.rect.bottom = self.rect.top
            else:
                self.player.rect.top = self.rect.bottom

        # Check the boundaries and see if we need to reverse
        # direction.
        if self.rect.bottom > self.boundary_bottom or self.rect.top < self.boundary_top:
            self.change_y *= -1

        cur_pos = self.rect.x - self.level.world_shift
        if cur_pos < self.boundary_left or cur_pos > self.boundary_right:
            self.change_x *= -1


class Level(object):
    """ This is a generic super-class used to define a level.
        Create a child class for each level with level-specific
        info. """

    def __init__(self, player):
        """ Constructor. Pass in a handle to player. Needed for when moving
            platforms collide with the player. """
        self.platform_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.player = player

        # Background image
        self.background = None

        # How far this world has been scrolled left/right
        self.world_shift = 0
        self.level_limit = -1000

    # Update everythign on this level
    def update(self):
        """ Update everything in this level."""
        self.platform_list.update()
        self.enemy_list.update()

    def draw(self, screen):
        """ Draw everything on this level. """

        # Draw the background
        screen.fill(BLUE)

        # Draw all the sprite lists that we have
        self.platform_list.draw(screen)
        self.enemy_list.draw(screen)

    def shift_world(self, shift_x):
        """ When the user moves left/right and we need to scroll everything:
        """

        # Keep track of the shift amount
        self.world_shift += shift_x

        # Go through all the sprite lists and shift
        for platform in self.platform_list:
            platform.rect.x += shift_x

        for enemy in self.enemy_list:
            enemy.rect.x += shift_x


# Create platforms for the level
class Level_01(Level):
    """ Definition for level 1. """

    def __init__(self, player):
        """ Create level 1. """

        # Call the parent constructor
        Level.__init__(self, player)

        self.level_limit = -8000

        # Array with width, height, x, and y of platform
        level = [

            # podelele
            [2800,  LOWER_BORDER, 0,    LOWER_BORDER_LIMIT],
            [800,   LOWER_BORDER, 2900, LOWER_BORDER_LIMIT],
            [1500, LOWER_BORDER, 3800, LOWER_BORDER_LIMIT],
            [4000, LOWER_BORDER, 5400, LOWER_BORDER_LIMIT],


                    # first set from the picture

            #initial platforming
            [50, 50, 700, LOWER_BORDER_LIMIT - 50 - 100],
            [250, 50, 950, LOWER_BORDER_LIMIT - 50 - 100],
            [50, 50, 1050, LOWER_BORDER_LIMIT - 50 - 250],

            #pipes jumps
            [70, 50, 1600, LOWER_BORDER_LIMIT - 50],
            [70, 100, 1850, LOWER_BORDER_LIMIT - 100],
            [70, 160, 2100, LOWER_BORDER_LIMIT - 150],
            [70, 160, 2350, LOWER_BORDER_LIMIT - 150],


                    # second set from the picture

            #platforming over the second hole - 3800
            [150, 50, 3300, LOWER_BORDER_LIMIT - 70 - 70],
            [250, 50, 3550, LOWER_BORDER_LIMIT - 70 - 200],
            [150, 50, 3900, LOWER_BORDER_LIMIT - 70 - 200],
            [50, 50, 4000, LOWER_BORDER_LIMIT - 160],

            [100, 50, 4200, LOWER_BORDER_LIMIT - 150],
            [50, 50, 4500, LOWER_BORDER_LIMIT - 150],
            [50, 50, 4600, LOWER_BORDER_LIMIT - 150],
            [50, 50, 4600, LOWER_BORDER_LIMIT - 100 - 200],
            [50, 50, 4700, LOWER_BORDER_LIMIT - 150],
            [50, 50, 4900, LOWER_BORDER_LIMIT - 150],


            #triangle jump over hole
            [50, 50, 5050, LOWER_BORDER_LIMIT - 50],
            [50, 100, 5100, LOWER_BORDER_LIMIT - 100],
            [50, 150, 5150, LOWER_BORDER_LIMIT - 150],
            [100, 200, 5200, LOWER_BORDER_LIMIT - 200],

            [50, 200, 5400, LOWER_BORDER_LIMIT - 200],
            [50, 150, 5450, LOWER_BORDER_LIMIT - 150],
            [50, 100, 5500, LOWER_BORDER_LIMIT - 100],
            [50, 50, 5550, LOWER_BORDER_LIMIT - 50],

            # triangle jump
            [50, 50, 6500, LOWER_BORDER_LIMIT - 50],
            [50, 100, 6550, LOWER_BORDER_LIMIT - 100],
            [50, 150, 6600, LOWER_BORDER_LIMIT - 150],
            [50, 200, 6650, LOWER_BORDER_LIMIT - 200],

            [50, 200, 6850, LOWER_BORDER_LIMIT - 200],
            [50, 150, 6900, LOWER_BORDER_LIMIT - 150],
            [50, 100, 6950, LOWER_BORDER_LIMIT - 100],
            [50, 50, 7000, LOWER_BORDER_LIMIT - 50],






            # flag
            [50, 550, 9000, LOWER_BORDER_LIMIT - 550],
            [50, 50, 8950, LOWER_BORDER_LIMIT - 550],
            [100, 50, 9000, LOWER_BORDER_LIMIT - 500],
            [150, 50, 8950, LOWER_BORDER_LIMIT - 50],

        ]

        # Go through the array above and add platforms
        for platform in level:
            block = Platform(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)

        # Add a custom moving platform
        block = MovingPlatform(70, 40)
        block.rect.x = 1350
        block.rect.y = 280
        block.boundary_left = 1350
        block.boundary_right = 1600
        block.change_x = 1
        block.player = self.player
        block.level = self
        self.platform_list.add(block)


# Create platforms for the level
class Level_02(Level):
    """ Definition for level 2. """

    def __init__(self, player):
        """ Create level 1. """

        # Call the parent constructor
        Level.__init__(self, player)

        self.level_limit = -1000

        # Array with type of platform, and x, y location of the platform.
        level = [[210, 70, 500, 550],
                 [210, 70, 800, 400],
                 [210, 70, 1000, 500],
                 [210, 70, 1120, 280],
                 ]

        # Go through the array above and add platforms
        for platform in level:
            block = Platform(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)

        # Add a custom moving platform
        block = MovingPlatform(70, 70)
        block.rect.x = 1500
        block.rect.y = 300
        block.boundary_top = 100
        block.boundary_bottom = 550
        block.change_y = -1
        block.player = self.player
        block.level = self
        self.platform_list.add(block)


def main():
    """ Main Program """
    agent = ch4d.DQN(SCREEN_HEIGHT * SCREEN_WIDTH // (10 * 10), 3)
    steps = []
    trials = 1000

    for trial in range(1000):

        pygame.init()
        

        # Set the height and width of the screen
        size = [SCREEN_WIDTH, SCREEN_HEIGHT]
        screen = pygame.display.set_mode(size)

        pygame.display.set_caption("Platformer with moving platforms")

        # Create the player
        player = Player()

        # Create all the levels
        level_list = []
        level_list.append(Level_01(player))
        level_list.append(Level_02(player))

        # Set the current level
        current_level_no = 0
        current_level = level_list[current_level_no]

        active_sprite_list = pygame.sprite.Group()
        player.level = current_level

        player.rect.x = 340
        player.rect.y = SCREEN_HEIGHT - player.rect.height - LOWER_BORDER
        active_sprite_list.add(player)

        # Loop until the user clicks the close button.
        done = False

        # Used to manage how fast the screen updates
        clock = pygame.time.Clock()
        

        import time
        import matplotlib.pyplot as plt

        score = 0
        COMPUTE_ONCE_EVERY = 15
        max_x = player.rect.x + current_level.world_shift
        begin_time = int(time.time())
        last_used_time = begin_time
        frame_counter = 0
        doing_bizniz = False
        action = None
        agent_last_score = None

        # -------- Main Program Loop -----------
        while not done:
            
            frame_counter += 1
            if frame_counter == COMPUTE_ONCE_EVERY:
                frame_counter = 0
                doing_bizniz = True
                cur_state = pygame.surfarray.array3d(pygame.display.get_surface())
                cur_state = ch4d.rgb2gray(cur_state)
                cur_state = ch4d.block_mean(cur_state, 10)
                
                agent_last_score = score
                action = agent.act(cur_state)
                print("Doing: ", action)
                if player.change_x < 0 or player.change_x > 0:
                    player.stop()

                if action == 0:
                    player.go_left()
                elif action == 1:
                    player.jump()
                elif action == 2:
                    player.go_right()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        player.go_left()
                    if event.key == pygame.K_RIGHT:
                        player.go_right()
                    if event.key == pygame.K_UP:
                        player.jump()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT and player.change_x < 0:
                        player.stop()
                    if event.key == pygame.K_RIGHT and player.change_x > 0:
                        player.stop()

            # Update the player.
            active_sprite_list.update()

            # Update items in the level
            current_level.update()

            # If the player gets near the right side, shift the world left (-x)
            if player.rect.right >= 500:
                diff = player.rect.right - 500
                player.rect.right = 500
                current_level.shift_world(-diff)

            # If the player gets near the left side, shift the world right (+x)
            if player.rect.left <= 120:
                diff = 120 - player.rect.left
                player.rect.left = 120
                current_level.shift_world(diff)

            # If the player gets to the end of the level, go to the next level
            current_position = player.rect.x + current_level.world_shift
            if current_position < current_level.level_limit:
                if current_level_no < len(level_list) - 1:
                    player.rect.x = 120
                    current_level_no += 1
                    current_level = level_list[current_level_no]
                    player.level = current_level
                else:
                    # Out of levels. This just exits the program.
                    # You'll want to do something better.
                    done = True

            # ALL CODE TO DRAW SHOULD GO BELOW THIS COMMENT
            current_level.draw(screen)
            active_sprite_list.draw(screen)

            # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT


            if player.rect.y > 510:
                score = -10000

            if score < -125: 
                done = True

            if current_position < max_x:
                score += (max_x - current_position)
                max_x = current_position


            print(score)

            current_time = int(time.time())
            score += last_used_time * 50
            score -= current_time * 50

            last_used_time = current_time

            if doing_bizniz == True:
                if current_position > max_x:
                    score -= 10

                agent_score_delta = score - agent_last_score

                new_state = pygame.surfarray.array3d(pygame.display.get_surface())
                new_state = ch4d.rgb2gray(new_state)
                new_state = ch4d.block_mean(new_state, 10)

                agent.remember(cur_state, action, agent_score_delta, new_state, done)

                doing_bizniz = False

            # Limit to 60 frames per second
            clock.tick(120)

            # Go ahead and update the screen with what we've drawn.
            pygame.display.flip()


        # Be IDLE friendly. If you forget this line, the program will 'hang'
        # on exit.
        if done == True:
            agent.replay()
            agent.target_train()
        
        pygame.quit()


if __name__ == "__main__":
    main()