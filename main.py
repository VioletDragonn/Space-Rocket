import pygame
import os
import math
import random
import sys

# Pygame inicializálása
pygame.init()
pygame.mixer.init()


# --- EXE KOMPATIBILITÁS ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# 1. Ablak beállítása
SZEL, MAG = 1400, 900
screen = pygame.display.set_mode((SZEL, MAG))
pygame.display.set_caption("Asteroids - Ultimate Hydra Edition")

# Színek és Fontok
PIROS, FEHER, SARGA, NARANCS, KEK = (255, 0, 0), (255, 255, 255), (255, 255, 0), (255, 120, 0), (0, 191, 255)
font_nagy = pygame.font.SysFont("Arial", 36)
font_giga = pygame.font.SysFont("Arial", 100)


# 2. Képek és Hangok betöltése
def kep_betoltes(fajlnev):
    for kit in ['.jpg', '.jpeg', '.png', '.jpeg.jpeg', '.png.png']:
        ut = resource_path(fajlnev + kit)
        if os.path.exists(ut): return pygame.image.load(ut)
    s = pygame.Surface((50, 50));
    s.fill((255, 0, 255));
    return s


def hang_betoltes(fajlnev):
    for kit in ['.wav', '.mp3']:
        ut = resource_path(fajlnev + kit)
        if os.path.exists(ut): return pygame.mixer.Sound(ut)
    return None


# Fájlok beolvasása
background = pygame.transform.scale(kep_betoltes('space'), (SZEL, MAG))
meteor_raw = kep_betoltes('meteor').convert_alpha()

# --- RAKÉTA FIXÁLÁSA (40 fok) ---
nyers_raketa = kep_betoltes('rocket').convert_alpha()
talpra_allitott = pygame.transform.rotate(nyers_raketa, 40)
urhajo_original = pygame.transform.scale(talpra_allitott, (60, 60))

# --- HANGOK ---
robbanas_hang = hang_betoltes('boom')
if robbanas_hang: robbanas_hang.set_volume(0.2)
zene_ut = resource_path('hatterzene.mp3')
if os.path.exists(zene_ut):
    pygame.mixer.music.load(zene_ut)
    pygame.mixer.music.set_volume(0.6)
    pygame.mixer.music.play(-1)


