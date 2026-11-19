import 'package:material_ui/material_ui.dart';

import 'client_app.dart';
import 'widgets.dart';

class WorkerShell extends StatefulWidget {
  const WorkerShell({super.key});

  @override
  State<WorkerShell> createState() => _WorkerShellState();
}

class _WorkerShellState extends State<WorkerShell> {
  int _index = 0;

  @override
  Widget build(BuildContext context) {
    const pages = [RequestsPage(worker: true), MissionsPage(), AccountPage()];
    return Scaffold(
      body: pages[_index],
      bottomNavigationBar: JefamoraBar(
        index: _index,
        onSelect: (value) => setState(() => _index = value),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.inbox_outlined), selectedIcon: Icon(Icons.inbox_rounded), label: 'Demandes'),
          NavigationDestination(icon: Icon(Icons.construction_outlined), selectedIcon: Icon(Icons.construction_rounded), label: 'Missions'),
          NavigationDestination(icon: Icon(Icons.person_outline), selectedIcon: Icon(Icons.person_rounded), label: 'Compte'),
        ],
      ),
    );
  }
}
