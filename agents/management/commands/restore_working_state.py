from django.core.management.base import BaseCommand
from django.core.management import call_command
import subprocess
import os

class Command(BaseCommand):
    help = 'Restore system to working state from backup'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm restoration (required to prevent accidental use)',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.ERROR('❌ Restoration requires --confirm flag to prevent accidents')
            )
            self.stdout.write('Usage: python manage.py restore_working_state --confirm')
            return

        self.stdout.write(
            self.style.WARNING('🔄 Starting restoration to working state...')
        )

        try:
            # Step 1: Switch to stable branch
            self.stdout.write('📦 Switching to stable branch...')
            result = subprocess.run(['git', 'checkout', 'stable-working-agents'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                self.stdout.write(
                    self.style.ERROR(f'❌ Git checkout failed: {result.stderr}')
                )
                return

            # Step 2: Run migrations to ensure database is up to date
            self.stdout.write('🗄️  Running migrations...')
            call_command('migrate')

            # Step 3: Restore agents from backup
            backup_file = 'backups/restore_agents.json'
            if os.path.exists(backup_file):
                self.stdout.write('🔧 Restoring agents from backup...')
                call_command('loaddata', backup_file)
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️  No agents backup file found')
                )

            # Step 4: Restore users and wallet if needed
            user_backup = 'backups/restore_users_wallet.json'
            if os.path.exists(user_backup):
                self.stdout.write('👥 Restoring users and wallet data...')
                call_command('loaddata', user_backup)

            # Step 5: Collect static files
            self.stdout.write('📁 Collecting static files...')
            call_command('collectstatic', '--noinput')

            self.stdout.write(
                self.style.SUCCESS('✅ Restoration completed successfully!')
            )
            self.stdout.write('🔒 All agents should be locked and working')
            self.stdout.write('🌐 Test the system at http://localhost:8000')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Restoration failed: {str(e)}')
            )
            self.stdout.write('💡 Check logs and try manual restoration')