const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
const container = document.getElementById('container_signup_signin');

function signUpValidateForm() {
	const password = document.querySelector('input[name="sign-up-passwd"]').value;
	const password2 = document.querySelector('input[name="sign-up-passwd2"]').value;
	
	if (password !== password2) {
		asAlertMsg({
			type: "error",
			message: "Mật khẩu xác nhận không khớp",
			timer: 5000
		});
		return false;
	}
	
	if (password.length < 8) {
		asAlertMsg({
			type: "error", 
			message: "Mật khẩu phải có ít nhất 8 ký tự",
			timer: 5000
		});
		return false;
	}
	
	return true;
}

function signInValidateForm() {
	return true;
}

signUpButton.addEventListener('click', () => {
	container.classList.add('right-panel-active');
});

signInButton.addEventListener('click', () => {
	container.classList.remove('right-panel-active');
});