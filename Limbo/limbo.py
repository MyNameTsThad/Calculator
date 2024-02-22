import pygame as pg
import json
import math
import random
import colorsys
import time

pg.init()

clock = pg.time.Clock()

pg.event.set_allowed([pg.QUIT, pg.KEYDOWN, pg.KEYUP])

pg.mixer.pre_init(44100, 16, 2, 4096)
screen = pg.display.set_mode(pg.display.get_desktop_sizes()[0], pg.DOUBLEBUF)
background = pg.image.load("./Limbo/background.png").convert_alpha()
minBackgroundRatio = min(pg.display.get_desktop_sizes()[0][0] / background.get_size()[0],
                         pg.display.get_desktop_sizes()[0][1] / background.get_size()[1])
maxBackgroundRatio = max(pg.display.get_desktop_sizes()[0][0] / background.get_size()[0],
                         pg.display.get_desktop_sizes()[0][1] / background.get_size()[1])
background = pg.transform.rotozoom(background, 0, maxBackgroundRatio)
background.set_alpha(127)
error_note = pg.image.load("./Limbo/Error.png").convert_alpha()
error_note = pg.transform.rotozoom(error_note, 0, 0.5)
catch_note = pg.image.load("./Limbo/Catch.png").convert_alpha()
catch_note = pg.transform.rotozoom(catch_note, 0, 0.5)
release_note = pg.image.load("./Limbo/Release.png").convert_alpha()
release_note = pg.transform.rotozoom(release_note, 0, 0.5)
press_note = pg.image.load("./Limbo/Press.png").convert_alpha()
press_note = pg.transform.rotozoom(press_note, 0, 0.5)
input_note = pg.image.load("./Limbo/Input.png").convert_alpha()
input_note = pg.transform.rotozoom(input_note, 0, 0.5)

Unknown_key = pg.image.load("./Limbo/key.png").convert_alpha()
correct_key = pg.image.load("./Limbo/correct_key.png").convert_alpha()
color_keys = [0, 50, 60, 120, 200, 240, 280, 300]
color_key_images = []

choosen = random.randint(0, 7)

key_rect = Unknown_key.get_rect()
for color in color_keys:
    key_clone = Unknown_key.copy()
    for x in range(key_rect.w):
        for y in range(key_rect.h):
            get_color = Unknown_key.get_at((x, y))
            h, s, v, a = get_color.hsva
            r, g, b = colorsys.hsv_to_rgb(color / 360, s / 100, v / 100)
            r = int(r * 255)
            g = int(g * 255)
            b = int(b * 255)
            a = int(a / 100 * 255)
            get_color.r = r
            get_color.g = g
            get_color.b = b
            get_color.a = a
            key_clone.set_at((x, y), get_color)
    color_key_images.append(key_clone)


def set_color(surface, color):
    rect = surface.get_rect()
    surf = pg.Surface(rect.size, pg.SRCALPHA)
    surf.fill(color)

    surface.blit(surf, (0, 0), None, pg.BLEND_ADD)


hit_list = []
for i in range(1, 31):
    exec(f"hit{str(i)} = pg.image.load(\"./Limbo/hit/{str(i)}.png\").convert_alpha()")
    exec(f"hit{str(i)} = pg.transform.rotozoom(hit{str(i)},0,0.8)")
    exec(f"hit_list.append(hit{str(i)})")

sfx_list = ["./Limbo/SFX/tap.mp3", "./Limbo/SFX/drag.mp3", "./Limbo/SFX/release.mp3", "./Limbo/SFX/error.mp3"]

pg.display.set_icon(background)

running = 1

chart = json.loads(open("./Limbo/song.json", mode="r+").read())

delay = 3_500

lines: dict = chart["lines"]
# [x%,y%,rotate]
circleInputs: dict = chart["inputs"]
# [x%,y%,rotate]
updates: dict = chart["updates"]

effects: list = []

# Random notes :)
last_choose = ""
r = ""
for i in range(152450, 190901, 75):
    while r == last_choose:
        r = random.choice(["0", "1", "2", "3", "7", "8"])
    last_choose = r
    circleInputs[r][5].append([0, i, 650, False])

# Auto sort
for circle in circleInputs.keys():
    circleInputs[circle][5].sort(key=lambda x: x[1])

