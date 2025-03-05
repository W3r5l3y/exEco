from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Bins, Items
from accounts.models import UserPoints, CustomUser

from django.urls import reverse
from django.template.loader import render_to_string
# Create your tests here.
class BingameTestCase(TestCase):
    def setUp(self):
        #Create a user because of @login_required
        self.user = get_user_model().objects.create_user(
            email="testuser@gmail.com",
            first_name="Test",
            last_name="User",
            password="password123",
        )
        self.client.login(email="testuser@gmail.com", password="password123")
        
        #Create the bins & items - 7 items in total, as it ensures the test getting 6 random items works
        self.bin1 = Bins.objects.create(
            bin_name="Plastic",
            bin_image="/img/bins/plastic.png"
        )
        
        self.bin2 = Bins.objects.create(
            bin_name="Glass",
            bin_image="/img/bins/glass.png"
        )
        
        self.bin3 = Bins.objects.create(
            bin_name="Card and Paper",
            bin_image="/img/bins/card_paper.png"
        )
        
        self.bin4 = Bins.objects.create(
            bin_name="Tins and Cans",
            bin_image="/img/bins/tins_cans.png"
        )
        
        self.item1 = Items.objects.create(
            item_name="Plastic Bottle",
            item_image="/img/items/plastic_bottle.png",
            bin_id=self.bin1
        )
        
        self.item2 = Items.objects.create(
            item_name="Glass Bottle",
            item_image="/img/items/glass_bottle.png",
            bin_id=self.bin2
        )
        
        self.item3 = Items.objects.create(
            item_name="Cardboard",
            item_image="/img/items/cardboard.png",
            bin_id=self.bin3
        )
        
        self.item4 = Items.objects.create(
            item_name="Chip Packet",
            item_image="/img/items/chip_packet.png",
            bin_id=self.bin1
        )
        
        self.item5 = Items.objects.create(
            item_name="Drink Can",
            item_image="/img/items/drink_can.png",
            bin_id=self.bin4
        )
        
        self.item6 = Items.objects.create(
            item_name="Envelope",
            item_image="/img/items/envelope.png",
            bin_id=self.bin3
        )
        
        self.item7 = Items.objects.create(
            item_name="Broken mirror",
            item_image="/img/items/broken_mirror.png",
            bin_id=self.bin2
        )
    
    #Check that the bins and items have correct ID's, as the ids would be produced automatically by the model
    def test_bin_and_item_ids(self):
        #Check initial bin IDs are correct
        self.assertEqual(self.bin1.bin_id, 1, "Bin1 should have ID 1")
        self.assertEqual(self.bin2.bin_id, 2, "Bin2 should have ID 2")
        self.assertEqual(self.bin3.bin_id, 3, "Bin3 should have ID 3")
        self.assertEqual(self.bin4.bin_id, 4, "Bin4 should have ID 4")
        
        #Check initial item IDs are correct
        self.assertEqual(self.item1.item_id, 1, "Item1 should have ID 1")
        self.assertEqual(self.item2.item_id, 2, "Item2 should have ID 2")    
        self.assertEqual(self.item3.item_id, 3, "Item3 should have ID 3")
        self.assertEqual(self.item4.item_id, 4, "Item4 should have ID 4")
        self.assertEqual(self.item5.item_id, 5, "Item5 should have ID 5")
        self.assertEqual(self.item6.item_id, 6, "Item6 should have ID 6")
        self.assertEqual(self.item7.item_id, 7, "Item7 should have ID 7")   
        
        #Check that the items 'correct bin id' is linked to the correct bin, and the link works. (Ensuring foreign key is working)
        self.assertEqual(self.item1.bin_id, self.bin1, "Item1 should be linked to Bin1")
        self.assertEqual(self.item2.bin_id, self.bin2, "Item2 should be linked to Bin2")
        self.assertEqual(self.item3.bin_id, self.bin3, "Item3 should be linked to Bin3")
        self.assertEqual(self.item4.bin_id, self.bin1, "Item4 should be linked to Bin1")
        self.assertEqual(self.item5.bin_id, self.bin4, "Item5 should be linked to Bin4")
        self.assertEqual(self.item6.bin_id, self.bin3, "Item6 should be linked to Bin3")
        self.assertEqual(self.item7.bin_id, self.bin2, "Item7 should be linked to Bin2")
        
        #Check bins/ items exist in database
        self.assertTrue(Bins.objects.filter(bin_id=self.bin1.bin_id).exists(), "Bin1 should exist in database")
        self.assertTrue(Items.objects.filter(item_id=self.item1.item_id).exists(), "Bin2 should exist in database")
    
    def test_game_view(self):
        response = self.client.get(reverse("bingame"))
        
        #Check page loads correctly
        self.assertEqual(response.status_code, 200, "Game view should return code 200")
        self.assertTemplateUsed(response, "bingame/bingame.html", "Game view should use the correct template")
        
        #Check that the bins are included in the page
        self.assertIn('bins', response.context, "Bins should be included in the context (response)")
        self.assertEqual(list(response.context['bins']), [self.bin1, self.bin2, self.bin3, self.bin4], "The same bins should be in the context (response)")
        
        #Check that the items are included in the page, and there are 6 items called out of the total (7 items in setup so ensures checking its 6 or less is correct)
        self.assertIn('items', response.context, "Items should be included in the context (response)")
        self.assertLessEqual(len(response.context['items']), 6, "There should be 6 or less items in the context (response)") 
        
        #Check that the items are instances of the Items model, means can call the attributes as .data instead of it being a dictionary or incorrect format
        for item in response.context['items']:
            self.assertIsInstance(item, Items, "Items should be instances of the Items model")
    
    #Test that the leaderboard is updated correctly
    def test_update_leaderboard(self):
        
        #Send a score of 10 to view to update the leaderboard
        response = self.client.post(
            reverse('update-leaderboard'),
            {'user_score': 10}
        )
        
        #Check that request is successful
        self.assertEqual(response.status_code, 200, "Update leaderboard should return code 200 - indicating success")

        #Check the score is correctly updated in the database
        user_points = UserPoints.objects.get(user=self.user)
        self.assertEqual(user_points.user, self.user, "User points should be linked to the correct user")
        self.assertEqual(user_points.bingame_points, 10, "User Bingame points should be updated to 10")
        
        
    #Test that get_bingame_leaderboard returns the correct leaderboard
    def test_get_bingame_leaderboard(self):
        # Generate mock users to test leaderboard
        user2 = CustomUser.objects.create_user(
            email="user2@example.com",
            first_name="User",
            last_name="Two",
            password="password123",
        )
        user3 = CustomUser.objects.create_user(
            email="user3@example.com",
            first_name="User",
            last_name="Three",
            password="password123",
        )

        # Give scores to the mock users
        UserPoints.objects.create(user=self.user, bingame_points=15)
        UserPoints.objects.create(user=user2, bingame_points=30)
        UserPoints.objects.create(user=user3, bingame_points=20)

        # Get bingame leaderboard
        response = self.client.get(reverse('get_bingame_leaderboard'))

        #Check that the request is successful
        self.assertEqual(response.status_code, 200)

        #Get the json response returned
        leaderboard = response.json()

        # Check 3 entries are returned
        self.assertEqual(len(leaderboard), 3)

        # Check users scores are sorted in ascending order: 30, 20, 15 based of of mock scores
        self.assertEqual(leaderboard[0]['username'], 'User Two')
        self.assertEqual(leaderboard[0]['bingame_points'], 30)

        self.assertEqual(leaderboard[1]['username'], 'User Three')
        self.assertEqual(leaderboard[1]['bingame_points'], 20)

        self.assertEqual(leaderboard[2]['username'], 'Test User')
        self.assertEqual(leaderboard[2]['bingame_points'], 15)

    #Test that the fetch random items view works
    def test_fetch_random_items(self):
        # Get random items
        response = self.client.get(reverse('fetch_random_items'))

        # Verify that the http response is successful
        self.assertEqual(response.status_code, 200)

        # Verify that the response contains the items
        data = response.json()
        self.assertIn('items', data)

        items = data['items']

        #Check that 6 items are returned
        self.assertEqual(len(items), 6)

        #Check that the items have correct fields
        for item in items:
            self.assertIn('id', item)
            self.assertIn('bin_id', item)
            self.assertIn('item_name', item)
            self.assertIn('item_image', item)
    
    def test_populate_bins_and_items(self):
        pass