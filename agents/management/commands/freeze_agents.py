from django.core.management.base import BaseCommand
from agents.models import Agent

class Command(BaseCommand):
    help = 'Lock all currently active agents to prevent modifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--unlock',
            action='store_true',
            help='Unlock all agents instead of locking them',
        )

    def handle(self, *args, **options):
        if options['unlock']:
            # Unlock all agents
            updated = Agent.objects.filter(is_locked=True).update(is_locked=False)
            self.stdout.write(
                self.style.SUCCESS(f'✅ Unlocked {updated} agents')
            )
        else:
            # Lock all active agents
            active_agents = Agent.objects.filter(is_active=True, is_locked=False)
            agent_names = list(active_agents.values_list('name', flat=True))
            updated = active_agents.update(is_locked=True)
            
            self.stdout.write(
                self.style.SUCCESS(f'🔒 Locked {updated} active agents:')
            )
            for name in agent_names:
                self.stdout.write(f'  - {name}')
            
            self.stdout.write(
                self.style.WARNING('⚠️  Locked agents cannot be modified until unlocked')
            )