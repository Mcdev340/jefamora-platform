import 'package:material_ui/material_ui.dart';

import 'api.dart';
import 'auth_pages.dart';
import 'client_app.dart';
import 'scope.dart';
import 'theme.dart';
import 'worker_app.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final session = SessionStore();
  await session.load();
  runApp(JefamoraApp(session: session, api: ApiClient(session)));
}

class JefamoraApp extends StatelessWidget {
  const JefamoraApp({super.key, required this.session, required this.api});

  final SessionStore session;
  final ApiClient api;

  @override
  Widget build(BuildContext context) {
    return AppScope(
      session: session,
      api: api,
      child: ListenableBuilder(
        listenable: session,
        builder: (context, _) {
          final profile = session.profile;
          return MaterialApp(
            key: ValueKey(profile?.id ?? 'signed-out'),
            title: 'Jefamora',
            debugShowCheckedModeBanner: false,
            theme: jefamoraTheme(),
            home: profile == null
                ? const WelcomePage()
                : profile.isProfessional
                    ? const WorkerShell()
                    : const ClientShell(),
          );
        },
      ),
    );
  }
}
