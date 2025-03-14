# accounts/utils.py (or wherever you prefer to put helper functions)

import pygame
import hashlib
import random
import os
from django.conf import settings

def generate_profile_picture(first_name, last_name, email, grid_size=5, square_size=50):
    seed = email
    random.seed(seed)
    
    # Define a color palette for the image.
    palette = [
        (0, 59, 60), (0, 57, 58), (0, 55, 56),
        (0, 53, 54), (0, 51, 52), (0, 49, 50),
        (0, 47, 48), (0, 45, 46), (0, 43, 44),
        (0, 41, 42), (0, 39, 40), (0, 38, 39),
        (0, 36, 37), (0, 34, 35), (0, 32, 33),
        (0, 39, 39)
    ]

    image_size = grid_size * square_size
    surface = pygame.Surface((image_size, image_size))
    
    # Fill the surface with a pattern.
    for row in range(grid_size):
        for col in range(grid_size):
            color = random.choice(palette)
            x1 = col * square_size
            y1 = row * square_size
            pygame.draw.rect(surface, color, (x1, y1, square_size, square_size))
    
    # Use first letter of first_name and first letter of last_name as initials.
    initials = (first_name[0] + last_name[0]).upper()
    
    # Render initials in the center.
    pygame.font.init()
    font_size = int(image_size // 1.5)
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(initials, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(image_size // 2, image_size // 2))
    surface.blit(text_surface, text_rect)
    
    # Save the image in MEDIA_ROOT/profile_pics.
    output_dir = os.path.join(settings.MEDIA_ROOT, "profile_pics")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # Use a unique filename; you could use a hash or a combination of names.
    file_name = f"{email}_profile_picture.png"
    output_path = os.path.join(output_dir, file_name)
    
    try:
        pygame.image.save(surface, output_path)
        print(f"Profile picture saved as {output_path}")
    except Exception as e:
        print("Error saving profile picture:", e)
    
    pygame.quit()
    # Return the relative path that Django will use.
    return f"profile_pics/{file_name}"


def create_empty_garden_image(user):
    pygame.init()
    
    grid_size = 9
    cell_size = 64
    width = grid_size * cell_size
    height = grid_size * cell_size
    
    surface = pygame.Surface((width, height))
    
    grass_img_path = os.path.join(settings.BASE_DIR, "garden", "static", "img", "grass.png")
    try:
        grass_img = pygame.image.load(grass_img_path)
        grass_img = pygame.transform.scale(grass_img, (width, height))
        surface.blit(grass_img, (0, 0))
    except Exception as e:
        print("Error loading grass background:", e)
        surface.fill((255, 255, 255))
    
    center_rect = pygame.Rect((5 - 1) * cell_size, (5 - 1) * cell_size, cell_size, cell_size)
    tree_img_path = os.path.join(settings.BASE_DIR, "garden", "static", "img", "temp-tree.png")
    try:
        tree_img = pygame.image.load(tree_img_path)
        tree_img = pygame.transform.scale(tree_img, (cell_size, cell_size))
        surface.blit(tree_img, center_rect)
    except Exception as e:
        print("Error loading tree image:", e)
    
    file_name = f"garden_state_user{user.id}.png"
    output_dir = os.path.join(settings.MEDIA_ROOT, "gardens")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, file_name)
    
    try:
        pygame.image.save(surface, output_path)
        print(f"Empty garden image saved to {output_path}")
    except Exception as e:
        print("Error saving empty garden image:", e)
    finally:
        pygame.quit()
    
    return output_path