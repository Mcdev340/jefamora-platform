import 'package:material_ui/material_ui.dart';

import 'api.dart';
import 'scope.dart';
import 'theme.dart';
import 'widgets.dart';

class WelcomePage extends StatelessWidget {
  const WelcomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return const StartPage();
  }
}

class StartPage extends StatelessWidget {
  const StartPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: navy,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(24, 24, 24, 28),
          child: Column(
            children: [
              const Spacer(),
              const BrandLockup(light: true),
              const SizedBox(height: 28),
              const Text(
                'Le bon professionnel, près de chez vous.',
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.white, fontSize: 32, height: 1.08, fontWeight: FontWeight.w800),
              ),
              const SizedBox(height: 12),
              const Text(
                'Clients et ouvriers au Sénégal. Une demande, des devis, une seule mission.',
                textAlign: TextAlign.center,
                style: TextStyle(color: Color(0xFFFFEDD5), height: 1.4),
              ),
              const Spacer(),
              FilledButton(
                style: FilledButton.styleFrom(backgroundColor: orange, foregroundColor: navy),
                onPressed: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const OnboardingPage())),
                child: const Text('Commencer'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class OnboardingPage extends StatefulWidget {
  const OnboardingPage({super.key});

  @override
  State<OnboardingPage> createState() => _OnboardingPageState();
}

class _OnboardingPageState extends State<OnboardingPage> {
  final _controller = PageController();
  int _page = 0;

  static const _slides = [
    (Icons.verified_rounded, 'Des profils vérifiés', 'Le badge Jefamora est accordé avant qu’un ouvrier apparaisse dans la recherche.'),
    (Icons.receipt_long_rounded, 'Plusieurs devis, un seul choix', 'Vous décrivez le besoin, vous comparez, vous n’en retenez qu’un.'),
    (Icons.place_rounded, 'Près de chez vous', 'La recherche suit le métier et l’adresse où la prestation doit avoir lieu.'),
  ];

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _next() {
    if (_page == _slides.length - 1) {
      Navigator.of(context).push(MaterialPageRoute(builder: (_) => const RolePage()));
      return;
    }
    _controller.nextPage(duration: const Duration(milliseconds: 280), curve: Curves.easeOut);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: cream,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(24, 12, 24, 24),
          child: Column(
            children: [
              Align(
                alignment: Alignment.centerRight,
                child: TextButton(
                  onPressed: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const RolePage())),
                  child: const Text('Passer'),
                ),
              ),
              Expanded(
                child: PageView.builder(
                  controller: _controller,
                  itemCount: _slides.length,
                  onPageChanged: (value) => setState(() => _page = value),
                  itemBuilder: (_, index) {
                    final item = _slides[index];
                    return Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          width: 120,
                          height: 120,
                          decoration: const BoxDecoration(color: navy, shape: BoxShape.circle),
                          child: Icon(item.$1, color: orange, size: 56),
                        ),
                        const SizedBox(height: 28),
                        Text(item.$2, textAlign: TextAlign.center, style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w800, color: navy)),
                        const SizedBox(height: 12),
                        Text(item.$3, textAlign: TextAlign.center, style: const TextStyle(color: muted, height: 1.4, fontSize: 16)),
                      ],
                    );
                  },
                ),
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  for (var i = 0; i < _slides.length; i++)
                    Container(
                      width: i == _page ? 22 : 8,
                      height: 8,
                      margin: const EdgeInsets.symmetric(horizontal: 4),
                      decoration: BoxDecoration(color: i == _page ? orange : navy.withValues(alpha: 0.2), borderRadius: BorderRadius.circular(99)),
                    ),
                ],
              ),
              const SizedBox(height: 18),
              FilledButton(onPressed: _next, child: Text(_page == _slides.length - 1 ? 'C’est parti' : 'Suivant')),
            ],
          ),
        ),
      ),
    );
  }
}

class RolePage extends StatelessWidget {
  const RolePage({super.key});

