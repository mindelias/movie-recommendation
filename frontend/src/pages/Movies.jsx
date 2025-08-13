import { useEffect, useState } from 'react';
import { apiFetch } from '../api';
import NavBar from '../components/NavBar';

export default function Movies() {
  const [movies, setMovies] = useState([]);
  const [ratings, setRatings] = useState({});

  useEffect(() => {
    apiFetch('/movies/')
      .then((res) => res.json())
      .then(setMovies);
  }, []);

  const rate = async (movieId) => {
    const rating = ratings[movieId];
    if (!rating) return;
    const res = await apiFetch('/movies/ratings', {
      method: 'POST',
      body: JSON.stringify({ movie_id: movieId, rating: parseFloat(rating) }),
    });
    if (res.ok) {
      alert('Rating saved');
    } else {
      alert('Rating failed');
    }
  };

  return (
    <div>
      <NavBar />
      <h2>All Movies</h2>
      <ul className="movie-grid">
        {movies.map((m) => (
          <li key={m.movie_id} className="movie-card">
            {m.poster_path && <img src={m.poster_path} alt={m.title} />}
            <h3>{m.title}</h3>
            <p>{m.overview}</p>
            <input
              type="number"
              min="0"
              max="5"
              step="0.5"
              value={ratings[m.movie_id] || ''}
              onChange={(e) =>
                setRatings({ ...ratings, [m.movie_id]: e.target.value })
              }
              placeholder="Rate 0-5"
            />
            <button onClick={() => rate(m.movie_id)}>Rate</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
