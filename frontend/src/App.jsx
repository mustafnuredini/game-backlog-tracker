import './App.css'
import GameCard from './components/GameCard'
import { useState, useEffect } from 'react'
import {
  getGames,
  getGameStats,
  searchGames,
  addGame
} from './api/games'

function App() {
  const [games, setGames] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showAddGame, setShowAddGame] = useState(false)
  const [gameQuery, setGameQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [searchLoading, setSearchLoading] = useState(false)
  const [addError, setAddError] = useState('')
  const [addingGameId, setAddingGameId] = useState(null)
  useEffect(() => {
    async function loadGames() {
      try {
        const [gamesData, statsData] = await Promise.all([
          getGames(),
          getGameStats()
        ])

        setGames(gamesData.games)
        setStats(statsData)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    loadGames()
  }, [])
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedStatus, setSelectedStatus] = useState('All Games')

  async function handleSearchGames() {
    if (!gameQuery.trim()) {
      setAddError('Please enter a game name.')
      return
    }

    setSearchLoading(true)
    setAddError('')
    setSearchResults([])

    try {
      const results = await searchGames(gameQuery)
      setSearchResults(results)
    } catch (err) {
      setAddError(err.message)
    } finally {
      setSearchLoading(false)
    }
  }

  async function handleAddGame(game) {
    setAddingGameId(game.rawg_id)
    setAddError('')

    try {
      const newGame = await addGame(game)

      setGames((currentGames) => [
        ...currentGames,
        newGame
      ])

      const updatedStats = await getGameStats()
      setStats(updatedStats)

      setSearchResults((currentResults) =>
        currentResults.filter(
          (result) => result.rawg_id !== game.rawg_id
        )
      )
    } catch (err) {
      setAddError(err.message)
    } finally {
      setAddingGameId(null)
    }
  }

  const filteredGames = games.filter((game) => {
    const matchesSearch = game.name
      .toLowerCase()
      .includes(searchTerm.toLowerCase())

    const matchesStatus =
      selectedStatus === 'All Games' || game.status === selectedStatus

    return matchesSearch && matchesStatus
  })
  return (
    <div className="app">
      <aside className="sidebar">
        <h2 className="logo">BACKLOG<span>.</span></h2>

        <p className="sidebar-label">MENU</p>

        <nav>
          <a className="nav-link active" href="#">Dashboard</a>
          <a className="nav-link" href="#">My Library</a>
          <a className="nav-link" href="#">Settings</a>
        </nav>

        <div className="sidebar-footer">
          <p>GAME BACKLOG TRACKER</p>
          <span>Built for gamers.</span>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">YOUR PERSONAL GAME LIBRARY</p>
            <h1>Dashboard</h1>
          </div>

          <div className="profile">G</div>
        </header>

        <section className="welcome">
          <p className="eyebrow">WELCOME BACK</p>
          <h2>Your next adventure awaits.</h2>
          <p>Keep track of what you're playing and what comes next.</p>
        </section>

        <section className="stats">
          <div className="stat-card">
            <span>Total Games</span>
            <strong>{stats?.total_games ?? 0}</strong>
          </div>
          <div className="stat-card">
            <span>Playing</span>
            <strong>{stats?.games_by_status?.['Playing'] ?? 0}</strong>
          </div>
          <div className="stat-card">
            <span>Completed</span>
            <strong>{stats?.games_by_status?.['Completed'] ?? 0}</strong>
          </div>
          <div className="stat-card">
            <span>Want to Play</span>
            <strong>{stats?.games_by_status?.['Want to Play'] ?? 0}</strong>
          </div>
        </section>

        <section className="library-section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">YOUR COLLECTION</p>
              <h2>Recently Added</h2>
            </div>

            <div className="library-controls">
              <input
                type="text"
                placeholder="Search games..."
                value={searchTerm}
                onChange={(event) => setSearchTerm(event.target.value)}
              />

              <select
                value={selectedStatus}
                onChange={(event) => setSelectedStatus(event.target.value)}
              >
                <option value="All Games">All Games</option>
                <option value="Playing">Playing</option>
                <option value="Completed">Completed</option>
                <option value="Want to Play">Want to Play</option>
              </select>
            </div>
          </div>

          <button
            className="add-game-button"
            onClick={() => {
              setShowAddGame(!showAddGame)
              setAddError('')
              setSearchResults([])
              setGameQuery('')
            }}
          >
            + Add Game
          </button>


          {showAddGame && (
            <div className="add-game-panel">
              <h3>Find a Game</h3>
              <p>Search RAWG's game database to add a title to your library.</p>

              <div className="add-game-search">
                <input
                  type="text"
                  placeholder="Search for a game..."
                  value={gameQuery}
                  onChange={(event) => setGameQuery(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter') {
                      handleSearchGames()
                    }
                  }}
                />

                <button
                  onClick={handleSearchGames}
                  disabled={searchLoading}
                >
                  {searchLoading ? 'Searching...' : 'Search'}
                </button>
              </div>

              {addError && (
                <p className="add-game-error">{addError}</p>
              )}

              <div className="search-results">
                {searchResults.map((game) => (
                  <div className="search-result-card" key={game.rawg_id}>
                    {game.image_url ? (
                      <img src={game.image_url} alt={game.name} />
                    ) : (
                      <div className="search-result-placeholder">
                        No artwork
                      </div>
                    )}

                    <div className="search-result-info">
                      <h4>{game.name}</h4>
                      <p>
                        {game.released || 'Release date unknown'}
                        {' · '}
                        ★ {game.rating ?? 'N/A'}
                      </p>
                    </div>

                    <button
                      onClick={() => handleAddGame(game)}
                      disabled={addingGameId === game.rawg_id}
                    >
                      {addingGameId === game.rawg_id ? 'Adding...' : 'Add'}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="game-grid">
            {filteredGames.length > 0 ? (
              filteredGames.map((game) => (
                <GameCard key={game.id} game={game} />
              ))
            ) : (
              <p className="no-results">No games found.</p>
            )}
          </div>
        </section>
      </main>
    </div>
  )
}

export default App
