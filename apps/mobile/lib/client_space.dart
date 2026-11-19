import 'package:material_ui/material_ui.dart';

import 'api.dart';
import 'scope.dart';
import 'theme.dart';
import 'trade_look.dart';
import 'widgets.dart';

class ClientMemory extends ChangeNotifier {
  final addresses = <ClientAddress>[
    ClientAddress('Maison', 'Plateau, Dakar', true),
    ClientAddress('Bureau', 'Almadies, Dakar', false),
  ];
  final favorites = <String>{};
  String? gpsLabel;

  ClientAddress get current => addresses.firstWhere((item) => item.isDefault, orElse: () => addresses.first);

  void allowGps() {
    gpsLabel = 'Position actuelle';
    notifyListeners();
  }

  void toggleFavorite(String name) {
    if (!favorites.add(name)) favorites.remove(name);
    notifyListeners();
  }

  void addAddress(String label, String line) {
    addresses.add(ClientAddress(label, line, addresses.isEmpty));
    notifyListeners();
  }

  void makeDefault(int index) {
    for (var i = 0; i < addresses.length; i++) {
      addresses[i].isDefault = i == index;
    }
    notifyListeners();
  }

  void removeAddress(int index) {
    final wasDefault = addresses[index].isDefault;
    addresses.removeAt(index);
    if (wasDefault && addresses.isNotEmpty) addresses.first.isDefault = true;
    notifyListeners();
  }
}

class ClientAddress {
  ClientAddress(this.label, this.line, this.isDefault);
  final String label;
  final String line;
  bool isDefault;
}

class ClientScope extends InheritedNotifier<ClientMemory> {
  const ClientScope({super.key, required ClientMemory memory, required super.child}) : super(notifier: memory);

  static ClientMemory of(BuildContext context) {
    final scope = context.dependOnInheritedWidgetOfExactType<ClientScope>();
    assert(scope != null, 'ClientScope absent');
    return scope!.notifier!;
  }
}

class ClientSpace extends StatefulWidget {
  const ClientSpace({super.key});

  @override
  State<ClientSpace> createState() => _ClientSpaceState();
}

class _ClientSpaceState extends State<ClientSpace> {
  final _memory = ClientMemory();
  int _index = 0;

  @override
  void dispose() {
    _memory.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final pages = [
      HomeTab(onSearch: () => setState(() => _index = 1)),
      const SearchTab(),
      const DemandsTab(),
      const ProfileTab(),
    ];
    return ClientScope(
      memory: _memory,
      child: Scaffold(
        body: pages[_index],
        bottomNavigationBar: JefamoraBar(
          index: _index,
          onSelect: (value) => setState(() => _index = value),
          destinations: const [
            NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home_rounded), label: 'Accueil'),
            NavigationDestination(icon: Icon(Icons.search), selectedIcon: Icon(Icons.search_rounded), label: 'Recherche'),
            NavigationDestination(icon: Icon(Icons.receipt_long_outlined), selectedIcon: Icon(Icons.receipt_long_rounded), label: 'Demandes'),
            NavigationDestination(icon: Icon(Icons.person_outline), selectedIcon: Icon(Icons.person_rounded), label: 'Profil'),
          ],
        ),
      ),
    );
  }
}

class HomeTab extends StatelessWidget {
  const HomeTab({super.key, required this.onSearch});

  final VoidCallback onSearch;

