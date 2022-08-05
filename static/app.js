const BASE_URL = "https://api.spoonacular.com/recipes/findByNutrients"
API_KEY = "16a0b68042a34d6c85b194f9348ecd9e"

$(document).on("click", "#fav-btn", async function (evt) {
    evt.preventDefault();

    const id = $(this).data('id');

    if ($(this).text() === "Remove from favorites") {
        await axios.delete(`/users/favorites/delete/${id}`)
        $(this).text("Add to favorites")
        $(this).removeClass('btn-danger')
        $(this).addClass('btn-success')
    } else {
        await axios.get(`/users/favorites/add/${id}`)
        $(this).text("Remove from favorites")
        $(this).removeClass('btn-success')
        $(this).addClass('btn-danger')
    }


});

$("#bmr-button").on('click', async function (evt) {
    evt.preventDefault();

    let height = $("#height").val();
    let weight = $("#weight").val();
    let age = $("#age").val();
    let gender = $("#gender").val();
    let activity = $("#activity").val();
    let bmr = 0;

    let bmrResult = $("#bmr-result")

    if (gender === "M") {
        bmr = Math.round(((10 * weight * 0.45359237) + (6.25 * height * 2.54) - (5 * age) + 5) * activity);
    } else {
        bmr = Math.round(((10 * weight * 0.45359237) + (6.25 * height * 2.54) - (5 * age) - 161) * activity);
    }
    bmrResult.empty();
    bmrResult.append(`<h5 class="mt-5 fw-bolder fs-3">BMR:</h5><p class="fs-3 ">${bmr} kcal</p>`);
});

$("#recipe-form").on("submit", async function handleSearch(evt) {
    evt.preventDefault();

    let query = $("#recipe-query").val();
    if (!query) return;

    let recipes = await searchRecipes(query);

    populateRecipes(recipes);
});

async function searchRecipes(query) {

    const response = await axios.get(BASE_URL,
        {
            params: {
                'query': query,
                'apiKey': API_KEY,
                'minProtein': 10
            }
        });
    let recipes = response.data.map(result => {
        let recipe = result;
        return {
            id: recipe.id,
            title: recipe.title,
            image: recipe.image,
            calories: recipe.calories,
            fat: recipe.fat,
            carbs: recipe.carbs,
            protein: recipe.protein
        };
    });

    return recipes;
}

function populateRecipes(recipes) {
    const $recipesList = $("#recipes-list");
    $recipesList.empty();
    let $item

    for (let recipe of recipes) {
        if (logged_on === 'None') {
            $item = $(
                `
               <div class="card">
                <img class="card-img-top cover container-fluid" src="${recipe.image}">
                 <div class="card-body">
                   <h5 class="card-title">${recipe.title}</h5>
                   <div>
                   <p class="card-text">Calories: ${recipe.calories} Fat: ${recipe.fat} Carbs: ${recipe.carbs} Protein: ${recipe.protein}</p>
                   <p class="card-text"><a href="recipes/${recipe.id}" >Go to Recipe!</a></p>
                 </div>
               </div>
             
            `);
        } else {


            if (favorites.includes(`${recipe.id}`)) {
                $item = $(
                    `
               <div class="card">
                <img class="card-img-top cover container-fluid" src="${recipe.image}">
                 <div class="card-body">
                   <h5 class="card-title">${recipe.title}</h5>
                   <div>
                   <p class="card-text">Calories: ${recipe.calories} Fat: ${recipe.fat} Carbs: ${recipe.carbs} Protein: ${recipe.protein}</p>
                   <p class="card-text"><a href="recipes/${recipe.id}" >Go to Recipe!</a></p>
                   <p class="card-text"><button class="btn btn-danger btn-sm" id="fav-btn" data-id="${recipe.id}">Remove from favorites</button></p>
                 </div>
               </div>
             
            `);
            } else {
                $item = $(
                    `
            <div class="card">
                <img class="card-img-top cover container-fluid" src="${recipe.image}">
                <div class="card-body">
                <h5 class="card-title">${recipe.title}</h5>
                <div>
                <p class="card-text">Calories: ${recipe.calories} Fat: ${recipe.fat} Carbs: ${recipe.carbs} Protein: ${recipe.protein}</p>
                <p class="card-text"><a href="recipes/${recipe.id}" >Go to Recipe!</a></p>
                <p class="card-text"><button class="btn btn-success btn-sm" id="fav-btn" data-id="${recipe.id}">Add to favorites</button></p>
                </div>
            </div>
            
            `);
            }
        }
        $recipesList.append($item);
    }
}