  @override
  Widget build(BuildContext context) {
    return GateFrame(
      title: 'Qui êtes-vous ?',
      subtitle: 'Le parcours n’est pas le même pour demander un devis et pour le proposer.',
      child: Column(
        children: [
          _RoleButton(
            icon: Icons.home_work_outlined,
            title: 'Client',
            text: 'Je cherche un ouvrier pour un besoin.',
            filled: true,
            onTap: () => _open(context, 'client'),
          ),
          const SizedBox(height: 12),
          _RoleButton(
            icon: Icons.handyman_outlined,
            title: 'Ouvrier',
            text: 'Je propose mon métier et j’envoie des devis.',
            filled: false,
            onTap: () => _open(context, 'professional'),
          ),
        ],
      ),
    );
  }

  void _open(BuildContext context, String role) {
    Navigator.of(context).push(MaterialPageRoute(builder: (_) => LoginPage(role: role)));
  }
}

class LoginPage extends StatefulWidget {
  const LoginPage({super.key, required this.role});

  final String role;

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _email = TextEditingController();
  final _password = TextEditingController();
  bool _busy = false;
  bool _hidden = true;
  String? _error;

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    setState(() {
      _busy = true;
      _error = null;
    });
    final api = AppScope.of(context).api;
    final session = AppScope.of(context).session;
    try {
      final body = await api.login(_email.text.trim(), _password.text);
      final profile = Profile.fromJson(Map<String, dynamic>.from(body['profile'] as Map));
      if (profile.role != widget.role) {
        setState(() => _error = widget.role == 'client'
            ? 'Ce compte est un compte ouvrier. Revenez choisir Ouvrier.'
            : 'Ce compte est un compte client. Revenez choisir Client.');
        return;
      }
      await session.apply(body);
    } on ApiException catch (error) {
      if (error.code == 'email_unverified' && mounted) {
        Navigator.of(context).push(MaterialPageRoute(builder: (_) => VerifyPage(email: _email.text.trim(), role: widget.role)));
      }
      setState(() => _error = error.message);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return GateFrame(
      role: widget.role,
      title: 'Connexion',
      subtitle: 'Retrouvez vos demandes et vos missions.',
      child: Column(
        children: [
          TextField(
            controller: _email,
            keyboardType: TextInputType.emailAddress,
            decoration: const InputDecoration(labelText: 'E-mail'),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _password,
            obscureText: _hidden,
            decoration: InputDecoration(
              labelText: 'Mot de passe',
              suffixIcon: IconButton(
                onPressed: () => setState(() => _hidden = !_hidden),
                icon: Icon(_hidden ? Icons.visibility_outlined : Icons.visibility_off_outlined),
              ),
            ),
          ),
          Align(
            alignment: Alignment.centerRight,
            child: TextButton(
              onPressed: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => ForgotPage(email: _email.text.trim()))),
              child: const Text('Mot de passe oublié'),
            ),
          ),
          if (_error != null) _ErrorText(_error!),
          const SizedBox(height: 8),
          FilledButton(onPressed: _busy ? null : _submit, child: Text(_busy ? 'Connexion…' : 'Se connecter')),
          TextButton(
            onPressed: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => SignupPage(role: widget.role))),
            child: const Text('Pas encore de compte ? Créer un compte'),
          ),
        ],
      ),
    );
  }
}

class SignupPage extends StatefulWidget {
  const SignupPage({super.key, required this.role});

  final String role;

  @override
  State<SignupPage> createState() => _SignupPageState();
}

class _SignupPageState extends State<SignupPage> {
  final _first = TextEditingController();
  final _last = TextEditingController();
  final _email = TextEditingController();
  final _password = TextEditingController();
  final _confirm = TextEditingController();
  String? _error;

  @override
  void dispose() {
    _first.dispose();
    _last.dispose();
    _email.dispose();
    _password.dispose();
    _confirm.dispose();
    super.dispose();
  }