  @override
  Widget build(BuildContext context) {
    final profile = AppScope.of(context).session.profile;
    final first = profile?.firstName.trim() ?? '';
    final api = AppScope.of(context).api;
    return ColoredBox(
      color: cream,
      child: RemoteBody<List<Trade>>(
        load: api.trades,
        builder: (trades, _) {
          return ListView(
            padding: EdgeInsets.zero,
            children: [
              Container(
                padding: const EdgeInsets.fromLTRB(20, 8, 20, 22),
                decoration: const BoxDecoration(color: navy, borderRadius: BorderRadius.vertical(bottom: Radius.circular(28))),
                child: SafeArea(
                  bottom: false,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const BrandLockup(light: true),
                          const Spacer(),
                          IconButton(
                            onPressed: () => _push(context, const NotificationsPage()),
                            icon: const Icon(Icons.notifications_none_rounded, color: Colors.white),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(first.isEmpty ? 'Bonjour' : 'Bonjour, $first', style: const TextStyle(color: Colors.white, fontSize: 26, fontWeight: FontWeight.w800)),
                      const SizedBox(height: 4),
                      const Text('Quel métier cherchez-vous aujourd’hui ?', style: TextStyle(color: Color(0xFFFFE7A3))),
                      const SizedBox(height: 14),
                      Material(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(16),
                        child: InkWell(
                          borderRadius: BorderRadius.circular(16),
                          onTap: onSearch,
                          child: const Padding(
                            padding: EdgeInsets.symmetric(horizontal: 14, vertical: 14),
                            child: Row(
                              children: [
                                Icon(Icons.search_rounded, color: navy),
                                SizedBox(width: 8),
                                Text('Rechercher un métier ou un ouvrier', style: TextStyle(color: muted)),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              const _SectionTitle('Catégories'),
              SizedBox(
                height: 96,
                child: ListView.separated(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  itemCount: trades.isEmpty ? _sampleTrades.length : trades.take(8).length,
                  separatorBuilder: (_, _) => const SizedBox(width: 10),
                  itemBuilder: (context, index) {
                    if (trades.isEmpty) {
                      final sample = _sampleTrades[index];
                      return _CategoryChip(name: sample, onTap: () => _push(context, WorkerListPage(title: sample)));
                    }
                    final trade = trades[index];
                    return _CategoryChip(name: TradeLook.label(trade.name), onTap: () => _push(context, WorkerListPage(title: trade.name, tradeId: trade.id)));
                  },
                ),
              ),
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 8, 20, 0),
                child: Material(
                  color: orange,
                  borderRadius: BorderRadius.circular(20),
                  child: const Padding(
                    padding: EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('0 FCFA de commission', style: TextStyle(color: navy, fontWeight: FontWeight.w800, fontSize: 18)),
                        SizedBox(height: 4),
                        Text('Le règlement de la prestation reste entre vous et l’ouvrier.', style: TextStyle(color: navy, height: 1.3)),
                      ],
                    ),
                  ),
                ),
              ),
              const _SectionTitle('Recommandés'),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                child: Column(
                  children: [
                    for (final person in _people)
                      WorkerCard(
                        person: person,
                        onTap: () => _push(context, WorkerProfilePage(person: person)),
                      ),
                  ],
                ),
              ),
              const SizedBox(height: 12),
            ],
          );
        },
      ),
    );
  }
}

class SearchTab extends StatefulWidget {
  const SearchTab({super.key});

  @override
  State<SearchTab> createState() => _SearchTabState();
}

class _SearchTabState extends State<SearchTab> {
  String _query = '';

  @override
  Widget build(BuildContext context) {
    final api = AppScope.of(context).api;
    return Scaffold(
      backgroundColor: cream,
      appBar: AppBar(title: const Text('Recherche')),
      body: RemoteBody<List<Trade>>(
        load: api.trades,
        builder: (trades, _) {
          final source = trades.isEmpty ? _sampleTrades.map((name) => Trade(id: name, name: name)).toList() : trades;
          final wanted = _query.trim().toLowerCase();
          final shown = source.where((trade) => trade.name.toLowerCase().contains(wanted) || TradeLook.label(trade.name).toLowerCase().contains(wanted)).toList();
          return ListView(
            padding: const EdgeInsets.all(20),
            children: [
              TextField(
                onChanged: (value) => setState(() => _query = value),
                decoration: const InputDecoration(hintText: 'Métier, ex. plombier', prefixIcon: Icon(Icons.search_rounded, color: navy)),
              ),
              const SizedBox(height: 16),
              const Text('Suggestions', style: TextStyle(fontWeight: FontWeight.w800, color: navy)),
              const SizedBox(height: 8),
              if (shown.isEmpty) const EmptyHint('Aucun métier ne correspond. Essayez un autre mot.'),
              for (final trade in shown)
                Card(
                  child: ListTile(
                    leading: CircleAvatar(backgroundColor: lavender, child: Icon(TradeLook.icon(trade.name), color: navy)),
                    title: Text(TradeLook.label(trade.name), style: const TextStyle(fontWeight: FontWeight.w700)),
                    subtitle: Text(trade.name),
                    onTap: () => _push(context, WorkerListPage(title: trade.name, tradeId: trade.id == trade.name ? null : trade.id)),
                  ),
                ),
            ],
          );
        },
      ),
    );
  }
}

class WorkerListPage extends StatelessWidget {
  const WorkerListPage({super.key, required this.title, this.tradeId});

  final String title;
  final String? tradeId;

  @override
  Widget build(BuildContext context) {
    final api = AppScope.of(context).api;
    return Scaffold(
      backgroundColor: cream,
      appBar: AppBar(
        title: Text(title),
        actions: [
          IconButton(onPressed: () => _push(context, const FilterPage()), icon: const Icon(Icons.tune_rounded)),
        ],
      ),
      body: FutureBuilder<List<ProCard>>(
        future: tradeId == null ? Future.value(const []) : api.professionals(trade: tradeId),
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done && tradeId != null) {
            return const Center(child: CircularProgressIndicator(color: navy));
          }
          if (snapshot.hasError) {
            return const _StateBlock(icon: Icons.wifi_off_rounded, title: 'Erreur réseau', text: 'La liste n’a pas pu être chargée.', action: 'Réessayer');
          }
          final remote = snapshot.data ?? const <ProCard>[];
          final people = remote.isEmpty ? _people.where((person) => person.trade == title || title.length < 3).toList() : remote.map(_fromPro).toList();
          final shown = people.isEmpty ? _people : people;
          if (remote.isEmpty && tradeId != null) {
            return const _StateBlock(icon: Icons.search_off_rounded, title: 'Aucun résultat', text: 'Aucun ouvrier vérifié pour ce métier. Élargissez la zone ou changez de filtre.', action: 'Changer les filtres');
          }
          return ListView(
            padding: const EdgeInsets.all(20),
            children: [
              for (final person in shown) WorkerCard(person: person, onTap: () => _push(context, WorkerProfilePage(person: person))),
            ],
          );
        },
      ),
    );
  }
}

class FilterPage extends StatefulWidget {
  const FilterPage({super.key});

