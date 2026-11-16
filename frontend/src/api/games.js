const API_URL = 'http://127.0.0.1:8000'

export async function getGames() {
    const response = await fetch(`${API_URL}/games`)

    if (!response.ok) {
        throw new Error('Failed to fetch games')
    }

    return response.json()
}

export async function getGameStats() {
    const response = await fetch(`${API_URL}/games/stats`)

    if (!response.ok) {
        throw new Error('Failed to fetch game statistics')
    }

    return response.json()
}

export async function searchGames(query) {
    const response = await fetch(
        `${API_URL}/games/search?query=${encodeURIComponent(query)}`
    )

    if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to search games')
    }

    return response.json()
}

export async function addGame(game) {
    const response = await fetch(`${API_URL}/games`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(game),
    })

    if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to add game')
    }

    return response.json()
}
