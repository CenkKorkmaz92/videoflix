from django.core.management.base import BaseCommand
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from authentication.models import CustomUser


class Command(BaseCommand):
    help = 'Get activation links for inactive users or activate users directly'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email of the user to get activation link for',
        )
        parser.add_argument(
            '--activate',
            action='store_true',
            help='Directly activate the user instead of showing activation link',
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all inactive users',
        )

    def handle(self, *args, **options):
        if options['list']:
            self.list_inactive_users()
            return

        if options['email']:
            try:
                user = CustomUser.objects.get(email=options['email'])
                if user.is_active:
                    self.stdout.write(
                        self.style.WARNING(f'User {user.email} is already active')
                    )
                    return

                if options['activate']:
                    user.is_active = True
                    user.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'User {user.email} has been activated successfully!')
                    )
                else:
                    self.show_activation_link(user)

            except CustomUser.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User with email {options["email"]} does not exist')
                )
        else:
            self.stdout.write(
                self.style.ERROR('Please provide an email with --email or use --list to see inactive users')
            )

    def list_inactive_users(self):
        inactive_users = CustomUser.objects.filter(is_active=False).order_by('-date_joined')
        if not inactive_users:
            self.stdout.write(self.style.SUCCESS('No inactive users found'))
            return

        self.stdout.write(self.style.SUCCESS('Inactive users:'))
        for user in inactive_users:
            self.stdout.write(f'- {user.email} (joined: {user.date_joined})')

    def show_activation_link(self, user):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        activation_link = f"http://localhost:3000/pages/auth/activate.html?uid={uid}&token={token}"
        
        self.stdout.write(self.style.SUCCESS(f'Activation link for {user.email}:'))
        self.stdout.write(activation_link)
        self.stdout.write('')
        self.stdout.write('You can also activate the user directly by running:')
        self.stdout.write(f'python manage.py activate_user --email {user.email} --activate')
