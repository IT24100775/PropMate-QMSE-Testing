import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:propmate_mobile/features/maintenance/screens/create_request.dart';

void main() {
  testWidgets(
    'TC-MOB-MNT-001: Empty maintenance description should show validation error',
    (WidgetTester tester) async {
      // Arrange
      await tester.pumpWidget(
        const MaterialApp(home: CreateRequestScreen(tenantId: 1)),
      );

      // Act
      final sendButton = find.text('Send request');
      await tester.tap(sendButton);
      await tester.pump();

      // Assert
      expect(find.text('Please describe the problem.'), findsOneWidget);
    },
  );

  testWidgets(
    'TC-MOB-MNT-002: Whitespace-only maintenance description should show validation error',
    (WidgetTester tester) async {
      // Arrange
      await tester.pumpWidget(
        const MaterialApp(home: CreateRequestScreen(tenantId: 1)),
      );
      await tester.enterText(find.byType(TextFormField), '   ');

      // Act
      await tester.tap(find.text('Send request'));
      await tester.pump();

      // Assert
      expect(find.text('Please describe the problem.'), findsOneWidget);
    },
  );

  testWidgets(
    'TC-MOB-MNT-003: Maintenance request form shows its default category and priority',
    (WidgetTester tester) async {
      // Arrange
      await tester.pumpWidget(
        const MaterialApp(home: CreateRequestScreen(tenantId: 1)),
      );

      // Assert
      expect(find.text('General'), findsOneWidget);
      expect(find.text('MEDIUM'), findsOneWidget);
      expect(find.text('Send request'), findsOneWidget);
    },
  );
}