# Random Inputs :)
circleShuffle = {"0": 0.35, "1": 0.45, "2": 0.55, "3": 0.65, "7": 0.25, "8": 0.75}
for i in range(181200, 190601, 450):
    choose_list = ["0", "1", "2", "3", "7", "8"]
    last_choose = []
    while len(last_choose) != 4:
        r = random.choice(choose_list)
        choose_list.remove(r)
        if not (r in last_choose):
            last_choose.append(r)
    random.shuffle(last_choose)
    for _ in range(2):
        a = last_choose.pop()
        b = last_choose.pop()
        a_in = circleShuffle[b] - circleShuffle[a]
        b_in = circleShuffle[a] - circleShuffle[b]
        updates["inputs"][a].append([i, i + 300, 0, "easeOutQuint", a_in, 0])
        updates["inputs"][b].append([i, i + 300, 0, "easeOutQuint", b_in, 0])
        circleShuffle[a], circleShuffle[b] = circleShuffle[b], circleShuffle[a]

noteType = [press_note, catch_note, release_note, error_note]

winScale = pg.display.get_desktop_sizes()[0]

song_started = 0

old_tick = 3_500

magic_number_1 = 1.70158
pi2o3 = math.pi * 2 / 3
magic_number_2 = 7.5625
x_start = winScale[0] / 2


# Ease functions
def linear(t):
    return t


def easeInSine(t):
    return 1 - math.cos(t * math.pi / 2)


def easeOutSine(t):
    return math.sin(t * math.pi / 2)


def easeInOutSine(t):
    return (1 - math.cos(math.pi * t)) / 2


def easeInQuad(t):
    return t * t


def easeOutQuad(t):
    return -t * (t - 2)


def easeInOutQuad(t):
    t *= 2
    if t < 1:
        return t * t / 2
    else:
        t -= 1
        return (1 - t * (t - 2)) / 2


def easeInCubic(t):
    return t ** 3


def easeOutCubic(t):
    t -= 1
    return t ** 3 + 1


def easeInOutCubic(t):
    t *= 2
    if t < 1:
        return t ** 3 / 2
    else:
        t -= 2
        return (t ** 3 + 2) / 2


def easeInQuart(t):
    return t ** 4


def easeOutQuart(t):
    t -= 1
    return (1 - t ** 4)


def easeInOutQuart(t):
    t *= 2
    if t < 1:
        return t ** 4 / 2
    else:
        t -= 2
        return (2 - t ** 4) / 2


def easeInQuint(t):
    return t ** 5


def easeOutQuint(t):
    t -= 1
    return t ** 5 + 1


def easeInOutQuint(t):
    t *= 2
    if t < 1:
        return t ** 5 / 2
    else:
        t -= 2
        return (t ** 5 + 2) / 2


def easeInExpo(t):
    return math.pow(2, 10 * (t - 1))


def easeOutExpo(t):
    return -math.pow(2, -10 * t) + 1


def easeInOutExpo(t):
    t *= 2
    if t < 1:
        return math.pow(2, 10 * (t - 1)) / 2
    else:
        t -= 1
        return -math.pow(2, -10 * t) - 1


def easeInCirc(t):
    return 1 - math.sqrt(1 - t * t)


def easeOutCirc(t):
    t -= 1
    return math.sqrt(1 - t * t)


def easeInOutCirc(t):
    t *= 2
    if t < 1:
        return -(math.sqrt(1 - t * t) - 1) / 2
    else:
        t -= 2
        return (math.sqrt(1 - t * t) + 1) / 2


def easeInBack(t):
    return (magic_number_1 + 1) * t ** 3 - magic_number_1 * t ** 2


def easeOutBack(t):
    return 1 + (magic_number_1 + 1) * (t - 1) ** 3 + magic_number_1 * (t - 1) ** 2


def easeInOutBack(t):
    t *= 2
    if t < 1:
        return (t ** 2 * ((magic_number_1 * 1.525 + 1) * t - magic_number_1 * 1.525)) / 2
    else:
        return ((t - 2) ** 2 * ((magic_number_1 * 1.525 + 1) * (t - 2) + (magic_number_1 * 1.525)) + 2) / 2


def easeInElastic(t):
    if t == 0:
        return 0
    elif t == 1:
        return 1
    else:
        return -2 ** (10 * (t - 1)) * math.sin(pi2o3 * (t * 10 - 10.75))


def easeOutElastic(t):
    if t == 0:
        return 0
    elif t == 1:
        return 1
    else:
        return 2 ** (-10 * t) * math.sin(pi2o3 * (t * 10 - 10.75)) + 1


def easeInOutElastic(t):
    t *= 2
    if t == 0:
        return 0
    elif t == 2:
        return 1
    elif t < 1:
        return -(2 ** (10 * (t - 1)) * math.sin((10 * t - 11.125) * pi2o3 * 2 / 3)) / 2
    else:
        return (2 ** (-10 * t + 10) * math.sin((10 * t - 11.125) * pi2o3 * 2 / 3)) / 2 + 1


