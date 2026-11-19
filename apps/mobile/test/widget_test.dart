import 'package:flutter_test/flutter_test.dart';
import 'package:jefamora/api.dart';
import 'package:jefamora/main.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  testWidgets('L’entrée propose de commencer puis de choisir un rôle', (tester) async {
    SharedPreferences.setMockInitialValues({});
    final session = SessionStore();
    await session.load();
    await tester.pumpWidget(JefamoraApp(session: session, api: ApiClient(session)));
    expect(find.text('Jefamora'), findsOneWidget);
    expect(find.text('Commencer'), findsOneWidget);

    await tester.tap(find.text('Commencer'));
    await tester.pumpAndSettle();

    expect(find.text('Client'), findsOneWidget);
    expect(find.text('Ouvrier'), findsOneWidget);
  });
}
