"""
CLI interface
"""
import argparse
from datetime import datetime
from ..application.services import BookingService
from ..application.dto import BookingCreateDTO


class BookingCLI:
    """Command-line interface for booking operations"""
    
    def __init__(self, booking_service: BookingService):
        self.booking_service = booking_service
    
    def run(self, args=None):
        """Run CLI"""
        parser = argparse.ArgumentParser(description='Hotel Booking System')
        subparsers = parser.add_subparsers(dest='command', help='Commands')
        
        # Create booking command
        create_parser = subparsers.add_parser('create', help='Create booking')
        create_parser.add_argument('--room-id', type=int, required=True)
        create_parser.add_argument('--guest-name', required=True)
        create_parser.add_argument('--guest-email', required=True)
        create_parser.add_argument('--check-in', required=True)
        create_parser.add_argument('--check-out', required=True)
        create_parser.add_argument('--guest-phone', required=False)
        
        # Cancel booking command
        cancel_parser = subparsers.add_parser('cancel', help='Cancel booking')
        cancel_parser.add_argument('--booking-id', required=True)
        
        # Get booking command
        get_parser = subparsers.add_parser('get', help='Get booking')
        get_parser.add_argument('--booking-id', required=True)
        
        parsed_args = parser.parse_args(args)
        
        if parsed_args.command == 'create':
            return self._create_booking(parsed_args)
        elif parsed_args.command == 'cancel':
            return self._cancel_booking(parsed_args)
        elif parsed_args.command == 'get':
            return self._get_booking(parsed_args)
        else:
            parser.print_help()
    
    def _create_booking(self, args):
        dto = BookingCreateDTO(
            room_id=args.room_id,
            guest_name=args.guest_name,
            guest_email=args.guest_email,
            check_in=datetime.strptime(args.check_in, '%Y-%m-%d').date(),
            check_out=datetime.strptime(args.check_out, '%Y-%m-%d').date(),
            guest_phone=args.guest_phone
        )
        booking = self.booking_service.create_booking(dto)
        print(f"Booking created: {booking.id}")
        print(f"Total price: {booking.total_price.amount} {booking.total_price.currency}")
        return booking
    
    def _cancel_booking(self, args):
        booking = self.booking_service.cancel_booking(args.booking_id)
        print(f"Booking cancelled: {booking.id}")
        return booking
    
    def _get_booking(self, args):
        booking = self.booking_service.get_booking(args.booking_id)
        if booking:
            dto = self.booking_service.get_booking_response_dto(booking)
            print(f"Booking ID: {dto.id}")
            print(f"Guest: {dto.guest_name}")
            print(f"Status: {dto.status}")
            print(f"Dates: {dto.check_in} - {dto.check_out}")
            print(f"Total: {dto.total_price} {dto.currency}")
        else:
            print("Booking not found")
        return booking