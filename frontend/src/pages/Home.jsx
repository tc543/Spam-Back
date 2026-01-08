import SearchBar from "../components/SearchBar";
import { useState } from "react";
import api from "../api";
import "./Home.css";

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
    <div className="home">
      <div class = "title">
        <h1>Welcome to</h1>
        <h1>Spam Back</h1>
      </div>
      <div className="search-wrapper">
        <SearchBar onSearchSubmit={handleSearchSubmit} />
      </div>
    </div>
  );
}

export default Home;