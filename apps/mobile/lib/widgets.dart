import 'package:material_ui/material_ui.dart';

import 'api.dart';
import 'scope.dart';
import 'theme.dart';

class BrandLockup extends StatelessWidget {
  const BrandLockup({super.key, this.light = false});

  final bool light;

  @override
  Widget build(BuildContext context) {
    final color = light ? Colors.white : navy;
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(6),
          decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(12)),
          child: Image.asset('assets/logo-mark.png', width: 36, height: 36),
        ),
        const SizedBox(width: 10),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Jefamora', style: TextStyle(color: color, fontWeight: FontWeight.w800, fontSize: 18)),
            Text('Clients et ouvriers', style: TextStyle(color: light ? const Color(0xFFFFEDD5) : muted, fontSize: 12)),
          ],
        ),
      ],
    );
  }
}

class JefamoraBar extends StatelessWidget {
  const JefamoraBar({super.key, required this.index, required this.onSelect, required this.destinations});

  final int index;
  final ValueChanged<int> onSelect;
  final List<NavigationDestination> destinations;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [BoxShadow(color: navy.withValues(alpha: 0.08), blurRadius: 18, offset: const Offset(0, -4))],
      ),
      child: NavigationBar(
        selectedIndex: index,
        onDestinationSelected: onSelect,
        destinations: destinations,
        labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
      ),
    );
  }
}

class StatusChip extends StatelessWidget {
  const StatusChip(this.label, {super.key});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(color: const Color(0xFFFFF3CC), borderRadius: BorderRadius.circular(99)),
      child: Text(label, style: const TextStyle(color: navy, fontWeight: FontWeight.w700, fontSize: 12)),
    );
  }
}

class EmptyHint extends StatelessWidget {
  const EmptyHint(this.text, {super.key});

  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 28),
      child: Text(text, textAlign: TextAlign.center, style: const TextStyle(color: muted)),
    );
  }
}

class RemoteBody<T> extends StatefulWidget {
  const RemoteBody({super.key, required this.load, required this.builder});

  final Future<T> Function() load;
  final Widget Function(T data, Future<void> Function() reload) builder;

  @override
  State<RemoteBody<T>> createState() => _RemoteBodyState<T>();
}

class _RemoteBodyState<T> extends State<RemoteBody<T>> {
  late Future<T> _future;

  @override
  void initState() {
    super.initState();
    _future = widget.load();
  }

  Future<void> _reload() async {
    setState(() => _future = widget.load());
    await _future;
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<T>(
      future: _future,
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const Center(child: CircularProgressIndicator(color: orange));
        }
        if (snapshot.hasError) {
          return Center(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text('${snapshot.error}', textAlign: TextAlign.center),
                  const SizedBox(height: 12),
                  FilledButton(onPressed: _reload, child: const Text('Réessayer')),
                ],
              ),
            ),
          );
        }
        return RefreshIndicator(
          color: orange,
          onRefresh: _reload,
          child: widget.builder(snapshot.data as T, _reload),
        );
      },
    );
  }
}

Future<void> runAction(BuildContext context, Future<void> Function() action, {String? done}) async {
  try {
    await action();
    if (!context.mounted) return;
    if (done != null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(done)));
    }
  } on ApiException catch (error) {
    if (!context.mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error.message)));
  }
}

class AccountPage extends StatelessWidget {
  const AccountPage({super.key});

  @override
  Widget build(BuildContext context) {
    final scope = AppScope.of(context);
    final profile = scope.session.profile!;
    final role = profile.isProfessional ? 'Ouvrier' : 'Client';
    return Scaffold(
      appBar: AppBar(title: const Text('Compte')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(profile.displayName, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w800, color: navy)),
          const SizedBox(height: 6),
          Text(profile.email, style: const TextStyle(color: muted)),
          const SizedBox(height: 14),
          StatusChip(role),
          if (profile.businessName != null && profile.businessName!.isNotEmpty) ...[
            const SizedBox(height: 16),
            Text(profile.businessName!, style: const TextStyle(fontWeight: FontWeight.w700)),
          ],
          if (profile.isProfessional) ...[
            const SizedBox(height: 8),
            Text(
              profile.badgeVerified == true ? 'Profil vérifié' : 'Profil en attente de vérification',
              style: const TextStyle(color: muted),
            ),
          ],
          const SizedBox(height: 28),
          OutlinedButton(
            onPressed: () => scope.api.logout(),
            child: const Text('Se déconnecter'),
          ),
        ],
      ),
    );
  }
}

class MissionsPage extends StatelessWidget {
  const MissionsPage({super.key});

  @override
  Widget build(BuildContext context) {
    final api = AppScope.of(context).api;
    final worker = AppScope.of(context).session.profile?.isProfessional ?? false;
    return Scaffold(
      appBar: AppBar(title: const Text('Missions')),
      body: RemoteBody<List<BookingItem>>(
        load: api.bookings,
        builder: (items, reload) {
          if (items.isEmpty) {
            return ListView(children: const [EmptyHint('Aucune mission pour le moment.')]);
          }
          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: items.length,
            separatorBuilder: (_, _) => const SizedBox(height: 10),
            itemBuilder: (context, index) {
              final item = items[index];
              return Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(item.professionalName, style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
                      const SizedBox(height: 8),
                      StatusChip(bookingLabel(item.status)),
                      const SizedBox(height: 12),
                      if (worker && item.status == 'confirmed')
                        FilledButton(
                          onPressed: () => runAction(context, () => api.startBooking(item.id), done: 'Mission démarrée')
                              .then((_) => reload()),
                          child: const Text('Démarrer'),
                        ),
                      if (worker && item.status == 'in_progress')
                        FilledButton(
                          onPressed: () => runAction(context, () => api.finishBooking(item.id), done: 'Fin déclarée')
                              .then((_) => reload()),
                          child: const Text('Déclarer la fin'),
                        ),
                      if (!worker && item.status == 'completed_by_professional')
                        FilledButton(
                          onPressed: () => runAction(context, () => api.confirmBooking(item.id), done: 'Mission confirmée')
                              .then((_) => reload()),
                          child: const Text('Confirmer la fin'),
                        ),
                    ],
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
