import 'package:flutter_test/flutter_test.dart';
import 'package:propmate_mobile/features/discovery-viewing/models/property.dart';
import 'package:propmate_mobile/features/discovery-viewing/models/viewing_booking.dart';
import 'package:propmate_mobile/features/discovery-viewing/models/viewing_slot.dart';

void main() {
  group('Property.fromJson', () {
    test('parses property fields and numeric values', () {
      final property = Property.fromJson({
        'id': 8,
        'title': 'City apartment',
        'description': 'Bright and spacious',
        'price': 250000,
        'purpose': 'Rent',
        'bedrooms': 2,
        'bathrooms': 1,
        'latitude': 6.9271,
        'longitude': 79.8612,
      });

      expect(property.id, 8);
      expect(property.title, 'City apartment');
      expect(property.price, 250000.0);
      expect(property.latitude, 6.9271);
      expect(property.longitude, 79.8612);
    });

    test('uses safe defaults for missing values', () {
      final property = Property.fromJson({});

      expect(property.id, 0);
      expect(property.title, '');
      expect(property.description, '');
      expect(property.price, 0.0);
      expect(property.bedrooms, 0);
      expect(property.bathrooms, 0);
      expect(property.address, isNull);
      expect(property.city, isNull);
      expect(property.latitude, isNull);
      expect(property.longitude, isNull);
      expect(property.images, isEmpty);
    });

    test('prefers imageUrls when both image formats are provided', () {
      final property = Property.fromJson({
        'imageUrls': ['front.jpg', null, 12],
        'images': [
          {'imageUrl': 'nested.jpg'},
        ],
        'primaryImageUrl': 'primary.jpg',
      });

      expect(property.images, ['front.jpg', '12']);
    });

    test('uses nested images when imageUrls are empty', () {
      final property = Property.fromJson({
        'imageUrls': [],
        'images': [
          {'imageUrl': 'front.jpg'},
          {'imageUrl': null},
          'ignored',
        ],
      });

      expect(property.images, ['front.jpg']);
    });

    test('uses the primary image as a final fallback', () {
      final property = Property.fromJson({
        'primaryImageUrl': 'primary.jpg',
      });

      expect(property.images, ['primary.jpg']);
    });
  });

  test('ViewingSlot parses times and availability', () {
    final slot = ViewingSlot.fromJson({
      'id': 4,
      'propertyListingId': 18,
      'startTime': '2026-10-09T09:00:00Z',
      'endTime': '2026-10-09T10:00:00Z',
      'isAvailable': true,
    });

    expect(slot.id, 4);
    expect(slot.propertyListingId, 18);
    expect(slot.startTime.isUtc, isFalse);
    expect(slot.endTime.isUtc, isFalse);
    expect(slot.isAvailable, isTrue);
  });

  group('ViewingBooking.fromJson', () {
    Map<String, dynamic> bookingJson(Object status) => {
          'id': 6,
          'status': status,
          'bookedAt': '2026-10-08T08:00:00Z',
          'viewingSlotId': 2,
          'startTime': '2026-10-09T09:00:00Z',
          'endTime': '2026-10-09T10:00:00Z',
          'propertyListingId': 18,
          'propertyTitle': 'City apartment',
          'propertyCity': 'Colombo',
        };

    test('maps a booked status and property details', () {
      final booking = ViewingBooking.fromJson(bookingJson(0));

      expect(booking.statusText, 'Booked');
      expect(booking.propertyTitle, 'City apartment');
      expect(booking.propertyCity, 'Colombo');
      expect(booking.primaryImageUrl, isNull);
    });

    test('maps completed and cancelled status strings', () {
      expect(
        ViewingBooking.fromJson(bookingJson('completed')).statusText,
        'Completed',
      );
      expect(
        ViewingBooking.fromJson(bookingJson('cancelled')).statusText,
        'Cancelled',
      );
    });

    test('reports unknown status codes', () {
      final booking = ViewingBooking.fromJson(bookingJson(99));

      expect(booking.statusText, 'Unknown');
    });
  });
}
