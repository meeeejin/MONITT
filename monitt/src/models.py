# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models


class ActualResponses(models.Model):
    test = models.ForeignKey('TestHistory', primary_key=True)
    return_code = models.IntegerField()
    response_time = models.IntegerField()
    header = models.TextField()
    body = models.TextField()

    class Meta:
        managed = False
        db_table = 'actual_responses'


class ExpectedResponses(models.Model):
    test = models.ForeignKey('TestHistory', primary_key=True)
    return_code = models.IntegerField()
    response_time = models.IntegerField()
    header = models.TextField()
    body = models.TextField()

    class Meta:
        managed = False
        db_table = 'expected_responses'


class Notifications(models.Model):
    testcase_id = models.CharField(unique=True, max_length=42)
    notification_type = models.CharField(max_length=20)
    fail_count = models.IntegerField()
    success_count = models.IntegerField()
    total_count = models.IntegerField()
    final_status = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'notifications'


class Requests(models.Model):
    test = models.ForeignKey('TestHistory', primary_key=True)
    method = models.CharField(max_length=10)
    url = models.CharField(max_length=255)
    url_parameter = models.TextField()
    header = models.TextField()
    body = models.TextField()

    class Meta:
        managed = False
        db_table = 'requests'


class Results(models.Model):
    test = models.ForeignKey('TestHistory', primary_key=True)
    result = models.CharField(max_length=10)
    error_list = models.TextField()

    class Meta:
        managed = False
        db_table = 'results'


class TestHistory(models.Model):
    test_id = models.IntegerField(primary_key=True)
    testcase_id = models.CharField(max_length=42)
    user_id = models.CharField(max_length=11)
    testcase_name = models.CharField(max_length=31)
    secret_key = models.CharField(max_length=11)

    class Meta:
        managed = False
        db_table = 'test_history'
