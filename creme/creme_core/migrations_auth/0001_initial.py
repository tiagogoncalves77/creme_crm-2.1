# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core import validators
from django.db import models, migrations
from django.utils import timezone


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='name')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', to_field='id')),
                ('codename', models.CharField(max_length=100, verbose_name='codename')),
            ],
            options={
                'ordering': ('content_type__app_label', 'content_type__model', 'codename'),
                'unique_together': set([('content_type', 'codename')]),
                'verbose_name': 'permission',
                'verbose_name_plural': 'permissions',
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=80, verbose_name='name')),
                ('permissions', models.ManyToManyField(to='auth.Permission', verbose_name='permissions', blank=True)),
            ],
            options={
                'verbose_name': 'group',
                'verbose_name_plural': 'groups',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, max_length=30, verbose_name='username', validators=[validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username.', 'invalid')])),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(max_length=75, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=timezone.now, verbose_name='date joined')),

                # These 2 lines have been commented during the 1.6 dev cycle
                # (because they made migrations test case fail -- with PostGre -- & were useless for us)
                # but all should be alright now.
                # ('groups', models.ManyToManyField(to='auth.Group', verbose_name='groups', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', related_name='user_set', related_query_name='user')),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(to='auth.Permission', verbose_name='user permissions', blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user')),

                # role    = ForeignKey(UserRole, verbose_name=_(u'Role'), null=True, on_delete=PROTECT)
                ('role_id', models.PositiveIntegerField(verbose_name='Role', null=True)), #NB: not a ForeignKey in order to avoid cycling import (an so create another migration files to add this field)
                # is_team = BooleanField(verbose_name=_(u'Is a team ?'), default=False)
                ('is_team', models.BooleanField(default=False, verbose_name='Is a team ?')),
            ],
            options={
                #'swappable': 'AUTH_USER_MODEL', #NB: we need the auth.user table to migrate old installations
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
        ),
    ]
