from django.core.management.base import BaseCommand
from django.utils.timezone import now
from challenges.models import UserChallenge, Challenge
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Force refreshes all challenges (daily & weekly) immediately, regardless of the current day."

    def handle(self, *args, **kwargs):
        UserModel = get_user_model()
        users = UserModel.objects.all()

        # Delete all existing UserChallenges (clears daily & weekly)
        UserChallenge.objects.all().delete()
        self.stdout.write("All existing user challenges have been deleted.")

        # Fetch fresh daily and weekly challenges
        daily_challenges = list(Challenge.objects.filter(challenge_type="daily"))
        weekly_challenges = list(Challenge.objects.filter(challenge_type="weekly"))

        # Assign new challenges to each user
        for user in users:
            assigned_daily = daily_challenges[:3]  # Select first 3 daily challenges
            assigned_weekly = weekly_challenges[:5]  # Select first 5 weekly challenges

            for challenge in assigned_daily + assigned_weekly:
                UserChallenge.objects.create(user=user, challenge=challenge)

        self.stdout.write("New daily and weekly challenges have been assigned to all users.")
        self.stdout.write("Challenge refresh completed successfully!")
