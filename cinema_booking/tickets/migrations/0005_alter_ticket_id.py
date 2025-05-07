from django.db import migrations, models

def reset_sequence(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        # Drop existing sequence if it exists
        cursor.execute("""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_sequences WHERE schemaname = 'public' AND sequencename = 'tickets_ticket_id_seq') THEN
                    DROP SEQUENCE tickets_ticket_id_seq;
                END IF;
            END $$;
        """)
        
        # Get the current maximum ID
        cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM tickets_ticket")
        max_id = cursor.fetchone()[0]
        
        # Create new sequence starting from max_id
        cursor.execute(f"""
            CREATE SEQUENCE tickets_ticket_id_seq
            START WITH {max_id}
            INCREMENT BY 1
            NO MINVALUE
            NO MAXVALUE
            CACHE 1
        """)
        
        # Set the sequence as owned by the id column
        cursor.execute("""
            ALTER SEQUENCE tickets_ticket_id_seq
            OWNED BY tickets_ticket.id;
        """)
        
        # Set the default value for the id column to use the sequence
        cursor.execute("""
            ALTER TABLE tickets_ticket
            ALTER COLUMN id SET DEFAULT nextval('tickets_ticket_id_seq');
        """)

class Migration(migrations.Migration):
    dependencies = [
        ('tickets', '0004_remove_ticket_seat_ticket_seats_alter_ticket_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='id',
            field=models.BigAutoField(primary_key=True),
        ),
        migrations.RunPython(reset_sequence),
    ] 