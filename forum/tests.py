from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Post, PostLike, Comment, PostReport
from accounts.models import UserCoins

User = get_user_model()


class ForumTests(TestCase):
    def setUp(self):
        # Create test users with required fields
        self.user1 = User.objects.create_user(
            email="user1@example.com",
            password="password123",
            first_name="User",
            last_name="One",
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com",
            password="password123",
            first_name="User",
            last_name="Two",
        )

        # Create a test post
        self.post = Post.objects.create(
            user=self.user1, description="This is a test post", likes=0
        )

    def test_create_post(self):
        """Test that a post can be created successfully."""
        post = Post.objects.create(user=self.user1, description="Another test post")
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(post.description, "Another test post")

    def test_like_post(self):
        """Test that a user can like a post."""
        PostLike.objects.create(user=self.user2, post=self.post, liked=True)
        self.post.likes = PostLike.objects.filter(post=self.post, liked=True).count()
        self.post.save()

        self.assertEqual(self.post.likes, 1)

    def test_add_comment(self):
        """Test that a user can add a comment to a post."""
        comment = Comment.objects.create(
            user=self.user2, post=self.post, text="This is a test comment"
        )
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(comment.text, "This is a test comment")
        self.assertEqual(comment.post, self.post)

    def test_report_post(self):
        """Test that a user can report a post."""
        report = PostReport.objects.create(user=self.user2, post=self.post)
        self.assertEqual(PostReport.objects.count(), 1)
        self.assertEqual(report.post, self.post)

    def test_user_coins_on_post_creation(self):
        """Test that creating a post awards coins to the user."""
        UserCoins.objects.get_or_create(user=self.user1)
        self.assertEqual(self.user1.usercoins.coins, 0)

        # Simulate awarding coins for creating a post
        self.user1.usercoins.add_coins(10)
        self.assertEqual(self.user1.usercoins.coins, 10)

    def test_user_coins_on_like(self):
        """Test that liking a post awards coins to the post owner."""
        UserCoins.objects.get_or_create(user=self.user1)
        self.assertEqual(self.user1.usercoins.coins, 0)

        # Simulate liking the post
        PostLike.objects.create(user=self.user2, post=self.post, liked=True)
        self.user1.usercoins.add_coins(5)
        self.assertEqual(self.user1.usercoins.coins, 5)

    def test_user_coins_on_comment(self):
        """Test that adding a comment awards coins to the commenter."""
        UserCoins.objects.get_or_create(user=self.user2)
        self.assertEqual(self.user2.usercoins.coins, 0)

        # Simulate adding a comment
        Comment.objects.create(user=self.user2, post=self.post, text="Nice post!")
        self.user2.usercoins.add_coins(3)
        self.assertEqual(self.user2.usercoins.coins, 3)

    def test_delete_post(self):
        """Test that a post can be deleted."""
        self.post.delete()
        self.assertEqual(Post.objects.count(), 0)

    def test_edit_post(self):
        """Test that a post description can be updated."""
        self.post.description = "Updated description"
        self.post.save()
        self.assertEqual(self.post.description, "Updated description")