  void _next() {
    if (_first.text.trim().isEmpty || _last.text.trim().isEmpty || !_email.text.contains('@')) {
      setState(() => _error = 'Indiquez le prénom, le nom et un e-mail valide.');
      return;
    }
    if (_password.text.length < 8) {
      setState(() => _error = 'Le mot de passe doit contenir au moins 8 caractères.');
      return;
    }
    if (_password.text != _confirm.text) {
      setState(() => _error = 'Les deux mots de passe ne correspondent pas.');
      return;
    }
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => SignupDetailsPage(
          role: widget.role,
          firstName: _first.text.trim(),
          lastName: _last.text.trim(),
          email: _email.text.trim(),
          password: _password.text,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return GateFrame(
      role: widget.role,
      step: '1 / 2',
      title: 'Créer un compte',
      subtitle: 'Ces informations servent à vous reconnaître.',
      child: Column(
        children: [
          TextField(controller: _first, textCapitalization: TextCapitalization.words, decoration: const InputDecoration(labelText: 'Prénom')),
          const SizedBox(height: 12),
          TextField(controller: _last, textCapitalization: TextCapitalization.words, decoration: const InputDecoration(labelText: 'Nom')),
          const SizedBox(height: 12),
          TextField(controller: _email, keyboardType: TextInputType.emailAddress, decoration: const InputDecoration(labelText: 'E-mail')),
          const SizedBox(height: 12),
          TextField(controller: _password, obscureText: true, decoration: const InputDecoration(labelText: 'Mot de passe')),
          const SizedBox(height: 12),
          TextField(controller: _confirm, obscureText: true, decoration: const InputDecoration(labelText: 'Confirmer le mot de passe')),
          if (_error != null) ...[const SizedBox(height: 12), _ErrorText(_error!)],
          const SizedBox(height: 16),
          FilledButton(onPressed: _next, child: const Text('Suivant')),
        ],
      ),
    );
  }
}

class SignupDetailsPage extends StatefulWidget {
  const SignupDetailsPage({
    super.key,
    required this.role,
    required this.firstName,
    required this.lastName,
    required this.email,
    required this.password,
  });

  final String role;
  final String firstName;
  final String lastName;
  final String email;
  final String password;

  @override
  State<SignupDetailsPage> createState() => _SignupDetailsPageState();
}

class _SignupDetailsPageState extends State<SignupDetailsPage> {
  final _phone = TextEditingController();
  final _business = TextEditingController();
  List<Zone> _zones = [];
  List<Trade> _trades = [];
  String? _city;
  String? _tradeId;
  bool _terms = false;
  bool _loading = true;
  bool _busy = false;
  bool _started = false;
  String? _error;

