from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import random
import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")
print("ANAHTAR DURUMU:", "BAŞARILI (OKUNDU)" if API_KEY else "BULUNAMADI!")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY bulunamadı.")

genai.configure(api_key=API_KEY)

available_models = []
for m in genai.list_models():
    if "generateContent" in getattr(m, "supported_generation_methods", []):
        available_models.append(m.name)

print("--- KULLANILABİLİR MODELLER ---")
for name in available_models:
    print(name)
print("-------------------------------")

preferred_models = [
    "models/gemini-3.6-flash",
    "gemini-3.6-flash",
    "models/gemini-2.5-flash",
    "gemini-2.5-flash",
]

MODEL_NAME = next(
    (name for name in preferred_models if name in available_models),
    available_models[0] if available_models else "gemini-3.6-flash",
)

model = genai.GenerativeModel(MODEL_NAME)



app = FastAPI(title="Buzdolabı Asistanı API")

# ...existing code...

class RecipeRequest(BaseModel):
    ingredients: List[str]

@app.get("/")
def read_root():
    return {"message": "Buzdolabı Asistanı Backend Çalışıyor!"}

@app.get("/foods")
def get_available_foods():
    return {"categories": FOOD_DATABASE}

@app.post("/get-recipe")
def get_recipe(request: RecipeRequest):
    total_calories = 0
    total_protein = 0.0
    total_carbs = 0.0
    total_fat = 0.0
    selected_names = []

    for category, items in FOOD_DATABASE.items():
        for key in request.ingredients:
            if key in items:
                food_info = items[key]
                total_calories += food_info["calories"]
                total_protein += food_info["protein"]
                total_carbs += food_info["carbs"]
                total_fat += food_info["fat"]
                selected_names.append(food_info["name"])

    return {
        "success": True,
        "selected_ingredients": selected_names,
        "nutrients": {
            "calories": total_calories,
            "protein": round(total_protein, 1),
            "carbs": round(total_carbs, 1),
            "fat": round(total_fat, 1)
        },
        "recipe_suggestion": f"Seçtiğiniz malzemelerle ({', '.join(selected_names)}) toplam {total_calories} kalorilik harika bir öğün hazırlayabilirsiniz!"
    }

@app.post("/random-recipe")
def get_random_recipe(request: RecipeRequest):
    if not request.ingredients:
        return {
            "success": False,
            "recipe_suggestion": "Dolabında hiç malzeme yok! Önce dolabına birkaç malzeme eklemelisin."
        }

    sample_count = min(len(request.ingredients), random.randint(2, 4))
    random_ingredients = random.sample(request.ingredients, sample_count)
    return get_recipe(RecipeRequest(ingredients=random_ingredients))

@app.get("/test-gemini")
def test_api():
    try:
        response = model.generate_content("Merhaba, bana sadece 2 kelime ile 'Bağlantı başarılı' yaz.")
        return {"mesaj": response.text}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Gemini API hatası: {exc}")