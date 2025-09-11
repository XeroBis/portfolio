from django.core.management.base import BaseCommand
from apps.newsfeed.models import FeedFetchTask


class Command(BaseCommand):
    help = 'Check status of RSS fetch tasks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--task-id',
            type=int,
            help='Check specific task ID',
        )

    def handle(self, *args, **options):
        if options['task_id']:
            try:
                task = FeedFetchTask.objects.get(id=options['task_id'])
                self.show_task_details(task)
            except FeedFetchTask.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Task {options["task_id"]} not found'))
        else:
            # Show recent tasks
            tasks = FeedFetchTask.objects.all()[:10]
            if not tasks:
                self.stdout.write('No fetch tasks found')
                return
                
            self.stdout.write('\nRecent fetch tasks:')
            self.stdout.write('-' * 80)
            
            for task in tasks:
                status_color = self.get_status_color(task.status)
                self.stdout.write(f'Task {task.id}: {status_color(task.status.upper())} - {task.created_at.strftime("%Y-%m-%d %H:%M:%S")}')
                if task.progress_text:
                    self.stdout.write(f'  Progress: {task.progress_text}')
                if task.status in ['running', 'completed']:
                    self.stdout.write(f'  Articles created: {task.articles_created}')
                    if task.total_feeds > 0:
                        self.stdout.write(f'  Progress: {task.processed_feeds}/{task.total_feeds} feeds ({task.progress_percentage}%)')
                if task.errors:
                    error_count = len(task.errors.split('\n'))
                    self.stdout.write(f'  Errors: {error_count}')
                self.stdout.write('')

    def show_task_details(self, task):
        """Show detailed information about a specific task"""
        status_color = self.get_status_color(task.status)
        
        self.stdout.write(f'\nTask {task.id} Details:')
        self.stdout.write('=' * 50)
        self.stdout.write(f'Status: {status_color(task.status.upper())}')
        self.stdout.write(f'Created: {task.created_at.strftime("%Y-%m-%d %H:%M:%S")}')
        
        if task.started_at:
            self.stdout.write(f'Started: {task.started_at.strftime("%Y-%m-%d %H:%M:%S")}')
        
        if task.completed_at:
            self.stdout.write(f'Completed: {task.completed_at.strftime("%Y-%m-%d %H:%M:%S")}')
            duration = task.completed_at - task.started_at
            self.stdout.write(f'Duration: {duration}')
        
        if task.total_feeds > 0:
            self.stdout.write(f'Progress: {task.processed_feeds}/{task.total_feeds} feeds ({task.progress_percentage}%)')
        
        self.stdout.write(f'Articles created: {task.articles_created}')
        
        if task.progress_text:
            self.stdout.write(f'Current progress: {task.progress_text}')
        
        if task.errors:
            self.stdout.write(f'\nErrors encountered:')
            self.stdout.write('-' * 20)
            for error in task.errors.split('\n'):
                if error.strip():
                    self.stdout.write(f'  {error}')

    def get_status_color(self, status):
        """Get appropriate color style for status"""
        color_map = {
            'pending': self.style.WARNING,
            'running': self.style.NOTICE,
            'completed': self.style.SUCCESS,
            'failed': self.style.ERROR,
        }
        return color_map.get(status, self.style.NOTICE)