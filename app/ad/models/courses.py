from core.base import BaseModelV2
from django.db import models
import uuid
import datetime
from .teachers import Teacher
#wdsa

class Course(BaseModelV2):
    course_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    course_name = models.CharField(max_length=30)
    duration = models.DurationField(
        default=datetime.timedelta(days = 30),
        help_text="Duration of the course(e.g, '30 days')."
    )
    teacher = models.ForeignKey(
        Teacher,
        null=True,
        blank=True,
        related_name="courses",
        on_delete=models.SET_NULL
    )
    LEVEL = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advance', 'Advance'),
    ] 

    level = models.CharField(
        max_length=50,
        choices=LEVEL,
        default="beginner"

    )    
    
    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"
    
    def __str__(self):
        return (f"{self.course_name} {self.get_level_display()}")
