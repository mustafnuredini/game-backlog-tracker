const STATUS_OPTIONS = [
    'Want to Play',
    'Playing',
    'Completed',
    'Dropped',
]

function GameCard({ game, onStatusChange, onDelete, onNotesChange, updating, deleting, updatingNotes }) {
    const [isEditingNotes, setIsEditingNotes] = useState(false)
    const [notesText, setNotesText] = useState(game.notes || '')

    const handleSaveNotes = () => {
        onNotesChange(game.id, notesText)
        setIsEditingNotes(false)
    }

    const handleCancelNotes = () => {
        setNotesText(game.notes || '')
        setIsEditingNotes(false)
    }

    const handleClearNotes = () => {
        setNotesText('')
    }

    const displayNotes = game.notes && game.notes.trim() !== ''

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

                <label className="game-status-control">
                    <span className="sr-only">Status for {game.name}</span>
                    <select
                        value={game.status}
                        disabled={updating}
                        onChange={(event) => onStatusChange(game.id, event.target.value)}
                    >
                        {STATUS_OPTIONS.map((status) => (
                            <option key={status} value={status}>
                                {status}
                            </option>
                        ))}
                    </select>
                </label>

                <div className="game-notes-section">
                    {isEditingNotes ? (
                        <div className="notes-editor">
                            <label htmlFor={`notes-${game.id}`} className="sr-only">
                                Notes for {game.name}
                            </label>
                            <textarea
                                id={`notes-${game.id}`}
                                value={notesText}
                                onChange={(e) => setNotesText(e.target.value)}
                                placeholder="Add personal notes..."
                                maxLength={2000}
                                disabled={updatingNotes}
                                rows={3}
                            />
                            <div className="notes-actions">
                                <span className="notes-char-count">
                                    {notesText.length}/2000
                                </span>
                                <div className="notes-buttons">
                                    <button
                                        type="button"
                                        className="notes-clear-button"
                                        onClick={handleClearNotes}
                                        disabled={updatingNotes || notesText === ''}
                                        aria-label="Clear notes"
                                    >
                                        Clear
                                    </button>
                                    <button
                                        type="button"
                                        className="notes-cancel-button"
                                        onClick={handleCancelNotes}
                                        disabled={updatingNotes}
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        type="button"
                                        className="notes-save-button"
                                        onClick={handleSaveNotes}
                                        disabled={updatingNotes}
                                    >
                                        {updatingNotes ? 'Saving...' : 'Save'}
                                    </button>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="notes-display" onClick={() => setIsEditingNotes(true)}>
                            {displayNotes ? (
                                <p className="notes-content">{game.notes}</p>
                            ) : (
                                <p className="notes-placeholder">Click to add notes...</p>
                            )}
                            <span className="notes-edit-hint">✎ Edit</span>
                        </div>
                    )}
                </div>

                <button
                    className="delete-button"
                    onClick={() => onDelete(game.id)}
                    disabled={deleting}
                    aria-label={`Delete ${game.name}`}
                >
                    {deleting ? 'Deleting...' : 'Delete'}
                </button>
            </div>
        </article>
    )
}

import { useState } from 'react'

export default GameCard