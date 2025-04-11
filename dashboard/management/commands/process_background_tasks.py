from django.core.management.base import BaseCommand
from background_task.models import Task
from background_task.process import process_tasks
import time

class Command(BaseCommand):
    help = 'Process background tasks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sleep',
            type=int,
            default=10,
            help='Sleep time between task processing cycles in seconds'
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting background task processor...')
        
        while True:
            try:
                # Process any pending tasks
                process_tasks()
                
                # Sleep for the specified time
                time.sleep(options['sleep'])
                
            except KeyboardInterrupt:
                self.stdout.write('Stopping background task processor...')
                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing tasks: {str(e)}'))
                time.sleep(options['sleep']) 