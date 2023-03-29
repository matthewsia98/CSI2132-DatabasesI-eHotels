let customer_radio = document.querySelector("#customer-radio");
let employee_radio = document.querySelector("#employee-radio");
let extra_fields = document.querySelector("#employee-extra-fields");

if (!employee_radio.checked) {
  extra_fields.style.display = "none";
}

function show_employee_extra_fields() {
  if (employee_radio.checked) {
    extra_fields.style.display = "flex";
  } else {
    extra_fields.style.display = "none";
  }
}

customer_radio.addEventListener("click", show_employee_extra_fields);
employee_radio.addEventListener("click", show_employee_extra_fields);
