//this is chatgpt code. please proofread later

function updateFormAction() {
    const gameId = document.getElementById('gameId').value;
    document.getElementById('joinForm').action = `/join/${gameId}`;
}

