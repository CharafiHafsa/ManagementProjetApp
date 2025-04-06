// Function to validate the password strength and check if passwords match
function validatePassword() {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;

    const passwordRequirements = document.getElementById('password-requirements');
    const lengthRegex = /.{8,}/;  // Minimum 8 characters
    const uppercaseRegex = /[A-Z]/;  // At least one uppercase letter
    const lowercaseRegex = /[a-z]/;  // At least one lowercase letter
    const numberRegex = /\d/;  // At least one number
    const specialRegex = /[!@#$%^&*(),.?":{}|<>]/;  // At least one special character

    // Show the requirements list if password is empty or weak
    if (password === "" || !lengthRegex.test(password) || !uppercaseRegex.test(password) ||
        !lowercaseRegex.test(password) || !numberRegex.test(password) || !specialRegex.test(password)) {
        passwordRequirements.style.display = 'block';
    } else {
        passwordRequirements.style.display = 'none';
    }

    // Check each requirement and update the color
    document.getElementById('length').style.color = lengthRegex.test(password) ? 'green' : 'red';
    document.getElementById('uppercase').style.color = uppercaseRegex.test(password) ? 'green' : 'red';
    document.getElementById('lowercase').style.color = lowercaseRegex.test(password) ? 'green' : 'red';
    document.getElementById('number').style.color = numberRegex.test(password) ? 'green' : 'red';
    document.getElementById('special').style.color = specialRegex.test(password) ? 'green' : 'red';

    // Check if passwords match only if both are filled
    const confirmPasswordError = document.getElementById('confirm-password-error');
    if (password !== confirmPassword && password !== "" && confirmPassword !== "") {
        confirmPasswordError.style.display = 'block';  // Show error if passwords don't match
    } else {
        confirmPasswordError.style.display = 'none';  // Hide error if passwords match or one is empty
    }
}

// Add event listeners to check password on input
document.getElementById('password').addEventListener('input', validatePassword);
document.getElementById('confirm_password').addEventListener('input', validatePassword);

// Toggle password visibility
const togglePassword = document.getElementById('toggle-password');
const passwordField = document.getElementById('password');
togglePassword.addEventListener('click', function () {
    const type = passwordField.type === 'password' ? 'text' : 'password';
    passwordField.type = type;
    // Change the icon based on visibility
    togglePassword.innerHTML = type === 'password' ? 
        '<span class="iconify" data-icon="solar:eye-line-duotone" data-inline="false"></span>' : 
        '<span class="iconify" data-icon="solar:eye-closed-bold" data-inline="false"></span>';
});

// Toggle confirm password visibility
const toggleConfirmPassword = document.getElementById('toggle-confirm-password');
const confirmPasswordField = document.getElementById('confirm_password');
toggleConfirmPassword.addEventListener('click', function () {
    const type = confirmPasswordField.type === 'password' ? 'text' : 'password';
    confirmPasswordField.type = type;
    // Change the icon based on visibility
    toggleConfirmPassword.innerHTML = type === 'password' ? 
        '<span class="iconify" data-icon="solar:eye-line-duotone" data-inline="false"></span>' : 
        '<span class="iconify" data-icon="solar:eye-closed-bold" data-inline="false"></span>';
});