import pygame
from random import choice, randint
import os
import json
from typing import Literal

# Player Image constants and settings
PLAYER_DIR = r"C:\Users\tanner.martin\Desktop\test_game\test_game2\resources\pokemon"
AVAILABLE_PLAYER_PREFIXES = ["p1", "p2", "p3"]
AVAILABLE_PLAYER_POSTFIXES = ["walk"]
PRE_POST_SEPERATOR = "_"


class Player(pygame.sprite.Sprite):
    def __init__(self, gravity:int=10, speed:int=10):
        super().__init__()
        self.spritesheet = generate_random_pokemon_spritesheet()
        self.animation_frames = self.generate_frames()
        self.frame_index = 0
        # physics
        self.velocity = [0, 0]
        self.max_velocity = [speed, gravity]
        self.min_velocity = [
            self.max_velocity[0] * -1,
            self.max_velocity[1] * -1,
        ]
        self.acceleration_increase = [2, 5]
        self.acceleration_decrease = [
            self.acceleration_increase[0] * -1,
            self.acceleration_increase[1] * -1,
        ]
        self.jumping = False
        self.direction = 1
        self.frame_index = randint(0, len(self.animation_frames)-1)
        self.image: pygame.surface.Surface = self.animation_frames[self.frame_index]
        self.rect = self.image.get_rect()

    def generate_frames(self):
        ss_width = self.spritesheet.get_width()
        ss_height = self.spritesheet.get_height()
        frame_width = int(ss_width/4)
        frame_height = int(ss_height/4)
        frame_x = 0
        frame_y = 0
        frames:list[pygame.surface.Surface] = []
        for row in range(4):
            frame_x = 0
            for column in range(4):
                frames.append(self.spritesheet.subsurface(pygame.Rect(frame_x, frame_y, frame_width, frame_height)))
                frame_x += frame_width
            frame_y += frame_height
        return frames
            
    def _frames_data_to_frames_animation(self):
        for frame_data in self.frames:
            try:
                frame = self.spritesheet.subsurface(
                    pygame.Rect(
                        frame_data.get("x"),
                        frame_data.get("y"),
                        frame_data.get("w"),
                        frame_data.get("h"),
                    )
                )
                self.animation_frames.append(frame)
            except:
                ...

    def get_image(self):
        image = self.animation_frames[self.frame_index]
        return image

    def change_frame_index(self):
        self.frame_index += 1
        if self.velocity[0] < 0:
            if self.frame_index > 7:
                self.frame_index = 4
        elif self.velocity[0] > 0:
            if self.frame_index > 11:
                self.frame_index = 8
        else:
            if self.frame_index > 3:
                self.frame_index = 0


        #print(self.frame_index, self.velocity)

    def move_x(self, velocity:int):
        if velocity != 0:
            self.velocity[0] = self.velocity[0] + velocity
        else:
            if self.velocity[0] != 0:
                self.velocity[0] = self.velocity[0] -1 if self.velocity[0] > 0 else self.velocity[0] + 1
      
        if self.velocity[0] > self.max_velocity[0] or self.velocity[0] < self.min_velocity[0]:
            self.velocity[0] = self.max_velocity[0] if self.velocity[0] > self.max_velocity[0] else self.min_velocity[0]

        if self.velocity[0] > 0:
            self.direction = 1
        elif self.velocity[0] < 0:
            self.direction = -1

    def move_y(self):
        if self.jumping:
            self.velocity[1] = self.velocity[1] + 1
            if self.velocity[1] > self.max_velocity[1]:
                self.velocity[1] = self.max_velocity[1]
        if self.rect.top < 0 and self.velocity[1] < 0:
            self.velocity[1] = self.velocity[1] * -1
            self.rect.top = 0
        self.rect.y += self.velocity[1]

    def jump(self):
        if not self.jumping:
            self.velocity[1] = self.min_velocity[1]
            self.jumping = True
    
    def land(self, bottom:int):
        if self.jumping and self.rect.bottom >= bottom:
            self.velocity[1] = 0
            self.rect.bottom = bottom
            self.jumping = False
    
    def wall_bounce(self, right:int):
        if self.velocity[0] > 0 and self.rect.right >= right:
            self.velocity[0] = self.velocity[0] * -1
        elif self.velocity[0] < 0 and self.rect.left <= 0:
            self.velocity[0] = self.velocity[0] * -1

    def move(self, pressed_keys:pygame.key.ScancodeWrapper, ww:int, wh:int, jump:bool):
        if pressed_keys[pygame.K_LEFT]:
            self.move_x(-3)
        elif pressed_keys[pygame.K_RIGHT]:
            self.move_x(3)
        else:
            self.move_x(0)
        if jump:
            self.jump()
        self.move_y()
        self.wall_bounce(ww)
        self.land(wh)
        self.rect.move_ip(self.velocity)

    def update(self):
        self.change_frame_index()
        self.image = self.get_image()
        self.rect.move_ip(self.velocity)

def generate_player_name():
    # use the constants to generate and return something like "p1_walk"
    player_prefix = choice(AVAILABLE_PLAYER_PREFIXES)
    player_postfix = "walk"
    chosen_player_name = PRE_POST_SEPERATOR.join([player_prefix, player_postfix])
    return chosen_player_name


def generate_player_spritesheet_and_frame_path(chosen_player_name: str):
    # use the generated player name like "p1_walk" to generate a path to it's spritesheet
    chosen_player_directory = os.path.join(PLAYER_DIR, chosen_player_name)
    player_spritesheet_name = chosen_player_name + ".png"
    player_frame_name = chosen_player_name + ".json"
    player_spritesheet_path = os.path.join(
        chosen_player_directory, player_spritesheet_name
    )
    player_frame_path = os.path.join(chosen_player_directory, player_frame_name)
    return player_spritesheet_path, player_frame_path


def convert_loaded_frames_to_list(frames: dict[str, dict]) -> list[dict]:
    return [v.get("frame") for k, v in frames.items()]


def load_and_return_player_frames(player_frame_path: str) -> dict[str, dict]:
    with open(player_frame_path, "rb") as fp:
        frames_data: dict[str:dict] = json.load(fp)
    return frames_data.get("frames")


def generate_player_spritesheet_and_frames(
    chosen_player_name: str | None = None, frame_type: Literal["LIST", "DICT"] = "LIST"
) -> tuple[pygame.Surface, dict[str, dict] | list[dict]]:
    # choose a random player, find it's path, load it's spritesheet and return it
    chosen_player_name = (
        chosen_player_name if chosen_player_name else generate_player_name()
    )
    (
        player_spritesheet_path,
        player_frame_path,
    ) = generate_player_spritesheet_and_frame_path(chosen_player_name)
    spritesheet = pygame.image.load(player_spritesheet_path)
    frames = load_and_return_player_frames(player_frame_path)
    if frame_type == "LIST":
        frames = convert_loaded_frames_to_list(frames)
    try:
        spritesheet = spritesheet.convert_alpha()
    except:
        ...
    return spritesheet, frames

def generate_random_pokemon_spritesheet():
    img_name = choice(os.listdir(PLAYER_DIR))
    img_path = os.path.join(PLAYER_DIR, img_name)
    sprite_sheet = pygame.image.load(img_path)
    try:
        sprite_sheet = sprite_sheet.convert_alpha()
    except:
        print(img_name)
        try:
            sprite_sheet = sprite_sheet.convert()
        except:
            ...
    return sprite_sheet