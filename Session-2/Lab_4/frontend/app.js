// app.js

// Hidden flag – the CSTI exploit must access this variable
const FLAG = "GCDXN7{matb9ach_t7t_les_var_fles_template_abatal}";

// Insecure template renderer
function renderGreeting() {
    const userInput = document.getElementById("username").value;

    const template = "Hello " + userInput;

    try {
        const output = Mustache.render(template);

        document.getElementById("output").innerHTML = output;

    } catch (e) {
        document.getElementById("output").innerHTML = "Error rendering template.";
    }
}
