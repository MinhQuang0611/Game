import pygame
import sys
import random
import pygame.mixer
from button import Button
pygame.init()

# Độ dài rộng màn hình 
WIDTH = 1200
HEIGHT = 600

# Điểm số
score = 0
high_score = 0

#tạo font
def game_font(size):
    return pygame.font.Font("contra_font.ttf",size)

# Khởi tạo màn hình
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TRACON")
pygame.mixer.init()

# Khởi chạy audio từ file
Contra_Music = pygame.mixer.Sound("ContraMusic.mp3")
title_music = pygame.mixer.Sound("01 Title.mp3")
game_over_music = pygame.mixer.Sound("13 Game Over.mp3")

# Cài đặt âm lượng
volume = 0.2
Contra_Music.set_volume(volume)
title_music.set_volume(volume)
# khởi tạo biến đồng hồ
clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    # Khởi tạo
    def __init__(self, images_left, images_right, jump_images_right, bullet_group, all_sprites, x , y, health_box_group):
        pygame.sprite.Sprite.__init__(self)  # Khởi tạo lớp cha pygame.sprite.Sprite
        self.images_left = images_left  # Chuỗi ảnh khi di chuyển sang trái
        self.images_right = images_right  # Chuỗi ảnh khi di chuyển sang phải
        self.jump_image_right = jump_images_right  # Ảnh khi nhảy sang phải
        self.image = self.images_right[0]  # Ảnh đầu tiên trong chuỗi ảnh khi di chuyển sang phải
        self.rect = self.image.get_rect() 
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.bullet_group = bullet_group
        self.all_sprites = all_sprites
        self.current_frame = 0
        self.direction = "right"
        self.is_move = False
        self.acceleration = 0.2
        self.velocity = 0
        self.frame_delay = 0.1
        self.shoot_delay = 0.5
        self.last_shoot_time = pygame.time.get_ticks()
        self.max_health = 200
        self.health = self.max_health
        self.is_dead = False
        self.health_box_group = health_box_group
    # Cập nhật trạng thái của người chơi
    def update(self):
        if self.is_dead:
            pygame.quit()
            sys.exit()

        self.apply_gravity()
        self.handle_input()
        self.move()
        self.animation()

        # Xử lý va chạm với đạn
        bullet_collisions = pygame.sprite.spritecollide(self, self.bullet_group, True)
        for bullet in bullet_collisions:
            self.health -= 20

        # Kiểm tra nếu mức máu dưới 0 thì đánh dấu người chơi đã chết
        if self.health <= 0:
            self.is_dead = True
        health_box_collisions = pygame.sprite.spritecollide(self, self.health_box_group, True)
        for health_box in health_box_collisions:
            self.health += 50
            if self.health > self.max_health:
                self.health = self.max_health
    # Áp dụng trọng lực lên người chơi
    def apply_gravity(self):
        self.velocity += self.acceleration
        self.rect.y += self.velocity

        # Kiểm tra và cập nhật nếu người chơi chạm đất
        if self.rect.y >= HEIGHT - self.rect.height:
            self.rect.y = HEIGHT - self.rect.height
            self.velocity = 0

    # Xử lý đầu vào từ bàn phím
    def handle_input(self):
        keys = pygame.key.get_pressed()
        speed = 0.1

        # Di chuyển sang trái hoặc phải dựa trên phím được nhấn
        if keys[pygame.K_LEFT]:
            self.direction = "left"
            self.rect.x -= speed
            self.is_move = True
        elif keys[pygame.K_RIGHT]:
            self.direction = "right"
            self.rect.x += speed
            self.is_move = True
        else:
            self.is_move = False

        
        if keys[pygame.K_SPACE]:
            self.shoot()
            
        # Xử lý nhảy và giới hạn di chuyển trong cửa sổ game
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.right >= WIDTH:
            self.rect.right = WIDTH
        if keys[pygame.K_UP] and self.rect.y >= HEIGHT - self.rect.height:
            self.jump()

    # Xử lý nhảy của người chơi
    def jump(self):
        self.velocity = -6

    # Di chuyển người chơi
    def move(self):
        keys = pygame.key.get_pressed()
        speed =  5

        if keys[pygame.K_LEFT]:
            self.direction == "left"
            self.rect.x -= speed
        elif keys[pygame.K_RIGHT]:
            self.direction == "right"
            self.rect.x += speed

    # Xử lý hoạt hình của người chơi
    def animation(self):
        if not self.is_move:
            if self.direction == "left":
                self.image = self.images_left[0]
            else:
                self.image = self.images_right[0]
        else:
            if self.direction == 'left':
                self.current_frame += self.frame_delay
                if int(self.current_frame) >= len(self.images_left):
                    self.current_frame = 0
                self.image = self.images_left[int(self.current_frame)]
            else:
                self.current_frame += self.frame_delay
                if int(self.current_frame) >= len(self.images_right):
                    self.current_frame = 0
                self.image = self.images_right[int(self.current_frame)]

    # Bắn đạn
    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shoot_time >= self.shoot_delay * 1000:
            bullet_x = self.rect.centerx + 80 if self.direction == "right" else self.rect.centerx - 80
            bullet = Bullet(bullet_x, self.rect.centery, self.direction)
            self.bullet_group.add(bullet)
            self.all_sprites.add(bullet)
            self.last_shoot_time = current_time
            
    # Vẽ thanh máu của người chơi
    def draw_health_bar(self):
        bar_length = 80
        bar_height = 5
        fill_width = int((self.health / self.max_health) * bar_length)
        fill_color = (0, 255, 0)
        outline_color = (255, 255, 255)
        bar_x = self.rect.centerx - bar_length // 2
        bar_y = self.rect.top - 20
        pygame.draw.rect(screen, outline_color, (bar_x, bar_y, bar_length, bar_height))
        pygame.draw.rect(screen, fill_color, (bar_x, bar_y, fill_width, bar_height))


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, player, bullet_group, all_sprites):
        super().__init__()
        # Load các hình ảnh cho di chuyển sang trái và sang phải
        self.images_left = [pygame.image.load("./graphics/enemies/standard/left/" + str(i) + ".png") for i in range(3)]
        self.images_right = [pygame.image.load("./graphics/enemies/standard/right/" + str(i) + ".png") for i in range(3)]
        self.image = self.images_right[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.player = player
        self.bullet_group = bullet_group
        self.all_sprites = all_sprites
        self.current_frame = 0
        self.direction = "right"
        self.is_dead = False
        self.acceleration = 0.2
        self.velocity = 0
        self.shoot_timer = random.randint(100, 300)
        self.max_health = 100
        self.health = self.max_health
        self.health_bar_color = (255, 0, 0)
        self.health_bar_width = 80
        self.health_bar_height = 5

    def update(self):
        # Cập nhật trạng thái của Enemy
        if not self.is_dead:
            self.apply_gravity()
            self.follow_player()
            self.move()
            self.shoot_timer -= 15

            # Bắn đạn theo một khoảng thời gian ngẫu nhiên
            if self.shoot_timer <= 0:
                self.shoot()
                self.shoot_timer = random.randint(100, 300)

        # Xử lý va chạm với đạn và giảm mức máu
        bullet_collisions = pygame.sprite.spritecollide(self, self.bullet_group, True)
        for bullet in bullet_collisions:
            self.health -= 20
            if self.health <= 0:
                self.is_dead = True
                self.respawn()

        # Hiển thị hình ảnh dựa vào hướng di chuyển
        if self.direction == "left":
            self.image = self.images_left[self.current_frame]
        elif self.direction == "right":
            self.image = self.images_right[self.current_frame]

        self.animation_movement()

    # Tái sinh Enemy khi bị hủy
    def respawn(self):
        global score
        self.health = self.max_health
        self.is_dead = False
        self.current_frame = 0
        self.image = self.images_right[0]
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        score += 1

    # Áp dụng trọng lực lên Enemy
    def apply_gravity(self):
        self.velocity += self.acceleration
        self.rect.y += self.velocity

        # Kiểm tra và cập nhật nếu Enemy chạm đất
        if self.rect.y >= HEIGHT - self.rect.height:
            self.rect.y = HEIGHT - self.rect.height
            self.velocity = 0

    # Theo dõi người chơi và điều chỉnh hướng di chuyển
    def follow_player(self):
        MAX_DISTANCE = WIDTH // 2
        if self.player is not None:
            if self.rect.x <= 0 or self.rect.x >= WIDTH - self.rect.width:
                self.direction = "right" if self.rect.x <= 0 else "left"

            if self.direction == "left":
                self.rect.x -= 2
            elif self.direction == "right":
                self.rect.x += 2

            # Đảo hướng di chuyển nếu quá xa so với người chơi
            if abs(self.player.rect.x - self.rect.x) >= MAX_DISTANCE:
                self.direction = "right" if self.player.rect.x > self.rect.x else "left"

    # Di chuyển Enemy
    def move(self):
        if self.direction == "left":
            self.rect.x -= 2
        elif self.direction == "right":
            self.rect.x += 2

    # Bắn đạn
    def shoot(self):
        bullet_direction = "left" if self.direction == 'left' else "right"
        if bullet_direction == "right":
            bullet_x = self.rect.centerx + 80
            self.image = self.images_right[0]
        else:
            bullet_x = self.rect.centerx - 80
            self.image = self.images_left[0]
        bullet = Bullet(bullet_x, self.rect.centery, bullet_direction)
        self.bullet_group.add(bullet)
        self.all_sprites.add(bullet)

    # Xử lý hoạt hình di chuyển của Enemy
    def animation_movement(self):
        if not self.is_dead:
            if self.direction == "left":
                self.current_frame = (self.current_frame + 1) % len(self.images_left)
                self.image = self.images_left[self.current_frame]
            elif self.direction == "right":
                self.current_frame = (self.current_frame + 1) % len(self.images_right)
                self.image = self.images_right[self.current_frame]

    # Vẽ thanh máu của Enemy
    def draw_health_bar(self):
        pygame.draw.rect(screen, self.health_bar_color, (self.rect.x, self.rect.y - 10, self.health_bar_width, self.health_bar_height))
        health_percentage = self.health / self.max_health
        health_bar_fill = health_percentage * self.health_bar_width
        pygame.draw.rect(screen, (0, 255, 0 ) , (self.rect.x, self.rect.y - 10, health_bar_fill, self.health_bar_height))

    # Hiển thị điểm số
    def draw_score(self):
        score_text = game_font(30).render(f"Score:{str(int(score))} ", True, (255,255,255))
        screen.blit(score_text,(10,10))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        # Load hình ảnh đạn
        self.images = [pygame.image.load("./graphics/bullet.png")]
        self.current_frame = 0
        self.image = self.images[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.direction = direction

    def update(self):
        # Cập nhật vị trí của đạn dựa trên hướng di chuyển
        if self.direction == "up":
            self.rect.y -= 5
        elif self.direction == "down":
            self.rect.y += 5
        elif self.direction == "left":
            self.rect.x -= 5
        elif self.direction == "right":
            self.rect.x += 5

        # Kiểm tra va chạm với biên của cửa sổ game và hủy đạn nếu ra khỏi biên
        if self.rect.top < 0 or self.rect.bottom > HEIGHT or self.rect.left < 0 or self.rect.right > WIDTH:
            self.kill()
        self.animation()

    # Xử lý hoạt hình của đạn
    def animation(self):
        self.current_frame = (self.current_frame + 1) % len(self.images)
        self.image = self.images[self.current_frame]

class HealthBox(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("health.png")  # Load the health box image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.is_collected = False
        self.velocity = 0
        self.acceleration = 0.1
        self.health_box_delay = 10  # Respawn delay in seconds
        self.respawn_timer_event = pygame.USEREVENT + 1
        pygame.time.set_timer(self.respawn_timer_event, self.health_box_delay * 1000)  # Set up the timer

    def update(self, *args):
        if args:
            player = args[0]
            if pygame.sprite.collide_rect(self, player) and not self.is_collected:
                player.health += 50
                if player.health > player.max_health:
                    player.health = player.max_health
                self.is_collected = True
                self.velocity = 0
                self.kill()

    def drop(self):
        self.velocity += self.acceleration
        self.rect.y += self.velocity

        # Kiểm tra và cập nhật nếu hộp chạm đất
        if self.rect.y >= HEIGHT - self.rect.height:
            self.rect.y = HEIGHT - self.rect.height
            self.velocity = 0

    def respawn(self):
        self.rect.x = random.randint(30, WIDTH - 30)
        self.rect.y = 0
        self.is_collected = False
all_sprites = pygame.sprite.Group()  # Tạo một nhóm sprite để quản lý tất cả các đối tượng sprite trong trò chơi.
enemy_group = pygame.sprite.Group()  # Tạo một nhóm sprite riêng cho các đối tượng Enemy.
bullet_group = pygame.sprite.Group()  # Tạo một nhóm sprite riêng cho các đối tượng đạn.
health_box_group = pygame.sprite.Group()


def main():
    global score,high_score
    
    health_box = HealthBox(random.randint(50, WIDTH - 50), random.randint(10,550))
    health_box_group.add(health_box)
    all_sprites.add(health_box)
    # Load hình ảnh cho người chơi và khởi tạo đối tượng Player
    player_images_left = [pygame.image.load(f"./graphics/player/left/{i}.png") for i in range(8)]
    player_images_right = [pygame.image.load(f"./graphics/player/right/{i}.png") for i in range(8)]
    player_jump_images_right = [pygame.image.load(f"./graphics/player/right_jump/0.png")]

    x = WIDTH // 2
    y = HEIGHT // 2

    player = Player(player_images_left, player_images_right, player_jump_images_right, bullet_group, all_sprites, x, y, health_box_group)
    all_sprites.add(player)

    # Khởi tạo đối tượng Enemy và đặt một số thuộc tính
    enemy = Enemy(random.randint(0, WIDTH - 30), random.randint(0, HEIGHT - 30), player, bullet_group, all_sprites)
    enemy.health_bar_color = (255, 0, 0)
    all_sprites.add(enemy)
    enemy_group.add(enemy)

    # Load hình nền và thiết lập kích thước
    background_image = pygame.image.load("./graphics/City2.png").convert()
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))   
    
    #load nền cuối game
    bg_end = pygame.image.load("nendc.png").convert()
    bg_end = pygame.transform.scale(bg_end,(WIDTH,HEIGHT))
    
    #load nền đầu game
    bg_intro = pygame.image.load("tracon.png").convert()
    
    #tạo menu đầu game
    def game_intro():
        intro = True
        while intro:
            title_music.play()
            PLAY_MOUSE_POS = pygame.mouse.get_pos()
            screen.blit(bg_intro,(0,0))
            start = pygame.transform.scale(pygame.image.load("assets/Play Rect.png").convert(), (200, 50))
            quit = pygame.transform.scale(pygame.image.load("assets/Quit Rect.png").convert(), (200, 50))
            PLAY_BUTTON = Button(image=start, pos=(600,300),
                           text_input="Play", font=game_font(30), base_color=(215, 252, 212), hovering_color=(255, 255, 255))
            PLAY_BUTTON.changeColor(PLAY_MOUSE_POS)
            PLAY_BUTTON.update(screen)
            QUIT_BUTTON = Button(image=quit, pos=(600,400),
                           text_input="quit", font=game_font(30), base_color=(215, 252, 212), hovering_color=(255, 255, 255))
            QUIT_BUTTON.changeColor(PLAY_MOUSE_POS)
            QUIT_BUTTON.update(screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if PLAY_BUTTON.checkForInput(PLAY_MOUSE_POS):
                        intro = False
                    if QUIT_BUTTON.checkForInput(PLAY_MOUSE_POS):
                        pygame.quit()
                        sys.exit()
            pygame.display.update()
    def show_menu(restart_game):
        menu_text = game_font(30).render("Press'S'to start,'Q'to quit", True, (255, 255, 255))
        menu_rect = menu_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        #game over
        game_over_text = game_font(40).render("Game over", True , (255,255,255))
        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, 50))
        #diểm cuối
        global score,high_score
        score_end = game_font(30).render(f"your score: {str(int(score))}", True, (255,255,255))
        score_end_rect = score_end.get_rect(center=(WIDTH // 2, HEIGHT // 2+50))
        if score > high_score:
            high_score = score
        high_score_end = game_font(30).render(f"high score: {str(int(high_score))}", True, (255,255,255))
        high_score_end_rect = high_score_end.get_rect(center=(WIDTH // 2, HEIGHT // 2+100))
        while restart_game:
            screen.blit(background_image, (0, 0))
            screen.blit(bg_end,(0,0)) #màn hình cuối game
            #text
            screen.blit(menu_text, menu_rect)
            screen.blit(game_over_text,game_over_rect)
            screen.blit(score_end,score_end_rect)
            screen.blit(score_end,score_end_rect)
            screen.blit(high_score_end,high_score_end_rect)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        return True  # Bắt đầu trò chơi
                    elif event.key == pygame.K_q:
                        return False  # Thoát trò chơi
                elif event.type == player.health_box_group.sprites()[0].respawn_timer_event:
                    player.health_box_group.sprites()[0].respawn()

            clock.tick(30)

        return False
    
    running = True
    restart_game = True
    game_intro()
    title_music.stop()
    while running:
        if player.health <= 0:
            Contra_Music.stop()
            game_over_music.play()
            restart_game = show_menu(restart_game)
            if restart_game:
                # Khởi tạo lại game
                # khởi tạo player
                player.health = player.max_health 
                player.is_dead = False
                player.rect.x = WIDTH // 2
                player.rect.y = HEIGHT // 2
                # khởi tạo enemy
                enemy.health = enemy.max_health
                enemy.is_dead = False
                enemy.current_frame = 0
                enemy.image = enemy.images_right[0]
                enemy.rect.x = random.randint(0, WIDTH - enemy.rect.width)
                score = 0
                game_over_music.stop()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        health_box_group.update(player)
        health_box_group.draw(screen)
        Contra_Music.play()
        all_sprites.update()
        screen.blit(background_image, (0, 0))
        player.draw_health_bar()
        enemy.draw_health_bar()
        all_sprites.draw(screen)
        enemy.draw_score()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main() 
    
