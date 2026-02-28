import { Tabs } from "expo-router";
import { COLORS } from "@/lib/constants";

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarStyle: { backgroundColor: COLORS.background, borderTopColor: COLORS.border },
        tabBarActiveTintColor: COLORS.primary,
        tabBarInactiveTintColor: COLORS.textSecondary,
        headerStyle: { backgroundColor: COLORS.background },
        headerTintColor: COLORS.text,
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: "ライブラリ",
          tabBarIcon: () => null,
        }}
      />
    </Tabs>
  );
}
