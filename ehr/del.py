        <section>
          <form method="post" enctype="multipart/form-data" class="text-xs">
              {% csrf_token %}
              <div class="md:flex md:flex-row justify-center md:gap-6 uppercase text-cyan-900 px-10">
                  {% for field in dispense_form.visible_fields %}
                          <div class="flex flex-row justify-center gap-2 text-center align-text-bottom ">
                            <div>
                              <label for="{{ field.id_for_label }}">{{ field.label }}</label>
                              {{ field }}
                            </div>
                              {% if field.errors %}
                              <div class="text-red-500 text-xs italic">
                                  {% for error in field.errors %}
                                  <p>{{ error }}</p>
                                  {% endfor %}
                              </div>
                              {% endif %}
                              {% endfor %}
                            </div>
                    <div class="">
                      <input type="submit" value="dispense" class="focus:opacity-10 uppercase focus:border-green-900 hover:bg-white hover:text-green-600 hover:border-2 hover:border-green-600 bg-green-700 text-white py-4 px-8 rounded shadow-lg hover:shadow-xl">
                    </div>
              </div>
          </form>
          {% if dispense_form.errors %}
          <div class="uk-alert-danger block text-xs uppercase text-rose-700 rounded-xl" uk-alert>
              <a href class="uk-alert-close font-bold" uk-close></a>
              <p>{{ dispense_form.errors }}</p>
          </div>
          {% endif %}
        </section>