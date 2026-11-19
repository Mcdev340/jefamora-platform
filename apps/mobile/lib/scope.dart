import 'package:material_ui/material_ui.dart';

import 'api.dart';

class AppScope extends InheritedWidget {
  const AppScope({super.key, required this.session, required this.api, required super.child});

  final SessionStore session;
  final ApiClient api;

  static AppScope of(BuildContext context) {
    final scope = context.dependOnInheritedWidgetOfExactType<AppScope>();
    assert(scope != null, 'AppScope est absent');
    return scope!;
  }

  @override
  bool updateShouldNotify(AppScope oldWidget) => session != oldWidget.session || api != oldWidget.api;
}
