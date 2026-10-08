import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:propmate_mobile/auth/screens/login_screen.dart';
import 'package:propmate_mobile/auth/screens/register_screen.dart';
import 'package:propmate_mobile/auth/services/mobile_auth_service.dart';
import 'package:propmate_mobile/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  Future<void> launchLoggedOutApp(WidgetTester tester) async {
    await MobileAuthService.logout();
    app.main();
    await tester.pumpAndSettle();
  }

  testWidgets('TC-MOB-INT-001: Logged-out launch shows the sign-in screen', (
    tester,
  ) async {
    await launchLoggedOutApp(tester);

    expect(find.byType(LoginScreen), findsOneWidget);
    expect(find.text('Welcome to PropMate'), findsOneWidget);
    expect(find.text('Sign In'), findsOneWidget);
  });

  testWidgets('TC-MOB-INT-002: Empty sign-in submission shows validation', (
    tester,
  ) async {
    await launchLoggedOutApp(tester);

    await tester.tap(find.text('Sign In'));
    await tester.pumpAndSettle();

    expect(find.text('Please enter your email.'), findsOneWidget);
    expect(find.text('Please enter your password.'), findsOneWidget);
    expect(find.textContaining('Unable to log in.'), findsNothing);
  });

  testWidgets('TC-MOB-INT-003: Sign-in password visibility can be toggled', (
    tester,
  ) async {
    await launchLoggedOutApp(tester);

    final passwordField = find.byType(TextFormField).at(1);
    final passwordInput = find.descendant(
      of: passwordField,
      matching: find.byType(EditableText),
    );

    expect(tester.widget<EditableText>(passwordInput).obscureText, isTrue);
    await tester.tap(find.byIcon(Icons.visibility_outlined).first);
    await tester.pumpAndSettle();

    expect(tester.widget<EditableText>(passwordInput).obscureText, isFalse);
  });

  testWidgets('TC-MOB-INT-004: Sign-in navigation opens registration', (
    tester,
  ) async {
    await launchLoggedOutApp(tester);

    await tester.tap(find.text('Create account'));
    await tester.pumpAndSettle();

    expect(find.byType(RegisterScreen), findsOneWidget);
    expect(find.text('Join PropMate'), findsOneWidget);
  });

  testWidgets(
    'TC-MOB-INT-005: Empty registration submission shows validation',
    (tester) async {
      await launchLoggedOutApp(tester);
      await tester.tap(find.text('Create account'));
      await tester.pumpAndSettle();

      final submitButton = find.widgetWithText(
        ElevatedButton,
        'Create Account',
      );
      await tester.ensureVisible(submitButton);
      await tester.tap(submitButton);
      await tester.pumpAndSettle();

      expect(find.text('Required'), findsNWidgets(2));
      expect(find.text('Please enter your email.'), findsOneWidget);
      expect(find.text('Please enter a password.'), findsOneWidget);
      expect(find.text('Please confirm your password.'), findsOneWidget);
    },
  );

  testWidgets('TC-MOB-INT-006: Registration sign-in link returns to login', (
    tester,
  ) async {
    await launchLoggedOutApp(tester);
    await tester.tap(find.text('Create account'));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Sign in'));
    await tester.pumpAndSettle();

    expect(find.byType(LoginScreen), findsOneWidget);
    expect(find.text('Welcome to PropMate'), findsOneWidget);
  });
}
