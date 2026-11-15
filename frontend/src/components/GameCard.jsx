function GameCard({ game }) {
    return (
        <article className="game-card">
            <div className="game-image-container">
                {game.image_url ? (
                    <img
                        src={game.image_url || '/fallback-game.png'}
                        alt={game.name}
                        className="game-image"
                    />
                ) : (
                    <div className="game-image-placeholder">
                        Artwork unavailable
                    </div>
                )}

                <span className={`status-badge ${game.status.toLowerCase().replaceAll(' ', '-')}`}>
                    {game.status}
                </span>
            </div>

            <div className="game-info">
                <div className="game-title-row">
                    <h3>{game.name}</h3>
                    <span className="game-rating">★ {game.rating}</span>
                </div>

                <p className="game-genre">{game.genre}</p>
            </div>
        </article>
    )
}

export default GameCard
