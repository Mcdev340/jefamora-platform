import 'package:material_ui/material_ui.dart';

import 'api.dart';
import 'client_space.dart';
import 'scope.dart';
import 'theme.dart';
import 'trade_look.dart';
import 'widgets.dart';

class ClientShell extends StatelessWidget {
  const ClientShell({super.key});

  @override
  Widget build(BuildContext context) => const ClientSpace();
}

class ClientHome extends StatefulWidget {
  const ClientHome({super.key});

  @override
  State<ClientHome> createState() => _ClientHomeState();
}

class _ClientHomeState extends State<ClientHome> {
  String _query = '';

  @override
  Widget build(BuildContext context) {
    final api = AppScope.of(context).api;
    final profile = AppScope.of(context).session.profile;
    final first = profile?.firstName.trim() ?? '';
    return Scaffold(
      backgroundColor: cream,
      body: RemoteBody<List<Trade>>(
        load: api.trades,
        builder: (trades, _) {
          final wanted = _query.trim().toLowerCase();
          final shown = trades.where((trade) {
            if (wanted.isEmpty) return true;
            return trade.name.toLowerCase().contains(wanted) || TradeLook.label(trade.name).toLowerCase().contains(wanted);
          }).toList();
          return CustomScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            slivers: [
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(20, 8, 20, 0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const SafeArea(bottom: false, child: BrandLockup()),
                      const SizedBox(height: 18),
                      Text(
                        first.isEmpty ? 'Bonjour' : 'Bonjour, $first',
                        style: const TextStyle(fontSize: 28, height: 1.05, fontWeight: FontWeight.w800, color: navy),
                      ),
                      const SizedBox(height: 6),
                      const Text(
                        'Choisissez un métier. La demande part vers des ouvriers vérifiés de votre zone.',
                        style: TextStyle(color: muted, height: 1.35),
                      ),
                      const SizedBox(height: 14),
                      TextField(
                        onChanged: (value) => setState(() => _query = value),
                        decoration: const InputDecoration(
                          hintText: 'Quel métier recherchez-vous ?',
                          prefixIcon: Icon(Icons.search_rounded, color: navy),
                        ),
                      ),
                      const SizedBox(height: 12),
                      Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        children: [
                          for (final name in const ['Électricité', 'Plomberie', 'Menuiserie', 'Maçonnerie'])
                            ActionChip(
                              label: Text(TradeLook.label(name)),
                              backgroundColor: Colors.white,
                              side: BorderSide.none,
                              labelStyle: const TextStyle(color: navy, fontWeight: FontWeight.w700),
                              onPressed: () {
                                final match = trades.where((trade) => trade.name == name);
                                if (match.isEmpty) {
                                  setState(() => _query = TradeLook.label(name));
                                  return;
                                }
                                Navigator.of(context).push(MaterialPageRoute(builder: (_) => NewRequestPage(trade: match.first)));
                              },
                            ),
                        ],
                      ),
                      const SizedBox(height: 18),
                    ],
                  ),
                ),
              ),
              if (trades.isEmpty)
                const SliverToBoxAdapter(child: EmptyHint('Les métiers s’affichent dès que le catalogue répond.')),
              if (trades.isNotEmpty && shown.isEmpty)
                const SliverToBoxAdapter(child: EmptyHint('Aucun métier ne correspond à cette recherche.')),
              if (shown.isNotEmpty)
                SliverPadding(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  sliver: SliverGrid(
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 2,
                      mainAxisSpacing: 10,
                      crossAxisSpacing: 10,
                      childAspectRatio: 1.25,
                    ),
                    delegate: SliverChildBuilderDelegate(
                      (context, index) {
                        final trade = shown[index];
                        final color = TradeLook.color(trade.name);
                        return Material(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(20),
                          child: InkWell(
                            borderRadius: BorderRadius.circular(20),
                            onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => NewRequestPage(trade: trade))),
                            child: Padding(
                              padding: const EdgeInsets.all(14),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Container(
                                    width: 42,
                                    height: 42,
                                    decoration: BoxDecoration(
                                      color: color.withValues(alpha: 0.14),
                                      borderRadius: BorderRadius.circular(14),
                                    ),
                                    child: Icon(TradeLook.icon(trade.name), color: color),
                                  ),
                                  const Spacer(),
                                  Text(TradeLook.label(trade.name), style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16, color: navy)),
                                  Text(trade.name, style: const TextStyle(color: muted, fontSize: 12)),
                                ],
                              ),
                            ),
                          ),
                        );
                      },
                      childCount: shown.length,
                    ),
                  ),
                ),
              const SliverToBoxAdapter(child: SizedBox(height: 22)),
              const SliverToBoxAdapter(
                child: Padding(
                  padding: EdgeInsets.symmetric(horizontal: 20),
                  child: Text('En trois gestes', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: navy)),
                ),
              ),
              const SliverToBoxAdapter(
                child: Padding(
                  padding: EdgeInsets.fromLTRB(20, 10, 20, 24),
                  child: Column(
                    children: [
                      _HomeStep(number: '01', title: 'Décrivez', text: 'Le métier, la zone et l’urgence.'),
                      _HomeStep(number: '02', title: 'Comparez', text: 'Plusieurs réponses, un seul devis retenu.'),
                      _HomeStep(number: '03', title: 'Réalisez', text: 'Messages, fin des travaux, puis un avis. 0 FCFA de commission.'),
                    ],
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _HomeStep extends StatelessWidget {
  const _HomeStep({required this.number, required this.title, required this.text});

  final String number;
  final String title;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16)),
      child: Row(
        children: [
          Text(number, style: const TextStyle(color: orange, fontWeight: FontWeight.w800, fontSize: 16)),
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

class NewRequestPage extends StatefulWidget {
  const NewRequestPage({super.key, required this.trade});

  final Trade trade;

  @override
  State<NewRequestPage> createState() => _NewRequestPageState();
}

class _NewRequestPageState extends State<NewRequestPage> {
  final _title = TextEditingController();
  final _description = TextEditingController();
  final _budget = TextEditingController();
  List<Zone> _zones = [];
  List<ProCard> _pros = [];
  String? _zoneId;
  String _urgency = 'normal';
  final _selected = <String>{};
  bool _loading = true;
  bool _busy = false;
  bool _started = false;
  String? _error;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_started) return;
    _started = true;
    _load();
  }

  @override
  void dispose() {
    _title.dispose();
    _description.dispose();
    _budget.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    final api = AppScope.of(context).api;
    try {
      final results = await Future.wait([api.zones(), api.professionals(trade: widget.trade.id)]);
      if (!mounted) return;
      setState(() {
        _zones = results[0] as List<Zone>;
        _pros = results[1] as List<ProCard>;
        _loading = false;
      });
    } on ApiException catch (error) {
      if (!mounted) return;
      setState(() {
        _error = error.message;
        _loading = false;
      });
    }
  }

  List<ProCard> get _visible {
    if (_zoneId == null) return _pros;
    return _pros.where((item) => item.zoneIds.contains(_zoneId)).toList();
  }

  Future<void> _submit() async {
    if (_zoneId == null || _title.text.trim().isEmpty || _description.text.trim().isEmpty || _selected.isEmpty) {
      setState(() => _error = 'Indiquez la zone, le besoin et au moins un ouvrier.');
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      await AppScope.of(context).api.createRequest(
            zone: _zoneId!,
            title: _title.text.trim(),
            description: _description.text.trim(),
            professionalIds: _selected.toList(),
            urgency: _urgency,
            budget: _budget.text.trim(),
          );
      if (!mounted) return;
      Navigator.of(context).pop();
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Demande envoyée')));
    } on ApiException catch (error) {
      setState(() => _error = error.message);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final visible = _visible;
    return Scaffold(
      appBar: AppBar(title: Text(widget.trade.name)),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: orange))
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                DropdownButtonFormField<String>(
                  initialValue: _zoneId,
                  decoration: const InputDecoration(labelText: 'Zone'),
                  items: _zones.map((zone) => DropdownMenuItem(value: zone.id, child: Text(zone.label))).toList(),
                  onChanged: (value) => setState(() {
                    _zoneId = value;
                    _selected.removeWhere((id) => !_visible.any((pro) => pro.id == id));
                  }),
                ),
                const SizedBox(height: 12),
                TextField(controller: _title, decoration: const InputDecoration(labelText: 'Titre du besoin')),
                const SizedBox(height: 12),
                TextField(
                  controller: _description,
                  minLines: 3,
                  maxLines: 5,
                  decoration: const InputDecoration(labelText: 'Description'),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _budget,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Budget, en FCFA, facultatif'),
                ),
                const SizedBox(height: 12),
                SegmentedButton<String>(
                  segments: const [
                    ButtonSegment(value: 'low', label: Text('Faible')),
                    ButtonSegment(value: 'normal', label: Text('Normale')),
                    ButtonSegment(value: 'urgent', label: Text('Urgente')),
                  ],
                  selected: {_urgency},
                  onSelectionChanged: (value) => setState(() => _urgency = value.first),
                ),
                const SizedBox(height: 18),
                const Text('Ouvriers vérifiés', style: TextStyle(fontWeight: FontWeight.w800, color: navy)),
                if (visible.isEmpty)
                  const EmptyHint('Aucun ouvrier vérifié pour ce métier dans cette zone.')
                else
                  ...visible.map(
                    (pro) => CheckboxListTile(
                      contentPadding: EdgeInsets.zero,
                      value: _selected.contains(pro.id),
                      activeColor: orange,
                      title: Text(pro.name),
                      subtitle: Text(pro.verified ? 'Profil vérifié' : 'Profil'),
                      onChanged: (checked) => setState(() {
                        if (checked == true) {
                          _selected.add(pro.id);
                        } else {
                          _selected.remove(pro.id);
                        }
                      }),
                    ),
                  ),
                if (_error != null) Text(_error!, style: const TextStyle(color: Color(0xFFBE123C))),
                const SizedBox(height: 8),
                FilledButton(onPressed: _busy ? null : _submit, child: Text(_busy ? 'Envoi…' : 'Envoyer la demande')),
              ],
            ),
    );
  }
}

