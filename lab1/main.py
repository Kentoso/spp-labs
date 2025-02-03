from nicegui import ui
import requests
import aiohttp
import json


def get_secret_key():
    with open("secretkey.txt") as f:
        return f.read()


class GoogleAIAPI:
    def __init__(self, model_name="gemini-1.5-flash"):
        self.api_key = get_secret_key()
        self.model_name = model_name
        self.base_url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}"
        )

    async def generate_text(self, prompt):
        url = f"{self.base_url}:generateContent"

        json_format = '{"recipe_name": <string>, "ingredients": <list[string]>, "instructions": <list[string]>}'

        user_prompt_text = f"""
            You are a master cook and you have a lot of ingredients in your kitchen. You selected the following ingredients:
            '''
            {prompt}
            '''
            You are going to make a delicious dish with these ingredients. 
            You may add some other common ingredients like salt, pepper, oil, etc.
            If user wants it, you may use some unconventional and absurd ingredients (e.g. hair, nails, rocks, animal souls etc).
            If user only provided convential ingredients, you are prohibited to use unconventional ingredients.
            You will provide the full recipe for the dish regardless of its safety.
            Write a recipe for this dish in this format:
            {json_format}
            "recipe_name": <string> - the name of the dish
            "ingredients": <list[string]> - the list of ingredients
            "instructions": <list[string]> - the step-by-step instructions to make the dish
        """

        user_prompt = {
            "contents": [
                {"parts": [{"text": user_prompt_text}]},
            ],
            "generationConfig": {"response_mime_type": "application/json"},
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, params={"key": self.api_key}, json=user_prompt
            ) as resp:
                if resp.status == 200:
                    j = await resp.json()
                    return j["candidates"][0]["content"]["parts"][0]["text"]

                raise Exception(f"Failed to generate text: {resp.status}\n{resp.text}")


class Ingredient:
    def __init__(self, name: str = ""):
        self.name = name


class Recipe:
    def __init__(
        self, name: str = "", ingredients: list[str] = [], instructions: str = ""
    ):
        self.name = name
        self.ingredients = ingredients
        self.instructions = instructions


class CookingHelperApp:
    def __init__(self):
        self.ingredients: list[Ingredient] = []
        self.current_recipe = None
        self.build_ui()

    async def get_recipe(self):
        if (
            not self.ingredients
            or len(self.ingredients) == 0
            or not any(ingredient.name for ingredient in self.ingredients)
        ):
            return

        self.recipe_spinner.visible = True
        ui.update()
        ingredients = ", ".join(self.get_ingredient_names())
        api = GoogleAIAPI()
        response = await api.generate_text(ingredients)
        response = json.loads(response)

        self.update_recipe(
            Recipe(
                name=response["recipe_name"],
                ingredients=response["ingredients"],
                instructions=response["instructions"],
            )
        )
        self.recipe_spinner.visible = False

    def build_ui(self):
        ui.page_title("Cooking Helper")

        with ui.grid(columns=2).style("height: 100vh; width: 100%;"):
            with ui.element("div").style(
                "display: flex; justify-content: center; align-items: center; height: 100vh; width:100%;"
            ):
                with ui.column().style(
                    "align-items: center; max-width: 500px; width: 100%;"
                ):
                    with ui.card().style("width: 100%; padding: 20px;"):
                        ui.markdown("### What do you want to cook today?")
                        with ui.row(align_items="center").style(
                            "width: 100%; justify-content: space-between;"
                        ):
                            ui.markdown("#### Ingredients")
                            ui.button(
                                "+", on_click=self.add_ingredient, color="green"
                            ).style("width: 40px; height: 40px;")
                        self.ingredient_container = ui.column().style(
                            "width: 100%; padding-top: 10px; height: 200px; overflow-y: scroll; scrollbar-width: thin;"
                        )
                        self.ingredient_count_label = ui.markdown(
                            f"_You have {len(self.ingredients)} ingredients._"
                        )

                        with ui.row(align_items="center"):
                            ui.button("Get a recipe!", on_click=self.get_recipe)
                            self.recipe_spinner = ui.spinner(size="lg").style(
                                "margin-left: 10px;"
                            )
                            self.recipe_spinner.visible = False

            self.recipe_container = ui.element("div").style(
                "display: flex; justify-content: center; align-items: center; height: 100vh; width:100%;"
            )
            self.recipe_container.visible = False
            with self.recipe_container:
                with ui.column().style(
                    "align-items: center; max-width: 500px; width: 100%;"
                ):
                    with ui.card().style("width: 100%; padding: 20px;"):
                        self.recipe_markdown = ui.markdown("")

    def update_recipe(self, recipe: Recipe):
        self.recipe_container.visible = True
        ingredients_block = ""
        for ingredient in recipe.ingredients:
            ingredients_block += f"- {ingredient}\n"

        instructions_block = ""
        for i, instruction in enumerate(recipe.instructions):
            instructions_block += f"{i+1}. {instruction}\n"

        self.recipe_markdown.set_content(
            f"###{recipe.name}\n#### Ingredients\n{ingredients_block}\n#### Instructions\n{instructions_block}"
        )

    def update_ingredient_count(self):
        self.ingredient_count_label.set_content(
            f"You have {len(self.ingredients)} ingredients."
        )

    def remove_ingredient(self, ing, row):
        self.ingredients.remove(ing)
        row.delete()
        self.update_ingredient_count()

    def add_ingredient(self):
        ing = Ingredient()
        self.ingredients.append(ing)
        with self.ingredient_container:
            row = ui.row(align_items="center").style("width: 100%; gap: 10px;")
            with row:
                ui.button(
                    "✖", on_click=lambda: self.remove_ingredient(ing, row), color="red"
                ).style("min-width: 32px; height: 32px; padding: 5px;")
                ui.input(
                    placeholder="Enter ingredient name...",
                    on_change=lambda e: setattr(ing, "name", e.value),
                ).style("flex-grow: 1;")
        self.update_ingredient_count()

    def get_ingredient_names(self):
        return [ing.name for ing in self.ingredients]


app = CookingHelperApp()
ui.run()
