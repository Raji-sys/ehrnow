<!-- {% extends 'base.html' %}
{% block title %}Surgery Bill{% endblock %}
{%block page_title%}<div class="flex justify-center"><a href="#"><i class="fa-solid fa-backward fa-2xl mr-4"></i></a>SURGERY BILL</div>{%endblock%}
{% block content %}
<form method="post" class="bg-white shadow-xl rounded px-4 pt-3 pb-4 text-xs mx-auto w-fit mt-1">
    {% csrf_token %}
    {{ formset.management_form }}
    <div class="grid md:grid-cols-1 p-1 gap-1 text-center ">
        {% for form in formset %}
        <div class=" p-2 border rounded shadow-md w-fit">
            <div class="flex justify-center">
                    <p class="text-left text-xs text-green-700">#{{ forloop.counter }}
                        {{ form }}
                    </p>
                    {% if form.non_field_errors %}
                        {% for error in form.non_field_errors %}
                            <p class="text-red-500 text-xs italic">{{ error }}</p>
                        {% endfor %}
                    {% endif %}
                </div>
            </div>
        {% endfor %}
    </div>
    <div class="flex items-center justify-center">
        <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline" type="submit">
            Save
        </button>
    </div>
</form>
<script>
    function initializePage() {
    function load_items(index) {
        const categoryId = document.getElementsByName(`form-${index}-category`)[0].value;
        const url = `/get_category/${categoryId}/`;
    
        fetch(url)
            .then(response => response.json())
            .then(data => {
                const itemSelect = document.getElementsByName(`form-${index}-item`)[0];
                itemSelect.innerHTML = '';  // Clear existing options
    
                data.items.forEach(item => {
                    const option = document.createElement('option');
                    option.value = item.id;
                    option.text = item.name;
                    itemSelect.add(option);
                });
            })
            .catch(error => console.error('Error:', error));
    }    
        // Event listener for category select elements in formset
        {% for form in formset %}
        document.getElementsByName('{{ form.category.html_name }}')[0].addEventListener('change', function() {
            load_items('{{ forloop.counter0 }}');
        });
        {% endfor %}
    }
    
    // Call the initializePage function when the page loads
    window.addEventListener('load', initializePage);
    
    </script>
    
{% endblock %} -->