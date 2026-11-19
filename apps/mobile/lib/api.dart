import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

const _storageKey = 'jefamora.session';

String apiBase() {
  const fromEnv = String.fromEnvironment('API_BASE');
  if (fromEnv.isNotEmpty) return fromEnv;
  if (!kIsWeb && defaultTargetPlatform == TargetPlatform.android) {
    return 'http://10.0.2.2:8000';
  }
  return 'http://127.0.0.1:8000';
}

class ApiException implements Exception {
  ApiException(this.message, {this.code = 'error', this.status = 0});

  final String message;
  final String code;
  final int status;

  @override
  String toString() => message;
}

class Profile {
  Profile({
    required this.id,
    required this.email,
    required this.firstName,
    required this.lastName,
    required this.role,
    required this.isVerified,
    this.phone,
    this.businessName,
    this.professionalProfileId,
    this.badgeVerified,
    this.verificationStatus,
    this.companyName,
  });

  final String id;
  final String email;
  final String firstName;
  final String lastName;
  final String role;
  final bool isVerified;
  final String? phone;
  final String? businessName;
  final String? professionalProfileId;
  final bool? badgeVerified;
  final String? verificationStatus;
  final String? companyName;

  bool get isProfessional => role == 'professional';

  String get displayName {
    final name = '$firstName $lastName'.trim();
    if (name.isNotEmpty) return name;
    return businessName ?? email;
  }

  factory Profile.fromJson(Map<String, dynamic> json) {
    return Profile(
      id: '${json['id']}',
      email: '${json['email'] ?? ''}',
      firstName: '${json['first_name'] ?? ''}',
      lastName: '${json['last_name'] ?? ''}',
      role: '${json['role'] ?? 'client'}',
      isVerified: json['is_verified'] == true,
      phone: json['phone'] as String?,
      businessName: json['business_name'] as String?,
      professionalProfileId: json['professional_profile_id'] as String?,
      badgeVerified: json['badge_verified'] as bool?,
      verificationStatus: json['verification_status'] as String?,
      companyName: json['company_name'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'email': email,
        'first_name': firstName,
        'last_name': lastName,
        'role': role,
        'is_verified': isVerified,
        'phone': phone,
        'business_name': businessName,
        'professional_profile_id': professionalProfileId,
        'badge_verified': badgeVerified,
        'verification_status': verificationStatus,
        'company_name': companyName,
      };
}

class SessionStore extends ChangeNotifier {
  Profile? profile;
  String? access;
  String? refresh;

  Future<void> load() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_storageKey);
    if (raw == null) return;
    final data = jsonDecode(raw);
    if (data is! Map) return;
    access = data['access'] as String?;
    refresh = data['refresh'] as String?;
    final body = data['profile'];
    if (access != null && body is Map) {
      profile = Profile.fromJson(Map<String, dynamic>.from(body));
    }
  }

  Future<void> apply(Map<String, dynamic> body) async {
    access = body['access'] as String?;
    refresh = body['refresh'] as String?;
    final raw = body['profile'];
    if (raw is Map) {
      profile = Profile.fromJson(Map<String, dynamic>.from(raw));
    }
    await _persist();
    notifyListeners();
  }

  Future<void> updateTokens(String nextAccess, String nextRefresh) async {
    access = nextAccess;
    refresh = nextRefresh;
    await _persist();
  }

  Future<void> clear() async {
    profile = null;
    access = null;
    refresh = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_storageKey);
    notifyListeners();
  }

  Future<void> _persist() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(
      _storageKey,
      jsonEncode({'access': access, 'refresh': refresh, 'profile': profile?.toJson()}),
    );
  }
}

class Trade {
  Trade({required this.id, required this.name});
  final String id;
  final String name;
  factory Trade.fromJson(Map<String, dynamic> json) => Trade(id: '${json['id']}', name: '${json['name']}');
}

class Zone {
  Zone({required this.id, required this.region, required this.city, required this.district});
  final String id;
  final String region;
  final String city;
  final String district;
  String get label => district.isEmpty ? '$city, $region' : '$district, $city';
  factory Zone.fromJson(Map<String, dynamic> json) => Zone(
        id: '${json['id']}',
        region: '${json['region'] ?? ''}',
        city: '${json['city'] ?? ''}',
        district: '${json['district'] ?? ''}',
      );
}

class ProCard {
  ProCard({required this.id, required this.name, required this.verified, required this.rating, required this.zoneIds});
  final String id;
  final String name;
  final bool verified;
  final String rating;
  final List<String> zoneIds;
  factory ProCard.fromJson(Map<String, dynamic> json) {
    final zones = json['zones'];
    return ProCard(
      id: '${json['id']}',
      name: '${json['business_name'] ?? 'Professionnel'}',
      verified: json['is_verified'] == true,
      rating: '${json['average_rating'] ?? '0'}',
      zoneIds: zones is List ? zones.map((item) => '${(item as Map)['id']}').toList() : const [],
    );
  }
}

