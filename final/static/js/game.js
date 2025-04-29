const socket = io();

// Join the game room as soon as game.html loads
const currentGameId = window.location.pathname.split('/').filter(Boolean).pop();
socket.emit('join_game', { game_id: currentGameId });

//root.html variables
const game_id = document.getElementById('game_id');
const newGameButton = document.getElementById('newGameButton'); 
const joinButton = document.getElementById('joinButton'); 
const joinForm = document.getElementById('joinForm');

//game.html variables
const inputUsername = document.getElementById('username');
const playersTable = document.getElementById('players');

if (newGameButton) {
	newGameButton.addEventListener('click', newGame);
}

function newGame() { //create new game
	fetch ('/new/')
	.then(response => {
		if (response.redirected) {
			window.location.href = response.url;
		} else {
			console.log("Error creating game.");
		}
	});
}

if (joinForm) { //add an event listener to grab the game id for joining a game
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

function addPlayer() { //large function for adding a player
	const newPlayer = inputUsername.value.trim();
	const gameID = window.location.pathname.split('/').filter(Boolean).pop();
	
	//logic to add player to the database
	if (!newPlayer) {
		console.log("Username required.");
		return;
	}
	
	if (newPlayer && gameID) {
		fetch ("/add_player/", {
			method: "POST", 
			headers: {
				'Content-Type': "application/json"
			},
			body: JSON.stringify({ username: newPlayer, game_id: gameID })
		})
		.then(res => res.json())
		.then(data => {
				console.log(data.message);
				
				//socket to add the player into the table on game.html live
				socket.emit('player_joined', { username: newPlayer, game_id: gameID });
	
				inputUsername.value = '';
		});
	}
}

socket.on('player_joined', ({ username, game_id, score }) => { //adds the joined player to the table on the join menu
	const currentGameID = window.location.pathname.split('/').filter(Boolean).pop();
	
	if (game_id !== currentGameID) return;
	
	const newRow = document.createElement('tr');
	newRow.innerHTML = `<td>${username}</td><td>${score}</td>`;
	playersTable.querySelector('tbody').appendChild(newRow);
});

document.addEventListener('DOMContentLoaded', () => { //adds all joined players to the table upon loading the game
	const gameID = window.location.pathname.split('/').filter(Boolean).pop();

	fetch(`/players/${gameID}`)
		.then(res => res.json())
		.then(usernames => {
			if (Array.isArray(usernames)) {
				const tbody = playersTable.querySelector('tbody');
				usernames.forEach(player => {
					const row = document.createElement('tr');
					row.innerHTML = `<td>${player.username}</td><td>${player.score}</td>`;
					tbody.appendChild(row);
				});
			}
		})
		.catch(err => console.error("Failed to fetch players:", err));
});