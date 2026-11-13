const API_URL = 'http://127.0.0.1:8000'

export async function getGames() {
    const response = await fetch(`${API_URL}/games`)

    if (!response.ok) {
        throw new Error('Failed to fetch games')
    }

    return response.json()
}