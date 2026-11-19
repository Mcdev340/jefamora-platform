import 'package:material_ui/material_ui.dart';

import 'api.dart';
import 'scope.dart';
import 'theme.dart';
import 'trade_look.dart';
import 'widgets.dart';

class GuestShell extends StatefulWidget {
  const GuestShell({super.key, required this.onRole});

  final void Function(String role) onRole;

  @override
  State<GuestShell> createState() => _GuestShellState();
}

class _GuestShellState extends State<GuestShell> {
  int _index = 0;

  @override
  Widget build(BuildContext context) {
    final pages = [
      WelcomeHome(onRole: widget.onRole),
      const _GuestTrades(),
      _GuestLock(
        title: 'Vos demandes',
        text: 'Connectez-vous pour envoyer une demande, comparer les devis et suivre la mission.',
        action: 'Je suis client',
        onTap: () => widget.onRole('client'),
      ),
      _GuestAccount(onRole: widget.onRole),
    ];
    return Scaffold(
      backgroundColor: cream,
      body: pages[_index],
      bottomNavigationBar: JefamoraBar(
        index: _index,
        onSelect: (value) => setState(() => _index = value),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home_rounded), label: 'Accueil'),
          NavigationDestination(icon: Icon(Icons.grid_view_outlined), selectedIcon: Icon(Icons.grid_view_rounded), label: 'Métiers'),
          NavigationDestination(icon: Icon(Icons.receipt_long_outlined), selectedIcon: Icon(Icons.receipt_long_rounded), label: 'Demandes'),
          NavigationDestination(icon: Icon(Icons.person_outline), selectedIcon: Icon(Icons.person_rounded), label: 'Compte'),
        ],
      ),
    );
  }
}

class WelcomeHome extends StatelessWidget {
  const WelcomeHome({super.key, required this.onRole});

  final void Function(String role) onRole;

  @override
  Widget build(BuildContext context) {
    return ColoredBox(
      color: cream,
      child: ListView(
        padding: const EdgeInsets.fromLTRB(20, 12, 20, 28),
        children: [
          const SafeArea(bottom: false, child: BrandLockup()),
          const SizedBox(height: 18),
          ClipRRect(
            borderRadius: BorderRadius.circular(28),
            child: Image.asset('assets/home-hero.jpg', height: 210, width: double.infinity, fit: BoxFit.cover),
          ),
          const SizedBox(height: 18),
          const Text(
            'RÉGION DE DAKAR · SÉNÉGAL',
            style: TextStyle(color: orange, fontWeight: FontWeight.w800, fontSize: 12, letterSpacing: 1.1),
          ),
          const SizedBox(height: 8),
          const Text.rich(
            TextSpan(
              text: 'Trouvez rapidement le bon ',
              children: [
                TextSpan(text: 'professionnel', style: TextStyle(color: orange)),
                TextSpan(text: ' près de chez vous'),
              ],
            ),
            style: TextStyle(fontSize: 30, height: 1.08, fontWeight: FontWeight.w800, color: navy),
          ),
          const SizedBox(height: 10),
          const Text(
            'Décrivez votre besoin, comparez les devis, retenez un seul professionnel. Le paiement reste entre vous et l’artisan.',
            style: TextStyle(color: muted, height: 1.4, fontSize: 15.5),
          ),
          const SizedBox(height: 16),
          _SearchBar(onSearch: () => onRole('client')),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              for (final name in const ['Électricien', 'Plombier', 'Menuisier', 'Maçon'])
                ActionChip(
                  label: Text(name),
                  backgroundColor: Colors.white,
                  side: BorderSide.none,
                  labelStyle: const TextStyle(color: navy, fontWeight: FontWeight.w700),
                  onPressed: () => onRole('client'),
                ),
            ],
          ),
          const SizedBox(height: 18),
          const Row(
            children: [
              Expanded(child: _Trust(icon: Icons.verified_rounded, text: 'Profils vérifiés')),
              SizedBox(width: 8),
              Expanded(child: _Trust(icon: Icons.receipt_long_rounded, text: 'Un seul devis')),
              SizedBox(width: 8),
              Expanded(child: _Trust(icon: Icons.payments_rounded, text: '0 FCFA')),
            ],
          ),
          const SizedBox(height: 26),
          const Text('Comment ça marche', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: navy)),
          const SizedBox(height: 12),
          const _Step(number: '1', title: 'Inscrivez-vous', text: 'Un compte gratuit, puis la confirmation de l’e-mail.'),
          const _Step(number: '2', title: 'Décrivez', text: 'Le métier, la zone et l’urgence du besoin.'),
          const _Step(number: '3', title: 'Comparez', text: 'Plusieurs devis. Vous n’en retenez qu’un.'),
          const _Step(number: '4', title: 'Réalisez', text: 'Suivez les travaux, confirmez la fin, laissez un avis.'),
          const SizedBox(height: 8),
          _Door(
            navyDoor: true,
            kicker: 'Client',
            title: 'Je suis client',
            text: 'Un besoin, plusieurs devis, un seul choix.',
            action: 'Lancer une demande',
            onTap: () => onRole('client'),
          ),
          const SizedBox(height: 12),
          _Door(
            navyDoor: false,
            kicker: 'Ouvrier',
            title: 'Je suis ouvrier',
            text: 'Votre fiche, vos zones, votre badge.',
            action: 'Ouvrir un compte',
            onTap: () => onRole('professional'),
          ),
        ],
      ),
    );
  }
}

class _SearchBar extends StatelessWidget {
  const _SearchBar({required this.onSearch});

