import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:propmate_mobile/auth/screens/login_screen.dart';
import 'package:propmate_mobile/auth/screens/register_screen.dart';

void main() {
  Future<void> showLogin(WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: LoginScreen()),
    );
  }

  Future<void> showRegister(WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: RegisterScreen()),
    );
  }

  testWidgets('login screen displays its core controls', (tester) async {
    await showLogin(tester);

    expect(find.text('Welcome to PropMate'), findsOneWidget);
    expect(find.byType(TextFormField), findsNWidgets(2));
    expect(find.text('Sign In'), findsOneWidget);
    expect(find.text('Create account'), findsOneWidget);
  });

  testWidgets('empty login form shows required-field errors', (tester) async {
    await showLogin(tester);
    await tester.tap(find.text('Sign In'));
    await tester.pump();

    expect(find.text('Please enter your email.'), findsOneWidget);
    expect(find.text('Please enter your password.'), findsOneWidget);
  });

  testWidgets('login form rejects an invalid email address', (tester) async {
    await showLogin(tester);
    await tester.enterText(find.byType(TextFormField).first, 'not-an-email');
    await tester.enterText(find.byType(TextFormField).last, 'password');
    await tester.tap(find.text('Sign In'));
    await tester.pump();

    expect(find.text('Please enter a valid email.'), findsOneWidget);
  });

  testWidgets('login screen opens account registration', (tester) async {
    await showLogin(tester);
    await tester.tap(find.text('Create account'));
    await tester.pumpAndSettle();

    expect(find.byType(RegisterScreen), findsOneWidget);
    expect(find.text('Join PropMate'), findsOneWidget);
  });

  testWidgets('empty registration form shows required-field errors',
      (tester) async {
    await showRegister(tester);
    final submitButton = find.widgetWithText(
      ElevatedButton,
      'Create Account',
    );
    await tester.ensureVisible(submitButton);
    await tester.tap(submitButton);
    await tester.pump();

    expect(find.text('Required'), findsNWidgets(2));
    expect(find.text('Please enter your email.'), findsOneWidget);
    expect(find.text('Please enter a password.'), findsOneWidget);
    expect(find.text('Please confirm your password.'), findsOneWidget);
  });

  testWidgets('registration form rejects an invalid email', (tester) async {
    await showRegister(tester);
    await tester.enterText(find.byType(TextFormField).at(0), 'Ada');
    await tester.enterText(find.byType(TextFormField).at(1), 'Lovelace');
    await tester.enterText(find.byType(TextFormField).at(2), 'invalid-email');
    await tester.enterText(find.byType(TextFormField).at(3), 'validpass1');
    await tester.enterText(find.byType(TextFormField).at(4), 'validpass1');

    final submitButton = find.widgetWithText(
      ElevatedButton,
      'Create Account',
    );
    await tester.ensureVisible(submitButton);
    await tester.tap(submitButton);
    await tester.pump();

    expect(find.text('Please enter a valid email.'), findsOneWidget);
  });

  testWidgets('registration form rejects a short password', (tester) async {
    await showRegister(tester);
    await tester.enterText(find.byType(TextFormField).at(0), 'Ada');
    await tester.enterText(find.byType(TextFormField).at(1), 'Lovelace');
    await tester.enterText(find.byType(TextFormField).at(2), 'ada@example.com');
    await tester.enterText(find.byType(TextFormField).at(3), 'short');
    await tester.enterText(find.byType(TextFormField).at(4), 'short');

    final submitButton = find.widgetWithText(
      ElevatedButton,
      'Create Account',
    );
    await tester.ensureVisible(submitButton);
    await tester.tap(submitButton);
    await tester.pump();

    expect(
      find.text('Password must be at least 8 characters.'),
      findsOneWidget,
    );
  });

  testWidgets('registration form rejects mismatched passwords',
      (tester) async {
    await showRegister(tester);
    await tester.enterText(find.byType(TextFormField).at(0), 'Ada');
    await tester.enterText(find.byType(TextFormField).at(1), 'Lovelace');
    await tester.enterText(find.byType(TextFormField).at(2), 'ada@example.com');
    await tester.enterText(find.byType(TextFormField).at(3), 'validpass1');
    await tester.enterText(find.byType(TextFormField).at(4), 'differentpass');

    final submitButton = find.widgetWithText(
      ElevatedButton,
      'Create Account',
    );
    await tester.ensureVisible(submitButton);
    await tester.tap(submitButton);
    await tester.pump();

    expect(find.text('Passwords do not match.'), findsOneWidget);
  });
}