  @override
  State<FilterPage> createState() => _FilterPageState();
}

class _FilterPageState extends State<FilterPage> {
  String _sort = 'Note';
  double _price = 25000;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: cream,
      appBar: AppBar(title: const Text('Filtres et tri')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const Text('Trier par', style: TextStyle(fontWeight: FontWeight.w800, color: navy)),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            children: [
              for (final name in const ['Note', 'Proximité', 'Prix', 'Expérience'])
                ChoiceChip(
                  label: Text(name),
                  selected: _sort == name,
                  selectedColor: orange,
                  onSelected: (_) => setState(() => _sort = name),
                ),
            ],
          ),
          const SizedBox(height: 18),
          Text('Budget indicatif : ${_price.round()} FCFA', style: const TextStyle(fontWeight: FontWeight.w800, color: navy)),
          Slider(value: _price, min: 5000, max: 150000, divisions: 29, activeColor: navy, onChanged: (value) => setState(() => _price = value)),
          const Text('Disponible aujourd’hui', style: TextStyle(color: muted)),
          SwitchListTile(contentPadding: EdgeInsets.zero, value: true, activeThumbColor: navy, onChanged: (_) {}, title: const Text('Profils vérifiés seulement')),
          const SizedBox(height: 12),
          FilledButton(onPressed: () => Navigator.pop(context), child: const Text('Voir les résultats')),
        ],
      ),
    );
  }
}

class WorkerProfilePage extends StatelessWidget {
  const WorkerProfilePage({super.key, required this.person});

  final ClientWorker person;

  @override
  Widget build(BuildContext context) {
    final memory = ClientScope.of(context);
    final saved = memory.favorites.contains(person.name);
    return Scaffold(
      backgroundColor: cream,
      appBar: AppBar(title: const Text('Profil')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Row(
            children: [
              CircleAvatar(radius: 32, backgroundColor: navy, child: Text(person.name.characters.first, style: const TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.w800))),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(person.name, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: navy)),
                    Text(person.trade, style: const TextStyle(color: muted)),
                    Text('${person.rating} · ${person.place}', style: const TextStyle(color: navy, fontWeight: FontWeight.w700)),
                  ],
                ),
              ),
              IconButton(
                onPressed: () => memory.toggleFavorite(person.name),
                icon: Icon(saved ? Icons.favorite_rounded : Icons.favorite_border_rounded, color: saved ? orange : navy),
              ),
            ],
          ),
          const SizedBox(height: 16),
          const _InfoCard(title: 'Compétences', text: 'Dépannage, installation et petit chantier. Profil contrôlé avant d’être visible.'),
          const _InfoCard(title: 'Disponibilité', text: 'Créneaux en journée. La date exacte se choisit dans la demande.'),
          const _InfoCard(title: 'Tarif indicatif', text: 'Le prix ferme arrive dans le devis. Jefamora ne prend pas de commission.'),
          const _InfoCard(title: 'Avis', text: 'Les avis s’affichent après une mission confirmée.'),
          const SizedBox(height: 8),
          FilledButton(onPressed: () => _push(context, DemandFlowPage(person: person)), child: const Text('Demander ce professionnel')),
          const SizedBox(height: 8),
          OutlinedButton(onPressed: () => _push(context, const MapPage()), child: const Text('Voir sur la carte')),
        ],
      ),
    );
  }
}

class MapPage extends StatelessWidget {
  const MapPage({super.key});

  @override
  Widget build(BuildContext context) {
    final allowed = ClientScope.of(context).gpsLabel != null;
    return Scaffold(
      backgroundColor: cream,
      appBar: AppBar(title: const Text('À proximité')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          if (!allowed)
            const _StateBlock(icon: Icons.location_off_rounded, title: 'Localisation indisponible', text: 'Autorisez le GPS ou saisissez l’adresse de la prestation.', action: 'Choisir une adresse')
          else
            Container(
              height: 220,
              decoration: BoxDecoration(color: const Color(0xFFE4DFF5), borderRadius: BorderRadius.circular(24)),
              child: const Stack(
                children: [
                  Positioned(left: 40, top: 50, child: _Pin(label: 'Awa')),
                  Positioned(left: 150, top: 90, child: _Pin(label: 'Moussa')),
                  Positioned(right: 36, top: 40, child: _Pin(label: 'Fatou')),
                ],
              ),
            ),
          const SizedBox(height: 12),
          const Text('La position du client sert à trouver l’adresse des travaux. Le déplacement de l’ouvrier n’est suivi qu’après une mission acceptée, avec son accord.', style: TextStyle(color: muted, height: 1.35)),
          const SizedBox(height: 12),
          FilledButton(onPressed: () => _push(context, const GpsPage()), child: const Text('Autoriser la localisation')),
          const SizedBox(height: 8),
          OutlinedButton(onPressed: () => _push(context, const AddressBookPage()), child: const Text('Choisir une adresse')),
        ],
      ),
    );
  }
}

class GpsPage extends StatelessWidget {
  const GpsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: cream,
      appBar: AppBar(title: const Text('Localisation')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            const Spacer(),
            const Icon(Icons.my_location_rounded, color: navy, size: 72),
            const SizedBox(height: 16),
            const Text('Utiliser votre position ?', textAlign: TextAlign.center, style: TextStyle(fontSize: 26, fontWeight: FontWeight.w800, color: navy)),
            const SizedBox(height: 8),
            const Text('Elle sert à proposer des ouvriers autour de l’adresse des travaux. Vous pouvez aussi la saisir à la main.', textAlign: TextAlign.center, style: TextStyle(color: muted, height: 1.4)),
            const Spacer(),
            FilledButton(
              onPressed: () {
                ClientScope.of(context).allowGps();
                _push(context, const AddressPickerPage());
              },
              child: const Text('Autoriser'),
            ),
            const SizedBox(height: 8),
            OutlinedButton(onPressed: () => _push(context, const AddressPickerPage()), child: const Text('Saisir l’adresse')),
          ],
        ),
      ),
    );
  }
}

