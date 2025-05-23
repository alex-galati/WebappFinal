//DEVELOPER'S NOTE: If all names don't appear on the scoreboard the first time, try closing the tabs and reopening them. That seems to work for some reason.
const socket = io();

// Join the game room as soon as game.html loads
const currentGameId = window.location.pathname.split('/').filter(Boolean).pop();

if (currentGameId && currentGameId.length === 16) {
	socket.emit('join_game', { game_id: currentGameId });
}

//root.html variables
const game_id = document.getElementById('game_id');
const newGameButton = document.getElementById('newGameButton'); 
const joinButton = document.getElementById('joinButton'); 
const joinForm = document.getElementById('joinForm');

//game.html variables
const inputUsername = document.getElementById('username');
const playersTable = document.getElementById('players');

let currentQuestion = 1;
let currentUsername = null;

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

function startGame(){
	socket.emit('start_game', { game_id: currentGameId });
}

function handleStartGame(){
	const card = document.getElementById("qcard");
	card.classList.add("show");

	const pregameStuff = document.getElementById("pre-game");
	if (pregameStuff) {
		Array.from(pregameStuff.children).forEach(child => {
			child.classList.add("hidden");
			child.classList.remove("show");
		});
		pregameStuff.remove();
	}

	currentQuestion = 1;
	nextQuestion();
}

socket.on('start_game', () => {
	handleStartGame();
});

function nextQuestion() {
	const card = document.getElementById("qcard");
	const title = card.querySelector('.card-title');
	const content = card.querySelector('.card-text');

	const question = questionData[currentQuestion.toString()][0];
	const correctAnswer = questionData[currentQuestion.toString()][1];

	title.innerHTML = `Question #${currentQuestion}`;
	content.innerHTML = question;
	
	document.querySelectorAll('input[name="radioDefault"]').forEach(r => r.checked = false); //clearing previously selected radio buttons for the next question
}

if (currentGameId && currentGameId.length === 16) {
	document.getElementById('submitAnswer').addEventListener('click', function() {
		const selectedOption = document.querySelector('input[name="radioDefault"]:checked');
		if (!selectedOption) {
			alert("Please select an answer.");
			return;
		}
		const userAnswer = selectedOption.value;
		socket.emit('submit_answer', {
			game_id: currentGameId,
			username: currentUsername,
			question_number: currentQuestion,
			answer: userAnswer
		});
	});
}

if (joinForm) { //add an event listener to grab the game id for joining a game
	joinForm.addEventListener('submit', function(e) {
		e.preventDefault();
		const trimmedGameID = game_id.value.trim();
		const IDLength = trimmedGameID.length;
		console.log(trimmedGameID);
		console.log(IDLength);
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
	
	currentUsername = newPlayer;

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

socket.on('all_answers_received', (data) => { //function to check if all players have answered the current question
	const { correct_answer, answers, question_number, updated_scores } = data;

	alert(`Correct answer: ${correct_answer}`); //popup with correct answer

	updated_scores.forEach(({ username, score }) => { 
		const rows = playersTable.querySelectorAll('tbody tr');
		rows.forEach(row => {
			const nameCell = row.children[0];
			if (nameCell.textContent === username) {
				row.children[1].textContent = score;
			}
		});
	});	
	
	const tbody = playersTable.querySelector('tbody'); //sorting tables by descending scores.
	const rowsArray = Array.from(tbody.querySelectorAll('tr'));
	
	rowsArray.sort((a, b) => {
		const scoreA = parseInt(a.children[1].textContent, 10);
		const scoreB = parseInt(b.children[1].textContent, 10);
		return scoreB - scoreA
	});
	
	rowsArray.forEach(row => tbody.appendChild(row));
	
	currentQuestion++;
	if (questionData[currentQuestion.toString()]) {
		nextQuestion();
	} else { //If no more questions, remove question card and show the game over card
		document.getElementById('qcard').classList.remove('show');
		document.getElementById('qcard').classList.add('hidden');
		
		const gameOverScreen = document.getElementById('gcard');
		gameOverScreen.style.display = 'block';
		
		const rows = playersTable.querySelectorAll('tbody tr');
		let topPlayer = null;
		let topScore = -1;
		
		rows.forEach(row => {
			const username = row.children[0].textContent;
			const score = parseInt(row.children[1].textContent, 10);
			if (score > topScore) {
				topScore = score;
				topPlayer = username
			}
		});
		const winnerText = document.getElementById('winnerText');
		if (topPlayer) {
			winnerText.textContent = `The winner is ${topPlayer} with ${topScore} point(s)!`;
		}
	}
});

document.addEventListener('DOMContentLoaded', () => { //adds all joined players to the table upon loading the game
	if (playersTable){
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
				
				const sortedRows = Array.from(tbody.querySelectorAll('tr')).sort((a, b) => { //sort by descending score upon loading the DOM
					return parseInt(b.children[1].textContent) - parseInt(a.children[1].textContent);
				});
				sortedRows.forEach(row => tbody.appendChild(row));
			}
		})
		.catch(err => console.error("Failed to fetch players:", err));
	}
});
