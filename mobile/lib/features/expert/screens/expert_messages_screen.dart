import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_endpoints.dart';
import '../../../theme/colors.dart';
import '../../../theme/typography.dart';
import '../../auth/providers/auth_provider.dart';
import '../services/expert_service.dart';
import '../widgets/expert_bottom_nav.dart';

class ExpertMessagesScreen extends ConsumerStatefulWidget {
  const ExpertMessagesScreen({super.key});

  @override
  ConsumerState<ExpertMessagesScreen> createState() => _ExpertMessagesScreenState();
}

class _ExpertMessagesScreenState extends ConsumerState<ExpertMessagesScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final expertEmail = authState.user?.email ?? 'expert@nutriplan.local';
    final threadsAsync = ref.watch(expertThreadsProvider(expertEmail));

    return Scaffold(
      backgroundColor: NutriColors.canvas,
      appBar: AppBar(
        backgroundColor: NutriColors.canvasRaised,
        elevation: 0,
        title: const Text('Clinical Patient Messages', style: NutriTypography.displaySm),
        bottom: TabBar(
          controller: _tabController,
          labelColor: NutriColors.primary,
          unselectedLabelColor: NutriColors.inkMuted,
          indicatorColor: NutriColors.primary,
          indicatorWeight: 3,
          labelStyle: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
          tabs: const [
            Tab(text: 'Active Consultations'),
            Tab(text: 'Intake Triage Requests'),
          ],
        ),
      ),
      body: threadsAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => Center(child: Text('Error loading threads: $err')),
        data: (threads) {
          final activeThreads = threads.where((t) => t.status == 'active').toList();
          final pendingThreads = threads.where((t) => t.status == 'pending').toList();

          return TabBarView(
            controller: _tabController,
            children: [
              _buildThreadList(activeThreads, isPending: false),
              _buildThreadList(pendingThreads, isPending: true),
            ],
          );
        },
      ),
      bottomNavigationBar: const ExpertBottomNav(currentIndex: 2),
    );
  }

  Widget _buildThreadList(List<ClinicalThreadItem> list, {required bool isPending}) {
    if (list.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              isPending ? Icons.done_all_rounded : Icons.forum_outlined,
              size: 48,
              color: NutriColors.inkMuted,
            ),
            const SizedBox(height: 12),
            Text(
              isPending ? 'No pending intake requests.' : 'No active clinical chats found.',
              style: NutriTypography.bodyMd,
            ),
            const SizedBox(height: 4),
            Text(
              isPending
                  ? 'New patients requesting reviews will appear here.'
                  : 'Start a message thread from the Patients tab.',
              style: NutriTypography.dataSm.copyWith(color: NutriColors.inkMuted),
            ),
          ],
        ),
      );
    }

    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemCount: list.length,
      separatorBuilder: (_, __) => const SizedBox(height: 10),
      itemBuilder: (context, index) {
        final thread = list[index];
        return InkWell(
          onTap: () => _openChatThread(context, thread),
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
                Stack(
                  children: [
                    CircleAvatar(
                      radius: 24,
                      backgroundColor: NutriColors.primarySoft,
                      child: Text(
                        thread.patientName.isNotEmpty ? thread.patientName[0] : 'P',
                        style: const TextStyle(
                          color: NutriColors.primaryStrong,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    Positioned(
                      bottom: 0,
                      right: 0,
                      child: Container(
                        width: 12,
                        height: 12,
                        decoration: BoxDecoration(
                          color: NutriColors.success,
                          shape: BoxShape.circle,
                          border: Border.all(color: Colors.white, width: 2),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            thread.patientName,
                            style: NutriTypography.bodyMd.copyWith(fontWeight: FontWeight.bold),
                          ),
                          Text(
                            thread.lastTime.isNotEmpty ? thread.lastTime : 'Active',
                            style: NutriTypography.dataSm.copyWith(color: NutriColors.inkMuted, fontSize: 10),
                          ),
                        ],
                      ),
                      const SizedBox(height: 3),
                      Text(
                        thread.intakeSummary.isNotEmpty
                            ? thread.intakeSummary
                            : thread.lastMessage,
                        style: NutriTypography.dataSm.copyWith(
                          color: thread.unreadCount > 0 ? NutriColors.ink : NutriColors.inkMuted,
                          fontWeight: thread.unreadCount > 0 ? FontWeight.w600 : FontWeight.normal,
                          fontSize: 11,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
                if (thread.unreadCount > 0) ...[
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.all(6),
                    decoration: const BoxDecoration(
                      color: NutriColors.primary,
                      shape: BoxShape.circle,
                    ),
                    child: Text(
                      '${thread.unreadCount}',
                      style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ],
            ),
          ),
        );
      },
    );
  }

  void _openChatThread(BuildContext context, ClinicalThreadItem thread) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => _ClinicalChatScreen(thread: thread),
      ),
    );
  }
}

