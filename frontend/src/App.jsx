import './App.css'
import games from './data/games'
import GameCard from './components/GameCard'
import { useState } from 'react'

function App() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedStatus, setSelectedStatus] = useState('All Games')

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
            <strong>24</strong>
          </div>
          <div className="stat-card">
            <span>Playing</span>
            <strong>3</strong>
          </div>
          <div className="stat-card">
            <span>Completed</span>
            <strong>12</strong>
          </div>
          <div className="stat-card">
            <span>Want to Play</span>
            <strong>9</strong>
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
