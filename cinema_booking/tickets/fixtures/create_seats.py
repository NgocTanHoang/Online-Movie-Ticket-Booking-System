import json
from django.core.management.base import BaseCommand
from tickets.models import Room, Seat, SeatType

class Command(BaseCommand):
    help = 'Create seats for all rooms'

    def handle(self, *args, **kwargs):
        # Get standard seat type
        standard_seat_type = SeatType.objects.get(name='Standard')
        
        # Get all rooms
        rooms = Room.objects.all()
        
        seats_data = []
        seat_id = 1
        
        for room in rooms:
            for row in range(1, room.rows + 1):
                for col in range(1, room.columns + 1):
                    seat = {
                        "model": "tickets.seat",
                        "pk": seat_id,
                        "fields": {
                            "room": room.id,
                            "row": row,
                            "column": col,
                            "seat_type": standard_seat_type.id,
                            "active": True
                        }
                    }
                    seats_data.append(seat)
                    seat_id += 1
        
        # Save to JSON file
        with open('cinema_booking/tickets/fixtures/seats.json', 'w') as f:
            json.dump(seats_data, f, indent=4)
            
        self.stdout.write(self.style.SUCCESS('Successfully created seats data')) 