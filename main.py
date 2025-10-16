import pygame, sys, random, asyncio

WIDTH, HEIGHT = 1024, 800
FPS = 60
MAX_WAIT = 10
TOTAL_TIME = 75
WHITE, BLACK = (255,255,255), (0,0,0)
GREEN, RED, BLUE, GRAY, YELLOW, BROWN = (0,200,0),(200,0,0),(0,100,255),(180,180,180),(255,255,0),(245,222,179)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chef vs Clock")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 16, bold=True)
big_font = pygame.font.SysFont("Arial", 36, bold=True)
small_font = pygame.font.SysFont("Arial", 24, bold=True)

try:
    background_img = pygame.image.load("restaurant_background.png").convert_alpha()
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
except:
    background_img = None

try:
    chef_img = pygame.image.load("chef.png").convert_alpha()
    chef_img = pygame.transform.scale(chef_img, (70, 70))
except:
    chef_img = pygame.Surface((70, 70), pygame.SRCALPHA)
    chef_img.fill(BLUE)

dish_names = ["Pizza","Noodles","Burger","Fried Rice","Salad","Cake"]
food_icons = {}
for name in dish_names:
    try:
        icon = pygame.image.load(f"{name.lower()}.png").convert_alpha()
        food_icons[name] = pygame.transform.scale(icon, (30, 30))
    except:
        surf = pygame.Surface((30, 30), pygame.SRCALPHA)
        surf.fill(random.choice([(255,0,0,150),(0,255,0,150),(0,0,255,150),(255,255,0,150)]))
        food_icons[name] = surf

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
        bg_color = BROWN + (180,)
        if self.finished and not self.lost: bg_color = GREEN + (180,)
        elif self.lost: bg_color = RED + (180,)
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=10)
        if is_selected:
            pygame.draw.rect(screen, YELLOW, self.rect, 3, border_radius=10)

        center_x = self.x + self.PANEL_WIDTH // 2
        y_offset = self.y + 8

        name_surf = font.render(self.name, True, BLACK)
        screen.blit(name_surf, (center_x - name_surf.get_width()//2, y_offset))
        y_offset += name_surf.get_height() + 2

        icon = food_icons[self.name]
        screen.blit(icon, (center_x - icon.get_width()//2, y_offset))
        y_offset += icon.get_height() + 2

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
    screen.blit(font.render("SPACE: Start/Stop Cooking",True,YELLOW),(30,45))
    screen.blit(font.render("P: Pause/Resume",True,YELLOW),(30,70))

paused = False
pause_accumulated = 0
pause_start_time = 0
remaining_time = TOTAL_TIME

async def main():
    global paused, pause_accumulated, pause_start_time, game_over, current_index, score, start_time, remaining_time

    running = True
    while running:
        dt = clock.tick(FPS)

        # draw background
        if background_img:
            screen.blit(background_img, (0, 0))
        else:
            screen.fill(WHITE)

        # event handling
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
                    if not paused:
                        paused = True
                        pause_start_time = pygame.time.get_ticks() / 1000.0
                    else:
                        paused = False
                        pause_end = pygame.time.get_ticks() / 1000.0
                        pause_accumulated += pause_end - pause_start_time

        # calculate elapsed + remaining time
        if not paused:
            elapsed = pygame.time.get_ticks() / 1000.0 - start_time - pause_accumulated
            remaining_time = max(int(TOTAL_TIME - elapsed), 0)

        # update dishes only if game running
        if not game_over and not paused:
            for d in dishes:
                d.update(dt)
            for d in dishes:
                if d.finished and not d.counted:
                    d.counted = True
                    if not d.lost:
                        score += 10
            if remaining_time <= 0 or all(d.finished for d in dishes):
                game_over = True
                for d in dishes:
                    d.cooking = False

        # draw dishes
        for i, d in enumerate(dishes):
            d.draw(i == current_index)

        # draw chef beside current dish
        chef = dishes[current_index]
        chef_x = chef.x - 195
        chef_y = chef.y + 5
        screen.blit(chef_img, (chef_x, chef_y))

        # status display
        if chef.cooking:
            chef_status = f"Cooking {chef.name}"
            status_color = GREEN
        elif chef.finished and not chef.lost:
            chef_status = f"{chef.name} Ready!"
            status_color = YELLOW
        elif chef.lost:
            chef_status = f"{chef.name} Burnt!"
            status_color = RED
        else:
            chef_status = "Idle"
            status_color = WHITE

        status_surf = small_font.render(chef_status, True, status_color)
        screen.blit(status_surf, (WIDTH // 2 - status_surf.get_width() // 2, 10))

        # HUD and overlays
        draw_hud()

        if paused:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            pause_text = big_font.render("PAUSED", True, YELLOW)
            sub_text = font.render("Press P to Resume", True, WHITE)
            screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 40))
            screen.blit(sub_text, (WIDTH // 2 - sub_text.get_width() // 2, HEIGHT // 2 + 20))

        if game_over:
            overlay_w, overlay_h = 500, 250
            overlay_x = WIDTH // 2 - overlay_w // 2
            overlay_y = HEIGHT // 2 - overlay_h // 2

            pygame.draw.rect(screen, BLACK, (overlay_x, overlay_y, overlay_w, overlay_h), border_radius=15)
            over_text = big_font.render("GAME OVER", True, RED)
            score_text = big_font.render(f"Score: {score}", True, YELLOW)

            button_w, button_h = 220, 60
            button_x = WIDTH // 2 - button_w // 2
            button_y = overlay_y + 150
            pygame.draw.rect(screen, GREEN, (button_x, button_y, button_w, button_h), border_radius=10)
            btn_text = font.render("Try Again", True, BLACK)
            screen.blit(btn_text, (button_x + (button_w - btn_text.get_width()) // 2,
                                   button_y + (button_h - btn_text.get_height()) // 2))

            screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, overlay_y + 20))
            screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, overlay_y + 90))

            mouse = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()
            if (button_x <= mouse[0] <= button_x + button_w) and (button_y <= mouse[1] <= button_y + button_h):
                pygame.draw.rect(screen, (0, 200, 0), (button_x, button_y, button_w, button_h), border_radius=10)
                screen.blit(btn_text, (button_x + (button_w - btn_text.get_width()) // 2,
                                       button_y + (button_h - btn_text.get_height()) // 2))
                if click[0]:
                    current_index = 0
                    score = 0
                    start_time = pygame.time.get_ticks() / 1000.0
                    pause_accumulated = 0
                    paused = False
                    game_over = False
                    remaining_time = TOTAL_TIME

                    for d in dishes:
                        d.remaining_time = d.total_time
                        d.wait_time = 0
                        d.cooking = False
                        d.finished = False
                        d.lost = False
                        d.counted = False

        pygame.display.flip()
        await asyncio.sleep(0)

asyncio.run(main())
