from core.base import BaseModelV2
from django.db import models
from ad.models import Course

class CourseChapter(BaseModelV2):
    title = models.CharField(max_length=100)
    duration = models.CharField(max_length=10)
    description = models.TextField(null=True, blank=True)

    course = models.ForeignKey(
        Course,
        null=True,
        blank=True,
        related_name="chapters",
        on_delete=models.CASCADE,
        db_column="course_id"

    )

    class Meta:
        db_table = "tbl_course_chapters"
        verbose_name = "Course Chapter"
        verbose_name_plural = "Course Chapters"
    
    def __str__(self):
        return f"{self.title} {self.course.course_name}"