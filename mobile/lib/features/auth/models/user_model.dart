class UserModel {
  final String id;
  final String email;
  final String? name;
  final String role;
  final bool hasCompletedOnboarding;

  const UserModel({
    required this.id,
    required this.email,
    this.name,
    required this.role,
    this.hasCompletedOnboarding = false,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] ?? json['sub'] ?? '',
      email: json['email'] ?? '',
      name: json['name'] ?? json['full_name'],
      role: json['role'] ?? 'patient',
      hasCompletedOnboarding: json['has_completed_onboarding'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'name': name,
      'role': role,
      'has_completed_onboarding': hasCompletedOnboarding,
    };
  }
}
