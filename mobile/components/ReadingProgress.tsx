import { StyleSheet, Text, View } from "react-native";

interface Props {
  current: number; // 0-indexed
  total: number;
}

export function ReadingProgress({ current, total }: Props) {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>
        {current + 1} / {total}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: "absolute",
    bottom: 40,
    alignSelf: "center",
    backgroundColor: "rgba(0,0,0,0.6)",
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 16,
  },
  text: {
    color: "#fff",
    fontSize: 13,
    fontWeight: "600",
  },
});
