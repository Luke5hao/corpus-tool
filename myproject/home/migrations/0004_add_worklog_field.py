# Manually added 

from django.db import migrations, models

def set_default_worklog(apps, schema_editor):
  TextEntry = apps.get_model('home', 'TextEntry')
  for entry in TextEntry.objects.all():
    if entry.worklog is None:
      entry.worklog = ''
      entry.save()

class Migration(migrations.Migration):

  dependencies = [
    ('home', '0003_alter_textentry_options_textentry_created_at_and_more'),
  ]

  operations = [
    migrations.AddField(
      model_name='textentry',
      name='worklog',
      field=models.TextField(default=''),
    ),
    migrations.RunPython(set_default_worklog),
  ]