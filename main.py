import pygame
import os
import math
import random
import sys

# Pygame inicializálása
pygame.init()
pygame.mixer.init()


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# 1. Ablak és Színek
SZEL, MAG = 1400, 900
screen = pygame.display.set_mode((SZEL, MAG))
pygame.display.set_caption("Asteroids - Final Stability Fix")

PIROS, FEHER, SARGA, NARANCS, KEK, SZURKE = (255, 0, 0), (255, 255, 255), (255, 255, 0), (255, 120, 0), (0, 191, 255), (
    50, 50, 50)
font_nagy = pygame.font.SysFont("Arial", 36)
font_giga = pygame.font.SysFont("Arial", 100)


# 2. Erőforrások
def kep_betoltes(fajlnev):
    for kit in ['.jpg', '.jpeg', '.png']:
        ut = resource_path(fajlnev + kit)
        if os.path.exists(ut): return pygame.image.load(ut).convert_alpha()
    s = pygame.Surface((50, 50));
    s.fill((255, 0, 255))
    return s


background = pygame.transform.scale(kep_betoltes('space'), (SZEL, MAG))
meteor_raw = kep_betoltes('meteor')
nyers_raketa = kep_betoltes('rocket')
urhajo_original = pygame.transform.scale(pygame.transform.rotate(nyers_raketa, 40), (60, 60))

# --- ZENE ÉS HANG ---
robbanas_hang = None
ut_boom = resource_path('boom.wav')
if os.path.exists(ut_boom):
    robbanas_hang = pygame.mixer.Sound(ut_boom)
    robbanas_hang.set_volume(0.2)

zene_ut = resource_path('hatterzene.mp3')
if os.path.exists(zene_ut):
    pygame.mixer.music.load(zene_ut)
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1)


