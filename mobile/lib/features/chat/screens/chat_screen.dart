import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../../../theme/colors.dart';
import '../../../theme/typography.dart';
import '../../../core/network/api_endpoints.dart';
import '../../auth/providers/auth_provider.dart';

// ── Data model ─────────────────────────────────────────────────────────────────
class ChatMessageItem {
  final String id;
  final String sender; // 'patient' | 'expert' | 'ai'
  final String text;
  final String time;
  final Map<String, dynamic>? attachment;

  ChatMessageItem({
    required this.id,
    required this.sender,
    required this.text,
    required this.time,
    this.attachment,
  });

  factory ChatMessageItem.fromJson(Map<String, dynamic> json) {
    return ChatMessageItem(
      id: json['id']?.toString() ?? DateTime.now().millisecondsSinceEpoch.toString(),
      sender: json['sender']?.toString() ?? 'expert',
      text: json['text']?.toString() ?? json['content']?.toString() ?? '',
      time: json['time']?.toString() ?? 'Just now',
      attachment: json['attachment'] is Map ? Map<String, dynamic>.from(json['attachment']) : null,
    );
  }
}

// ── Screen ─────────────────────────────────────────────────────────────────────
class ChatScreen extends ConsumerStatefulWidget {
  const ChatScreen({super.key});

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final TextEditingController _textController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  // ── Clinical chat state ───────────────────────────────────────────────────
  WebSocketChannel? _clinicalChannel;
  bool _isConnected = false;
  bool _isExpertTyping = false;
  String _threadStatus = 'active'; // 'active' | 'pending' | 'declined'

  static const String _expertEmail = 'expert@nutriplan.local';

  // Dynamic user session properties
  String _currentUserEmail = '';
  String _currentUserName = '';
  String _currentRoomId = '';

  bool _intakeInitiated = false;

  final List<ChatMessageItem> _clinicalMessages = [];

