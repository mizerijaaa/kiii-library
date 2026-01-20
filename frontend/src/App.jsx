import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './index.css';


const API_URL = import.meta.env.VITE_API_URL;

function App() {
  const [books, setBooks] = useState([]);
  const [newBook, setNewBook] = useState({ title: '', author: '', genre: '', year: '' });
  const [editingBook, setEditingBook] = useState(null);

  useEffect(() => {
    fetchBooks();
  }, []);

  const fetchBooks = async () => {
    try {
      const res = await axios.get(`${API_URL}/api/books`);
      setBooks(res.data);
    } catch (error) {
      console.error('Error fetching books:', error);
    }
  };

  const addBook = async () => {
    try {
      await axios.post(`${API_URL}/api/books`, { ...newBook, year: parseInt(newBook.year) });
      fetchBooks();
      setNewBook({ title: '', author: '', genre: '', year: '' });
    } catch (error) {
      console.error('Error adding book:', error);
    }
  };

  const updateBook = async (id) => {
    try {
      await axios.put(`${API_URL}/api/books/${id}`, { ...editingBook, year: parseInt(editingBook.year) });
      fetchBooks();
      setEditingBook(null);
    } catch (error) {
      console.error('Error updating book:', error);
    }
  };

  const deleteBook = async (id) => {
    try {
      await axios.delete(`${API_URL}/api/books/${id}`);
      fetchBooks();
    } catch (error) {
      console.error('Error deleting book:', error);
    }
  };

  return (
    <div className="App">
      <h1>My Library</h1>

      {/* Add Book Form */}
      <div className="card">
        <h2>Add a Book</h2>
        <input
          type="text"
          placeholder="Title"
          value={newBook.title}
          onChange={(e) => setNewBook({ ...newBook, title: e.target.value })}
        />
        <input
          type="text"
          placeholder="Author"
          value={newBook.author}
          onChange={(e) => setNewBook({ ...newBook, author: e.target.value })}
        />
        <input
          type="text"
          placeholder="Genre"
          value={newBook.genre}
          onChange={(e) => setNewBook({ ...newBook, genre: e.target.value })}
        />
        <input
          type="number"
          placeholder="Year"
          value={newBook.year}
          onChange={(e) => setNewBook({ ...newBook, year: e.target.value })}
        />
        <button onClick={addBook}>Add Book</button>
      </div>

      {/* Book List */}
      <h2>Books</h2>
      {books.length === 0 && <p>No books yet 😅</p>}
      <div className="books-grid">
        {books.map((book) => (
          <div key={book._id} className="card">
            {editingBook && editingBook._id === book._id ? (
              <div>
                <input
                  type="text"
                  value={editingBook.title}
                  onChange={(e) => setEditingBook({ ...editingBook, title: e.target.value })}
                />
                <input
                  type="text"
                  value={editingBook.author}
                  onChange={(e) => setEditingBook({ ...editingBook, author: e.target.value })}
                />
                <input
                  type="text"
                  value={editingBook.genre}
                  onChange={(e) => setEditingBook({ ...editingBook, genre: e.target.value })}
                />
                <input
                  type="number"
                  value={editingBook.year}
                  onChange={(e) => setEditingBook({ ...editingBook, year: e.target.value })}
                />
                <button onClick={() => updateBook(book._id)}>Update</button>
                <button onClick={() => setEditingBook(null)}>Cancel</button>
              </div>
            ) : (
              <div>
                <h3>{book.title}</h3>
                <p><strong>Author:</strong> {book.author}</p>
                <p><strong>Genre:</strong> {book.genre}</p>
                <p><strong>Year:</strong> {book.year}</p>
                <div className="button-row">
                  <button onClick={() => setEditingBook(book)}>Edit</button>
                  <button onClick={() => deleteBook(book._id)}>Delete</button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