class AddressPickerPage extends StatelessWidget {
  const AddressPickerPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: cream,
      appBar: AppBar(title: const Text('Adresse des travaux')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const TextField(decoration: InputDecoration(labelText: 'Rechercher une adresse', prefixIcon: Icon(Icons.search_rounded))),
          const SizedBox(height: 12),
          Container(
            height: 160,
            alignment: Alignment.center,
            decoration: BoxDecoration(color: const Color(0xFFE4DFF5), borderRadius: BorderRadius.circular(20)),
            child: const Text('Placez le repère sur la carte', style: TextStyle(color: navy, fontWeight: FontWeight.w700)),
          ),
          const SizedBox(height: 12),
          FilledButton(
            onPressed: () {
              ClientScope.of(context).addAddress('Prestation', 'Adresse choisie sur la carte');
              Navigator.pop(context);
            },
            child: const Text('Utiliser cette adresse'),
          ),
        ],
      ),
    );
  }
}

class AddressBookPage extends StatefulWidget {
  const AddressBookPage({super.key});

  @override
  State<AddressBookPage> createState() => _AddressBookPageState();
}

class _AddressBookPageState extends State<AddressBookPage> {
  final _label = TextEditingController();
  final _line = TextEditingController();

  @override
  void dispose() {
    _label.dispose();
    _line.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final memory = ClientScope.of(context);
    return Scaffold(
      backgroundColor: cream,
      appBar: AppBar(title: const Text('Mes adresses')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          if (memory.addresses.isEmpty) const EmptyHint('Ajoutez l’adresse où la prestation doit avoir lieu.'),
          for (var i = 0; i < memory.addresses.length; i++)
            Card(
              child: ListTile(
                title: Text(memory.addresses[i].label, style: const TextStyle(fontWeight: FontWeight.w800)),
                subtitle: Text(memory.addresses[i].line),
                trailing: memory.addresses[i].isDefault ? const StatusChip('Par défaut') : TextButton(onPressed: () => memory.makeDefault(i), child: const Text('Définir')),
                onLongPress: () => memory.removeAddress(i),
              ),
            ),
          const SizedBox(height: 8),
          TextField(controller: _label, decoration: const InputDecoration(labelText: 'Nom, ex. Maison')),
          const SizedBox(height: 8),
          TextField(controller: _line, decoration: const InputDecoration(labelText: 'Adresse')),
          const SizedBox(height: 8),
          FilledButton(
            onPressed: () {
              if (_label.text.trim().isEmpty || _line.text.trim().isEmpty) return;
              memory.addAddress(_label.text.trim(), _line.text.trim());
              _label.clear();
              _line.clear();
            },
            child: const Text('Ajouter'),
          ),
          const SizedBox(height: 6),
          const Text('Appui long sur une adresse pour la retirer.', style: TextStyle(color: muted, fontSize: 12)),
        ],
      ),
    );
  }
}

class DemandFlowPage extends StatefulWidget {
  const DemandFlowPage({super.key, required this.person});

  final ClientWorker person;

  @override
  State<DemandFlowPage> createState() => _DemandFlowPageState();
}

class _DemandFlowPageState extends State<DemandFlowPage> {
  int _step = 0;
  final _need = TextEditingController();
  bool _photo = false;
  int _day = 0;
  String _slot = 'Après-midi';

  @override
  void dispose() {
    _need.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final titles = ['Le besoin', 'Date et heure', 'Confirmation'];
    return Scaffold(
      backgroundColor: cream,
      appBar: AppBar(title: Text(titles[_step])),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text('${_step + 1} / 3', style: const TextStyle(color: muted, fontWeight: FontWeight.w700)),
          const SizedBox(height: 12),
          if (_step == 0) ...[
            Text(widget.person.trade, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: navy)),
            const SizedBox(height: 12),
            TextField(controller: _need, minLines: 4, maxLines: 6, decoration: const InputDecoration(labelText: 'Décrivez le besoin')),
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed: () => setState(() => _photo = !_photo),
              icon: Icon(_photo ? Icons.check_circle : Icons.add_a_photo_outlined),
              label: Text(_photo ? 'Photo jointe' : 'Ajouter une photo'),
            ),
          ],
          if (_step == 1) ...[
            const Text('Jour', style: TextStyle(fontWeight: FontWeight.w800, color: navy)),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: [
                for (var i = 0; i < 5; i++)
                  ChoiceChip(label: Text('J+${i + 1}'), selected: _day == i, selectedColor: orange, onSelected: (_) => setState(() => _day = i)),
              ],
            ),
            const SizedBox(height: 16),
            const Text('Créneau', style: TextStyle(fontWeight: FontWeight.w800, color: navy)),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: [
                for (final slot in const ['Matin', 'Après-midi', 'Soir'])
                  ChoiceChip(label: Text(slot), selected: _slot == slot, selectedColor: orange, onSelected: (_) => setState(() => _slot = slot)),
              ],
            ),
          ],
          if (_step == 2) ...[
            _InfoCard(title: widget.person.name, text: '${widget.person.trade} · ${widget.person.place}'),
            _InfoCard(title: 'Besoin', text: _need.text.trim().isEmpty ? 'Description à préciser' : _need.text.trim()),
            _InfoCard(title: 'Moment', text: 'J+${_day + 1} · $_slot'),
            _InfoCard(title: 'Adresse', text: ClientScope.of(context).addresses.isEmpty ? 'Adresse à choisir' : ClientScope.of(context).current.line),
            const _InfoCard(title: 'Prix', text: 'Estimatif uniquement. Le montant ferme est celui du devis accepté.'),
          ],
          const SizedBox(height: 16),
          FilledButton(
            onPressed: () {
              if (_step < 2) {
                setState(() => _step += 1);
                return;
              }
              _push(context, const DemandSentPage());
            },
            child: Text(_step == 2 ? 'Envoyer la demande' : 'Continuer'),
          ),
        ],
      ),
    );
  }
}