  // ── AI chat state ─────────────────────────────────────────────────────────
  WebSocketChannel? _aiChannel;
  bool _isAiThinking = false;
  final List<ChatMessageItem> _aiMessages = [];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _connectAiWs();
    // Delay clinical connection to read auth state
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initUserAndConnect();
    });
  }

  void _initUserAndConnect() {
    final authUser = ref.read(authProvider).user;
    final email = authUser?.email.trim();
    final patientEmail = (email != null && email.isNotEmpty) ? email : 'patient@nutriplan.mobile';
    final patientName = (authUser?.name != null && authUser!.name!.isNotEmpty) ? authUser.name! : 'Mobile Patient';

    // Build canonical roomId: alphabetically sorted join
    final emails = [patientEmail, _expertEmail]..sort();
    final roomId = emails.join('_');

    // If switching account, clear previous messages and reset intake
    if (_currentRoomId != roomId) {
      _clinicalChannel?.sink.close();
      _clinicalMessages.clear();
      _intakeInitiated = false;
      _threadStatus = 'pending';
    }

    _currentUserEmail = patientEmail;
    _currentUserName = patientName;
    _currentRoomId = roomId;

    _connectClinicalWs();
    _initiateIntakeRequest();
  }

  // ── Clinical WebSocket ────────────────────────────────────────────────────

  /// Calls POST /clinical/intake/initiate to register this patient's consultation
  /// request on the backend. The expert frontend polls this endpoint and will
  /// see it in the "Requests" tab as a pending intake to accept or decline.
  Future<void> _initiateIntakeRequest() async {
    if (_intakeInitiated || _currentUserEmail.isEmpty) return;
    try {
      final dio = Dio();
      final url = '${ApiEndpoints.chatBaseUrl}/clinical/intake/initiate';
      final response = await dio.post(
        url,
        data: {
          'patient_email': _currentUserEmail,
          'expert_email': _expertEmail,
          'patient_name': _currentUserName,
          'intake_summary':
              '$_currentUserName requesting clinical consultation · Goal: personalized diet plan · Awaiting expert review.',
        },
        options: Options(headers: {'Content-Type': 'application/json'}),
      );
      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        final status = data['status']?.toString() ?? 'pending';
        if (mounted) setState(() => _threadStatus = status);
        _intakeInitiated = true;
      }
    } catch (_) {
      // Network error — intake will be re-registered on next app launch
    }
  }

  void _connectClinicalWs() {
    if (_currentRoomId.isEmpty || _currentUserEmail.isEmpty) return;
    try {
      final host = ApiEndpoints.domain;
      // Backend WS path: /api/v1/chat/ws/clinical/{room_id}/{sender_email}
      final wsUrl = Uri.parse(
        '${ApiEndpoints.wsScheme}://$host:8012/api/v1/chat/ws/clinical/$_currentRoomId/$_currentUserEmail',
      );
      _clinicalChannel?.sink.close();
      _clinicalChannel = WebSocketChannel.connect(wsUrl);

      _clinicalChannel!.stream.listen(
        _onClinicalMessage,
        onDone: () {
          if (mounted) setState(() => _isConnected = false);
          // Attempt reconnect after 3s
          Future.delayed(const Duration(seconds: 3), () {
            if (mounted && _clinicalChannel == null) _connectClinicalWs();
          });
        },
        onError: (_) {
          if (mounted) setState(() => _isConnected = false);
        },
      );

      if (mounted) setState(() => _isConnected = true);
    } catch (_) {
      if (mounted) setState(() => _isConnected = false);
    }
  }

  void _onClinicalMessage(dynamic raw) {
    if (!mounted) return;
    try {
      final data = jsonDecode(raw.toString()) as Map<String, dynamic>;
      final type = data['type']?.toString() ?? '';

      switch (type) {
        // Backend sends full history on connect
        case 'history':
          final msgs = (data['messages'] as List?)
              ?.whereType<Map<String, dynamic>>()
              .map(ChatMessageItem.fromJson)
              .toList() ?? [];
          setState(() => _clinicalMessages
            ..clear()
            ..addAll(msgs));
          _scrollToBottom();
          break;

        // Thread status update (pending / active / declined)
        case 'thread_status':
          setState(() => _threadStatus = data['status']?.toString() ?? 'active');
          break;

        // Intake accepted — thread unlocked + welcome message
        case 'intake_accepted':
          final payload = data['payload'] as Map<String, dynamic>?;
          setState(() {
            _threadStatus = 'active';
            if (payload?['welcome_message'] is Map<String, dynamic>) {
              _clinicalMessages.add(
                ChatMessageItem.fromJson(payload!['welcome_message'] as Map<String, dynamic>),
              );
            }
          });
          _scrollToBottom();
          break;

        // Intake declined
        case 'intake_declined':
          setState(() => _threadStatus = 'declined');
          break;

        // Incoming message (patient or expert)
        case 'clinical_message':
          final payload = data['payload'];
          if (payload is Map<String, dynamic>) {
            final msg = ChatMessageItem.fromJson(payload);
            // Avoid duplicating own messages (we add them optimistically on send)
            if (msg.sender != 'patient') {
              setState(() => _clinicalMessages.add(msg));
              _scrollToBottom();
            }
          }
          break;

        // Typing indicator from expert
        case 'typing':
          setState(() => _isExpertTyping = data['is_typing'] == true);
          break;

        // Server-side error (e.g. thread pending)
        case 'error':
          final detail = data['detail']?.toString() ?? 'Message not sent';
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(detail),
                backgroundColor: AppColors.danger,
              ),
            );
          }
          break;
      }
    } catch (_) {
      // Non-JSON frame — ignore
    }
  }

  void _sendClinicalMessage(String text) {
    if (text.isEmpty) return;

    // Optimistic UI — add immediately
    final optimistic = ChatMessageItem(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      sender: 'patient',
      text: text,
      time: _nowTime(),
    );
    setState(() => _clinicalMessages.add(optimistic));
    _scrollToBottom();

    // Send over WebSocket
    try {
      _clinicalChannel?.sink.add(jsonEncode({
        'type': 'message',
        'sender': 'patient',
        'sender_email': _currentUserEmail,
        'recipient_email': _expertEmail,
        'text': text,
      }));
    } catch (_) {
      // If channel is broken, reconnect
      _connectClinicalWs();
    }
  }

  // ── AI WebSocket ──────────────────────────────────────────────────────────

  void _connectAiWs() {
    try {
      final wsUrl = Uri.parse('${ApiEndpoints.aiChatWsUrl}/mob_usr_001');
      _aiChannel = WebSocketChannel.connect(wsUrl);

      _aiChannel!.stream.listen((message) {
        if (!mounted) return;
        try {
          final data = jsonDecode(message.toString()) as Map<String, dynamic>;
          final type = data['type']?.toString() ?? '';
          if (type == 'status') {
            setState(() => _isAiThinking = true);
          } else if (type == 'ai_response' || type == 'escalation') {
            setState(() {
              _isAiThinking = false;
              _aiMessages.add(ChatMessageItem(
                id: DateTime.now().millisecondsSinceEpoch.toString(),
                sender: 'ai',
                text: data['message']?.toString() ?? '',
                time: _nowTime(),
              ));
            });
            _scrollToBottom();
          }
        } catch (_) {
          // Plain text response
          setState(() {
            _isAiThinking = false;
            _aiMessages.add(ChatMessageItem(
              id: DateTime.now().millisecondsSinceEpoch.toString(),
              sender: 'ai',
              text: message.toString(),
              time: _nowTime(),
            ));
          });
          _scrollToBottom();
        }
      }, onDone: () {
        if (mounted) setState(() => _isAiThinking = false);
      }, onError: (_) {
        if (mounted) setState(() => _isAiThinking = false);
      });
    } catch (_) {}
  }

  // ── Shared send ───────────────────────────────────────────────────────────

  void _sendMessage() {
    final text = _textController.text.trim();
    if (text.isEmpty) return;
    _textController.clear();

    if (_tabController.index == 0) {
      // Clinical tab
      _sendClinicalMessage(text);
    } else {
      // AI tab
      setState(() {
        _aiMessages.add(ChatMessageItem(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          sender: 'patient',
          text: text,
          time: _nowTime(),
        ));
        _isAiThinking = true;
      });
      try {
        if (_aiChannel == null) _connectAiWs();
        _aiChannel?.sink.add(jsonEncode({
          'message': text,
          'user_id': 'mob_usr_001',
        }));
      } catch (_) {
        setState(() => _isAiThinking = false);
      }
      _scrollToBottom();
    }
  }

  // ── Helpers ───────────────────────────────────────────────────────────────

  String _nowTime() {
    final now = DateTime.now();
    final h = now.hour % 12 == 0 ? 12 : now.hour % 12;
    final m = now.minute.toString().padLeft(2, '0');
    final period = now.hour < 12 ? 'AM' : 'PM';
    return '$h:$m $period';
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    _textController.dispose();
    _scrollController.dispose();
    _clinicalChannel?.sink.close();
    _aiChannel?.sink.close();
    super.dispose();
  }

  // ── Build ─────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('NutriPlan Care Chat', style: AppTypography.headingMedium),
        backgroundColor: AppColors.surface,
        elevation: 0,
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: AppColors.primary,
          labelColor: AppColors.primary,
          unselectedLabelColor: AppColors.textSecondary,
          tabs: const [
            Tab(icon: Icon(Icons.medical_services_outlined, size: 20), text: 'Dr. Sarah (Dietitian)'),
            Tab(icon: Icon(Icons.smart_toy_outlined, size: 20), text: 'AI Health Coach'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildClinicalChatView(),
          _buildAiChatView(),
        ],
      ),
    );
  }

  // ── Clinical Chat View ────────────────────────────────────────────────────

  Widget _buildClinicalChatView() {
    return Column(
      children: [
        // Header bar with connection status
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          color: AppColors.surfaceAlt,
          child: Row(
            children: [
              const CircleAvatar(
                radius: 14,
                backgroundImage: NetworkImage(
                  'https://images.unsplash.com/photo-1594824813620-1361c4de4a75?w=150&q=80',
                ),
              ),
              const SizedBox(width: 8),
              const Expanded(
                child: Text(
                  _expertEmail,
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textPrimary,
                  ),
                ),
              ),
              _buildStatusBadge(),
            ],
          ),
        ),

        // Thread pending banner
        if (_threadStatus == 'pending')
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            color: AppColors.warning.withValues(alpha: 0.12),
            child: const Row(
              children: [
                Icon(Icons.hourglass_top_rounded, size: 16, color: AppColors.warning),
                SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Awaiting expert acceptance — messaging will unlock once Dr. Sarah accepts.',
                    style: TextStyle(fontSize: 11, color: AppColors.warning),
                  ),
                ),
              ],
            ),
          ),

        if (_threadStatus == 'declined')
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            color: AppColors.danger.withValues(alpha: 0.12),
            child: const Text(
              'Consultation request was declined by the expert.',
              style: TextStyle(fontSize: 11, color: AppColors.danger),
              textAlign: TextAlign.center,
            ),
          ),

        // Messages list
        Expanded(
          child: _clinicalMessages.isEmpty
              ? _buildEmptyState(
                  icon: Icons.chat_bubble_outline,
                  message: 'No messages yet.\nSend your first message to start the consultation.',
                )
              : ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.all(16),
                  itemCount: _clinicalMessages.length,
                  itemBuilder: (ctx, i) => _buildMessageBubble(_clinicalMessages[i]),
                ),
        ),

        // Typing indicator
        if (_isExpertTyping)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            alignment: Alignment.centerLeft,
            child: const Text(
              'Dr. Sarah is typing...',
              style: TextStyle(
                fontSize: 12,
                fontStyle: FontStyle.italic,
                color: AppColors.textSecondary,
              ),
            ),
          ),

        // Input bar
        _buildInputBar(disabled: _threadStatus == 'declined'),
      ],
    );
  }

  Widget _buildStatusBadge() {
    final isLive = _isConnected && _threadStatus == 'active';
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: (isLive ? AppColors.success : AppColors.warning).withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        isLive ? 'LIVE' : (_threadStatus == 'pending' ? 'PENDING' : 'OFFLINE'),
        style: TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.bold,
          color: isLive ? AppColors.success : AppColors.warning,
        ),
      ),
    );
  }

  // ── AI Chat View ──────────────────────────────────────────────────────────

  Widget _buildAiChatView() {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          color: AppColors.surfaceAlt,
          child: const Row(
            children: [
              CircleAvatar(
                radius: 14,
                backgroundColor: AppColors.primary,
                child: Icon(Icons.smart_toy_outlined, size: 16, color: Colors.white),
              ),
              SizedBox(width: 8),
              Text(
                'NutriPlan AI Health Coach · 24/7',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textPrimary,
                ),
              ),
            ],
          ),
        ),
        Expanded(
          child: _aiMessages.isEmpty
              ? _buildEmptyState(
                  icon: Icons.smart_toy_outlined,
                  message: 'Hello! Ask me about Indian regional recipes,\nmacro targets, or ICMR-NIN recommendations.',
                )
              : ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.all(16),
                  itemCount: _aiMessages.length,
                  itemBuilder: (ctx, i) => _buildMessageBubble(_aiMessages[i]),
                ),
        ),
        if (_isAiThinking)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
            alignment: Alignment.centerLeft,
            child: const Row(
              children: [
                SizedBox(
                  width: 12,
                  height: 12,
                  child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.primary),
                ),
                SizedBox(width: 8),
                Text(
                  'AI is thinking...',
                  style: TextStyle(
                    fontSize: 12,
                    fontStyle: FontStyle.italic,
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
        _buildInputBar(),
      ],
    );
  }

  // ── Shared widgets ────────────────────────────────────────────────────────

  Widget _buildEmptyState({required IconData icon, required String message}) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 48, color: AppColors.textSecondary.withValues(alpha: 0.4)),
          const SizedBox(height: 12),
          Text(
            message,
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 13, color: AppColors.textSecondary, height: 1.5),
          ),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(ChatMessageItem msg) {
    final isMe = msg.sender == 'patient';
    return Align(
      alignment: isMe ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.75,
        ),
        decoration: BoxDecoration(
          color: isMe ? AppColors.primary : AppColors.surface,
          borderRadius: BorderRadius.circular(16).copyWith(
            bottomRight: isMe ? const Radius.circular(0) : const Radius.circular(16),
            bottomLeft: !isMe ? const Radius.circular(0) : const Radius.circular(16),
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.04),
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (!isMe && msg.sender == 'expert')
              Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Text(
                  'Dr. Sarah Jenkins',
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                    color: AppColors.primary.withValues(alpha: 0.8),
                  ),
                ),
              ),
            Text(
              msg.text,
              style: TextStyle(
                fontSize: 14,
                color: isMe ? Colors.white : AppColors.textPrimary,
                height: 1.4,
              ),
            ),
            if (msg.attachment != null) ...[
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: isMe
                      ? Colors.white.withValues(alpha: 0.15)
                      : AppColors.surfaceAlt,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Icon(Icons.insert_chart_outlined,
                        size: 18,
                        color: isMe ? Colors.white : AppColors.primary),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text(
                        msg.attachment!['title']?.toString() ?? '',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                          color: isMe ? Colors.white : AppColors.textPrimary,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
            const SizedBox(height: 4),
            Text(
              msg.time,
              style: TextStyle(
                fontSize: 10,
                color: isMe ? Colors.white70 : AppColors.textSecondary,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInputBar({bool disabled = false}) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: const BoxDecoration(
        color: AppColors.surface,
        border: Border(top: BorderSide(color: AppColors.border)),
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _textController,
              enabled: !disabled,
              decoration: InputDecoration(
                hintText: disabled
                    ? 'Consultation closed'
                    : 'Type your message...',
                hintStyle: const TextStyle(
                  fontSize: 13,
                  color: AppColors.textSecondary,
                ),
                filled: true,
                fillColor: AppColors.surfaceAlt,
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 14,
                  vertical: 10,
                ),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(20),
                  borderSide: BorderSide.none,
                ),
              ),
              onSubmitted: disabled ? null : (_) => _sendMessage(),
            ),
          ),
          const SizedBox(width: 8),
          IconButton(
            icon: Icon(
              Icons.send_rounded,
              color: disabled ? AppColors.textSecondary : AppColors.primary,
            ),
            onPressed: disabled ? null : _sendMessage,
          ),
        ],
      ),
    );
  }
}
