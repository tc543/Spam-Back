import SearchBar from "../components/SearchBar";
import { useState } from "react";

function Home() {
  const [submittedText, setSubmittedText] = useState("");

  const handleSearchSubmit = (text) => {
    setSubmittedText(text); // <-- RECEIVES VALUE FROM CHILD
  };

  return (
    <div>
      <SearchBar onSearchSubmit={handleSearchSubmit} />
      <div>Last submitted: {submittedText}</div>
    </div>
  );
}

export default Home;