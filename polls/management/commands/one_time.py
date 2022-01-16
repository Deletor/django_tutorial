from django.core.management.base import BaseCommand
from django.utils import timezone
from timeit import default_timer as timer
from datetime import timedelta
from polls.models import Question, Choice


class Command(BaseCommand):
    help = 'Displays current time'

    def handle(self, *args, **options):
        start = timer()

        queryset = Choice.objects.all()
        for item in queryset:
            print(item.question)

        query = Question.objects.all().filter()
        for item in query:
            print(item)

        end = timer()
        print(timedelta(seconds=end-start))
