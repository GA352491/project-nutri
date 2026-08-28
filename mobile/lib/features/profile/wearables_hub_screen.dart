import 'dart:io';
import 'package:flutter/material.dart';
import '../../theme/colors.dart';
import 'services/health_kit_service.dart';

class WearablesHubScreen extends StatefulWidget {
  const WearablesHubScreen({super.key});

  @override
  State<WearablesHubScreen> createState() => _WearablesHubScreenState();
}

class _WearablesHubScreenState extends State<WearablesHubScreen> {
  bool _isSyncing = false;
  final HealthKitService _healthService = HealthKitService();
  String _adaptiveFeedback = 'Biometrics active. Daily calories dynamically adjust to activity level.';
  Map<String, dynamic>? _liveSummary;

  final List<Map<String, dynamic>> _devices = [
    {
      'id': 'apple',
      'name': 'Apple HealthKit & Watch',
      'icon': Icons.watch_rounded,
      'desc': 'Live Steps, Active Energy Burned & Heart Rate from Apple Watch',
      'connected': true,
      'battery': '94%',
      'lastSync': 'Just now',
      'color': Colors.redAccent,
    },
    {
      'id': 'whoop',
      'name': 'Whoop 4.0',
      'icon': Icons.bolt_rounded,
      'desc': 'Strain score, Recovery %, HRV & deep sleep tracking',
      'connected': true,
      'battery': '88%',
      'lastSync': '4m ago',
      'color': Colors.amber,
    },
    {
      'id': 'fitbit',
      'name': 'Fitbit / Pixel Watch',
      'icon': Icons.health_and_safety_rounded,
      'desc': 'Heart rate zones & sleep score by Google',
      'connected': false,
      'color': Colors.cyan,
    },
    {
      'id': 'garmin',
      'name': 'Garmin Connect',
      'icon': Icons.explore_rounded,
      'desc': 'Body Battery™, VO2 Max & training load',
      'connected': false,
      'color': Colors.blueAccent,
    },
  ];

  @override
  void initState() {
    super.initState();
    _loadSummary();
  }

  Future<void> _loadSummary() async {
    final summary = await _healthService.fetchSummary('user_123');
    if (summary != null && mounted) {
      setState(() {
        _liveSummary = summary;
        if (summary['adaptive_message'] != null) {
          _adaptiveFeedback = summary['adaptive_message'];
        }
      });
    }
  }