# --- JÁTÉK LOGIKA ---
def tavolsag(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def uj_meteor(olesek_szama):
    meret = random.randint(50, 90) + min(olesek_szama // 5, 40)
    sebesseg_szorzo = 1.0 + (olesek_szama // 15) * 0.1
    kaosz = (olesek_szama // 20) * 0.4
    oldal = random.randint(0, 3)
    if oldal == 0:
        x, y = random.randint(0, SZEL), -meret
    elif oldal == 1:
        x, y = random.randint(0, SZEL), MAG + meret
    elif oldal == 2:
        x, y = -meret, random.randint(0, MAG)
    else:
        x, y = SZEL + meret, random.randint(0, MAG)
    irany_x, irany_y = SZEL // 2 - x, MAG // 2 - y
    tav = max(tavolsag(x, y, SZEL // 2, MAG // 2), 1)
    seb = random.uniform(1.2, 2.8) * sebesseg_szorzo
    return {
        'x': x, 'y': y, 'vx': (irany_x / tav) * seb + random.uniform(-kaosz, kaosz),
        'vy': (irany_y / tav) * seb + random.uniform(-kaosz, kaosz),
        'szog': 0, 'forgas_seb': random.uniform(-2, 2) * sebesseg_szorzo,
        'kep': pygame.transform.scale(meteor_raw, (meret, meret)), 'meret': meret
    }


def reset_jatek():
    return {
        'x': SZEL // 2, 'y': MAG // 2, 'szog': 0, 'sebesseg': 0,
        'oles_szamlalo': 0, 'eletek': 10, 'game_over': False,
        'lovedekek': [], 'akadalyok': [uj_meteor(0) for _ in range(10)],
        'pajzs_aktiv': False, 'utolso_pajzs_ido': -30000
    }


jatek = reset_jatek()
clock = pygame.time.Clock()

# --- FŐ CIKLUS ---
running = True
while running:
    jelenlegi_ido = pygame.time.get_ticks()
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

        if not jatek['game_over']:
            # BAL KLIKK: Lövés
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                jatek['lovedekek'].append([jatek['x'], jatek['y'], jatek['szog']])
                if jatek['oles_szamlalo'] >= 100:
                    jatek['lovedekek'].append([jatek['x'] + 10, jatek['y'] + 10, jatek['szog']])

            # JOBB KLIKK: Pajzs (50 felett, 30mp cooldown)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                if jatek['oles_szamlalo'] >= 50 and (jelenlegi_ido - jatek['utolso_pajzs_ido'] >= 30000):
                    jatek['pajzs_aktiv'] = True
                    jatek['utolso_pajzs_ido'] = jelenlegi_ido

        if jatek['game_over'] and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            jatek = reset_jatek()

    if not jatek['game_over']:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]: jatek['szog'] += 5
        if keys[pygame.K_d]: jatek['szog'] -= 5
        if keys[pygame.K_w]:
            jatek['sebesseg'] = min(jatek['sebesseg'] + 0.2, 7)
        elif keys[pygame.K_s]:
            jatek['sebesseg'] = max(jatek['sebesseg'] - 0.2, -3)
        else:
            jatek['sebesseg'] *= 0.98

        rad = math.radians(jatek['szog'])
        jatek['x'] = (jatek['x'] - math.sin(rad) * jatek['sebesseg']) % SZEL
        jatek['y'] = (jatek['y'] - math.cos(rad) * jatek['sebesseg']) % MAG

        # Lövedékek
        for l in jatek['lovedekek'][:]:
            l[0] -= math.sin(math.radians(l[2])) * 15
            l[1] -= math.cos(math.radians(l[2])) * 15
            if l[0] < 0 or l[0] > SZEL or l[1] < 0 or l[1] > MAG:
                if l in jatek['lovedekek']: jatek['lovedekek'].remove(l)
                continue
            for ak in jatek['akadalyok'][:]:
                if tavolsag(l[0], l[1], ak['x'], ak['y']) < (ak['meret'] / 2 + 10):
                    if robbanas_hang: robbanas_hang.play()
                    jatek['akadalyok'].remove(ak)
                    jatek['oles_szamlalo'] += 1
                    # HIDRA LOGIKA: Minden 3. ölés után +1 meteor
                    jatek['akadalyok'].append(uj_meteor(jatek['oles_szamlalo']))
                    if jatek['oles_szamlalo'] % 3 == 0:
                        jatek['akadalyok'].append(uj_meteor(jatek['oles_szamlalo']))
                    if l in jatek['lovedekek']: jatek['lovedekek'].remove(l)
                    break

        # Meteorok
        for ak in jatek['akadalyok'][:]:
            ak['x'] += ak['vx'];
            ak['y'] += ak['vy'];
            ak['szog'] += ak['forgas_seb']
            if ak['x'] < -400 or ak['x'] > SZEL + 400 or ak['y'] < -400 or ak['y'] > MAG + 400:
                jatek['akadalyok'].remove(ak)
                jatek['akadalyok'].append(uj_meteor(jatek['oles_szamlalo']))
                continue
            if tavolsag(jatek['x'], jatek['y'], ak['x'], ak['y']) < (ak['meret'] / 2 + 20):
                if jatek['pajzs_aktiv']:
                    jatek['pajzs_aktiv'] = False
                else:
                    jatek['eletek'] -= 1
                    jatek['x'], jatek['y'], jatek['sebesseg'] = SZEL // 2, MAG // 2, 0
                jatek['akadalyok'].remove(ak)
                jatek['akadalyok'].append(uj_meteor(jatek['oles_szamlalo']))
                if jatek['eletek'] <= 0: jatek['game_over'] = True
                break

    # Rajzolás
    for ak in jatek['akadalyok']:
        m_img = pygame.transform.rotate(ak['kep'], ak['szog'])
        screen.blit(m_img, m_img.get_rect(center=(ak['x'], ak['y'])).topleft)

    if not jatek['game_over']:
        for l in jatek['lovedekek']:
            pygame.draw.circle(screen, NARANCS if jatek['oles_szamlalo'] >= 100 else SARGA, (int(l[0]), int(l[1])), 4)
        s_img = pygame.transform.rotate(urhajo_original, jatek['szog'])
        # FEHÉR KONTÚR PAJZS
        if jatek['pajzs_aktiv']: pygame.draw.circle(screen, FEHER, (int(jatek['x']), int(jatek['y'])), 38, 2)
        screen.blit(s_img, s_img.get_rect(center=(jatek['x'], jatek['y'])).topleft)
    else:
        screen.blit(font_giga.render("GAME OVER", True, PIROS), (SZEL // 2 - 250, MAG // 2 - 50))
        screen.blit(font_nagy.render("Nyomj 'R'-t az újraindításhoz", True, FEHER), (SZEL // 2 - 180, MAG // 2 + 60))

    # UI Megjelenítés
    screen.blit(font_nagy.render(
        f"Ölések: {jatek['oles_szamlalo']}  Életek: {jatek['eletek']}  Meteorok: {len(jatek['akadalyok'])}", True,
        SARGA), (20, 20))

    # PAJZS SZÁMLÁLÓ UI
    hatralevo = max(0, (30000 - (jelenlegi_ido - jatek['utolso_pajzs_ido'])) // 1000)
    if jatek['oles_szamlalo'] >= 50:
        p_szoveg = "PAJZS KÉSZ!" if hatralevo == 0 else f"Pajzs töltődik: {hatralevo}s"
        p_szin = FEHER if hatralevo == 0 else KEK
        screen.blit(font_nagy.render(p_szoveg, True, p_szin), (20, 70))

    pygame.display.flip()
    clock.tick(60)
pygame.quit()