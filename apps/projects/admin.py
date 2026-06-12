from django.contrib import admin
from .models import Project, ProjectMember

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'workspace_id', 'status', 'priority', 'created_by', 'created_at')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('name', 'code', 'workspace_id', 'description')
    readonly_fields = ('slug', 'created_at', 'updated_at')

@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'user', 'role', 'workspace_id', 'removed_at', 'created_at')
    list_filter = ('role', 'created_at', 'removed_at')
    search_fields = ('project__name', 'user__username', 'user__email', 'workspace_id')
    readonly_fields = ('created_at', 'updated_at')
