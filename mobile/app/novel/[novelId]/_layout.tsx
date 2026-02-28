import { Stack } from "expo-router";
import { COLORS } from "@/lib/constants";

export default function NovelLayout() {
  return (
    <Stack
      screenOptions={{
        headerStyle: { backgroundColor: COLORS.background },
        headerTintColor: COLORS.text,
        contentStyle: { backgroundColor: COLORS.background },
      }}
    >
      <Stack.Screen name="index" options={{ title: "章一覧" }} />
      <Stack.Screen
        name="[chapterId]"
        options={{
          headerShown: false,
          animation: "fade",
        }}
      />
    </Stack>
  );
}