class DemandSentPage extends StatelessWidget {
  const DemandSentPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: cream,
      body: const _StateBlock(icon: Icons.mark_email_read_rounded, title: 'Demande envoyée', text: 'L’ouvrier reçoit votre besoin. Vous suivez le statut dans l’onglet Demandes.', action: 'Voir mes demandes'),
    );
  }
}

class DemandsTab extends StatelessWidget {
  const DemandsTab({super.key});

  @override
  Widget build(BuildContext context) {
    final api = AppScope.of(context).api;
    return Scaffold(
      backgroundColor: cream,
      appBar: AppBar(
        title: const Text('Demandes'),
        actions: [IconButton(onPressed: () => _push(context, const HistoryPage()), icon: const Icon(Icons.history_rounded))],
      ),
      body: RemoteBody<List<ServiceRequestItem>>(
        load: api.requests,
        builder: (items, reload) {
          if (items.isEmpty) {
            return ListView(
              children: const [
                _StateBlock(icon: Icons.inbox_rounded, title: 'Aucune demande', text: 'Décrivez un premier besoin depuis un profil d’ouvrier.', action: 'Commencer'),
              ],
            );
          }
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              for (final item in items)
                Card(
                  child: ListTile(
                    title: Text(item.title, style: const TextStyle(fontWeight: FontWeight.w800)),
                    subtitle: Text(requestLabel(item.status)),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: () => _push(context, DemandDetailPage(item: item)),
                  ),
                ),
            ],
          );
        },
      ),
    );
  }
}

class DemandDetailPage extends StatelessWidget {
  const DemandDetailPage({super.key, required this.item});

  final ServiceRequestItem item;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: cream,
      appBar: AppBar(title: const Text('Détail')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(item.title, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w800, color: navy)),
          const SizedBox(height: 8),
          StatusChip(requestLabel(item.status)),
          const SizedBox(height: 12),
          Text(item.description),
          const SizedBox(height: 16),
          OutlinedButton(onPressed: () => _push(context, CancelDemandPage(item: item)), child: const Text('Annuler la demande')),
          const SizedBox(height: 8),
          FilledButton(onPressed: () => _push(context, ChatPage(title: item.title)), child: const Text('Écrire à l’ouvrier')),
        ],
      ),
    );
  }
}

class CancelDemandPage extends StatelessWidget {
  const CancelDemandPage({super.key, required this.item});

  final ServiceRequestItem item;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: cream,
      appBar: AppBar(title: const Text('Annulation')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(item.title, style: const TextStyle(fontWeight: FontWeight.w800, color: navy, fontSize: 20)),
          const SizedBox(height: 12),
          const TextField(decoration: InputDecoration(labelText: 'Motif')),
          const SizedBox(height: 12),
          FilledButton(
            onPressed: () async {
              try {
                await AppScope.of(context).api.cancelRequest(item.id);
              } catch (_) {}
              if (context.mounted) _push(context, const _StateBlock(icon: Icons.cancel_outlined, title: 'Demande annulée', text: 'Le statut est mis à jour. Vous pouvez relancer un besoin similaire.', action: 'Retour'));
            },
            child: const Text('Confirmer l’annulation'),
          ),
        ],
      ),
    );
  }
}

class HistoryPage extends StatelessWidget {
  const HistoryPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const _FilteredDemands(title: 'Historique');
  }
}

class _FilteredDemands extends StatefulWidget {
  const _FilteredDemands({required this.title});

  final String title;

  @override
  State<_FilteredDemands> createState() => _FilteredDemandsState();
}

class _FilteredDemandsState extends State<_FilteredDemands> {
  String _filter = 'Toutes';

  @override
  Widget build(BuildContext context) {
    final api = AppScope.of(context).api;
    return Scaffold(
      backgroundColor: cream,
      appBar: AppBar(title: Text(widget.title)),
      body: RemoteBody<List<ServiceRequestItem>>(
        load: api.requests,
        builder: (items, _) {
          final shown = items.where((item) {
            if (_filter == 'En attente') return item.status == 'open' || item.status == 'quoted';
            if (_filter == 'Terminées') return item.status == 'closed' || item.status == 'booked';
            if (_filter == 'Annulées') return item.status == 'cancelled';
            return true;
          }).toList();
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              TextField(decoration: const InputDecoration(hintText: 'Rechercher une demande', prefixIcon: Icon(Icons.search_rounded))),
              const SizedBox(height: 10),
              Wrap(
                spacing: 8,
                children: [
                  for (final name in const ['Toutes', 'En attente', 'Terminées', 'Annulées'])
                    ChoiceChip(label: Text(name), selected: _filter == name, selectedColor: orange, onSelected: (_) => setState(() => _filter = name)),
                ],
              ),
              if (shown.isEmpty) const EmptyHint('Rien dans ce filtre. Une demande terminée pourra être refaite depuis son détail.'),
              for (final item in shown)
                Card(
                  child: ListTile(
                    title: Text(item.title, style: const TextStyle(fontWeight: FontWeight.w700)),
                    subtitle: Text(requestLabel(item.status)),
                    onTap: () => _push(context, DemandDetailPage(item: item)),
                  ),
                ),
            ],
          );
        },
      ),
    );
  }
}

