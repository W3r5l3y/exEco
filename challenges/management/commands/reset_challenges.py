from django.core.management.base import BaseCommand
from django.utils import timezone
from challenges.models import UserChallenge, Challenge
from accounts.models import CustomUser

import random

class Command(BaseCommand):
    help = "Resets daily challenges every day and weekly challenges only on Mondays"

    def handle(self, *args, **kwargs):
        now = timezone.now()
        is_monday = now.weekday() == 0  # Check if today is Monday

        self.stdout.write(f"Today is {'Monday' if is_monday else 'Not Monday'}")

        # Reset daily challenges
        UserChallenge.objects.filter(challenge__challenge_type="daily").delete()
        self.stdout.write("Daily challenges reset!")

        # Fetch new daily challenges
        daily_challenges = list(Challenge.objects.filter(challenge_type="daily"))
        if len(daily_challenges) < 3:
            self.stdout.write("Not enough daily challenges in the database!")
            return

        daily_challenges = random.sample(daily_challenges, 3)

        # If it's Monday, reset weekly challenges
        if is_monday:
            UserChallenge.objects.filter(challenge__challenge_type="weekly").delete()
            self.stdout.write("Weekly challenges reset!")

        # Assign new daily challenges
        for user in CustomUser.objects.all():
            self.stdout.write(f"Assigning daily challenges to {user.email}")

            for challenge in daily_challenges:
                UserChallenge.objects.create(user=user, challenge=challenge)

            # Assign weekly challenges only if the user has less than 5 assigned
            current_weekly_count = UserChallenge.objects.filter(user=user, challenge__challenge_type="weekly").count()
            if current_weekly_count < 5:
                remaining_slots = 5 - current_weekly_count
                weekly_challenges = list(Challenge.objects.filter(challenge_type="weekly"))

                if len(weekly_challenges) >= remaining_slots:
                    weekly_challenges = random.sample(weekly_challenges, remaining_slots)
                    for challenge in weekly_challenges:
                        UserChallenge.objects.create(user=user, challenge=challenge)
                    self.stdout.write(f" Assigned {remaining_slots} new weekly challenges to {user.email}")
                else:
                    self.stdout.write(f" Not enough weekly challenges to fill all slots for {user.email}")

        self.stdout.write("🎯 Challenge reset complete!")
