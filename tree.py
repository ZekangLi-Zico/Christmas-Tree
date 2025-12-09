import math
import random
import pygame

# ================== 全局参数 ==================
WIDTH, HEIGHT = 1600, 900
BLACK = (0, 0, 0)

# 粒子数量
TREE_POINTS   = 50000      # 树更“毛茸茸”
GROUND_POINTS = 4000
STAR_POINTS   = 1200       # 空中小亮点，跟树/地面一起转
HEART_POINTS  = 1000       # 树顶 3D 爱心的小光点
SNOW2D_POINTS = 10          # 前景大雪花

# 相机参数 —— 俯视视角
CAM_DIST   = 13          # 相机离原点的“前后”距离（拉远一点，树不被裁）
CAM_HEIGHT = 6.0           # 相机高度
PITCH      = -0.25         # 负角度 = 俯视

TREE_HEIGHT = 12.0         # 树高度


# ================== 生成圣诞树 ==================
def gen_tree_points():
    pts = []
    loops = 9
    spiral_n = int(TREE_POINTS * 0.7)   # 70% 螺旋灯带，其余填充

    # 70% 螺旋灯带 —— 高度分布偏向下半部分
    for _ in range(spiral_n):
        u = random.random()          # [0,1] 螺旋参数
        h = u ** 1.6                 # <=== 这里：底部密一点，顶部稀一点
        y = TREE_HEIGHT * h + 0.2

        # 基础半径：整体较宽
        base_r = (1 - h) ** 1.1 * 3.2
        # 用正弦做“树枝层次”
        branch_wave = max(0.0, math.sin((h * 5.8 + 0.15) * math.tau))
        branch_factor = 1.0 + 0.65 * branch_wave
        base_r *= branch_factor

        t = u * loops * math.tau
        angle = t + random.uniform(-0.22, 0.22)
        r = base_r * random.uniform(0.85, 1.08)

        x = math.cos(angle) * r
        z = math.sin(angle) * r

        # 中段更亮
        mid_boost = 1.0 - abs(h - 0.55) * 1.5
        mid_boost = max(0.15, mid_boost)
        base_g = 155 + int(90 * mid_boost)
        base_b = 185 + int(70 * mid_boost)

        color = (
            255,
            min(255, base_g + random.randint(-15, 20)),
            min(255, base_b + random.randint(-15, 35)),
        )
        # 点缀更亮的小灯
        if random.random() < 0.08:
            color = (255, 255 - random.randint(0, 35), 230 + random.randint(0, 25))

        pts.append([x, y, z, color])

    # 30% 随机填充，让轮廓更“毛茸茸”
    fill_n = TREE_POINTS - spiral_n
    for _ in range(fill_n):
        # 填充部分再偏向底部一点（指数更大）
        h = random.random() ** 1.9
        # 在树身上下稍微抖一点，填补空隙
        y = TREE_HEIGHT * h + 0.2 + random.uniform(-0.08, 0.08)

        base_r = (1 - h) ** 1.1 * 4.3
        branch_wave = max(0.0, math.sin((h * 5.8 + 0.15) * math.tau))
        branch_factor = 1.0 + 0.65 * branch_wave
        base_r *= branch_factor

        # 半径仍然偏外圈，营造蓬松边缘
        r = base_r * math.sqrt(random.random())
        angle = random.random() * math.tau

        x = math.cos(angle) * r + random.uniform(-0.08, 0.08)
        z = math.sin(angle) * r + random.uniform(-0.08, 0.08)

        g = random.randint(165, 225)
        b = random.randint(190, 250)
        color = (255, g, b)
        pts.append([x, y, z, color])

    return pts


# ================== 地面光环（法阵盘子） ==================
def gen_ground_points():
    pts = []
    rings = [4.6, 6.0, 7.4, 8.8, 10.2, 11.4]
    for _ in range(GROUND_POINTS):
        ring = random.choice(rings)
        r = random.gauss(ring, 0.3)
        theta = random.random() * math.tau
        x = math.cos(theta) * r
        z = math.sin(theta) * r
        y = -0.25

        if random.random() < 0.15:
            c = random.randint(235, 255)
        else:
            c = random.randint(190, 235)
        color = (c, c, 255)
        pts.append([x, y, z, color])
    return pts


# ================== 空中 3D 小亮点（随场景旋转） ==================
def gen_star_points():
    pts = []
    for _ in range(STAR_POINTS):
        x = random.uniform(-18.0, 18.0)
        z = random.uniform(-18.0, 18.0)
        y = random.uniform(3.0, 18.0)
        base = random.randint(215, 255)
        color = (base, base, 255)
        pts.append([x, y, z, color])
    return pts


# ================== 树顶 3D 爱心（2D 心形 + 小厚度） ==================
def gen_heart_points():
    """
    先用 2D 心形隐式方程：
        (x^2 + y^2 - 1)^3 - x^2 * y^3 <= 0
    在平面上采样点，再加一点 z 抖动，放在树顶上方。
    """
    pts = []
    scale = 0.9
    top_y = TREE_HEIGHT + 0.05   # 心尖大致在 TREE_HEIGHT 附近

    while len(pts) < HEART_POINTS:
        x = random.uniform(-1.3, 1.3)
        y = random.uniform(-1.4, 1.4)

        f = (x * x + y * y - 1.0) ** 3 - x * x * (y ** 3)

        if f <= 0.0:
            wx = x * scale * 0.8
            wy = top_y + (y + 1.0) * scale * 0.5
            wz = random.uniform(-0.18, 0.18)

            dist = math.hypot(x, y)
            factor = max(0.35, 1.15 - 0.5 * dist)
            r = 255
            g = int(130 * factor + 80)
            b = int(190 * factor + 70)
            g = max(120, min(255, g))
            b = max(120, min(255, b))

            pts.append([wx, wy, wz, (r, g, b)])

    return pts


