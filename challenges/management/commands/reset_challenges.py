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

        self.stdout.write(
            f"Executing challenge reset. Today is {'Monday' if is_monday else 'not Monday'}."
        )

        # Reset daily challenges for all users
        UserChallenge.objects.filter(challenge__challenge_type="daily").delete()
        self.stdout.write("Daily challenges have been reset.")

        # Fetch new daily challenges
        daily_challenges = list(Challenge.objects.filter(challenge_type="daily"))
        if len(daily_challenges) < 3:
            self.stdout.write(
                "Error: Not enough daily challenges available in the database."
            )
            return

        daily_challenges = random.sample(daily_challenges, 3)

        # Reset weekly challenges on Mondays
        if is_monday:
            UserChallenge.objects.filter(challenge__challenge_type="weekly").delete()
            self.stdout.write("Weekly challenges have been reset.")

        # Assign challenges to all users
        for user in CustomUser.objects.all():
            self.stdout.write(f"Assigning challenges to user: {user.email}")

            # Assign daily challenges
            for challenge in daily_challenges:
                UserChallenge.objects.create(user=user, challenge=challenge)

            # Ensure the user has five weekly challenges
            user_weekly_challenges = UserChallenge.objects.filter(
                user=user, challenge__challenge_type="weekly"
            )
            if user_weekly_challenges.count() < 5:
                missing_slots = 5 - user_weekly_challenges.count()
                available_weekly_challenges = list(
                    Challenge.objects.filter(challenge_type="weekly")
                )

                if len(available_weekly_challenges) >= missing_slots:
                    assigned_weekly_challenges = random.sample(
                        available_weekly_challenges, missing_slots
                    )
                    for challenge in assigned_weekly_challenges:
                        UserChallenge.objects.create(user=user, challenge=challenge)
                    self.stdout.write(
                        f"Assigned {missing_slots} additional weekly challenges to user: {user.email}"
                    )
                else:
                    self.stdout.write(
                        f"Warning: Not enough weekly challenges available to fill all slots for user: {user.email}."
                    )

        self.stdout.write("Challenge reset process completed successfully.")
