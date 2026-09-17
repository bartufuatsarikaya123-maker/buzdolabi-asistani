from fastapi import Request
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

FOOD_DATABASE = {
  "Süt Ürünleri ve Peynirler": {
        "beyaz_peynir": {"name": "Beyaz Peynir (100g)", "calories": 264, "protein": 14.0, "carbs": 1.2, "fat": 22.0},
        "lor_peyniri": {"name": "Lor Peyniri (100g)", "calories": 98, "protein": 15.0, "carbs": 3.5, "fat": 2.5},
        "kasar_peyniri": {"name": "Kaşar Peyniri (100g)", "calories": 404, "protein": 25.0, "carbs": 1.5, "fat": 33.0},
        "dil_peyniri": {"name": "Dil Peyniri (100g)", "calories": 285, "protein": 23.0, "carbs": 1.5, "fat": 20.0},
        "yogurt": {"name": "Yoğurt (100g)", "calories": 61, "protein": 3.5, "carbs": 4.7, "fat": 3.3}
    },
    "Protein Kaynaklari": {
        "tavuk_gogsu": {"name": "Tavuk Göğsü (100g)", "calories": 165, "protein": 31.0, "carbs": 0.0, "fat": 3.6},
        "yumurta": {"name": "Yumurta (1 Adet)", "calories": 78, "protein": 6.5, "carbs": 0.6, "fat": 5.5},
        "kiyma": {"name": "Dana Kıyma (100g)", "calories": 250, "protein": 26.0, "carbs": 0.0, "fat": 15.0},
        "ton_baligi": {"name": "Ton Balığı Konserve (100g)", "calories": 116, "protein": 26.0, "carbs": 0.0, "fat": 1.0},
        "hindi_eti": {"name": "Hindi Eti (100g)", "calories": 135, "protein": 30.0, "carbs": 0.0, "fat": 1.0}
    },
    "Sebzeler": {
        "domates": {"name": "Domates (100g)", "calories": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2},
        "patates": {"name": "Patates (100g)", "calories": 77, "protein": 2.0, "carbs": 17.5, "fat": 0.1},
        "sogan": {"name": "Soğan (100g)", "calories": 40, "protein": 1.1, "carbs": 9.3, "fat": 0.1},
        "biber": {"name": "Biber (100g)", "calories": 20, "protein": 0.9, "carbs": 4.6, "fat": 0.2},
        "ispanak": {"name": "Ispanak (100g)", "calories": 23, "protein": 2.9, "carbs": 3.6, "fat": 0.4},
        "salatalik": {"name": "Salatalık (100g)", "calories": 15, "protein": 0.6, "carbs": 3.6, "fat": 0.1}
    },
    "Kiler ve Tahillar": {
        "yulaf_ezmesi": {"name": "Yulaf Ezmesi (100g)", "calories": 389, "protein": 16.9, "carbs": 66.3, "fat": 6.9},
        "makarna": {"name": "Makarna Kuru (100g)", "calories": 131, "protein": 5.0, "carbs": 25.0, "fat": 1.1},
        "pirinc": {"name": "Pirinç (100g)", "calories": 130, "protein": 2.7, "carbs": 28.0, "fat": 0.3},
        "mercimek": {"name": "Kuru Mercimek (100g)", "calories": 352, "protein": 24.6, "carbs": 63.4, "fat": 1.1},
        "ekmek": {"name": "Tam Buğday Ekmeği (1 Dilim)", "calories": 75, "protein": 4.0, "carbs": 12.5, "fat": 1.0}
    },
    "Yaglar ve Soslar": {
        "zeytinyagi": {"name": "Zeytinyağı (1 Yemek Kaşığı)", "calories": 119, "protein": 0.0, "carbs": 0.0, "fat": 13.5},
        "tereyagi": {"name": "Tereyağı (1 Tatlı Kaşığı)", "calories": 72, "protein": 0.1, "carbs": 0.0, "fat": 8.1},
        "aycicek_yagi": {"name": "Ayçiçek Yağı (1 Yemek Kaşığı)", "calories": 119, "protein": 0.0, "carbs": 0.0, "fat": 13.5},
        "domates_salcasi": {"name": "Domates Salçası (1 Yemek Kaşığı)", "calories": 20, "protein": 1.0, "carbs": 4.0, "fat": 0.1},
        "biber_salcasi": {"name": "Biber Salçası (1 Yemek Kaşığı)", "calories": 25, "protein": 1.1, "carbs": 4.5, "fat": 0.5}
    }
}
class RecipeRequest(BaseModel):
    ingredients: List[str]

@app.get("/")
def read_root():
    return {"message": "Buzdolabı Asistanı Backend Çalışıyor!"}

@app.get("/foods")
def get_available_foods():
    return {"categories": FOOD_DATABASE}

@app.post("/get-recipe-nutrients")
def get_recipe_nutrients(request: RecipeRequest):
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
    return get_recipe_nutrients(RecipeRequest(ingredients=random_ingredients))

@app.get("/test-gemini")
def test_api():
    try:
        response = model.generate_content("Merhaba, bana sadece 2 kelime ile 'Bağlantı başarılı' yaz.")
        return {"mesaj": response.text}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Gemini API hatası: {exc}")

@app.post("/get-recipe")
async def generate_recipe(request: Request):
    # React Native'den gelen malzeme listesini alıyoruz
    data = await request.json()
    ingredients = data.get("ingredients", [])
    
    # Eğer liste boş gelirse uyaralım
    if not ingredients:
        return {"recipe_suggestion": "Dolabında hiç malzeme yok gibi görünüyor. Önce birkaç malzeme eklemelisin!"}
    
    # Malzemeleri virgülle ayrılmış bir metne çeviriyoruz (Örn: "Elma, Süt, Yulaf")
    ingredients_text = ", ".join(ingredients)
    
    # Prompt Engineering (Modele vereceğimiz şef rolü ve kurallar)
    prompt = f"""
    Sen yaratıcı, pratik ve samimi bir mutfak asistanısın. 
    Kullanıcının buzdolabındaki malzemeler şunlar: {ingredients_text}.
    
    Görevlerin:
    1. Sadece bu malzemeleri ve evde her zaman bulunabilecek temel kiler ürünlerini (tuz, karabiber, zeytinyağı, su vb.) kullanarak yapılabilecek en iyi 1 (bir) tarifi öner.
    2. Yemeğe iştah açıcı bir isim ver.
    3. Malzemeleri ve adım adım yapılışını kısa, net ve anlaşılır bir şekilde listele.
    4. Cevabın doğrudan tarifle başlasın, gereksiz giriş cümleleri kullanma.
    """
    
    try:
        # Gemini 3.5 Flash modeline prompt'u gönderiyoruz
        response = model.generate_content(prompt)
        
        # Gelen cevabı React Native'in beklediği formatta döndürüyoruz
        return {"recipe_suggestion": response.text}
        
    except Exception as e:
        print(f"Yapay Zeka Hatası: {e}")
        return {"recipe_suggestion": "Şu an mutfakta küçük bir yangın var (Sunucu Hatası), lütfen birazdan tekrar dene!"}