from django.contrib import admin

from .models import BenchT, JudgeT, ReaderJudgeAssignment


@admin.register(JudgeT)
class JudgeTAdmin(admin.ModelAdmin):
    list_display = (
        'judge_code',
        'judge_name',
        'user',
        'seniority',
        'is_active',
    )
    search_fields = (
        'judge_code',
        'judge_name',
        'user__email',
        'user__first_name',
        'user__last_name',
    )
    list_filter = ('is_active',)


@admin.register(BenchT)
class BenchTAdmin(admin.ModelAdmin):
    list_display = (
        'bench_code',
        'bench_name',
        'judge',
        'from_date',
        'to_date',
        'is_active',
    )
    search_fields = (
        'bench_code',
        'bench_name',
        'judge__judge_name',
        'judge__judge_code',
    )
    list_filter = ('is_active', 'from_date', 'to_date')


@admin.register(ReaderJudgeAssignment)
class ReaderJudgeAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        'judge',
        'reader_user',
        'effective_from',
        'effective_to',
        'is_active',
    )
    search_fields = (
        'judge__judge_name',
        'judge__judge_code',
        'reader_user__email',
        'reader_user__first_name',
        'reader_user__last_name',
    )
    list_filter = ('is_active', 'effective_from', 'effective_to')
