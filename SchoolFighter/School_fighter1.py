import os
import random
import sys
import pygame

# ---------------- Constants ----------------
SCREEN_WIDTH, SCREEN_HEIGHT = 960, 540
FPS = 60
GRAVITY = 1
ATTACK_DURATION_FRAMES = int(0.3 * FPS)  # ~0.3s at 60FPS
PROJECTILE_SPEED = 10
MOVE_SPEED = int(round(5 * 1.4))  # +40% player speed
BOT_SPEED = int(round(3 * 1.4))   # +40% bot speed

IMG_PATH = "img"
SPRITES_PATH = "sprites"
SOUND_PATH = "sound"

BACKGROUND_IMAGES = [
    "classroom.jpg",
    "playground.jpg",
    "corridors.jpg",
    "cafeteria.jpg",
]

# Controls
CONTROLS = {
    "player1": {
        "left": pygame.K_q,
        "right": pygame.K_d,
        "jump": pygame.K_z,
        "punch": pygame.K_f,
        "kick": pygame.K_g,
        "special": pygame.K_h,
        "block": pygame.K_s,
    },
    "player2": {
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "jump": pygame.K_UP,
        "punch": pygame.K_k,
        "kick": pygame.K_l,
        "special": pygame.K_m,
        "block": pygame.K_DOWN,
    },
}

