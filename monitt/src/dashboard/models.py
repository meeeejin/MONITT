from __future__ import unicode_literals

from django.db import models
from django.db import models

# Create your models here.
class UploadFile(models.Model):
    testfile = models.FileField(upload_to='files', blank=False, null=False)

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [app_label]'
# into your database.

class ActualResponses(models.Model):
    test = models.ForeignKey('TestHistory', primary_key=True)
    return_code = models.IntegerField()
    response_time = models.IntegerField()
    header = models.TextField()
    body = models.TextField()

    class Meta:
        managed = True
        db_table = 'actual_responses'


class ExpectedResponses(models.Model):
    test = models.ForeignKey('TestHistory', primary_key=True)
    return_code = models.IntegerField()
    response_time = models.IntegerField()
    header = models.TextField()
    body = models.TextField()

    class Meta:
        managed = True
        db_table = 'expected_responses'


class Notifications(models.Model):
    notification_id = models.IntegerField(primary_key=True)
    user_id = models.CharField(max_length=11)
    testcase_id = models.CharField(max_length=100)
    notification_type = models.CharField(max_length=20)
    fail_count = models.IntegerField()
    success_count = models.IntegerField()
    total_count = models.IntegerField()
    final_status = models.CharField(max_length=10)
    notification_count = models.IntegerField()
    register_time = models.DateTimeField()
    testcase_name = models.CharField(max_length=31)

    class Meta:
        managed = True
        db_table = 'notifications'


class Requests(models.Model):
    test = models.ForeignKey('TestHistory', primary_key=True)
    method = models.CharField(max_length=10)
    url = models.CharField(max_length=255)
    url_parameter = models.TextField()
    header = models.TextField()
    body = models.TextField()

    class Meta:
        managed = True
        db_table = 'requests'


class Results(models.Model):
    test = models.ForeignKey('TestHistory', primary_key=True)
    result = models.CharField(max_length=10)
    error_list = models.TextField()
    finished_time = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'results'


class Schedulings(models.Model):
    scheduling_id = models.IntegerField(primary_key=True)
    user_id = models.CharField(max_length=11)
    testcase_id = models.CharField(max_length=100)
    method = models.CharField(max_length=15)
    frequency = models.CharField(max_length=40)
    times = models.IntegerField()
    testcase_name = models.CharField(max_length=31)
    request_method = models.CharField(max_length=10)
    request_url = models.CharField(max_length=255)
    register_time = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'schedulings'


class TestHistory(models.Model):
    test_id = models.AutoField(primary_key=True)
    testcase_id = models.CharField(max_length=100)
    user_id = models.CharField(max_length=11)
    testcase_name = models.CharField(max_length=31)
    secret_key = models.CharField(max_length=11)

    class Meta:
        managed = True
        db_table = 'test_history'