class Recipient {
  Recipient({required this.id, required this.professional, required this.name, required this.status});
  final String id;
  final String professional;
  final String name;
  final String status;
  factory Recipient.fromJson(Map<String, dynamic> json) => Recipient(
        id: '${json['id']}',
        professional: '${json['professional']}',
        name: '${json['professional_name'] ?? ''}',
        status: '${json['status'] ?? ''}',
      );
}

class ServiceRequestItem {
  ServiceRequestItem({
    required this.id,
    required this.title,
    required this.description,
    required this.status,
    required this.urgency,
    required this.zone,
    required this.budget,
    required this.bookingId,
    required this.recipients,
  });

  final String id;
  final String title;
  final String description;
  final String status;
  final String urgency;
  final String zone;
  final String? budget;
  final String? bookingId;
  final List<Recipient> recipients;

  factory ServiceRequestItem.fromJson(Map<String, dynamic> json) {
    final people = json['recipients'];
    return ServiceRequestItem(
      id: '${json['id']}',
      title: '${json['title'] ?? ''}',
      description: '${json['description'] ?? ''}',
      status: '${json['status'] ?? ''}',
      urgency: '${json['urgency'] ?? ''}',
      zone: '${json['zone'] ?? ''}',
      budget: json['budget']?.toString(),
      bookingId: json['booking_id']?.toString(),
      recipients: people is List
          ? people.map((item) => Recipient.fromJson(Map<String, dynamic>.from(item as Map))).toList()
          : const [],
    );
  }
}

class QuoteItem {
  QuoteItem({required this.id, required this.amount, required this.status, required this.delay, required this.conditions});
  final String id;
  final String amount;
  final String status;
  final String delay;
  final String conditions;
  factory QuoteItem.fromJson(Map<String, dynamic> json) => QuoteItem(
        id: '${json['id']}',
        amount: '${json['total_amount'] ?? ''}',
        status: '${json['status'] ?? ''}',
        delay: '${json['estimated_delay'] ?? ''}',
        conditions: '${json['conditions'] ?? ''}',
      );
}

class BookingItem {
  BookingItem({required this.id, required this.status, required this.professionalName, required this.scheduledAt});
  final String id;
  final String status;
  final String professionalName;
  final String? scheduledAt;
  factory BookingItem.fromJson(Map<String, dynamic> json) => BookingItem(
        id: '${json['id']}',
        status: '${json['status'] ?? ''}',
        professionalName: '${json['professional_name'] ?? ''}',
        scheduledAt: json['scheduled_at']?.toString(),
      );
}

String requestLabel(String status) => const {
      'draft': 'Brouillon',
      'open': 'Ouverte',
      'quoted': 'Devis reçu',
      'booked': 'Réservée',
      'cancelled': 'Annulée',
      'closed': 'Clôturée',
    }[status] ??
    status;

String urgencyLabel(String value) => const {
      'low': 'Faible',
      'normal': 'Normale',
      'urgent': 'Urgente',
    }[value] ??
    value;

String quoteLabel(String status) => const {
      'draft': 'Brouillon',
      'sent': 'Envoyé',
      'accepted': 'Accepté',
      'refused': 'Refusé',
      'expired': 'Expiré',
    }[status] ??
    status;

String bookingLabel(String status) => const {
      'confirmed': 'Confirmée',
      'in_progress': 'En cours',
      'completed_by_professional': 'Fin déclarée',
      'confirmed_by_client': 'Terminée',
      'cancelled': 'Annulée',
      'disputed': 'En litige',
    }[status] ??
    status;

class ApiClient {
  ApiClient(this.session, {http.Client? httpClient, String? base})
      : _http = httpClient ?? http.Client(),
        _base = base ?? apiBase();

  final SessionStore session;
  final http.Client _http;
  final String _base;

  Future<Map<String, dynamic>> login(String email, String password) {
    return _object('POST', '/api/v1/users/login/', body: {'email': email, 'password': password}, auth: false);
  }

  Future<String> register(Map<String, dynamic> payload) async {
    final data = await _object('POST', '/api/v1/users/register/', body: payload, auth: false);
    return '${data['message'] ?? 'Un code a été envoyé.'}';
  }

  Future<Map<String, dynamic>> verify(String email, String code) {
    return _object('POST', '/api/v1/users/verify-email/', body: {'email': email, 'code': code}, auth: false);
  }

  Future<void> requestReset(String email) {
    return _send('POST', '/api/v1/users/password-reset/', body: {'email': email}, auth: false);
  }

  Future<void> confirmReset({required String email, required String code, required String password}) {
    return _send(
      'POST',
      '/api/v1/users/password-reset/confirm/',
      body: {'email': email, 'code': code, 'password': password},
      auth: false,
    );
  }

  Future<void> logout() async {
    final refresh = session.refresh;
    if (refresh != null) {
      try {
        await _send('POST', '/api/v1/users/logout/', body: {'refresh': refresh}, auth: false);
      } catch (_) {}
    }
    await session.clear();
  }

  Future<List<Trade>> trades() async {
    final data = await _send('GET', '/api/v1/catalog/trades/', auth: false);
    return _page(data, Trade.fromJson);
  }

  Future<List<Zone>> zones() async {
    final data = await _send('GET', '/api/v1/catalog/zones/', auth: false);
    return _page(data, Zone.fromJson);
  }

