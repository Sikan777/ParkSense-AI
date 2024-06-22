let searchForm = document.querySelector('.search-form');
//let shoppingCart = document.querySelector('.shopping-cart');
let navbar = document.querySelector('.navbar');
let loginForm = document.querySelector('.login-form');
let logoutForm = document.querySelector('.logout-form');
let signupForm = document.querySelector('.signup-form');


document.querySelector('#search-btn').onclick = () =>{
	searchForm.classList.toggle('active');
	//shoppingCart.classList.remove('active');
	loginForm.classList.remove('active');
	signupForm.classList.remove('active');
	navbar.classList.remove('active');
}



// document.querySelector('#cart-btn').onclick = () =>{
// shoppingCart.classList.toggle('active');
// searchForm.classList.remove('active');
// loginForm.classList.remove('active');
// signupForm.classList.remove('active');
// navbar.classList.remove('active');
// }



document.querySelector('#login-btn').onclick = () =>{
	loginForm.classList.toggle('active');
	searchForm.classList.remove('active');
	//shoppingCart.classList.remove('active');
	signupForm.classList.remove('active');
	navbar.classList.remove('active');
}



document.querySelector('#signup-btn').onclick = () =>{
	signupForm.classList.toggle('active');
	searchForm.classList.remove('active');
	//shoppingCart.classList.remove('active');
	loginForm.classList.remove('active');
	navbar.classList.remove('active');
}

document.querySelector('#logout-btn').onclick = () =>{
	logoutForm.classList.toggle('active');
	signupForm.classList.remove('active');
	searchForm.classList.remove('active');
	//shoppingCart.classList.remove('active');
	loginForm.classList.remove('active');
	navbar.classList.remove('active');
}



document.querySelector('#menu-btn').onclick = () =>{
	navbar.classList.toggle('active');
	searchForm.classList.remove('active');
	//shoppingCart.classList.remove('active');
	loginForm.classList.remove('active');
	signupForm.classList.remove('active');
}

window.onscroll = () =>{
	searchForm.classList.remove('active');
	//shoppingCart.classList.remove('active');
	loginForm.classList.remove('active');
	signupForm.classList.remove('active');
	navbar.classList.remove('active');
}

var swiper = new Swiper(".product-slider", {
	loop:true,
	spaceBetween: 20,
	autoplay: {
		delay: 7500,
		disableOnInteraction: false,
	},
	centeredSlides: true,
	breakpoints: {
		0: {
			slidesPerView: 1,
		},
		768: {
			slidesPerView: 2,
		},
		1020: {
			slidesPerView: 3,
		},
	},
});

var swiper = new Swiper(".review-slider", {
	loop:true,
	spaceBetween: 20,
	autoplay: {
		delay: 7500,
		disableOnInteraction: false,
	},
	centeredSlides: true,
	breakpoints: {
		0: {
			slidesPerView: 1,
		},
		768: {
			slidesPerView: 2,
		},
		1020: {
			slidesPerView: 3,
		},
	},
});