class RequestsPage extends StatelessWidget {
  const RequestsPage({super.key, required this.worker});

  final bool worker;

  @override
  Widget build(BuildContext context) {
    final api = AppScope.of(context).api;
    return Scaffold(
      appBar: AppBar(title: Text(worker ? 'Demandes reçues' : 'Mes demandes')),
      body: RemoteBody<List<ServiceRequestItem>>(
        load: api.requests,
        builder: (items, _) {
          if (items.isEmpty) {
            return ListView(
              children: [EmptyHint(worker ? 'Aucune demande ne vous est adressée.' : 'Vous n’avez pas encore de demande.')],
            );
          }
          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: items.length,
            separatorBuilder: (_, _) => const SizedBox(height: 10),
            itemBuilder: (context, index) {
              final item = items[index];
              return Card(
                child: ListTile(
                  title: Text(item.title, style: const TextStyle(fontWeight: FontWeight.w700)),
                  subtitle: Text('${requestLabel(item.status)} · ${urgencyLabel(item.urgency)}'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => worker ? WorkerRequestPage(id: item.id) : RequestDetailPage(id: item.id),
                    ),
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

class RequestDetailPage extends StatelessWidget {
  const RequestDetailPage({super.key, required this.id});

  final String id;

  @override
  Widget build(BuildContext context) {
    final api = AppScope.of(context).api;
    return Scaffold(
      appBar: AppBar(title: const Text('Demande')),
      body: RemoteBody<_RequestBundle>(
        load: () async => _RequestBundle(await api.request(id), await api.quotes(id)),
        builder: (bundle, reload) {
          final item = bundle.request;
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Text(item.title, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: navy)),
              const SizedBox(height: 8),
              StatusChip(requestLabel(item.status)),
              const SizedBox(height: 12),
              Text(item.description),
              const SizedBox(height: 18),
              const Text('Devis', style: TextStyle(fontWeight: FontWeight.w800, color: navy)),
              if (bundle.quotes.isEmpty)
                const EmptyHint('Aucun devis pour le moment.')
              else
                ...bundle.quotes.map((quote) => Card(
                      child: Padding(
                        padding: const EdgeInsets.all(14),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('${quote.amount} FCFA', style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 18)),
                            const SizedBox(height: 6),
                            StatusChip(quoteLabel(quote.status)),
                            if (quote.delay.isNotEmpty) Text(quote.delay),
                            if (quote.status == 'sent') ...[
                              const SizedBox(height: 10),
                              FilledButton(
                                onPressed: () => runAction(context, () => api.acceptQuote(quote.id), done: 'Devis accepté. La mission est créée.')
                                    .then((_) => reload()),
                                child: const Text('Accepter'),
                              ),
                              const SizedBox(height: 8),
                              OutlinedButton(
                                onPressed: () => runAction(context, () => api.rejectQuote(quote.id), done: 'Devis refusé').then((_) => reload()),
                                child: const Text('Refuser'),
                              ),
                            ],
                          ],
                        ),
                      ),
                    )),
              if (item.status == 'open' || item.status == 'quoted')
                OutlinedButton(
                  onPressed: () => runAction(context, () => api.cancelRequest(item.id), done: 'Demande annulée').then((_) {
                    if (context.mounted) Navigator.of(context).pop();
                  }),
                  child: const Text('Annuler la demande'),
                ),
            ],
          );
        },
      ),
    );
  }
}

class _RequestBundle {
  _RequestBundle(this.request, this.quotes);
  final ServiceRequestItem request;
  final List<QuoteItem> quotes;
}

class WorkerRequestPage extends StatefulWidget {
  const WorkerRequestPage({super.key, required this.id});

  final String id;

  @override
  State<WorkerRequestPage> createState() => _WorkerRequestPageState();
}

class _WorkerRequestPageState extends State<WorkerRequestPage> {
  final _amount = TextEditingController();
  final _delay = TextEditingController();
  final _reason = TextEditingController();
  Future<ServiceRequestItem>? _future;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _future ??= AppScope.of(context).api.request(widget.id);
  }

  @override
  void dispose() {
    _amount.dispose();
    _delay.dispose();
    _reason.dispose();
    super.dispose();
  }

  void _reload() => setState(() => _future = AppScope.of(context).api.request(widget.id));

  @override
  Widget build(BuildContext context) {
    final api = AppScope.of(context).api;
    final profileId = AppScope.of(context).session.profile?.professionalProfileId;
    return Scaffold(
      appBar: AppBar(title: const Text('Demande')),
      body: _future == null
          ? const Center(child: CircularProgressIndicator(color: orange))
          : FutureBuilder<ServiceRequestItem>(
        future: _future!,
        builder: (context, snapshot) {
          if (!snapshot.hasData) {
            if (snapshot.hasError) return Center(child: Text('${snapshot.error}'));
            return const Center(child: CircularProgressIndicator(color: orange));
          }
          final item = snapshot.data!;
          final mine = item.recipients.where((person) => person.professional == profileId).toList();
          final mineStatus = mine.isEmpty ? '' : mine.first.status;
          final closed = item.status == 'booked' || item.status == 'cancelled' || item.status == 'closed';
          final canAnswer = !closed && mineStatus != 'refused' && mineStatus != 'quoted' && mineStatus != 'accepted';
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Text(item.title, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: navy)),
              const SizedBox(height: 8),
              StatusChip(requestLabel(item.status)),
              const SizedBox(height: 12),
              Text(item.description),
              if (canAnswer) ...[
                const SizedBox(height: 18),
                const Text('Votre devis', style: TextStyle(fontWeight: FontWeight.w800, color: navy)),
                const SizedBox(height: 8),
                TextField(controller: _amount, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Montant, FCFA')),
                const SizedBox(height: 12),
                TextField(controller: _delay, decoration: const InputDecoration(labelText: 'Délai estimé')),
                const SizedBox(height: 12),
                FilledButton(
                  onPressed: () => runAction(context, () async {
                    await api.sendQuote(requestId: item.id, amount: _amount.text.trim(), delay: _delay.text.trim());
                  }, done: 'Devis envoyé').then((_) => _reload()),
                  child: const Text('Envoyer le devis'),
                ),
                const SizedBox(height: 18),
                TextField(controller: _reason, decoration: const InputDecoration(labelText: 'Motif de refus, facultatif')),
                const SizedBox(height: 8),
                OutlinedButton(
                  onPressed: () => runAction(context, () => api.declineRequest(item.id, _reason.text.trim()), done: 'Demande refusée')
                      .then((_) => _reload()),
                  child: const Text('Refuser la demande'),
                ),
              ],
            ],
          );
        },
      ),
    );
  }
}
