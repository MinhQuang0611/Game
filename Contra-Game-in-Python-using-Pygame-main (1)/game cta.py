import pygame
import sys
import random
import pygame.mixer
from button import Button
pygame.init()

# Độ dài rộng màn hình 
WIDTH = 1200
HEIGHT = 600

# Điểm số người chơi bắt đầu là 0
score = 0

# điểm số gần nhất tạo hộp máu
last_create_box = 0
last_create_box1 = 0
# Điểm số cao nhất bắt đầu là 0
high_score = 0

# Tạo font chữ theo file
def game_font(size):
    return pygame.font.Font("contra_font.ttf",size)

# Khởi tạo màn hình
screen = pygame.display.set_mode((WIDTH, HEIGHT)) # Độ dài và rộng màn hình theo số mặc định
pygame.display.set_caption("TRACON") # Tên màn hình
pygame.mixer.init() # Khởi tạo audio

# Khởi chạy audio từ file
Contra_Music = pygame.mixer.Sound("ContraMusic.mp3") # nhạc chạy trong toàn bộ trò chơi
title_music = pygame.mixer.Sound("01 Title.mp3") # nhạc chạy khi bắt đầu
game_over_music = pygame.mixer.Sound("13 Game Over.mp3") # nhạc chạy khi kết thúc

# Cài đặt âm lượng
volume = 0.2
Contra_Music.set_volume(volume) # âm lượng nhạc khi chơi 
title_music.set_volume(volume) # âm lướng khi bắt đầu

