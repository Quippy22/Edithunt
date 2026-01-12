import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import CustomUser, Bounty, Tag, Submission
from faker import Faker
from decimal import Decimal

class Command(BaseCommand):
    help = 'Populates the database with fake data for testing and presentation.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Deleting old data...')
        # Clear existing data to avoid duplicates/conflicts (optional, be careful in prod!)
        Submission.objects.all().delete()
        Bounty.objects.all().delete()
        Tag.objects.all().delete()
        CustomUser.objects.exclude(is_superuser=True).delete()

        fake = Faker('ro_RO')
        
        # 1. Create Tags
        self.stdout.write('Creating tags...')
        tag_names = [
            "Gaming", "Vlog", "Documentary", "Music Video", "Short Film", 
            "Commercial", "Tutorial", "Social Media", "Wedding", "Corporate",
            "Trailers", "Educational", "Animation", "Montage"
        ]
        tags = []
        for name in tag_names:
            tag, created = Tag.objects.get_or_create(name=name)
            tags.append(tag)

        # 2. Create Users
        self.stdout.write('Creating users...')
        
        # Demo Creator
        demo_creator, _ = CustomUser.objects.get_or_create(username='creator', email='creator@example.com')
        demo_creator.set_password('password123')
        demo_creator.role = 'creator'
        demo_creator.bio = "I am a content creator looking for the best editors!"
        demo_creator.save()

        # Demo Editor
        demo_editor, _ = CustomUser.objects.get_or_create(username='editor', email='editor@example.com')
        demo_editor.set_password('password123')
        demo_editor.role = 'editor'
        demo_editor.bio = "Professional editor ready to hunt bounties."
        demo_editor.save()

        creators = [demo_creator]
        editors = [demo_editor]

        # Random Creators
        for _ in range(10):
            u = CustomUser.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password='password123',
                role='creator',
                bio=fake.paragraph(nb_sentences=3)
            )
            creators.append(u)

        # Random Editors
        for _ in range(15):
            u = CustomUser.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password='password123',
                role='editor',
                bio=fake.paragraph(nb_sentences=3)
            )
            editors.append(u)

        # 3. Create Bounties
        self.stdout.write('Creating bounties...')
        bounties = []
        
        # Helper to get realistic footage links
        def get_footage_link():
            return "https://www.youtube.com/watch?v=" + fake.bothify(text='???????????')

        for _ in range(30):
            creator = random.choice(creators)
            is_active = random.random() > 0.3 # 70% active
            
            if is_active:
                status = 'active'
                deadline = timezone.now() + timedelta(days=random.randint(1, 30))
            else:
                status = random.choice(['completed', 'completed', 'in_review']) # completed is more likely
                deadline = timezone.now() - timedelta(days=random.randint(1, 10))

            budget_min = Decimal(random.randint(50, 1000))
            budget_max = budget_min + Decimal(random.randint(50, 500)) if random.random() > 0.5 else None

            bounty = Bounty.objects.create(
                creator=creator,
                title=fake.catch_phrase(),
                description=fake.text(max_nb_chars=500),
                footage_link=get_footage_link(),
                budget_min=budget_min,
                budget_max=budget_max,
                deadline=deadline,
                status=status
            )
            
            # Add random tags
            bounty.tags.set(random.sample(tags, k=random.randint(1, 4)))
            bounties.append(bounty)

        # 4. Create Submissions
        self.stdout.write('Creating submissions...')
        for bounty in bounties:
            # Random number of submissions for each bounty
            num_submissions = random.randint(0, 5)
            
            # If bounty is completed, ensure at least one submission and one winner
            if bounty.status == 'completed' and num_submissions == 0:
                num_submissions = 1
            
            bounty_submissions = []
            for _ in range(num_submissions):
                editor = random.choice(editors)
                # Ensure editor hasn't already submitted to this bounty
                if not Submission.objects.filter(bounty=bounty, editor=editor).exists():
                    sub = Submission.objects.create(
                        bounty=bounty,
                        editor=editor,
                        file_link=get_footage_link(), # reuse fake link generator
                        is_winner=False
                    )
                    bounty_submissions.append(sub)
            
            # If completed, pick a winner
            if bounty.status == 'completed' and bounty_submissions:
                winner = random.choice(bounty_submissions)
                winner.is_winner = True
                winner.save()

        self.stdout.write(self.style.SUCCESS('Database populated successfully!'))
        self.stdout.write(f'Created {len(tags)} tags, {len(creators)} creators, {len(editors)} editors, {len(bounties)} bounties.')