  Future<List<ProCard>> professionals({String? trade, String? zone}) async {
    final query = <String, String>{
      'trade': ?trade,
      'zone': ?zone,
    };
    final data = await _send('GET', '/api/v1/professionals/', query: query);
    return _page(data, ProCard.fromJson);
  }

  Future<List<ServiceRequestItem>> requests() async {
    final data = await _send('GET', '/api/v1/service_requests/');
    return _page(data, ServiceRequestItem.fromJson);
  }

  Future<ServiceRequestItem> request(String id) async {
    final data = await _object('GET', '/api/v1/service_requests/$id/');
    return ServiceRequestItem.fromJson(data);
  }

  Future<ServiceRequestItem> createRequest({
    required String zone,
    required String title,
    required String description,
    required List<String> professionalIds,
    required String urgency,
    String? budget,
  }) async {
    final data = await _object('POST', '/api/v1/service_requests/', body: {
      'zone': zone,
      'title': title,
      'description': description,
      'professional_ids': professionalIds,
      'urgency': urgency,
      if (budget != null && budget.isNotEmpty) 'budget': budget,
    });
    return ServiceRequestItem.fromJson(data);
  }

  Future<void> cancelRequest(String id) {
    return _send('POST', '/api/v1/service_requests/$id/cancel/');
  }

  Future<void> declineRequest(String id, String reason) {
    return _send('POST', '/api/v1/service_requests/$id/decline/', body: {'reason': reason});
  }

  Future<List<QuoteItem>> quotes(String requestId) async {
    final data = await _send('GET', '/api/v1/service_requests/$requestId/quotes/');
    return _page(data, QuoteItem.fromJson);
  }

  Future<void> sendQuote({required String requestId, required String amount, required String delay}) {
    return _send('POST', '/api/v1/quotes/', body: {
      'service_request': requestId,
      'total_amount': amount,
      'estimated_delay': delay,
    });
  }

  Future<void> acceptQuote(String id) => _send('POST', '/api/v1/quotes/$id/accept/');

  Future<void> rejectQuote(String id) => _send('POST', '/api/v1/quotes/$id/reject/');

  Future<List<BookingItem>> bookings() async {
    final data = await _send('GET', '/api/v1/bookings/');
    return _page(data, BookingItem.fromJson);
  }

  Future<void> startBooking(String id) => _send('POST', '/api/v1/bookings/$id/start/');

  Future<void> finishBooking(String id) => _send('POST', '/api/v1/bookings/$id/request-completion/');

  Future<void> confirmBooking(String id) => _send('POST', '/api/v1/bookings/$id/confirm-completion/');

  Future<Map<String, dynamic>> _object(
    String method,
    String path, {
    Map<String, dynamic>? body,
    bool auth = true,
  }) async {
    final data = await _send(method, path, body: body, auth: auth);
    if (data is Map) return Map<String, dynamic>.from(data);
    return {};
  }

  Future<dynamic> _send(
    String method,
    String path, {
    Map<String, dynamic>? body,
    Map<String, String>? query,
    bool auth = true,
    bool retry = true,
  }) async {
    final uri = Uri.parse('$_base$path').replace(queryParameters: query == null || query.isEmpty ? null : query);
    final headers = {'Accept': 'application/json', 'Content-Type': 'application/json'};
    if (auth && session.access != null) {
      headers['Authorization'] = 'Bearer ${session.access}';
    }
    final request = http.Request(method, uri)..headers.addAll(headers);
    if (body != null) request.body = jsonEncode(body);
    final response = await http.Response.fromStream(await _http.send(request));
    if (response.statusCode == 401 && auth && retry && session.refresh != null) {
      final rotated = await _refresh();
      if (rotated) {
        return _send(method, path, body: body, query: query, auth: auth, retry: false);
      }
    }
    if (response.statusCode == 204 || response.body.isEmpty) {
      if (response.statusCode >= 400) {
        throw ApiException('La requête a échoué.', status: response.statusCode);
      }
      return null;
    }
    final decoded = jsonDecode(response.body);
    if (response.statusCode >= 400) {
      final map = decoded is Map ? Map<String, dynamic>.from(decoded) : <String, dynamic>{};
      throw ApiException(
        '${map['message'] ?? 'La requête a échoué.'}',
        code: '${map['code'] ?? 'error'}',
        status: response.statusCode,
      );
    }
    return decoded;
  }

  Future<bool> _refresh() async {
    try {
      final data = await _object('POST', '/api/v1/users/refresh/', body: {'refresh': session.refresh}, auth: false);
      final access = data['access'] as String?;
      final refresh = data['refresh'] as String?;
      if (access == null || refresh == null) return false;
      await session.updateTokens(access, refresh);
      return true;
    } catch (_) {
      await session.clear();
      return false;
    }
  }

  List<T> _page<T>(dynamic data, T Function(Map<String, dynamic>) map) {
    final raw = data is Map && data['results'] is List ? data['results'] as List : data;
    if (raw is! List) return [];
    return raw.map((item) => map(Map<String, dynamic>.from(item as Map))).toList();
  }
}
