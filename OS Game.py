import pygame, sys, random

WIDTH, HEIGHT = 1024, 803
FPS = 60
MAX_WAIT = 10
TOTAL_TIME = 75
WHITE, BLACK = (255,255,255), (0,0,0)
GREEN, RED, BLUE, GRAY, YELLOW = (0,200,0),(200,0,0),(0,100,255),(180,180,180),(255,255,0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chef vs Clock")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial",18,bold=True)
big_font = pygame.font.SysFont("Arial",48,bold=True)

try:
    background_img = pygame.image.load("restaurant_background.png").convert_alpha()
    background_img = pygame.transform.scale(background_img,(WIDTH,HEIGHT))
except:
    background_img = None

try:
    chef_img = pygame.image.load("chef.png").convert_alpha()
    chef_img = pygame.transform.scale(chef_img,(90,90))
except:
    chef_img = pygame.Surface((90,90),pygame.SRCALPHA)
    chef_img.fill(BLUE)

dish_names = ["Pizza","Noodles","Burger","Fried Rice","Salad","Cake"]
food_icons = {}
for name in dish_names:
    icon = pygame.image.load(f"{name.lower()}.png").convert_alpha()
    food_icons[name] = pygame.transform.scale(icon,(36,36))

class Dish:
    PANEL_WIDTH = 145
    PANEL_HEIGHT = 115

    def __init__(self,name,burst_time,x,y):
        self.name=name
        self.total_time=burst_time
        self.remaining_time=burst_time
        self.x,self.y=x,y
        self.wait_time=0
        self.cooking=False
        self.finished=False
        self.lost=False
        self.counted=False
        self.rect = pygame.Rect(x,y,self.PANEL_WIDTH,self.PANEL_HEIGHT)

    def update(self,dt):
        if self.finished: return
        dt_sec = dt/1000.0
        if self.cooking:
            self.remaining_time -= dt_sec
            self.wait_time=0
            if self.remaining_time<=0:
                self.remaining_time=0
                self.finished=True
                self.cooking=False
        else:
            self.wait_time+=dt_sec
            if self.wait_time>=MAX_WAIT:
                self.lost=True
                self.finished=True
                self.cooking=False

    def draw(self, is_selected):
        bg_color = GRAY + (180,)
        if self.finished and not self.lost: bg_color = GREEN + (180,)
        elif self.lost: bg_color = RED + (180,)
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=10)
        if is_selected:
            pygame.draw.rect(screen, YELLOW, self.rect, 3, border_radius=10)

        # Layout calculations
        center_x = self.x + self.PANEL_WIDTH // 2
        y_offset = self.y + 8

        # Dish Name
        name_surf = font.render(self.name, True, BLACK)
        screen.blit(name_surf, (center_x - name_surf.get_width()//2, y_offset))
        y_offset += name_surf.get_height() + 2

        # Icon
        icon = food_icons[self.name]
        screen.blit(icon, (center_x - icon.get_width()//2, y_offset))
        y_offset += icon.get_height() + 2

        # Progress Bar
        bar_w, bar_h = 120, 10
        bar_x = center_x - bar_w//2
        bar_y = y_offset
        pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_w, bar_h), 2)
        progress = (self.total_time - self.remaining_time)/self.total_time
        bar_color = GREEN if not self.lost else RED
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, int(bar_w*progress), bar_h))
        y_offset += bar_h + 2

        # Time Text
        small_font = pygame.font.SysFont("Arial", 16, bold=True)
        text = "LOST" if self.lost else ("DONE!" if self.finished else f"{int(self.remaining_time)+1}s")
        t_surf = small_font.render(text, True, BLACK)
        screen.blit(t_surf, (center_x - t_surf.get_width()//2, y_offset))
        y_offset += t_surf.get_height() + 2

        # Patience Bar
        patience_w, patience_h = 120, 4
        patience_x = center_x - patience_w//2
        patience_y = y_offset
        pygame.draw.rect(screen, BLACK, (patience_x, patience_y, patience_w, patience_h), 1)
        if not self.cooking and not self.finished:
            wait_progress = min(self.wait_time/MAX_WAIT,1)
            pygame.draw.rect(screen, RED, (patience_x, patience_y, int(patience_w*wait_progress), patience_h))

# Dish Positions
positions=[(438,55),(438,180),(438,305),(438,430),(438,555),(438,679)]
dishes = [Dish(dish_names[i],random.randint(8,15),positions[i][0],positions[i][1]) for i in range(len(dish_names))]

current_index = 0
score = 0
start_time = pygame.time.get_ticks()/1000.0
game_over=False

def draw_hud():
    hud_rect = pygame.Rect(WIDTH-250,10,230,90)
    hud_surf = pygame.Surface(hud_rect.size,pygame.SRCALPHA)
    hud_surf.fill(BLACK+(150,))
    pygame.draw.rect(hud_surf,GRAY,(0,0,hud_rect.width,hud_rect.height),2,border_radius=5)
    screen.blit(hud_surf,hud_rect.topleft)
    score_text = font.render(f"Score: {score}",True,WHITE)
    screen.blit(score_text,(WIDTH-230,20))
    timer_color = RED if remaining_time<=10 else WHITE
    timer_text = font.render(f"Time Left: {remaining_time}s",True,timer_color)
    screen.blit(timer_text,(WIDTH-230,50))

    inst_rect = pygame.Rect(20,10,220,90)
    inst_surf = pygame.Surface(inst_rect.size,pygame.SRCALPHA)
    inst_surf.fill(BLACK+(150,))
    pygame.draw.rect(inst_surf,GRAY,(0,0,inst_rect.width,inst_rect.height),2,border_radius=5)
    screen.blit(inst_surf,inst_rect.topleft)
    screen.blit(font.render("UP/DOWN: Select Dish",True,YELLOW),(30,20))
    screen.blit(font.render("SPACE: Start/Stop Cooking",True,YELLOW),(30,50))

# --- Main Loop ---
paused = False
pause_accumulated = 0
pause_start_time = 0

while True:
    dt = clock.tick(FPS)

    # --- Background ---
    if background_img:
        screen.blit(background_img, (0, 0))
    else:
        screen.fill(WHITE)

    # --- Events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if not game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                current_index = (current_index - 1) % len(dishes)
            if event.key == pygame.K_DOWN:
                current_index = (current_index + 1) % len(dishes)
            if event.key == pygame.K_SPACE:
                selected = dishes[current_index]
                if not selected.finished:
                    for d in dishes:
                        d.cooking = False
                    selected.cooking = not selected.cooking
            if event.key == pygame.K_p:
                paused = not paused
                if paused:
                    pause_start_time = pygame.time.get_ticks() / 1000.0
                else:
                    pause_end = pygame.time.get_ticks() / 1000.0
                    pause_accumulated += pause_end - pause_start_time

    # --- Game Updates ---
    if not game_over and not paused:
        for d in dishes:
            d.update(dt)

        for d in dishes:
            if d.finished and not d.counted:
                d.counted = True
                if not d.lost:
                    score += 10

        elapsed = pygame.time.get_ticks() / 1000.0 - start_time - pause_accumulated
        remaining_time = max(int(TOTAL_TIME - elapsed), 0)

        if remaining_time <= 0 or all(d.finished for d in dishes):
            game_over = True
            for d in dishes:
                d.cooking = False

    # --- Draw Dishes ---
    for i, d in enumerate(dishes):
        d.draw(i == current_index)

    # --- Chef ---
    chef = dishes[current_index]
    chef_x = chef.x - 160
    chef_y = chef.y + 5
    screen.blit(chef_img, (chef_x, chef_y))

    # --- Chef Status Banner (Centered Top) ---
    chef_status = "Cooking 🍳" if chef.cooking else "Idle 😴"
    status_color = GREEN if chef.cooking else WHITE

    # semi-transparent bar
    banner_rect = pygame.Rect(0, 0, WIDTH, 60)
    banner_surf = pygame.Surface(banner_rect.size, pygame.SRCALPHA)
    banner_surf.fill((0, 0, 0, 150))
    screen.blit(banner_surf, banner_rect.topleft)

    # text centered
    status_surf = big_font.render(chef_status, True, status_color)
    screen.blit(status_surf, (WIDTH // 2 - status_surf.get_width() // 2, 10))

    # --- HUD ---
    draw_hud()

    # --- Pause Overlay ---
    if paused:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        pause_text = big_font.render("PAUSED", True, YELLOW)
        sub_text = font.render("Press P to Resume", True, WHITE)
        screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 40))
        screen.blit(sub_text, (WIDTH // 2 - sub_text.get_width() // 2, HEIGHT // 2 + 20))

    # --- Game Over Screen ---
    if game_over:
        overlay_w, overlay_h = 500, 200
        overlay_x = WIDTH // 2 - overlay_w // 2
        overlay_y = HEIGHT // 2 - overlay_h // 2
        pygame.draw.rect(screen, BLACK, (overlay_x, overlay_y, overlay_w, overlay_h), border_radius=15)

        over_text = big_font.render("GAME OVER", True, RED)
        score_text = big_font.render(f"Score: {score}", True, YELLOW)
        exit_text = font.render("Press ESC to Exit", True, WHITE)
        screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, overlay_y + 20))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, overlay_y + 80))
        screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, overlay_y + 140))
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()

    pygame.display.flip()