class NotificationsPage extends StatelessWidget {
  const NotificationsPage({super.key});

  @override
  Widget build(BuildContext context) {
    const notes = [
      ('Demande envoyée', 'Votre besoin a été transmis.'),
      ('Nouveau message', 'Un ouvrier a répondu.'),
      ('Statut', 'Un devis est disponible.'),
    ];
    return Scaffold(
      backgroundColor: cream,
      appBar: AppBar(title: const Text('Notifications')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          for (final note in notes)
            Card(
              child: ListTile(
                leading: const CircleAvatar(backgroundColor: lavender, child: Icon(Icons.notifications_none_rounded, color: navy)),
                title: Text(note.$1, style: const TextStyle(fontWeight: FontWeight.w800)),
                subtitle: Text(note.$2),
                onTap: () => _push(context, NoticePage(title: note.$1, body: note.$2)),
              ),
            ),
        ],
      ),
    );
  }
}

class NoticePage extends StatelessWidget {
  const NoticePage({super.key, required this.title, required this.body});

  final String title;
  final String body;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: cream,
      appBar: AppBar(title: const Text('Notification')),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: const TextStyle(fontSize: 26, fontWeight: FontWeight.w800, color: navy)),
            const SizedBox(height: 8),
            Text(body, style: const TextStyle(color: muted, height: 1.4)),
            const Spacer(),
            FilledButton(onPressed: () => Navigator.pop(context), child: const Text('Voir la demande')),
          ],
        ),
      ),
    );
  }
}

class ChatPage extends StatefulWidget {
  const ChatPage({super.key, required this.title});

  final String title;

  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  final _text = TextEditingController();
  final _lines = <(bool, String)>[
    (false, 'Bonjour, je peux passer sur le créneau choisi.'),
  ];

  @override
  void dispose() {
    _text.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: cream,
      appBar: AppBar(title: Text(widget.title)),
      body: Column(
        children: [
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                for (final line in _lines)
                  Align(
                    alignment: line.$1 ? Alignment.centerRight : Alignment.centerLeft,
                    child: Container(
                      margin: const EdgeInsets.only(bottom: 8),
                      padding: const EdgeInsets.all(12),
                      constraints: const BoxConstraints(maxWidth: 260),
                      decoration: BoxDecoration(color: line.$1 ? navy : Colors.white, borderRadius: BorderRadius.circular(16)),
                      child: Text(line.$2, style: TextStyle(color: line.$1 ? Colors.white : navy)),
                    ),
                  ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 0, 12, 12),
            child: Row(
              children: [
                Expanded(child: TextField(controller: _text, decoration: const InputDecoration(hintText: 'Message'))),
                const SizedBox(width: 8),
                IconButton.filled(
                  style: IconButton.styleFrom(backgroundColor: navy),
                  onPressed: () {
                    if (_text.text.trim().isEmpty) return;
                    setState(() => _lines.add((true, _text.text.trim())));
                    _text.clear();
                  },
                  icon: const Icon(Icons.send_rounded, color: Colors.white),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class ThreadsPage extends StatelessWidget {
  const ThreadsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: cream,
      appBar: AppBar(title: const Text('Messages')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          for (final name in const ['Awa Ndiaye', 'Moussa Diop'])
            Card(
              child: ListTile(
                leading: CircleAvatar(backgroundColor: navy, child: Text(name.characters.first, style: const TextStyle(color: Colors.white))),
                title: Text(name, style: const TextStyle(fontWeight: FontWeight.w800)),
                subtitle: const Text('Dernier échange sur la demande'),
                onTap: () => _push(context, ChatPage(title: name)),
              ),
            ),
        ],
      ),
    );
  }
}

class PayPage extends StatelessWidget {
  const PayPage({super.key});

  @override
  Widget build(BuildContext context) {
    const methods = ['Wave', 'Orange Money', 'Free Money', 'Espèces', 'Carte bancaire'];
    return Scaffold(
      backgroundColor: cream,
      appBar: AppBar(title: const Text('Paiement')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const Text('Le montant est celui du devis accepté. Jefamora ne prélève pas de commission.', style: TextStyle(color: muted, height: 1.35)),
          const SizedBox(height: 12),
          for (final method in methods)
            Card(
              child: ListTile(
                title: Text(method, style: const TextStyle(fontWeight: FontWeight.w700)),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => _push(context, PayResultPage(method: method)),
              ),
            ),
        ],
      ),
    );
  }
}

class PayResultPage extends StatelessWidget {
  const PayResultPage({super.key, required this.method});

  final String method;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: cream,
      body: _StateBlock(
        icon: Icons.payments_rounded,
        title: 'Paiement préparé',
        text: '$method sera utilisé entre vous et l’ouvrier. Le reçu reprend le devis accepté.',
        action: 'Voir le reçu',
      ),
    );
  }
}

class ReceiptPage extends StatelessWidget {
  const ReceiptPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: cream,
      appBar: AppBar(title: const Text('Reçu')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: const [
          _InfoCard(title: 'Prestation', text: 'Intervention convenue dans le devis.'),
          _InfoCard(title: 'Montant', text: 'Celui du devis accepté, en FCFA.'),
          _InfoCard(title: 'Commission Jefamora', text: '0 FCFA'),
        ],
      ),
    );
  }
}

