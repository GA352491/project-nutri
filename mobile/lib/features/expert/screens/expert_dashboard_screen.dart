import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../theme/colors.dart';
import '../../../theme/typography.dart';
import '../../auth/providers/auth_provider.dart';
import '../services/expert_service.dart';
import '../widgets/expert_bottom_nav.dart';

class ExpertDashboardScreen extends ConsumerWidget {
  const ExpertDashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);
    final expertEmail = authState.user?.email ?? 'expert@nutriplan.local';
    final expertName = authState.user?.name ?? 'Dr. Sarah Jenkins, RD';

    final statsAsync = ref.watch(expertStatsProvider(expertEmail));
    final appointmentsAsync = ref.watch(expertAppointmentsProvider);

    return Scaffold(
      backgroundColor: NutriColors.canvas,
      appBar: AppBar(
        backgroundColor: NutriColors.canvasRaised,
        elevation: 0,
        titleSpacing: 16,
        title: Row(
          children: [
            Container(
              width: 38,
              height: 38,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(color: NutriColors.primary, width: 2),
                image: const DecorationImage(
                  image: NetworkImage('https://images.unsplash.com/photo-1594824813580-c1fd9f939e6a?w=150&q=80'),
                  fit: BoxFit.cover,
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    expertName,
                    style: NutriTypography.bodyMd.copyWith(fontWeight: FontWeight.bold),
                    overflow: TextOverflow.ellipsis,
                  ),
                  Row(
                    children: [
                      Container(
                        width: 7,
                        height: 7,
                        decoration: const BoxDecoration(
                          color: NutriColors.success,
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: 5),
                      Text(
                        'Licensed Provider · IDA Active',
                        style: NutriTypography.dataSm.copyWith(color: NutriColors.inkMuted, fontSize: 10),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_none_rounded, color: NutriColors.ink),
            tooltip: 'Alerts',
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('No urgent clinical triage alerts at this time.')),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.logout_rounded, color: NutriColors.danger),
            tooltip: 'Logout',
            onPressed: () async {
              await ref.read(authProvider.notifier).logout();
              if (context.mounted) {
                context.go('/login');
              }
            },
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: RefreshIndicator(
        color: NutriColors.primary,
        onRefresh: () async {
          ref.invalidate(expertStatsProvider(expertEmail));
          ref.invalidate(expertAppointmentsProvider);
        },
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // ── Header Welcome ──────────────────────────────────────────
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF234226), Color(0xFF2F5233)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: NutriColors.primary.withValues(alpha: 0.25),
                      blurRadius: 14,
                      offset: const Offset(0, 6),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'CLINICAL PRACTICE PORTAL',
                          style: TextStyle(
                            color: Color(0xFFDDE8DF),
                            fontSize: 10,
                            letterSpacing: 1.2,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(
                            color: Colors.white.withValues(alpha: 0.2),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: const Row(
                            children: [
                              Icon(Icons.verified, color: Colors.white, size: 12),
                              SizedBox(width: 4),
                              Text(
                                'Telehealth Live',
                                style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    const Text(
                      'Welcome to your Practice Hub',
                      style: TextStyle(
                        fontFamily: NutriTypography.displayFont,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Monitor patient compliance, conduct consultations, and sign off ICMR-NIN nutrition plans.',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.white.withValues(alpha: 0.85),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 20),

              // ── KPI Metrics Grid ─────────────────────────────────────────
              const Text('Practice Performance', style: NutriTypography.displaySm),
              const SizedBox(height: 12),
              statsAsync.when(
                loading: () => const Center(
                  child: Padding(
                    padding: EdgeInsets.symmetric(vertical: 24),
                    child: CircularProgressIndicator(),
                  ),
                ),
                error: (_, __) => _buildStatsGrid(
                  const ExpertStats(
                    totalPatients: 42,
                    monthlyEarnings: 3840.0,
                    rating: 4.9,
                    pendingPayouts: 480.0,
                    reviewCount: 38,
                  ),
                ),
                data: (stats) => _buildStatsGrid(stats),
              ),

              const SizedBox(height: 24),

              // ── Quick Action Shortcuts ───────────────────────────────────
              const Text('Quick Actions', style: NutriTypography.displaySm),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: _buildActionTile(
                      icon: Icons.people_alt_rounded,
                      color: const Color(0xFF1D5FAC),
                      title: 'My Patients',
                      subtitle: 'Review charts & diets',
                      onTap: () => context.go('/expert/patients'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildActionTile(
                      icon: Icons.mark_chat_unread_rounded,
                      color: const Color(0xFF6C47FF),
                      title: 'Patient Inbox',
                      subtitle: 'Direct clinical chat',
                      onTap: () => context.go('/expert/messages'),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 24),

              // ── Today's Schedule & Consultations ─────────────────────────
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text("Today's Consultations", style: NutriTypography.displaySm),
                  TextButton.icon(
                    onPressed: () => context.go('/expert/patients'),
                    icon: const Icon(Icons.arrow_forward, size: 14),
                    label: const Text('All Patients', style: TextStyle(fontSize: 12)),
                  ),
                ],
              ),
              const SizedBox(height: 8),

              appointmentsAsync.when(
                loading: () => const Center(
                  child: Padding(
                    padding: EdgeInsets.symmetric(vertical: 32),
                    child: CircularProgressIndicator(),
                  ),
                ),
                error: (_, __) => const Text('Could not load appointment slots'),
                data: (appointments) {
                  if (appointments.isEmpty) {
                    return Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(24),
                      decoration: BoxDecoration(
                        color: NutriColors.canvasRaised,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: NutriColors.border),
                      ),
                      child: const Column(
                        children: [
                          Icon(Icons.event_available_rounded, size: 40, color: NutriColors.inkMuted),
                          SizedBox(height: 8),
                          Text('No upcoming consultations for today', style: NutriTypography.bodyMd),
                          SizedBox(height: 4),
                          Text('New patient bookings will appear here automatically.', style: TextStyle(color: NutriColors.inkMuted, fontSize: 12)),
                        ],
                      ),
                    );
                  }

                  return Column(
                    children: appointments.map((apt) => _buildAppointmentCard(context, apt)).toList(),
                  );
                },
              ),

              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
      bottomNavigationBar: const ExpertBottomNav(currentIndex: 0),
    );
  }

  Widget _buildStatsGrid(ExpertStats stats) {
    return GridView.count(
      crossAxisCount: 2,
      crossAxisSpacing: 12,
      mainAxisSpacing: 12,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      childAspectRatio: 1.6,
      children: [
        _buildStatCard(
          title: 'ACTIVE PATIENTS',
          value: stats.totalPatients.toString(),
          icon: Icons.group_rounded,
          color: NutriColors.primary,
        ),
        _buildStatCard(
          title: 'THIS MONTH',
          value: '\$${stats.monthlyEarnings.toStringAsFixed(0)}',
          icon: Icons.trending_up_rounded,
          color: NutriColors.success,
        ),
        _buildStatCard(
          title: 'PENDING PAYOUT',
          value: '\$${stats.pendingPayouts.toStringAsFixed(0)}',
          icon: Icons.account_balance_wallet_rounded,
          color: NutriColors.secondary,
        ),
        _buildStatCard(
          title: 'AVERAGE RATING',
          value: '${stats.rating.toStringAsFixed(1)} ★',
          icon: Icons.star_rounded,
          color: Colors.amber.shade700,
        ),
      ],
    );
  }

  Widget _buildStatCard({
    required String title,
    required String value,
    required IconData icon,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: NutriColors.canvasRaised,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: NutriColors.border),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.02),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                title,
                style: NutriTypography.dataSm.copyWith(
                  color: NutriColors.inkMuted,
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Icon(icon, color: color, size: 18),
            ],
          ),
          Text(
            value,
            style: NutriTypography.displaySm.copyWith(
              color: NutriColors.ink,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionTile({
    required IconData icon,
    required Color color,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: NutriColors.canvasRaised,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: NutriColors.border),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: color, size: 22),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: NutriTypography.bodySm.copyWith(fontWeight: FontWeight.bold)),
                  Text(
                    subtitle,
                    style: NutriTypography.dataSm.copyWith(color: NutriColors.inkMuted, fontSize: 11),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAppointmentCard(BuildContext context, ExpertAppointment apt) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: NutriColors.canvasRaised,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: NutriColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: NutriColors.primarySoft,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      '${apt.time} (${apt.duration})',
                      style: const TextStyle(
                        color: NutriColors.primaryStrong,
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    apt.date,
                    style: NutriTypography.dataSm.copyWith(color: NutriColors.inkMuted, fontSize: 11),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: NutriColors.success.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  apt.status,
                  style: const TextStyle(color: NutriColors.success, fontSize: 10, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(apt.patientName, style: NutriTypography.bodyMd.copyWith(fontWeight: FontWeight.bold)),
          const SizedBox(height: 2),
          Text(
            apt.type,
            style: NutriTypography.dataSm.copyWith(color: NutriColors.inkMuted, fontSize: 12),
          ),
          const SizedBox(height: 14),
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        backgroundColor: NutriColors.primary,
                        content: Text('Connecting to encrypted telehealth room for ${apt.patientName}...'),
                      ),
                    );
                  },
                  icon: const Icon(Icons.videocam_rounded, size: 16),
                  label: const Text('Join Video Room'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: NutriColors.primary,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              OutlinedButton(
                onPressed: () => context.go('/expert/patients'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: NutriColors.ink,
                  side: const BorderSide(color: NutriColors.border),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                child: const Text('Chart'),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