# ---------------- Audio Manager ----------------
class AudioManager:
    def __init__(self, sound_dir: str, music_file: str, sfx_volume: float = 0.8, music_volume: float = 0.6):
        self.sound_dir = sound_dir
        self.music_file = music_file
        self._music_volume = max(0.0, min(1.0, music_volume))
        self._muted = False
        self.sfx = {}
        self._load_effects()
        self._load_music()

    def _load_effects(self):
        mapping = {
            "punch": "punch.wav",
            "kick": "kick.wav",
            "special": "special.wav",
            "block": "block.wav",
        }
        for name, file in mapping.items():
            path = os.path.join(self.sound_dir, file)
            if os.path.exists(path):
                try:
                    snd = pygame.mixer.Sound(path)
                    snd.set_volume(0.8)
                    self.sfx[name] = snd
                except Exception:
                    pass

    def _load_music(self):
        try:
            if os.path.exists(self.music_file):
                pygame.mixer.music.load(self.music_file)
                pygame.mixer.music.set_volume(self._music_volume if not self._muted else 0.0)
        except Exception:
            pass

    def play_music(self, loop: int = -1):
        try:
            pygame.mixer.music.play(loop)
        except Exception:
            pass

    def toggle_mute(self):
        self._muted = not self._muted
        try:
            pygame.mixer.music.set_volume(0.0 if self._muted else self._music_volume)
        except Exception:
            pass

    def set_music_volume(self, v: float):
        self._music_volume = max(0.0, min(1.0, v))
        if not self._muted:
            try:
                pygame.mixer.music.set_volume(self._music_volume)
            except Exception:
                pass

    def adjust_music_volume(self, delta: float):
        self.set_music_volume(self._music_volume + delta)

    def play_sfx(self, name: str):
        snd = self.sfx.get(name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass


audio_manager: AudioManager | None = None

# ---------------- Helpers ----------------

def load_image(path: str) -> pygame.Surface:
    return pygame.image.load(path).convert_alpha()


def scale_to_height(img: pygame.Surface, target_h: int) -> pygame.Surface:
    w, h = img.get_size()
    scale = target_h / float(h)
    new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
    return pygame.transform.smoothscale(img, new_size)


def draw_text(surface, text, size, x, y, color=(255, 255, 255)):
    font = pygame.font.SysFont("arial", size)
    txt = font.render(text, True, color)
    surface.blit(txt, (x, y))


def draw_health_bar(surface, x, y, health):
    health = max(0, min(100, int(health)))
    pygame.draw.rect(surface, (255, 0, 0), (x, y, 200, 20))
    pygame.draw.rect(surface, (0, 255, 0), (x, y, 2 * health, 20))


# ---------------- Sprites Loading ----------------

def load_sprites() -> dict:
    def frames(prefix: str, action: str, idx=None, single=False):
        out = []
        if single:
            p = os.path.join(SPRITES_PATH, f"{prefix}_{action}.png")
            if os.path.exists(p):
                out.append(load_image(p))
        else:
            for i in (idx or []):
                p = os.path.join(SPRITES_PATH, f"{prefix}_{action}{i}.png")
                if os.path.exists(p):
                    out.append(load_image(p))
        return out if out else [pygame.Surface((64, 64), pygame.SRCALPHA)]

    target_h = 140  # reduce size to fit gameplay

    def build(prefix: str):
        data = {
            "idle": frames(prefix, "idle", single=True),
            "walk": frames(prefix, "walk", idx=[0, 1, 2]),
            "jump": frames(prefix, "jump", single=True),
            "punch": frames(prefix, "punch", idx=[0, 1, 2]),
            "kick": frames(prefix, "kick", idx=[0, 1, 2]),
            # special now explicitly uses 4 frames 0..3
            "special": frames(prefix, "special", idx=[0, 1, 2, 3]),
            "block": frames(prefix, "block", single=True),
        }
        # scale
        for k in list(data.keys()):
            data[k] = [scale_to_height(img, target_h) for img in data[k]]
        return data

    return {
        "player1": build("player1"),
        # If player2 sprites don't exist, fallback to player1 assets
        "player2": build("player2") if os.path.exists(os.path.join(SPRITES_PATH, "player2_idle.png")) else build("player1"),
    }


# ---------------- Projectile ----------------
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction: int, kind: str):
        super().__init__()
        self.kind = kind
        img_file = "fireball.png" if kind == "fireball" else "lightning.png"
        path = os.path.join(SPRITES_PATH, img_file)
        if os.path.exists(path):
            img = load_image(path)
        else:
            img = pygame.Surface((32, 16), pygame.SRCALPHA)
            pygame.draw.circle(img, (255, 140, 0) if kind == "fireball" else (150, 200, 255), (16, 8), 8)
        # Enlarge special projectiles by 4x compared to previous height
        self.image = scale_to_height(img, 40 * 4)
        self.rect = self.image.get_rect(center=(x, y))
        self.vx = PROJECTILE_SPEED * direction

    def update(self):
        self.rect.x += self.vx
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

    def get_hitbox(self) -> pygame.Rect:
        # Return a reduced hitbox (1/3 width and height), centered on projectile
        hb = self.rect.copy()
        new_w = max(1, hb.width // 3)
        new_h = max(1, hb.height // 3)
        hb.x += (hb.width - new_w) // 2
        hb.y += (hb.height - new_h) // 2
        hb.width = new_w
        hb.height = new_h
        return hb


# ---------------- Player ----------------
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, controls, sprites, facing_right=True, is_p1=True):
        super().__init__()
        self.controls = controls
        self.sprites = sprites
        self.state = "idle"
        self.image = self.sprites["idle"][0]
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.facing_right = facing_right
        self.vel_y = 0
        self.on_ground = True
        self.health = 100
        self.blocking = False
        self.attack_cooldown = 0
        self.attack_frames_left = 0
        self.projectiles = pygame.sprite.Group()
        self.is_p1 = is_p1
        # double jump
        self.max_jumps = 2
        self.jumps_used = 0
        self.jump_was_down = False
        # delayed projectile spawn for specials
        self.pending_projectile_frames = 0

    def get_hurtbox(self) -> pygame.Rect:
        hb = self.rect.copy()
        new_w = hb.width // 2
        hb.x += (hb.width - new_w) // 2
        hb.width = new_w
        return hb

    def update(self, keys, opponent):
        # projectiles
        self.projectiles.update()

        # movement disabled during attack execution window
        moving = False
        if self.attack_frames_left <= 0:
            if keys[self.controls["left"]]:
                self.rect.x -= MOVE_SPEED
                self.facing_right = False
                self.state = "walk"
                moving = True
            if keys[self.controls["right"]]:
                self.rect.x += MOVE_SPEED
                self.facing_right = True
                self.state = "walk"
                moving = True

        # jump
        jump_now = keys[self.controls["jump"]]
        if jump_now and not self.jump_was_down:
            # allow double jump (max 2 jumps before touching ground again)
            if self.jumps_used < self.max_jumps and self.attack_frames_left <= 0:
                self.vel_y = -15
                self.on_ground = False
                self.state = "jump"
                self.jumps_used += 1
        # update jump edge flag
        self.jump_was_down = jump_now

        # attacks
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.attack_frames_left > 0:
            self.attack_frames_left -= 1
        # handle delayed projectile spawn irrespective of special state
        if self.pending_projectile_frames > 0:
            self.pending_projectile_frames -= 1
            if self.pending_projectile_frames == 0:
                self.spawn_projectile_now()

        if self.attack_frames_left <= 0 and self.attack_cooldown == 0:
            if keys[self.controls["punch"]]:
                self.state = "punch"
                self.attack_frames_left = ATTACK_DURATION_FRAMES
                self.attack_cooldown = 10
                if audio_manager: audio_manager.play_sfx("punch")
                self.melee_attack(opponent, 10)
            elif keys[self.controls["kick"]]:
                self.state = "kick"
                self.attack_frames_left = ATTACK_DURATION_FRAMES
                self.attack_cooldown = 10
                if audio_manager: audio_manager.play_sfx("kick")
                self.melee_attack(opponent, 15)
            elif keys[self.controls["special"]]:
                self.state = "special"
                self.attack_frames_left = ATTACK_DURATION_FRAMES
                self.attack_cooldown = 30
                # delay projectile launch by 0.5s
                self.pending_projectile_frames = int(0.5 * FPS)
                if audio_manager: audio_manager.play_sfx("special")

        # when an attack animation ends, return to idle sprite
        if self.attack_frames_left == 0 and self.state in ("punch", "kick", "special") and not self.blocking:
            # If special still waiting to spawn, keep special pose until spawn, then reset in spawn_projectile_now
            if not (self.state == "special" and self.pending_projectile_frames > 0):
                # reset to idle if not moving/jumping
                if self.on_ground and not (keys[self.controls["left"]] or keys[self.controls["right"]]):
                    self.state = "idle"

        # blocking
        self.blocking = keys[self.controls["block"]]
        if self.blocking:
            self.state = "block"

        # gravity
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        if self.rect.bottom >= SCREEN_HEIGHT - 50:
            self.rect.bottom = SCREEN_HEIGHT - 50
            self.vel_y = 0
            self.on_ground = True
            self.jumps_used = 0  # reset double jump when touching ground

        # screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

        # animation (cycle special frames over its duration)
        self.animate()

    def melee_attack(self, opponent, damage):
        hitbox = self.get_hurtbox()  # narrower width
        if hitbox.colliderect(opponent.get_hurtbox()):
            if not opponent.blocking:
                opponent.health = max(0, opponent.health - damage)
            else:
                opponent.health = max(0, opponent.health - damage // 4)
                if audio_manager: audio_manager.play_sfx("block")

    def shoot_projectile(self):
        kind = "fireball" if self.is_p1 else "lightning"
        direction = 1 if self.facing_right else -1
        start_x = self.rect.centerx + (self.rect.width // 2 * direction)
        start_y = self.rect.centery - 20
        self.projectiles.add(Projectile(start_x, start_y, direction, kind))

    def spawn_projectile_now(self):
        # spawn using current facing/origin
        self.shoot_projectile()
        # reset sprite to starting sprite once projectile launched
        self.attack_frames_left = 0
        self.state = "idle"

    def animate(self):
        prev = self.rect.midbottom
        frames = self.sprites.get(self.state, self.sprites["idle"]) or self.sprites["idle"]
        # For special, step through frames proportional to elapsed time
        if self.state == "special" and len(frames) > 1 and ATTACK_DURATION_FRAMES > 0:
            elapsed = ATTACK_DURATION_FRAMES - max(0, self.attack_frames_left)
            frame_index = min(len(frames) - 1, int(elapsed / ATTACK_DURATION_FRAMES * len(frames)))
            img = frames[frame_index]
        else:
            img = frames[0]
        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)
        self.image = img
        self.rect = self.image.get_rect(midbottom=prev)

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)
        # draw projectiles
        self.projectiles.draw(surface)


class Bot(Player):
    def update(self, keys, opponent):
        # simple AI follow and random attack
        if opponent.rect.x < self.rect.x:
            self.rect.x -= BOT_SPEED
            self.facing_right = False
        elif opponent.rect.x > self.rect.x:
            self.rect.x += BOT_SPEED
            self.facing_right = True

        if random.randint(0, 60) == 0 and self.attack_cooldown == 0 and self.attack_frames_left <= 0:
            choice = random.choice(["punch", "kick", "special"])
            if choice == "punch":
                self.state = "punch"; self.attack_frames_left = ATTACK_DURATION_FRAMES; self.attack_cooldown = 10
                self.melee_attack(opponent, 10)
                if audio_manager: audio_manager.play_sfx("punch")
            elif choice == "kick":
                self.state = "kick"; self.attack_frames_left = ATTACK_DURATION_FRAMES; self.attack_cooldown = 10
                self.melee_attack(opponent, 15)
                if audio_manager: audio_manager.play_sfx("kick")
            else:
                self.state = "special"; self.attack_frames_left = ATTACK_DURATION_FRAMES; self.attack_cooldown = 30
                # delay projectile like players
                self.pending_projectile_frames = int(0.5 * FPS)
                if audio_manager: audio_manager.play_sfx("special")

        # gravity and bounds via parent
        super().update(keys, opponent)


# ---------------- UI Screens ----------------

def main_menu(screen):
    menu_options = ["Single Player", "Two Players", "Instructions", "Settings", "Exit"]
    selected = 0
    clock = pygame.time.Clock()
    while True:
        screen.fill((30, 30, 60))
        draw_text(screen, "School Fighter", 60, 320, 80, (255, 255, 0))
        for i, option in enumerate(menu_options):
            color = (255, 255, 255) if i != selected else (0, 255, 0)
            draw_text(screen, option, 40, 360, 200 + i * 60, color)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    if selected == 0:
                        return "single"
                    elif selected == 1:
                        return "two"
                    elif selected == 2:
                        instructions_screen(screen)
                    elif selected == 3:
                        settings_screen(screen)
                    elif selected == 4:
                        pygame.quit(); sys.exit()
        clock.tick(30)


def instructions_screen(screen):
    screen.fill((20, 20, 40))
    draw_text(screen, "Instructions", 50, 350, 50)
    draw_text(screen, "Player 1:", 30, 100, 120)
    draw_text(screen, "Q/D: Gauche/Droite | Z: Saut | F: Poing | G: Pied | H: Spécial | S: Blocage", 25, 100, 160)
    draw_text(screen, "Player 2:", 30, 100, 220)
    draw_text(screen, "←/→: Gauche/Droite | ↑: Saut | K: Poing | L: Pied | M: Spécial | ↓: Blocage", 25, 100, 260)
    draw_text(screen, "M: Mute musique | +/-: Volume musique | Entrée: Retour", 22, 250, 320, (200, 200, 200))
    draw_text(screen, "Appuyez sur une touche pour revenir au menu.", 25, 250, 400)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False


def settings_screen(screen):
    options = ["Mute Music", "Adjust Music Volume", "Back"]
    selected = 0
    clock = pygame.time.Clock()
    while True:
        screen.fill((10, 10, 30))
        draw_text(screen, "Settings", 50, 380, 60, (255, 255, 0))
        mute_on = (audio_manager._muted if audio_manager else False)

        vol_percent = int((audio_manager._music_volume if audio_manager else 0.6) * 100)
        labels = [
            f"Mute Music: {'On' if mute_on else 'Off'}",
            f"Music Volume: {vol_percent}%",
            "Back",
        ]
        for i, label in enumerate(labels):
            color = (255, 255, 255) if i != selected else (0, 255, 0)
            draw_text(screen, label, 36, 360, 180 + i * 60, color)
        draw_text(screen, "←/→ pour régler le volume, Entrée pour valider", 22, 250, 380, (200, 200, 200))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_LEFT and selected == 1 and audio_manager:
                    audio_manager.adjust_music_volume(-0.05)
                elif event.key == pygame.K_RIGHT and selected == 1 and audio_manager:
                    audio_manager.adjust_music_volume(0.05)
                elif event.key == pygame.K_RETURN:
                    if selected == 0 and audio_manager:
                        audio_manager.toggle_mute()
                    elif selected == 2:
                        return
        clock.tick(30)


# ---------------- Game Loop ----------------

def game_loop(screen, mode):
    bg_path = os.path.join(IMG_PATH, random.choice(BACKGROUND_IMAGES))
    bg_img = pygame.image.load(bg_path).convert()
    background = pygame.transform.smoothscale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

    sprites = load_sprites()
    p1 = Player(200, SCREEN_HEIGHT - 50, CONTROLS["player1"], sprites["player1"], True, is_p1=True)
    if mode == "single":
        p2 = Bot(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 50, CONTROLS["player2"], sprites["player2"], False, is_p1=False)
    else:
        p2 = Player(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 50, CONTROLS["player2"], sprites["player2"], False, is_p1=False)

    clock = pygame.time.Clock()
    running = True
    # stop menu music when fight starts
    if audio_manager:
        pygame.mixer.music.stop()
    while running:
        screen.blit(background, (0, 0))
        keys = pygame.key.get_pressed()

        p1.update(keys, p2)
        p2.update(keys, p1)

        # draw
        p1.draw(screen)
        p2.draw(screen)

        # projectiles collisions
        for proj in list(p1.projectiles):
            if proj.get_hitbox().colliderect(p2.get_hurtbox()):
                p2.health = max(0, p2.health - 20)
                proj.kill()
        for proj in list(p2.projectiles):
            if proj.get_hitbox().colliderect(p1.get_hurtbox()):
                p1.health = max(0, p1.health - 20)
                proj.kill()

        draw_health_bar(screen, 50, 30, p1.health)
        draw_health_bar(screen, SCREEN_WIDTH - 250, 30, p2.health)

        if p1.health <= 0 or p2.health <= 0:
            winner = "Joueur 1" if p2.health <= 0 else "Joueur 2"
            draw_text(screen, f"{winner} a gagné !", 50, 350, 250, (255, 0, 0))
            pygame.display.flip()
            pygame.time.wait(2000)
            running = False

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN and audio_manager:
                if event.key == pygame.K_m:
                    audio_manager.toggle_mute()
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                    audio_manager.adjust_music_volume(0.05)
                elif event.key in (pygame.K_MINUS, pygame.K_UNDERSCORE):
                    audio_manager.adjust_music_volume(-0.05)

        clock.tick(FPS)


# ---------------- Main ----------------

def main():
    pygame.init()
    try:
        pygame.mixer.init()
    except Exception:
        pass

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("School Fighter")

    global audio_manager
    audio_manager = AudioManager(SOUND_PATH, os.path.join(SOUND_PATH, "background_music.mp3"))
    # Play background music only in menus
    audio_manager.play_music(-1)

    while True:
        mode = main_menu(screen)
        # stop music before entering the fight loop (safety)
        if audio_manager:
            pygame.mixer.music.stop()
        game_loop(screen, mode)
        # when returning to menu, resume music
        if audio_manager:
            audio_manager.play_music(-1)


if __name__ == "__main__":
    main()