  bool get _worker => widget.role == 'professional';

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_started) return;
    _started = true;
    _load();
  }

  @override
  void dispose() {
    _phone.dispose();
    _business.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    final api = AppScope.of(context).api;
    try {
      final zones = await api.zones();
      final trades = _worker ? await api.trades() : <Trade>[];
      if (!mounted) return;
      setState(() {
        _zones = zones;
        _trades = trades;
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

  List<String> get _cities {
    final names = _zones.map((zone) => zone.city).where((city) => city.isNotEmpty).toSet().toList();
    names.sort();
    return names;
  }

  Future<void> _submit() async {
    if (_phone.text.trim().length < 8 || _city == null) {
      setState(() => _error = 'Indiquez un téléphone et une ville.');
      return;
    }
    if (_worker && (_business.text.trim().isEmpty || _tradeId == null)) {
      setState(() => _error = 'Indiquez le nom de l’activité et le métier.');
      return;
    }
    if (!_terms) {
      setState(() => _error = 'Acceptez les conditions pour créer le compte.');
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      await AppScope.of(context).api.register({
        'email': widget.email,
        'password': widget.password,
        'first_name': widget.firstName,
        'last_name': widget.lastName,
        'phone': _phone.text.trim(),
        'role': widget.role,
        'city': _city,
        'accept_terms': true,
        if (_worker) 'business_name': _business.text.trim(),
        if (_worker) 'trade_id': _tradeId,
      });
      if (!mounted) return;
      Navigator.of(context).push(MaterialPageRoute(builder: (_) => VerifyPage(email: widget.email, role: widget.role)));
    } on ApiException catch (error) {
      setState(() => _error = error.message);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final cities = _cities;
    return GateFrame(
      role: widget.role,
      step: '2 / 2',
      title: _worker ? 'Votre activité' : 'Où vous joindre',
      subtitle: _worker ? 'Le métier et la ville servent à recevoir les bonnes demandes.' : 'Le téléphone et la ville restent sur votre compte.',
      child: _loading
          ? const Padding(padding: EdgeInsets.all(24), child: Center(child: CircularProgressIndicator(color: orange)))
          : Column(
              children: [
                TextField(controller: _phone, keyboardType: TextInputType.phone, decoration: const InputDecoration(labelText: 'Téléphone')),
                const SizedBox(height: 12),
                if (_worker) ...[
                  TextField(controller: _business, decoration: const InputDecoration(labelText: 'Nom de l’activité')),
                  const SizedBox(height: 12),
                  if (_trades.isNotEmpty)
                    DropdownButtonFormField<String>(
                      initialValue: _tradeId,
                      decoration: const InputDecoration(labelText: 'Métier'),
                      items: _trades.map((trade) => DropdownMenuItem(value: trade.id, child: Text(trade.name))).toList(),
                      onChanged: (value) => setState(() => _tradeId = value),
                    ),
                  const SizedBox(height: 12),
                ],
                if (cities.isNotEmpty)
                  DropdownButtonFormField<String>(
                    initialValue: _city,
                    decoration: const InputDecoration(labelText: 'Ville'),
                    items: cities.map((city) => DropdownMenuItem(value: city, child: Text(city))).toList(),
                    onChanged: (value) => setState(() => _city = value),
                  ),
                CheckboxListTile(
                  contentPadding: EdgeInsets.zero,
                  value: _terms,
                  activeColor: orange,
                  onChanged: (value) => setState(() => _terms = value ?? false),
                  title: const Text('J’accepte les conditions de Jefamora'),
                  controlAffinity: ListTileControlAffinity.leading,
                ),
                if (cities.isEmpty) const _ErrorText('Les villes s’affichent dès que le référentiel répond.'),
                if (_error != null) _ErrorText(_error!),
                const SizedBox(height: 8),
                FilledButton(onPressed: _busy ? null : _submit, child: Text(_busy ? 'Création…' : 'Créer le compte')),
              ],
            ),
    );
  }
}

class VerifyPage extends StatefulWidget {
  const VerifyPage({super.key, required this.email, required this.role});

  final String email;
  final String role;

  @override
  State<VerifyPage> createState() => _VerifyPageState();
}

class _VerifyPageState extends State<VerifyPage> {
  final _code = TextEditingController();
  bool _busy = false;
  String? _error;

  @override
  void dispose() {
    _code.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final body = await AppScope.of(context).api.verify(widget.email, _code.text.trim());
      final profile = Profile.fromJson(Map<String, dynamic>.from(body['profile'] as Map));
      if (profile.role != widget.role) {
        setState(() => _error = 'Ce code correspond à un autre type de compte.');
        return;
      }
      if (!mounted) return;
      await AppScope.of(context).session.apply(body);
    } on ApiException catch (error) {
      setState(() => _error = error.message);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return GateFrame(
      role: widget.role,
      title: 'Confirmez l’e-mail',
      subtitle: 'Saisissez le code envoyé à ${widget.email}. Ensuite, vous entrez dans votre espace.',
      child: Column(
        children: [
          TextField(controller: _code, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Code')),
          if (_error != null) ...[const SizedBox(height: 12), _ErrorText(_error!)],
          const SizedBox(height: 16),
          FilledButton(onPressed: _busy ? null : _submit, child: Text(_busy ? 'Vérification…' : 'Entrer')),
        ],
      ),
    );
  }
}

class ForgotPage extends StatefulWidget {
  const ForgotPage({super.key, this.email = ''});

  final String email;

  @override
  State<ForgotPage> createState() => _ForgotPageState();
}

class _ForgotPageState extends State<ForgotPage> {
  late final TextEditingController _email = TextEditingController(text: widget.email);
  final _code = TextEditingController();
  final _password = TextEditingController();
  bool _sent = false;
  bool _busy = false;
  String? _error;

  @override
  void dispose() {
    _email.dispose();
    _code.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _sendCode() async {
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      await AppScope.of(context).api.requestReset(_email.text.trim());
      setState(() => _sent = true);
    } on ApiException catch (error) {
      setState(() => _error = error.message);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _confirm() async {
    if (_password.text.length < 8) {
      setState(() => _error = 'Le mot de passe doit contenir au moins 8 caractères.');
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      await AppScope.of(context).api.confirmReset(email: _email.text.trim(), code: _code.text.trim(), password: _password.text);
      if (!mounted) return;
      Navigator.of(context).pop();
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Mot de passe mis à jour. Vous pouvez vous connecter.')));
    } on ApiException catch (error) {
      setState(() => _error = error.message);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return GateFrame(
      title: 'Mot de passe oublié',
      subtitle: _sent ? 'Saisissez le code reçu et choisissez un nouveau mot de passe.' : 'Nous envoyons un code à cette adresse si le compte existe.',
      child: Column(
        children: [
          TextField(controller: _email, keyboardType: TextInputType.emailAddress, decoration: const InputDecoration(labelText: 'E-mail')),
          if (_sent) ...[
            const SizedBox(height: 12),
            TextField(controller: _code, decoration: const InputDecoration(labelText: 'Code')),
            const SizedBox(height: 12),
            TextField(controller: _password, obscureText: true, decoration: const InputDecoration(labelText: 'Nouveau mot de passe')),
          ],
          if (_error != null) ...[const SizedBox(height: 12), _ErrorText(_error!)],
          const SizedBox(height: 16),
          FilledButton(
            onPressed: _busy ? null : (_sent ? _confirm : _sendCode),
            child: Text(_busy ? 'Envoi…' : (_sent ? 'Mettre à jour' : 'Recevoir le code')),
          ),
        ],
      ),
    );
  }
}

class GateFrame extends StatelessWidget {
  const GateFrame({super.key, required this.title, required this.child, this.subtitle, this.role, this.step, this.footer});

  final String title;
  final String? subtitle;
  final String? role;
  final String? step;
  final Widget child;
  final Widget? footer;

  @override
  Widget build(BuildContext context) {
    final badge = role == null ? null : (role == 'professional' ? 'Ouvrier' : 'Client');
    return Scaffold(
      backgroundColor: cream,
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 8, 20, 24),
          children: [
            Row(
              children: [
                IconButton(
                  onPressed: () => Navigator.of(context).maybePop(),
                  icon: const Icon(Icons.arrow_back_rounded, color: navy),
                ),
                const Spacer(),
                if (badge != null)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(color: navy, borderRadius: BorderRadius.circular(99)),
                    child: Text(badge, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w800, fontSize: 12)),
                  ),
                if (step != null) ...[
                  const SizedBox(width: 8),
                  Text(step!, style: const TextStyle(color: muted, fontWeight: FontWeight.w700)),
                ],
              ],
            ),
            const SizedBox(height: 8),
            const BrandLockup(),
            const SizedBox(height: 22),
            Text(title, style: const TextStyle(fontSize: 30, height: 1.05, fontWeight: FontWeight.w800, color: navy)),
            if (subtitle != null) ...[
              const SizedBox(height: 8),
              Text(subtitle!, style: const TextStyle(color: muted, height: 1.4)),
            ],
            const SizedBox(height: 20),
            child,
            if (footer != null) ...[const SizedBox(height: 8), Center(child: footer!)],
          ],
        ),
      ),
    );
  }
}

class _RoleButton extends StatelessWidget {
  const _RoleButton({required this.icon, required this.title, required this.text, required this.filled, required this.onTap});

  final IconData icon;
  final String title;
  final String text;
  final bool filled;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final foreground = filled ? Colors.white : navy;
    return Material(
      color: filled ? navy : Colors.white,
      borderRadius: BorderRadius.circular(18),
      child: InkWell(
        borderRadius: BorderRadius.circular(18),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 18),
          child: Row(
            children: [
              Icon(icon, color: filled ? Colors.white : orange),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: TextStyle(color: foreground, fontSize: 18, fontWeight: FontWeight.w800)),
                    const SizedBox(height: 2),
                    Text(text, style: TextStyle(color: filled ? const Color(0xFFFFEDD5) : muted)),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ErrorText extends StatelessWidget {
  const _ErrorText(this.text);

  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(text, style: const TextStyle(color: Color(0xFFBE123C))),
    );
  }
}