class _ClinicalChatScreen extends StatefulWidget {
  final ClinicalThreadItem thread;

  const _ClinicalChatScreen({required this.thread});

  @override
  State<_ClinicalChatScreen> createState() => _ClinicalChatScreenState();
}

class _ClinicalChatScreenState extends State<_ClinicalChatScreen> {
  final TextEditingController _textController = TextEditingController();
  final List<Map<String, dynamic>> _messages = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _fetchMessages();
  }

  Future<void> _fetchMessages() async {
    setState(() => _isLoading = true);
    try {
      final res = await ApiClient().dio.get(
            '${ApiEndpoints.chatBaseUrl}/clinical/thread/${widget.thread.roomId}/messages',
          );
      if (res.data is List) {
        setState(() {
          _messages.clear();
          for (final m in res.data) {
            _messages.add(Map<String, dynamic>.from(m));
          }
        });
      }
    } catch (_) {}

    // If message list is empty, initialize thread greeting
    if (_messages.isEmpty) {
      setState(() {
        _messages.add({
          'sender': 'expert',
          'text': 'Hello ${widget.thread.patientName}! I have reviewed your health intake form and nutrition goals. How are your energy levels and meals progressing?',
          'time': 'Just now',
        });
      });
    }

    setState(() => _isLoading = false);
  }

  Future<void> _sendMessage() async {
    final text = _textController.text.trim();
    if (text.isEmpty) return;

    _textController.clear();
    setState(() {
      _messages.add({
        'sender': 'expert',
        'text': text,
        'time': 'Just now',
      });
    });

    try {
      await ApiClient().dio.post(
        '${ApiEndpoints.chatBaseUrl}/send',
        data: {
          'message': text,
          'recipient': widget.thread.patientEmail,
        },
      );
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: NutriColors.canvas,
      appBar: AppBar(
        backgroundColor: NutriColors.canvasRaised,
        elevation: 0,
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(widget.thread.patientName, style: NutriTypography.bodyMd.copyWith(fontWeight: FontWeight.bold)),
            Text(
              widget.thread.patientEmail,
              style: NutriTypography.dataSm.copyWith(color: NutriColors.inkMuted, fontSize: 10),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.videocam_rounded, color: NutriColors.primary),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('Starting telehealth session with ${widget.thread.patientName}...')),
              );
            },
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _messages.length,
                    itemBuilder: (context, index) {
                      final msg = _messages[index];
                      final isExpert = msg['sender'] == 'expert';

                      return Align(
                        alignment: isExpert ? Alignment.centerRight : Alignment.centerLeft,
                        child: Container(
                          margin: const EdgeInsets.symmetric(vertical: 4),
                          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                          constraints: BoxConstraints(
                            maxWidth: MediaQuery.of(context).size.width * 0.78,
                          ),
                          decoration: BoxDecoration(
                            color: isExpert ? NutriColors.primary : NutriColors.canvasRaised,
                            borderRadius: BorderRadius.circular(16).copyWith(
                              bottomRight: isExpert ? const Radius.circular(0) : const Radius.circular(16),
                              bottomLeft: !isExpert ? const Radius.circular(0) : const Radius.circular(16),
                            ),
                            border: isExpert ? null : Border.all(color: NutriColors.border),
                          ),
                          child: Column(
                            crossAxisAlignment:
                                isExpert ? CrossAxisAlignment.end : CrossAxisAlignment.start,
                            children: [
                              Text(
                                msg['text'] ?? '',
                                style: TextStyle(
                                  color: isExpert ? Colors.white : NutriColors.ink,
                                  fontSize: 13,
                                  height: 1.4,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                msg['time'] ?? '',
                                style: TextStyle(
                                  color: isExpert ? Colors.white70 : NutriColors.inkMuted,
                                  fontSize: 9,
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
          ),
          Container(
            padding: const EdgeInsets.all(12),
            color: NutriColors.canvasRaised,
            child: SafeArea(
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _textController,
                      decoration: InputDecoration(
                        hintText: 'Type clinical consultation message...',
                        hintStyle: const TextStyle(fontSize: 13, color: NutriColors.inkMuted),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                        filled: true,
                        fillColor: NutriColors.canvas,
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(20),
                          borderSide: const BorderSide(color: NutriColors.border),
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(20),
                          borderSide: const BorderSide(color: NutriColors.border),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton(
                    onPressed: _sendMessage,
                    icon: const Icon(Icons.send_rounded, color: NutriColors.primary),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