class ReviewPage extends StatelessWidget {
  const ReviewPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: cream,
      appBar: AppBar(title: const Text('Évaluation')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const Row(children: [Icon(Icons.star_rounded, color: orange), Icon(Icons.star_rounded, color: orange), Icon(Icons.star_rounded, color: orange), Icon(Icons.star_rounded, color: orange), Icon(Icons.star_outline_rounded, color: orange)]),
          const SizedBox(height: 12),
          const TextField(minLines: 3, maxLines: 5, decoration: InputDecoration(labelText: 'Votre commentaire')),
          const SizedBox(height: 12),
          FilledButton(onPressed: () => Navigator.pop(context), child: const Text('Publier l’avis')),
        ],
      ),
    );
  }
}

class ProfileTab extends StatelessWidget {
  const ProfileTab({super.key});

  @override
  Widget build(BuildContext context) {
    final profile = AppScope.of(context).session.profile;
    return Scaffold(
      backgroundColor: cream,
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const SafeArea(bottom: false, child: SizedBox(height: 8)),
          Text(profile?.displayName ?? 'Profil', style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w800, color: navy)),
          Text(profile?.email ?? '', style: const TextStyle(color: muted)),
          const SizedBox(height: 16),
          _Link('Modifier mes informations', const EditProfilePage()),
          _Link('Mes favoris', const FavoritesPage()),
          _Link('Mes avis', const ReviewPage()),
          _Link('Mes adresses', const AddressBookPage()),
          _Link('Messages', const ThreadsPage()),
          _Link('Paiements', const PayPage()),
          _Link('Historique des paiements', const ReceiptPage()),
          _Link('Paramètres', const SettingsPage()),
          _Link('Aide', const HelpPage()),
          _Link('À propos', const AboutPage()),
          const SizedBox(height: 8),
          OutlinedButton(onPressed: () => AppScope.of(context).api.logout(), child: const Text('Se déconnecter')),
        ],
      ),
    );
  }
}

class EditProfilePage extends StatelessWidget {
  const EditProfilePage({super.key});

  @override
  Widget build(BuildContext context) {
    final profile = AppScope.of(context).session.profile;
    return Scaffold(
      backgroundColor: cream,
      appBar: AppBar(title: const Text('Mes informations')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          TextField(decoration: InputDecoration(labelText: 'Prénom', hintText: profile?.firstName)),
          const SizedBox(height: 12),
          TextField(decoration: InputDecoration(labelText: 'Nom', hintText: profile?.lastName)),
          const SizedBox(height: 12),
          TextField(decoration: InputDecoration(labelText: 'Téléphone', hintText: profile?.phone)),
          const SizedBox(height: 12),
          TextField(decoration: InputDecoration(labelText: 'E-mail', hintText: profile?.email)),
          const SizedBox(height: 16),
          const FilledButton(onPressed: null, child: Text('Enregistrer')),
        ],
      ),
    );
  }
}

class FavoritesPage extends StatelessWidget {
  const FavoritesPage({super.key});

  @override
  Widget build(BuildContext context) {
    final names = ClientScope.of(context).favorites.toList();
    return Scaffold(
      backgroundColor: cream,
      appBar: AppBar(title: const Text('Favoris')),
      body: names.isEmpty
          ? const _StateBlock(icon: Icons.favorite_border_rounded, title: 'Aucun favori', text: 'Enregistrez un ouvrier depuis son profil.', action: 'Explorer')
          : ListView(padding: const EdgeInsets.all(16), children: [for (final name in names) WorkerCard(person: _people.firstWhere((item) => item.name == name, orElse: () => ClientWorker(name, 'Métier', '—', 'Dakar')), onTap: () {})]),
    );
  }
}

class SettingsPage extends StatelessWidget {
  const SettingsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: cream,
      appBar: AppBar(title: const Text('Paramètres')),
      body: ListView(
        children: [
          _Link('Confidentialité et sécurité', const PrivacyPage()),
          _Link('Conditions d’utilisation', const LegalPage(title: 'Conditions', text: 'L’usage de Jefamora suppose un compte confirmé. Un seul devis est retenu par demande.')),
          _Link('Politique de confidentialité', const LegalPage(title: 'Confidentialité', text: 'Le téléphone, l’e-mail et l’adresse des travaux servent à la mise en relation. La position de l’ouvrier n’est suivie qu’avec son accord, pendant une mission acceptée.')),
          _Link('Compte suspendu', const _StateBlock(icon: Icons.gpp_bad_rounded, title: 'Compte suspendu', text: 'L’accès aux demandes est fermé. Écrivez au support pour la suite.', action: 'Contacter le support')),
          _Link('Session expirée', const _StateBlock(icon: Icons.lock_clock_rounded, title: 'Session expirée', text: 'Reconnectez-vous pour retrouver vos demandes.', action: 'Se reconnecter')),
          _Link('Paiement échoué', const _StateBlock(icon: Icons.error_outline_rounded, title: 'Paiement échoué', text: 'Aucun montant n’a été confirmé. Vous pouvez choisir un autre moyen.', action: 'Réessayer')),
        ],
      ),
    );
  }
}

