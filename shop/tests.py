from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import ShopItems
from accounts.models import CustomUser, UserCoins
from inventory.models import Inventory
import os
import shutil
from django.conf import settings

"""
MODELS TESTING
"""


class ShopModelTests(TestCase):

    def setUp(self):

        # Create test media directory if it doesn’t exist
        self.test_media_dir = os.path.join(settings.BASE_DIR, "shop/static/img/")
        os.makedirs(self.test_media_dir, exist_ok=True)

        # Create a temporary image file inside the test media directory
        self.test_image_path = os.path.join(self.test_media_dir, "test_image.png")
        with open(self.test_image_path, "wb") as f:
            f.write(b"file_content")

        # Create a shop item instance
        self.shop_item = ShopItems.objects.create(
            name="Test Item",
            description="Some form of item",
            image="/img/test_plant_snake.png",
            cost=50,
        )

        self.test_images = [self.test_image_path]

    def test_shop_item_creation(self):
        # Check if shop item was created correctly
        self.assertEqual(self.shop_item.name, "Test Item")
        self.assertEqual(self.shop_item.description, "Some form of item")
        self.assertEqual(self.shop_item.cost, 50)
        self.assertTrue(self.shop_item.image)

    def test_shop_item_str(self):
        # Check __str__ method for readability
        self.assertEqual(str(self.shop_item), "Test Item - 50 coins")

    def tearDown(self):
        # Delete test images
        for image_path in self.test_images:
            if os.path.exists(image_path):
                os.remove(image_path)
            # Ensure 'static/shop/' is fully removed
            # Force delete the entire static/shop/ directory
        # Force delete the entire static/shop/ directory
        static_shop_dir = os.path.join(settings.BASE_DIR, "static/shop/")
        shutil.rmtree(static_shop_dir, ignore_errors=True)


"""
VIEWS TESTING
"""


class ShopViewsTests(TestCase):

    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
            password="password123",
        )

        # Create test media directory if it doesn’t exist
        self.test_media_dir = os.path.join(settings.BASE_DIR, "shop/static/img/")
        os.makedirs(self.test_media_dir, exist_ok=True)

        self.test_images = []

        # Create a temporary image file inside the test media directory
        self.test_image_path = os.path.join(self.test_media_dir, "test_plant_snake.png")
        with open(self.test_image_path, "wb") as f:
            f.write(b"file_content")

        self.test_images.append(self.test_image_path)

        # Create test shop item
        self.shop_item = ShopItems.objects.create(
            name="Test Plant",
            description="Snake plant - best at air purification -those who know, know",
            image="shop/static/img/test_plant_snake.png",
            cost=300,
        )

        # Create user coins
        self.user_coins = UserCoins.objects.create(user=self.user, coins=500)

        # Create client and login user
        self.client = Client()
        self.client.login(email="testuser@example.com", password="password123")

        # Create inventory for user
        self.inventory = Inventory.objects.create(user=self.user)

    def test_shop_view(self):
        # Test if the shop page loads successfully
        response = self.client.get(reverse("shop"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shop/shop.html")
        self.assertIn("shop_items", response.context)
        self.assertEqual(response.context["shop_items"].count(), 1)

    def test_buy_item_success(self):
        # Test purchasing an item successfully
        url = reverse("buy_item", kwargs={"item_id": self.shop_item.itemId})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding="utf8"),
            {"success": "Item purchased successfully"},
        )

        # Check that the user's coins decreased
        self.user_coins.refresh_from_db()
        self.assertEqual(self.user_coins.coins, 200)  # 500 - 300

        # Check if item was added to inventory
        self.assertEqual(self.inventory.items.count(), 1)

    def test_buy_item_insufficient_coins(self):
        # Test insufficient coins
        self.user_coins.coins = 100
        self.user_coins.save()

        url = reverse("buy_item", kwargs={"item_id": self.shop_item.itemId})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            str(response.content, encoding="utf8"), {"lowbalance": "Not enough coins"}
        )

        # Confirm that no item was added
        self.assertEqual(self.inventory.items.count(), 0)

    def test_buy_item_invalid_item(self):
        # Try purchasing a non-existent item
        url = reverse("buy_item", kwargs={"item_id": 9999})  # Non-existent ID
        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(
            str(response.content, encoding="utf8"), {"error": "Item not found"}
        )

    def test_buy_item_get_request(self):
        # Ensure GET requests are rejected
        url = reverse("buy_item", kwargs={"item_id": self.shop_item.itemId})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            str(response.content, encoding="utf8"), {"error": "POST request required."}
        )

    def tearDown(self):
        # Clean up after tests
        for image_path in self.test_images:
            if os.path.exists(image_path):
                os.remove(image_path)

        # Force delete the entire static/shop/ directory
        static_shop_dir = os.path.join(settings.BASE_DIR, "static/shop/")
        shutil.rmtree(static_shop_dir, ignore_errors=True)
