import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../../../theme/colors.dart';
import '../../../theme/typography.dart';
import '../../../core/network/api_endpoints.dart';

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
      id: json['id'] ?? DateTime.now().millisecondsSinceEpoch.toString(),
      sender: json['sender'] ?? (json['role'] == 'user' ? 'patient' : 'expert'),
      text: json['text'] ?? json['content'] ?? '',
      time: json['time'] ?? 'Just now',
      attachment: json['attachment'],
    );
  }
}

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final TextEditingController _textController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  WebSocketChannel? _clinicalChannel;
  bool _isConnected = false;
  bool _isExpertTyping = false;
  String _clinicalStatus = 'active';

  final List<ChatMessageItem> _clinicalMessages = [
    ChatMessageItem(
      id: 'm1',
      sender: 'expert',
      text: "Hello! I'm Dr. Sarah Jenkins. I've reviewed your metabolic bio. Your blood sugar is stabilizing nicely with our high-fiber regional swaps.",
      time: "10:30 AM",
    ),
    ChatMessageItem(
      id: 'm2',
      sender: 'patient',
      text: "Dr. Sarah, my fasting sugar was 114 mg/dL this morning after the 15-min walk. Should I continue with the 45g carb dinner target?",
      time: "10:45 AM",
      attachment: {
        'title': 'Continuous Glucose Monitor (CGM) Log',
        'meta': 'Avg: 118 mg/dL · TIR: 94%'
      }
    ),
    ChatMessageItem(
      id: 'm3',
      sender: 'expert',
      text: "Yes, absolutely! Prioritize steamed greens (palak or methi) first on your plate to blunt any post-meal excursion.",
      time: "10:50 AM",
    )
  ];

  final List<ChatMessageItem> _aiMessages = [
    ChatMessageItem(
      id: 'ai1',
      sender: 'ai',
      text: "Hello! I am your NutriPlan 24/7 AI Health Coach. Ask me about Indian regional recipes, macro math, or ICMR-NIN nutrition recommendations.",
      time: "Just now",
    )
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _connectClinicalWs();
  }

  void _connectClinicalWs() {
    try {
      final host = ApiEndpoints.authBaseUrl.contains('10.0.2.2') ? '10.0.2.2' : 'localhost';
      final wsUrl = Uri.parse('ws://$host:8012/api/v1/chat/ws/clinical/expert@nutriplan.local_test@test.com/test@test.com');
      _clinicalChannel = WebSocketChannel.connect(wsUrl);

      _clinicalChannel!.stream.listen((message) {
        final data = jsonDecode(message);
        if (data['type'] == 'clinical_message') {
          final payload = data['payload'];
          setState(() {
            _clinicalMessages.add(ChatMessageItem.fromJson(payload));
          });
          _scrollToBottom();
        } else if (data['type'] == 'typing') {
          setState(() {
            _isExpertTyping = data['is_typing'] ?? false;
          });
        }
      }, onDone: () {
        setState(() => _isConnected = false);
      }, onError: (e) {
        setState(() => _isConnected = false);
      });

      setState(() => _isConnected = true);
    } catch (_) {
      // Fallback in case of mock environment
    }
  }

  void _sendMessage() {
    final text = _textController.text.trim();
    if (text.isEmpty) return;

    _textController.clear();

    if (_tabController.index == 0) {
      // Clinical Dietitian tab
      final newMsg = ChatMessageItem(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        sender: 'patient',
        text: text,
        time: 'Just now',
      );
      setState(() {
        _clinicalMessages.add(newMsg);
      });

      // Send to WebSocket
      try {
        _clinicalChannel?.sink.add(jsonEncode({
          'type': 'message',
          'sender': 'patient',
          'sender_email': 'test@test.com',
          'recipient_email': 'expert@nutriplan.local',
          'text': text,
        }));
      } catch (_) {}

    } else {
      // AI Coach tab
      final userMsg = ChatMessageItem(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        sender: 'patient',
        text: text,
        time: 'Just now',
      );
      setState(() {
        _aiMessages.add(userMsg);
      });

      // Simulated AI reply
      Future.delayed(const Duration(milliseconds: 1200), () {
        if (!mounted) return;
        setState(() {
          _aiMessages.add(ChatMessageItem(
            id: DateTime.now().millisecondsSinceEpoch.toString(),
            sender: 'ai',
            text: "Based on your 1800 kcal target, pairing whole-grain roti or brown rice with high-protein dal (moong/toor) aligns with ICMR-NIN balanced dietary standards.",
            time: 'Just now',
          ));
        });
        _scrollToBottom();
      });
    }

    _scrollToBottom();
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
    super.dispose();
  }

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
          _buildChatView(_clinicalMessages, isClinical: true),
          _buildChatView(_aiMessages, isClinical: false),
        ],
      ),
    );
  }

  Widget _buildChatView(List<ChatMessageItem> messages, {required bool isClinical}) {
    return Column(
      children: [
        if (isClinical)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            color: AppColors.surfaceAlt,
            child: Row(
              children: [
                const CircleAvatar(
                  radius: 14,
                  backgroundImage: NetworkImage('https://images.unsplash.com/photo-1594824813620-1361c4de4a75?w=150&q=80'),
                ),
                const SizedBox(width: 8),
                const Expanded(
                  child: Text(
                    'Dr. Sarah Jenkins · Active Care Window',
                    style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: AppColors.success.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Text(
                    'LIVE',
                    style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppColors.success),
                  ),
                ),
              ],
            ),
          ),
        Expanded(
          child: ListView.builder(
            controller: _scrollController,
            padding: const EdgeInsets.all(16),
            itemCount: messages.length,
            itemBuilder: (context, index) {
              final msg = messages[index];
              final isMe = msg.sender == 'patient';
              return Align(
                alignment: isMe ? Alignment.centerRight : Alignment.centerLeft,
                child: Container(
                  margin: const EdgeInsets.only(bottom: 12),
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                  constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
                  decoration: BoxDecoration(
                    color: isMe ? AppColors.primary : AppColors.surface,
                    borderRadius: BorderRadius.circular(16).copyWith(
                      bottomRight: isMe ? const Radius.circular(0) : const Radius.circular(16),
                      bottomLeft: !isMe ? const Radius.circular(0) : const Radius.circular(16),
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.04),
                        blurRadius: 4,
                        offset: const Offset(0, 2),
                      )
                    ],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        msg.text,
                        style: TextStyle(
                          fontSize: 14,
                          color: isMe ? Colors.white : AppColors.textPrimary,
                          height: 1.3,
                        ),
                      ),
                      if (msg.attachment != null) ...[
                        const SizedBox(height: 8),
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: isMe ? Colors.white.withOpacity(0.15) : AppColors.surfaceAlt,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Row(
                            children: [
                              const Icon(Icons.insert_chart_outlined, size: 20, color: AppColors.primary),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  msg.attachment!['title'] ?? '',
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
            },
          ),
        ),
        if (_isExpertTyping)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            alignment: Alignment.centerLeft,
            child: const Text(
              'Dr. Sarah is typing...',
              style: TextStyle(fontSize: 12, fontStyle: FontStyle.italic, color: AppColors.textSecondary),
            ),
          ),
        Container(
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
                  decoration: InputDecoration(
                    hintText: 'Type your message...',
                    hintStyle: const TextStyle(fontSize: 13, color: AppColors.textSecondary),
                    filled: true,
                    fillColor: AppColors.surfaceAlt,
                    contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(20),
                      borderSide: BorderSide.none,
                    ),
                  ),
                  onSubmitted: (_) => _sendMessage(),
                ),
              ),
              const SizedBox(width: 8),
              IconButton(
                icon: const Icon(Icons.send_rounded, color: AppColors.primary),
                onPressed: _sendMessage,
              ),
            ],
          ),
        ),
      ],
    );
  }
}