class PrivacyPage extends StatelessWidget {
  const PrivacyPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: cream,
      appBar: AppBar(title: const Text('Sécurité')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: const [
          _InfoCard(title: 'Mot de passe', text: 'Le changement passe par le code reçu par e-mail.'),
          _InfoCard(title: 'Sessions', text: 'La déconnexion ferme la session de cet appareil.'),
          _InfoCard(title: 'Données', text: 'Vous pouvez écrire au support pour une demande d’accès ou de suppression.'),
        ],
      ),
    );
  }
}

class HelpPage extends StatelessWidget {
  const HelpPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: cream,
      appBar: AppBar(title: const Text('Aide')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const _InfoCard(title: 'Comment ça marche ?', text: 'Choisissez un métier, décrivez le besoin, comparez les devis, suivez la mission.'),
          const _InfoCard(title: 'Le paiement', text: 'Il se fait entre vous et l’ouvrier. Jefamora ne prend pas de commission.'),
          const TextField(minLines: 3, maxLines: 5, decoration: InputDecoration(labelText: 'Décrire un problème')),
          const SizedBox(height: 12),
          FilledButton(onPressed: () => Navigator.pop(context), child: const Text('Envoyer au support')),
        ],
      ),
    );
  }
}

class AboutPage extends StatelessWidget {
  const AboutPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const LegalPage(title: 'À propos', text: 'Jefamora relie les clients et les ouvriers au Sénégal. Version mobile 1.0.');
  }
}

class LegalPage extends StatelessWidget {
  const LegalPage({super.key, required this.title, required this.text});

  final String title;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: cream,
      appBar: AppBar(title: Text(title)),
      body: Padding(padding: const EdgeInsets.all(20), child: Text(text, style: const TextStyle(height: 1.45, fontSize: 16))),
    );
  }
}

class WorkerCard extends StatelessWidget {
  const WorkerCard({super.key, required this.person, required this.onTap});

  final ClientWorker person;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: ListTile(
        onTap: onTap,
        leading: CircleAvatar(backgroundColor: navy, child: Text(person.name.characters.first, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w800))),
        title: Text(person.name, style: const TextStyle(fontWeight: FontWeight.w800)),
        subtitle: Text('${person.trade} · ${person.place}'),
        trailing: Text(person.rating, style: const TextStyle(color: navy, fontWeight: FontWeight.w800)),
      ),
    );
  }
}

class _CategoryChip extends StatelessWidget {
  const _CategoryChip({required this.name, required this.onTap});

  final String name;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(18),
      child: InkWell(
        borderRadius: BorderRadius.circular(18),
        onTap: onTap,
        child: SizedBox(
          width: 108,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(TradeLook.icon(name), color: navy),
              const SizedBox(height: 6),
              Text(name, textAlign: TextAlign.center, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 12, color: navy)),
            ],
          ),
        ),
      ),
    );
  }
}

class _SectionTitle extends StatelessWidget {
  const _SectionTitle(this.text);

  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 8),
      child: Text(text, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: navy)),
    );
  }
}

class _InfoCard extends StatelessWidget {
  const _InfoCard({required this.title, required this.text});

  final String title;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: const TextStyle(fontWeight: FontWeight.w800, color: navy)),
            const SizedBox(height: 4),
            Text(text, style: const TextStyle(color: muted, height: 1.35)),
          ],
        ),
      ),
    );
  }
}

class _Link extends StatelessWidget {
  const _Link(this.label, this.page);

  final String label;
  final Widget page;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        title: Text(label, style: const TextStyle(fontWeight: FontWeight.w700)),
        trailing: const Icon(Icons.chevron_right),
        onTap: () => _push(context, page),
      ),
    );
  }
}

class _Pin extends StatelessWidget {
  const _Pin({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const Icon(Icons.location_on_rounded, color: navy, size: 32),
        Text(label, style: const TextStyle(fontWeight: FontWeight.w800, color: navy, fontSize: 12)),
      ],
    );
  }
}

class _StateBlock extends StatelessWidget {
  const _StateBlock({required this.icon, required this.title, required this.text, required this.action});

  final IconData icon;
  final String title;
  final String text;
  final String action;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(28),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: navy, size: 56),
          const SizedBox(height: 12),
          Text(title, textAlign: TextAlign.center, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w800, color: navy)),
          const SizedBox(height: 8),
          Text(text, textAlign: TextAlign.center, style: const TextStyle(color: muted, height: 1.4)),
          const SizedBox(height: 16),
          FilledButton(onPressed: () => Navigator.of(context).maybePop(), child: Text(action)),
        ],
      ),
    );
  }
}

class ClientWorker {
  const ClientWorker(this.name, this.trade, this.rating, this.place);
  final String name;
  final String trade;
  final String rating;
  final String place;
}

const _people = [
  ClientWorker('Awa Ndiaye', 'Électricité', '4,8', 'Dakar'),
  ClientWorker('Moussa Diop', 'Plomberie', '4,6', 'Pikine'),
  ClientWorker('Fatou Sarr', 'Peinture', '4,9', 'Guédiawaye'),
];

const _sampleTrades = ['Électricité', 'Plomberie', 'Menuiserie', 'Maçonnerie', 'Peinture', 'Climatisation'];

ClientWorker _fromPro(ProCard card) => ClientWorker(card.name, card.verified ? 'Profil vérifié' : 'Professionnel', card.rating, 'Dakar');

void _push(BuildContext context, Widget page) {
  Navigator.of(context).push(MaterialPageRoute(builder: (_) => page));
}
