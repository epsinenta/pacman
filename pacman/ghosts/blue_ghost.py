from math import sqrt

import pygame

import global_variables
from ghosts.core import AbstractGhostLogic, MainGhost, Direction
from ghosts.sounds import Sound
from layouts import map_with_sprites
from player import Pacman


class BlueGhostLogic(AbstractGhostLogic):
    default_position: pygame.Vector2 = None
    default_direction = "right"
    back_animations = [f"./textures/ghosts/blue/{global_variables.theme_api.texture_modifier}b1.png",
                       f"./textures/ghosts/blue/{global_variables.theme_api.texture_modifier}b2.png"]
    left_animations = [f"./textures/ghosts/blue/{global_variables.theme_api.texture_modifier}l1.png",
                       f"./textures/ghosts/blue/{global_variables.theme_api.texture_modifier}l2.png"]
    right_animations = [f"./textures/ghosts/blue/{global_variables.theme_api.texture_modifier}r1.png",
                        f"./textures/ghosts/blue/{global_variables.theme_api.texture_modifier}r2.png"]
    up_animations = [f"./textures/ghosts/blue/{global_variables.theme_api.texture_modifier}u1.png",
                     f"./textures/ghosts/blue/{global_variables.theme_api.texture_modifier}u2.png"]
    scared_animations_blue = [f"./textures/ghosts/scared/z{i}.png" for i in range(1, 5)]
    speed = 0.3
    flag = 1
    list_normal_tile = ['seed', 5, 'nrg']
    eaten: int = 0

    def __new__(cls, *args, **kwargs):
        cls = super().__new__(cls)
        cls.default_position = pygame.Vector2(11 * global_variables.cell_size + (global_variables.cell_size / 2),
                                              14 * global_variables.cell_size)
        return cls

    def __init__(self, main_ghost: "MainGhost"):
        super().__init__(main_ghost)
        self.prev_block = (0, 0)
        self.main_ghost = main_ghost
        self.stage = 1
        self.eaten = 0
        self.stay = 1
        self.blyat = 0

    def my_position_in_blocks(self):
        return int((self.main_ghost.position.x + global_variables.cell_size / 2) // global_variables.cell_size), \
               int((self.main_ghost.position.y + global_variables.cell_size / 2) // global_variables.cell_size)

    def find_ways(self):  # 0 - ищем выход из начальной комнаты
        tmp_list_vec = []
        if self.main_ghost.position[0] % global_variables.cell_size == 0 and \
                self.main_ghost.position[1] % global_variables.cell_size == 0 and self.prev_block != (
                self.main_ghost.position[0], self.main_ghost.position[1]):
            self.prev_block = (self.main_ghost.position[0], self.main_ghost.position[1])
            if len(map_with_sprites[0]) <= self.my_position_in_blocks()[0] + 1 or \
                    self.my_position_in_blocks()[0] - 1 < 0:
                tmp_list_vec.append('ll')
                return tmp_list_vec
            try:
                if map_with_sprites[self.my_position_in_blocks()[1] + 1][self.my_position_in_blocks()[0]] in \
                        self.list_normal_tile:
                    tmp_list_vec.append('back')
            except IndexError:
                pass
            try:
                if map_with_sprites[self.my_position_in_blocks()[1] - 1][self.my_position_in_blocks()[0]] in \
                        self.list_normal_tile:
                    tmp_list_vec.append('up')
            except IndexError:
                pass
            try:
                if map_with_sprites[self.my_position_in_blocks()[1]][self.my_position_in_blocks()[0] + 1] in \
                        self.list_normal_tile:
                    tmp_list_vec.append('right')
            except IndexError:
                pass
            try:
                if map_with_sprites[self.my_position_in_blocks()[1]][self.my_position_in_blocks()[0] - 1] in \
                        self.list_normal_tile:
                    tmp_list_vec.append('left')
            except IndexError:
                pass
        return tmp_list_vec

    def select_tile(self, target_pos):
        if global_variables.debug:
            pygame.draw.rect(
                self.main_ghost.screen, (26, 26, 255),
                (target_pos[0], target_pos[1] + 50, global_variables.cell_size, global_variables.cell_size),
                1
            )
        direction = self.main_ghost.direction
        tmp_list_ways = self.find_ways()
        if direction == 'right':
            back_direction = 'left'
        elif direction == 'left':
            back_direction = 'right'
        elif direction == 'up':
            back_direction = 'back'
        elif direction == 'back':
            back_direction = 'up'
        else:
            back_direction = ''
        if len(tmp_list_ways) == 1 and tmp_list_ways[0] == 'll':
            return back_direction
        elif len(tmp_list_ways) > 2:
            min_range = 100000
            min_vel = 'left'
            for tmp_vel in tmp_list_ways:
                if tmp_vel != back_direction:
                    if tmp_vel == 'right':
                        tmp_range = sqrt((self.main_ghost.position[0] + global_variables.cell_size - target_pos[0]) ** 2
                                         + (self.main_ghost.position[1] - target_pos[1]) ** 2)
                    elif tmp_vel == 'left':
                        tmp_range = sqrt((self.main_ghost.position[0] - global_variables.cell_size - target_pos[0]) ** 2
                                         + (self.main_ghost.position[1] - target_pos[1]) ** 2)
                    elif tmp_vel == 'up':
                        tmp_range = sqrt((self.main_ghost.position[0] - target_pos[0]) ** 2 + (
                                self.main_ghost.position[1] - global_variables.cell_size - target_pos[1]) ** 2)
                    else:
                        tmp_range = sqrt((self.main_ghost.position[0] - target_pos[0]) ** 2 + (
                                self.main_ghost.position[1] + global_variables.cell_size - target_pos[1]) ** 2)
                    if tmp_range < min_range:
                        min_range = tmp_range
                        min_vel = tmp_vel
            direction = min_vel
        elif len(tmp_list_ways) == 2:
            for tmp_vel in tmp_list_ways:
                if tmp_vel != back_direction:
                    direction = tmp_vel
        return direction

    def acceleration_stage(self):
        target_pos = [216 * (global_variables.cell_size / 8), 256 * (global_variables.cell_size / 8)]
        return self.select_tile(target_pos)

    def chase_stage(self, pacman, all_ghosts):
        blinky_pos = all_ghosts[1].position
        tmp_pos = [pacman.x, pacman.y]
        if pacman.vec == 0:
            tmp_pos[0] += 16 * (global_variables.cell_size / 8)
        elif pacman.vec == 1:
            tmp_pos[1] -= 16 * (global_variables.cell_size / 8)
        elif pacman.vec == 2:
            tmp_pos[0] -= 16 * (global_variables.cell_size / 8)
        elif pacman.vec == 3:
            tmp_pos[1] += 16 * (global_variables.cell_size / 8)
        else:
            print("или стоит или фейл")
        target_pos = (tmp_pos[0] + tmp_pos[0] - blinky_pos[0], tmp_pos[1] + tmp_pos[1] - blinky_pos[1])
        return self.select_tile(target_pos)

    def go_home(self):
        self.main_ghost.reset_position()
        self.main_ghost.direction = "up"
        self.stay = 1
        self.stage = 1

    def stay_stage(self, trigger):
        if trigger != 0 and self.stay == 1:
            self.stay = 2
        if self.flag == 1:
            self.main_ghost.direction = 'up'
            self.flag = 0
        if self.stay == 1:
            if (self.main_ghost.position[1] + (global_variables.cell_size / 2)) % global_variables.cell_size == 0:
                if map_with_sprites[
                    (self.main_ghost.position.y + global_variables.cell_size) // global_variables.cell_size + 1
                ][
                    (self.main_ghost.position.x // global_variables.cell_size)
                ] in self.list_normal_tile:
                    return 'back'
                elif map_with_sprites[
                    (self.main_ghost.position.y + global_variables.cell_size) // global_variables.cell_size - 1
                ][
                    (self.main_ghost.position.x // global_variables.cell_size)
                ] in self.list_normal_tile:
                    return 'up'
            return self.main_ghost.direction
        elif self.stay == 2:
            if (self.main_ghost.position[0] + (global_variables.cell_size / 2)) % global_variables.cell_size == 0:
                if any(
                        map_with_sprites[self.main_ghost.position_in_blocks[1] - i][
                            self.main_ghost.position_in_blocks[0]] == 'gate'
                        for i in range(1, 3)
                ):
                    self.stay = 3
                    return 'up'
            return 'right'
        elif self.stay == 3:
            if self.main_ghost.position[1] % global_variables.cell_size == 0:
                if map_with_sprites[self.my_position_in_blocks()[1] + 1][self.main_ghost.position_in_blocks[0]] == \
                        'gate':
                    self.stay = 0
                    self.prev_block = (self.main_ghost.position[0], self.main_ghost.position[1])
                    return 'right'
            return 'up'

    def scared_stage(self, pacman):
        left_block = [self.main_ghost.position.x + -1 * 24, self.main_ghost.position.y]
        down_block = [self.main_ghost.position.x, self.main_ghost.position.y + -1 * 24]
        up_block = [self.main_ghost.position.x, self.main_ghost.position.y + 1 * 24]
        if sqrt((pacman.x - up_block[0]) ** 2 + (pacman.y - up_block[1]) ** 2) > sqrt(
                (pacman.x - left_block[0]) ** 2 + (pacman.y - left_block[1]) ** 2):
            target_pos = up_block
        elif sqrt((pacman.x - left_block[0]) ** 2 + (pacman.y - left_block[1]) ** 2) > sqrt(
                (pacman.x - down_block[0]) ** 2 + (pacman.y - down_block[1]) ** 2):
            target_pos = left_block
        else:
            target_pos = down_block
        return self.select_tile(target_pos)

    def eaten_stage(self):
        target_pos = [13 * global_variables.cell_size + (global_variables.cell_size / 2),
                      11 * global_variables.cell_size]
        if self.eaten == 1:
            self.speed = 8
            if ((self.main_ghost.position.x - target_pos[0]) ** 2 + (self.main_ghost.position.y - target_pos[1]) ** 2) \
                    ** 0.5 > global_variables.cell_size // 2:
                return self.select_tile(target_pos)
            else:
                self.main_ghost._position.x = target_pos[0]
                self.main_ghost._position.y = target_pos[1]
                self.eaten = 2
                self.speed = 1
                return 'back'
        elif self.eaten == 2:
            if abs(self.main_ghost.position.y - 14.5 * global_variables.cell_size) >= \
                    2 * (global_variables.cell_size / 8):
                return 'back'
            else:
                self.eaten = 3
                return 'left'
        elif self.eaten == 3:
            if self.main_ghost.position.x != 11 * global_variables.cell_size + 4:
                return 'left'
            else:
                self.eaten = 0
                self.stay = 1
                self.speed = 0.3
                self.main_ghost.scared = 0
                return 'up'

    def where_am_i_should_move(self, pacman: Pacman, all_ghosts, stage=1,
                               trigger=0) -> Direction:  # 1 - стадия разгона, 2 - стадия преследования, 3 - страх
        if self.stay:
            return self.stay_stage(global_variables.blue_trigger)
        elif self.eaten:
            if self.eaten == 1:
                if not self.blyat:
                    self.main_ghost.force()
                    self.blyat = 1
                else:
                    self.blyat = 0
            return self.eaten_stage()
        elif self.main_ghost.scared:
            return self.scared_stage(pacman)
        elif self.stage == 1:
            Sound().current_sound_index = max(Sound().current_sound_index, 3)
            return self.chase_stage(pacman, all_ghosts)
        elif self.stage == 2:
            Sound().current_sound_index = max(Sound().current_sound_index, 3)
            return self.acceleration_stage()
        return 'back'