def easeInBounce(t):
    return 1 - easeOutBounce(1 - t)


def easeOutBounce(t):
    if (t < 1 / 2.75):
        return magic_number_2 * t ** 2
    elif (x < 2 / 2.75):
        return magic_number_2 * (t := t - 1.5 / 2.75) * t + 0.75
    elif (x < 2.5 / 2.75):
        return magic_number_2 * (t := t - 2.25 / 2.75) * t + 0.9375
    else:
        return magic_number_2 * (t := t - 2.625 / 2.75) * t + 0.984375


def easeInOutBounce(t):
    t *= 2
    if t < 1:
        return (1 - easeOutBounce(1 - t)) / 2
    else:
        return (1 + easeOutBounce(t - 1)) / 2


font = pg.font.SysFont("arial", int(15 * minBackgroundRatio))
FOCUS_font = pg.font.SysFont("arial", int(30 * minBackgroundRatio))

auto = 1
game_over = 0
headphone_delay = 300
keyPressing = []

game_delay = delay
music_delay = delay + headphone_delay

if auto:
    interval = (-100, 0, 0)
else:
    interval = (-100, 100, 250)

test_time = 0

while running:
    keyPress = []
    keyRelease = []
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = 0
        elif event.type == pg.KEYDOWN:
            keyPress.append(event.unicode)
            keyPressing.append(event.unicode)
        elif event.type == pg.KEYUP:
            keyRelease.append(event.unicode)
            keyPressing.remove(event.unicode)
    if background.get_alpha() < 255:
        screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))
    if auto:
        text = font.render("AUTO", 0, pg.Color(255, 255, 255))
        textrect = text.get_rect()[2:4]
        screen.blit(text, (winScale[0] / 2 - textrect[0] / 2, textrect[1] / 2))
    if (pg.time.get_ticks() < game_delay / 2):
        pass
    elif (pg.time.get_ticks() < game_delay):
        d = easeInOutQuint((min(pg.time.get_ticks(), 2750) - 1750) / 750)
        pg.draw.line(screen, (255, 255, 255), (x_start - x_start * d, winScale[1] / 2),
                     (x_start + x_start * d, winScale[1] / 2), 5)
    elif (pg.time.get_ticks() >= game_delay) and not game_over:
        start_tick = pg.time.get_ticks() - music_delay
        game_tick = test_time + pg.time.get_ticks()
        if not song_started:
            pg.mixer_music.load("./Limbo/LIMBO.mp3")
            pg.mixer_music.play(start=(test_time + headphone_delay + start_tick) // 1000)
            song_started = 1
        for key in updates.keys():
            for index in updates[key].keys():
                if key == "lines":
                    util = lines[index]
                elif key == "inputs":
                    util = circleInputs[index]
                remove_updates = []
                for command in updates[key][index]:
                    if command[0] + delay > game_tick:
                        break
                    else:
                        if type(command[4]) == tuple:
                            command[4] = random.randint(command[4][0], command[4][1])
                        if game_tick >= command[1] + delay:
                            if command[3] == "set":
                                util[command[2]] = command[4]
                            elif command[5]:
                                exec(
                                    f"util[command[2]] += (1 - {command[3]}((game_tick-command[0]- delay)/(command[1]-command[0])))*command[4]")
                            else:
                                command[5] = 1
                                exec(
                                    f"util[command[2]] += command[4]")
                            remove_updates.append(command)
                        else:
                            if command[3] == "set":
                                util[command[2]] = command[4]
                                remove_updates.append(command)
                            elif command[5]:
                                exec(
                                    f"util[command[2]] += ({command[3]}((game_tick-command[0]- delay)/(command[1]-command[0])) - {command[3]}((old_tick-command[0]- delay)/(command[1]-command[0])))*command[4]")
                            else:
                                command[5] = 1
                                exec(
                                    f"util[command[2]] += {command[3]}((game_tick-command[0]- delay)/(command[1]-command[0]))*command[4]")
                for command in remove_updates:
                    updates[key][index].remove(command)

        remove_effect = []
        for effect in effects:
            effect[2] += game_tick - old_tick
            if effect[2] > 400:
                remove_effect.append(effect)
        for effect in remove_effect:
            effects.remove(effect)

        for index in lines.keys():
            line = lines[index]
            posx = math.cos(math.pi * line[2] / 180)
            posy = math.sin(math.pi * line[2] / 180)
            winx = winScale[0] * line[0]
            winy = winScale[1] * line[1]
            pg.draw.line(screen, (255, 255, 255), (-(posx * 2000) + winx, -(posy * 2000) + winy),
                         ((posx * 2000) + winx, (posy * 2000) + winy), 5)
        for index in circleInputs.keys():
            try:
                circle = circleInputs[index]
            except:
                continue
            winx = winScale[0] * circle[0] - 25
            winy = winScale[1] * circle[1] - 25
            if (-50 <= winx <= winScale[0] + 50) and (-50 <= winy <= winScale[1] + 50) and circle[3]:
                input_note.set_alpha(circle[3])
                screen.blit(input_note, (winx, winy))
            if circle[4][1]:
                if circle[4][2]:
                    text = FOCUS_font.render(f"{circle[4][0]}", 0, pg.Color(255, 255, 255, a=circle[4][1]))
                    textrect = text.get_rect()[2:4]
                else:
                    text = font.render(f"{circle[4][0]}", 0, pg.Color(255, 255, 255, a=circle[4][1]))
                    textrect = text.get_rect()[2:4]
                screen.blit(text, (winx + 25 - textrect[0] / 2, winy + 25 - textrect[1] * 2))
            remove_note = []
            pressed = 0
            for note in circle[5]:
                note[1] -= game_tick - old_tick
                x = math.cos(math.pi * circle[2] / 180) * note[1] * 0.001 * note[2] * minBackgroundRatio + winx
                if (-50 >= x) or (x >= winScale[0] + 50):
                    continue
                y = math.sin(math.pi * circle[2] / 180) * note[1] * 0.001 * note[2] * minBackgroundRatio + winy
                if (-50 >= y) or (y >= winScale[1] + 50):
                    continue
                screen.blit(noteType[note[0]], (x, y))
                if note[1] < -100:
                    if auto:
                        circle[5].remove(note)
                        effects.append([winx, winy, 0])
                        pg.mixer.SoundType(file=sfx_list[note[0]]).play()
                        continue
                    else:
                        lines = []
                        circleInputs = []
                        updates = []
                        game_over = 1
                        break
                elif interval[0] <= note[1] <= interval[2]:
                    if auto:
                        circle[5].remove(note)
                        effects.append([winx, winy, 0])
                        # Test if sound aligned
                        if 1:
                            pg.mixer.SoundType(file=sfx_list[note[0]]).play()
                        continue
                    if not pressed:
                        pressed = 1
                    else:
                        continue
                    match note[0]:
                        case 0:
                            if (circle[4][0] in keyPress) and (interval[0] <= note[1] <= interval[1]):
                                circle[5].remove(note)
                                effects.append([winx, winy, 0])
                                pg.mixer.SoundType(file=sfx_list[0]).play()
                                continue
                            elif (circle[4][0] in keyPress) and (interval[1] < note[1] <= interval[2]):
                                lines = []
                                circleInputs = []
                                updates = []
                                game_over = 1
                                break
                        case 1:
                            if (circle[4][0] in keyPressing) and (interval[0] <= note[1] <= 0):
                                circle[5].remove(note)
                                effects.append([winx, winy, 0])
                                pg.mixer.SoundType(file=sfx_list[1]).play()
                                continue
                        case 2:
                            if (circle[4][0] in keyRelease) and (interval[0] <= note[1] <= interval[1]):
                                circle[5].remove(note)
                                effects.append([winx, winy, 0])
                                pg.mixer.SoundType(file=sfx_list[2]).play()
                                continue
                            elif (circle[4][0] in keyRelease) and (interval[1] < note[1] <= interval[2]):
                                lines = []
                                circleInputs = []
                                updates = []
                                game_over = 1
                                break
                        case 3:
                            if (circle[4][0] in keyPressing) and (interval[0] <= note[1] <= 0):
                                lines = []
                                circleInputs = []
                                updates = []
                                game_over = 1
                                break
                            elif interval[0] <= note[0] <= 0:
                                circle[5].remove(note)
                                effects.append([winx, winy, 0])
                                pg.mixer.SoundType(file=sfx_list[3]).play()
                                continue
                        case _:
                            continue
            for note in remove_note:
                circle[5].remove(note)
            for effect in effects:
                d = (effect[2] * 30) // 400 - 1
                hit_rect = hit_list[d].get_rect()[2:4]
                screen.blit(hit_list[d], (effect[0] - hit_rect[0] / 2 + 25, effect[1] - hit_rect[1] / 2 + 25))
        old_tick = game_tick
    elif game_over:
        pg.mixer_music.stop()
        text = FOCUS_font.render("Game Over", 1, (255, 0, 0))
        text_rect = text.get_rect()[2:4]
        screen.blit(text, (winScale[0] / 2 - text_rect[0] / 2, winScale[1] / 2 - text_rect[1] / 2))
    pg.display.flip()
