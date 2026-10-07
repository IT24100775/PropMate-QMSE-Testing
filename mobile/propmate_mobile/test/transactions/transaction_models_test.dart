import 'package:flutter_test/flutter_test.dart';
import 'package:propmate_mobile/features/transactions/models/transaction_models.dart';

void main() {
  test(
    'RentalApplication parses rental details and converts income to double',
    () {
      final application = RentalApplication.fromJson({
        'id': 3,
        'propertyListingId': 12,
        'propertyTitle': 'Garden apartment',
        'tenantId': 7,
        'tenantName': 'Sam Tenant',
        'employment': 'Engineer',
        'monthlyIncome': 180000,
        'occupants': 2,
        'preferredMoveInDate': '2026-11-01T00:00:00Z',
        'durationMonths': 12,
        'message': 'Available to move soon',
        'status': 'Pending',
        'negotiationStatus': 'None',
      });

      expect(application.id, 3);
      expect(application.propertyTitle, 'Garden apartment');
      expect(application.monthlyIncome, 180000.0);
      expect(application.monthlyIncome, isA<double>());
      expect(application.occupants, 2);
      expect(application.preferredMoveInDate, DateTime.utc(2026, 11));
      expect(application.message, 'Available to move soon');
      expect(application.status, 'Pending');
    },
  );

  test('PurchaseOffer parses amount, status and optional conditions', () {
    final offer = PurchaseOffer.fromJson({
      'id': 5,
      'propertyListingId': 13,
      'propertyTitle': 'Family home',
      'buyerId': 9,
      'buyerName': 'Alex Buyer',
      'offerAmount': 12500000,
      'conditions': 'Subject to inspection',
      'status': 'Pending',
      'negotiationStatus': 'Open',
    });

    expect(offer.offerAmount, 12500000.0);
    expect(offer.conditions, 'Subject to inspection');
    expect(offer.status, 'Pending');
    expect(offer.negotiationStatus, 'Open');
  });

  test('RentalNegotiationOffer parses date and proposed rent', () {
    final offer = RentalNegotiationOffer.fromJson({
      'id': 2,
      'proposedByUserId': 14,
      'monthlyRent': 175000,
      'moveInDate': '2026-12-01T00:00:00Z',
      'durationMonths': 6,
      'conditions': 'Rent includes parking',
      'status': 'Pending',
    });

    expect(offer.proposedByUserId, 14);
    expect(offer.monthlyRent, 175000.0);
    expect(offer.moveInDate, DateTime.utc(2026, 12));
    expect(offer.durationMonths, 6);
    expect(offer.conditions, 'Rent includes parking');
  });

  test('PurchaseNegotiationOffer parses offer amount and status', () {
    final offer = PurchaseNegotiationOffer.fromJson({
      'id': 4,
      'proposedByUserId': 11,
      'offerAmount': 9800000,
      'conditions': null,
      'status': 'Accepted',
    });

    expect(offer.offerAmount, 9800000.0);
    expect(offer.conditions, isNull);
    expect(offer.status, 'Accepted');
  });

  test('NegotiationMessage parses sender, text and creation time', () {
    final message = NegotiationMessage.fromJson({
      'id': 15,
      'senderUserId': 21,
      'senderName': 'Property Owner',
      'message': 'I can adjust the move-in date.',
      'createdAt': '2026-10-08T12:30:00Z',
    });

    expect(message.senderUserId, 21);
    expect(message.senderName, 'Property Owner');
    expect(message.message, 'I can adjust the move-in date.');
    expect(message.createdAt, DateTime.utc(2026, 10, 8, 12, 30));
  });

  test('RentalAgreement parses confirmation flags and financial terms', () {
    final agreement = RentalAgreement.fromJson({
      'id': 10,
      'finalMonthlyRent': 160000,
      'moveInDate': '2026-11-01T00:00:00Z',
      'durationMonths': 12,
      'terms': 'Standard lease',
      'tenantObligation': 'Pay rent on time',
      'ownerObligation': 'Maintain the property',
      'penaltyTerms': 'Late fee applies',
      'buyerConfirmed': true,
      'sellerConfirmed': false,
      'status': 'Awaiting confirmation',
    });

    expect(agreement.finalMonthlyRent, 160000.0);
    expect(agreement.durationMonths, 12);
    expect(agreement.buyerConfirmed, isTrue);
    expect(agreement.sellerConfirmed, isFalse);
    expect(agreement.status, 'Awaiting confirmation');
  });

  test('PurchaseAgreement parses purchase price and confirmation flags', () {
    final agreement = PurchaseAgreement.fromJson({
      'id': 11,
      'finalPurchasePrice': 11000000,
      'conditions': 'Sale subject to inspection',
      'buyerObligation': 'Pay deposit',
      'sellerObligation': 'Transfer title',
      'penaltyTerms': 'As stated in contract',
      'buyerConfirmed': true,
      'sellerConfirmed': true,
      'status': 'Confirmed',
    });

    expect(agreement.finalPurchasePrice, 11000000.0);
    expect(agreement.conditions, 'Sale subject to inspection');
    expect(agreement.buyerConfirmed, isTrue);
    expect(agreement.sellerConfirmed, isTrue);
    expect(agreement.status, 'Confirmed');
  });
}
