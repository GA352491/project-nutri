import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:nutriplan/main.dart';

void main() {
  testWidgets('NutriPlanApp smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const ProviderScope(child: NutriPlanApp()));
    expect(find.byType(NutriPlanApp), findsOneWidget);
  });
}
