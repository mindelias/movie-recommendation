import { useEffect, useState } from 'react';
import { apiFetch } from '../api';
import NavBar from '../components/NavBar';

export default function TopMovies() {
  const [movies, setMovies] = useState([]);

  useEffect(() => {
    apiFetch('/movies/top')
      .then((res) => res.json())
      .then(setMovies);
  }, []);

  return (
    <div>
      <NavBar />
      <h2>Top Movies</h2>
      <ul className="movie-grid">
        {movies.map((m) => (
          <li key={m.movie_id} className="movie-card">
            {m.poster_path && <img src={m.poster_path} alt={m.title} />}
            <h3>{m.title}</h3>
            <p>{m.overview}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