# khởi tạo biến đồng hồ
clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    # Khởi tạo các thông số 
    def __init__(self, images_left, images_right, jump_images_right, bullet_group, all_sprites, x , y, health_box_group,upgrade_box_group):
        pygame.sprite.Sprite.__init__(self)  # Class Player sẽ kế thừa các thuộc tính của class Sprite
        self.images_left = images_left  # Chuỗi ảnh khi di chuyển sang trái
        self.images_right = images_right  # Chuỗi ảnh khi di chuyển sang phải
        self.jump_image_right = jump_images_right  # Ảnh khi nhảy sang phải
        self.image = self.images_right[0]  # Ảnh đầu tiên trong chuỗi ảnh khi di chuyển sang phải
        self.rect = self.image.get_rect() # Lấy toạ độ của ảnh đầu tiên trong chuỗi ảnh khi di chuyên sang phải
        self.rect.center = (WIDTH // 2, HEIGHT // 2) # Lấy trung tâm ảnh làm vị trí ảnh 
        self.bullet_group = bullet_group # nhóm các hình ảnh viên đạn
        self.all_sprites = all_sprites # nhóm tất cả các hình ảnh
        self.current_frame = 0 
        self.direction = "right" # hướng mặc định của nhân vật là bên phải khi bắt đầu trò chơi
        self.is_move = False # Bắt đầu trò chơi người chơi đang đứng yên
        self.acceleration = 0.2 # gia tốc 
        self.velocity = 0 # tốc độ khi bắt đầu chơi
        self.frame_delay = 0.1 # độ trễ giữa các khung hình
        self.shoot_delay = 0.1 # độ trễ khi bắn đạn
        self.last_shoot_time = pygame.time.get_ticks() # thời gian gần nhất người chơi bắn đạn
        self.max_health = 5000 # máu tối đa của người chơi
        self.health = self.max_health # máu khi bắt đầu chơi sẽ đầy
        self.is_dead = False # trạng thái người chơi sống hay chết
        self.health_box_group = health_box_group # nhóm các class hộp máu
        self.upgrade_box_group = upgrade_box_group
    # Cập nhật trạng thái của người chơi
    def update(self):
        """Cập nhật lại các thông số để hiển thị ra màn hình"""
        if self.is_dead: # Nếu trạng thái người chơi là chết thì kết thúc trò chơi và thoát chương trình
            pygame.quit()
            sys.exit()

        self.apply_gravity() # Xử lí trọng lực
        self.handle_input() # Xử lý những phím bấm
        self.move() # Xử lí các di chuyển 
        self.animation() # Xử lí các hoạt hoạ

        # Xử lý va chạm với đạn
        bullet_collisions = pygame.sprite.spritecollide(self, self.bullet_group, True)
        for bullet in bullet_collisions: # Mỗi viên đạn chạm vào nhân vật sẽ làm giảm đi 20 máu của người chơi 
            self.health -= 20

        # Kiểm tra nếu mức máu dưới 0 thì đánh dấu người chơi đã chết
        if self.health <= 0:
            self.is_dead = True

        # Xử lý va chạm với hộp máu   
        health_box_collisions = pygame.sprite.spritecollide(self, self.health_box_group, True)
        for health_box in health_box_collisions: # Với mỗi hộp máu ăn được tăng 50 máu người chơi
            self.health += 50
            if self.health > self.max_health: # Không thể tăng thêm nếu máu đã đầuy thanh
                self.health = self.max_health
                
        upgrade_box_collisions = pygame.sprite.spritecollide(self, self.upgrade_box_group, True)
        for upgrade_box in upgrade_box_collisions: # Với mỗi hộp máu tăng cường
            self.shoot_delay -= 0.05
            
    # Áp dụng trọng lực lên người chơi
    def apply_gravity(self):
        """Cài đặt trọng lực"""
        self.velocity += self.acceleration # vận tốc sẽ tăng theo gia tốc
        self.rect.y += self.velocity # vị trí nhân vật sẽ thay đổi theo vận tốc

        # Kiểm tra và cập nhật nếu người chơi chạm đất
        if self.rect.y >= HEIGHT - self.rect.height: # Nếu người chơi chạm đất thì tốc độ trở về 0, và không thể rơi xuống nữa
            self.rect.y = HEIGHT - self.rect.height
            self.velocity = 0

    # Xử lý đầu vào từ bàn phím
    def handle_input(self):
        keys = pygame.key.get_pressed() # các phím mà người chơi đã ấn
        speed = 0.1 # tốc độ xử lý 

        # Di chuyển sang trái hoặc phải dựa trên phím được nhấn
        if keys[pygame.K_LEFT]: # phím sang trái được ấn
            self.direction = "left" # hướng hình ảnh nhân vật là trái
            self.rect.x -= speed # hình ảnh nhân vật sẽ di chuyển sang trái (toạ độ x giảm) 
            self.is_move = True # trạng thái nhân vật thay đổi thành đang di chuyển
        elif keys[pygame.K_RIGHT]: # phím sang phải được ấn
            self.direction = "right" # hướng hướng hình ảnh nhân vật là phải
            self.rect.x += speed # hình ảnh nhân vật sẽ di chuyển sang phải (toạ độ x tăng)
            self.is_move = True # trạng thái nhân vật thay đổi thành đang di chuyển
        else:
            self.is_move = False # nếu không có phím sang trái và phải được ấn, trạng thái nhân vật là không di chuyển

        
        if keys[pygame.K_SPACE]: # Nếu phím cách được ấn, xử lý theo hàm shoot
            self.shoot()
            
        # Xử lý giới hạn di chuyển trong cửa sổ game
        if self.rect.left <= 0: # Không thể di chuyển sang trái nữa nếu đến mép trái màn hình
            self.rect.left = 0
        if self.rect.right >= WIDTH: # Không thể di chuyển sang phải nữa nếu đến mép trái màn hình
            self.rect.right = WIDTH

        # Xử lý nhảy của người chơi
        # Nếu phím lên trên được ấn và người chơi đang chạm đất, xử lý theo hàm jump
        if keys[pygame.K_UP] and self.rect.y >= HEIGHT - self.rect.height:
            self.jump()

    # Xử lý nhảy của người chơi
    def jump(self):
        self.velocity = -6 # vận tốc giảm đi 6

    # Di chuyển người chơi
    def move(self):
        keys = pygame.key.get_pressed() # các phím được ấn
        speed =  5 # tốc độ di chuyển

        if keys[pygame.K_LEFT]: # phím sang trái được ấn thì hướng hình ảnh nhân vật sang trái và di chuyển sang trái (toạ độ x giảm) 
            self.direction == "left"
            self.rect.x -= speed
        elif keys[pygame.K_RIGHT]: # phím sang phải được ấn thì hướng hình ảnh nhân vật sang phải và di chuyển sang phải (toạ độ x tăng) 
            self.direction == "right"
            self.rect.x += speed

    # Xử lý hoạt hình của người chơi
    def animation(self):
        if not self.is_move: # nếu trạng thái là không di chuyển
            if self.direction == "left": # nếu hướng hình ảnh là trái thì hiển thị hình ảnh đầu tiên của chuỗi ảnh nhân vật hướng sang trái
                self.image = self.images_left[0]
            else: # nếu hướng hình ảnh là phải thì hiển thị hình ảnh đầu tiên của chuỗi ảnh nhân vật hướng sang phải
                self.image = self.images_right[0]
        else: # nếu trạng thái là di chuyển
            if self.direction == 'left': # nếu hướng hình ảnh là trái thì hiển thị lần lượt các ảnh trong chuỗi hoạt ảnh di chuyển sang trái
                self.current_frame += self.frame_delay
                if int(self.current_frame) >= len(self.images_left): # Lặp lại nếu chuỗi ảnh hết
                    self.current_frame = 0
                self.image = self.images_left[int(self.current_frame)]
            else: # nếu hướng hình ảnh là trái thì hiển thị lần lượt các ảnh trong chuỗi hoạt ảnh di chuyển sang trái
                self.current_frame += self.frame_delay
                if int(self.current_frame) >= len(self.images_right):
                    self.current_frame = 0
                self.image = self.images_right[int(self.current_frame)]

    # Bắn đạn
    def shoot(self):
        current_time = pygame.time.get_ticks() # thời gian bắn gần nhất
        if current_time - self.last_shoot_time >= self.shoot_delay * 1000: # khoảng cách giữa 2 lần bắn là từ 1 giây trở lên là hợp lệ
            bullet_x = self.rect.centerx + 80 if self.direction == "right" else self.rect.centerx - 80 # nếu nhân vật đang hướng sang phải thì toạ độ đạn xuất hiện cách nhân vật 80px bên phải, ngược lại nếu là bên trái
            bullet = Bullet(bullet_x, self.rect.centery, self.direction) # tạo hình ảnh đạn
            self.bullet_group.add(bullet) # thêm vào các nhóm hình ảnh để quản lí
            self.all_sprites.add(bullet)
            self.last_shoot_time = current_time # lưu lại lần bắn gần nhất
            
    # Vẽ thanh máu của người chơi
    def draw_health_bar(self):
        bar_length = 80 # thanh máu dài 80px
        bar_height = 5 # thanh máu cao 5px
        fill_width = int((self.health / self.max_health) * bar_length) # tính toán độ dài phần máu hiện tại
        fill_color = (0, 255, 0) # đổ màu thanh máu
        outline_color = (255, 255, 255) # màu viền 
        bar_x = self.rect.centerx - bar_length // 2 # toạ độ thanh máu (trên nhân vạt 20px, chiều dọc theo nhân vật)
        bar_y = self.rect.top - 20
        pygame.draw.rect(screen, outline_color, (bar_x, bar_y, bar_length, bar_height)) # hiển thị ra màn hình theo các thông số đã tính toán
        pygame.draw.rect(screen, fill_color, (bar_x, bar_y, fill_width, bar_height))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, player, bullet_group, all_sprites):
        super().__init__()
        # Load các hình ảnh cho di chuyển sang trái và sang phải
        self.images_left = [pygame.image.load("./graphics/enemies/standard/left/" + str(i) + ".png") for i in range(3)] # chuỗi hình ảnh kẻt thù hướng sang trái
        self.images_right = [pygame.image.load("./graphics/enemies/standard/right/" + str(i) + ".png") for i in range(3)] # chuỗi hình ảnh kẻt thù hướng sang phải
        self.image = self.images_right[0] # hình ảnh ban đầu đang hướng hình ảnh phải
        self.rect = self.image.get_rect() # toạ độ hình ảnh
        self.rect.x = x 
        self.rect.y = y
        self.player = player # người chơi
        self.bullet_group = bullet_group # nhóm hình ảnh viên đạn
        self.all_sprites = all_sprites # nhóm tất cả hình ảnh 
        self.current_frame = 0 # thứ tự load hình ảnh trong chuỗi hình ảnh ban đầu là ảnh đầu tiên
        self.direction = "right" # hướng hình ảnh ban đầu đang hướng hình ảnh phải
        self.is_dead = False # trạng thái là chưa chết
        self.acceleration = 0.2 # gia tốc ban đầu
        self.velocity = 0 # tốc độ ban đầu
        self.shoot_timer = random.randint(100, 300) # thời gian giãn cách giữa các lần bắn sẽ dao động từ 0.1 đến 0.3 giây
        self.max_health = 100 # máu tối đa là 100
        self.health = self.max_health # máu ban đầu là đầy
        self.health_bar_color = (255, 0, 0) # màu thanh máu
        self.health_bar_width = 80 # chiều dài thanh máu
        self.health_bar_height = 5 # chiều cao thanh máu

    def update(self):
        # Cập nhật trạng thái của Enemy
        if not self.is_dead:
            self.apply_gravity() # tính toán trong lực
            self.follow_player() # tính toán để chạy theo người chơi
            self.move() # tự động di chuyển
            self.shoot_timer -= 15 # thời gian giãn cách giữa mỗi lần bắn giảm dần 15 mili giây

            # Reset lại thời gian giãn cách giữa một lần bắn nếu nó về 0 (không thể bắn nữa)
            if self.shoot_timer <= 0:
                self.shoot()
                self.shoot_timer = random.randint(100, 300)

        # Xử lý va chạm với đạn và giảm mức máu
        bullet_collisions = pygame.sprite.spritecollide(self, self.bullet_group, True) 
        for bullet in bullet_collisions: # Mỗi viên đạn người chơi bắn vào kẻ thù, kẻ thù bị mất 20 máu
            self.health -= 20
            if self.health <= 0: # máu giảm về 0 sẽ chết, tạo kẻ thù mới
                self.is_dead = True
                self.respawn()

        # Hiển thị hình ảnh dựa vào hướng di chuyển
        if self.direction == "left":
            self.image = self.images_left[self.current_frame]
        elif self.direction == "right":
            self.image = self.images_right[self.current_frame]

        self.animation_movement() # tính toán hoạt ảnh di chuyển

    # Tái sinh Enemy khi bị hủy
    def respawn(self):
        global score
        self.health = self.max_health # máu ban đầu là đầy
        self.is_dead = False # trạng thái là chưa chết
        self.current_frame = 0 # thứ tự load hình ảnh trong chuỗi hình ảnh ban đầu là ảnh đầu tiên
        self.image = self.images_right[0] # hình ảnh ban đầu đang hướng hình ảnh phải
        self.rect.x = random.randint(0, WIDTH - self.rect.width) # toạ độ xuất hiện là ngẫu nhiên trong khung hình
        score += 1 # điểm số của người chơi tăng 1

    # Áp dụng trọng lực lên Enemy
    def apply_gravity(self):
        self.velocity += self.acceleration # tốc độ tăng theo gia tốc 
        self.rect.y += self.velocity # toạ độ y sẽ thay đổi theo tốc độ

        # Kiểm tra và cập nhật nếu Enemy chạm đất thì sẽ không thể rơi xuống thêm nữa, tốc độ về 0
        if self.rect.y >= HEIGHT - self.rect.height:
            self.rect.y = HEIGHT - self.rect.height
            self.velocity = 0

    # Theo dõi người chơi và điều chỉnh hướng di chuyển
    def follow_player(self):
        MAX_DISTANCE = WIDTH // 2 # khoảng cách tối đa với người chơi là nửa màn hình
        if self.player is not None: # nếu tìm thấy người chơi
            if self.rect.x <= 0 or self.rect.x >= WIDTH - self.rect.width: # quay lại nếu chạm tường 
                self.direction = "right" if self.rect.x <= 0 else "left"
            
            # tính toạ độ nếu di chuyển qua 2 bên
            if self.direction == "left":
                self.rect.x -= 2
            elif self.direction == "right":
                self.rect.x += 2

            # Đảo hướng di chuyển nếu quá xa so với người chơi
            if abs(self.player.rect.x - self.rect.x) >= MAX_DISTANCE:
                self.direction = "right" if self.player.rect.x > self.rect.x else "left"

    # Di chuyển Enemy
    def move(self):
        # tính toạ độ nếu di chuyển qua 2 bên
        if self.direction == "left":
            self.rect.x -= 2
        elif self.direction == "right":
            self.rect.x += 2

    # Bắn đạn
    def shoot(self):
        bullet_direction = "left" if self.direction == 'left' else "right" # hướng đạn bắn sẽ theo hướng Enemy
        if bullet_direction == "right":
            bullet_x = self.rect.centerx + 80 # đạn bắn sẽ di chuyển sang phải, load hình ảnh đầu tiên
            self.image = self.images_right[0]
        else:
            bullet_x = self.rect.centerx - 80 # đạn bắn sẽ di chuyển sang trái, load hình ảnh đầu tiên
            self.image = self.images_left[0]
        bullet = Bullet(bullet_x, self.rect.centery, bullet_direction) # tạo đối tượng hình ảnh
        self.bullet_group.add(bullet) # thêm vào các nhóm để quản lý
        self.all_sprites.add(bullet)

    # Xử lý hoạt hình di chuyển của Enemy
    def animation_movement(self):
        if not self.is_dead: # nếu Enemy chưa chết load từng hình ảnh theo hướng hiện tại
            if self.direction == "left": 
                self.current_frame = (self.current_frame + 1) % len(self.images_left)
                self.image = self.images_left[self.current_frame]
            elif self.direction == "right":
                self.current_frame = (self.current_frame + 1) % len(self.images_right)
                self.image = self.images_right[self.current_frame]

    # Vẽ thanh máu của Enemy
    def draw_health_bar(self):
        # vẽ thanh máu theo các thông số đã tính toán
        pygame.draw.rect(screen, self.health_bar_color, (self.rect.x, self.rect.y - 10, self.health_bar_width, self.health_bar_height))
        health_percentage = self.health / self.max_health
        health_bar_fill = health_percentage * self.health_bar_width
        pygame.draw.rect(screen, (0, 255, 0 ) , (self.rect.x, self.rect.y - 10, health_bar_fill, self.health_bar_height))

    # Hiển thị điểm số
    def draw_score(self):
        score_text = game_font(30).render(f"Score:{str(int(score))} ", True, (255,255,255)) # Hiển thị lên màn hình thông báo điểm số hiện tại sau khi người chơi chết
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
        self.image = pygame.image.load("health.png")  
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.is_collected = False # trạng thái đã được ăn chưa
        self.velocity = 0
        self.acceleration = 0.01
        self.last_health_box = pygame.time.get_ticks() # thời gian hộp gần nhất xuất hiện
        self.health_box_delay = 1 # độ trễ
    def update(self, *args):
        if args:
            player = args[0] # tìm người chơi đang xuất hiện
            if pygame.sprite.collide_rect(self, player) and not self.is_collected: # nếu va chạm với người chơi và chưa được ăn
                player.health += 50 # tăng máu người chơi lên 50 
                if player.health > player.max_health:  # chỉ tăng tối đa đầy thanh máu
                    player.health = player.max_health
                self.is_collected = True # chuyển sang trạng thái đã bị ăn
        self.check_and_delay() 
        self.drop()

    def drop(self):
        # trọng lực cho hộp
        self.velocity += self.acceleration
        self.rect.y += self.velocity

        # Kiểm tra và cập nhật nếu hộp chạm đất thì không rơi được thêm nữa
        if self.rect.y >= HEIGHT - self.rect.height:
            self.rect.y = HEIGHT - self.rect.height
            self.velocity = 0
    def check_and_delay(self): # hộp box mới xuất hiện sau khi hộp cũ xuất hiện 20 giây
        current_time = pygame.time.get_ticks() 
        if current_time - self.last_health_box >= self.health_box_delay * 20000:
            self.last_health_box = current_time
            self.rect.x = random.randint(30, WIDTH - 30)
            self.rect.y = 0