  Future<void> _toggleDevice(Map<String, dynamic> device) async {
    final willConnect = !(device['connected'] as bool);
    setState(() {
      device['connected'] = willConnect;
      if (willConnect) {
        device['battery'] = '96%';
        device['lastSync'] = 'Just now';
      }
    });

    if (willConnect) {
      if (device['id'] == 'apple') {
        await _healthService.syncHealthTelemetry(
          userId: 'user_123',
          steps: 9240,
          activeEnergyBurned: 480.0,
        );
      } else if (device['id'] == 'whoop') {
        await _healthService.syncWhoopTelemetry(
          userId: 'user_123',
          strain: 16.2,
          recoveryScore: 82,
          activeCalories: 520.0,
        );
      }
      await _loadSummary();
    }

    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          willConnect
              ? 'Paired ${device['name']}! Biometrics synced to Meal Plan.'
              : 'Disconnected ${device['name']}.',
        ),
        backgroundColor: willConnect ? NutriColors.primary : Colors.grey[800],
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  Future<void> _manualSync() async {
    setState(() => _isSyncing = true);
    
    // Sync Apple HealthKit / Health Connect
    final hkRes = await _healthService.syncHealthTelemetry(
      userId: 'user_123',
      steps: 10450,
      activeEnergyBurned: 530.0,
      heartRateAvg: 68,
    );

    // Sync Whoop
    final whoopRes = await _healthService.syncWhoopTelemetry(
      userId: 'user_123',
      strain: 15.8,
      recoveryScore: 88,
      activeCalories: 512.0,
    );

    await _loadSummary();

    setState(() => _isSyncing = false);
    if (!mounted) return;

    final feedback = whoopRes['data']?['adaptive_feedback'] ?? 'Synced latest biometrics from Apple Watch & Whoop! ✨';

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(feedback),
        backgroundColor: NutriColors.primary,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final steps = _liveSummary?['today_steps'] ?? 9240;
    final activeCals = _liveSummary?['today_calories'] ?? 480;
    final hrv = _liveSummary?['hrv_ms'] ?? 58;

    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F172A),
        elevation: 0,
        title: const Text('Wearables & Devices', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
        actions: [
          IconButton(
            icon: _isSyncing
                ? SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: NutriColors.primary))
                : Icon(Icons.sync_rounded, color: NutriColors.primary),
            onPressed: _isSyncing ? null : _manualSync,
          )
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // AI Biometric Adaptation Card
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [NutriColors.primary.withValues(alpha: 0.2), Colors.teal.withValues(alpha: 0.1)],
              ),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: NutriColors.primary.withValues(alpha: 0.3)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: NutriColors.primary.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(Icons.auto_awesome_rounded, color: NutriColors.primary, size: 24),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Text('Live Biometric Adaptation', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
                          const SizedBox(width: 6),
                          Chip(
                            label: const Text('LIVE SYNC', style: TextStyle(color: Colors.white, fontSize: 9, fontWeight: FontWeight.bold)),
                            backgroundColor: NutriColors.primary,
                            visualDensity: VisualDensity.compact,
                            padding: EdgeInsets.zero,
                          )
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        _adaptiveFeedback,
                        style: TextStyle(color: Colors.white.withValues(alpha: 0.8), fontSize: 12, height: 1.4),
                      ),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          _buildStatPill('👟 $steps steps'),
                          const SizedBox(width: 8),
                          _buildStatPill('🔥 $activeCals kcal'),
                          const SizedBox(width: 8),
                          _buildStatPill('💓 $hrv ms HRV'),
                        ],
                      )
                    ],
                  ),
                )
              ],
            ),
          ),

          const SizedBox(height: 24),
          const Text('Connected Health Trackers', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
          const SizedBox(height: 12),

          // Device Cards
          ..._devices.map((device) {
            final isConn = device['connected'] as bool;
            return Container(
              margin: const EdgeInsets.only(bottom: 12),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF1E293B),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: isConn ? NutriColors.primary.withValues(alpha: 0.4) : Colors.white.withValues(alpha: 0.08)),
              ),
              child: Column(
                children: [
                  Row(
                    children: [
                      CircleAvatar(
                        backgroundColor: (device['color'] as Color).withValues(alpha: 0.15),
                        child: Icon(device['icon'] as IconData, color: device['color'] as Color),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(device['name'] as String, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
                            Text(device['desc'] as String, style: TextStyle(color: Colors.white.withValues(alpha: 0.6), fontSize: 12)),
                          ],
                        ),
                      ),
                    ],
                  ),
                  if (isConn) ...[
                    const SizedBox(height: 12),
                    Divider(color: Colors.white.withValues(alpha: 0.08), height: 1),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('🔋 Battery: ${device['battery']}', style: TextStyle(color: Colors.white.withValues(alpha: 0.5), fontSize: 11)),
                        Text('🕒 Synced: ${device['lastSync']}', style: TextStyle(color: Colors.white.withValues(alpha: 0.5), fontSize: 11)),
                      ],
                    ),
                  ],
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    child: OutlinedButton(
                      style: OutlinedButton.styleFrom(
                        foregroundColor: isConn ? Colors.redAccent : NutriColors.primary,
                        side: BorderSide(color: isConn ? Colors.redAccent.withValues(alpha: 0.5) : NutriColors.primary),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                      onPressed: () => _toggleDevice(device),
                      child: Text(isConn ? 'Disconnect' : 'Connect Device →', style: const TextStyle(fontWeight: FontWeight.bold)),
                    ),
                  )
                ],
              ),
            );
          }),
        ],
      ),
    );
  }

  Widget _buildStatPill(String label) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(label, style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
    );
  }
}
