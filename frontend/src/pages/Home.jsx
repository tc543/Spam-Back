import SearchBar from "../components/SearchBar";
import { useState } from "react";
import api from "../api";

function Home() {
  const [submittedText, setSubmittedText] = useState("");

  const handleSearchSubmit = async (text) => {
    setSubmittedText(text); // update UI immediately
    try {
      await api.post("/sending", {
        phone_number: text
      });
      console.log("Search sent to backend");
    } catch (error) {
      console.error("Error sending search", error);
    }
  };

  return (
    <div>
      <SearchBar onSearchSubmit={handleSearchSubmit} />
      <div>Last submitted: {submittedText}</div>
    </div>
  );
}

export default Home;