class upgrade(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("upgrade.png")  
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.is_collected = False # trạng thái đã được ăn chưa
        self.velocity = 0
        self.acceleration = 0.01
        self.last_upgrade = pygame.time.get_ticks() # thời gian hộp gần nhất xuất hiện
        self.upgrade_delay = 1 # độ trễ
    def update(self, *args):
        if args:
            player = args[0] # tìm người chơi đang xuất hiện
            if pygame.sprite.collide_rect(self, player) and not self.is_collected: # nếu va chạm với người chơi và chưa được ăn
                player.shoot_delay -= 0.05 # tăng tốc bắn lên 0.05
                self.is_collected = True # chuyển sang trạng thái đã bị ăn
        self.check_and_delay() 
        self.drop()

    def drop(self):
        # trọng lực cho hộp
        self.velocity += self.acceleration
        self.rect.y += self.velocity

        # Kiểm tra và cập nhật nếu hộp chạm đất thì không rơi được thêm nữa
        if self.rect.y >= HEIGHT - self.rect.height:
            self.rect.y = HEIGHT - self.rect.height
            self.velocity = 0
    def check_and_delay(self): # hộp box mới xuất hiện sau khi hộp cũ xuất hiện 20 giây
        current_time = pygame.time.get_ticks() 
        if current_time - self.last_upgrade >= self.upgrade_delay * 20000:
            self.last_upgrade = current_time
            self.rect.x = random.randint(30, WIDTH - 30)
            self.rect.y = 0
            
all_sprites = pygame.sprite.Group()  # Tạo một nhóm sprite để quản lý tất cả các đối tượng sprite trong trò chơi.
enemy_group = pygame.sprite.Group()  # Tạo một nhóm sprite riêng cho các đối tượng Enemy.
bullet_group = pygame.sprite.Group()  # Tạo một nhóm sprite riêng cho các đối tượng đạn.
health_box_group = pygame.sprite.Group() # Tạo một nhóm sprite riêng cho các đối tượng hộp máu.
upgrade_box_group = pygame.sprite.Group() # Tạo một nhóm sprite riêng cho các đối tượng hộp c

def main():
    global score,high_score,last_create_box, last_create_box1 # biến toàn cục
    # Hàm tạo các box hồi máu
    def create_heathbox():
            health_box = HealthBox(random.randint(50, WIDTH - 50), random.randint(10,550)) # vị trí ngẫu nhiên
            health_box_group.add(health_box) # thêm vào group upgrade để quản lí
            all_sprites.add(health_box) # thêm vào group all_sprites để quản lí

    def create_upgrade():
            upgrade_box = upgrade(random.randint(50, WIDTH - 50), random.randint(10,550)) # vị trí ngẫu nhiên
            upgrade_box_group.add(upgrade_box) # thêm vào group upgrade_box_group để quản lí
            all_sprites.add(upgrade_box) # thêm vào group all_sprites để quản lí
            
    # Load hình ảnh cho người chơi cho các trạng thái khác nhau
    player_images_left = [pygame.image.load(f"./graphics/player/left/{i}.png") for i in range(8)]
    player_images_right = [pygame.image.load(f"./graphics/player/right/{i}.png") for i in range(8)]
    player_jump_images_right = [pygame.image.load(f"./graphics/player/right_jump/0.png")]

    x = WIDTH // 2 # tạo độ trung tâm màn hình
    y = HEIGHT // 2

    # khởi tạo đối tượng người chơi 
    player = Player(player_images_left, player_images_right, player_jump_images_right, bullet_group, all_sprites, x, y, health_box_group,upgrade_box_group)
    all_sprites.add(player)

    # Khởi tạo đối tượng Enemy
    enemy = Enemy(random.randint(0, WIDTH - 30), random.randint(0, HEIGHT - 30), player, bullet_group, all_sprites)
    enemy.health_bar_color = (255, 0, 0)
    all_sprites.add(enemy)
    enemy_group.add(enemy)

    # Load hình nền và thiết lập kích thước
    background_image = pygame.image.load("./graphics/City2.png").convert()
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))   
    
    # load nền cuối game
    bg_end = pygame.image.load("nendc.png").convert()
    bg_end = pygame.transform.scale(bg_end,(WIDTH,HEIGHT))
    
    # load nền đầu game
    bg_intro = pygame.image.load("tracon.png").convert()
    
    def tutorial():
        intro = True
        title_music.stop()
        while intro:
            TUTORIAL_MOUSE_POS = pygame.mouse.get_pos()
            
            screen.fill("white")

            TUTORIAL_TEXT = game_font(30).render("tutorial", True, "Black")
            TUTORIAL_RECT = TUTORIAL_TEXT.get_rect(center=(600, 50))
            screen.blit(TUTORIAL_TEXT, TUTORIAL_RECT)

            move = pygame.image.load("move.png").convert_alpha()
            screen.blit(move,(600,130))
            jump = game_font(30).render("move : ", True, "Black")
            jump_rect =jump.get_rect(center =(500, 200))
            screen.blit(jump, jump_rect)
            
            space = pygame.image.load("space.png").convert_alpha()
            screen.blit(space,(600,280))
            shoot = game_font(30).render("shoot : ", True , "Black")
            shoot_rect = shoot.get_rect(center =(500, 300))
            screen.blit(shoot,shoot_rect)
            
            TUTORIAL_BACK = Button(image=None, pos=(600, 460), 
                                text_input="BACK", font=game_font(40), base_color="Black", hovering_color="Green")

            TUTORIAL_BACK.changeColor(TUTORIAL_MOUSE_POS)
            TUTORIAL_BACK.update(screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if TUTORIAL_BACK.checkForInput(TUTORIAL_MOUSE_POS):
                        intro = False
                        game_intro()

            pygame.display.update()
                        
    #tạo menu đầu game
    def game_intro():
        title_music.play() # bật nhạc đầu game
        intro = True
        while intro:
            PLAY_MOUSE_POS = pygame.mouse.get_pos() # lấy tạo độ chuột
            screen.blit(bg_intro,(0,0)) # load hình nền giới thiệu
            start = pygame.transform.scale(pygame.image.load("assets/Play Rect.png").convert(), (200, 50)) # load hình ảnh nút bắt đầu chơi
            quit = pygame.transform.scale(pygame.image.load("assets/Quit Rect.png").convert(), (200, 50)) # load hình ảnh nút thoát trò chơi
            PLAY_BUTTON = Button(image=start, pos=(600,300),text_input="Play", font=game_font(30), base_color=(215, 252, 212), hovering_color=(255, 255, 255)) # tạo đối tượng nút bắt đầu chơi
            PLAY_BUTTON.changeColor(PLAY_MOUSE_POS) # thay đổi màu nút bắt đầu chơi
            PLAY_BUTTON.update(screen) # hien thi nút bắt đầu chơi
            QUIT_BUTTON = Button(image=quit, pos=(600, 500), text_input="quit", font=game_font(30), base_color=(215, 252, 212), hovering_color=(255, 255, 255)) # tạo đối tượng nút thoát trò chơi
            QUIT_BUTTON.changeColor(PLAY_MOUSE_POS) # thay đổi màu nút thoát trò chơi
            QUIT_BUTTON.update(screen) # hiển thị nút thoát trò chơi
            TUTORIALS = Button(image=quit, pos=(600,400), text_input="tutorial", font= game_font(25), base_color=(215, 252, 212), hovering_color=(255, 255, 255))
            TUTORIALS.changeColor(PLAY_MOUSE_POS)
            TUTORIALS.update(screen)
            for event in pygame.event.get(): # kiểm tra các sự kiện 
                if event.type == pygame.QUIT: # nếu có sự kiện thoát trò chơi, tắt chương trình
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN: # nếu có sự kiện click chuột, xem có click vào nút bắt đầu chơi hay thoát trò chơi không, nếu có thì thực hiện thao tác tương ứng
                    if TUTORIALS.checkForInput(PLAY_MOUSE_POS):
                        tutorial()
                    if PLAY_BUTTON.checkForInput(PLAY_MOUSE_POS): # tắt phần giới thiệu và bắt đầu chơi nếu ấn nút bắt đầu
                        intro = False
                    if QUIT_BUTTON.checkForInput(PLAY_MOUSE_POS): # tắt phần giờ thiệu và thoát trò chơi nếu ấn nút thoát trò chơi
                        pygame.quit()
                        sys.exit()
            pygame.display.update() # load lại màn hình
    def show_menu(restart_game):
        # menu sau khi người chơi chết

        # Chữ các lựa chọn chơi tiếp hay thoát trờ chơi
        menu_text = game_font(30).render("Press'S'to start,'Q'to quit", True, (255, 255, 255)) # hiển thị các nút ấn lựa chọn
        menu_rect = menu_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)) # lấy toạ độ trung tâm chữ 
        
        # Chữ Game over
        game_over_text = game_font(40).render("Game over", True , (255,255,255))
        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, 50))

        # Điểm số hiện tại và điểm số cao nhất
        global score,high_score
        score_end = game_font(30).render(f"your score: {str(int(score))}", True, (255,255,255))
        score_end_rect = score_end.get_rect(center=(WIDTH // 2, HEIGHT // 2-50))

        # cập nhật lại điểm cao nhất
        if score > high_score:
            high_score = score

        # Điểm cao nhât
        high_score_end = game_font(30).render(f"high score: {str(int(high_score))}", True, (255,255,255))
        high_score_end_rect = high_score_end.get_rect(center=(WIDTH // 2, HEIGHT // 2-100))
        
        back_menu = game_font(30).render("Press 'r' back to menu", True, (255, 255, 255))
        back_menu_rect = back_menu.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))

        # trong khi hiển thị màn hình khởi động lại game
        while restart_game:
            screen.blit(background_image, (0, 0)) # hien thi màn hình nền
            screen.blit(bg_end,(0,0)) #màn hình cuối game
            
            # các chữ cần hiển thị
            screen.blit(menu_text, menu_rect)
            screen.blit(game_over_text,game_over_rect)
            screen.blit(score_end,score_end_rect)
            screen.blit(score_end,score_end_rect)
            screen.blit(high_score_end,high_score_end_rect)
            screen.blit(back_menu,back_menu_rect)
            pygame.display.flip() # Cập nhật lại màn hình

            for event in pygame.event.get(): # đọc sự kiện ấn nút 
                if event.type == pygame.QUIT: # ấn nút thoát thì thoát chương trình
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s: # ấn nút s thì khởi động lại trò chơi
                        return True  # Bắt đầu trò chơi
                    elif event.key == pygame.K_q: # ấn nút q thì thoát chương trình
                        return False  # Thoát trò chơi
                    elif event.key == pygame.K_r:
                        game_over_music.stop()
                        game_intro()
                        title_music.stop()
                        return True

            clock.tick(30) # load lại mỗi 30 mili giây

        return False
    
    running = True # biến xác định trò chơi có đang chạy không
    restart_game = True # biến xác định trò chơi có khởi chạy lại không

    game_intro() # bật phần giới thiệu
    title_music.stop() # dừng nhạc khi bắt đầu

    while running: # khi trạng thái trò chơi là đang chạy
        
        if player.health <= 0: # nếu máu người chơi về 0
            Contra_Music.stop() # dừng nhạc chính của trò chơi
            game_over_music.play() # bật nhạc kết thúc trò chơi
            restart_game = show_menu(restart_game) # hien thi màn hình khởi động lại trò chơi
            if restart_game: 
                # Nếu chọn khởi tạo lại trò chơi
                # khởi tạo player
                player.health = player.max_health # làm đầy thanh máu
                player.is_dead = False 
                player.rect.x = WIDTH // 2
                player.rect.y = HEIGHT // 2

                # khởi tạo enemy ở vị trí ngẫu nhiên
                enemy.health = enemy.max_health
                enemy.is_dead = False
                enemy.current_frame = 0
                enemy.image = enemy.images_right[0]
                enemy.rect.x = random.randint(0, WIDTH - enemy.rect.width)

                score = 0 # điểm số về 0
                last_create_box = 0 # điểm số tạo hộp máu gần nhât
                
                last_create_box1 = 0 # điểm số tạo hộp nâng cấp gần nhât
                game_over_music.stop() # dừng nhạc kết thúc trò chơi

        for event in pygame.event.get(): # thoát game nếu ấn nút thoát
            if event.type == pygame.QUIT:
                running = False
                # Nếu health box bị ăn hết, tạo lại chúng
        # Khi điểm số người chơi lớn hơn 0, chia hết cho 5 và chưa tạo lại hộp máu ở điểm số đó thì tạo lại
        if len(health_box_group)==0:
            if score > 0 and score > last_create_box and score % 5 == 0 :
                create_heathbox()
                last_create_box = score
            #Khi điểm số người chơi lớn hơn 0, chia hết cho 10 và chưa tạo lại hộp nâng cấp ở điểm số đó thì tạo lại và giới hạn tốc bắn là 0.05 sẽ không xuất hiện nữa:
        if len(upgrade_box_group)==0:
            if score > 0 and score > last_create_box1 and score % 10 == 0 and player.shoot_delay > 0.05:
                create_upgrade()
                last_create_box1 = score
        upgrade_box_group.update(player) # kiểm tra va chạm giữa hộp nâng cấp và người chơi
        upgrade_box_group.draw(screen) # vẽ lại
        health_box_group.update(player) # kiểm tra va chạm giữa hộp máu và người chơi
        health_box_group.draw(screen) # vẽ lại
        Contra_Music.play() # bật nhạc chính lên
        all_sprites.update() # cập nhật lại các hình ảnh
        screen.blit(background_image, (0, 0)) # vẽ hình nền
        player.draw_health_bar() # vẽ thanh máu người chơi
        enemy.draw_health_bar() # vẽ thanh máu enemy
        all_sprites.draw(screen) # vẽ hình ảnh
        enemy.draw_score() # vẽ điểm số enemy đã tiêu diệt
        pygame.display.flip() # cập  nhật lại màn hình
        clock.tick(60) # cập nhật mỗi 60 mili giây

    pygame.quit() # thoát game
    sys.exit() # thoát chương trình


if __name__ == "__main__":
    main() 
    
