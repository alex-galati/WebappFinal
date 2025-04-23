//const socket = io()
const game_id = document.getElementById('game_id')
const newGameButton = document.getElementById('newGameButton'); 
const joinButton = document.getElementById('joinButton'); 

if (newGameButton) {
	newGameButton.addEventListener('click', newGame);
}

function newGame() {
	fetch ('/new/')
	.then(response => {
		if (response.redirected) {
			window.location.href = response.url;
		} else {
			console.log("Error creating game.");
		}
	});
}

if (joinForm) {
	joinForm.addEventListener('submit', function(e) {
		e.preventDefault();
		const trimmedGameID = game_id.value.trim();
		const IDLength = trimmedGameID.length;
		if (trimmedGameID && IDLength == 16) {
			window.location.href = `/join/${trimmedGameID}/`;
		} else {
			console.log("Please enter a valid game ID");
		}
		game_id.value = '';
	});
}