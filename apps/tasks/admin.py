# Register your models here.
from .models import Board, Column, Task
from django.contrib import admin

admin.site.register(Board)
admin.site.register(Column)
admin.site.register(Task)
