import { useState } from "react";

function SearchBar({ onSearchSubmit }) {
  const [value, setValue] = useState("");

  const handleChange = (e) => {
    setValue(e.target.value); // update internal input
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearchSubmit(value); // <-- SENDS VALUE TO PARENT
    setValue(""); // optional: clear input
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={value}
        onChange={handleChange}
        placeholder="Type something..."
      />
      <button type="submit">Search</button>
    </form>
  );
}

export default SearchBar;

