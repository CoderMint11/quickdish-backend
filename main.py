from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import openai

from fastapi.middleware.cors import CORSMiddleware

import os

# Get API key from Replit secrets
openai.api_key = os.environ.get('OPENAI_API_KEY')

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Allow any website to use this API (including Wix)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "https://*.wix.com", "https://*.wixsite.com", "https://*.editorx.com", "https://*.wixstudio.io"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


class RecipeRequest(BaseModel):
    dish_name: str
    servings: int
    complexity: str
    category: str
    dietary: str


@app.post("/get-ingredients")
async def get_ingredients(data: RecipeRequest):
    complexity_guide = {
        "easy": "Make it simple and quick to prepare, using minimal ingredients and steps.",
        "medium": "Use standard cooking techniques and moderate preparation time.",
        "complex": "Include more elaborate techniques and ingredients for an impressive result."
    }

    category_prefix = "" if data.category == "any" else f"Create a {data.category} recipe for"
    dietary_guide = "" if data.dietary == "none" else f"\nMake sure the recipe is {data.dietary}."
    
    prompt = f"""
    {category_prefix} "{data.dish_name}" serving {data.servings} people.
    {complexity_guide[data.complexity]}{dietary_guide}
    Include:
    1. Total cooking time at the beginning
    2. Basic nutritional information (calories, protein, carbs, fat)
    3. Difficulty level (1-5 stars)
    4. Equipment needed
    
    Format the response as follows:
    
    Total Time: [Preparation + Cooking time]
    
    [Recipe Name]
    Servings: [number]
    Preparation Time: [time]
    
    INGREDIENTS:
    • List each ingredient on a new line with measurements
    
    INSTRUCTIONS:
    1. First step
    2. Second step
    (etc.)
    
    Do not use asterisks or markdown formatting. Use plain text with clear sections.
    """

    response = openai.chat.completions.create(model="gpt-4",
                                              messages=[{
                                                  "role": "user",
                                                  "content": prompt
                                              }],
                                              temperature=0.7)

    ingredients = response.choices[0].message.content
    return {"ingredients": ingredients}
