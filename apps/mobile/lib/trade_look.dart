import 'package:material_ui/material_ui.dart';

import 'theme.dart';

class TradeLook {
  static String label(String name) {
    return const {
          'Électricité': 'Électricien',
          'Plomberie': 'Plombier',
          'Menuiserie': 'Menuisier',
          'Maçonnerie': 'Maçon',
          'Peinture': 'Peintre',
          'Carrelage': 'Carreleur',
          'Jardin': 'Jardinier',
          'Serrurerie': 'Serrurier',
        }[name] ??
        name;
  }

  static Color color(String name) {
    return const {
          'Électricité': Color(0xFFD97706),
          'Plomberie': Color(0xFF2563EB),
          'Menuiserie': orange,
          'Maçonnerie': Color(0xFFBE123C),
          'Peinture': Color(0xFF7C3AED),
          'Carrelage': Color(0xFF0369A1),
          'Jardin': Color(0xFF15803D),
          'Serrurerie': Color(0xFF9F1239),
          'Climatisation': Color(0xFF0284C7),
          'Froid': Color(0xFF0369A1),
          'Nettoyage': Color(0xFF15803D),
        }[name] ??
        navy;
  }

  static IconData icon(String name) {
    return const {
          'Électricité': Icons.bolt_rounded,
          'Plomberie': Icons.water_drop_rounded,
          'Menuiserie': Icons.carpenter_rounded,
          'Maçonnerie': Icons.apartment_rounded,
          'Peinture': Icons.format_paint_rounded,
          'Carrelage': Icons.grid_view_rounded,
          'Jardin': Icons.yard_rounded,
          'Serrurerie': Icons.key_rounded,
          'Climatisation': Icons.ac_unit_rounded,
          'Froid': Icons.kitchen_rounded,
          'Nettoyage': Icons.cleaning_services_rounded,
        }[name] ??
        Icons.handyman_rounded;
  }
}