# --- FUNKCIÓK ---
def tavolsag(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def uj_meteor(olesek_szama):
    meret = random.randint(50, 90) + min(olesek_szama // 5, 40)
    oldal = random.randint(0, 3)
    if oldal == 0:
        x, y = random.randint(0, SZEL), -meret
    elif oldal == 1:
        x, y = random.randint(0, SZEL), MAG + meret
    elif oldal == 2:
        x, y = -meret, random.randint(0, MAG)
    else:
        x, y = SZEL + meret, random.randint(0, MAG)

    tav = max(tavolsag(x, y, SZEL // 2, MAG // 2), 1)
    seb = random.uniform(1.2, 2.8) * (1.0 + (olesek_szama // 15) * 0.1)

    # Speciális meteor logika javítva
    elet = 1
    szin_mod = (255, 255, 255)
    if olesek_szama >= 60 and random.random() < 0.25:
        elet = 2
        szin_mod = (100, 255, 200)

    kep = pygame.transform.scale(meteor_raw, (meret, meret))
    if elet == 2:
        temp_kep = kep.copy()
        temp_kep.fill(szin_mod, special_flags=pygame.BLEND_RGB_MULT)
        kep = temp_kep

    return {
        'x': x, 'y': y, 'vx': ((SZEL // 2 - x) / tav) * seb, 'vy': ((MAG // 2 - y) / tav) * seb,
        'szog': 0, 'forgas_seb': random.uniform(-2, 2),
        'kep': kep, 'meret': meret, 'elet': elet
    }


def uj_boss(olesek):
    szint = olesek // 20
    hp = 10 + (szint - 1) * 5
    vx, vy = 5.0, 0
    if szint == 2:
        vx, vy = 0, 5.0
    elif szint >= 4:
        vx, vy = 5.0, 5.0
    return {
        'x': SZEL // 2, 'y': 200, 'vx': vx, 'vy': vy, 'szint': szint,
        'meret': 320, 'elet': hp, 'max_elet': hp, 'szog': 0, 'idomeres': 0,
        'kep': pygame.transform.scale(meteor_raw, (320, 320))
    }


def reset_jatek():
    return {
        'x': SZEL // 2, 'y': MAG // 2, 'szog': 0, 'sebesseg': 0,
        'oles_szamlalo': 0, 'eletek': 10, 'game_over': False,
        'lovedekek': [], 'akadalyok': [uj_meteor(0) for _ in range(10)],
        'powerups': [], 'pajzs_aktiv': False, 'utolso_pajzs_ido': -30000,
        'gyorsitas_vege': 0, 'utolso_loves': 0, 'boss': None
    }


jatek = reset_jatek()
clock = pygame.time.Clock()
running = True

while running:
    jelenlegi_ido = pygame.time.get_ticks()
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if jatek['game_over'] and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            jatek = reset_jatek()
        if not jatek['game_over'] and event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if jatek['oles_szamlalo'] >= 50 and (jelenlegi_ido - jatek['utolso_pajzs_ido'] >= 30000):
                jatek['pajzs_aktiv'] = True
                jatek['utolso_pajzs_ido'] = jelenlegi_ido

    if not jatek['game_over']:
        # Tüzelés
        tuz_seb = 80 if jelenlegi_ido < jatek['gyorsitas_vege'] else 160
        if pygame.mouse.get_pressed()[0]:
            if jelenlegi_ido - jatek['utolso_loves'] > tuz_seb:
                if jatek['oles_szamlalo'] < 100:
                    jatek['lovedekek'].append({'x': jatek['x'], 'y': jatek['y'], 'szog': jatek['szog']})
                else:
                    jatek['lovedekek'].append({'x': jatek['x'] - 12, 'y': jatek['y'], 'szog': jatek['szog']})
                    jatek['lovedekek'].append({'x': jatek['x'] + 12, 'y': jatek['y'], 'szog': jatek['szog']})
                jatek['utolso_loves'] = jelenlegi_ido

        # Mozgás
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]: jatek['szog'] += 3
        if keys[pygame.K_d]: jatek['szog'] -= 3
        if keys[pygame.K_w]:
            jatek['sebesseg'] = min(jatek['sebesseg'] + 0.2, 7)
        elif keys[pygame.K_s]:
            jatek['sebesseg'] = max(jatek['sebesseg'] - 0.2, -3)
        else:
            jatek['sebesseg'] *= 0.98

        rad = math.radians(jatek['szog'])
        jatek['x'] = (jatek['x'] - math.sin(rad) * jatek['sebesseg']) % SZEL
        jatek['y'] = (jatek['y'] - math.cos(rad) * jatek['sebesseg']) % MAG

        # Lövedék mozgás
        for l in jatek['lovedekek'][:]:
            l['x'] -= math.sin(math.radians(l['szog'])) * 15
            l['y'] -= math.cos(math.radians(l['szog'])) * 15
            if not (0 < l['x'] < SZEL and 0 < l['y'] < MAG): jatek['lovedekek'].remove(l)

        # Power-up felvétel
        for p in jatek['powerups'][:]:
            if tavolsag(jatek['x'], jatek['y'], p['x'], p['y']) < 40:
                if p['tipus'] == 'elet':
                    jatek['eletek'] += 1
                elif p['tipus'] == 'gyorsitas':
                    jatek['gyorsitas_vege'] = jelenlegi_ido + 10000
                jatek['powerups'].remove(p)
            elif jelenlegi_ido - p['ido'] > 10000:
                jatek['powerups'].remove(p)

        # Meteor és Boss interakciók
        if jatek['boss']:
            b = jatek['boss']
            b['szog'] += 1
            if b['szint'] == 1:
                b['x'] += b['vx']
            elif b['szint'] == 2:
                b['y'] += b['vy']
            elif b['szint'] == 3:
                b['idomeres'] += 0.03
                b['x'] = SZEL // 2 + math.cos(b['idomeres']) * 350
                b['y'] = MAG // 2 + math.sin(b['idomeres']) * 250
            else:
                b['x'] += b['vx']; b['y'] += b['vy']

            if b['x'] < 160 or b['x'] > SZEL - 160: b['vx'] *= -1
            if b['y'] < 160 or b['y'] > MAG - 160: b['vy'] *= -1

            # BOSS SEBZÉS JAVÍTVA
            if tavolsag(jatek['x'], jatek['y'], b['x'], b['y']) < 160:
                if jatek['pajzs_aktiv']:
                    jatek['pajzs_aktiv'] = False
                else:
                    jatek['eletek'] -= 1; jatek['x'], jatek['y'], jatek['sebesseg'] = SZEL // 2, MAG // 2, 0
                if jatek['eletek'] <= 0: jatek['game_over'] = True

            for l in jatek['lovedekek'][:]:
                if tavolsag(l['x'], l['y'], b['x'], b['y']) < 150:
                    b['elet'] -= 1
                    if l in jatek['lovedekek']: jatek['lovedekek'].remove(l)
                    if b['elet'] <= 0:
                        jatek['boss'] = None;
                        jatek['oles_szamlalo'] += 1
                        jatek['akadalyok'] = [uj_meteor(jatek['oles_szamlalo']) for _ in range(10)]
        else:
            for ak in jatek['akadalyok'][:]:
                ak['x'] += ak['vx'];
                ak['y'] += ak['vy'];
                ak['szog'] += ak['forgas_seb']
                # Hajó-Meteor ütközés
                if tavolsag(jatek['x'], jatek['y'], ak['x'], ak['y']) < (ak['meret'] / 2 + 15):
                    if jatek['pajzs_aktiv']:
                        jatek['pajzs_aktiv'] = False
                    else:
                        jatek['eletek'] -= 1; jatek['x'], jatek['y'], jatek['sebesseg'] = SZEL // 2, MAG // 2, 0
                    jatek['akadalyok'].remove(ak);
                    jatek['akadalyok'].append(uj_meteor(jatek['oles_szamlalo']))
                    if jatek['eletek'] <= 0: jatek['game_over'] = True
                    break
                # Lövedék-Meteor ütközés
                for l in jatek['lovedekek'][:]:
                    if tavolsag(l['x'], l['y'], ak['x'], ak['y']) < ak['meret'] / 2:
                        ak['elet'] -= 1
                        if l in jatek['lovedekek']: jatek['lovedekek'].remove(l)
                        if ak['elet'] <= 0:
                            if robbanas_hang: robbanas_hang.play()
                            if random.random() < 0.15: jatek['powerups'].append(
                                {'x': ak['x'], 'y': ak['y'], 'tipus': random.choice(['elet', 'gyorsitas']),
                                 'ido': jelenlegi_ido})
                            jatek['oles_szamlalo'] += 1
                            jatek['akadalyok'].remove(ak);
                            jatek['akadalyok'].append(uj_meteor(jatek['oles_szamlalo']))
                        break

        if jatek['oles_szamlalo'] > 0 and jatek['oles_szamlalo'] % 20 == 0 and jatek['boss'] is None:
            jatek['boss'] = uj_boss(jatek['oles_szamlalo']);
            jatek['akadalyok'].clear()

    # --- RAJZOLÁS ---
    for p in jatek['powerups']:
        szin = PIROS if p['tipus'] == 'elet' else SARGA
        pygame.draw.circle(screen, szin, (int(p['x']), int(p['y'])), 18)
        pygame.draw.circle(screen, FEHER, (int(p['x']), int(p['y'])), 18, 3)

    if jatek['boss']:
        b = jatek['boss']
        screen.blit(pygame.transform.rotate(b['kep'], b['szog']), b['kep'].get_rect(center=(b['x'], b['y'])))
        pygame.draw.rect(screen, PIROS, (b['x'] - 100, b['y'] - 180, (b['elet'] / b['max_elet']) * 200, 15))
    else:
        for ak in jatek['akadalyok']:
            screen.blit(pygame.transform.rotate(ak['kep'], ak['szog']), ak['kep'].get_rect(center=(ak['x'], ak['y'])))

    if not jatek['game_over']:
        for l in jatek['lovedekek']: pygame.draw.circle(screen, SARGA, (int(l['x']), int(l['y'])), 4)
        s_img = pygame.transform.rotate(urhajo_original, jatek['szog'])
        if jatek['pajzs_aktiv']: pygame.draw.circle(screen, KEK, (int(jatek['x']), int(jatek['y'])), 45, 3)
        if jelenlegi_ido < jatek['gyorsitas_vege']: pygame.draw.circle(screen, SARGA,
                                                                       (int(jatek['x']), int(jatek['y'])), 35, 2)
        screen.blit(s_img, s_img.get_rect(center=(jatek['x'], jatek['y'])))

    screen.blit(font_nagy.render(f"Ölések: {jatek['oles_szamlalo']}  Élet: {jatek['eletek']}", True, SARGA), (20, 20))
    if jatek['game_over']: screen.blit(font_giga.render("GAME OVER", True, PIROS), (SZEL // 2 - 250, MAG // 2 - 50))

    pygame.display.flip()
    clock.tick(60)
pygame.quit()