# ================== 前景 2D 大雪花（亮、贴屏、数量≤8） ==================
def init_snow2d():
    flakes = []
    for _ in range(SNOW2D_POINTS):
        x = random.uniform(0, WIDTH)
        y = random.uniform(-80, -10)
        radius = random.uniform(10.0, 16.0)
        speed = random.uniform(30.0, 45.0)
        travel = HEIGHT + 80 - y
        life = travel / speed
        max_life = life
        flakes.append([x, y, radius, speed, life, max_life])
    return flakes


def respawn_flake(f):
    x = random.uniform(0, WIDTH)
    y = random.uniform(-80, -10)
    radius = random.uniform(10.0, 16.0)
    speed = random.uniform(30.0, 45.0)
    travel = HEIGHT + 80 - y
    life = travel / speed
    max_life = life
    f[0], f[1], f[2], f[3], f[4], f[5] = x, y, radius, speed, life, max_life


def update_snow2d(flakes, dt):
    for f in flakes:
        x, y, r, v, life, max_life = f
        y += v * dt
        life -= dt
        if life <= 0 or y > HEIGHT + 50:
            respawn_flake(f)
        else:
            f[0], f[1], f[4] = x, y, life


def draw_snow2d(surface, flakes):
    surface.fill((0, 0, 0, 0))
    for x, y, r, v, life, max_life in flakes:
        if max_life <= 0:
            continue

        phase = life / max_life
        if phase > 0.3:
            alpha = 255
        else:
            alpha = int(255 * (phase / 0.3))
        alpha = max(0, min(255, alpha))

        cx, cy = int(x), int(y)

        r1 = max(1, int(r * 1.3))
        r2 = max(1, int(r * 1.0))
        r3 = max(1, int(r * 0.75))
        r4 = max(1, int(r * 0.55))
        r5 = max(1, int(r * 0.45))

        a1 = alpha // 20
        a2 = alpha // 12
        a3 = alpha // 6
        a4 = alpha // 3
        a5 = alpha

        if a1 > 0:
            pygame.draw.circle(surface, (255, 255, 255, a1), (cx, cy), r1)
        if a2 > 0:
            pygame.draw.circle(surface, (255, 255, 255, a2), (cx, cy), r2)
        if a3 > 0:
            pygame.draw.circle(surface, (255, 255, 255, a3), (cx, cy), r3)
        if a4 > 0:
            pygame.draw.circle(surface, (255, 255, 255, a4), (cx, cy), r4)

        pygame.draw.circle(surface, (255, 255, 255, a5), (cx, cy), r5)


# ================== 3D -> 2D 投影（俯视） ==================
def project_point(x, y, z, angle):
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    xz = x * cos_a - z * sin_a
    zz = x * sin_a + z * cos_a

    cos_p = math.cos(PITCH)
    sin_p = math.sin(PITCH)
    yp = y * cos_p - zz * sin_p
    zp = y * sin_p + zz * cos_p

    zp = zp + CAM_DIST
    yp = yp - CAM_HEIGHT

    if zp <= 0.1:
        return None

    f = (HEIGHT * 0.63) / zp
    sx = int(WIDTH / 2 + xz * f)
    sy = int(HEIGHT / 2 - yp * f)
    depth = zp
    return sx, sy, depth


# ================== 主循环 ==================
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Merry Christmas")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Monotype Corsiva", 45, bold=False)

    tree = gen_tree_points()
    ground = gen_ground_points()
    stars = gen_star_points()
    heart = gen_heart_points()
    snow2d = init_snow2d()
    snow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    angle = 0.0
    running = True

    while running:
        dt_ms = clock.tick(60)
        dt = dt_ms / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BLACK)

        update_snow2d(snow2d, dt)

        draw_list = []
        for x, y, z, color in tree + ground + stars + heart:
            proj = project_point(x, y, z, angle)
            if proj:
                sx, sy, depth = proj
                size = max(1, int(3.6 - depth * 0.13))
                draw_list.append((depth, sx, sy, size, color))

        draw_list.sort(key=lambda v: v[0], reverse=True)
        for _, sx, sy, size, color in draw_list:
            if 0 <= sx < WIDTH and 0 <= sy < HEIGHT:
                pygame.draw.circle(screen, color, (sx, sy), size)

        text1 = font.render("Merry Christmas", True, (255, 255, 255))
        screen.blit(text1, (40, HEIGHT // 3))

        text2 = font.render("647", True, (255, 255, 255))
        screen.blit(text2, (40, HEIGHT // 3 + text1.get_height() + 10))

        draw_snow2d(snow_surface, snow2d)
        screen.blit(snow_surface, (0, 0))

        pygame.display.flip()
        angle += 0.0045

    pygame.quit()


if __name__ == "__main__":
    main()
