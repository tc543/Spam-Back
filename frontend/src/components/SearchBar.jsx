import { useState } from "react";
import "./SearchBar.css"

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
    <form className="search-form" onSubmit={handleSubmit}>
      <input
        type="text"
        value={value}
        onChange={handleChange}
        placeholder="Enter Spammer's Phone Number"
      />
      <button type="submit">Search</button>
    </form>
  );
}

export default SearchBar;

