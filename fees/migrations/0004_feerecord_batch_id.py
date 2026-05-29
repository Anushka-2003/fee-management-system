from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fees', '0003_feerecord_received_by_feerecord_received_by_other'),
    ]

    operations = [
        migrations.AddField(
            model_name='feerecord',
            name='batch_id',
            field=models.UUIDField(blank=True, db_index=True, null=True),
        ),
    ]