  final VoidCallback onSearch;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white,
      elevation: 0,
      borderRadius: BorderRadius.circular(18),
      child: InkWell(
        borderRadius: BorderRadius.circular(18),
        onTap: onSearch,
        child: Padding(
          padding: const EdgeInsets.fromLTRB(14, 8, 8, 8),
          child: Row(
            children: [
              const Icon(Icons.search_rounded, color: navy),
              const SizedBox(width: 8),
              const Expanded(
                child: Text('Quel métier recherchez-vous ?', style: TextStyle(color: muted, fontSize: 15)),
              ),
              FilledButton(
                style: FilledButton.styleFrom(minimumSize: const Size(76, 40), padding: const EdgeInsets.symmetric(horizontal: 16)),
                onPressed: onSearch,
                child: const Text('Voir'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _Trust extends StatelessWidget {
  const _Trust({required this.icon, required this.text});

  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 12),
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16)),
      child: Column(
        children: [
          Icon(icon, color: orange, size: 22),
          const SizedBox(height: 6),
          Text(text, textAlign: TextAlign.center, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: navy, height: 1.2)),
        ],
      ),
    );
  }
}

class _Step extends StatelessWidget {
  const _Step({required this.number, required this.title, required this.text});

  final String number;
  final String title;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(
        children: [
          Container(
            width: 36,
            height: 36,
            alignment: Alignment.center,
            decoration: const BoxDecoration(color: navy, shape: BoxShape.circle),
            child: Text(number, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w800)),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontWeight: FontWeight.w800, color: navy)),
                Text(text, style: const TextStyle(color: muted, height: 1.3)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _Door extends StatelessWidget {
  const _Door({
    required this.navyDoor,
    required this.kicker,
    required this.title,
    required this.text,
    required this.action,
    required this.onTap,
  });

  final bool navyDoor;
  final String kicker;
  final String title;
  final String text;
  final String action;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final foreground = navyDoor ? Colors.white : navy;
    return Material(
      color: navyDoor ? navy : Colors.white,
      borderRadius: BorderRadius.circular(22),
      child: InkWell(
        borderRadius: BorderRadius.circular(22),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(18),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(kicker.toUpperCase(), style: TextStyle(color: orange, fontWeight: FontWeight.w800, fontSize: 12, letterSpacing: 1)),
              const SizedBox(height: 6),
              Text(title, style: TextStyle(color: foreground, fontSize: 22, fontWeight: FontWeight.w800)),
              const SizedBox(height: 4),
              Text(text, style: TextStyle(color: navyDoor ? const Color(0xFFFFEDD5) : muted, height: 1.35)),
              const SizedBox(height: 12),
              Text(action, style: TextStyle(color: navyDoor ? Colors.white : orange, fontWeight: FontWeight.w800)),
            ],
          ),
        ),
      ),
    );
  }
}

class _GuestTrades extends StatelessWidget {
  const _GuestTrades();

  @override
  Widget build(BuildContext context) {
    final api = AppScope.of(context).api;
    return RemoteBody<List<Trade>>(
      load: api.trades,
      builder: (trades, _) {
        if (trades.isEmpty) {
          return ListView(children: const [EmptyHint('Les métiers s’affichent dès que le catalogue répond.')]);
        }
        return GridView.builder(
          padding: const EdgeInsets.fromLTRB(20, 16, 20, 24),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            mainAxisSpacing: 10,
            crossAxisSpacing: 10,
            childAspectRatio: 1.25,
          ),
          itemCount: trades.length,
          itemBuilder: (context, index) {
            final trade = trades[index];
            final color = TradeLook.color(trade.name);
            return Material(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              child: Padding(
                padding: const EdgeInsets.all(14),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      width: 42,
                      height: 42,
                      decoration: BoxDecoration(color: color.withValues(alpha: 0.14), borderRadius: BorderRadius.circular(14)),
                      child: Icon(TradeLook.icon(trade.name), color: color),
                    ),
                    const Spacer(),
                    Text(TradeLook.label(trade.name), style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16, color: navy)),
                    Text(trade.name, style: const TextStyle(color: muted, fontSize: 12)),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }
}

class _GuestLock extends StatelessWidget {
  const _GuestLock({required this.title, required this.text, required this.action, required this.onTap});

  final String title;
  final String text;
  final String action;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        const SafeArea(bottom: false, child: SizedBox(height: 12)),
        Text(title, style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w800, color: navy)),
        const SizedBox(height: 8),
        Text(text, style: const TextStyle(color: muted, height: 1.4)),
        const SizedBox(height: 18),
        FilledButton(onPressed: onTap, child: Text(action)),
      ],
    );
  }
}

class _GuestAccount extends StatelessWidget {
  const _GuestAccount({required this.onRole});

  final void Function(String role) onRole;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        const SafeArea(bottom: false, child: SizedBox(height: 8)),
        const Text('Compte', style: TextStyle(fontSize: 28, fontWeight: FontWeight.w800, color: navy)),
        const SizedBox(height: 6),
        const Text('Choisissez comment vous utilisez Jefamora.', style: TextStyle(color: muted)),
        const SizedBox(height: 16),
        _Door(
          navyDoor: true,
          kicker: 'Client',
          title: 'Je suis client',
          text: 'Décrivez le besoin, comparez les devis, suivez la mission.',
          action: 'Se connecter',
          onTap: () => onRole('client'),
        ),
        const SizedBox(height: 12),
        _Door(
          navyDoor: false,
          kicker: 'Ouvrier',
          title: 'Je suis ouvrier',
          text: 'Recevez les demandes, envoyez un devis, suivez le chantier.',
          action: 'Se connecter',
          onTap: () => onRole('professional'),
        ),
      ],
    );
  }
}
