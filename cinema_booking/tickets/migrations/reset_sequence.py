from django.db import migrations

def reset_ticket_sequence(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        # Get the current maximum ID
        cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM tickets_ticket")
        max_id = cursor.fetchone()[0]
        
        # Reset the sequence to the max ID
        cursor.execute(f"""
            ALTER SEQUENCE tickets_ticket_id_seq RESTART WITH {max_id}
        """)

def reverse_migration(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('tickets', '0004_remove_ticket_seat_ticket_seats_alter_ticket_status'),  # Update this to your latest migration
    ]

    operations = [
        migrations.RunPython(reset_ticket_sequence, reverse_migration),
    ] 