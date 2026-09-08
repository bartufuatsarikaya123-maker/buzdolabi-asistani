import { useState } from "react";
import {
  FlatList,
  SafeAreaView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";

export default function HomeScreen() {
  const [ingredient, setIngredient] = useState("");
  const [ingredientList, setIngredientList] = useState<string[]>([]);

  const addIngredient = () => {
    if (ingredient.trim() === "") return;
    setIngredientList([...ingredientList, ingredient.trim()]);
    setIngredient("");
  };

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.title}>🍳 Buzdolabı Asistanı</Text>

      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder="Malzeme yaz (örn: Domates, Peynir)"
          placeholderTextColor="#888"
          value={ingredient}
          onChangeText={setIngredient}
        />
        <TouchableOpacity style={styles.addButton} onPress={addIngredient}>
          <Text style={styles.addButtonText}>Ekle</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.listContainer}>
        <Text style={styles.subtitle}>Buzdolabındakiler:</Text>
        <FlatList
          data={ingredientList}
          keyExtractor={(item, index) => index.toString()}
          renderItem={({ item }) => (
            <View style={styles.itemCard}>
              <Text style={styles.itemText}>• {item}</Text>
            </View>
          )}
          ListEmptyComponent={
            <Text style={styles.emptyText}>Henüz malzeme eklenmedi.</Text>
          }
        />
      </View>

      <TouchableOpacity style={styles.recipeButton}>
        <Text style={styles.recipeButtonText}>Tarif Önerisi Al</Text>
      </TouchableOpacity>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f9f9f9",
    padding: 20,
    paddingTop: 50,
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    marginBottom: 20,
    textAlign: "center",
    color: "#333",
  },
  inputContainer: { flexDirection: "row", marginBottom: 15 },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: "#ddd",
    backgroundColor: "#fff",
    padding: 12,
    borderRadius: 8,
    fontSize: 16,
    marginRight: 10,
  },
  addButton: {
    backgroundColor: "#34C759",
    justifyContent: "center",
    paddingHorizontal: 20,
    borderRadius: 8,
  },
  addButtonText: { color: "#fff", fontSize: 16, fontWeight: "bold" },
  listContainer: { flex: 1, marginVertical: 10 },
  subtitle: {
    fontSize: 18,
    fontWeight: "600",
    marginBottom: 10,
    color: "#555",
  },
  itemCard: {
    backgroundColor: "#fff",
    padding: 10,
    borderRadius: 6,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: "#eee",
  },
  itemText: { fontSize: 16, color: "#333" },
  emptyText: { color: "#888", fontStyle: "italic" },
  recipeButton: {
    backgroundColor: "#007AFF",
    padding: 15,
    borderRadius: 8,
    alignItems: "center",
    marginTop: 10,
  },
  recipeButtonText: { color: "#fff", fontSize: 16, fontWeight: "bold" },
});