let access_token;
document.addEventListener("DOMContentLoaded", function(){
	// /signup user
	
	let createAccountLink = document.querySelector('#signup-btn');
	createAccountLink.onclick = () =>{
		signupForm.classList.toggle('active');
	}
	
	signupForm.onsubmit = async (e) => {
		e.preventDefault();
		
		let username = document.getElementById('username').value;
		let email = document.getElementById('email').value;
		let password = document.getElementById('password').value;
		let phone_number = document.getElementById('phone_number').value;
		
		let userData = {
			username: username,
			email: email,
			password: password,
			phone_number: phone_number
		};
		
		await fetch('http://localhost:8000/api/auth/signup', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(userData)
		})
		.then(response => {
			if (response.ok) {
				// Обработка успешного ответа
				console.log("Пользователь успешно зарегистрирован.");
				alert("Registration successful!");
				window.location.href = 'index.html'; // Перенаправление на страницу Home
				} else {
				// Обработка ошибки
				return response.json().then(errorData => {
					console.error('Ошибка:', errorData.detail);
					alert(errorData.detail); // Показать сообщение об ошибке, если регистрация не удалась
				});
			}
		})
		.catch(error => {
			console.error('Ошибка:', error);
		});
	}
	
	// /login user
	document.querySelector('.login-form').addEventListener('submit', async function(event) {
		event.preventDefault();
		const formData = new FormData(this);
		const formDataJSON = Object.fromEntries(formData.entries());
		// const formData = new URLSearchParams();
		// for (const key in formDataJSON) {
		// formData.append(key, formDataJSON[key]);
		// }
		
		try {
			const response = await fetch('http://localhost:8000/api/auth/login', {
				method: 'POST',
				body: formData
			    //body: JSON.stringify(formDataJSON)
				//headers: {'Content-Type': 'application/x-www-form-urlencoded'},
				// mode: 'cors',
				// headers: {
				// 'Content-Type': 'application/json'
				// },
			});
			
			if (response.ok) {
				const data = await response.json();
				console.log(data); // Вывод ответа сервера
				access_token = data.access_token;
				console.log("Access Token:", access_token);
				console.log("Link Telegram:", data.link_telebot);
				
				
				
				// Скрыть форму login
				document.getElementById('login-form').style.display = 'none';
				// Скрыть кнопки login и signup
				document.getElementById('login-btn').style.display = 'none';
				document.getElementById('signup-btn').style.display = 'none';
				
				
				// Показать кнопку logout
				document.getElementById('logout-btn').style.display = 'inline-block';
				const usernameElement = document.getElementById('username-data');
				usernameElement.innerText = formData.get('username')
				;
				
				
				const telegramIcon = document.getElementById("telegram-icon");
				const linkT = data.link_telebot;  // Переменная link из Python передаётся в шаблон HTML
				telegramIcon.href = linkT;
				console.log(linkT)
				
				// window.location.href = 'http://localhost:8000/docs'; // Перенаправление на страницу Home
				} else {
				const errorData = await response.json();
				console.error(errorData); // Вывод ошибки
			}
			} catch (error) {
			console.error('Error:', error);
		}
	});
	
	// // /logout
	// Проверяем, есть ли сохраненная информация о входе пользователя в локальном хранилище
	const accessToken = localStorage.getItem('access_token');
	const refreshToken = localStorage.getItem('refresh_token');
	const username = localStorage.getItem('username');
	
	if (accessToken && refreshToken && username) {
		// Если есть информация о входе пользователя, скрываем форму входа и показываем кнопку с именем пользователя
		document.getElementById('login-btn').style.display = 'none';
		document.getElementById('logout-btn').style.display = 'inline-block';
		document.getElementById('username-data').innerText = formData.get('username');
		
		// Обработчик события для формы logout
		document.getElementById('logout-form').addEventListener('submit', async function(event) {
			event.preventDefault();
			try {
				const response = await fetch('http://localhost:8000/api/auth/logout', {
					method: 'POST',
					headers: {
						'Authorization': `Bearer ${access_token}`
					}
				});
				if (response.ok) {
					// Удаляем информацию о входе пользователя из локального хранилища
					localStorage.removeItem('accessToken');
					localStorage.removeItem('refreshToken');
					localStorage.removeItem('username');
					// показать и форму кнопки login и signup
					document.getElementById('login-form').style.display = 'inline-block';
					document.getElementById('logout-btn').style.display = 'none';
					document.getElementById('login-btn').style.display = 'inline-block';
					document.getElementById('signup-btn').style.display = 'inline-block';
					// Перезагружаем страницу после успешного выхода из системы
					window.location.reload();
					} else {
					const data = await response.json();
					console.error(data);
				}
				} catch (error) {
				console.error('Error:', error);
			}
		});
	}
	//create image
	
})

document.addEventListener("DOMContentLoaded", () => {
    const addPhotoBtnEntry = document.getElementById("addPhotoBtnEntry");
    const fileInputEntry = document.getElementById("fileInputEntry");
	const addPhotoBtnExit = document.getElementById("addPhotoBtnExit");
    const fileInputExit = document.getElementById("fileInputExit");
    const uploadedImagesSection = document.getElementById("uploadedImages");
	
    addPhotoBtnEntry.addEventListener("click", () => {
        fileInputEntry.click();
	});
	
	addPhotoBtnExit.addEventListener("click", () => {
        fileInputExit.click();
	});
	
	fileInputEntry.addEventListener("change", async (event) => {
        await handleUpload(event, 'http://127.0.0.1:8000/api/parking/entry');
	});
	
    fileInputExit.addEventListener("change", async (event) => {
        await handleUpload(event, 'http://127.0.0.1:8000/api/parking/exit');
	});
	
	async function handleUpload(event, apiEndpoint) {
		
		event.preventDefault();
		const photo = event.target.files[0];
		const descriptionInput = document.getElementById("description");
		const description = descriptionInput.value.trim();
		
		const formData = new FormData();
		formData.append("photo", photo);
		formData.append("description", description);
		
		descriptionInput.value = "";
		
		try {
			const response = await fetch(apiEndpoint, {
				method: 'POST',
				headers: {
					'Authorization': `Bearer ${access_token}`
				},
				body: formData
			});
			
			if (!response.ok) {
				throw new Error("Failed to upload image");
			}
			
			const imageData = await response.json();
			const imageUrl = imageData.image_url;
			console.log(imageData);
			console.log(imageUrl);
			
			const imageElement = document.createElement("img");
			imageElement.src = imageUrl;
			uploadedImagesSection.appendChild(imageElement);
            } catch (error) {
			console.error("Error uploading image:", error);
		}
	};
	
});




